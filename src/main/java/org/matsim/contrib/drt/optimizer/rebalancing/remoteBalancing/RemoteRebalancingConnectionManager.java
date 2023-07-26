package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import org.matsim.core.controler.events.IterationEndsEvent;
import org.matsim.core.controler.events.IterationStartsEvent;
import org.matsim.core.controler.events.ShutdownEvent;
import org.matsim.core.controler.events.StartupEvent;
import org.matsim.core.controler.listener.IterationEndsListener;
import org.matsim.core.controler.listener.IterationStartsListener;
import org.matsim.core.controler.listener.ShutdownListener;
import org.matsim.core.controler.listener.StartupListener;

/**
 * Handles connection and lifecycle to the remote server.
 */
public class RemoteRebalancingConnectionManager implements StartupListener, ShutdownListener, IterationStartsListener, IterationEndsListener {
	@Override
	public void notifyIterationEnds(IterationEndsEvent iterationEndsEvent) {

	}

	@Override
	public void notifyIterationStarts(IterationStartsEvent iterationStartsEvent) {

	}

	@Override
	public void notifyShutdown(ShutdownEvent shutdownEvent) {

	}

	@Override
	public void notifyStartup(StartupEvent startupEvent) {

	}
}
