# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\adoption\adoption_liability.py
# Compiled at: 2017-04-10 17:13:28
# Size of source mod 2**32: 793 bytes
from interactions.liability import Liability

class AdoptionLiability(Liability):
    LIABILITY_TOKEN = 'AdoptionLiability'

    def __init__(self, household, sim_ids, **kwargs):
        (super().__init__)(**kwargs)
        self._household = household
        self._sim_ids = sim_ids

    def on_add(self, interaction):
        for sim_id in self._sim_ids:
            self._household.add_adopting_sim(sim_id)

    def release(self):
        for sim_id in self._sim_ids:
            self._household.remove_adopting_sim(sim_id)