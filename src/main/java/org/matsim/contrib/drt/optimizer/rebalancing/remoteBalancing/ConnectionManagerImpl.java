package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.matsim.contrib.drt.analysis.zonal.DrtZonalSystem;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server.RebalancingStrategyGrpc;
import org.matsim.contrib.dvrp.fleet.FleetSpecification;
import org.matsim.core.controler.events.IterationEndsEvent;
import org.matsim.core.controler.events.IterationStartsEvent;
import org.matsim.core.controler.events.ShutdownEvent;
import org.matsim.core.controler.events.StartupEvent;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.concurrent.TimeUnit;

/**
 * Handles connection and lifecycle to the remote server.
 */
final class ConnectionManagerImpl extends RebalancingStrategyGrpc.RebalancingStrategyImplBase implements RemoteConnectionManager {

	private static final Logger log = LogManager.getLogger(ConnectionManagerImpl.class);

	private final int port;
	private final RebalancingParams params;
	private final DrtZonalSystem zonalSystem;
	private final FleetSpecification fleet;
	private Server server;

	public ConnectionManagerImpl(int port, RebalancingParams params, DrtZonalSystem zonalSystem, FleetSpecification fleet) {
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


}
