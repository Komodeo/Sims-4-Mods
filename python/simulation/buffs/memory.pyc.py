# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\buffs\memory.py
# Compiled at: 2015-09-23 21:02:33
# Size of source mod 2**32: 1872 bytes
from sims4.localization import TunableLocalizedString
from sims4.tuning.dynamic_enum import DynamicEnumLocked
from sims4.tuning.tunable import TunableMapping, TunableTuple, TunableEnumEntry, TunableReference
from sims4.tuning.tunable_base import ExportModes
import services, sims4

class MemoryUid(DynamicEnumLocked, display_sorted=True):
    Invalid = 0


class TunableMemoryTuple(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(name=TunableLocalizedString(export_modes=(ExportModes.All), description='Localization String for the kind of memory.'), reminisce_affordance=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)), class_restrictions='SuperInteraction', description='The interaction that is pushed on the Sim when they Reminisce about this Memory. Should most often be from the Reminisce Prototype.'), **kwargs)


class Memory:
    MEMORIES = TunableMapping(key_type=TunableEnumEntry(MemoryUid, export_modes=(ExportModes.All), default=(MemoryUid.Invalid), description='The Type of Memory. Should be unique. Defined in MemoryUid.'), value_type=(TunableMemoryTuple()),
      tuple_name='MemoryMappingTuple',
      export_modes=(ExportModes.All))