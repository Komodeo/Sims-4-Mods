# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_categories.py
# Compiled at: 2013-05-16 19:23:47
# Size of source mod 2**32: 498 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import sims4.log
logger = sims4.log.Logger('SimStatistics')

class StatisticCategory(DynamicEnum):
    INVALID = 0