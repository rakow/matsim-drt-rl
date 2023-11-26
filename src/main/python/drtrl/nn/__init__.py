# -*- coding: utf-8 -*-

__all__ = ["get_actor_net", "get_critic_net", "DenseNetwork", "DenseCriticNetwork", "RegressionNetwork"]

from .dense import DenseNetwork, DenseGumbelNetwork, DenseCriticNetwork
from .simple import RegressionNetwork


def get_actor_net(args):
    """ Get actor network based on command line arguments"""

    if args.actor_network == "dense":
        return DenseNetwork
    elif args.actor_network == "regression":
        return RegressionNetwork
    elif args.actor_network == "gumbel":
        return DenseGumbelNetwork

    raise ValueError(f"Unknown actor network {args.actor_network}")


def get_critic_net(args):
    """ Get critic network based on command line arguments"""

    if args.critic_network == "dense":
        return DenseCriticNetwork

    raise ValueError(f"Unknown critic network {args.critic_network}")
