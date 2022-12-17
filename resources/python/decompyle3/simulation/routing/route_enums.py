# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_enums.py
# Compiled at: 2021-05-04 09:44:29
# Size of source mod 2**32: 2031 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class RouteEventType(enum.Int, export=False):
    LOW_REPEAT = 1
    LOW_SINGLE = 2
    HIGH_SINGLE = 3
    BROADCASTER = 4
    ENTER_LOT_LEVEL_INDOOR = 5
    INTERACTION_PRE = 6
    INTERACTION_POST = 7
    FIRST_OUTDOOR = 8
    LAST_OUTDOOR = 9
    FIRST_INDOOR = 10
    LAST_INDOOR = 11


class RouteEventPriority(DynamicEnum):
    DEFAULT = 0


class RoutingStageEvent(enum.Int, export=False):
    ROUTE_START = 0
    ROUTE_END = 1
    OBJECT_ROUTE_FAIL = 2