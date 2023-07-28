# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: drtrl/server/rebalancer.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='drtrl/server/rebalancer.proto',
  package='drtrl.server',
  syntax='proto3',
  serialized_options=b'\nCorg.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.server',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1d\x64rtrl/server/rebalancer.proto\x12\x0c\x64rtrl.server\"\x07\n\x05\x45mpty\"8\n\x04Zone\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\tcentroidX\x18\x02 \x01(\x01\x12\x11\n\tcentroidY\x18\x03 \x01(\x01\"\x87\x01\n\x18RebalancingSpecification\x12\x10\n\x08interval\x18\x01 \x01(\x05\x12\x0f\n\x07\x65ndTime\x18\x02 \x01(\x01\x12\x11\n\tfleetSize\x18\x03 \x01(\x05\x12!\n\x05zones\x18\x04 \x03(\x0b\x32\x12.drtrl.server.Zone\x12\x12\n\niterations\x18\x05 \x01(\x05\"\x1e\n\x0eSimulationTime\x12\x0c\n\x04time\x18\x01 \x01(\x05\"d\n\nDrtRequest\x12\x16\n\x0esubmissionTime\x18\x01 \x01(\x01\x12\x15\n\rdepartureTime\x18\x02 \x01(\x01\x12\x12\n\npickupTime\x18\x03 \x01(\x01\x12\x13\n\x0b\x64ropOffTime\x18\x04 \x01(\x01\"K\n\x05Stats\x12\x0b\n\x03sum\x18\x01 \x01(\x01\x12\x0c\n\x04mean\x18\x02 \x01(\x01\x12\x0e\n\x06median\x18\x03 \x01(\x01\x12\x0b\n\x03q95\x18\x04 \x01(\x01\x12\n\n\x02q5\x18\x05 \x01(\x01\"\x8b\x02\n\x17RebalancingInstructions\x12\x13\n\x0b\x63urrentTime\x18\x01 \x01(\x05\x12\x46\n\x0bzoneTargets\x18\x02 \x01(\x0b\x32\x31.drtrl.server.RebalancingInstructions.ZoneTargets\x12\x46\n\x0bminCostFlow\x18\x03 \x01(\x0b\x32\x31.drtrl.server.RebalancingInstructions.MinCostFlow\x1a\x1f\n\x0bZoneTargets\x12\x10\n\x08vehicles\x18\x01 \x03(\x05\x1a*\n\x0bMinCostFlow\x12\r\n\x05\x61lpha\x18\x01 \x01(\x01\x12\x0c\n\x04\x62\x65ta\x18\x02 \x01(\x01\"\xc0\x03\n\x10RebalancingState\x12\x16\n\x0esimulationTime\x18\x01 \x01(\x01\x12\x64\n\x1brebalancableVehiclesPerZone\x18\x02 \x03(\x0b\x32?.drtrl.server.RebalancingState.RebalancableVehiclesPerZoneEntry\x12\x32\n\x10performedRequest\x18\x03 \x03(\x0b\x32\x18.drtrl.server.DrtRequest\x12\x32\n\x10rejectedRequests\x18\x04 \x03(\x0b\x32\x18.drtrl.server.DrtRequest\x12\x16\n\x0e\x65xpectedDemand\x18\x05 \x03(\x01\x12(\n\x0bwaitingTime\x18\x06 \x01(\x0b\x32\x13.drtrl.server.Stats\x12\'\n\ntravelTime\x18\x07 \x01(\x0b\x32\x13.drtrl.server.Stats\x12\x17\n\x0fsimulationEnded\x18\x08 \x01(\x08\x1a\x42\n RebalancableVehiclesPerZoneEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01\x32\x98\x02\n\x13RebalancingStrategy\x12Q\n\x10GetSpecification\x12\x13.drtrl.server.Empty\x1a&.drtrl.server.RebalancingSpecification\"\x00\x12Q\n\x0fGetCurrentState\x12\x1c.drtrl.server.SimulationTime\x1a\x1e.drtrl.server.RebalancingState\"\x00\x12[\n\x12PerformRebalancing\x12%.drtrl.server.RebalancingInstructions\x1a\x1c.drtrl.server.SimulationTime\"\x00\x42\x45\nCorg.matsim.contrib.drt.optimizer.rebalancing.remoteBalancing.serverb\x06proto3'
)




_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='drtrl.server.Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=47,
  serialized_end=54,
)


_ZONE = _descriptor.Descriptor(
  name='Zone',
  full_name='drtrl.server.Zone',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='drtrl.server.Zone.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='centroidX', full_name='drtrl.server.Zone.centroidX', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='centroidY', full_name='drtrl.server.Zone.centroidY', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=56,
  serialized_end=112,
)


_REBALANCINGSPECIFICATION = _descriptor.Descriptor(
  name='RebalancingSpecification',
  full_name='drtrl.server.RebalancingSpecification',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='interval', full_name='drtrl.server.RebalancingSpecification.interval', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='endTime', full_name='drtrl.server.RebalancingSpecification.endTime', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='fleetSize', full_name='drtrl.server.RebalancingSpecification.fleetSize', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='zones', full_name='drtrl.server.RebalancingSpecification.zones', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='iterations', full_name='drtrl.server.RebalancingSpecification.iterations', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=115,
  serialized_end=250,
)


_SIMULATIONTIME = _descriptor.Descriptor(
  name='SimulationTime',
  full_name='drtrl.server.SimulationTime',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='time', full_name='drtrl.server.SimulationTime.time', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=252,
  serialized_end=282,
)


_DRTREQUEST = _descriptor.Descriptor(
  name='DrtRequest',
  full_name='drtrl.server.DrtRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='submissionTime', full_name='drtrl.server.DrtRequest.submissionTime', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='departureTime', full_name='drtrl.server.DrtRequest.departureTime', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='pickupTime', full_name='drtrl.server.DrtRequest.pickupTime', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='dropOffTime', full_name='drtrl.server.DrtRequest.dropOffTime', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=284,
  serialized_end=384,
)


_STATS = _descriptor.Descriptor(
  name='Stats',
  full_name='drtrl.server.Stats',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='sum', full_name='drtrl.server.Stats.sum', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='mean', full_name='drtrl.server.Stats.mean', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='median', full_name='drtrl.server.Stats.median', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='q95', full_name='drtrl.server.Stats.q95', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='q5', full_name='drtrl.server.Stats.q5', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=386,
  serialized_end=461,
)


_REBALANCINGINSTRUCTIONS_ZONETARGETS = _descriptor.Descriptor(
  name='ZoneTargets',
  full_name='drtrl.server.RebalancingInstructions.ZoneTargets',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='vehicles', full_name='drtrl.server.RebalancingInstructions.ZoneTargets.vehicles', index=0,
      number=1, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=656,
  serialized_end=687,
)

_REBALANCINGINSTRUCTIONS_MINCOSTFLOW = _descriptor.Descriptor(
  name='MinCostFlow',
  full_name='drtrl.server.RebalancingInstructions.MinCostFlow',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='alpha', full_name='drtrl.server.RebalancingInstructions.MinCostFlow.alpha', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='beta', full_name='drtrl.server.RebalancingInstructions.MinCostFlow.beta', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=689,
  serialized_end=731,
)

_REBALANCINGINSTRUCTIONS = _descriptor.Descriptor(
  name='RebalancingInstructions',
  full_name='drtrl.server.RebalancingInstructions',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='currentTime', full_name='drtrl.server.RebalancingInstructions.currentTime', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='zoneTargets', full_name='drtrl.server.RebalancingInstructions.zoneTargets', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='minCostFlow', full_name='drtrl.server.RebalancingInstructions.minCostFlow', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_REBALANCINGINSTRUCTIONS_ZONETARGETS, _REBALANCINGINSTRUCTIONS_MINCOSTFLOW, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=464,
  serialized_end=731,
)


_REBALANCINGSTATE_REBALANCABLEVEHICLESPERZONEENTRY = _descriptor.Descriptor(
  name='RebalancableVehiclesPerZoneEntry',
  full_name='drtrl.server.RebalancingState.RebalancableVehiclesPerZoneEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='drtrl.server.RebalancingState.RebalancableVehiclesPerZoneEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='drtrl.server.RebalancingState.RebalancableVehiclesPerZoneEntry.value', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1116,
  serialized_end=1182,
)

_REBALANCINGSTATE = _descriptor.Descriptor(
  name='RebalancingState',
  full_name='drtrl.server.RebalancingState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='simulationTime', full_name='drtrl.server.RebalancingState.simulationTime', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rebalancableVehiclesPerZone', full_name='drtrl.server.RebalancingState.rebalancableVehiclesPerZone', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='performedRequest', full_name='drtrl.server.RebalancingState.performedRequest', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rejectedRequests', full_name='drtrl.server.RebalancingState.rejectedRequests', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='expectedDemand', full_name='drtrl.server.RebalancingState.expectedDemand', index=4,
      number=5, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='waitingTime', full_name='drtrl.server.RebalancingState.waitingTime', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='travelTime', full_name='drtrl.server.RebalancingState.travelTime', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='simulationEnded', full_name='drtrl.server.RebalancingState.simulationEnded', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_REBALANCINGSTATE_REBALANCABLEVEHICLESPERZONEENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=734,
  serialized_end=1182,
)

_REBALANCINGSPECIFICATION.fields_by_name['zones'].message_type = _ZONE
_REBALANCINGINSTRUCTIONS_ZONETARGETS.containing_type = _REBALANCINGINSTRUCTIONS
_REBALANCINGINSTRUCTIONS_MINCOSTFLOW.containing_type = _REBALANCINGINSTRUCTIONS
_REBALANCINGINSTRUCTIONS.fields_by_name['zoneTargets'].message_type = _REBALANCINGINSTRUCTIONS_ZONETARGETS
_REBALANCINGINSTRUCTIONS.fields_by_name['minCostFlow'].message_type = _REBALANCINGINSTRUCTIONS_MINCOSTFLOW
_REBALANCINGSTATE_REBALANCABLEVEHICLESPERZONEENTRY.containing_type = _REBALANCINGSTATE
_REBALANCINGSTATE.fields_by_name['rebalancableVehiclesPerZone'].message_type = _REBALANCINGSTATE_REBALANCABLEVEHICLESPERZONEENTRY
_REBALANCINGSTATE.fields_by_name['performedRequest'].message_type = _DRTREQUEST
_REBALANCINGSTATE.fields_by_name['rejectedRequests'].message_type = _DRTREQUEST
_REBALANCINGSTATE.fields_by_name['waitingTime'].message_type = _STATS
_REBALANCINGSTATE.fields_by_name['travelTime'].message_type = _STATS
DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
DESCRIPTOR.message_types_by_name['Zone'] = _ZONE
DESCRIPTOR.message_types_by_name['RebalancingSpecification'] = _REBALANCINGSPECIFICATION
DESCRIPTOR.message_types_by_name['SimulationTime'] = _SIMULATIONTIME
DESCRIPTOR.message_types_by_name['DrtRequest'] = _DRTREQUEST
DESCRIPTOR.message_types_by_name['Stats'] = _STATS
DESCRIPTOR.message_types_by_name['RebalancingInstructions'] = _REBALANCINGINSTRUCTIONS
DESCRIPTOR.message_types_by_name['RebalancingState'] = _REBALANCINGSTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'drtrl.server.rebalancer_pb2'
  # @@protoc_insertion_point(class_scope:drtrl.server.Empty)
  })
_sym_db.RegisterMessage(Empty)

Zone = _reflection.GeneratedProtocolMessageType('Zone', (_message.Message,), {
  'DESCRIPTOR' : _ZONE,
  '__module__' : 'drtrl.server.rebalancer_pb2'
  # @@protoc_insertion_point(class_scope:drtrl.server.Zone)
  })
_sym_db.RegisterMessage(Zone)

RebalancingSpecification = _reflection.GeneratedProtocolMessageType('RebalancingSpecification', (_message.Message,), {
  'DESCRIPTOR' : _REBALANCINGSPECIFICATION,
  '__module__' : 'drtrl.server.rebalancer_pb2'
  # @@protoc_insertion_point(class_scope:drtrl.server.RebalancingSpecification)
  })
_sym_db.RegisterMessage(RebalancingSpecification)

SimulationTime = _reflection.GeneratedProtocolMessageType('SimulationTime', (_message.Message,), {
  'DESCRIPTOR' : _SIMULATIONTIME,
  '__module__' : 'drtrl.server.rebalancer_pb2'
  # @@protoc_insertion_point(class_scope:drtrl.server.SimulationTime)
  })
_sym_db.RegisterMessage(SimulationTime)

DrtRequest = _reflection.GeneratedProtocolMessageType('DrtRequest', (_message.Message,), {
  'DESCRIPTOR' : _DRTREQUEST,
  '__module__' : 'drtrl.server.rebalancer_pb2'
  # @@protoc_insertion_point(class_scope:drtrl.server.DrtRequest)
  })
_sym_db.RegisterMessage(DrtRequest)

Stats = _reflection.GeneratedProtocolMessageType('Stats', (_message.Message,), {
  'DESCRIPTOR' : _STATS,
  '__module__' : 'drtrl.server.rebalancer_pb2'
  # @@protoc_insertion_point(class_scope:drtrl.server.Stats)
  })
_sym_db.RegisterMessage(Stats)

RebalancingInstructions = _reflection.GeneratedProtocolMessageType('RebalancingInstructions', (_message.Message,), {

  'ZoneTargets' : _reflection.GeneratedProtocolMessageType('ZoneTargets', (_message.Message,), {
    'DESCRIPTOR' : _REBALANCINGINSTRUCTIONS_ZONETARGETS,
    '__module__' : 'drtrl.server.rebalancer_pb2'
    # @@protoc_insertion_point(class_scope:drtrl.server.RebalancingInstructions.ZoneTargets)
    })
  ,

  'MinCostFlow' : _reflection.GeneratedProtocolMessageType('MinCostFlow', (_message.Message,), {
    'DESCRIPTOR' : _REBALANCINGINSTRUCTIONS_MINCOSTFLOW,
    '__module__' : 'drtrl.server.rebalancer_pb2'
    # @@protoc_insertion_point(class_scope:drtrl.server.RebalancingInstructions.MinCostFlow)
    })
  ,
  'DESCRIPTOR' : _REBALANCINGINSTRUCTIONS,
  '__module__' : 'drtrl.server.rebalancer_pb2'
  # @@protoc_insertion_point(class_scope:drtrl.server.RebalancingInstructions)
  })
_sym_db.RegisterMessage(RebalancingInstructions)
_sym_db.RegisterMessage(RebalancingInstructions.ZoneTargets)
_sym_db.RegisterMessage(RebalancingInstructions.MinCostFlow)

RebalancingState = _reflection.GeneratedProtocolMessageType('RebalancingState', (_message.Message,), {

  'RebalancableVehiclesPerZoneEntry' : _reflection.GeneratedProtocolMessageType('RebalancableVehiclesPerZoneEntry', (_message.Message,), {
    'DESCRIPTOR' : _REBALANCINGSTATE_REBALANCABLEVEHICLESPERZONEENTRY,
    '__module__' : 'drtrl.server.rebalancer_pb2'
    # @@protoc_insertion_point(class_scope:drtrl.server.RebalancingState.RebalancableVehiclesPerZoneEntry)
    })
  ,
  'DESCRIPTOR' : _REBALANCINGSTATE,
  '__module__' : 'drtrl.server.rebalancer_pb2'
  # @@protoc_insertion_point(class_scope:drtrl.server.RebalancingState)
  })
_sym_db.RegisterMessage(RebalancingState)
_sym_db.RegisterMessage(RebalancingState.RebalancableVehiclesPerZoneEntry)


DESCRIPTOR._options = None
_REBALANCINGSTATE_REBALANCABLEVEHICLESPERZONEENTRY._options = None

_REBALANCINGSTRATEGY = _descriptor.ServiceDescriptor(
  name='RebalancingStrategy',
  full_name='drtrl.server.RebalancingStrategy',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=1185,
  serialized_end=1465,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetSpecification',
    full_name='drtrl.server.RebalancingStrategy.GetSpecification',
    index=0,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_REBALANCINGSPECIFICATION,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetCurrentState',
    full_name='drtrl.server.RebalancingStrategy.GetCurrentState',
    index=1,
    containing_service=None,
    input_type=_SIMULATIONTIME,
    output_type=_REBALANCINGSTATE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='PerformRebalancing',
    full_name='drtrl.server.RebalancingStrategy.PerformRebalancing',
    index=2,
    containing_service=None,
    input_type=_REBALANCINGINSTRUCTIONS,
    output_type=_SIMULATIONTIME,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_REBALANCINGSTRATEGY)

DESCRIPTOR.services_by_name['RebalancingStrategy'] = _REBALANCINGSTRATEGY

# @@protoc_insertion_point(module_scope)
