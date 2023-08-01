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
import org.matsim.contrib.drt.optimizer.rebalancing.targetcalculator.RebalancingTargetCalculator;
import org.matsim.contrib.dvrp.fleet.DvrpVehicle;
import org.matsim.contrib.dvrp.fleet.Fleet;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.ToDoubleFunction;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;


/**
 * Implements the remote balancing strategy, which will receive rebalancing instructions from an external service.
 */
public class RemoteRebalancingStrategy implements RebalancingStrategy {

	private static final Logger log = LogManager.getLogger(RemoteRebalancingStrategy.class);

	private final ConnectionManager server;
	private final DrtZonalSystem zonalSystem;
	private final Fleet fleet;
	private final RebalancingTargetCalculator rebalancingTargetCalculator;
	private final ZonalRelocationCalculator relocationCalculator;
	private final RebalancingParams params;
	private final RemoteRebalancingParams remoteParams;

	public RemoteRebalancingStrategy(ConnectionManager server, DrtZonalSystem zonalSystem, Fleet fleet,
									 RebalancingTargetCalculator rebalancingTargetCalculator,
									 ZonalRelocationCalculator relocationCalculator,
									 RebalancingParams params, RemoteRebalancingParams remoteParams) {
		this.server = server;
		this.zonalSystem = zonalSystem;
		this.fleet = fleet;
		this.rebalancingTargetCalculator = rebalancingTargetCalculator;
		this.relocationCalculator = relocationCalculator;
		this.params = params;
		this.remoteParams = remoteParams;
	}

	@Override
	public List<Relocation> calcRelocations(Stream<? extends DvrpVehicle> rebalancableVehicles, double time) {

		Map<DrtZone, List<DvrpVehicle>> rebalancableVehiclesPerZone = RebalancingUtils.groupRebalancableVehicles(
			zonalSystem, params, rebalancableVehicles, time);

		Map<DrtZone, List<DvrpVehicle>> soonIdleVehiclesPerZone = RebalancingUtils.groupSoonIdleVehicles(zonalSystem,
			params, fleet, time);

		// No rebalancing before start and after end
		if (time < remoteParams.startRebalancing || time > remoteParams.endRebalancing)
			return List.of();

		Rebalancer.RebalancingState state = server.setCurrentState(time, rebalancableVehiclesPerZone);

		// Check if last time step was signaled
		if (state.getSimulationEnded())
			return List.of();

		Rebalancer.RebalancingInstructions cmd = server.waitForInstructions(time);

		if (cmd.hasZoneTargets()) {
			return calculateRebalanceTargets(cmd.getZoneTargets(), rebalancableVehiclesPerZone, soonIdleVehiclesPerZone);
		} else if (cmd.hasMinCostFlow()) {
			return calculateMinCostRelocations(cmd.getMinCostFlow(), time, rebalancableVehiclesPerZone, soonIdleVehiclesPerZone);
		}

		log.warn("No rebalancing method was given.");
		return List.of();
	}


	private List<Relocation> calculateRebalanceTargets(Rebalancer.RebalancingInstructions.ZoneTargets targets,
													   Map<DrtZone, List<DvrpVehicle>> rebalancableVehiclesPerZone,
													   Map<DrtZone, List<DvrpVehicle>> soonIdleVehiclesPerZone) {
		if (targets.getVehiclesCount() != zonalSystem.getZones().size()) {
			log.error("Invalid number of targets in rebalancing instruction: {}", targets.getVehiclesCount());
			return List.of();
		}

		List<AggregatedMinCostRelocationCalculator.DrtZoneVehicleSurplus> surpluses = new ArrayList<>();

		int i = 0;
		for (DrtZone z : zonalSystem.getZones().values()) {
			int target = targets.getVehicles(i++);

			int rebalancable = rebalancableVehiclesPerZone.getOrDefault(z, List.of()).size();
			int soonIdle = soonIdleVehiclesPerZone.getOrDefault(z, List.of()).size();

			int surplus = Math.min(rebalancable + soonIdle - target, rebalancable);

			surpluses.add(new AggregatedMinCostRelocationCalculator.DrtZoneVehicleSurplus(z, surplus));
		}


		return relocationCalculator.calcRelocations(surpluses, rebalancableVehiclesPerZone);
	}

	private List<Relocation> calculateMinCostRelocations(Rebalancer.RebalancingInstructions.MinCostFlow minCostFlow, double time,
														 Map<DrtZone, List<DvrpVehicle>> rebalancableVehiclesPerZone,
														 Map<DrtZone, List<DvrpVehicle>> soonIdleVehiclesPerZone) {

		ToDoubleFunction<DrtZone> targetFunction = rebalancingTargetCalculator.calculate(time, rebalancableVehiclesPerZone);
		double alpha = minCostFlow.getAlpha();
		double beta = minCostFlow.getBeta();

		log.info("Received alpha={}, beta={}", alpha, beta);

		List<AggregatedMinCostRelocationCalculator.DrtZoneVehicleSurplus> vehicleSurpluses = zonalSystem.getZones().values().stream().map(z -> {
			int rebalancable = rebalancableVehiclesPerZone.getOrDefault(z, List.of()).size();
			int soonIdle = soonIdleVehiclesPerZone.getOrDefault(z, List.of()).size();
			int target = (int) Math.floor(alpha * targetFunction.applyAsDouble(z) + beta);
			int surplus = Math.min(rebalancable + soonIdle - target, rebalancable);
			return new AggregatedMinCostRelocationCalculator.DrtZoneVehicleSurplus(z, surplus);
		}).collect(toList());

		return relocationCalculator.calcRelocations(vehicleSurpluses, rebalancableVehiclesPerZone);
	}


}
