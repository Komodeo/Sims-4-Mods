# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\join_liability.py
# Compiled at: 2016-08-09 15:38:08
# Size of source mod 2**32: 2222 bytes
import weakref
from interactions.interaction_finisher import FinishingType
from interactions.liability import Liability
JOIN_INTERACTION_LIABILITY = 'JoinInteractionLiability'

class JoinInteractionLiability(Liability):

    def __init__(self, join_interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._join_interaction_refs = [
         weakref.ref(join_interaction)]
        self._owning_interaction_ref = None

    def merge(self, interaction, key, new_liability):
        self._join_interaction_refs.extend(new_liability._join_interaction_refs)
        return self

    def on_add(self, interaction):
        self._owning_interaction_ref = weakref.ref(interaction)

    def release(self):
        for join_ref in self._join_interaction_refs:
            join_interaction = join_ref() if join_ref() is not None else None
            if join_interaction is not None:
                finishing_type = FinishingType.LIABILITY
                owning_interaction = self._owning_interaction_ref() if self._owning_interaction_ref is not None else None
                if owning_interaction is not None:
                    finishing_type = owning_interaction.finishing_type
                else:
                    join_interaction.cancel(finishing_type, cancel_reason_msg='Linked join interaction has finished/been cancelled.')