package org.matsim.run;

import org.matsim.api.core.v01.Scenario;
import org.matsim.application.MATSimApplication;
import org.matsim.contrib.drt.routing.DrtRoute;
import org.matsim.contrib.drt.routing.DrtRouteFactory;
import org.matsim.contrib.drt.run.DrtConfigs;
import org.matsim.contrib.drt.run.MultiModeDrtConfigGroup;
import org.matsim.contrib.drt.run.MultiModeDrtModule;
import org.matsim.contrib.dvrp.run.DvrpConfigGroup;
import org.matsim.contrib.dvrp.run.DvrpModule;
import org.matsim.contrib.dvrp.run.DvrpQSimComponents;
import org.matsim.core.config.Config;
import org.matsim.core.config.ConfigGroup;
import org.matsim.core.controler.Controler;
import org.matsim.vis.otfvis.OTFVisConfigGroup;

import java.util.List;

/**
 * Run DRT scenario with rebalancing as defined in the config.
 */
public final class RunDrtScenario extends MATSimApplication {


	public RunDrtScenario() {
		super("scenarios/cottbus/drt_cottbus.xml");
	}

	public static void main(String[] args) {
		MATSimApplication.run(RunDrtScenario.class, args);
	}


	@Override
	protected List<ConfigGroup> getCustomModules() {
		return List.of(new MultiModeDrtConfigGroup(), new DvrpConfigGroup(), new OTFVisConfigGroup());
	}

	@Override
	protected Config prepareConfig(Config config) {

		MultiModeDrtConfigGroup multiModeDrtConfig = MultiModeDrtConfigGroup.get(config);
		DrtConfigs.adjustMultiModeDrtConfig(multiModeDrtConfig, config.planCalcScore(), config.plansCalcRoute());

		return config;
	}

	@Override
	protected void prepareScenario(Scenario scenario) {
		scenario.getPopulation()
			.getFactory()
			.getRouteFactories()
			.setRouteFactory(DrtRoute.class, new DrtRouteFactory());
	}

	@Override
	protected void prepareControler(Controler controler) {
		MultiModeDrtConfigGroup multiModeDrtConfig = MultiModeDrtConfigGroup.get(controler.getConfig());

		controler.addOverridingModule(new DvrpModule());
		controler.addOverridingModule(new MultiModeDrtModule());
		controler.configureQSimComponents(DvrpQSimComponents.activateAllModes(multiModeDrtConfig));
	}
}
