#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import numpy as np
from attrs import asdict
from enum import Enum
from time import strftime

from mushroom_rl.core import Core
from mushroom_rl.utils.dataset import compute_J, compute_metrics

from drtrl import *
from drtrl.DrtEnvironment import DrtEnvironment, DrtObjective


class Algorithm(Enum):
    """ Defines the available training algorithms """

    dpg = DPG
    ddpg = DDPG
    sac = SAC
    a2c = A2C
    ac = AC
    ppo = PPO


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RL experiment")
    parser.add_argument("--host", type=str, default="localhost:5555", help="Address of MATSim host")
    parser.add_argument("--objective", type=DrtObjective, help="Objective type", default=DrtObjective.ZONE_TARGETS)
    parser.add_argument("--algorithm", type=str, choices=list(x.name.lower() for x in Algorithm),
                        help="Algorithm to run", required=True)
    parser.add_argument("--normalize", type=bool, default=False, action=argparse.BooleanOptionalAction,
                        help="Normalize action space")
    parser.add_argument("--eval", type=int, default=100, help="Evaluate each nth iteration")

    args = parser.parse_args()

    # MDP
    env = DrtEnvironment(args.host, args.objective, normalize_action_space=args.normalize)

    clazz = Algorithm[args.algorithm].value

    # Create instance
    algo: Base = clazz(env)

    print("Running", args.algorithm)
    print("Parameters", asdict(algo))

    agent = algo.create_agent(args)

    # Algorithm
    core = Core(agent, env)

    n_epochs = 1 + env.spec.iterations
    gamma_eval = 1.

    if algo.is_pretrained():
        # Fill the replay memory with random samples
        core.learn(n_episodes=5, n_steps_per_fit=5)

        # Subtract used epochs
        n_epochs -= 6

        dataset = core.evaluate(n_episodes=1, render=False)
        J = compute_J(dataset, gamma_eval)
        print('Epoch: 0')
        print('J: ', np.mean(J))

    print("Training for", n_epochs, "epochs")

    out = os.path.join("output", strftime("%Y%m%d-%H%M") + "_%s.csv" % args.algorithm)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    epoch = 0

    with open(out, "w") as f:

        f.write("epoch,mean_reward\n")

        while n_epochs > 0:

            n = min(n_epochs, args.eval)

            core.learn(n_episodes=n, n_steps_per_fit=5, render=False)

            n_epochs -= n
            epoch += n

            if n_epochs > 0:
                dataset = core.evaluate(n_episodes=1, render=False, quiet=True)
                metrics = compute_metrics(dataset, gamma_eval)
                J = compute_J(dataset, gamma_eval)
                n_epochs -= 1

                f.write("%d,%f\n" % (epoch, np.mean(J)))
                f.flush()
