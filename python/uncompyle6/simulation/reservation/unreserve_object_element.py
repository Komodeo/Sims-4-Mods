# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reservation\unreserve_object_element.py
# Compiled at: 2020-09-08 11:23:33
# Size of source mod 2**32: 2327 bytes
from element_utils import CleanupType
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.interaction_liabilities import RESERVATION_LIABILITY
from interactions.utils.line_utils import WaitingLineInteractionChainLiability
from sims4.tuning.tunable import TunableTuple, OptionalTunable, TunableSimMinute

class UnreserveObjectElement(XevtTriggeredElement):
    FACTORY_TUNABLES = {'timing': TunableTuple(description="\n            The behavior should occur at the very beginning of the\n            interaction.  It will not be tightly synchronized visually with\n            animation.  This isn't a very common use case and would most\n            likely be used in an immediate interaction or to change hidden\n            state that is used for bookkeeping rather than visual\n            appearance.\n            ",
                 offset_time=OptionalTunable(description='\n                If enabled, the interaction will wait this amount of time\n                after the beginning before running the element.\n\n                Only use this if absolutely necessary. Better alternatives\n                include using xevts, time based conditional action with\n                loot ops, and using outcomes.\n                ',
                 tunable=TunableSimMinute(description='The interaction will wait this amount of time after the beginning before running the element', default=2),
                 enabled_by_default=True),
                 locked_args={'timing':XevtTriggeredElement.AT_BEGINNING, 
                'criticality':CleanupType.NotCritical,  'xevt_id':None,  'supports_failsafe':None})}

    def _do_behavior(self):
        self.interaction.remove_liability(RESERVATION_LIABILITY)
        self.interaction.remove_liability(WaitingLineInteractionChainLiability.LIABILITY_TOKEN)
        return True