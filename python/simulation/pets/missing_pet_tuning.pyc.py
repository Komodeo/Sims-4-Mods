# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\pets\missing_pet_tuning.py
# Compiled at: 2017-08-31 11:08:56
# Size of source mod 2**32: 3221 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from objects import ALL_HIDDEN_REASONS
from sims4.tuning.tunable import TunableFactory
import interactions, singletons

class MakePetMissing(BaseLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            return
        if subject.is_pet:
            if subject.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                missing_pet_tracker = subject.household.missing_pet_tracker
                missing_pet_tracker.run_away(subject)

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        if description is singletons.DEFAULT:
            description = 'The object the tags are applied to.'
        return (BaseLootOperation.get_participant_tunable)('subject', description=description, 
         default_participant=interactions.ParticipantType.Actor, **kwargs)


class PostMissingPetAlert(BaseLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            return
        if subject.household.missing_pet_tracker.is_pet_missing(subject):
            missing_pet_tracker = subject.household.missing_pet_tracker
            missing_pet_tracker.post_alert()

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        if description is singletons.DEFAULT:
            description = 'The object the tags are applied to.'
        return (BaseLootOperation.get_participant_tunable)('subject', description=description, 
         default_participant=interactions.ParticipantType.Actor, **kwargs)