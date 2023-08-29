# -*- coding: utf-8 -*-

import numpy as np

from mushroom_rl.algorithms.actor_critic import COPDAC_Q
from mushroom_rl.approximators import Regressor
from mushroom_rl.approximators.parametric import LinearApproximator
from mushroom_rl.core.agent import Agent
from mushroom_rl.features import Features
from mushroom_rl.features.tiles import Tiles
from mushroom_rl.policy import GaussianPolicy
from mushroom_rl.utils.parameters import Parameter

from attrs import define

from .base import Base


@define
class DPG(Base):
    n_tilings: int = 10

    def create_agent(self) -> Agent:
        alpha_theta = Parameter(5e-3 / self.n_tilings)
        alpha_omega = Parameter(0.5 / self.n_tilings)
        alpha_v = Parameter(0.5 / self.n_tilings)
        tilings = Tiles.generate(self.n_tilings, [10, 10],
                                 self.env.info.observation_space.low,
                                 self.env.info.observation_space.high + 1e-3)

        phi = Features(tilings=tilings)

        input_shape = (phi.size,)

        n_actions = self.env.info.action_space.shape[0]

        mu = Regressor(LinearApproximator,
                       input_shape=input_shape,
                       output_shape=self.env.info.action_space.shape,
                       n_actions=n_actions)

        sigma = 1e-1 * np.eye(n_actions)
        policy = GaussianPolicy(mu, sigma)

        agent = COPDAC_Q(self.env.info, policy, mu,
                         alpha_theta, alpha_omega, alpha_v,
                         value_function_features=phi,
                         policy_features=phi)

        return agent
