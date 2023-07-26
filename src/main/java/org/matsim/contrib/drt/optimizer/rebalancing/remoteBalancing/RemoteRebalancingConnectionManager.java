package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server.RebalancingStrategyGrpc;
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

/**
 * Handles connection and lifecycle to the remote server.
 */
public class RemoteRebalancingConnectionManager extends RebalancingStrategyGrpc.RebalancingStrategyImplBase implements StartupListener, ShutdownListener, IterationStartsListener, IterationEndsListener {

	private static final Logger log = LogManager.getLogger(RemoteRebalancingConnectionManager.class);


	private final RemoteRebalancingParams params;

	public RemoteRebalancingConnectionManager(RemoteRebalancingParams params) {
		this.params = params;
	}

	@Override
	public void notifyStartup(StartupEvent startupEvent) {

		Server server = ServerBuilder.forPort(params.port)
			.addService(this)
			.build();

		try {
			server.start();
			log.info("Running server on port {} ...", params.port);
		} catch (IOException e) {
			throw new UncheckedIOException(e);
		}

	}

	@Override
	public void notifyShutdown(ShutdownEvent shutdownEvent) {

	}

	@Override
	public void notifyIterationEnds(IterationEndsEvent iterationEndsEvent) {

	}

	@Override
	public void notifyIterationStarts(IterationStartsEvent iterationStartsEvent) {

	}


}
