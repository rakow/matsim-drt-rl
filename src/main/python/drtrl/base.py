# -*- coding: utf-8 -*-

from abc import abstractmethod

from attrs import define
from mushroom_rl.core.agent import Agent

from .DrtEnvironment import DrtEnvironment, DrtObjective

@define
class Base:
    """ Base class for different RL algorithms """

    env: DrtEnvironment

    @staticmethod
    def is_pretrained():
        """ Whether there is a pretraining loop required """
        return False

    @abstractmethod
    def create_agent(self, args) -> Agent:
        """ Create the agent that will then be used in the training loop """
        pass
