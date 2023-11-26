# -*- coding: utf-8 -*-

import torch
import torch.nn as nn


class RegressionNetwork(nn.Module):
    """ Simpler network only doing regression """

    def __init__(self, input_shape, output_shape, **kwargs):
        super(RegressionNetwork, self).__init__()

        n_input = input_shape[-1]
        self.weight = nn.Parameter(torch.ones(n_input - 1), requires_grad=True)

    def forward(self, state, **kwargs):
        features1 = torch.squeeze(state, 1).float()

        # Put copy of state into the network (without time for now)
        a = self.weight.mul(features1[:, 1:])

        return a
