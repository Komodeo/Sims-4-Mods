# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\global_gender_preference_tuning.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 11478 bytes
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableReference, TunableList, TunableTuple, Tunable, TunableSet
import enum, services, sims.sim_info_types, sims4

class GenderPreference(enum.Int):
    LIKES_NEITHER = 0
    HETEROSEXUAL = 1
    HOMOSEXUAL = 2
    BISEXUAL = 3


class SexualityStatus(enum.Int):
    NOT_EXPLORING = 0
    EXPLORING = 1


class GenderPreferenceType(enum.Int):
    INVALID = 0
    ROMANTIC = 1
    WOOHOO = 2


class GlobalGenderPreferenceTuning:
    GENDER_PREFERENCE = TunableMapping(description='\n        A mapping between gender and the gender preference statistic for easy lookup.\n        ',
      key_type=TunableEnumEntry(description='\n            The gender to index the gender preference to.\n            ',
      tunable_type=(sims.sim_info_types.Gender),
      default=(sims.sim_info_types.Gender.MALE)),
      value_type=TunableReference(description='\n            The statistic that represents the matching gender preference.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC))))
    GENDER_PREFERENCE_WEIGHTS = TunableList(description='\n        A weightings list for the weighted random choice of sexual preference.\n        ',
      tunable=TunableTuple(description='\n            A mapping between gender and the gender preference statistic for easy lookup.\n            ',
      gender_preference=TunableEnumEntry(description='\n                The gender to index the gender preference to.\n                ',
      tunable_type=GenderPreference,
      default=(GenderPreference.LIKES_NEITHER)),
      weight=Tunable(description='\n                The weight to denote the percentage of NPCs we want to exist with this gender preference.\n                ',
      tunable_type=int,
      default=0)))
    GENDER_PREFERENCE_MAPPING = TunableMapping(description='\n        A mapping between gender preference and matching orientation for easy lookup\n        (e.g. a heterosexual female Sim will be attracted to only male Sims.)\n        ',
      key_type=TunableEnumEntry(description='\n            The gender preference to match attraction to.\n            ',
      tunable_type=GenderPreference,
      default=(GenderPreference.LIKES_NEITHER)),
      value_type=TunableMapping(description='\n            Mapping between gender of a particular orientation and their preferences.\n            ',
      key_type=TunableEnumEntry(description='\n                The gender of the "actor."\n                ',
      tunable_type=(sims.sim_info_types.Gender),
      default=(sims.sim_info_types.Gender.MALE)),
      value_type=(TunableSet(TunableEnumEntry(description='\n                    Which genders we expect this Sim with this preference to be attracted to.\n                    ',
      tunable_type=(sims.sim_info_types.Gender),
      default=(sims.sim_info_types.Gender.MALE))))))
    GENDER_PREFERENCE_THRESHOLD = Tunable(description='\n        The threshold in which this sim will consider having an appropriate\n        gender preference. Note that being GREATER THAN OR EQUAL TO this \n        threshold will indicate the Sim has an attraction to the respective \n        gender and will have the appropriate attraction trait, whereas LESS THAN \n        will indicate the opposite (that they have the NotAttracted trait).\n        ',
      tunable_type=float,
      default=0)
    EXPLORING_SEXUALITY_TRAITS_MAPPING = TunableMapping(description='\n        A mapping between the exploring enum to expected traits for easy lookup.\n        ',
      key_type=TunableEnumEntry(description='\n            Whether Sim should be exploring or not exploring their sexuality.\n            ',
      tunable_type=SexualityStatus,
      default=(SexualityStatus.EXPLORING)),
      value_type=TunableReference(description='\n            The matching trait representative of exploring or not exploring sexuality.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT))))
    EXPLORING_SEXUALITY_WEIGHTS = TunableList(description='\n        A weightings list for the weighted random choice of exploring sexuality.\n        ',
      tunable=TunableTuple(exploring_sexuality=TunableEnumEntry(description='\n                Whether Sim should be exploring or not exploring their sexuality.\n                ',
      tunable_type=SexualityStatus,
      default=(SexualityStatus.EXPLORING)),
      weight=Tunable(description='\n                The weight to denote the percentage of NPCs we want to exist with this trait.\n                ',
      tunable_type=int,
      default=0)))
    ROMANTIC_PREFERENCE_TRAITS_MAPPING = TunableMapping(description='\n        A mapping between gender and the romantic orientation traits for easy lookup.\n        ',
      key_type=TunableEnumEntry(description='\n            The gender to index the attraction trait to.\n            ',
      tunable_type=(sims.sim_info_types.Gender),
      default=(sims.sim_info_types.Gender.MALE)),
      value_type=TunableTuple(description='\n            A tuple of traits representing that the Sim is attracted and not attracted, respectively.\n            ',
      is_attracted_trait=TunableReference(description='\n                Reference to the trait that denotes that the Sim is attracted to this gender.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT))),
      not_attracted_trait=TunableReference(description='\n                Reference to the trait that denotes that the Sim is not attracted to this gender.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)))))
    WOOHOO_PREFERENCE_TRAITS_MAPPING = TunableMapping(description='\n        A mapping between gender and the woohoo orientation traits for easy lookup.\n        ',
      key_type=TunableEnumEntry(description='\n            The gender to index the attraction trait to.\n            ',
      tunable_type=(sims.sim_info_types.Gender),
      default=(sims.sim_info_types.Gender.MALE)),
      value_type=TunableTuple(description='\n            A tuple of traits representing that the Sim is attracted and not attracted, respectively.\n            ',
      is_attracted_trait=TunableReference(description='\n                Reference to the trait that denotes that the Sim is attracted to this gender.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT))),
      not_attracted_trait=TunableReference(description='\n                Reference to the trait that denotes that the Sim is not attracted to this gender.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)))))
    enable_autogeneration_same_sex_preference = False
    ENABLE_AUTOGENERATION_SAME_SEX_PREFERENCE_THRESHOLD = Tunable(description="\n        A value that, once crossed, indicates the player's allowance of same-\n        sex relationships with townie auto-generation.\n        ",
      tunable_type=float,
      default=1.0)
    ENABLED_AUTOGENERATION_SAME_SEX_PREFERENCE_WEIGHTS = TunableList(description='\n        An alternative weightings list for the weighted random choice of sexual\n        preference after a romantic same-sex relationship has been kindled.\n        ',
      tunable=TunableTuple(description='\n            A mapping between gender and desired weight.\n            ',
      gender_preference=TunableEnumEntry(description='\n                The gender to index the gender preference to.\n                ',
      tunable_type=GenderPreference,
      default=(GenderPreference.LIKES_NEITHER)),
      weight=Tunable(description='\n                The weight to denote the percentage of NPCs we want to exist with this gender preference.\n                ',
      tunable_type=int,
      default=0)))
    ENABLED_AUTOGENERATION_EXPLORING_SEXUALITY_WEIGHTS = TunableList(description='\n        An alternative weightings list for the weighted random choice of sexuality\n        exploration after a romantic same-sex relationship has been kindled.\n        ',
      tunable=TunableTuple(description="\n            A mapping between whether we're exploring sexuality and the desired weight.\n            ",
      exploring_sexuality=TunableEnumEntry(description='\n                Whether Sim should be exploring or not exploring their sexuality.\n                ',
      tunable_type=SexualityStatus,
      default=(SexualityStatus.EXPLORING)),
      weight=Tunable(description='\n                The weight to denote the percentage of NPCs we want to exist with this trait.\n                ',
      tunable_type=int,
      default=0)))
    MALE_CLOTHING_PREFERENCE_TRAIT = TunableReference(description='\n        The trait that signifies that this sim prefers to wear male clothing.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)))
    FEMALE_CLOTHING_PREFERENCE_TRAIT = TunableReference(description='\n        The trait that signifies that this sim prefers to wear female clothing.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)))

    @classmethod
    def get_preference_traits(cls):
        romantic_traits = []
        woohoo_traits = []
        for trait_tuple in GlobalGenderPreferenceTuning.ROMANTIC_PREFERENCE_TRAITS_MAPPING.values():
            romantic_traits.extend([trait_tuple.is_attracted_trait, trait_tuple.not_attracted_trait])

        for trait_tuple in GlobalGenderPreferenceTuning.WOOHOO_PREFERENCE_TRAITS_MAPPING.values():
            woohoo_traits.extend([trait_tuple.is_attracted_trait, trait_tuple.not_attracted_trait])

        return (
         romantic_traits, woohoo_traits)