#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ray
from ray import air, tune
from ray.tune.registry import get_trainable_cls

from drtrl.ManagedDrtEnvironment import ManagedDrtEnvironment, DrtObjective

if __name__ == "__main__":
    ray.init(local_mode=True)

    alg = "SAC"

    config = (
        get_trainable_cls(alg)
        .get_default_config()
        # or "corridor" if registered above
        .environment(ManagedDrtEnvironment,
                     env_config={"jar": "../../../matsim-drt-rl-1.x-SNAPSHOT-f1aa466-dirty.jar",
                                 "configPath": "../../../scenarios/cottbus/drt_cottbus.xml",
                                 "objective": DrtObjective.MIN_COST_FLOW},
                     normalize_actions=True)
        .framework("torch")
        .training(gamma=0.8)
        .rollouts(num_rollout_workers=0, num_envs_per_worker=1, create_env_on_local_worker=True)
        # Use GPUs iff `RLLIB_NUM_GPUS` env var set to > 0.
        .resources(num_gpus=0)
        .evaluation(evaluation_duration=5)
    )

    stop = {
        "training_iteration": 5,
    }

    #    config.lr = 1e-3
    #    algo = config.build(use_copy=False)

    # run manual training loop and print results after each iteration
    # for _ in range(5):
    #     result = algo.train()
    #     print(pretty_print(result))
    #
    # algo.evaluate()
    # algo.stop()
    #

    tuner = tune.Tuner(
        alg, param_space=config, run_config=air.RunConfig(stop=stop, verbose=1)
    )
    tuner.fit()

    ray.shutdown()
