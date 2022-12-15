# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\zone_modifier\zone_modifier_tuning.py
# Compiled at: 2016-02-22 11:33:38
# Size of source mod 2**32: 1097 bytes
from sims4.tuning.tunable import TunableMapping, TunableHouseDescription, TunableList
from sims4.tuning.tunable_base import ExportModes
from zone_modifier.zone_modifier import ZoneModifier

class ZoneModifierTuning:
    INITIAL_ZONE_MODIFIERS = TunableMapping(description='\n        A mapping of HouseDescription to zone modifiers the lot with that\n        HouseDescription should have.\n        ',
      key_type=TunableHouseDescription(description='\n            The lot with this HouseDescription will have the tuned ZoneModifiers.\n            ',
      pack_safe=True),
      value_type=TunableList(description='\n            The list of ZoneModifiers to give to the lot with the corresponding\n            HouseDescription.\n            ',
      tunable=ZoneModifier.TunableReference(pack_safe=True)),
      tuple_name='InitialZoneModifiersMapping',
      export_modes=(ExportModes.All))