# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\high_school_graduation\graduation_ops.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 2436 bytes
import services, sims4
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableEnumEntry, AutoFactoryInit, TunableVariant, TunableTuple
logger = sims4.log.Logger('HighSchoolGraduation', default_owner='rfleig')

class GraduationUpdateSims(BaseLootOperation):
    ADD = 0
    REMOVE = 1
    VALEDICTORIAN = 2
    FACTORY_TUNABLES = {'action': TunableVariant(description='\n            The action to be applied to the specified target.\n            ',
                 add=TunableTuple(description='\n                Add a Sim as a graduating student.\n                ',
                 locked_args={'action': ADD}),
                 remove=TunableTuple(description='\n                Remove a Sim from being considered for graduation.\n                ',
                 locked_args={'action': REMOVE}),
                 add_valedictorian=TunableTuple(description='\n                Mark a Sim as being the valedictorian for the appropriate graduation ceremony.\n                ',
                 locked_args={'action': VALEDICTORIAN}),
                 default='add')}

    def __init__(self, action=None, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._action = action

    def _apply_to_subject_and_target(self, subject, target, resolver):
        graduation_service = services.get_graduation_service()
        if not graduation_service:
            logger.error('Trying to add a Sim to graduation when there is no graduation service.')
        if self._action.action == GraduationUpdateSims.ADD:
            graduation_service.add_sim_info_as_graduating(subject)
        else:
            if self._action.action == GraduationUpdateSims.REMOVE:
                graduation_service.remove_sim_info_as_graduating(subject)
            else:
                if self._action.action == GraduationUpdateSims.VALEDICTORIAN:
                    if not graduation_service.add_sim_as_valedictorian(subject):
                        logger.error('Unable to mark the Sim ({}) as valedictorian. This would only happen if there is already a valedictorian or the Sim is not currently graduating.', subject)