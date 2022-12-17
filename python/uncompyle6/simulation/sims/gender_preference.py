# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\gender_preference.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 2710 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import Tunable
import interactions

class GenderPreferenceOp(BaseLootOperation):
    FACTORY_TUNABLES = {'gender_preference_statistic_increase':Tunable(description='\n                The value that will be added to the appropriate gender\n                preference statistic when this loot is applied. The global\n                gender preference tuning is module tunable GENDER_PREFERENCE.\n                ',
       tunable_type=int,
       default=0), 
     'gender_preference_statistic_decrease':Tunable(description='\n                The value that will be added to the appropriate gender\n                preference statistic when this loot is applied. This should be\n                a negative number. The global gender preference tuning is a\n                module tunable GENDER_PREFERENCE.\n                ',
       tunable_type=int,
       default=0)}

    def __init__(self, gender_preference_statistic_increase, gender_preference_statistic_decrease, **kwargs):
        (super().__init__)(target_participant_type=interactions.ParticipantType.TargetSim, **kwargs)
        self._gender_preference_statistic_increase = gender_preference_statistic_increase
        self._gender_preference_statistic_decrease = gender_preference_statistic_decrease

    def _apply_gender_preference_change(self, subject_sim_info, target_sim_info):
        if not subject_sim_info.is_exploring_sexuality:
            return
        for gender, gender_preference_statistic in subject_sim_info.get_gender_preferences_gen():
            if gender_preference_statistic is None:
                continue
            if gender == target_sim_info.gender:
                gender_preference_statistic.add_value(self._gender_preference_statistic_increase)
            else:
                gender_preference_statistic.add_value(self._gender_preference_statistic_decrease)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        self._apply_gender_preference_change(subject, target)
        self._apply_gender_preference_change(target, subject)