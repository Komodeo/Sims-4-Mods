# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\stand.py
# Compiled at: 2021-09-01 10:58:18
# Size of source mod 2**32: 1373 bytes
from interactions.base.super_interaction import SuperInteraction
from sims4.tuning.tunable import TunableReference
import services, sims4.resources

class StandSuperInteraction(SuperInteraction):
    STAND_POSTURE_TYPE = TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)), description='The Posture Type for the Stand posture.')

    @classmethod
    def _is_linked_to(cls, super_affordance):
        return cls is not super_affordance

    def get_cancel_replacement_aops_contexts_postures(self, can_transfer_ownership=True, carry_cancel_override=None):
        if self.target is None:
            if self.sim.posture.posture_type == self.STAND_POSTURE_TYPE:
                return []
        return super().get_cancel_replacement_aops_contexts_postures(can_transfer_ownership=can_transfer_ownership, carry_cancel_override=carry_cancel_override)