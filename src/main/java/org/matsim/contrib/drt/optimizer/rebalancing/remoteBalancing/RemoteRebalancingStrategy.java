package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
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

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;


/**
 * Implements the remote balancing strategy, which will receive rebalancing instructions from an external service.
 */
public class RemoteRebalancingStrategy implements RebalancingStrategy {

	private static final Logger log = LogManager.getLogger(RemoteRebalancingStrategy.class);

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

		Rebalancer.RebalancingState state = server.setCurrentState(time, rebalancableVehiclesPerZone);

		// Check if last time step was signaled
		if (state.getSimulationEnded())
			return List.of();

		List<AggregatedMinCostRelocationCalculator.DrtZoneVehicleSurplus> surpluses = new ArrayList<>();
		Rebalancer.RebalancingInstructions targets = server.waitForInstructions(time);

		if (targets.getTargetsCount() != zonalSystem.getZones().size()) {
			log.error("Invalid number of targets in rebalancing instruction: {}", targets.getTargetsCount());
			return List.of();
		}

		int i = 0;
		for (DrtZone z : zonalSystem.getZones().values()) {
			int target = targets.getTargets(i++);

			int rebalancable = rebalancableVehiclesPerZone.getOrDefault(z, List.of()).size();
			int soonIdle = soonIdleVehiclesPerZone.getOrDefault(z, List.of()).size();

			int surplus = Math.min(rebalancable + soonIdle - target, rebalancable);

			surpluses.add(new AggregatedMinCostRelocationCalculator.DrtZoneVehicleSurplus(z, surplus));
		}


		return relocationCalculator.calcRelocations(surpluses, rebalancableVehiclesPerZone);
	}
}
