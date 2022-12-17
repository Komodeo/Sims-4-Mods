# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\seasons\seasons_enums.py
# Compiled at: 2018-04-16 17:26:15
# Size of source mod 2**32: 1160 bytes
import enum

class SeasonType(enum.Int):
    SUMMER = 0
    FALL = 1
    WINTER = 2
    SPRING = 3


class SeasonLength(enum.Int):
    NORMAL = 0
    LONG = 1
    VERY_LONG = 2


class SeasonSegment(enum.Int):
    EARLY = 0
    MID = 1
    LATE = 2


class SeasonParameters(enum.Int):
    LEAF_ACCUMULATION = 1
    FLOWER_GROWTH = 2
    FOLIAGE_REDUCTION = 3
    FOLIAGE_COLORSHIFT = 4


class SeasonSetSource(enum.Int, export=False):
    PROGRESSION = ...
    CHEAT = ...
    LOOT = ...