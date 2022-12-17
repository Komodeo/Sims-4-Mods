# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\rabbit_hole\tunable_rabbit_hole_condition.py
# Compiled at: 2018-08-14 09:06:05
# Size of source mod 2**32: 918 bytes
from sims4.tuning.tunable import TunableVariant
from statistics.statistic_conditions import TunableStatisticCondition

class TunableRabbitHoleCondition(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, stat_based=TunableStatisticCondition(description='\n                A condition based on the status of a statistic.\n                '), 
         default='stat_based', **kwargs)