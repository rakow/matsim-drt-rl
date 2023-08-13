#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from enum import Enum

import numpy as np
from attrs import asdict

from mushroom_rl.core import Core
from mushroom_rl.utils.dataset import compute_J


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

    args = parser.parse_args()

    # MDP
    env = DrtEnvironment(args.host, args.objective)

    clazz = Algorithm[args.algorithm].value

    # Create instance
    algo: Base = clazz(env)

    print("Running", args.algorithm)
    print("Parameters", asdict(algo))

    agent = algo.create_agent()

    # Algorithm
    core = Core(agent, env)

    n_eval = 3
    n_epochs = 1 + env.spec.iterations - n_eval
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

    core.learn(n_episodes=n_epochs, n_steps_per_fit=5, render=False)

    # Evaluate results during last iterations
    for n in range(n_eval):
        dataset = core.evaluate(n_episodes=1, render=False)
        J = compute_J(dataset, gamma_eval)
        print('J: ', np.mean(J))