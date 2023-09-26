# -*- coding: utf-8 -*-

import numpy as np

from .server.rebalancer_pb2 import RebalancingSpecification, RebalancingState, SimulationTime, Zone
from .server.rebalancer_pb2_grpc import RebalancingStrategyServicer


class DummyServer(RebalancingStrategyServicer):
    """ Dummy server to simulate an artificial drt environment """

    def __init__(self, zones=20, vehicles=10, shuffle=10, iterations=10_000):
        super().__init__()
        self.spec = RebalancingSpecification()
        self.spec.iterations = iterations
        self.spec.interval = 1800
        self.spec.startTime = 0
        self.spec.endTime = 24 * 3600
        # Create empty zones
        for i in range(zones):
            self.spec.zones.append(Zone())

        self.spec.fleetSize = vehicles
        self.spec.steps = int(self.spec.endTime // self.spec.interval)

        self.time = 0
        # Targets received from rebalancing
        self.zone_targets = np.zeros(zones)
        self.n = 0
        self.shuffle = shuffle

        self.demand = self.create_demand()

    def create_demand(self):
        demand = np.random.normal(0, 2 * (self.spec.fleetSize / len(self.spec.zones)),
                                  (int(self.spec.endTime // self.spec.interval), len(self.spec.zones)))
        return np.maximum(0, demand.round().astype(int))

    def GetSpecification(self, request, **kwargs):
        return self.spec

    def GetCurrentState(self, request, **kwargs):
        state = RebalancingState()

        self.time = int(request.time // self.spec.interval)

        state.expectedDemand.extend(self.demand[self.time])
        # avoid division by zero
        state.maxExpectedDemand = max(1, np.max(self.demand[self.time]))

        if request.time == self.spec.endTime - self.spec.interval:

            state.simulationEnded = True
            # reset demand
            if self.shuffle > 0 and self.n % self.shuffle == 0:
                self.demand = self.create_demand()

            self.n += 1

        # print("Demand", self.demand[self.time-1], "Target", self.zone_targets)
        # print(state)

        available = self.spec.fleetSize
        # Simulate waiting time based on rebalancing
        for i in range(len(self.zone_targets)):
            surplus = int(self.demand[self.time - 1, i] - min(available, self.zone_targets[i]))

            # too fee vehicles results in waiting time
            if surplus > 0:
                state.waitingTime.n += self.demand[self.time - 1, i]
                state.waitingTime.sum += 1000 * surplus

            # too much vehicles results in empty milage
            elif surplus < 0:
                state.drivenEmptyDistance.n += -surplus
                state.drivenEmptyDistance.sum += 1000 * -surplus

            # similar to waiting time of zero
            else:
                state.waitingTime.n += self.demand[self.time - 1, i]

            # subtract used vehicles
            available -= self.zone_targets[i]
            available = max(0, available)

        return state

    def PerformRebalancing(self, request, **kwargs):
        t = SimulationTime()
        t.time = int(request.currentTime + self.spec.interval)

        self.zone_targets = np.array(request.zoneTargets.vehicles)

        return t
