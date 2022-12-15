# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\routing_constants.py
# Compiled at: 2020-07-24 16:14:34
# Size of source mod 2**32: 4503 bytes
import enum
INVALID_TERRAIN_HEIGHT = -100.0

class TransitionFailureReasons(enum.Int, export=False):
    UNKNOWN = 0
    NO_DESTINATION_NODE = 1
    NO_PATH_FOUND = 2
    NO_VALID_INTERSECTION = 3
    NO_GOALS_GENERATED = 4
    BUILD_BUY = 5
    BLOCKING_OBJECT = 6
    RESERVATION = 7
    NO_CONNECTIVITY_TO_GOALS = 8
    PATH_PLAN_FAILED = 9
    GOAL_ON_SLOPE = 10
    INSUFFICIENT_HEAD_CLEARANCE = 11