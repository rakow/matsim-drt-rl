#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import os
from attrs import asdict
from enum import Enum
from json import dump
from mushroom_rl.core import Core
from mushroom_rl.utils.dataset import compute_J, compute_metrics
from time import strftime

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
    parser.add_argument("--output", type=str, help="Path to output csv")
    parser.add_argument("--algorithm", type=str, choices=list(x.name.lower() for x in Algorithm),
                        help="Algorithm to run", required=True)
    parser.add_argument("--eval", type=int, default=100, help="Evaluate each nth iteration")
    parser.add_argument("--normalize", type=bool, default=False, action=argparse.BooleanOptionalAction,
                        help="Normalize action space")
    parser.add_argument("--std-init", type=float, default=0.1, help="Standard deviation for exploration")
    parser.add_argument("--actor-network", type=str, default="dense", choices=["dense", "gumbel", "regression"])
    parser.add_argument("--critic-network", type=str, default="dense", choices=["dense"])

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

    # keep track of matsim iteration number, 0th iteration is not used by RL
    n_matsim = 1

    if algo.is_pretrained():
        # Fill the replay memory with random samples
        core.learn(n_episodes=5, n_steps_per_fit=5)

        # Subtract used epochs
        n_epochs -= 6
        n_matsim += 6

        dataset = core.evaluate(n_episodes=1, render=False)
        J = compute_J(dataset, gamma_eval)
        print('Epoch: 0')
        print('J: ', np.mean(J))

    print("Training for", n_epochs, "epochs")

    if args.output is None:
        out = os.path.join("output", strftime("%Y%m%d-%H%M") + "_%s.csv" % args.algorithm)
    else:
        out = args.output

    with open(out.replace(".csv", ".json"), "w") as f:
        dump(vars(args), f, default=str, indent=4)

    os.makedirs(os.path.dirname(out), exist_ok=True)

    epoch = 0

    with open(out, "w") as f:

        f.write("epoch,matsim_iteration,mean_reward\n")

        while n_epochs > 0:

            n = min(n_epochs, args.eval)

            # Do one less train epoch, so that the last one is always evaluation
            if n == n_epochs:
                n -= 1

            core.learn(n_episodes=n, n_steps_per_fit=5, render=False)

            n_epochs -= n
            n_matsim += n
            epoch += n

            if n_epochs > 0:
                dataset = core.evaluate(n_episodes=1, render=False, quiet=True)
                metrics = compute_metrics(dataset, gamma_eval)
                J = compute_J(dataset, gamma_eval)
                n_epochs -= 1
                n_matsim += 1

                f.write("%d,%d,%f\n" % (epoch, n_matsim, np.mean(J)))
                f.flush()
