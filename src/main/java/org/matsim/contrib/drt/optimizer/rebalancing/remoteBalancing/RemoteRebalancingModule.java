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

import org.matsim.contrib.drt.analysis.zonal.DrtZonalSystem;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingParams;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingStrategy;
import org.matsim.contrib.drt.optimizer.rebalancing.mincostflow.ZonalRelocationCalculator;
import org.matsim.contrib.drt.run.DrtConfigGroup;
import org.matsim.contrib.dvrp.fleet.Fleet;
import org.matsim.contrib.dvrp.run.AbstractDvrpModeModule;
import org.matsim.contrib.dvrp.run.AbstractDvrpModeQSimModule;


/**
 * Module to install remote balancing functionality.
 */
public class RemoteRebalancingModule extends AbstractDvrpModeModule {

	private final DrtConfigGroup drtCfg;


	public RemoteRebalancingModule(DrtConfigGroup drtCfg) {
		super(drtCfg.getMode());
		this.drtCfg = drtCfg;
	}


	@Override
	public void install() {
		RebalancingParams params = drtCfg.getRebalancingParams().orElseThrow();

		RemoteRebalancingParams strategyParams = (RemoteRebalancingParams) params.getRebalancingStrategyParams();

		bindModal(RemoteRebalancingParams.class).toInstance(strategyParams);
		addControlerListenerBinding().toProvider(modalProvider(getter -> getter.getModal(RemoteRebalancingConnectionManager.class))).asEagerSingleton();

		installQSimModule(new AbstractDvrpModeQSimModule(this.getMode()) {
			@Override
			protected void configureQSim() {
				bindModal(RebalancingStrategy.class).toProvider(modalProvider(
					getter -> new RemoteRebalancingStrategy(
						getter.getModal(RemoteRebalancingConnectionManager.class),
						getter.getModal(DrtZonalSystem.class),
						getter.getModal(Fleet.class),
						getter.getModal(ZonalRelocationCalculator.class)))).asEagerSingleton();
			}
		});
	}
}
