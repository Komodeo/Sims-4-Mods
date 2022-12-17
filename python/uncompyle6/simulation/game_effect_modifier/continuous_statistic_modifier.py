# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\continuous_statistic_modifier.py
# Compiled at: 2020-11-20 01:43:08
# Size of source mod 2**32: 3060 bytes
from game_effect_modifier.base_game_effect_modifier import BaseGameEffectModifier
from game_effect_modifier.game_effect_type import GameEffectType
from sims4.log import StackVar
from sims4.tuning.tunable import HasTunableSingletonFactory, Tunable, TunablePackSafeReference
from statistics.skill import Skill
import services, sims4.log, sims4.resources
logger = sims4.log.LoggerClass('ContinuousStatisticModifier')

class ContinuousStatisticModifier(HasTunableSingletonFactory, BaseGameEffectModifier):

    @staticmethod
    def _verify_tunable_callback(cls, tunable_name, source, value):
        if value.modifier_value == 0:
            logger.error('Trying to tune a Continuous Statistic Modifier to have a value of 0 which will do nothing on: {}.', StackVar(('cls', )))

    FACTORY_TUNABLES = {'description':"\n        The modifier to add to the current statistic modifier of this continuous statistic,\n        resulting in it's increase or decrease over time. Adding this modifier to something by\n        default doesn't change, i.e. a skill, will start that skill to be added to over time.\n        ", 
     'statistic':TunablePackSafeReference(description='\n        "The statistic we are operating on.',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'modifier_value':Tunable(description='\n        The value to add to the modifier. Can be negative.',
       tunable_type=float,
       default=0), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, statistic, modifier_value, **kwargs):
        super().__init__(GameEffectType.CONTINUOUS_STATISTIC_MODIFIER)
        self.statistic = statistic
        self.modifier_value = modifier_value

    def apply_modifier(self, sim_info):
        if self.statistic is None:
            return
        stat = sim_info.get_statistic(self.statistic)
        if stat is None:
            return
        stat.add_statistic_modifier(self.modifier_value)
        if isinstance(stat, Skill):
            sim_info.current_skill_guid = stat.guid64

    def remove_modifier(self, sim_info, handle):
        if self.statistic is None:
            return
            stat = sim_info.get_statistic(self.statistic)
            if stat is None:
                return
        else:
            stat.remove_statistic_modifier(self.modifier_value)
            if isinstance(stat, Skill):
                if stat._statistic_modifier <= 0 and sim_info.current_skill_guid == stat.guid64:
                    sim_info.current_skill_guid = 0