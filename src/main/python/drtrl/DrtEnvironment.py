# -*- coding: utf-8 -*-

from enum import Enum, auto

import grpc
import numpy as np
from mushroom_rl.core import Environment, MDPInfo
from mushroom_rl.utils.spaces import Box

from .server.rebalancer_pb2 import Empty, SimulationTime, RebalancingInstructions
from .server.rebalancer_pb2_grpc import RebalancingStrategyStub
from .DummyServer import DummyServer

class DrtObjective(Enum):
    """ The action space of the environment """

    MIN_COST_FLOW = auto()
    ZONE_TARGETS = auto()


class DrtEnvironment(Environment):
    """ Environment for DRT Rebalancing"""

    def __init__(self, server, objective=DrtObjective.MIN_COST_FLOW):

        if server.startswith("dummy"):
            self.server = DummyServer()
        else:
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
            self.action_space = Box(low=-1, high=1, shape=(2,))

        elif self.objective == DrtObjective.ZONE_TARGETS:
            # Observe time and expected demand
            self.observation_space = Box(low=0, high=1, shape=(1 + len(self.spec.zones),))

            # One target value per zone
            self.action_space = Box(low=-1, high=1, shape=(len(self.spec.zones),))
        else:
            raise Exception("Invalid objective: %s" % self.objective)

        # low discount factor since actions don't reach far into the future
        mdp_info = MDPInfo(self.observation_space, self.action_space, gamma=0.8, horizon=self.spec.steps)
        super().__init__(mdp_info)

    def __repr__(self):
        return "<DrtEnvironment: interval=%d, fleetSize=%d, startTime=%.0f, zones=%d" % (
            self.spec.interval, self.spec.fleetSize, self.spec.startTime, len(self.spec.zones))

    def step(self, action):

        cmd = RebalancingInstructions()

        reward = 0

        if self.objective == DrtObjective.MIN_COST_FLOW:

            bound = 1.5

            # Unsquash and clip action space
            action = (action + 1) * bound / 2
            action = np.clip(action, 0, bound)

            cmd.minCostFlow.alpha = action[0]
            cmd.minCostFlow.beta = action[1]

        elif self.objective == DrtObjective.ZONE_TARGETS:

            # max fleet of 50% per zone can be rebalanced
            bound = self.spec.fleetSize / 2.0

            action = (action + 1) * bound / 2
            action = np.clip(action, 0, bound)

            total = 0
            for a in action:
                v = int(a)
                cmd.zoneTargets.vehicles.append(v)
                total += v

            # Too many vehicles results in negative reward
            if total > self.spec.fleetSize:
                reward -= (total - self.spec.fleetSize)

        # submit current time
        cmd.currentTime = int(self.time)

        response = self.server.PerformRebalancing(cmd)

        state = self.update_state(response)

        # Any wait above 180min gives negative reward, divided to reduce the scale
        reward += (180 * state.waitingTime.n + -state.waitingTime.sum) / (1000 * self.spec.fleetSize)

        reward -= state.drivenEmptyDistance.sum / (1000 * self.spec.fleetSize)

        return self._state, reward, state.simulationEnded, {}

    def reset(self, state=None):
        # Wait for initial state

        if state is None:
            self._state = np.zeros(shape=self.observation_space.shape)
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
