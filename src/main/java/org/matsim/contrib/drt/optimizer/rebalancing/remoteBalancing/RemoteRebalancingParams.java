package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import jakarta.validation.constraints.Positive;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
import org.matsim.core.config.ReflectiveConfigGroup;

/**
 * Strategy params for remote rebalancing.
 */
@SuppressWarnings("VisibilityModifier")
public class RemoteRebalancingParams extends ReflectiveConfigGroup implements RebalancingParams.RebalancingStrategyParams {

	@Parameter
	@Comment("Remote port for the server to listen to")
	@Positive
	public int port = 5555;

	@Parameter
	@Comment("Earliest time for accepting rebalancing instructions.")
	public double startRebalancing = 6 * 3600;


	@Parameter
	@Comment("Latest time for the last rebalancing interval.")
	public double endRebalancing = 18 * 3600;

	@Parameter
	@Comment("Skip time steps without expected demand.")
	public boolean skipNoDemand = true;

	public RemoteRebalancingParams() {
		super("remoteRebalancing");
	}
}
