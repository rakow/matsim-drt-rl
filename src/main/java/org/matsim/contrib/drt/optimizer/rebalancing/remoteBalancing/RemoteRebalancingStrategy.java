package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import org.matsim.contrib.drt.analysis.zonal.DrtZonalSystem;
import org.matsim.contrib.drt.analysis.zonal.DrtZone;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingStrategy;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingUtils;
import org.matsim.contrib.drt.optimizer.rebalancing.mincostflow.AggregatedMinCostRelocationCalculator;
import org.matsim.contrib.drt.optimizer.rebalancing.mincostflow.ZonalRelocationCalculator;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server.Rebalancer;
import org.matsim.contrib.dvrp.fleet.DvrpVehicle;
import org.matsim.contrib.dvrp.fleet.Fleet;

import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;


/**
 * Implements the remote balancing strategy, which will receive rebalancing instructions from an external service.
 */
public class RemoteRebalancingStrategy implements RebalancingStrategy {

	private final ConnectionManager server;
	private final DrtZonalSystem zonalSystem;
	private final Fleet fleet;
	private final ZonalRelocationCalculator relocationCalculator;
	private final RebalancingParams params;

	public RemoteRebalancingStrategy(ConnectionManager server, DrtZonalSystem zonalSystem, Fleet fleet,
									 ZonalRelocationCalculator relocationCalculator, RebalancingParams params) {
		this.server = server;
		this.zonalSystem = zonalSystem;
		this.fleet = fleet;
		this.relocationCalculator = relocationCalculator;
		this.params = params;
	}

	@Override
	public List<Relocation> calcRelocations(Stream<? extends DvrpVehicle> rebalancableVehicles, double time) {

		Map<DrtZone, List<DvrpVehicle>> rebalancableVehiclesPerZone = RebalancingUtils.groupRebalancableVehicles(
			zonalSystem, params, rebalancableVehicles, time);

		Map<DrtZone, List<DvrpVehicle>> soonIdleVehiclesPerZone = RebalancingUtils.groupSoonIdleVehicles(zonalSystem,
			params, fleet, time);

		// set current state for the server
		Rebalancer.RebalancingState.Builder state = Rebalancer.RebalancingState.newBuilder();

		server.setCurrentState(time, state.build());

		server.waitForInstructions(time);

		// TODO: call server, how to gather current statistics?

		List<AggregatedMinCostRelocationCalculator.DrtZoneVehicleSurplus> vehicleSurpluses = zonalSystem.getZones().values().stream().map(z -> {
			int rebalancable = rebalancableVehiclesPerZone.getOrDefault(z, List.of()).size();
			int soonIdle = soonIdleVehiclesPerZone.getOrDefault(z, List.of()).size();

			// TODO: target from RL
			int target = 0;

			int surplus = Math.min(rebalancable + soonIdle - target, rebalancable);
			return new AggregatedMinCostRelocationCalculator.DrtZoneVehicleSurplus(z, surplus);
		}).collect(toList());

		return relocationCalculator.calcRelocations(vehicleSurpluses, rebalancableVehiclesPerZone);
	}
}
