# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_activity.py
# Compiled at: 2022-02-09 10:21:47
# Size of source mod 2**32: 1489 bytes
from holidays.holiday_tradition import HolidayTradition, TraditionType
from sims4.tuning.instances import lock_instance_tunables

class SituationActivity(HolidayTradition):
    REMOVE_INSTANCE_TUNABLES = ('pre_holiday_buffs', 'pre_holiday_buff_reason', 'holiday_buffs',
                                'holiday_buff_reason', 'drama_nodes_to_score', 'drama_nodes_to_run',
                                'additional_walkbys', 'preference', 'preference_reward_buff',
                                'lifecycle_actions', 'events', 'core_object_tags',
                                'deco_object_tags', 'business_cost_multiplier')