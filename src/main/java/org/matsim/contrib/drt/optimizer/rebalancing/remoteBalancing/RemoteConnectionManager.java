package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server.RebalancingStrategyGrpc;
import org.matsim.core.controler.listener.IterationEndsListener;
import org.matsim.core.controler.listener.IterationStartsListener;
import org.matsim.core.controler.listener.ShutdownListener;
import org.matsim.core.controler.listener.StartupListener;

/**
 * Interface for managing the remote connections to clients.
 */
public interface RemoteConnectionManager extends RebalancingStrategyGrpc.AsyncService,
	StartupListener, ShutdownListener, IterationStartsListener, IterationEndsListener {
}
