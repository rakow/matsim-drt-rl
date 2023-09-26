# -*- coding: utf-8 -*-

import numpy as np

from .server.rebalancer_pb2 import RebalancingSpecification, RebalancingState, SimulationTime, Zone
from .server.rebalancer_pb2_grpc import RebalancingStrategyServicer


class DummyServer(RebalancingStrategyServicer):
    """ Dummy server to simulate an artificial drt environment """

    def __init__(self, zones=20, vehicles=10, iterations=10_000):
        super().__init__()
        self.spec = RebalancingSpecification()
        self.spec.interval = 1800
        self.spec.startTime = 0
        self.spec.endTime = 24 * 3600
        # Create empty zones
        for i in range(zones):
            self.spec.zones.append(Zone())

        self.spec.fleetSize = vehicles
        self.spec.steps = iterations

        self.time = 0
        # Targets received from rebalancing
        self.zone_targets = np.zeros(zones)

        self.demand = np.random.normal(0, 2 * (vehicles / zones), (int(self.spec.endTime // self.spec.interval), zones))
        self.demand = np.maximum(0, self.demand.round().astype(int))

    def GetSpecification(self, request, **kwargs):
        return self.spec

    def GetCurrentState(self, request, **kwargs):
        state = RebalancingState()

        self.time = int(request.time // self.spec.interval)

        state.expectedDemand.extend(self.demand[self.time])
        state.maxExpectedDemand = np.max(self.demand[self.time])

        if request.time == self.spec.endTime - self.spec.interval:
            state.simulationEnded = True

        available = self.spec.fleetSize
        # Simulate waiting time based on rebalancing
        for i in range(len(self.zone_targets)):
            surplus = int(self.demand[self.time - 1, i] - min(available, self.zone_targets[i]))

            # too fee vehicles results in waiting time
            if surplus > 0:
                state.waitingTime.n += surplus
                state.waitingTime.sum += 1000 * surplus

            # too much vehicles results in empty milage
            elif surplus < 0:
                state.drivenEmptyDistance.n += -surplus
                state.drivenEmptyDistance.sum += 1000 * -surplus

            # subtract used vehicles
            available -= self.zone_targets[i]
            available = max(0, available)

        # print("Demand", self.demand[self.time-1], "Target", self.zone_targets)
        # print(state)

        return state

    def PerformRebalancing(self, request, **kwargs):
        t = SimulationTime()
        t.time = int(request.currentTime + self.spec.interval)

        self.zone_targets = np.array(request.zoneTargets.vehicles)

        return t
