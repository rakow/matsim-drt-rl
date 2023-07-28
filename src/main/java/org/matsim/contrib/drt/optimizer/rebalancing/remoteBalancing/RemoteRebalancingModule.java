/*
 * *********************************************************************** *
 * project: org.matsim.*
 * *********************************************************************** *
 *                                                                         *
 * copyright       : (C) 2018 by the members listed in the COPYING,        *
 *                   LICENSE and WARRANTY file.                            *
 * email           : info at matsim dot org                                *
 *                                                                         *
 * *********************************************************************** *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *   See also COPYING, LICENSE and WARRANTY file                           *
 *                                                                         *
 * *********************************************************************** *
 */

package org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing;

import org.matsim.contrib.drt.analysis.DrtEventSequenceCollector;
import org.matsim.contrib.drt.analysis.zonal.DrtModeZonalSystemModule;
import org.matsim.contrib.drt.analysis.zonal.DrtZonalSystem;
import org.matsim.contrib.drt.analysis.zonal.DrtZoneTargetLinkSelector;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingStrategy;
import org.matsim.contrib.drt.optimizer.rebalancing.demandestimator.PreviousIterationDrtDemandEstimator;
import org.matsim.contrib.drt.optimizer.rebalancing.demandestimator.ZonalDemandEstimator;
import org.matsim.contrib.drt.optimizer.rebalancing.mincostflow.AggregatedMinCostRelocationCalculator;
import org.matsim.contrib.drt.optimizer.rebalancing.mincostflow.ZonalRelocationCalculator;
import org.matsim.contrib.drt.optimizer.rebalancing.targetcalculator.DemandEstimatorAsTargetCalculator;
import org.matsim.contrib.drt.optimizer.rebalancing.targetcalculator.RebalancingTargetCalculator;
import org.matsim.contrib.drt.run.DrtConfigGroup;
import org.matsim.contrib.dvrp.fleet.Fleet;
import org.matsim.contrib.dvrp.fleet.FleetSpecification;
import org.matsim.contrib.dvrp.run.AbstractDvrpModeModule;
import org.matsim.contrib.dvrp.run.AbstractDvrpModeQSimModule;
import org.matsim.core.config.Config;


/**
 * Module to install remote balancing functionality.
 */
public class RemoteRebalancingModule extends AbstractDvrpModeModule {

	private final DrtConfigGroup drtCfg;
	private final int port;


	public RemoteRebalancingModule(DrtConfigGroup drtCfg, int port) {
		super(drtCfg.getMode());
		this.drtCfg = drtCfg;
		this.port = port;
	}


	@Override
	public void install() {
		RebalancingParams params = drtCfg.getRebalancingParams().orElseThrow();

		// Is only needed because it is not bound via the normal rebalancing
		{
			install(new DrtModeZonalSystemModule(drtCfg));
			bindModal(ZonalRelocationCalculator.class).toProvider(modalProvider(
				getter -> new AggregatedMinCostRelocationCalculator(
					getter.getModal(DrtZoneTargetLinkSelector.class)))).asEagerSingleton();
		}

		bindModal(PreviousIterationDrtDemandEstimator.class).toProvider(modalProvider(
			getter -> new PreviousIterationDrtDemandEstimator(getter.getModal(DrtZonalSystem.class), drtCfg, params.interval))).asEagerSingleton();
		bindModal(ZonalDemandEstimator.class).to(modalKey(PreviousIterationDrtDemandEstimator.class));
		addEventHandlerBinding().to(modalKey(PreviousIterationDrtDemandEstimator.class));

		bindModal(ConnectionManager.class).toProvider(modalProvider(getter -> new ConnectionManager(
			port, getter.get(Config.class), params, getter.getModal(DrtZonalSystem.class),
			getter.getModal(FleetSpecification.class), getter.getModal(DrtEventSequenceCollector.class), getter.getModal(ZonalDemandEstimator.class)
		))).asEagerSingleton();

		addControlerListenerBinding().to(modalKey(ConnectionManager.class));

		// Only used with min cost flow
		bindModal(RebalancingTargetCalculator.class).toProvider(modalProvider(getter -> new DemandEstimatorAsTargetCalculator(
			getter.getModal(ZonalDemandEstimator.class), params.interval))).asEagerSingleton();

		installQSimModule(new AbstractDvrpModeQSimModule(this.getMode()) {
			@Override
			protected void configureQSim() {
				bindModal(RebalancingStrategy.class).toProvider(modalProvider(
					getter -> new RemoteRebalancingStrategy(
						getter.getModal(ConnectionManager.class),
						getter.getModal(DrtZonalSystem.class),
						getter.getModal(Fleet.class),
						getter.getModal(RebalancingTargetCalculator.class),
						getter.getModal(ZonalRelocationCalculator.class),
						params))).asEagerSingleton();
			}
		});
	}
}
