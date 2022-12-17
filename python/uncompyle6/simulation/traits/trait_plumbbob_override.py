# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_plumbbob_override.py
# Compiled at: 2016-07-14 13:28:10
# Size of source mod 2**32: 1504 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry
from sims4.tuning.tunable_hash import TunableStringHash64

class PlumbbobOverridePriority(DynamicEnum):
    INVALID = 0


class PlumbbobOverrideRequest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'active_sim_plumbbob':TunableStringHash64(description='\n            The plumbbob model to use when this is the active sim,\n            '), 
     'active_sim_club_leader_plumbbob':TunableStringHash64(description="\n            The plumbbob model to use when this is the active sim and they're\n            the leader of the club.\n            "), 
     'priority':TunableEnumEntry(description='\n            The requests priority.\n            ',
       tunable_type=PlumbbobOverridePriority,
       default=PlumbbobOverridePriority.INVALID,
       invalid_enums={
      PlumbbobOverridePriority.INVALID})}