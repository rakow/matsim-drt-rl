# -*- coding: utf-8 -*-

import atexit
import os
import subprocess
import sys
from time import sleep
from typing import Optional, Union, Tuple, Set, List

import grpc
import gymnasium as gym
import numpy as np
from gymnasium.spaces import Box
from ray.rllib.env.base_env import BaseEnv, _DUMMY_AGENT_ID
from ray.rllib.env.env_context import EnvContext
from ray.rllib.utils.annotations import override, PublicAPI
from ray.rllib.utils.typing import AgentID, EnvID, EnvType, MultiEnvDict

from .base import DrtObjective
from .server.rebalancer_pb2 import Empty, RebalancingSpecification, RebalancingInstructions, SimulationTime
from .server.rebalancer_pb2_grpc import RebalancingStrategyStub

_DUMMY_ENV_ID = "env0"


def connect_server(server_addr):
    """ Connect to server and wait for first response. """

    channel = grpc.insecure_channel(server_addr)
    server = RebalancingStrategyStub(channel)

    print("Connecting to %s..." % server_addr)
    server.GetSpecification(Empty(), wait_for_ready=True)
    return server, channel


@PublicAPI
class ManagedDrtEnvironment(BaseEnv):
    """ Environment for DRT Rebalancing that also manages the MATSim runs """

    def __init__(self, config: EnvContext):

        self.jar = config["jar"]
        self.configPath = config["configPath"]
        self.objective = config["objective"]

        self._state = None
        self.last_state = None
        self.time = -1

        self.port = 49152
        self.process = None
        self.server = None
        self.channel = None
        self.drt_spec: RebalancingSpecification = None

        # Ensure process is terminated
        def terminate():
            if self.process is not None:
                self.process.terminate()

        atexit.register(terminate)

        self.start_process()

        self._max_episode_steps = (self.drt_spec.endTime - self.drt_spec.startTime) // self.drt_spec.interval

    def __repr__(self):
        return "<ManagedDrtEnvironment: interval=%d, fleetSize=%d, startTime=%.0f, zones=%d" % (
            self.drt_spec.interval, self.drt_spec.fleetSize, self.drt_spec.startTime, len(self.drt_spec.zones))

    def start_process(self):
        cmd = "java -jar %s run --config %s --port %d --output %s --iterations 10000" % (self.jar, self.configPath,
                                                                                        self.port,
                                                                                        "output/%s" % self.port)
        cmd = cmd.strip()

        print("Starting MATSim: ", cmd)

        if os.name != 'nt':
            cmd = cmd.split(" ")

        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        sleep(3)

        if self.process.poll() is not None:
            # Process already terminated
            if self.process.returncode != 0:
                raise Exception("Process returned with error code: %s" % self.process.returncode)

        self.server, self.channel = connect_server("localhost:%d" % self.port)
        self.time = -1

        self.drt_spec = self.server.GetSpecification(Empty(), wait_for_ready=True)

    @override(BaseEnv)
    @PublicAPI
    def send_actions(self, action_dict: MultiEnvDict) -> None:

        if action_dict:
            action = action_dict[_DUMMY_ENV_ID][_DUMMY_AGENT_ID]

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

            # updated time step
            self.time = response.time
            self.last_state = None

    @override(BaseEnv)
    def poll(
            self,
    ) -> Tuple[
        MultiEnvDict,
        MultiEnvDict,
        MultiEnvDict,
        MultiEnvDict,
        MultiEnvDict,
        MultiEnvDict,
    ]:
        # print("Poll called")

        req = SimulationTime()
        req.time = int(self.time)

        state = self.update_state(req)

        # Any wait above 180min gives negative reward, divided to reduce the scale
        reward = (180 * state.waitingTime.n + -state.waitingTime.sum) / 1000

        return ({_DUMMY_ENV_ID: {_DUMMY_AGENT_ID: self._state}},
                {_DUMMY_ENV_ID: {_DUMMY_AGENT_ID: reward}},
                {_DUMMY_ENV_ID: {"__all__": state.simulationEnded}},
                {_DUMMY_ENV_ID: {"__all__": False}},
                {_DUMMY_ENV_ID: {}},
                {_DUMMY_ENV_ID: {}})

    @override(BaseEnv)
    @PublicAPI
    def try_reset(
            self,
            env_id: Optional[EnvID] = None,
            *,
            seed: Optional[int] = None,
            options: Optional[dict] = None,
    ) -> Tuple[Optional[MultiEnvDict], Optional[MultiEnvDict]]:

        # Wait for initial state
        # print("Try reset called", env_id)

        self._state = np.zeros(shape=self.observation_space.shape, dtype=np.float32)

        t = SimulationTime()
        t.time = int(self.drt_spec.startTime)

        self.update_state(t)

        return {_DUMMY_ENV_ID: {_DUMMY_AGENT_ID: self._state}}, {_DUMMY_ENV_ID: {_DUMMY_AGENT_ID: {}}}

    def update_state(self, req):
        """ Internally updates the current state based on server response """

        self.time = req.time
        self._state[0] = req.time / self.drt_spec.endTime

        # Re-use state if requested multiple times
        if self.last_state is not None and int(self.last_state.simulationTime) == req.time:
            state = self.last_state
        else:
            state = self.server.GetCurrentState(req)

        # Normalize demand with the max expected
        if self.objective == DrtObjective.MIN_COST_FLOW:
            self._state[1] = sum(state.expectedDemand) / state.maxExpectedDemand
        elif self.objective == DrtObjective.ZONE_TARGETS:
            for i in range(len(state.expectedDemand)):
                self._state[i + 1] = state.expectedDemand[i] / state.maxExpectedDemand

        self.last_state = state
        return state

    @override(BaseEnv)
    @PublicAPI
    def try_restart(self, env_id: Optional[EnvID] = None) -> None:
        print("Try restart called")

    @override(BaseEnv)
    @PublicAPI
    def stop(self) -> None:
        print("Stop called")
        self.process.terminate()

    @property
    @override(BaseEnv)
    @PublicAPI
    def observation_space(self) -> gym.Space:
        if self.objective == DrtObjective.MIN_COST_FLOW:
            # Observe time and total expected demand
            return Box(low=0, high=1, shape=(2,), dtype=np.float32)
        elif self.objective == DrtObjective.ZONE_TARGETS:
            # Observe time and expected demand
            return Box(low=0, high=1, shape=(1 + len(self.drt_spec.zones),), dtype=np.float32)
        else:
            raise Exception("Invalid objective: %s" % self.objective)

    @property
    @override(BaseEnv)
    @PublicAPI
    def action_space(self) -> gym.Space:
        if self.objective == DrtObjective.MIN_COST_FLOW:
            # Give alpha beta parameter
            return Box(low=0, high=3, shape=(2,), dtype=np.float32)

        elif self.objective == DrtObjective.ZONE_TARGETS:
            # One target value per zone
            return Box(low=0, high=self.drt_spec.fleetSize, shape=(len(self.drt_spec.zones),), dtype=np.float32)
        else:
            raise Exception("Invalid objective: %s" % self.objective)

    @override(BaseEnv)
    @PublicAPI
    def get_sub_environments(self, as_dict: bool = False) -> Union[List[EnvType], dict]:
        if as_dict:
            # TODO: might create separate sub envs
            return {_DUMMY_ENV_ID: self}
        else:
            return [_DUMMY_ENV_ID]

    @override(BaseEnv)
    @PublicAPI
    def get_agent_ids(self) -> Set[AgentID]:
        return {_DUMMY_AGENT_ID}
