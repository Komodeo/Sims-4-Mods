# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\relationship_knowledge_ops.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 14421 bytes
import random
from distributor.shared_messages import IconInfoData
from event_testing.resolver import DoubleSimResolver
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
from interactions.utils.notification import NotificationElement
from sims.global_gender_preference_tuning import GenderPreferenceType
from sims4.localization import LocalizationHelperTuning
from sims4.tuning.tunable import TunableVariant, TunableTuple, TunableList, TunableRange, OptionalTunable, TunableSet, TunableReference, TunableEnumEntry, Tunable
from traits.trait_type import TraitType
from traits.traits import Trait
import interactions.utils, services, sims4.resources
logger = sims4.log.Logger('KnowOtherSimTraitOp', default_owner='asantos')

class KnowOtherSimTraitOp(BaseTargetedLootOperation):
    TRAIT_SPECIFIED = 0
    TRAIT_RANDOM = 1
    TRAIT_ALL = 2
    FACTORY_TUNABLES = {'traits':TunableVariant(description='\n            The traits that the subject may learn about the target.\n            ',
       specified=TunableTuple(description='\n                Specify individual traits that can be learned.\n                ',
       locked_args={'learned_type': TRAIT_SPECIFIED},
       potential_traits=TunableList(description='\n                    A list of traits that the subject may learn about the target.\n                    ',
       tunable=(Trait.TunableReference()))),
       random=TunableTuple(description='\n                Specify a random number of traits to learn.\n                ',
       locked_args={'learned_type': TRAIT_RANDOM},
       count=TunableRange(description='\n                    The number of potential traits the subject may learn about\n                    the target.\n                    ',
       tunable_type=int,
       default=1,
       minimum=1),
       trait_types=TunableList(description='\n                    The random traits are picked from the traits of these types.\n                    If this list is empty, pick only from Personality traits.\n                    ',
       tunable=TraitType,
       set_default_as_first_entry=True,
       unique_entries=True)),
       all=TunableTuple(description="\n                The subject Sim may learn all of the target's traits.\n                ",
       locked_args={'learned_type': TRAIT_ALL},
       trait_types=TunableList(description='\n                    The subject will learn all the traits of these types.\n                    If this list is empty, sim learns all the Personality traits.\n                    ',
       tunable=TraitType,
       set_default_as_first_entry=True,
       unique_entries=True)),
       default='specified'), 
     'notification':OptionalTunable(description="\n            Specify a notification that will be displayed for every subject if\n            information is learned about each individual target_subject. This\n            should probably be used only if you can ensure that target_subject\n            does not return multiple participants. The first two additional\n            tokens are the Sim and target Sim, respectively. A third token\n            containing a string with a bulleted list of trait names will be a\n            String token in here. If you are learning multiple traits, you\n            should probably use it. If you're learning a single trait, you can\n            get away with writing specific text that does not use this token.\n            ",
       tunable=NotificationElement.TunableFactory(locked_args={'recipient_subject': None})), 
     'notification_no_more_traits':OptionalTunable(description='\n            Specify a notification that will be displayed when a Sim knows\n            all traits of another target Sim.\n            ',
       tunable=NotificationElement.TunableFactory(locked_args={'recipient_subject': None}))}

    def __init__(self, *args, traits, notification, notification_no_more_traits, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.traits = traits
        self.notification = notification
        self.notification_no_more_traits = notification_no_more_traits

    @property
    def loot_type(self):
        return interactions.utils.LootType.RELATIONSHIP_BIT

    @staticmethod
    def _select_traits(knowledge, trait_tracker, trait_types, random_count=None):
        traits = set()
        for trait_type in trait_types:
            traits.update((trait for trait in trait_tracker.get_traits_of_type(trait_type) if trait not in knowledge.known_traits))

        if random_count is not None:
            if traits:
                return random.sample(traits, min(random_count, len(traits)))
        return traits

    def verify_valid_knowledge_trait(self, trait_tracker, interaction):
        if self.traits.learned_type == KnowOtherSimTraitOp.TRAIT_SPECIFIED:
            for trait in self.traits.potential_traits:
                if trait.trait_type not in trait_tracker.KNOWLEDGE_TRAIT_TYPES:
                    logger.error("{}: Tuned to get knowledge of trait {}, whose type {} is not allowed. Look at 'Knowledge Trait Types' in trait_tracker for the valid types.",
                      (interaction.affordance.__name__),
                      trait, (trait.trait_type), owner='asantos')

        else:
            if self.traits.learned_type == KnowOtherSimTraitOp.TRAIT_ALL or self.traits.learned_type == KnowOtherSimTraitOp.TRAIT_RANDOM:
                for trait_type in self.traits.trait_types:
                    if trait_type not in trait_tracker.KNOWLEDGE_TRAIT_TYPES:
                        logger.error("{}: Tuned to get knowledge of trait of type {}, which is not allowed. Look at 'Knowledge Trait Types' in trait_tracker for the valid types.",
                          (interaction.affordance.__name__),
                          (trait_type.name), owner='asantos')

    def _apply_to_subject_and_target(self, subject, target, resolver):
        knowledge = subject.relationship_tracker.get_knowledge((target.sim_id), initialize=True)
        if knowledge is None:
            return
        trait_tracker = target.trait_tracker
        if self.traits.learned_type == self.TRAIT_SPECIFIED:
            traits = tuple((trait for trait in self.traits.potential_traits if trait_tracker.has_trait(trait) if trait not in knowledge.known_traits))
        else:
            if self.traits.learned_type == self.TRAIT_ALL:
                traits = self._select_traits(knowledge, trait_tracker, self.traits.trait_types)
            else:
                pass
        if self.traits.learned_type == self.TRAIT_RANDOM:
            traits = self._select_traits(knowledge, trait_tracker, (self.traits.trait_types), random_count=(self.traits.count))
            if not traits:
                if self.notification_no_more_traits is not None:
                    interaction = resolver.interaction
                    if interaction is not None:
                        self.notification_no_more_traits(interaction).show_notification(additional_tokens=(subject, target), recipients=(subject,), icon_override=IconInfoData(obj_instance=target))
            for trait in traits:
                knowledge.add_known_trait(trait)

            if traits:
                interaction = resolver.interaction
                if interaction is not None:
                    if self.notification is not None:
                        trait_string = (LocalizationHelperTuning.get_bulleted_list)(*(None, ), *(trait.display_name(target) for trait in traits))
                        self.notification(interaction).show_notification(additional_tokens=(subject, target, trait_string), recipients=(subject,), icon_override=IconInfoData(obj_instance=target))


class KnowOtherSimCareerOp(BaseTargetedLootOperation):

    @property
    def loot_type(self):
        return interactions.utils.LootType.RELATIONSHIP_BIT

    def _apply_to_subject_and_target(self, subject, target, resolver):
        knowledge = subject.relationship_tracker.get_knowledge((target.sim_id), initialize=True)
        if knowledge is None or knowledge.knows_career:
            return
        knowledge.add_knows_career(target.sim_id)
        career_tracker = target.career_tracker
        if career_tracker.has_custom_career:
            career_tracker.custom_career_data.show_custom_career_knowledge_notification(subject, DoubleSimResolver(subject, target))
            return
        for career in knowledge.get_known_careers():
            career.show_knowledge_notification(subject, DoubleSimResolver(subject, target))


class KnowOtherSimSexualOrientationOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'gender_preference_types': TunableList(description='\n            Gender preference types that the actor may learn about the target.\n            ',
                                  tunable=TunableEnumEntry(description='\n                The orientation type of the Sim that we are adding knowledge for.\n                Romantic includes which genders the Sim is romantically attracted\n                to, as well as whether they are exploring. Woohoo refers to the\n                set of genders the Sim is interested in Woohoo with.\n                ',
                                  tunable_type=GenderPreferenceType,
                                  default=(GenderPreferenceType.ROMANTIC)))}

    def __init__(self, *args, gender_preference_types, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.gender_preference_types = gender_preference_types

    @property
    def loot_type(self):
        return interactions.utils.LootType.RELATIONSHIP_BIT

    def _apply_to_subject_and_target(self, subject, target, resolver):
        knowledge = subject.relationship_tracker.get_knowledge((target.sim_id), initialize=True)
        if knowledge is None:
            return
        for orientation_type in self.gender_preference_types:
            if orientation_type == GenderPreferenceType.ROMANTIC:
                if knowledge.knows_romantic_preference:
                    continue
                else:
                    knowledge.add_knows_romantic_preference(target.sim_id)
            else:
                if orientation_type == GenderPreferenceType.WOOHOO:
                    if knowledge.knows_woohoo_preference:
                        continue
                    else:
                        knowledge.add_knows_woohoo_preference(target.sim_id)
                else:
                    logger.error('Invalid orientation type tuned for Sexual Orientation knowledge.', owner='amwu')
                    return


class KnowOtherSimsStat(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'statistics': TunableSet(description='\n            A list of all the Statistics that the Sim can learn from\n            this loot op.\n            ',
                     tunable=TunableReference(description='\n                A tunable reference to a statistic that might be learned\n                from this op.\n                ',
                     manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
                     pack_safe=True))}

    def __init__(self, *args, statistics=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._statistics = statistics

    @property
    def loot_type(self):
        return interactions.utils.LootType.RELATIONSHIP

    def _apply_to_subject_and_target(self, subject, target, resolver):
        knowledge = subject.relationship_tracker.get_knowledge((target.sim_id), initialize=True)
        if knowledge is None:
            return
        target_tracker = target.commodity_tracker
        for stat in self._statistics:
            if target_tracker.has_statistic(stat):
                knowledge.add_known_stat(stat)


class KnowOtherSimMajorOp(BaseTargetedLootOperation):

    @property
    def loot_type(self):
        return interactions.utils.LootType.RELATIONSHIP_BIT

    def _apply_to_subject_and_target(self, subject, target, resolver):
        knowledge = subject.relationship_tracker.get_knowledge((target.sim_id), initialize=True)
        if knowledge is None or knowledge.knows_major:
            return
        knowledge.add_knows_major(target.sim_id)
        degree_tracker = target.degree_tracker
        degree_tracker.show_knowledge_notification(subject, DoubleSimResolver(subject, target))