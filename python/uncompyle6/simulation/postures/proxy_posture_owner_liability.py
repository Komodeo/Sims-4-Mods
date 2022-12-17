# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\proxy_posture_owner_liability.py
# Compiled at: 2018-09-24 14:47:11
# Size of source mod 2**32: 1592 bytes
from interactions.interaction_finisher import FinishingType
from interactions.liability import Liability
from sims4.tuning.tunable import HasTunableFactory

class ProxyPostureOwnerLiability(Liability, HasTunableFactory):
    LIABILITY_TOKEN = 'ProxyPostureOwnerLiability'

    def __init__(self, interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._interaction = interaction

    def transfer(self, interaction):
        self._interaction = interaction

    def release(self):
        sim = self._interaction.sim
        posture = sim.posture_state.body
        if self._interaction in posture.owning_interactions:
            if len(posture.owning_interactions) == 1:
                if posture.source_interaction is not None:
                    if posture.source_interaction is not self._interaction:
                        posture.source_interaction.cancel((FinishingType.SI_FINISHED), cancel_reason_msg='Posture Proxy Owner Liability Released')