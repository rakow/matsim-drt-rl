#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import torch.nn.functional as F
import torch.optim as optim
from attrs import define
from mushroom_rl.algorithms.actor_critic import DDPG as MDDPG
from mushroom_rl.core import Agent
from mushroom_rl.policy import OrnsteinUhlenbeckPolicy

from .DrtEnvironment import DrtObjective
from .base import Base
from .nn import get_critic_net, get_actor_net

@define
class DDPG(Base):

    def is_pretrained(self):
        return True

    def create_agent(self, args) -> Agent:
        # Policy
        policy_class = OrnsteinUhlenbeckPolicy
        policy_params = dict(sigma=np.ones(1) * .2, theta=.15, dt=1e-2)

        # Settings
        n_steps = self.env.spec.endTime // self.env.spec.interval

        print("Steps per episode", n_steps)

        initial_replay_size = 5 * n_steps
        max_replay_size = 5000
        batch_size = 200
        n_features = 80 if self.env.objective == DrtObjective.ZONE_TARGETS else 40
        tau = .001

        # Approximator
        actor_input_shape = self.env.info.observation_space.shape
        actor_params = dict(network=get_actor_net(args),
                            n_features=n_features,
                            upper_bound=self.env.info.action_space.high[0],  # same upper bound for both
                            input_shape=actor_input_shape,
                            output_shape=self.env.info.action_space.shape)

        actor_optimizer = {'class': optim.Adam,
                           'params': {'lr': 1e-5}}

        critic_input_shape = (actor_input_shape[0] + self.env.info.action_space.shape[0],)
        critic_params = dict(network=get_critic_net(args),
                             optimizer={'class': optim.Adam,
                                        'params': {'lr': 1e-3}},
                             loss=F.mse_loss,
                             n_features=n_features,
                             input_shape=critic_input_shape,
                             output_shape=(1,))

        # Agent
        return MDDPG(self.env.info, policy_class, policy_params,
                     actor_params, actor_optimizer, critic_params,
                     batch_size, initial_replay_size, max_replay_size,
                     tau)
