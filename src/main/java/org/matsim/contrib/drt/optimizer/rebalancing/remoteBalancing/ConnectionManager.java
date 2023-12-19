package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import it.unimi.dsi.fastutil.doubles.Double2BooleanArrayMap;
import it.unimi.dsi.fastutil.doubles.Double2BooleanMap;
import it.unimi.dsi.fastutil.doubles.DoubleArrayList;
import it.unimi.dsi.fastutil.doubles.DoubleList;
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.matsim.api.core.v01.Id;
import org.matsim.contrib.drt.analysis.DrtEventSequenceCollector;
import org.matsim.contrib.drt.analysis.DrtVehicleDistanceStats;
import org.matsim.contrib.drt.analysis.zonal.DrtZonalSystem;
import org.matsim.contrib.drt.analysis.zonal.DrtZone;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
import org.matsim.contrib.drt.optimizer.rebalancing.demandestimator.ZonalDemandEstimator;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server.Rebalancer;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server.RebalancingStrategyGrpc;
import org.matsim.contrib.dvrp.fleet.DvrpVehicle;
import org.matsim.contrib.dvrp.fleet.FleetSpecification;
import org.matsim.core.config.Config;
import org.matsim.core.controler.events.IterationEndsEvent;
import org.matsim.core.controler.events.IterationStartsEvent;
import org.matsim.core.controler.events.ShutdownEvent;
import org.matsim.core.controler.events.StartupEvent;
import org.matsim.core.controler.listener.IterationEndsListener;
import org.matsim.core.controler.listener.IterationStartsListener;
import org.matsim.core.controler.listener.ShutdownListener;
import org.matsim.core.controler.listener.StartupListener;
import org.matsim.vehicles.Vehicle;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.function.ToDoubleFunction;

/**
 * Handles connection and lifecycle to the remote server.
 */
final class ConnectionManager extends RebalancingStrategyGrpc.RebalancingStrategyImplBase
	implements StartupListener, ShutdownListener, IterationStartsListener, IterationEndsListener {

	private static final Logger log = LogManager.getLogger(ConnectionManager.class);

	private final Config config;
	private final RebalancingParams params;

	private final RemoteRebalancingParams remoteParams;
	private final DrtZonalSystem zonalSystem;
	private final FleetSpecification fleet;

	private final DrtEventSequenceCollector drtEvents;
	private final ZonalDemandEstimator zonalDemand;
	private final MethodHandle vehicleStats;

	private final BackoffIdleStrategy wait = new BackoffIdleStrategy();

	private final Map<Id<Vehicle>, VehicleState> vehicleStates = new HashMap<>();

	/**
	 * Store time-steps that will be skipped.
	 */
	private final Double2BooleanMap skipTimestep = new Double2BooleanArrayMap();

	private VehicleStatsHandles vehicleStatsHandles;

	private Server server;

	/**
	 * Maximum total expected demand in all zone per time step.
	 */
	private double maxExpectedDemand;

	/**
	 * Current iteration.
	 */
	private int iteration;

	/**
	 * Current state.
	 */
	private volatile Rebalancer.RebalancingState state;
	/**
	 * Current instructions.
	 */
	private volatile Rebalancer.RebalancingInstructions instructions;

	ConnectionManager(Config config, RebalancingParams params, RemoteRebalancingParams remoteParams, DrtZonalSystem zonalSystem,
					  FleetSpecification fleet, DrtEventSequenceCollector drtEvents, ZonalDemandEstimator zonalDemand,
					  DrtVehicleDistanceStats vehicleStats) {
		this.config = config;
		this.params = params;
		this.remoteParams = remoteParams;
		this.zonalSystem = zonalSystem;
		this.fleet = fleet;
		this.drtEvents = drtEvents;
		this.zonalDemand = zonalDemand;

		try {
			MethodHandles.Lookup lookup = MethodHandles.lookup();
			Method m = vehicleStats.getClass().getDeclaredMethod("getVehicleStates");
			m.trySetAccessible();

			this.vehicleStats = lookup.unreflect(m).bindTo(vehicleStats);
		} catch (ReflectiveOperationException e) {
			throw new IllegalStateException("Could not retrieve vehicle state");
		}
	}

	private static Rebalancer.DrtRequest.Builder convert(DrtEventSequenceCollector.EventSequence request) {
		Rebalancer.DrtRequest.Builder builder = Rebalancer.DrtRequest.newBuilder()
			.setSubmissionTime(request.getSubmitted().getTime());

		if (request.getDeparture().isPresent())
			builder.setDepartureTime(request.getDeparture().get().getTime());

		if (request.getPickedUp().isPresent())
			builder.setPickupTime(request.getPickedUp().get().getTime());

		if (request.getDroppedOff().isPresent())
			builder.setDropOffTime(request.getDroppedOff().get().getTime());

		return builder;
	}

	private static Rebalancer.Stats convert(DescriptiveStatistics stats) {
		return Rebalancer.Stats.newBuilder()
			.setSum(stats.getSum())
			.setMean(stats.getMean())
			.setMedian(stats.getPercentile(0.5))
			.setQ5(stats.getPercentile(0.05))
			.setQ95(stats.getPercentile(0.95))
			.setN((int) stats.getN())
			.build();
	}

	@Override
	public void notifyStartup(StartupEvent startupEvent) {

		server = ServerBuilder.forPort(remoteParams.port)
			.addService(this)
			.build();

		try {
			server.start();
			log.info("Running server on port {} ...", remoteParams.port);
		} catch (IOException e) {
			throw new UncheckedIOException(e);
		}
	}

	@Override
	public void notifyShutdown(ShutdownEvent shutdownEvent) {
		server.shutdown();
		try {
			server.awaitTermination(5, TimeUnit.SECONDS);
		} catch (InterruptedException e) {
			log.warn("Error shutting down server", e);
		}
	}

	@Override
	public void notifyIterationStarts(IterationStartsEvent iterationStartsEvent) {
		// reset from old iteration
		state = null;
		instructions = null;
		iteration = iterationStartsEvent.getIteration();

		// 1 is the minimum
		maxExpectedDemand = 1;

		DoubleList demands = new DoubleArrayList();

		skipTimestep.clear();
		vehicleStates.clear();

		// TODO: might only skip if there are at lest two consecutive empty periods

		for (double t = remoteParams.startRebalancing; t < remoteParams.endRebalancing; t += params.interval) {
			ToDoubleFunction<DrtZone> demand = zonalDemand.getExpectedDemand(t, params.interval);
			double sum = zonalSystem.getZones().values().stream().mapToDouble(demand).sum();
			demands.add(sum);
			if (sum > maxExpectedDemand)
				maxExpectedDemand = sum;

			if (sum == 0 && remoteParams.skipNoDemand)
				skipTimestep.put(t, true);

		}

		// For debugging and info
		log.info("Sum of demands per time step from {} to {}: {}", remoteParams.startRebalancing, remoteParams.endRebalancing, demands);
		log.info("Skipping time-steps: {}", skipTimestep);
	}

	@Override
	public void notifyIterationEnds(IterationEndsEvent iterationEndsEvent) {

		// Wait until last state has be retrieved
		while (state != null)
			wait.idle();

		wait.reset();
	}

	@Override
	public void getSpecification(Rebalancer.Empty request, StreamObserver<Rebalancer.RebalancingSpecification> responseObserver) {

		Rebalancer.RebalancingSpecification.Builder builder = Rebalancer.RebalancingSpecification.newBuilder()
			.setInterval(params.interval)
			.setStartTime(remoteParams.startRebalancing)
			.setEndTime(remoteParams.endRebalancing)
			// 2 iterations are skipped to estimate demand
			.setIterations(config.controler().getLastIteration() - 2)
			.setSteps((int) ((remoteParams.endRebalancing - remoteParams.startRebalancing) / params.interval))
			.setFleetSize(fleet.getVehicleSpecifications().size());

		for (DrtZone zone : zonalSystem.getZones().values()) {
			builder.addZones(Rebalancer.Zone.newBuilder()
				.setId(zone.getId())
				.setCentroidX(zone.getCentroid().getX())
				.setCentroidY(zone.getCentroid().getY())
				.build());
		}

		responseObserver.onNext(builder.build());
		responseObserver.onCompleted();
	}

	/**
	 * Called by the client to receive state from last time step. Will block until time step is ready.
	 * {@link #setCurrentState(double, Map)}
	 */
	@Override
	public void getCurrentState(Rebalancer.SimulationTime request, StreamObserver<Rebalancer.RebalancingState> responseObserver) {

		while (state == null || state.getSimulationTime() < request.getTime()) {
			wait.idle();
		}

		wait.reset();

		if (state.getSimulationTime() > request.getTime()) {
			log.error("Invalid state requested for {}, current time ist {}", request.getTime(), state.getSimulationTime());
			responseObserver.onError(new IllegalArgumentException("Simulation time is further than requested"));
			return;
		}

		responseObserver.onNext(state);
		responseObserver.onCompleted();

		// state is reset and can only be retrieved one time
		state = null;
	}

	/**
	 * Called by the client to send rebalance instructions.
	 */
	@Override
	public void performRebalancing(Rebalancer.RebalancingInstructions request, StreamObserver<Rebalancer.SimulationTime> responseObserver) {
		// Only store instructions
		instructions = request;

		int nextTimeStep = request.getCurrentTime() + params.interval;

		while (skipTimestep.containsKey(nextTimeStep))
			nextTimeStep += params.interval;

		responseObserver.onNext(Rebalancer.SimulationTime.newBuilder().setTime(nextTimeStep).build());
		responseObserver.onCompleted();
	}

	/**
	 * Skip iterations until expected demand is available.
	 */
	boolean skipTimestep(double time) {
		if (iteration <= 1)
			return true;

		// First time step is not skipped because it will always be queried
		if (time == remoteParams.startRebalancing)
			return false;

		return skipTimestep.containsKey(time);
	}

	/**
	 * Blocks until rebalance instructions for specified time stamp have arrived.
	 */
	Rebalancer.RebalancingInstructions waitForInstructions(double time) {

		log.info("Rebalancing time step {}", time);

		while (instructions == null || instructions.getCurrentTime() < time) {
			wait.idle();
		}

		wait.reset();

		if (time > instructions.getCurrentTime())
			throw new IllegalStateException(String.format("Received instructions for time %d are further in time than simulation: %f",
				instructions.getCurrentTime(), time));

		return instructions;
	}

	/**
	 * Provide current state to the server.
	 */
	@SuppressWarnings("IllegalCatch")
	Rebalancer.RebalancingState setCurrentState(double time, Map<DrtZone, List<DvrpVehicle>> rebalancableVehiclesPerZone,
												Map<DrtZone, List<DvrpVehicle>> soonIdleVehiclesPerZone) {

		// set current state for the server
		Rebalancer.RebalancingState.Builder state = Rebalancer.RebalancingState.newBuilder();

		ToDoubleFunction<DrtZone> demand = zonalDemand.getExpectedDemand(time, params.interval);
		for (DrtZone zone : zonalSystem.getZones().values()) {
			state.addRebalancableVehicles(rebalancableVehiclesPerZone.getOrDefault(zone, List.of()).size());
			state.addSoonIdleVehicles(soonIdleVehiclesPerZone.getOrDefault(zone, List.of()).size());
			// Fill expected demand
			state.addExpectedDemand(demand.applyAsDouble(zone));
		}

		DescriptiveStatistics waitingTime = new DescriptiveStatistics();
		DescriptiveStatistics travelTime = new DescriptiveStatistics();

		for (DrtEventSequenceCollector.EventSequence request : drtEvents.getPerformedRequestSequences().values()) {

			if (request.getSubmitted().getTime() > time - params.interval)
				state.addPerformedRequest(convert(request));

			if (request.getPickedUp().isPresent() && request.getPickedUp().get().getTime() > time - params.interval) {
				waitingTime.addValue(request.getPickedUp().get().getTime() - request.getDeparture().get().getTime());
			}

			if (request.getDroppedOff().isPresent() && request.getDroppedOff().get().getTime() > time - params.interval) {
				travelTime.addValue(request.getDroppedOff().get().getTime() - request.getPickedUp().get().getTime());
			}
		}

		for (DrtEventSequenceCollector.EventSequence request : drtEvents.getRejectedRequestSequences().values()) {
			if (request.getSubmitted().getTime() > time - params.interval)
				state.addRejectedRequests(convert(request));
		}

		try {
			setVehicleStats(state);
		} catch (Throwable e) {
			throw new IllegalStateException("Could not get vehicle state", e);
		}

		state.setSimulationTime(time);
		state.setWaitingTime(convert(waitingTime));
		state.setTravelTime(convert(travelTime));
		state.setMaxExpectedDemand(maxExpectedDemand);

		if (time >= remoteParams.endRebalancing)
			state.setSimulationEnded(true);

		this.state = state.build();
		return this.state;
	}

	/**
	 * Extract vehicle stats.
	 */
	@SuppressWarnings({"unchecked", "IllegalThrows"})
	private void setVehicleStats(Rebalancer.RebalancingState.Builder state) throws Throwable {

		Map<Id<Vehicle>, Object> stats = (Map<Id<Vehicle>, Object>) vehicleStats.invoke();

		DescriptiveStatistics totalDistance = new DescriptiveStatistics();
		DescriptiveStatistics totalEmptyDistance = new DescriptiveStatistics();
		DescriptiveStatistics totalPassangerDistance = new DescriptiveStatistics();

		for (Map.Entry<Id<Vehicle>, Object> e : stats.entrySet()) {

			Object o = e.getValue();

			VehicleStatsHandles handles = getHandles(o);
			VehicleState old = vehicleStates.computeIfAbsent(e.getKey(), vehicleId -> new VehicleState());

			double empty = (double) handles.totalDistance.get(o) - (double) handles.totalOccupiedDistance.get(o);

			totalDistance.addValue((double) handles.totalDistance.get(o) - old.totalDistance);
			totalEmptyDistance.addValue(empty - old.totalEmptyDistance);
			totalPassangerDistance.addValue((double) handles.totalPassengerTraveledDistance.get(o) - old.totalPassengerTraveledDistance);

			old.totalDistance = (double) handles.totalDistance.get(o);
			old.totalEmptyDistance = empty;
			old.totalPassengerTraveledDistance = (double) handles.totalPassengerTraveledDistance.get(o);
		}

		state.setDrivenDistance(convert(totalDistance));
		state.setDrivenEmptyDistance(convert(totalEmptyDistance));
		state.setPassengerTraveledDistance(convert(totalPassangerDistance));

	}

	/**
	 * Retrieve and store var handles from non-accessible class in {@link DrtVehicleDistanceStats}.
	 */
	private VehicleStatsHandles getHandles(Object o) throws ReflectiveOperationException {

		if (vehicleStatsHandles == null) {
			vehicleStatsHandles = new VehicleStatsHandles(
				MethodHandles.privateLookupIn(o.getClass(), MethodHandles.lookup())
					.findVarHandle(o.getClass(), "totalDistance", double.class),

				MethodHandles.privateLookupIn(o.getClass(), MethodHandles.lookup())
					.findVarHandle(o.getClass(), "totalOccupiedDistance", double.class),

				MethodHandles.privateLookupIn(o.getClass(), MethodHandles.lookup())
					.findVarHandle(o.getClass(), "totalPassengerTraveledDistance", double.class)
			);
		}

		return vehicleStatsHandles;

	}


	private static class VehicleState {
		double totalDistance = 0;
		double totalEmptyDistance = 0;
		double totalPassengerTraveledDistance = 0;
	}

	private record VehicleStatsHandles(VarHandle totalDistance, VarHandle totalOccupiedDistance, VarHandle totalPassengerTraveledDistance) {
	}

}
