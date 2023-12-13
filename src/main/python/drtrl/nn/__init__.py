# -*- coding: utf-8 -*-

__all__ = ["get_actor_net", "get_critic_net", "DenseNetwork", "DenseCriticNetwork", "RegressionNetwork",
           "RegressionBiasNetwork"]

from .dense import DenseNetwork, DenseGumbelNetwork, DenseCriticNetwork
from .simple import RegressionNetwork, RegressionBiasNetwork


def get_actor_net(args):
    """ Get actor network based on command line arguments"""

    if args.actor_network == "dense":
        return DenseNetwork
    elif args.actor_network == "regression":
        return RegressionNetwork
    elif args.actor_network == "regression-bias":
        return RegressionBiasNetwork
    elif args.actor_network == "gumbel":
        return DenseGumbelNetwork

    raise ValueError(f"Unknown actor network {args.actor_network}")


def get_critic_net(args, action_input=True):
    """ Get critic network based on command line arguments"""

    # Some networks don't require the action as separate input
    if action_input:
        if args.critic_network == "dense":
            return DenseCriticNetwork
    else:
        if args.critic_network == "dense":
            return DenseNetwork
        elif args.critic_network == "regression":
            return RegressionNetwork
        elif args.critic_network == "regression-bias":
            return RegressionBiasNetwork
        elif args.critic_network == "gumbel":
            return DenseGumbelNetwork

    raise ValueError(f"Unknown critic network {args.critic_network}")
