# -*- coding: utf-8 -*-

import torch
import torch.nn.functional as F
import torch.optim as optim
from attrs import define
from mushroom_rl.algorithms.actor_critic import PPO as MPPO
from mushroom_rl.core import Agent
from mushroom_rl.policy import GaussianTorchPolicy

from .base import Base
from .nn import DenseNetwork, get_actor_net


@define
class PPO(Base):

    def create_agent(self, args) -> Agent:
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

        critic_params = dict(network=DenseNetwork,
                             optimizer={'class': optim.Adam,
                                        'params': {'lr': 3e-4}},
                             loss=F.mse_loss,
                             n_features=32,
                             batch_size=64,
                             input_shape=self.env.info.observation_space.shape,
                             output_shape=(1,))

        policy = GaussianTorchPolicy(get_actor_net(args),
                                     self.env.info.observation_space.shape,
                                     self.env.info.action_space.shape,
                                     **policy_params)

        ppo_params['critic_params'] = critic_params

        return MPPO(self.env.info, policy, **ppo_params)
