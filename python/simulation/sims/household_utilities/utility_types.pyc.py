# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\household_utilities\utility_types.py
# Compiled at: 2016-04-20 17:17:06
# Size of source mod 2**32: 526 bytes
from sims4.tuning.dynamic_enum import DynamicEnum

class Utilities(DynamicEnum):
    POWER = 0
    WATER = 1


class UtilityShutoffReasonPriority(DynamicEnum):
    NO_REASON = 0