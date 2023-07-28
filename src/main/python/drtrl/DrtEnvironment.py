# -*- coding: utf-8 -*-

import grpc
import numpy as np
from mushroom_rl.core import Environment, MDPInfo
from mushroom_rl.utils.spaces import Box

from .server.rebalancer_pb2 import Empty, SimulationTime, RebalancingInstructions
from .server.rebalancer_pb2_grpc import RebalancingStrategyStub


class DrtEnvironment(Environment):
    """ Environment for DRT Rebalancing"""

    def __init__(self, server):
        channel = grpc.insecure_channel(server)
        self.server = RebalancingStrategyStub(channel)

        print("Connecting to %s..." % server)
        self.spec = self.server.GetSpecification(Empty(), wait_for_ready=True)

        # only time is observed
        self.observation_space = Box(low=0, high=1, shape=(2,))
        self.action_space = Box(low=0, high=self.spec.fleetSize, shape=(len(self.spec.zones),))

        mdp_info = MDPInfo(self.observation_space, self.action_space, gamma=0.99, horizon=100)
        super().__init__(mdp_info)

    def step(self, action):

        cmd = RebalancingInstructions()
        for a in action:
            cmd.zoneTargets.vehicles.append(max(0, int(a)))

        # submit current time
        cmd.currentTime = int(self._state[0])

        response = self.server.PerformRebalancing(cmd)

        self._state[0] = response.time
        self._state[1] = response.time

        state = self.server.GetCurrentState(response)

        reward = -state.waitingTime.sum

        return self._state, reward, state.simulationEnded, {}

    def reset(self, state=None):
        # Wait for initial state
        current_state = self.server.GetCurrentState(SimulationTime())

        if state is None:
            self._state = np.zeros(2)
        else:
            self._state = state
            self._state[0] = 0

        return self._state


DrtEnvironment.register()
