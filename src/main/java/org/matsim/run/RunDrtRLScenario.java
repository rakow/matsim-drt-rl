package org.matsim.run;

import net.bytebuddy.ByteBuddy;
import net.bytebuddy.agent.ByteBuddyAgent;
import net.bytebuddy.dynamic.loading.ClassReloadingStrategy;
import net.bytebuddy.implementation.FixedValue;
import org.matsim.api.core.v01.Scenario;
import org.matsim.application.MATSimApplication;
import org.matsim.contrib.drt.optimizer.rebalancing.RebalancingModule;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.RemoteRebalancingModule;
import org.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.RemoteRebalancingParams;
import org.matsim.contrib.drt.routing.DrtRoute;
import org.matsim.contrib.drt.routing.DrtRouteFactory;
import org.matsim.contrib.drt.run.DrtConfigGroup;
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
import picocli.CommandLine;

import java.io.IOException;
import java.net.ConnectException;
import java.net.Socket;
import java.util.List;

import static net.bytebuddy.matcher.ElementMatchers.named;

/**
 * Main class to run a scenario with remote balancing.
 */
public final class RunDrtRLScenario extends MATSimApplication {

	@CommandLine.Option(names = "--port", description = "Base port to run on", defaultValue = "5555")
	private int port;

	public RunDrtRLScenario() {
		super("scenarios/cottbus/drt_cottbus.xml");
	}

	public static void main(String[] args) {
		patchModules();
		MATSimApplication.run(RunDrtRLScenario.class, args);
	}

	/**
	 * It is not possible with DRT to define custom rebalancing that is not in the core. This method does some byte modifications to patches this
	 */
	public static void patchModules() {
		ByteBuddyAgent.install();

		// TODO: core needs to be changed to allow this without byte patching

		// RebalancingModule is basically changed to do nothing
		new ByteBuddy()
			.redefine(RebalancingModule.class)
			.method(named("install"))
			.intercept(FixedValue.originType())
			.make()
			.load(
				RebalancingModule.class.getClassLoader(),
				ClassReloadingStrategy.fromInstalledAgent());
	}

	private static boolean portAvailable(int port) throws IllegalStateException {
		try (Socket ignored = new Socket("localhost", port)) {
			return false;
		} catch (ConnectException e) {
			return true;
		} catch (IOException e) {
			throw new IllegalStateException("Error while trying to check open port", e);
		}
	}

	@Override
	protected List<ConfigGroup> getCustomModules() {
		return List.of(new MultiModeDrtConfigGroup(), new DvrpConfigGroup(), new OTFVisConfigGroup());
	}

	@Override
	protected Config prepareConfig(Config config) {

		MultiModeDrtConfigGroup multiModeDrtConfig = MultiModeDrtConfigGroup.get(config);
		DrtConfigs.adjustMultiModeDrtConfig(multiModeDrtConfig, config.planCalcScore(), config.plansCalcRoute());

		config.controler().setOutputDirectory(config.controler().getOutputDirectory() + "-rl");

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

		int port = this.port;
		for (DrtConfigGroup drtConfig : multiModeDrtConfig.getModalElements()) {

			RemoteRebalancingParams p = new RemoteRebalancingParams();
			p.port = port++;

			if (!portAvailable(port))
				throw new IllegalStateException("The port " + port + " is not available.");

			controler.addOverridingModule(new RemoteRebalancingModule(drtConfig, p));
		}

	}
}
