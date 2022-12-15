# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\pets\missing_pets_liability.py
# Compiled at: 2017-09-13 13:11:07
# Size of source mod 2**32: 1539 bytes
from interactions import ParticipantType
from interactions.liability import Liability
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableEnumEntry
MISSING_PET_LIABILITY = 'MissingPetLiability'

class MissingPetLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = MISSING_PET_LIABILITY
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant of the interaction that is going missing.\n            ',
                      tunable_type=ParticipantType,
                      default=(ParticipantType.Actor))}

    def __init__(self, interaction, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._interaction = interaction

    def should_transfer(self, continuation):
        return False

    def on_run(self):
        participant = self._interaction.get_participant(self.participant)
        participant.sim_info.household.missing_pet_tracker.run_away_succeeded(participant.sim_info)

    def release(self):
        participant = self._interaction.get_participant(self.participant)
        participant.sim_info.household.missing_pet_tracker.run_away_interaction_released(participant.sim_info)