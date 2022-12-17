# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_skill_fixup_action.py
# Compiled at: 2019-09-16 13:25:30
# Size of source mod 2**32: 986 bytes
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims4.tuning.tunable import Tunable
from statistics.skill import Skill

class _SimInfoSkillFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'skill':Skill.TunableReference(description='\n            The skill which will be assigned to the sim_info.\n            '), 
     'initial_level':Tunable(description='\n            The initial level at which to assign the skill.\n            ',
       tunable_type=int,
       default=1)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def __call__(self, sim_info):
        sim_info.commodity_tracker.set_user_value(self.skill, self.initial_level)