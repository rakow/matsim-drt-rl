# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from attrs import define
from mushroom_rl.algorithms.actor_critic import SAC as MSAC
from mushroom_rl.core import Agent

from .base import Base


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
    def __init__(self, input_shape, output_shape, n_features, **kwargs):
        super(ActorNetwork, self).__init__()

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

    def forward(self, state):
        features1 = F.relu(self._h1(torch.squeeze(state, 1).float()))
        features2 = F.relu(self._h2(features1))
        a = self._h3(features2)

        return a


@define
class SAC(Base):

    def is_pretrained(self):
        return True

    def create_agent(self) -> Agent:
        # Settings
        initial_replay_size = 64
        max_replay_size = 50000
        batch_size = 64
        n_features = 64
        warmup_transitions = 100
        tau = 0.005
        lr_alpha = 3e-4

        use_cuda = torch.cuda.is_available()

        # Approximator
        actor_input_shape = self.env.info.observation_space.shape
        actor_mu_params = dict(network=ActorNetwork,
                               n_features=n_features,
                               input_shape=actor_input_shape,
                               output_shape=self.env.info.action_space.shape,
                               use_cuda=use_cuda)
        actor_sigma_params = dict(network=ActorNetwork,
                                  n_features=n_features,
                                  input_shape=actor_input_shape,
                                  output_shape=self.env.info.action_space.shape,
                                  use_cuda=use_cuda)

        actor_optimizer = {'class': optim.Adam,
                           'params': {'lr': 3e-4}}

        critic_input_shape = (actor_input_shape[0] + self.env.info.action_space.shape[0],)
        critic_params = dict(network=CriticNetwork,
                             optimizer={'class': optim.Adam,
                                        'params': {'lr': 3e-4}},
                             loss=F.mse_loss,
                             n_features=n_features,
                             input_shape=critic_input_shape,
                             output_shape=(1,),
                             use_cuda=use_cuda)

        # Agent
        return MSAC(self.env.info, actor_mu_params, actor_sigma_params,
                   actor_optimizer, critic_params, batch_size, initial_replay_size,
                   max_replay_size, warmup_transitions, tau, lr_alpha,
                   critic_fit_params=None)
