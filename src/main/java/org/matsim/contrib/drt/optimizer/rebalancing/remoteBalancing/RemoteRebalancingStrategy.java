package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import org.matsim.contrib.drt.analysis.zonal.DrtZonalSystem;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingStrategy;
import org.matsim.contrib.drt.optimizer.rebalancing.mincostflow.ZonalRelocationCalculator;
import org.matsim.contrib.dvrp.fleet.DvrpVehicle;
import org.matsim.contrib.dvrp.fleet.Fleet;

import java.util.List;
import java.util.stream.Stream;


/**
 * Implement the remote balancing strategy, which will receive rebalancing instructions from an external service.
 */
public class RemoteRebalancingStrategy implements RebalancingStrategy {

	public RemoteRebalancingStrategy(RemoteRebalancingConnectionManager server, DrtZonalSystem zonalSystem,
									 Fleet fleet, ZonalRelocationCalculator relocationCalculator) {
	}

	@Override
	public List<Relocation> calcRelocations(Stream<? extends DvrpVehicle> rebalancableVehicles, double time) {
		return List.of();
	}
}
