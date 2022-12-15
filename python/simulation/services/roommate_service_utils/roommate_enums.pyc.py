# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\roommate_service_utils\roommate_enums.py
# Compiled at: 2019-07-24 10:55:45
# Size of source mod 2**32: 561 bytes
from sims4.tuning.dynamic_enum import DynamicEnumLocked
import enum

class RoommateLeaveReason(DynamicEnumLocked):
    INVALID = 0
    OVERCAPACITY = 1


class LeaveReasonTestingTime(enum.Int):
    UNTESTED = 0
    HOUSEHOLD_ROOMMATES_ALL_LOTS = 1
    HOUSEHOLD_ROOMMATES_HOME_LOT = 2
    ALL_ROOMMATES = 3