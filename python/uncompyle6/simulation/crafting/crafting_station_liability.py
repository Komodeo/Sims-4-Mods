# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\crafting_station_liability.py
# Compiled at: 2016-08-09 15:37:06
# Size of source mod 2**32: 1430 bytes
from interactions import ParticipantType
from interactions.liability import Liability
from sims4.tuning.tunable import HasTunableFactory

class CraftingStationLiability(Liability, HasTunableFactory):
    LIABILITY_TOKEN = 'CraftingStation'

    def __init__(self, interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._obj = interaction.get_participant(ParticipantType.Object)
        self._removed_from_cache = False

    def on_run(self):
        if self._removed_from_cache:
            return
        if self._obj is None:
            return
        self._obj.remove_from_crafting_cache()
        self._removed_from_cache = True

    def release(self):
        if not self._removed_from_cache:
            return
        if self._obj is None:
            return
        self._obj.add_to_crafting_cache()