# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_tracker.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 77181 bytes
import itertools
from sims.global_gender_preference_tuning import GlobalGenderPreferenceTuning
from collections import defaultdict
import operator, random
from protocolbuffers import Commodities_pb2
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from crafting.crafting_tunable import CraftingTuning
from crafting.food_restrictions_utils import FoodRestrictionUtils
from cas.cas_preference_item import ObjectPreferenceItem
from distributor.rollback import ProtocolBufferRollback
from event_testing import test_events
from event_testing.resolver import SingleSimResolver
from interactions import ParticipantTypeSim
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils.tunable import TunableContinuation
from objects import ALL_HIDDEN_REASONS
from objects.mixins import AffordanceCacheMixin, ProvidedAffordanceData
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims.sim_info_types import Gender, Species, SpeciesExtended
from sims.sim_info_utils import apply_super_affordance_commodity_flags, remove_super_affordance_commodity_flags
from sims4.localization import LocalizationHelperTuning, TunableLocalizedStringFactory
from sims4.tuning.tunable import Tunable, TunableMapping, TunableEnumEntry, TunableList, TunableTuple, TunableSet, OptionalTunable, TunableReference
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod, classproperty
from statistics.commodity_messages import send_sim_commodity_list_update_message
from traits.preference_tracker_mixin import PreferenceTrackerMixin
from traits.preference_utils import preferences_gen
from traits.trait_day_night_tracking import DayNightTrackingState
from traits.trait_quirks import add_quirks
from traits.traits import logger, Trait
from traits.trait_type import TraitType
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList
from ui.ui_dialog_picker import ObjectPickerRow
from vfx.vfx_mask import generate_mask_message
import game_services, services, sims.ghost, sims4.telemetry, telemetry_helper
TELEMETRY_GROUP_TRAITS = 'TRAT'
TELEMETRY_HOOK_ADD_TRAIT = 'TADD'
TELEMETRY_HOOK_REMOVE_TRAIT = 'TRMV'
TELEMETRY_FIELD_TRAIT_ID = 'idtr'
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_TRAITS)

class HasTraitTrackerMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    @property
    def trait_tracker(self):
        return self._trait_tracker

    def add_trait(self, *args, **kwargs):
        return (self._trait_tracker._add_trait)(*args, **kwargs)

    def get_traits(self):
        return self._trait_tracker.equipped_traits

    def has_trait(self, *args, **kwargs):
        return (self._trait_tracker.has_trait)(*args, **kwargs)

    def remove_trait(self, *args, **kwargs):
        return (self._trait_tracker._remove_trait)(*args, **kwargs)

    def get_initial_commodities(self):
        initial_commodities = set()
        blacklisted_commodities = set()
        conditional_commodities = self._trait_tracker.conditional_commodities
        for trait in self._trait_tracker:
            initial_commodities.update(trait.initial_commodities)
            blacklisted_commodities.update(trait.initial_commodities_blacklist)
            if conditional_commodities:
                if trait in conditional_commodities:
                    initial_commodities.update(conditional_commodities[trait])

        initial_commodities -= blacklisted_commodities
        return frozenset(initial_commodities)

    def on_all_traits_loaded(self):
        pass

    def _get_trait_ids(self):
        return self._trait_tracker.trait_ids


class TraitTracker(AffordanceCacheMixin, PreferenceTrackerMixin, SimInfoTracker):
    GENDER_TRAITS = TunableMapping(description='\n        A mapping from gender to trait. Any Sim with the specified gender will\n        have the corresponding gender trait.\n        ',
      key_type=TunableEnumEntry(description="\n            The Sim's gender.\n            ",
      tunable_type=Gender,
      default=(Gender.MALE)),
      value_type=Trait.TunableReference(description='\n            The trait associated with the specified gender.\n            '))
    DEFAULT_GENDER_OPTION_TRAITS = TunableMapping(description="\n        A mapping from gender to default gender option traits. After loading the\n        sim's trait tracker, if no gender option traits are found (e.g. loading\n        a save created prior to them being added), the tuned gender option traits\n        for the sim's gender will be added.\n        ",
      key_type=TunableEnumEntry(description="\n            The Sim's gender.\n            ",
      tunable_type=Gender,
      default=(Gender.MALE)),
      value_type=TunableSet(description='\n            The default gender option traits to be added for this gender.\n            ',
      tunable=Trait.TunableReference(pack_safe=True)))
    SPECIES_TRAITS = TunableMapping(description='\n        A mapping from species to trait. Any Sim of the specified species will\n        have the corresponding species trait.\n        ',
      key_type=TunableEnumEntry(description="\n            The Sim's species.\n            ",
      tunable_type=Species,
      default=(Species.HUMAN),
      invalid_enums=(
     Species.INVALID,)),
      value_type=Trait.TunableReference(description='\n            The trait associated with the specified species.\n            ',
      pack_safe=True))
    SPECIES_EXTENDED_TRAITS = TunableMapping(description='\n        A mapping from extended species to trait. Any Sim of the specified \n        extended species will have the corresponding extended species trait.\n        ',
      key_type=TunableEnumEntry(description="\n            The Sim's extended species.\n            ",
      tunable_type=SpeciesExtended,
      default=(SpeciesExtended.SMALLDOG),
      invalid_enums=(
     SpeciesExtended.INVALID,)),
      value_type=Trait.TunableReference(description='\n            The trait associated with the specified extended species.\n            ',
      pack_safe=True))
    TRAIT_INHERITANCE = TunableList(description='\n        Define how specific traits are transferred to offspring. Define keys of\n        sets of traits resulting in the assignment of another trait, weighted\n        against other likely outcomes.\n        ',
      tunable=TunableTuple(description='\n            A set of trait requirements and outcomes. Please note that inverted\n            requirements are not necessary. The game will automatically swap\n            parents A and B to try to fulfill the constraints.\n            \n            e.g. Alien Inheritance\n                Alien inheritance follows a simple set of rules:\n                 Alien+Alien always generates aliens\n                 Alien+None always generates part aliens\n                 Alien+PartAlien generates either aliens or part aliens\n                 PartAlien+PartAlien generates either aliens, part aliens, or regular Sims\n                 PartAlien+None generates either part aliens or regular Sims\n                 \n                Given the specifications involving "None", we need to probably\n                blacklist the two traits to detect a case where only one of the\n                two parents has a meaningful trait:\n                \n                a_whitelist = Alien\n                b_whitelist = Alien\n                outcome = Alien\n                \n                a_whitelist = Alien\n                b_blacklist = Alien,PartAlien\n                outcome = PartAlien\n                \n                etc...\n            ',
      parent_a_whitelist=TunableList(description='\n                Parent A must have ALL these traits in order to generate this\n                outcome.\n                ',
      tunable=(Trait.TunablePackSafeReference()),
      allow_none=True),
      parent_a_blacklist=TunableList(description='\n                Parent A must not have ANY of these traits in order to generate this\n                outcome.\n                ',
      tunable=Trait.TunableReference(pack_safe=True)),
      parent_b_whitelist=TunableList(description='\n                Parent B must have ALL these traits in order to generate this\n                outcome.\n                ',
      tunable=(Trait.TunablePackSafeReference()),
      allow_none=True),
      parent_b_blacklist=TunableList(description='\n                Parent B must not have ANY of these traits in order to generate this\n                outcome.\n                ',
      tunable=Trait.TunableReference(pack_safe=True)),
      outcomes=TunableList(description='\n                A weighted list of potential outcomes given that the\n                requirements have been satisfied.\n                ',
      tunable=TunableTuple(description='\n                    A weighted outcome. The weight is relative to other entries\n                    within this outcome set.\n                    ',
      weight=Tunable(description='\n                        The relative weight of this outcome versus other\n                        outcomes in this same set.\n                        ',
      tunable_type=float,
      default=1),
      trait=Trait.TunableReference(description='\n                        The potential inherited trait.\n                        ',
      allow_none=True,
      pack_safe=True)))))
    KNOWLEDGE_TRAIT_TYPES = TunableSet(description='\n        Sims are allowed to get knowledge about traits of these types.\n        ',
      tunable=TraitType)

    def __init__(self, sim_info):
        super().__init__()
        self._sim_info = sim_info
        self._sim_info.on_base_characteristic_changed.append(self.add_auto_traits)
        self._disabled_trait_types = set()
        self._equipped_traits = set()
        self._unlocked_equip_slot = 0
        self._buff_handles = {}
        self.trait_vfx_mask = 0
        self.trait_exclude_vfx_mask = 0
        self._hiding_relationships = False
        self._day_night_state = None
        self._test_events = None
        self._load_in_progress = False
        self._delayed_active_lod_traits = None
        self._conditional_commodities = {}

    def __iter__(self):
        return self._equipped_traits.__iter__()

    def __len__(self):
        return len(self._equipped_traits)

    def can_add_trait(self, trait):
        if not self._has_valid_lod(trait):
            logger.info('Trying to equip a trait {} for Sim {} without meeting the min lod (sim: {} < trait: {})', trait, self._sim_info, self._sim_info.lod, trait.min_lod_value)
            return False
        if self.has_trait(trait):
            logger.info('Trying to equip an existing trait {} for Sim {}', trait, self._sim_info)
            return False
        if trait.is_personality_trait:
            if self.empty_slot_number == 0:
                logger.info('Reach max equipment slot number {} for Sim {}', self.equip_slot_number, self._sim_info)
                return False
        if trait.is_preference_trait:
            if self.at_preference_capacity():
                logger.info('Reached max preference-traits for Sim {}', self._sim_info)
                return False
        if not trait.is_valid_trait(self._sim_info):
            logger.info("Trying to equip a trait {} that conflicts with Sim {}'s age {} or gender {}", trait, self._sim_info, self._sim_info.age, self._sim_info.gender)
            return False
        if self.is_conflicting(trait):
            logger.info('Trying to equip a conflicting trait {} for Sim {}', trait, self._sim_info)
            return False
        if trait.trait_type == TraitType.LIFESTYLE:
            if not services.lifestyle_service().lifestyles_enabled:
                logger.info('Trying to equip a lifestyle trait {} for Sim {} without lifestyles enabled', trait, self._sim_info)
                return False
            return True

    def add_auto_traits(self):
        for trait in itertools.chain(self.GENDER_TRAITS.values(), self.SPECIES_TRAITS.values(), self.SPECIES_EXTENDED_TRAITS.values()):
            if self.has_trait(trait):
                self._remove_trait(trait)

        auto_traits = (
         self.GENDER_TRAITS.get(self._sim_info.gender), self.SPECIES_TRAITS.get(self._sim_info.species), self.SPECIES_EXTENDED_TRAITS.get(self._sim_info.extended_species))
        for trait in auto_traits:
            if trait is None:
                continue
            else:
                self._add_trait(trait)

    def remove_invalid_traits(self):
        for trait in tuple(self._equipped_traits):
            if not trait.is_valid_trait(self._sim_info):
                self._sim_info.remove_trait(trait)

    def sort_and_send_commodity_list(self):
        if not self._sim_info.is_selectable:
            return
        final_list = []
        commodities = self._sim_info.get_initial_commodities()
        for trait in self._equipped_traits:
            if not trait.ui_commodity_sort_override:
                continue
            else:
                final_list = [override_commodity for override_commodity in trait.ui_commodity_sort_override if override_commodity in commodities]
            break

        if not final_list:
            final_list = sorted(commodities, key=(operator.attrgetter('ui_sort_order')))
        self._send_commodity_list_msg(final_list)

    def _send_commodity_list_msg(self, commodity_list):
        list_msg = Commodities_pb2.CommodityListUpdate()
        list_msg.sim_id = self._sim_info.sim_id
        for commodity in commodity_list:
            if commodity.visible:
                stat = self._sim_info.commodity_tracker.get_statistic(commodity)
                if stat:
                    if stat.is_visible_commodity():
                        with ProtocolBufferRollback(list_msg.commodities) as commodity_msg:
                            stat.populate_commodity_update_msg(commodity_msg, is_rate_change=False)

        send_sim_commodity_list_update_message(self._sim_info, list_msg)

    @property
    def conditional_commodities(self):
        return self._conditional_commodities

    def on_all_households_and_sim_infos_loaded(self):
        self._check_conditional_commodities()

    def _check_conditional_commodities(self):
        previous_initial_commodities = self._sim_info.get_initial_commodities()
        for trait, _ in self._conditional_commodities.items():
            self._update_conditional_commodities_dict(trait)
            self._update_commodities(trait, previous_initial_commodities)

    def _update_conditional_commodities_dict(self, trait, add=True):
        if not trait.conditional_commodities:
            return
        if not add:
            if not self._conditional_commodities:
                return
        commodities_to_remove = []
        for commodity_info in trait.conditional_commodities:
            if not add:
                if trait in self._conditional_commodities:
                    del self._conditional_commodities[trait]
            if add:
                if trait not in self._conditional_commodities:
                    self._conditional_commodities[trait] = []
                if commodity_info.tests.run_tests(resolver=(SingleSimResolver(self._sim_info))):
                    self._conditional_commodities[trait].append(commodity_info.commodity)
                else:
                    if commodity_info.commodity in self._conditional_commodities[trait]:
                        self._conditional_commodities[trait].remove(commodity_info.commodity)
                if self._sim_info.lod >= commodity_info.commodity.min_lod_value:
                    commodities_to_remove.append(commodity_info.commodity)

        if commodities_to_remove:
            self._remove_commodities(commodities_to_remove)

    def _remove_commodities(self, commodities):
        if not commodities:
            return
        should_update_commodity_ui = False
        for commodity in commodities:
            commodity_inst = self._sim_info.commodity_tracker.get_statistic(commodity)
            if commodity_inst is None:
                continue
            else:
                if not should_update_commodity_ui:
                    if commodity_inst.is_visible_commodity():
                        should_update_commodity_ui = True
                commodity_inst.core = False
                self._sim_info.commodity_tracker.remove_statistic(commodity)

        if should_update_commodity_ui:
            self.sort_and_send_commodity_list()

    def _add_commodities(self, commodities):
        if not commodities:
            return
        should_update_commodity_ui = False
        for commodity_to_add in commodities:
            commodity_inst = self._sim_info.commodity_tracker.add_statistic(commodity_to_add)
            if commodity_inst is None:
                continue
            else:
                commodity_inst.core = True
            if not should_update_commodity_ui:
                if commodity_inst.is_visible_commodity():
                    should_update_commodity_ui = True

        if should_update_commodity_ui:
            self.sort_and_send_commodity_list()

    def _update_commodities(self, trait, previous_initial_commodities):
        current_initial_commodities = self._sim_info.get_initial_commodities()
        commodities_to_remove = previous_initial_commodities - current_initial_commodities
        self._remove_commodities(commodities_to_remove)
        commodities_to_add = current_initial_commodities - previous_initial_commodities
        self._add_commodities(commodities_to_add)

    def _add_trait(self, trait, from_load=False):
        if not self.can_add_trait(trait):
            return False
        if trait.trait_type in self._disabled_trait_types:
            return False
        owner_sim_info = self._sim_info
        initial_commodities_modified = trait.initial_commodities or trait.initial_commodities_blacklist
        if initial_commodities_modified:
            previous_initial_commodities = owner_sim_info.get_initial_commodities()
        self._equipped_traits.add(trait)
        if initial_commodities_modified:
            if not from_load:
                self._update_conditional_commodities_dict(trait)
            self._update_commodities(trait, previous_initial_commodities)
        if not trait.buffs_add_on_spawn_only or owner_sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
            try:
                self._add_buffs(trait)
            except Exception as e:
                try:
                    logger.exception('Error adding buffs while adding trait: {0}. {1}.', (trait.__name__), e, owner='asantos')
                finally:
                    e = None
                    del e

            self._add_vfx_mask(trait, send_op=(not from_load))
            self._add_day_night_tracking(trait)
            self.update_trait_effects()
            if trait.is_ghost_trait:
                sims.ghost.Ghost.enable_ghost_routing(owner_sim_info)
            if trait.disable_aging:
                owner_sim_info.update_age_callbacks()
            age_transition = owner_sim_info.get_age_transition_data(owner_sim_info.age)
            if trait in age_transition.trait_age_duration_mutliplier.keys():
                owner_sim_info.update_age_callbacks()
            if trait.is_robot_trait:
                if not from_load:
                    owner_sim_info.set_days_alive_to_zero()
                sim = owner_sim_info.get_sim_instance()
                provided_affordances = []
                for provided_affordance in trait.target_super_affordances:
                    provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
                    provided_affordances.append(provided_affordance_data)

                self.add_to_affordance_caches(trait.super_affordances, provided_affordances)
                self.add_to_actor_mixer_cache(trait.actor_mixers)
                self.add_to_provided_mixer_cache(trait.provided_mixers)
                apply_super_affordance_commodity_flags(sim, trait, trait.super_affordances)
                self._hiding_relationships |= trait.hide_relationships
                if sim is not None:
                    teleport_style_interaction = trait.get_teleport_style_interaction_to_inject()
                    if teleport_style_interaction is not None:
                        sim.add_teleport_style_interaction_to_inject(teleport_style_interaction)
                food_restriction_tracker = owner_sim_info.food_restriction_tracker
                if food_restriction_tracker is not None:
                    for ingredient in trait.restricted_ingredients:
                        food_restriction_tracker.add_food_restriction(ingredient)

                if not from_load:
                    if trait.trait_type in self.KNOWLEDGE_TRAIT_TYPES:
                        if owner_sim_info.household is not None:
                            for household_sim in owner_sim_info.household:
                                if household_sim is owner_sim_info:
                                    continue
                                else:
                                    household_sim.relationship_tracker.add_known_trait(trait, owner_sim_info.sim_id)

                        else:
                            logger.error("Attempting to add a trait to a Sim that doesn't have a household. This shouldn't happen. Sim={}, trait={}", owner_sim_info, trait)
                    owner_sim_info.resend_trait_ids(traits_to_add=[trait.guid64])
                    if trait.disable_aging is not None:
                        owner_sim_info.resend_age_progress_data()
                    if sim is not None:
                        with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_ADD_TRAIT, sim=sim) as hook:
                            hook.write_int(TELEMETRY_FIELD_TRAIT_ID, trait.guid64)
                    if trait.always_send_test_event_on_add or sim is not None:
                        services.get_event_manager().process_event((test_events.TestEvent.TraitAddEvent), sim_info=owner_sim_info)
                    if trait.loot_on_trait_add is not None:
                        resolver = SingleSimResolver(owner_sim_info)
                        for loot_action in trait.loot_on_trait_add:
                            loot_action.apply_to_resolver(resolver)

                    if trait.trait_statistic is not None:
                        trait.trait_statistic.on_trait_added(owner_sim_info, trait)
                    self._register_trait_events(trait)
            return True

    def _remove_trait(self, trait):
        if not self.has_trait(trait):
            return False
        owner_sim_info = self._sim_info
        initial_commodities_modified = trait.initial_commodities or trait.initial_commodities_blacklist
        if initial_commodities_modified:
            previous_initial_commodities = owner_sim_info.get_initial_commodities()
        self._equipped_traits.remove(trait)
        if initial_commodities_modified:
            self._update_conditional_commodities_dict(trait, add=False)
            self._update_commodities(trait, previous_initial_commodities)
        self._remove_buffs(trait)
        self._remove_vfx_mask(trait)
        self._remove_day_night_tracking(trait)
        self._remove_build_buy_purchase_tracking(trait)
        self._remove_trait_knowledge(trait)
        self._remove_sexuality_knowledge(trait)
        self.update_trait_effects()
        self.update_affordance_caches()
        age_transition = owner_sim_info.get_age_transition_data(owner_sim_info.age)
        if trait.disable_aging or trait in age_transition.trait_age_duration_mutliplier.keys():
            owner_sim_info.update_age_callbacks()
        owner_sim_info.resend_trait_ids(traits_to_remove=[trait.guid64])
        if trait.disable_aging is not None:
            owner_sim_info.resend_age_progress_data()
        if not any((t.is_ghost_trait for t in self._equipped_traits)):
            sims.ghost.Ghost.remove_ghost_from_sim(owner_sim_info)
        sim = owner_sim_info.get_sim_instance()
        if sim is not None:
            with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_REMOVE_TRAIT, sim=sim) as hook:
                hook.write_int(TELEMETRY_FIELD_TRAIT_ID, trait.guid64)
            services.get_event_manager().process_event((test_events.TestEvent.TraitRemoveEvent), sim_info=owner_sim_info)
            teleport_style_interaction = trait.get_teleport_style_interaction_to_inject()
            if teleport_style_interaction is not None:
                sim.try_remove_teleport_style_interaction_to_inject(teleport_style_interaction)
        remove_super_affordance_commodity_flags(sim, trait)
        self._hiding_relationships = any((trait.hide_relationships for trait in self))
        if trait.trait_statistic is not None:
            trait.trait_statistic.on_trait_removed(owner_sim_info, trait)
        self._unregister_trait_events(trait)
        food_restriction_tracker = owner_sim_info.food_restriction_tracker
        if food_restriction_tracker is not None:
            for ingredient in trait.restricted_ingredients:
                food_restriction_tracker.remove_food_restriction(ingredient)

        return True

    def disable_traits_of_type(self, trait_type):
        if trait_type in self._disabled_trait_types:
            return
        self._disabled_trait_types.add(trait_type)
        self.remove_traits_of_type(trait_type)

    def enable_traits_of_type(self, trait_type):
        if trait_type not in self._disabled_trait_types:
            return
        self._disabled_trait_types.remove(trait_type)

    def get_traits_of_type(self, trait_type):
        return [t for t in self._equipped_traits if t.trait_type == trait_type]

    def get_object_preferences(self, preference_types):
        return [t for t in self.get_preferences(preference_types) if t.is_object_preference]

    def get_preferences(self, preference_types):
        return [t for t in self._equipped_traits if t.trait_type in preference_types]

    def possible_preferences_gen(self, decorator_only=False):
        for preference in preferences_gen():
            if decorator_only:
                if not preference.decorator_preference:
                    continue
                if self.can_add_trait(preference):
                    yield preference

    def remove_traits_of_type(self, trait_type):
        for trait in list(self._equipped_traits):
            if trait.trait_type == trait_type:
                self._remove_trait(trait)

    def clear_traits(self):
        for trait in list(self._equipped_traits):
            self._remove_trait(trait)

    def has_trait(self, trait):
        return trait in self._equipped_traits

    def has_any_trait(self, traits):
        return bool(self._equipped_traits & set(traits))

    def is_conflicting(self, trait):
        if trait is None:
            return False
        if set(trait.conflicting_traits) & self._equipped_traits:
            return True
        for t in self._equipped_traits:
            if trait in t.conflicting_traits:
                return True

        return False

    @staticmethod
    def _get_inherited_traits_internal(traits_a, traits_b, trait_entry):
        if trait_entry.parent_a_whitelist:
            if not all((t in traits_a for t in trait_entry.parent_a_whitelist)):
                return False
            if any((t in traits_a for t in trait_entry.parent_a_blacklist)):
                return False
            if trait_entry.parent_b_whitelist:
                if not all((t in traits_b for t in trait_entry.parent_b_whitelist)):
                    return False
                if any((t in traits_b for t in trait_entry.parent_b_blacklist)):
                    return False
            return True

    def get_inherited_traits(self, other_sim):
        traits_a = list(self)
        traits_b = list(other_sim.trait_tracker)
        inherited_entries = []
        for trait_entry in TraitTracker.TRAIT_INHERITANCE:
            if not self._get_inherited_traits_internal(traits_a, traits_b, trait_entry):
                if self._get_inherited_traits_internal(traits_b, traits_a, trait_entry):
                    pass
            inherited_entries.append(tuple(((outcome.weight, outcome.trait) for outcome in trait_entry.outcomes)))

        return inherited_entries

    def get_leave_lot_now_interactions(self, must_run=False):
        interactions = set()
        for trait in self:
            if trait.npc_leave_lot_interactions:
                if must_run:
                    interactions.update(trait.npc_leave_lot_interactions.leave_lot_now_must_run_interactions)
                else:
                    interactions.update(trait.npc_leave_lot_interactions.leave_lot_now_interactions)

        return interactions

    @property
    def personality_traits(self):
        return tuple((trait for trait in self if trait.is_personality_trait))

    @property
    def gender_option_traits(self):
        return tuple((trait for trait in self if trait.is_gender_option_trait))

    @property
    def aspiration_traits(self):
        return tuple((trait for trait in self if trait.is_aspiration_trait))

    @property
    def trait_ids(self):
        return [t.guid64 for t in self._equipped_traits]

    @property
    def equipped_traits(self):
        return self._equipped_traits

    def get_default_trait_asm_params(self, actor_name):
        asm_param_dict = {}
        for trait_asm_param in Trait.default_trait_params:
            asm_param_dict[(trait_asm_param, actor_name)] = False

        return asm_param_dict

    @property
    def equip_slot_number(self):
        age = self._sim_info.age
        slot_number = self._unlocked_equip_slot
        slot_number += self._sim_info.get_aging_data().get_personality_trait_count(age)
        return slot_number

    @property
    def empty_slot_number(self):
        equipped_personality_traits = sum((1 for trait in self if trait.is_personality_trait))
        empty_slot_number = self.equip_slot_number - equipped_personality_traits
        return max(empty_slot_number, 0)

    def _add_buffs(self, trait):
        if trait.guid64 in self._buff_handles:
            return
        buff_handles = []
        for buff in trait.buffs:
            buff_handle = self._sim_info.add_buff((buff.buff_type), buff_reason=(buff.buff_reason), remove_on_zone_unload=(trait.buffs_add_on_spawn_only))
            if buff_handle is not None:
                buff_handles.append(buff_handle)

        if buff_handles:
            self._buff_handles[trait.guid64] = buff_handles

    def _remove_buffs(self, trait):
        if trait.guid64 in self._buff_handles:
            for buff_handle in self._buff_handles[trait.guid64]:
                self._sim_info.remove_buff(buff_handle)

            del self._buff_handles[trait.guid64]

    def _add_vfx_mask(self, trait, send_op=False):
        trait_vfx_mask = trait.vfx_mask
        trait_exclude_vfx_mask = trait.exclude_vfx_mask
        if trait_vfx_mask is None:
            if trait_exclude_vfx_mask is None:
                return
        if trait_vfx_mask is not None:
            for mask in trait_vfx_mask:
                self.trait_vfx_mask |= mask

        if trait_exclude_vfx_mask is not None:
            for mask in trait_exclude_vfx_mask:
                self.trait_exclude_vfx_mask |= mask

        if send_op:
            if self._sim_info is services.active_sim_info():
                generate_mask_message(self.trait_vfx_mask, self._sim_info)

    def _remove_vfx_mask(self, trait):
        trait_vfx_mask = trait.vfx_mask
        trait_exclude_vfx_mask = trait.exclude_vfx_mask
        if trait_vfx_mask is None:
            if trait_exclude_vfx_mask is None:
                return
        if trait_vfx_mask is not None:
            for mask in trait_vfx_mask:
                self.trait_vfx_mask ^= mask

        if trait_exclude_vfx_mask is not None:
            for mask in trait_exclude_vfx_mask:
                self.trait_exclude_vfx_mask ^= mask

        if self._sim_info is services.active_sim_info():
            generate_mask_message(self.trait_vfx_mask, self._sim_info)

    def update_trait_effects(self):
        if self._load_in_progress:
            return
        self._update_voice_effect()
        self._update_plumbbob_override()

    def _update_voice_effect(self):
        try:
            voice_effect_request = max((trait.voice_effect for trait in self if trait.voice_effect is not None), key=(operator.attrgetter('priority')))
            self._sim_info.voice_effect = voice_effect_request.voice_effect
        except ValueError:
            self._sim_info.voice_effect = None

    def _update_plumbbob_override(self):
        try:
            plumbbob_override_request = max((trait.plumbbob_override for trait in self if trait.plumbbob_override is not None), key=(operator.attrgetter('priority')))
            self._sim_info.plumbbob_override = (plumbbob_override_request.active_sim_plumbbob,
             plumbbob_override_request.active_sim_club_leader_plumbbob)
        except ValueError:
            self._sim_info.plumbbob_override = None

    def _add_default_gender_option_traits(self):
        gender_option_traits = self.DEFAULT_GENDER_OPTION_TRAITS.get(self._sim_info.gender)
        for gender_option_trait in gender_option_traits:
            if not self.has_trait(gender_option_trait):
                self._add_trait(gender_option_trait)

    def fixup_gender_preference_statistics(self):
        for gender, gender_preference_statistic in self._sim_info.get_gender_preferences_gen():
            attraction_traits = GlobalGenderPreferenceTuning.ROMANTIC_PREFERENCE_TRAITS_MAPPING[gender]
            if self.has_trait(attraction_traits.is_attracted_trait):
                if not gender_preference_statistic.get_value() >= GlobalGenderPreferenceTuning.GENDER_PREFERENCE_THRESHOLD:
                    gender_preference_statistic.set_value(gender_preference_statistic.max_value)
            else:
                if self.has_trait(attraction_traits.not_attracted_trait):
                    if not gender_preference_statistic.get_value() < GlobalGenderPreferenceTuning.GENDER_PREFERENCE_THRESHOLD:
                        gender_preference_statistic.set_value(gender_preference_statistic.min_value)

    def on_sim_startup(self):
        sim = self._sim_info.get_sim_instance()
        for trait in tuple(self):
            if trait in self:
                if trait.buffs_add_on_spawn_only:
                    self._add_buffs(trait)
                else:
                    apply_super_affordance_commodity_flags(sim, trait, trait.super_affordances)
                    teleport_style_interaction = trait.get_teleport_style_interaction_to_inject()
                    if teleport_style_interaction is not None:
                        sim.add_teleport_style_interaction_to_inject(teleport_style_interaction)
            else:
                logger.error('Trait:{} was removed during startup', trait)

        if any((trait.is_ghost_trait for trait in self)):
            sims.ghost.Ghost.enable_ghost_routing(self._sim_info)

    def on_zone_unload(self):
        if self._test_events is not None:
            self._test_events.clear()
            self._test_events = None
        if game_services.service_manager.is_traveling:
            for trait in tuple(self):
                if trait in self:
                    if not trait.buffs_add_on_spawn_only:
                        self._remove_buffs(trait)
                    if not trait.persistable:
                        self._remove_trait(trait)

    def on_zone_load(self):
        if game_services.service_manager.is_traveling:
            for trait in tuple(self):
                if trait in self:
                    if not trait.buffs_add_on_spawn_only:
                        self._add_buffs(trait)

    def on_sim_removed(self):
        for trait in tuple(self):
            if trait.buffs_add_on_spawn_only:
                self._remove_buffs(trait)
            if not trait.persistable:
                self._remove_trait(trait)

    def save(self):
        data = protocols.PersistableTraitTracker()
        trait_ids = [trait.guid64 for trait in self._equipped_traits if trait.persistable]
        if self._delayed_active_lod_traits is not None:
            trait_ids.extend((trait.guid64 for trait in self._delayed_active_lod_traits))
        data.trait_ids.extend(trait_ids)
        return data

    def load(self, data, skip_load):
        trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
        try:
            self._load_in_progress = True
            self._sim_info._update_age_trait(self._sim_info.age)
            premade_sim_needing_fixup = bool(self._sim_info.premade_sim_template_id)
            for trait_instance_id in data.trait_ids:
                trait = trait_manager.get(trait_instance_id)
                if trait is not None:
                    if not self._has_valid_lod(trait):
                        if trait.min_lod_value == SimInfoLODLevel.ACTIVE:
                            if self._delayed_active_lod_traits is None:
                                self._delayed_active_lod_traits = list()
                            else:
                                self._delayed_active_lod_traits.append(trait)
                            continue
                    if skip_load:
                        if not premade_sim_needing_fixup:
                            if not trait.allow_from_gallery:
                                continue
                        self._sim_info.add_trait(trait, from_load=True)

            if not self.personality_traits:
                if not self._sim_info.is_baby:
                    possible_traits = [trait for trait in trait_manager.types.values() if trait.is_personality_trait if self.can_add_trait(trait)]
                    if possible_traits:
                        chosen_trait = random.choice(possible_traits)
                        self._add_trait(chosen_trait, from_load=True)
            self._add_default_gender_option_traits()
            add_quirks(self._sim_info)
            self._sim_info.on_all_traits_loaded()
        finally:
            self._load_in_progress = False

    def _has_any_trait_with_day_night_tracking(self):
        return any((trait for trait in self if trait.day_night_tracking is not None))

    def _add_day_night_tracking(self, trait):
        sim = self._sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            return
        if trait.day_night_tracking is not None:
            if not sim.is_on_location_changed_callback_registered(self._day_night_tracking_callback):
                sim.register_on_location_changed(self._day_night_tracking_callback)
        self.update_day_night_tracking_state(force_update=True)

    def _remove_day_night_tracking(self, trait):
        self._day_night_state = None
        sim = self._sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            return
        if trait.day_night_tracking is None or self._has_any_trait_with_day_night_tracking():
            return
        sim.unregister_on_location_changed(self._day_night_tracking_callback)

    def _day_night_tracking_callback(self, *_, **__):
        self.update_day_night_tracking_state()

    def update_day_night_tracking_state(self, force_update=False, full_reset=False):
        if not self._has_any_trait_with_day_night_tracking():
            return
        sim = self._sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            return
        if full_reset:
            self._clear_all_day_night_buffs()
        time_service = services.time_service()
        is_day = time_service.is_day_time()
        in_sunlight = time_service.is_in_sunlight(sim)
        new_state = self._day_night_state is None
        if new_state:
            self._day_night_state = DayNightTrackingState(is_day, in_sunlight)
        update_day_night = new_state or self._day_night_state.is_day != is_day
        update_sunlight = new_state or self._day_night_state.in_sunlight != in_sunlight
        if not force_update:
            if not update_day_night:
                if not update_sunlight:
                    return
        self._day_night_state.is_day = is_day
        self._day_night_state.in_sunlight = in_sunlight
        for trait in self:
            if not trait.day_night_tracking:
                continue
            else:
                day_night_tracking = trait.day_night_tracking
                if update_day_night or force_update:
                    self._add_remove_day_night_buffs((day_night_tracking.day_buffs), add=is_day)
                    self._add_remove_day_night_buffs((day_night_tracking.night_buffs), add=(not is_day))
            if not update_sunlight:
                if force_update:
                    pass
            self._add_remove_day_night_buffs((day_night_tracking.sunlight_buffs), add=in_sunlight)
            self._add_remove_day_night_buffs((day_night_tracking.shade_buffs), add=(not in_sunlight))

    def update_day_night_buffs_on_buff_removal(self, buff_to_remove):
        if not self._has_any_trait_with_day_night_tracking():
            return
        for trait in self:
            if trait.day_night_tracking:
                if not trait.day_night_tracking.force_refresh_buffs:
                    continue
                else:
                    force_refresh_buffs = trait.day_night_tracking.force_refresh_buffs
                if any((buff.buff_type is buff_to_remove.buff_type for buff in force_refresh_buffs)):
                    self.update_day_night_tracking_state(full_reset=True, force_update=True)
                    return

    def _clear_all_day_night_buffs(self):
        for trait in self:
            if not trait.day_night_tracking:
                continue
            else:
                day_night_tracking = trait.day_night_tracking
                self._add_remove_day_night_buffs((day_night_tracking.day_buffs), add=False)
                self._add_remove_day_night_buffs((day_night_tracking.night_buffs), add=False)
                self._add_remove_day_night_buffs((day_night_tracking.sunlight_buffs), add=False)
                self._add_remove_day_night_buffs((day_night_tracking.shade_buffs), add=False)

    def _add_remove_day_night_buffs(self, buffs, add=True):
        for buff in buffs:
            if add:
                self._sim_info.add_buff((buff.buff_type), buff_reason=(buff.buff_reason))
            else:
                self._sim_info.remove_buff_by_type(buff.buff_type)

    def _has_any_trait_with_build_buy_purchase_tracking(self):
        return any((trait for trait in self if trait.build_buy_purchase_tracking is not None))

    def _add_build_buy_purchase_tracking(self, trait):
        if trait.build_buy_purchase_tracking is not None:
            if not services.get_event_manager().is_registered_for_event(self, test_events.TestEvent.ObjectAdd):
                services.get_event_manager().register(self, (test_events.TestEvent.ObjectAdd,))

    def _remove_build_buy_purchase_tracking(self, trait):
        if trait.build_buy_purchase_tracking is None or self._has_any_trait_with_build_buy_purchase_tracking():
            return
        services.get_event_manager().unregister(self, (test_events.TestEvent.ObjectAdd,))

    def _handle_build_buy_purchase_event(self, trait, resolver):
        if not trait.build_buy_purchase_tracking:
            return
        for loot_action in trait.build_buy_purchase_tracking:
            loot_action.apply_to_resolver(resolver)

    def handle_event(self, sim_info, event_type, resolver):
        if event_type == test_events.TestEvent.ObjectAdd:
            for trait in self:
                self._handle_build_buy_purchase_event(trait, resolver)

    def on_sim_ready_to_simulate(self):
        for trait in self:
            self._add_day_night_tracking(trait)
            self._add_build_buy_purchase_tracking(trait)

    def get_provided_super_affordances(self):
        affordances, target_affordances = set(), list()
        for trait in self._equipped_traits:
            affordances.update(trait.super_affordances)
            for provided_affordance in trait.target_super_affordances:
                provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
                target_affordances.append(provided_affordance_data)

        return (
         affordances, target_affordances)

    def get_actor_and_provided_mixers_list(self):
        actor_mixers = [trait.actor_mixers for trait in self._equipped_traits]
        provided_mixers = [trait.provided_mixers for trait in self._equipped_traits]
        return (
         actor_mixers, provided_mixers)

    def get_sim_info_from_provider(self):
        return self._sim_info

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.MINIMUM

    def on_lod_update(self, old_lod, new_lod):
        if new_lod == old_lod:
            return
        increase_lod = old_lod < new_lod
        for trait in tuple(self._equipped_traits):
            if self._has_valid_lod(trait):
                if increase_lod:
                    initial_commodities = trait.initial_commodities - trait.initial_commodities_blacklist
                    initial_commodities = initial_commodities - frozenset(self._sim_info.get_blacklisted_statistics())
                    for commodity in initial_commodities:
                        commodity_inst = self._sim_info.commodity_tracker.get_statistic(commodity, add=True)
                        if commodity_inst is not None:
                            commodity_inst.core = True

            else:
                if trait.min_lod_value >= SimInfoLODLevel.ACTIVE:
                    if self._delayed_active_lod_traits is None:
                        self._delayed_active_lod_traits = list()
                    self._delayed_active_lod_traits.append(trait)
                self._sim_info.remove_trait(trait)

        if new_lod >= SimInfoLODLevel.ACTIVE:
            if self._delayed_active_lod_traits is not None:
                for trait in self._delayed_active_lod_traits:
                    self._add_trait(trait, from_load=True)

                self._delayed_active_lod_traits = None

    def _has_valid_lod(self, trait):
        if self._sim_info.lod < trait.min_lod_value:
            return False
        return True

    @property
    def hide_relationships(self):
        return self._hiding_relationships

    def _register_trait_events(self, trait):
        if self._sim_info.is_npc:
            return
        if not trait.event_test_based_loots:
            return
        event_manager = services.get_event_manager()
        for index, event_test_data in enumerate(trait.event_test_based_loots):
            test_events = [(test_event, None) for test_event in event_test_data.test.get_test_events_to_register()]
            test_events.extend(event_test_data.test.get_custom_event_registration_keys())
            for test_key in test_events:
                if self._test_events is None or test_key not in self._test_events:
                    event_manager.register_with_custom_key(self, test_key[0], test_key[1])
                else:
                    if self._test_events is None:
                        self._test_events = defaultdict(list)
                    self._test_events[test_key].append((trait, index))

    def register_all_trait_events(self):
        for trait in self._equipped_traits:
            self._register_trait_events(trait)

    def _unregister_trait_events(self, trait):
        if self._test_events is None:
            return
        event_manager = services.get_event_manager()
        for test_key, traits in tuple(self._test_events.items()):
            for trait_data in tuple(traits):
                if trait is not trait_data[0]:
                    continue
                else:
                    traits.remove(trait_data)
                if traits:
                    continue
                else:
                    event_manager.unregister_with_custom_key(self, test_key[0], test_key[1])
                    del self._test_events[test_key]

    def _remove_trait_knowledge(self, trait, update_ui=True):
        if trait.trait_type not in self.KNOWLEDGE_TRAIT_TYPES:
            return
        tracker = self._sim_info.relationship_tracker
        for target in tracker.get_target_sim_infos():
            if target is None:
                logger.error('\n                            SimInfo {} has a relationship with a None target. The target\n                            has probably been pruned and the data is out of sync. Please\n                            provide a save and GSI dump and file a DT for this.\n                            ',
                  (self._sim_info),
                  owner='asantos')
                continue
            else:
                target.relationship_tracker.remove_known_trait(trait, (self._sim_info.id), notify_client=update_ui)

    def _remove_sexuality_knowledge(self, trait, update_ui=True):
        gender_preference_traits = GlobalGenderPreferenceTuning.get_preference_traits()
        is_romance_trait = trait in gender_preference_traits[0]
        is_woohoo_trait = trait in gender_preference_traits[1]
        if not is_romance_trait:
            if not is_woohoo_trait:
                return
        tracker = self._sim_info.relationship_tracker
        for target in tracker.get_target_sim_infos():
            if target is None:
                logger.error('\n                            SimInfo {} has a relationship with a None target. The target\n                            has probably been pruned and the data is out of sync. Please\n                            provide a save and GSI dump and file a bug for this.\n                            ',
                  (self._sim_info),
                  owner='amwu')
                continue
            if is_romance_trait:
                target.relationship_tracker.remove_knows_romantic_preference((self._sim_info.id), notify_client=update_ui)
            if is_woohoo_trait:
                target.relationship_tracker.remove_knows_woohoo_preference((self._sim_info.id), notify_client=update_ui)

    def _test_key(self, key, resolver):
        if self._test_events is None or key not in self._test_events:
            return
        for trait, test_index in self._test_events[key]:
            if resolver(trait.event_test_based_loots[test_index].test):
                trait.event_test_based_loots[test_index].loot.apply_to_resolver(resolver)

    def handle_event(self, sim_info, event, resolver):
        if sim_info is not self._sim_info:
            return
        self._test_key((event, None), resolver)
        for custom_key in resolver.custom_keys:
            self._test_key((event, custom_key), resolver)


class TraitPickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'is_add':Tunable(description='\n            If this interaction is trying to add a trait to the sim or to\n            remove a trait from the sim.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.PICKERTUNING), 
     'already_equipped_tooltip':OptionalTunable(description='\n            If tuned, we show this tooltip if row is disabled when trait is \n            already equipped.\n            ',
       tunable=TunableLocalizedStringFactory(description='\n                Tooltip to display.\n                '),
       tuning_group=GroupNames.PICKERTUNING), 
     'filter_by_types':OptionalTunable(description='\n            If specified, limits the traits that appear in this picker to specific types of traits.\n            If disabled, all traits are available.\n            ',
       tunable=TunableWhiteBlackList(tunable=TunableEnumEntry(default=(TraitType.PERSONALITY),
       tunable_type=TraitType)),
       tuning_group=GroupNames.PICKERTUNING), 
     'continuation':OptionalTunable(description='\n            If enabled then a continuation will be pushed after the\n            picker selection has been made.\n            ',
       tunable=TunableContinuation(description='\n                If specified, a continuation to push when a picker\n                selection has been made.\n                '),
       tuning_group=GroupNames.PICKERTUNING), 
     'picker_target':TunableEnumEntry(tunable_type=ParticipantTypeSim,
       default=ParticipantTypeSim.TargetSim,
       tuning_group=GroupNames.PICKERTUNING)}

    def _run_interaction_gen(self, timeline):
        trait_target = self.get_participant(self.picker_target)
        self._show_picker_dialog(trait_target, target_sim=trait_target)
        return True
        if False:
            yield None

    @classmethod
    def _match_trait_type(cls, trait):
        if cls.filter_by_types is None:
            return True
        return cls.filter_by_types.test_item(trait.trait_type)

    @classmethod
    def _trait_selection_gen(cls, target):
        trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
        trait_tracker = target.sim_info.trait_tracker
        if cls.is_add:
            for trait in trait_manager.types.values():
                if not cls._match_trait_type(trait):
                    continue
                if trait.sim_info_fixup_actions:
                    continue
                if trait_tracker.can_add_trait(trait):
                    yield trait

        else:
            for trait in trait_tracker.equipped_traits:
                if not cls._match_trait_type(trait):
                    continue
                else:
                    yield trait

    @flexmethod
    def picker_rows_gen--- This code section failed: ---

 L.1627         0  LOAD_FAST                'inst'
                2  LOAD_CONST               None
                4  COMPARE_OP               is-not
                6  POP_JUMP_IF_FALSE    12  'to 12'
                8  LOAD_FAST                'inst'
               10  JUMP_FORWARD         14  'to 14'
             12_0  COME_FROM             6  '6'
               12  LOAD_DEREF               'cls'
             14_0  COME_FROM            10  '10'
               14  STORE_FAST               'inst_or_cls'

 L.1628        16  LOAD_FAST                'inst_or_cls'
               18  LOAD_ATTR                get_participant
               20  LOAD_DEREF               'cls'
               22  LOAD_ATTR                picker_target
               24  BUILD_TUPLE_1         1 
               26  LOAD_DEREF               'target'
               28  LOAD_FAST                'context'
               30  LOAD_CONST               ('target', 'context')
               32  BUILD_CONST_KEY_MAP_2     2 
               34  LOAD_FAST                'kwargs'
               36  BUILD_MAP_UNPACK_WITH_CALL_2     2 
               38  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
               40  STORE_FAST               'trait_target'

 L.1629        42  LOAD_FAST                'trait_target'
               44  LOAD_ATTR                sim_info
               46  LOAD_ATTR                trait_tracker
               48  STORE_FAST               'trait_tracker'

 L.1630        50  SETUP_LOOP          182  'to 182'
               52  LOAD_DEREF               'cls'
               54  LOAD_METHOD              _trait_selection_gen
               56  LOAD_FAST                'trait_target'
               58  CALL_METHOD_1         1  '1 positional argument'
               60  GET_ITER         
             62_0  COME_FROM           178  '178'
             62_1  COME_FROM            84  '84'
             62_2  COME_FROM            70  '70'
               62  FOR_ITER            180  'to 180'
               64  STORE_FAST               'trait'

 L.1631        66  LOAD_FAST                'trait'
               68  LOAD_ATTR                display_name
               70  POP_JUMP_IF_FALSE_LOOP    62  'to 62'

 L.1632        72  LOAD_FAST                'trait'
               74  LOAD_METHOD              display_name
               76  LOAD_FAST                'trait_target'
               78  CALL_METHOD_1         1  '1 positional argument'
               80  STORE_FAST               'display_name'
               82  JUMP_FORWARD         86  'to 86'

 L.1637        84  CONTINUE             62  'to 62'
             86_0  COME_FROM            82  '82'

 L.1641        86  LOAD_CONST               True
               88  STORE_FAST               'is_enabled'

 L.1642        90  LOAD_CONST               None
               92  STORE_FAST               'row_tooltip'

 L.1643        94  LOAD_DEREF               'cls'
               96  LOAD_ATTR                is_add
               98  POP_JUMP_IF_FALSE   144  'to 144'

 L.1644       100  LOAD_FAST                'trait_tracker'
              102  LOAD_METHOD              has_trait
              104  LOAD_FAST                'trait'
              106  CALL_METHOD_1         1  '1 positional argument'
              108  UNARY_NOT        
              110  STORE_FAST               'is_enabled'

 L.1645       112  LOAD_FAST                'is_enabled'
              114  POP_JUMP_IF_TRUE    126  'to 126'
              116  LOAD_DEREF               'cls'
              118  LOAD_ATTR                already_equipped_tooltip
              120  LOAD_CONST               None
              122  COMPARE_OP               is
              124  POP_JUMP_IF_FALSE   130  'to 130'
            126_0  COME_FROM           114  '114'
              126  LOAD_CONST               None
              128  JUMP_FORWARD        142  'to 142'
            130_0  COME_FROM           124  '124'
              130  LOAD_CLOSURE             'cls'
              132  LOAD_CLOSURE             'target'
              134  BUILD_TUPLE_2         2 
              136  LOAD_LAMBDA              '<code_object <lambda>>'
              138  LOAD_STR                 'TraitPickerSuperInteraction.picker_rows_gen.<locals>.<lambda>'
              140  MAKE_FUNCTION_CLOSURE        'closure'
            142_0  COME_FROM           128  '128'
              142  STORE_FAST               'row_tooltip'
            144_0  COME_FROM            98  '98'

 L.1647       144  LOAD_GLOBAL              ObjectPickerRow
              146  LOAD_FAST                'display_name'
              148  LOAD_FAST                'trait'
              150  LOAD_METHOD              trait_description
              152  LOAD_FAST                'trait_target'
              154  CALL_METHOD_1         1  '1 positional argument'

 L.1648       156  LOAD_FAST                'trait'
              158  LOAD_ATTR                icon
              160  LOAD_FAST                'trait'
              162  LOAD_FAST                'is_enabled'
              164  LOAD_FAST                'row_tooltip'
              166  LOAD_CONST               ('name', 'row_description', 'icon', 'tag', 'is_enable', 'row_tooltip')
              168  CALL_FUNCTION_KW_6     6  '6 total positional and keyword args'
              170  STORE_FAST               'row'

 L.1649       172  LOAD_FAST                'row'
              174  YIELD_VALUE      
              176  POP_TOP          
              178  JUMP_LOOP            62  'to 62'
              180  POP_BLOCK        
            182_0  COME_FROM_LOOP       50  '50'

Parse error at or near `CONTINUE' instruction at offset 84

    def on_choice_selected(self, choice_tag, **kwargs):
        trait = choice_tag
        if trait is not None:
            if self.is_add:
                trait_target = self.get_participant(self.picker_target)
                trait_target.sim_info.add_trait(trait)
            else:
                trait_target = self.get_participant(self.picker_target)
                trait_target.sim_info.remove_trait(trait)
            if self.continuation is not None:
                self.push_tunable_continuation(self.continuation)


class AgentPickerSuperInteraction(TraitPickerSuperInteraction):

    @classmethod
    def _trait_selection_gen(cls, target):
        career_tracker = target.sim_info.career_tracker
        for career in career_tracker:
            for trait in career.current_level_tuning.agents_available:
                yield trait