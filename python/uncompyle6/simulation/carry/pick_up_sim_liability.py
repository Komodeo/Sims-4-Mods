# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\carry\pick_up_sim_liability.py
# Compiled at: 2016-09-15 17:56:30
# Size of source mod 2**32: 1686 bytes
from interactions.liability import Liability

class WaitToBePickedUpLiability(Liability):
    LIABILITY_TOKEN = 'WaitToBePickedUpLiability'


class PickUpSimLiability(Liability):
    LIABILITY_TOKEN = 'PickUpSimLiability'

    def __init__(self, original_interaction, on_finish_callback):
        super().__init__()
        self._interaction = None
        self._original_interaction = original_interaction
        self._on_finish_callback = on_finish_callback
        original_interaction.add_liability(WaitToBePickedUpLiability.LIABILITY_TOKEN, WaitToBePickedUpLiability())

    @property
    def original_interaction(self):
        return self._original_interaction

    def on_add(self, interaction):
        self._interaction = interaction

    def should_transfer(self, continuation):
        return continuation.is_putdown

    def transfer(self, interaction):
        self._interaction = interaction

    def release(self):
        if self._on_finish_callback is not None:
            self._on_finish_callback(self._interaction)
        self._original_interaction.remove_liability(WaitToBePickedUpLiability.LIABILITY_TOKEN)