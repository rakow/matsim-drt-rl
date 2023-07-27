package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.matsim.contrib.drt.analysis.zonal.DrtZonalSystem;
import org.matsim.contrib.drt.analysis.zonal.DrtZone;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server.Rebalancer;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server.RebalancingStrategyGrpc;
import org.matsim.contrib.dvrp.fleet.FleetSpecification;
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
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/**
 * Handles connection and lifecycle to the remote server.
 */
final class ConnectionManager extends RebalancingStrategyGrpc.RebalancingStrategyImplBase
	implements StartupListener, ShutdownListener, IterationStartsListener, IterationEndsListener {

	private static final Logger log = LogManager.getLogger(ConnectionManager.class);

	private final int port;
	private final RebalancingParams params;
	private final DrtZonalSystem zonalSystem;
	private final FleetSpecification fleet;
	private Server server;

	ConnectionManager(int port, RebalancingParams params, DrtZonalSystem zonalSystem, FleetSpecification fleet) {
		this.port = port;
		this.params = params;
		this.zonalSystem = zonalSystem;
		this.fleet = fleet;
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
	public void notifyIterationEnds(IterationEndsEvent iterationEndsEvent) {

	}

	@Override
	public void notifyIterationStarts(IterationStartsEvent iterationStartsEvent) {

	}

	@Override
	public void getSpecification(Rebalancer.Empty request, StreamObserver<Rebalancer.RebalancingSpecification> responseObserver) {

		Rebalancer.RebalancingSpecification.Builder builder = Rebalancer.RebalancingSpecification.newBuilder()
			.setInterval(params.interval)
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

	@Override
	public void performRebalancing(Rebalancer.RebalancingInstructions request, StreamObserver<Rebalancer.CurrentTime> responseObserver) {

		// TODO: check simulation time
		// store rebalancing

	}

	/**
	 * Blocks until rebalance instructors for specified time stamp have arrived.
	 */
	Rebalancer.RebalancingInstructions waitForInstructions(double time) {

		log.info("Rebalancing time step {}", time);

		CountDownLatch latch = new CountDownLatch(1);

		try {
			latch.await();
		} catch (InterruptedException e) {
			throw new RuntimeException(e);
		}

		return null;
	}

	/**
	 * Provide current state to the server.
	 */
	void setCurrentState(double time, Rebalancer.RebalancingState state) {

	}
}
