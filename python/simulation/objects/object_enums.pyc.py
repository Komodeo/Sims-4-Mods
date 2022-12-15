# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\object_enums.py
# Compiled at: 2019-07-25 16:23:33
# Size of source mod 2**32: 2130 bytes
import enum
from sims4.tuning.dynamic_enum import DynamicEnum

class ResetReason(enum.Int, export=False):
    NONE = ...
    RESET_EXPECTED = ...
    RESET_ON_ERROR = ...
    BEING_DESTROYED = ...


class ItemLocation(enum.Int):
    INVALID_LOCATION = 0
    ON_LOT = 1
    SIM_INVENTORY = 2
    HOUSEHOLD_INVENTORY = 3
    OBJECT_INVENTORY = 4
    FROM_WORLD_FILE = 5
    FROM_OPEN_STREET = 6
    FROM_CONDITIONAL_LAYER = 7


class PersistenceType(enum.Int):
    FULL = 0
    BUILDBUY = 1
    NONE = 2


class ObjectClaimStatus(enum.Int, export=False):
    UNCLAIMED = 0
    CLAIMED = 1


class ObjectRoutingBehaviorTrackingCategory(DynamicEnum):
    NONE = 0
    BOT = 1