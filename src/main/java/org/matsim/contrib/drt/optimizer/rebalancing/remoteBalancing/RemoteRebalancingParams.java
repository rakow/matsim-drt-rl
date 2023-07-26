package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import jakarta.validation.constraints.NotNull;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
import org.matsim.contrib.util.ReflectiveConfigGroupWithConfigurableParameterSets;


/**
 * Config params for remote balancing.
 */
public class RemoteRebalancingParams extends ReflectiveConfigGroupWithConfigurableParameterSets implements RebalancingParams.RebalancingStrategyParams {

	public static final String SET_NAME = "remoteRebalancingStrategyParams";

	@Parameter
	@Comment("Port on which to listen for connections")
	@NotNull
	public int port = 5555;


	public RemoteRebalancingParams() {
		super(SET_NAME);
	}
}
