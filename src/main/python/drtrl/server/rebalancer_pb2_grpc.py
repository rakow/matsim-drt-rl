# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc



class RebalancingStrategyStub(object):
    """TODO naming because the server only accepts the reblancing


    Server running within MATSim and accepting rebalancing input
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """


class RebalancingStrategyServicer(object):
    """TODO naming because the server only accepts the reblancing


    Server running within MATSim and accepting rebalancing input
    """


def add_RebalancingStrategyServicer_to_server(servicer, server):
    rpc_method_handlers = {
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'RebalancingStrategy', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RebalancingStrategy(object):
    """TODO naming because the server only accepts the reblancing


    Server running within MATSim and accepting rebalancing input
    """
