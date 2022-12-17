# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\inventory_owner_tuning.py
# Compiled at: 2015-02-14 15:12:46
# Size of source mod 2**32: 521 bytes
from objects.components.state import TunableStateValueReference
from sims4.tuning.tunable import TunableList

class InventoryTuning:
    INVALID_ACCESS_STATES = TunableList(TunableStateValueReference(description='\n        If an inventory owner is in any of the states tuned here, it will not\n        be available to grab objects out of.\n        ',
      pack_safe=True))