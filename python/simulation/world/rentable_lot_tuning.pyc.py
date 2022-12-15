# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\rentable_lot_tuning.py
# Compiled at: 2014-09-08 15:07:16
# Size of source mod 2**32: 925 bytes
from sims4.tuning.tunable import TunableTuple, Tunable
from sims4.tuning.tunable_base import ExportModes

class RentableZoneTuning:
    PRICE_MODIFIERS = TunableTuple(description='\n        Global price modifiers for all rentable zones.\n        ',
      add=Tunable(description='\n            Add modifier for the price to rent a lot.\n            ',
      tunable_type=float,
      default=0.0),
      multiply=Tunable(description='\n            Multiplier for the price to rent a lot.\n            ',
      tunable_type=float,
      default=1.0),
      export_class_name='TunablePriceModifiers',
      export_modes=(ExportModes.All))