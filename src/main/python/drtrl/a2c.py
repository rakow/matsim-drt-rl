# -*- coding: utf-8 -*-


import torch.nn.functional as F
import torch.optim as optim
from attrs import define
from mushroom_rl.algorithms.actor_critic import A2C as AA2C
from mushroom_rl.core import Agent
from mushroom_rl.policy import GaussianTorchPolicy

from .base import Base
from .nn import get_critic_net, get_actor_net


@define
class A2C(Base):

    def create_agent(self, args) -> Agent:
        alg_params = dict(actor_optimizer={'class': optim.RMSprop,
                                           'params': {'lr': 7e-4,
                                                      'eps': 3e-3}},
                          max_grad_norm=0.5,
                          ent_coeff=0.01)

        critic_params = dict(network=get_critic_net(args),
                             optimizer={'class': optim.RMSprop,
                                        'params': {'lr': 7e-4,
                                                   'eps': 1e-5}},
                             loss=F.mse_loss,
                             n_features=64,
                             batch_size=64,
                             input_shape=self.env.info.observation_space.shape,
                             output_shape=(1,))

        alg_params['critic_params'] = critic_params

        policy_params = dict(
            std_0=args.std_init,
            n_features=64,
            upper_bound=self.env.spec.fleetSize + 1,
            use_cuda=False
        )

        policy = GaussianTorchPolicy(get_actor_net(args),
                                     self.env.info.observation_space.shape,
                                     self.env.info.action_space.shape,
                                     **policy_params)

        return AA2C(self.env.info, policy, **alg_params)
