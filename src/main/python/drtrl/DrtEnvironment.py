# -*- coding: utf-8 -*-

from enum import Enum, auto

import grpc
import numpy as np
from mushroom_rl.core import Environment, MDPInfo
from mushroom_rl.utils.spaces import Box

from .server.rebalancer_pb2 import Empty, SimulationTime, RebalancingInstructions
from .server.rebalancer_pb2_grpc import RebalancingStrategyStub


class DrtObjective(Enum):
    """ The action space of the environment """

    MIN_COST_FLOW = auto()
    ZONE_TARGETS = auto()


class DrtEnvironment(Environment):
    """ Environment for DRT Rebalancing"""

    def __init__(self, server, objective=DrtObjective.MIN_COST_FLOW):
        channel = grpc.insecure_channel(server)
        self.server = RebalancingStrategyStub(channel)
        self.time = 0

        print("Connecting to %s..." % server)
        self.spec = self.server.GetSpecification(Empty(), wait_for_ready=True)

        # observe time and demand
        self.objective = objective

        if self.objective == DrtObjective.MIN_COST_FLOW:

            # Observe time and total expected demand
            self.observation_space = Box(low=0, high=1, shape=(2,))

            # Give alpha beta parameter
            self.action_space = Box(low=0, high=3, shape=(2,))

        elif self.objective == DrtObjective.ZONE_TARGETS:
            # Observe time and expected demand
            self.observation_space = Box(low=0, high=1, shape=(1 + len(self.spec.zones),))

            # One target value per zone
            self.action_space = Box(low=0, high=self.spec.fleetSize, shape=(len(self.spec.zones),))
        else:
            raise Exception("Invalid objective: %s" % self.objective)

        mdp_info = MDPInfo(self.observation_space, self.action_space, gamma=0.99, horizon=self.spec.steps)
        super().__init__(mdp_info)

    def step(self, action):

        cmd = RebalancingInstructions()

        if self.objective == DrtObjective.MIN_COST_FLOW:
            cmd.minCostFlow.alpha = action[0]
            cmd.minCostFlow.beta = action[1]

        elif self.objective == DrtObjective.ZONE_TARGETS:
            for a in action:
                cmd.zoneTargets.vehicles.append(max(0, int(a)))

        # submit current time
        cmd.currentTime = int(self.time)

        response = self.server.PerformRebalancing(cmd)

        state = self.update_state(response)

        # Scale near 1
        reward = -state.waitingTime.sum / 1000

        return self._state, reward, state.simulationEnded, {}

    def reset(self, state=None):
        # Wait for initial state

        if state is None:
            self._state = np.zeros(shape=self.action_space.shape)
        else:
            self._state = state
            self._state.fill(0)

        t = SimulationTime()
        t.time = int(self.spec.startTime)

        self.update_state(t)

        return self._state

    def update_state(self, req):
        """ Internally updates the current state based on server response """

        self.time = req.time
        self._state[0] = req.time / self.spec.endTime

        state = self.server.GetCurrentState(req)

        # Normalize demand with the max expected
        if self.objective == DrtObjective.MIN_COST_FLOW:
            self._state[1] = sum(state.expectedDemand) / state.maxExpectedDemand
        elif self.objective == DrtObjective.ZONE_TARGETS:
            for i in range(len(state.expectedDemand)):
                self._state[i + 1] = state.expectedDemand[i] / state.maxExpectedDemand

        return state


DrtEnvironment.register()
