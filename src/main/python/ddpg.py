#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from mushroom_rl.algorithms.actor_critic import DDPG
from mushroom_rl.core import Core
from mushroom_rl.policy import OrnsteinUhlenbeckPolicy
from mushroom_rl.utils.dataset import compute_J

from drtrl.DrtEnvironment import DrtEnvironment, DrtObjective


class CriticNetwork(nn.Module):
    def __init__(self, input_shape, output_shape, n_features, **kwargs):
        super().__init__()

        n_input = input_shape[-1]
        n_output = output_shape[0]

        self._h1 = nn.Linear(n_input, n_features)
        self._h2 = nn.Linear(n_features, n_features)
        self._h3 = nn.Linear(n_features, n_output)

        nn.init.xavier_uniform_(self._h1.weight,
                                gain=nn.init.calculate_gain('relu'))
        nn.init.xavier_uniform_(self._h2.weight,
                                gain=nn.init.calculate_gain('relu'))
        nn.init.xavier_uniform_(self._h3.weight,
                                gain=nn.init.calculate_gain('linear'))

    def forward(self, state, action):
        state_action = torch.cat((state.float(), action.float()), dim=1)
        features1 = F.relu(self._h1(state_action))
        features2 = F.relu(self._h2(features1))
        q = self._h3(features2)

        return torch.squeeze(q)


class ActorNetwork(nn.Module):
    def __init__(self, input_shape, output_shape, n_features, upper_bound, **kwargs):
        super(ActorNetwork, self).__init__()

        n_input = input_shape[-1]
        n_output = output_shape[0]

        self.upper_bound = upper_bound / 2
        self._h1 = nn.Linear(n_input, n_features)
        self._h2 = nn.Linear(n_features, n_features)
        self._h3 = nn.Linear(n_features, n_output)

        nn.init.xavier_uniform_(self._h1.weight,
                                gain=nn.init.calculate_gain('relu'))
        nn.init.xavier_uniform_(self._h2.weight,
                                gain=nn.init.calculate_gain('relu'))
        nn.init.xavier_uniform_(self._h3.weight,
                                gain=nn.init.calculate_gain('tanh'))

    def forward(self, state):
        features1 = F.relu(self._h1(torch.squeeze(state, 1).float()))
        features2 = F.relu(self._h2(features1))

        # Scale action space to sensible value
        a = (torch.tanh(self._h3(features2)) + 1) * self.upper_bound

        return a


if __name__ == "__main__":

    # MDP
    env = DrtEnvironment("localhost:5555")

    horizon = env.info.horizon
    gamma = env.info.gamma
    gamma_eval = 1.

    # Policy
    policy_class = OrnsteinUhlenbeckPolicy
    policy_params = dict(sigma=np.ones(1) * .2, theta=.15, dt=1e-2)

    # Settings
    n_steps = env.spec.endTime // env.spec.interval

    print("Steps per episode", n_steps)

    initial_replay_size = 5 * n_steps
    max_replay_size = 5000
    batch_size = 200
    n_features = 80 if env.objective == DrtObjective.ZONE_TARGETS else 40
    tau = .001

    # Approximator
    actor_input_shape = env.info.observation_space.shape
    actor_params = dict(network=ActorNetwork,
                        n_features=n_features,
                        upper_bound=env.spec.fleetSize if env.objective == DrtObjective.ZONE_TARGETS else 3,
                        input_shape=actor_input_shape,
                        output_shape=env.info.action_space.shape)

    actor_optimizer = {'class': optim.Adam,
                       'params': {'lr': 1e-5}}

    critic_input_shape = (actor_input_shape[0] + env.info.action_space.shape[0],)
    critic_params = dict(network=CriticNetwork,
                         optimizer={'class': optim.Adam,
                                    'params': {'lr': 1e-3}},
                         loss=F.mse_loss,
                         n_features=n_features,
                         input_shape=critic_input_shape,
                         output_shape=(1,))

    # Agent
    agent = DDPG(env.info, policy_class, policy_params,
                 actor_params, actor_optimizer, critic_params,
                 batch_size, initial_replay_size, max_replay_size,
                 tau)

    # Algorithm
    core = Core(agent, env)

    # Fill the replay memory with random samples
    core.learn(n_episodes=5, n_steps_per_fit=5)

    # RUN
    # subtract  evaluate iterations
    n_eval = 4
    n_epochs = 1 + env.spec.iterations - 5 - n_eval

    dataset = core.evaluate(n_episodes=1, render=False)
    J = compute_J(dataset, gamma_eval)
    print('Epoch: 0')
    print('J: ', np.mean(J))

    core.learn(n_episodes=n_epochs, n_episodes_per_fit=1, render=False)

    # Evaluate results during last iterations
    for n in range(1, n_eval):
        dataset = core.evaluate(n_episodes=1, render=False)
        J = compute_J(dataset, gamma_eval)
        print('J: ', np.mean(J))
