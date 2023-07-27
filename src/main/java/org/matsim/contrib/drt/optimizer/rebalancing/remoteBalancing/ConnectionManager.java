package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.matsim.contrib.drt.analysis.DrtEventSequenceCollector;
import org.matsim.contrib.drt.analysis.zonal.DrtZonalSystem;
import org.matsim.contrib.drt.analysis.zonal.DrtZone;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
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

import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Handles connection and lifecycle to the remote server.
 */
final class ConnectionManager extends RebalancingStrategyGrpc.RebalancingStrategyImplBase
	implements StartupListener, ShutdownListener, IterationStartsListener, IterationEndsListener {

	private static final Logger log = LogManager.getLogger(ConnectionManager.class);

	private final int port;
	private final Config config;
	private final RebalancingParams params;
	private final DrtZonalSystem zonalSystem;
	private final FleetSpecification fleet;

	private final DrtEventSequenceCollector drtEvents;

	private final BackoffIdleStrategy wait = new BackoffIdleStrategy();

	private Server server;

	/**
	 * Current state.
	 */
	private volatile Rebalancer.RebalancingState state;
	/**
	 * Current instructions.
	 */
	private volatile Rebalancer.RebalancingInstructions instructions;

	ConnectionManager(int port, Config config, RebalancingParams params, DrtZonalSystem zonalSystem, FleetSpecification fleet, DrtEventSequenceCollector drtEvents) {
		this.port = port;
		this.config = config;
		this.params = params;
		this.zonalSystem = zonalSystem;
		this.fleet = fleet;
		this.drtEvents = drtEvents;
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
			.build();
	}

	@Override
	public void notifyStartup(StartupEvent startupEvent) {

		Server server = ServerBuilder.forPort(port)
			.addService(this)
			.build();

		try {
			server.start();
			log.info("Running server on port {} ...", port);
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
			throw new RuntimeException(e);
		}
	}

	@Override
	public void notifyIterationStarts(IterationStartsEvent iterationStartsEvent) {
		// reset from old iteration
		state = null;
		instructions = null;
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
			.setEndTime(config.qsim().getEndTime().orElse(-1))
			.setIterations(config.controler().getLastIteration())
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
		responseObserver.onNext(Rebalancer.SimulationTime.newBuilder().setTime(request.getCurrentTime() + params.interval).build());
		responseObserver.onCompleted();
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
	Rebalancer.RebalancingState setCurrentState(double time, Map<DrtZone, List<DvrpVehicle>> rebalancableVehiclesPerZone) {

		// set current state for the server
		Rebalancer.RebalancingState.Builder state = Rebalancer.RebalancingState.newBuilder();
		for (Map.Entry<DrtZone, List<DvrpVehicle>> e : rebalancableVehiclesPerZone.entrySet()) {
			state.putRebalancableVehiclesPerZone(e.getKey().getId(), e.getValue().size());
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

		for (DrtEventSequenceCollector.EventSequence request : drtEvents.getRejectedRequestSequences().values())
			state.addPerformedRequest(convert(request));

		state.setSimulationTime(time);
		state.setWaitingTime(convert(waitingTime));
		state.setTravelTime(convert(travelTime));

		if (time == config.qsim().getEndTime().orElse(-1))
			state.setSimulationEnded(true);

		this.state = state.build();
		return this.state;
	}
}
