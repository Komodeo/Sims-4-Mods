# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lunar_cycle\lunar_cycle_enums.py
# Compiled at: 2022-06-13 15:18:17
# Size of source mod 2**32: 902 bytes
import enum

class LunarPhaseType(enum.Int):
    NEW_MOON = 0
    WAXING_CRESCENT = 1
    FIRST_QUARTER = 2
    WAXING_GIBBOUS = 3
    FULL_MOON = 4
    WANING_GIBBOUS = 5
    THIRD_QUARTER = 6
    WANING_CRESCENT = 7


class LunarPhaseLockedOption(LunarPhaseType, export=False):
    NO_LUNAR_PHASE_LOCK = 8


class LunarCycleLengthOption(enum.Int):
    TWO_DAY = 0
    FOUR_DAY = 1
    FULL_LENGTH = 2
    DOUBLE_LENGTH = 3
    TRIPLE_LENGTH = 4