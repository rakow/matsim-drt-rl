# -*- coding: utf-8 -*-

import torch
import torch.nn.functional as F
import torch.optim as optim
from attrs import define
from mushroom_rl.algorithms.actor_critic import SAC as MSAC
from mushroom_rl.core import Agent

from .base import Base
from .nn import get_actor_net, get_critic_net, DenseNetwork, DenseCriticNetwork


@define
class SAC(Base):

    def is_pretrained(self):
        return True

    def create_agent(self, args) -> Agent:
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
        actor_mu_params = dict(network=get_actor_net(args),
                               n_features=n_features,
                               input_shape=actor_input_shape,
                               output_shape=self.env.info.action_space.shape,
                               use_cuda=use_cuda)
        actor_sigma_params = dict(network=DenseNetwork,
                                  n_features=n_features,
                                  input_shape=actor_input_shape,
                                  output_shape=self.env.info.action_space.shape,
                                  use_cuda=use_cuda)

        actor_optimizer = {'class': optim.Adam,
                           'params': {'lr': 3e-4}}

        critic_input_shape = (actor_input_shape[0] + self.env.info.action_space.shape[0],)
        critic_params = dict(network=get_critic_net(args),
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
