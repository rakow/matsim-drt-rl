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
	@Comment("The address (host + port) of the rebalancing server")
	@NotNull
	private String address = "tcp://localhost:5555";


	public RemoteRebalancingParams() {
		super(SET_NAME);
	}
}
