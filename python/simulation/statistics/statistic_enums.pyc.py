# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_enums.py
# Compiled at: 2019-06-11 17:31:41
# Size of source mod 2**32: 1689 bytes
import enum

class PeriodicStatisticBehavior(enum.Int):
    APPLY_AT_START_ONLY = ...
    RETEST_ON_INTERVAL = ...
    APPLY_AT_INTERVAL_ONLY = ...


class CommodityTrackerSimulationLevel(enum.Int, export=False):
    REGULAR_SIMULATION = ...
    LOW_LEVEL_SIMULATION = ...


class StatisticLockAction(enum.Int):
    DO_NOT_CHANGE_VALUE = 0
    USE_MIN_VALUE_TUNING = 1
    USE_MAX_VALUE_TUNING = 2
    USE_BEST_VALUE_TUNING = 3