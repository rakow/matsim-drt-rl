# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from attrs import define
from mushroom_rl.algorithms.actor_critic import PPO as MPPO
from mushroom_rl.core import Agent
from mushroom_rl.policy import GaussianTorchPolicy

from .base import Base


class Network(nn.Module):
    def __init__(self, input_shape, output_shape, n_features, **kwargs):
        super(Network, self).__init__()

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

    def forward(self, state, **kwargs):
        features1 = F.relu(self._h1(torch.squeeze(state, 1).float()))
        features2 = F.relu(self._h2(features1))
        a = 1 + self._h3(features2)

        return a


@define
class PPO(Base):

    def create_agent(self) -> Agent:

        policy_params = dict(
            std_0=1.,
            n_features=32,
            use_cuda=torch.cuda.is_available()

        )

        ppo_params = dict(actor_optimizer={'class': optim.Adam,
                                           'params': {'lr': 3e-4}},
                          n_epochs_policy=4,
                          batch_size=64,
                          eps_ppo=.2,
                          lam=.95)

        critic_params = dict(network=Network,
                             optimizer={'class': optim.Adam,
                                        'params': {'lr': 3e-4}},
                             loss=F.mse_loss,
                             n_features=32,
                             batch_size=64,
                             input_shape=self.env.info.observation_space.shape,
                             output_shape=(1,))

        policy = GaussianTorchPolicy(Network,
                                     self.env.info.observation_space.shape,
                                     self.env.info.action_space.shape,
                                     **policy_params)

        ppo_params['critic_params'] = critic_params

        return MPPO(self.env.info, policy, **ppo_params)
