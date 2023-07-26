# MATSim DRT RL

Repository to combine DRT rebalancing and reinforcement learning.

All important source code is contained in `src/main`. The java code implements a [RemoteRebalancingStrategy](src%2Fmain%2Fjava%2Forg%2Fmatsim%2Fcontrib%2Fdrt%2Foptimizer%2Frebalancing%2FremoteBalancing%2FRemoteRebalancingStrategy.java) that accepts rebalancing instructions from a client.
The reinforcment learning part is implemented in python and contained in the `src/main/python`.


## Installation

Install python requirements in:

`
pip install -r src/main/python/requirements.txt
`

## Running scenarios