# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\baby\baby_aging.py
# Compiled at: 2017-06-26 18:46:47
# Size of source mod 2**32: 1449 bytes
from interactions.aop import AffordanceObjectPair
from interactions.context import InteractionContext, InteractionSource, QueueInsertStrategy
from interactions.priority import Priority
from sims.aging.aging_element import ChangeAgeElement
import services, sims4.log
logger = sims4.log.Logger('Baby')

def baby_age_up(sim_info):
    bassinet = services.object_manager().get(sim_info.id)
    if bassinet is None:
        return
    middle_bassinet = bassinet.replace_for_age_up()
    if middle_bassinet is None:
        return

    def _on_spawn(sim):
        affordance = bassinet.get_age_up_addordance()
        aop = AffordanceObjectPair(affordance, middle_bassinet, affordance, None, is_baby_age_up=True)
        context = InteractionContext(sim, (InteractionSource.SCRIPT), (Priority.Critical), insert_strategy=(QueueInsertStrategy.NEXT))
        result = aop.test_and_execute(context)
        if not result:
            logger.error('Failed to run baby age up interaction: {}', result, owner='jjacobson')

    ChangeAgeElement.spawn_for_age_up(sim_info, (middle_bassinet.position), spawn_action=_on_spawn, sim_location=(middle_bassinet.location))