# -*- coding: utf-8 -*-

import numpy as np
import grpc

from mushroom_rl.core import Environment, MDPInfo
from mushroom_rl.utils.spaces import Box

from .server.rebalancer_pb2_grpc import RebalancingStrategyStub

class DrtEnvironment(Environment):
    """ Environment for DRT Rebalancing"""

    def __init__(self, server):

        channel = grpc.insecure_channel(server)
        stub = RebalancingStrategyStub(channel)


        # only time is observed
        self.observation_space = Box(low=0, high=1, shape=(1,))

        self.action_space = Box(low=0, high=1, shape=(len(zones),))

        mdp_info = MDPInfo(self.observation_space, self.action_space, gamma=0.99, horizon=100)
        super().__init__(mdp_info)

    def step(self, action):
        return self._state, reward, end, {}


    def reset(self, state=None):
        if state is None:
            self._state = np.zeros(1)
        else:
            self._state = state

        return self._state