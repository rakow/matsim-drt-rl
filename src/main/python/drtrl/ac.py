# -*- coding: utf-8 -*-

import numpy as np
from attrs import define
from mushroom_rl.algorithms.actor_critic import StochasticAC_AVG
from mushroom_rl.approximators import Regressor
from mushroom_rl.approximators.parametric import LinearApproximator
from mushroom_rl.core import Agent
from mushroom_rl.features import Features
from mushroom_rl.features.tiles import Tiles
from mushroom_rl.policy import StateLogStdGaussianPolicy
from mushroom_rl.utils.parameters import Parameter

from .base import Base


@define
class AC(Base):
    n_tilings: int = 11

    def create_agent(self, args) -> Agent:
        alpha_r = Parameter(.0001)
        alpha_theta = Parameter(.001 / self.n_tilings)
        alpha_v = Parameter(.1 / self.n_tilings)
        tilings = Tiles.generate(self.n_tilings - 1, [10] * self.env.info.observation_space.low.shape[0],
                                 self.env.info.observation_space.low,
                                 self.env.info.observation_space.high + 1e-3)

        phi = Features(tilings=tilings)

        tilings_v = tilings + Tiles.generate(1, [1, 1],
                                             self.env.info.observation_space.low,
                                             self.env.info.observation_space.high + 1e-3)
        psi = Features(tilings=tilings_v)

        input_shape = (phi.size,)

        mu = Regressor(LinearApproximator, input_shape=input_shape,
                       output_shape=self.env.info.action_space.shape)

        std = Regressor(LinearApproximator, input_shape=input_shape,
                        output_shape=self.env.info.action_space.shape)

        std_0 = np.sqrt(1.)
        std.set_weights(np.log(std_0) / self.n_tilings * np.ones(std.weights_size))

        policy = StateLogStdGaussianPolicy(mu, std)

        agent = StochasticAC_AVG(self.env.info, policy,
                                 alpha_theta, alpha_v, alpha_r,
                                 lambda_par=.5,
                                 value_function_features=psi,
                                 policy_features=phi)

        return agent
