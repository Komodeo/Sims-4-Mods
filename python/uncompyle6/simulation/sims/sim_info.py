# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_info.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 216308 bytes
import singletons
from _sims4_collections import frozendict
import contextlib
from collections import OrderedDict
import itertools, math, random, time
from whims import whims_tracker
from satisfaction.satisfaction_tracker import SatisfactionTracker
from protocolbuffers import SimObjectAttributes_pb2 as protocols, FileSerialization_pb2 as serialization, GameplaySaveData_pb2 as gameplay_serialization, SimObjectAttributes_pb2
from protocolbuffers import SimsCustomOptions_pb2 as custom_options
from protocolbuffers.DistributorOps_pb2 import SetWhimBucks
from protocolbuffers.ResourceKey_pb2 import ResourceKeyList
from away_actions.away_action_tracker import AwayActionTracker
from away_actions.away_actions import AwayAction
from away_actions.away_actions_interactions import ApplyDefaultAwayActionInteraction
from bucks.sim_info_bucks_tracker import SimInfoBucksTracker
from caches import cached
from careers.career_tracker import CareerTracker
from clock import interval_in_sim_days
from crafting.food_restrictions import FoodRestrictionTracker
from date_and_time import DateAndTime, TimeSpan
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from event_testing import test_events
from event_testing.resolver import SingleSimResolver, DoubleSimResolver
from fame.fame_tuning import FameTunables
from fame.lifestyle_brand_tracker import LifestyleBrandTracker
from familiars.familiar_tracker import FamiliarTracker
from indexed_manager import ObjectLoadData
from interactions.aop import AffordanceObjectPair
from interactions.utils.adventure import AdventureTracker
from interactions.utils.death import DeathTracker
from interactions.utils.tunable import SetGoodbyeNotificationElement
from lunar_cycle.lunar_effect_tracker import LunarEffectTracker
from notebook.notebook_tracker import NotebookTrackerSimInfo
from objects import ALL_HIDDEN_REASONS, ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED, HiddenReasonFlag
from objects.components import ComponentContainer, forward_to_components
from objects.components.consumable_component import ConsumableComponent
from objects.components.inventory_enums import InventoryType
from objects.components.inventory_item import InventoryItemComponent
from objects.components.statistic_component import HasStatisticComponent
from objects.object_enums import ItemLocation
from objects.system import create_object
from organizations.organization_tracker import OrganizationTracker
from relationships.global_relationship_tuning import RelationshipGlobalTuning
from relationships.relationship_tracker import RelationshipTracker
from relics.relic_tracker import RelicTracker
from reputation.reputation_tuning import ReputationTunables
from routing import SurfaceType
from services.persistence_service import PersistenceTuning
from services.relgraph_service import RelgraphService
from sickness.sickness_tracker import SicknessTracker
from sims.aging.aging_mixin import AgingMixin
from sims.baby.baby_utils import run_baby_spawn_behavior
from sims.body_type_level.body_type_level_tracker import BodyTypeLevelTracker
from sims.favorites.favorites_tracker import FavoritesTracker
from sims.fixup.fixup_tracker import FixupTracker
from sims.fixup.sim_info_fixup_action import SimInfoFixupActionTiming
from sims.genealogy_relgraph_enums import SimRelBitFlags
from sims.genealogy_tracker import GenealogyTracker, FamilyRelationshipIndex, genealogy_caching
from sims.ghost import Ghost
from sims.global_gender_preference_tuning import GlobalGenderPreferenceTuning, SexualityStatus, GenderPreferenceType
from sims.occult.sim_info_with_occult_tracker import SimInfoWithOccultTracker
from sims.outfits.outfit_enums import OutfitCategory, SpecialOutfitIndex
from sims.outfits.outfit_tuning import OutfitTuning
from sims.pregnancy.pregnancy_client_mixin import PregnancyClientMixin
from sims.pregnancy.pregnancy_tracker import PregnancyTracker
from sims.royalty_tracker import RoyaltyTracker
from sims.sim_info_favorites_mixin import SimInfoFavoriteMixin
from sims.sim_info_gameplay_options import SimInfoGameplayOptions
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_name_data import SimInfoNameData
from sims.sim_info_tests import SimInfoTest, TraitTest
from sims.sim_info_types import SimInfoSpawnerTags, SimSerializationOption, Gender, Species, SpeciesExtended
from sims.sim_spawner_enums import SimInfoCreationSource
from sims.suntan.suntan_ops import SetTanLevel
from sims.suntan.suntan_tracker import SuntanTracker
from sims.template_affordance_provider.template_affordance_tracker import TemplateAffordanceTracker
from sims.university.degree_tracker import DegreeTracker
from sims.unlock_tracker import UnlockTracker
from sims4.common import is_available_pack, UnavailablePackError
from sims4.math import clamp, Threshold
from sims4.profiler_utils import create_custom_named_profiler_function
from sims4.protocol_buffer_utils import persist_fields_for_custom_option
from sims4.resources import Types
from sims4.tuning.tunable import TunableResourceKey, Tunable, TunableList, TunableReference, TunableTuple, TunableMapping, TunableEnumEntry, TunableVariant, OptionalTunable
from sims4.utils import constproperty
from singletons import DEFAULT, EMPTY_SET
from social_media.social_media_tuning import SocialMediaTunables
from statistics.commodity import Commodity
from statistics.life_skill_statistic import LifeSkillStatistic
from statistics.statistic_enums import CommodityTrackerSimulationLevel, StatisticLockAction
from story_progression.story_progression_enums import CullingReasons
from story_progression.story_progression_tracker import SimStoryProgressionTracker
from traits.trait_tracker import TraitTracker
from world.spawn_point import SpawnPointOption, SpawnPoint
from world.spawn_point_enums import SpawnPointRequestReason
import aspirations.aspirations, build_buy, caches, clans, clubs, date_and_time, distributor.fields, distributor.ops, enum, event_testing, game_services, gsi_handlers, indexed_manager, objects.components, operator, placement, routing, services
import sims.sim_info_types as types
import sims4.log, sims4.resources, statistics.skill, tag, telemetry_helper, whims
logger = sims4.log.Logger('SimInfo', default_owner='manus')
lod_logger = sims4.log.Logger('LoD', default_owner='miking')
TELEMETRY_CHANGE_ASPI = 'ASPI'
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_CHANGE_ASPI)
TELEMETRY_SIMULATION_ERROR = 'SERR'
simulation_error_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_SIMULATION_ERROR)
with sims4.reload.protected(globals()):
    SAVE_ACTIVE_HOUSEHOLD_COMMAND = False
    INJECT_LOD_NAME_IN_CALLSTACK = False

class TunableSimTestVariant(TunableVariant):

    def __init__(self, description='A single tunable test.', **kwargs):
        (super().__init__)(sim_info=SimInfoTest.TunableFactory(locked_args={'tooltip': None}), 
         trait=TraitTest.TunableFactory(locked_args={'tooltip': None}), 
         default='sim_info', 
         description=description, **kwargs)


class TunableSimTestList(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None):
        if description is None:
            description = 'A list of tests.  All tests must succeed to pass the TestSet.'
        super().__init__(description=description, tunable=(TunableSimTestVariant()))


class SimInfo(SimInfoWithOccultTracker, SimInfoCreationSource.SimInfoCreationSourceMixin, AgingMixin, PregnancyClientMixin, SimInfoFavoriteMixin, ComponentContainer, HasStatisticComponent):

    class BodyBlendTypes(enum.Int, export=False):
        BODYBLENDTYPE_HEAVY = 0
        BODYBLENDTYPE_FIT = 1
        BODYBLENDTYPE_LEAN = 2
        BODYBLENDTYPE_BONY = 3
        BODYBLENDTYPE_PREGNANT = 4
        BODYBLENDTYPE_HIPS_WIDE = 5
        BODYBLENDTYPE_HIPS_NARROW = 6
        BODYBLENDTYPE_WAIST_WIDE = 7
        BODYBLENDTYPE_WAIST_NARROW = 8

    DEFAULT_THUMBNAIL = TunableResourceKey(None, resource_types=(sims4.resources.CompoundTypes.IMAGE), description='Icon to be displayed for the Buff.')
    DEFAULT_GAMEPLAY_OPTIONS = SimInfoGameplayOptions.ALLOW_FAME | SimInfoGameplayOptions.ALLOW_REPUTATION
    SIM_DEFINITIONS = TunableMapping(description='\n        A Map from Species to base definition object.\n        ',
      key_type=TunableEnumEntry(description='\n            Species this definition is for.\n            ',
      tunable_type=SpeciesExtended,
      default=(SpeciesExtended.HUMAN),
      invalid_enums=(
     SpeciesExtended.INVALID,)),
      value_type=TunableReference(description='\n            The definition used to instantiate Sims.\n            ',
      manager=(services.definition_manager()),
      class_restrictions='Sim',
      pack_safe=True))

    @staticmethod
    def get_sim_definition(species):
        if species in SimInfo.SIM_DEFINITIONS:
            return SimInfo.SIM_DEFINITIONS[species]
        logger.error("Requesting the definition for a species({}) type that doesn't have one in SIM_DEFINITIONS", species)
        return SimInfo.SIM_DEFINITIONS[Species.HUMAN]

    PHYSIQUE_CHANGE_AFFORDANCES = TunableTuple(description="\n        Affordances to run when a Sim's physique changes.\n        ",
      FAT_CHANGE_POSITIVE_AFFORDANCE=TunableReference(description="\n            Affordance to run when a Sim's fat changes to positive effect.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      FAT_CHANGE_MAX_POSITIVE_AFFORDANCE=TunableReference(description="\n            Affordance to run when a Sim's fat changes to maximum positive effect.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      FAT_CHANGE_NEGATIVE_AFFORDANCE=TunableReference(description="\n            Affordance to run when a Sim's fat changes to negative effect.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      FAT_CHANGE_MAX_NEGATIVE_AFFORDANCE=TunableReference(description="\n            Affordance to run when a Sim's fat changes to maximum negative effect.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      FAT_CHANGE_NEUTRAL_AFFORDANCE=TunableReference(description="\n            Affordance to run when a Sim's fat changes to neutral effect.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      FIT_CHANGE_POSITIVE_AFFORDANCE=TunableReference(description="\n            Affordance to run when a Sim's fitness changes to positive effect.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      FIT_CHANGE_NEGATIVE_AFFORDANCE=TunableReference(description="\n            Affordance to run when a Sim's fitness changes to negative effect.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      FIT_CHANGE_NEUTRAL_AFFORDANCE=TunableReference(description="\n            Affordance to run when a Sim's fitness changes to neutral effect.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))))
    MAXIMUM_SAFE_FITNESS_VALUE = Tunable(description="\n        This is the value over which a Sim's fitness will always decay.  When a\n        Sim's fitness is set initially inside of CAS, it will not decay below\n        that value unless it is higher than this tunable. Sims with an initial\n        fitness value higher than this tunable will see their fitness commodity\n        decay towards this point.\n        \n        EXAMPLE: MAXIMUM_SAFE_FITNESS_VALUE is set to 90, and a Sim is created\n        in CAS with a fitness value of 100.  Their fitness commodity will decay\n        towards 90.  Another Sim is created with a fitness value of 80.  Their\n        fitness commodity will decay towards 80.\n        ",
      tunable_type=int,
      default=90)
    STATIC_COMMODITIES_WHILE_INSTANCED = TunableList(description='\n        A list of static commodities that are added to every sim info when they are\n        instanced and removed when they become uninstanced. \n        ',
      tunable=TunableReference(description='\n            A static commodity that is added to each sim info on its creation.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATIC_COMMODITY))))
    INITIAL_STATISTICS = TunableList(description='\n        A list of statistics that will be added to each sim info on its\n        creation.\n        ',
      tunable=TunableTuple(statistic=TunableReference(description='\n                A statistic that will be added to each sim info upon creation.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      pack_safe=True),
      tests=OptionalTunable(description='\n                If enabled, the statistic will only be added to each sim info\n                if the tests pass.\n                ',
      tunable=(TunableSimTestList()))))
    AWAY_ACTIONS = TunableMapping(description='\n        A mapping between affordances and lists of away actions.  The\n        affordances are used to generate AoPs with each of the away actions.\n        ',
      key_type=TunableReference(description='\n            The interaction that will be used to create AoPs from the away list\n            of away actions that it is mapped to.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      value_type=TunableList(description='\n            A list of away actions that are available for the player to select\n            from and apply to the sim.\n            ',
      tunable=AwayAction.TunableReference(pack_safe=True)))
    DEFAULT_AWAY_ACTION = TunableMapping(description='\n        Map of commodities to away action.  When the default away action is\n        asked for we look at the ad data of each commodity and select the away\n        action linked to the commodity that is advertising the highest.\n        ',
      key_type=Commodity.TunableReference(description='\n            The commodity that we will look at the advertising value for.\n            ',
      pack_safe=True),
      value_type=AwayAction.TunableReference(description='\n            The away action that will applied if the key is the highest\n            advertising commodity of the ones listed.\n            ',
      pack_safe=True))
    APPLY_DEFAULT_AWAY_ACTION_INTERACTION = ApplyDefaultAwayActionInteraction.TunableReference(description='\n        Interaction that will be used to apply the default away action onto the\n        sim info.\n        ')
    SIM_SKEWER_AFFORDANCES = TunableList(description="\n        A list of affordances that will test and be available when the player\n        clicks on a Sim's interaction button in the Sim skewer.\n        ",
      tunable=TunableReference(description="\n            An affordance shown when the player clicks on a sim's\n            interaction button in the Sim skewer.\n            ",
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))))
    SIM_INFO_TRACKERS = OrderedDict((
     (
      '_relationship_tracker', RelationshipTracker),
     (
      '_trait_tracker', TraitTracker),
     (
      '_pregnancy_tracker', PregnancyTracker),
     (
      '_death_tracker', DeathTracker),
     (
      '_adventure_tracker', AdventureTracker),
     (
      '_royalty_tracker', RoyaltyTracker),
     (
      '_career_tracker', CareerTracker),
     (
      '_genealogy_tracker', GenealogyTracker),
     (
      '_story_progression_tracker', SimStoryProgressionTracker),
     (
      '_unlock_tracker', UnlockTracker),
     (
      '_away_action_tracker', AwayActionTracker),
     (
      '_notebook_tracker', NotebookTrackerSimInfo),
     (
      '_whim_tracker', whims.whims_tracker.WhimsTracker),
     (
      '_aspiration_tracker', aspirations.aspirations.AspirationTracker),
     (
      '_template_affordance_tracker', TemplateAffordanceTracker),
     (
      '_relic_tracker', RelicTracker),
     (
      '_lifestyle_brand_tracker', LifestyleBrandTracker),
     (
      '_suntan_tracker', SuntanTracker),
     (
      '_sickness_tracker', SicknessTracker),
     (
      '_familiar_tracker', FamiliarTracker),
     (
      '_favorites_tracker', FavoritesTracker),
     (
      '_degree_tracker', DegreeTracker),
     (
      '_organization_tracker', OrganizationTracker),
     (
      '_fixup_tracker', FixupTracker),
     (
      '_food_restriction_tracker', FoodRestrictionTracker),
     (
      '_lunar_effect_tracker', LunarEffectTracker),
     (
      '_satisfaction_tracker', SatisfactionTracker),
     (
      '_body_type_level_tracker', BodyTypeLevelTracker)))

    def __init__(self, *args, zone_id=0, zone_name='', world_id=0, account=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._revision = 0
        self._lod = SimInfoLODLevel.BACKGROUND
        self.add_component(objects.components.buff_component.BuffComponent(self))
        self.commodity_tracker.simulation_level = CommodityTrackerSimulationLevel.LOW_LEVEL_SIMULATION
        for tracker_attr in SimInfo.SIM_INFO_TRACKERS:
            setattr(self, tracker_attr, None)

        self._prior_household_zone_id = None
        self._prespawn_zone_id = zone_id
        self._zone_id = zone_id
        self.zone_name = zone_name
        self._world_id = world_id
        self._account = account
        self._sim_ref = None
        self._serialization_option = SimSerializationOption.UNDECLARED
        self._household_id = None
        self._autonomy_scoring_preferences = {}
        self._autonomy_use_preferences = {}
        self._primary_aspiration = None
        self._current_skill_guid = 0
        self._fat = 0
        self._fit = 0
        self._generation = 0
        self._travel_group_id = 0
        self._primary_aspiration_telemetry_suppressed = False
        self.thumbnail = self.DEFAULT_THUMBNAIL
        self._current_whims = []
        self._sim_creation_path = None
        self._time_sim_was_saved = None
        self._additional_bonus_days = 0
        self.startup_sim_location = None
        self._si_state = None
        self._has_loaded_si_state = False
        self._cached_inventory_value = 0
        self.spawn_point_id = None
        self.spawner_tags = []
        self.spawn_point_option = SpawnPointOption.SPAWN_ANY_POINT_WITH_CONSTRAINT_TAGS
        self.game_time_bring_home = None
        self._initial_fitness_value = None
        self._build_buy_unlocks = set()
        self._singed = False
        self._grubby = False
        self._scratched = False
        self._dyed = False
        self._plumbbob_override = None
        self._goodbye_notification = None
        self._transform_on_load = None
        self._level_on_load = 0
        self._surface_id_on_load = 1
        self._sim_headline = None
        self.premade_sim_template_id = 0
        self._inventory_data = None
        self._bucks_tracker = None
        self._linked_sims = None
        self._fix_relationships = False
        self.do_first_sim_info_load_fixups = False
        self._blacklisted_statistics_cache = None
        self._gameplay_options = self.DEFAULT_GAMEPLAY_OPTIONS
        self._squad_members = set()
        self.roommate_zone_id = 0
        self._vehicle_id = None

    def __repr__(self):
        return "<sim '{0}' {1:#x}>".format(self.full_name, self.sim_id)

    def __str__(self):
        return self.full_name

    def get_delete_op(self):
        pass

    @constproperty
    def is_sim():
        return True

    @property
    def sim_info(self):
        return self

    @distributor.fields.Field(op=(distributor.ops.SetIsNpc))
    def is_npc(self):
        return services.active_household_id() != self.household_id

    resend_is_npc = is_npc.get_resend()

    @property
    def is_player_sim(self):
        household = self.household
        if household is not None:
            return household.is_player_household
        return False

    @property
    def is_played_sim(self):
        household = self.household
        if household is not None:
            return household.is_played_household
        return False

    @property
    def is_selectable(self):
        client = services.client_manager().get_client_by_household_id(self._household_id)
        if client is None:
            return False
        return self in client.selectable_sims

    @property
    def is_selected(self):
        sim = self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is not None:
            return sim.is_selected
        return False

    @property
    def is_premade_sim(self):
        return self.creation_source.is_creation_source(SimInfoCreationSource.PRE_MADE)

    @property
    def lod(self):
        return self._lod

    def request_lod(self, new_lod):
        if self._lod == new_lod:
            return True
        else:
            if not self.can_change_lod(self._lod):
                return False
            return self.can_set_to_lod(new_lod) or False
        old_lod = self._lod
        self._lod = new_lod
        if self.household is not None:
            self.household.on_sim_lod_update(self, old_lod, new_lod)
        for tracker_attr, tracker_type in SimInfo.SIM_INFO_TRACKERS.items():
            if not any((is_available_pack(pack) for pack in tracker_type.required_packs)):
                continue
            is_valid = tracker_type.is_valid_for_lod(new_lod)
            tracker = getattr(self, tracker_attr, None)
            if tracker is None:
                if is_valid:
                    tracker = tracker_type(self)
                    setattr(self, tracker_attr, tracker)
            if tracker is not None:
                tracker.on_lod_update(old_lod, new_lod)
                is_valid or setattr(self, tracker_attr, None)

        if self.has_component(objects.components.types.STATISTIC_COMPONENT):
            self.statistic_component.on_lod_update(old_lod, new_lod)
        if self.Buffs is not None:
            self.Buffs.on_lod_update(old_lod, new_lod)
        if new_lod == SimInfoLODLevel.MINIMUM:
            self._build_buy_unlocks.clear()
            if services.hidden_sim_service().is_hidden(self.id):
                services.hidden_sim_service().unhide_sim(self.id)
            clubs.on_sim_killed_or_culled(self)
            clans.on_sim_killed_or_culled(self)
            self.refresh_age_settings()
            self.clear_outfits_to_minimum()
            self._primary_aspiration = None
            if self.has_component(objects.components.types.STATISTIC_COMPONENT):
                self.statistic_component.on_remove()
                self.remove_component(objects.components.types.STATISTIC_COMPONENT)
            self.Buffs.clean_up()
            self.remove_component(objects.components.types.BUFF_COMPONENT)
            self._zone_id = 0
        return True

    def can_set_to_lod(self, lod):
        if lod == SimInfoLODLevel.MINIMUM:
            if self.get_culling_immunity_reasons():
                return False
        return True

    def can_change_lod(self, lod):
        if lod == SimInfoLODLevel.MINIMUM:
            return False
        return True

    @property
    def can_instantiate_sim(self):
        if self.lod == SimInfoLODLevel.MINIMUM:
            return False
        return True

    def get_name_data(self):
        return SimInfoNameData(self.gender, self.first_name, self.last_name, self.full_name_key)

    def get_additional_create_ops(self):
        if self.Buffs is not None:
            return self.Buffs.get_additional_create_ops()
        return EMPTY_SET

    def get_resolver(self):
        return SingleSimResolver(self)

    def on_loading_screen_animation_finished(self):
        if self._career_tracker is not None:
            self._career_tracker.on_loading_screen_animation_finished()

    def on_situation_request(self, situation):
        if self._career_tracker is None:
            logger.error('on_situation_request: sim_info {} has no career_tracker.', self, owner='nabaker')
            return
        self._career_tracker.on_situation_request(situation)

    def update_fitness_state(self):
        sim = self._sim_ref()
        if not sim.needs_fitness_update:
            return
        sim.needs_fitness_update = False
        self._set_fit_fat()

    @property
    def household(self):
        return services.household_manager().get(self._household_id)

    @property
    def family_funds(self):
        return self.household.funds

    @property
    def travel_group(self):
        return services.travel_group_manager().get(self._travel_group_id)

    def on_add(self):
        if self.has_component(objects.components.types.STATISTIC_COMPONENT):
            self.commodity_tracker.add_watcher(self._publish_commodity_update)
            self.statistic_tracker.add_watcher(self._publish_statistic_update)

    @forward_to_components
    def on_remove(self):
        if self.lod > SimInfoLODLevel.MINIMUM:
            with services.relationship_service().suppress_client_updates_context_manager():
                self.Buffs.clean_up()
            if self._whim_tracker is not None:
                self._whim_tracker.clean_up()
            self._current_whims.clear()
            if self._away_action_tracker is not None:
                self._away_action_tracker.clean_up()
            self._career_tracker.clean_up()
            if self._aspiration_tracker is not None:
                self._aspiration_tracker.clean_up()
            if self._favorites_tracker is not None:
                self._favorites_tracker.clean_up()
        if self.household is not None:
            if self.household.client is not None:
                self.household.client.set_next_sim_or_none(only_if_this_active_sim_info=self)
                self.household.client.selectable_sims.remove_selectable_sim_info(self)
            self.household.remove_sim_info(self)

    def get_is_enabled_in_skewer(self, consider_active_sim=True):
        if self.is_baby:
            return False
            if self.is_pet:
                if not services.get_selectable_sims().can_select_pets:
                    return False
            if self.household is None:
                return False
            if self.lod == SimInfoLODLevel.MINIMUM:
                return False
            daycare_service = services.daycare_service()
            if daycare_service is None:
                return False
        else:
            if consider_active_sim:
                active_sim_info = services.active_sim_info()
                if active_sim_info is not None:
                    if self.travel_group_id != active_sim_info.travel_group_id:
                        return False
            if self in daycare_service.get_sim_infos_for_nanny(self.household):
                return False
            if services.hidden_sim_service().is_hidden(self.id):
                return False
            tutorial_service = services.get_tutorial_service()
            if tutorial_service is not None and tutorial_service.is_sim_unselectable(self):
                return False
        return True

    def try_add_object_to_inventory_without_component(self, obj):
        if not obj.can_go_in_inventory_type(InventoryType.SIM):
            return (
             False, obj)
        obj.item_location = ItemLocation.SIM_INVENTORY
        obj.save_object(self.inventory_data.objects, ItemLocation.SIM_INVENTORY, self.id)
        obj.destroy(cause="Added to uninstantiated sim's inventory")
        return (True, None)

    def inventory_value(self):
        sim = self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is not None:
            self._cached_inventory_value = sim.inventory_component.inventory_value
        return self._cached_inventory_value

    def _generate_default_away_action_aop(self, context, **kwargs):
        return AffordanceObjectPair(SimInfo.APPLY_DEFAULT_AWAY_ACTION_INTERACTION,
 None,
 SimInfo.APPLY_DEFAULT_AWAY_ACTION_INTERACTION,
 None, away_action_sim_info=self, **kwargs)

    def _generate_away_action_affordances(self, context, **kwargs):
        for affordance, away_action_list in SimInfo.AWAY_ACTIONS.items():
            for away_action in away_action_list:
                yield AffordanceObjectPair(affordance,
 None,
 affordance,
 None, away_action=away_action, 
                 away_action_sim_info=self, **kwargs)

    def sim_skewer_affordance_gen(self, context, **kwargs):
        career = self._career_tracker.get_currently_at_work_career()
        if career is not None:
            if not career.is_at_active_event:
                yield from (career.sim_skewer_rabbit_hole_affordances_gen)(context, **kwargs)
                return
        rabbit_hole_service = services.get_rabbit_hole_service()
        if rabbit_hole_service.is_in_rabbit_hole(self.id):
            yield from (rabbit_hole_service.sim_skewer_rabbit_hole_affordances_gen)(self, context, **kwargs)
            return
        sim = self.get_sim_instance()
        for affordance in self.SIM_SKEWER_AFFORDANCES:
            if not affordance.simless:
                if sim is None:
                    continue
            for aop in (affordance.potential_interactions)(sim, context, sim_info=self, **kwargs):
                yield aop

        if not self.household.missing_pet_tracker.is_pet_missing(self):
            yield (self._generate_default_away_action_aop)(context, **kwargs)
            yield from (self._generate_away_action_affordances)(context, **kwargs)

    def bucks_trackers_gen(self):
        if self.household is not None:
            yield self.household.bucks_tracker
        club_service = services.get_club_service()
        if club_service is not None:
            for club in club_service.get_clubs_for_sim_info(self):
                yield club.bucks_tracker

        yield self.get_bucks_tracker(add_if_none=False)

    @property
    def sim_creation_path(self):
        return self._sim_creation_path

    def send_age_progress_bar_update(self):
        self.resend_age_progress_data()
        days_until_ready_to_age = interval_in_sim_days(max(0, self.days_until_ready_to_age()))
        current_time = services.time_service().sim_now
        ready_to_age_time = current_time + days_until_ready_to_age
        self.update_time_alive()
        op = distributor.ops.SetSimAgeProgressTooltipData(int(current_time.absolute_days()), int(ready_to_age_time.absolute_days()), int(self._time_alive.in_days()))
        Distributor.instance().add_op(self, op)

    @contextlib.contextmanager
    def primary_aspiration_telemetry_suppressed(self):
        if self._primary_aspiration_telemetry_suppressed:
            yield
        else:
            self._primary_aspiration_telemetry_suppressed = True
            try:
                yield
            finally:
                self._primary_aspiration_telemetry_suppressed = False

    @distributor.fields.Field(op=(distributor.ops.SetPrimaryAspiration))
    def primary_aspiration(self):
        return self._primary_aspiration

    resend_primary_aspiration = primary_aspiration.get_resend()

    @primary_aspiration.setter
    def primary_aspiration(self, value):
        self._primary_aspiration = value
        if self.aspiration_tracker is not None:
            self.aspiration_tracker.initialize_aspiration()
        services.get_event_manager().process_event((test_events.TestEvent.AspirationChanged), sim_info=self,
          new_aspiration=value)
        if not self._primary_aspiration_telemetry_suppressed:
            with telemetry_helper.begin_hook(writer, TELEMETRY_CHANGE_ASPI, sim=self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)) as (hook):
                hook.write_guid('aspi', value.guid64 if value is not None else 0)

    def start_aspiration_tracker_on_instantiation(self, force_ui_update=False):
        if self._aspiration_tracker is None:
            logger.error("Trying to start aspiration tracker when it hasn't been loaded for Sim {}", self, owner='tingyul')
            return
        if force_ui_update:
            self._aspiration_tracker.force_send_data_update()
        self._aspiration_tracker.initialize_aspiration(from_load=True)
        self._aspiration_tracker.activate_timed_aspirations_from_load()
        self._aspiration_tracker.set_update_alarm()
        self._career_tracker.activate_career_aspirations()
        self._organization_tracker.activate_organization_tasks()

    @distributor.fields.Field(op=(distributor.ops.SetCurrentWhims))
    def current_whims(self):
        return self._current_whims

    resend_current_whims = current_whims.get_resend()

    @current_whims.setter
    def current_whims(self, value):
        self._current_whims = value

    def send_satisfaction_points_update(self, reason):
        self._satisfaction_tracker.send_satisfaction_points_update(reason)

    def apply_satisfaction_points_delta(self, amount, reason, source=None):
        self._satisfaction_tracker.apply_satisfaction_points_delta(amount, reason, source)

    def get_satisfaction_points(self):
        return self._satisfaction_tracker.get_satisfaction_points()

    @property
    def goodbye_notification(self):
        return self._goodbye_notification

    def try_to_set_goodbye_notification(self, value):
        if self._goodbye_notification != SetGoodbyeNotificationElement.NEVER_USE_NOTIFICATION_NO_MATTER_WHAT:
            self._goodbye_notification = value

    def clear_goodbye_notification(self):
        self._goodbye_notification = None

    @property
    def clothing_preference_gender(self):
        if self.has_trait(GlobalGenderPreferenceTuning.MALE_CLOTHING_PREFERENCE_TRAIT):
            return Gender.MALE
        if self.has_trait(GlobalGenderPreferenceTuning.FEMALE_CLOTHING_PREFERENCE_TRAIT):
            return Gender.FEMALE
        return self.gender

    @distributor.fields.Field(op=(distributor.ops.OverridePlumbbob))
    def plumbbob_override(self):
        return self._plumbbob_override

    @plumbbob_override.setter
    def plumbbob_override(self, value):
        self._plumbbob_override = value

    @distributor.fields.Field(op=(distributor.ops.SetDeathType))
    def death_type(self):
        return self._death_tracker.death_type

    resend_death_type = death_type.get_resend()

    @property
    def is_ghost(self):
        return self._death_tracker.is_ghost

    @property
    def death_tracker(self):
        return self._death_tracker

    @property
    def pregnancy_tracker(self):
        return self._pregnancy_tracker

    @property
    def adventure_tracker(self):
        return self._adventure_tracker

    @property
    def royalty_tracker(self):
        return self._royalty_tracker

    @property
    def away_action_tracker(self):
        return self._away_action_tracker

    @property
    def food_restriction_tracker(self):
        return self._food_restriction_tracker

    @property
    def template_affordance_tracker(self):
        return self._template_affordance_tracker

    @property
    def notebook_tracker(self):
        return self._notebook_tracker

    @property
    def sickness_tracker(self):
        return self._sickness_tracker

    @property
    def current_sickness(self):
        if self._sickness_tracker is None:
            return
        return self._sickness_tracker.current_sickness

    def has_sickness_tracking(self):
        return self.current_sickness is not None

    def is_sick(self):
        current_sickness = self.current_sickness
        return current_sickness is not None and current_sickness.considered_sick

    def has_sickness(self, sickness):
        return self.current_sickness is sickness

    def sickness_record_last_progress(self, progress):
        self._sickness_tracker.record_last_progress(progress)

    def discover_symptom(self, symptom):
        self._sickness_tracker.discover_symptom(symptom)

    def track_examination(self, affordance):
        self._sickness_tracker.track_examination(affordance)

    def track_treatment(self, affordance):
        self._sickness_tracker.track_treatment(affordance)

    def rule_out_treatment(self, affordance):
        self._sickness_tracker.rule_out_treatment(affordance)

    def was_symptom_discovered(self, symptom):
        return symptom in self._sickness_tracker.discovered_symptoms

    def was_exam_performed(self, affordance):
        return affordance in self._sickness_tracker.exams_performed

    def was_treatment_performed(self, affordance):
        return affordance in self._sickness_tracker.treatments_performed

    def was_treatment_ruled_out(self, affordance):
        return affordance in self._sickness_tracker.ruled_out_treatments

    @distributor.fields.Field(op=(distributor.ops.SetAwayAction))
    def current_away_action(self):
        if self._away_action_tracker is None:
            return
        return self._away_action_tracker.current_away_action

    resend_current_away_action = current_away_action.get_resend()

    def add_statistic(self, stat_type, value):
        tracker = self.get_tracker(stat_type)
        tracker.set_value(stat_type, value, add=True)

    def remove_statistic(self, stat_type):
        tracker = self.get_tracker(stat_type)
        if tracker is not None:
            tracker.remove_statistic(stat_type)

    @property
    def si_state(self):
        return self._si_state

    @property
    def has_loaded_si_state(self):
        return self._has_loaded_si_state

    @property
    def is_pregnant(self):
        if self._pregnancy_tracker is None:
            return False
        return self._pregnancy_tracker.is_pregnant

    @property
    def current_skill_guid(self):
        return self._current_skill_guid

    @current_skill_guid.setter
    def current_skill_guid(self, value):
        if self._current_skill_guid != value:
            self._current_skill_guid = value

    @property
    def prior_household_home_zone_id(self):
        return self._prior_household_zone_id

    @property
    def prespawn_zone_id(self):
        return self._prespawn_zone_id

    @property
    def zone_id(self):
        return self._zone_id

    def set_zone_on_spawn(self):
        logger.assert_raise((not self.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS)), 'Attempting to set instanced sim into current zone.',
          owner='jjacobson')
        current_zone = services.current_zone()
        current_zone_id = current_zone.id
        if self.is_npc:
            if not ((self._serialization_option == SimSerializationOption.UNDECLARED or self._serialization_option) == SimSerializationOption.LOT and self._zone_id != current_zone_id):
                if not self._serialization_option == SimSerializationOption.OPEN_STREETS or self.world_id != current_zone.open_street_id:
                    self.set_current_outfit((OutfitCategory.EVERYDAY, 0))
        if self._zone_id != current_zone_id:
            self._prespawn_zone_id = self._zone_id
            self._zone_id = current_zone_id
            self.world_id = current_zone.open_street_id
            self._si_state = gameplay_serialization.SuperInteractionSaveState()

    def inject_into_inactive_zone(self, new_zone_id, start_away_actions=True, skip_instanced_check=False, skip_daycare=False):
        if services.current_zone_id() == new_zone_id:
            logger.error('Attempting to put sim:{} into the active zone:{}', self, services.current_zone())
            return
            if self._zone_id == new_zone_id:
                return
            if not skip_instanced_check:
                if self.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                    logger.error('Trying to inject {} into zone when sim_info is still instanced.', self)
        else:
            self._zone_id = new_zone_id
            self.world_id = services.get_persistence_service().get_world_id_from_zone(new_zone_id)
            self.spawner_tags = []
            self.spawn_point_option = SpawnPointOption.SPAWN_ANY_POINT_WITH_CONSTRAINT_TAGS
            self.startup_sim_location = None
            self._si_state = gameplay_serialization.SuperInteractionSaveState()
            self._serialization_option = SimSerializationOption.UNDECLARED
            if self._away_action_tracker is not None:
                if start_away_actions:
                    self._away_action_tracker.refresh(on_travel_away=True)
            skip_daycare or services.daycare_service().refresh_household_daycare_nanny_status(self, try_enable_if_selectable_toddler=True)

    @property
    def world_id(self):
        return self._world_id

    @world_id.setter
    def world_id(self, value):
        if self._world_id != value:
            self._world_id = value

    @property
    def serialization_option(self):
        return self._serialization_option

    @property
    def fat(self):
        return self._fat

    @fat.setter
    def fat(self, value):
        self._fat = value

    @property
    def fit(self):
        return self._fit

    @fit.setter
    def fit(self, value):
        self._fit = value

    @distributor.fields.Field(op=(distributor.ops.SetSinged), default=False)
    def singed(self):
        return self._singed

    @singed.setter
    def singed(self, value):
        self._singed = value

    @distributor.fields.Field(op=(distributor.ops.SetGrubby), default=False)
    def grubby(self):
        return self._grubby

    @grubby.setter
    def grubby(self, value):
        self._grubby = value

    @distributor.fields.Field(op=(distributor.ops.SetScratched), default=False)
    def scratched(self):
        return self._scratched

    @scratched.setter
    def scratched(self, value):
        self._scratched = value

    @distributor.fields.Field(op=(distributor.ops.SetDyed), default=False)
    def dyed(self):
        return self._dyed

    @dyed.setter
    def dyed(self, value):
        self._dyed = value

    @property
    def on_fire(self):
        sim_instance = self.get_sim_instance()
        if not sim_instance:
            return False
        return services.get_fire_service().sim_is_on_fire(sim_instance)

    @property
    def thumbnail(self):
        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, value):
        if value is not None:
            self._thumbnail = value
        else:
            self._thumbnail = sims4.resources.Key(0, 0, 0)

    @property
    def autonomy_scoring_preferences(self):
        return self._autonomy_scoring_preferences

    @property
    def autonomy_use_preferences(self):
        return self._autonomy_use_preferences

    @distributor.fields.Field(op=(distributor.ops.SetCareers))
    def career_tracker(self):
        return self._career_tracker

    @property
    def careers(self):
        if self._career_tracker is not None:
            return self._career_tracker.careers
        return frozendict()

    @property
    def has_custom_career(self):
        if self._career_tracker is not None:
            return self._career_tracker.has_custom_career
        return False

    @property
    def time_sim_was_saved(self):
        return self._time_sim_was_saved

    @time_sim_was_saved.setter
    def time_sim_was_saved(self, value):
        self._time_sim_was_saved = value

    def get_days_since_instantiation(self, *, uninstatiated_time):
        if self.time_sim_was_saved is None:
            return uninstatiated_time
        time_since_instantiation = services.time_service().sim_now - self.time_sim_was_saved
        time_since_instantiation = time_since_instantiation.in_days()
        return time_since_instantiation

    def apply_career_changes(self, missed_time_percent=0):
        for statistic in tuple(self.commodity_tracker):
            if isinstance(statistic, LifeSkillStatistic):
                if statistic.missing_career_decay_rate == 0.0:
                    continue
                reduced_value = statistic.get_value() - missed_time_percent * statistic.missing_career_decay_rate
                statistic.set_value(reduced_value)

    def get_school_data(self):
        sim_definition = self.get_sim_definition(self.extended_species)
        return sim_definition._cls._school

    @property
    def relationship_tracker(self):
        return self._relationship_tracker

    @distributor.fields.Field(op=(distributor.ops.SetSimHeadline))
    def sim_headline(self):
        return self._sim_headline

    @sim_headline.setter
    def sim_headline(self, value):
        self._sim_headline = value

    @distributor.fields.Field(op=(distributor.ops.SetLinkedSims))
    def linked_sims(self):
        if self._linked_sims is None:
            return tuple()
        return tuple(self._linked_sims)

    resend_linked_sims = linked_sims.get_resend()

    def add_linked_sim(self, linked_sim_id):
        if self.id == linked_sim_id:
            return
        if self._linked_sims is None:
            self._linked_sims = set()
        self._linked_sims.add(linked_sim_id)
        self.resend_linked_sims()

    def remove_linked_sim(self, linked_sim_id):
        if self._linked_sims is None:
            return
        if linked_sim_id in self._linked_sims:
            self._linked_sims.remove(linked_sim_id)
            self.resend_linked_sims()

    @distributor.fields.Field(op=(distributor.ops.SetAccountId))
    def account_id(self):
        if self._account is not None:
            return self._account.id

    @property
    def account(self):
        return self._account

    @property
    def client(self):
        if self.account is not None:
            return self.account.get_client(self.zone_id)

    @property
    def Buffs(self):
        return self.get_component(objects.components.types.BUFF_COMPONENT)

    @property
    def aspiration_tracker(self):
        return self._aspiration_tracker

    @property
    def whim_tracker(self):
        return self._whim_tracker

    @property
    def satisfaction_tracker(self):
        return self._satisfaction_tracker

    @property
    def unlock_tracker(self):
        return self._unlock_tracker

    @property
    def relic_tracker(self):
        return self._relic_tracker

    @property
    def lifestyle_brand_tracker(self):
        return self._lifestyle_brand_tracker

    @property
    def familiar_tracker(self):
        return self._familiar_tracker

    @property
    def favorites_tracker(self):
        return self._favorites_tracker

    @property
    def suntan_tracker(self):
        return self._suntan_tracker

    @property
    def degree_tracker(self):
        return self._degree_tracker

    @property
    def organization_tracker(self):
        return self._organization_tracker

    @property
    def fixup_tracker(self):
        return self._fixup_tracker

    @property
    def lunar_effect_tracker(self):
        return self._lunar_effect_tracker

    @property
    def body_type_level_tracker(self):
        return self._body_type_level_tracker

    @distributor.fields.Field(op=SetTanLevel)
    def suntan_data(self):
        return self.suntan_tracker

    resend_suntan_data = suntan_data.get_resend()

    def force_resend_suntan_data(self):
        if self.suntan_tracker:
            self.suntan_tracker.set_tan_level(force_update=True)

    @property
    def revision(self):
        return self._revision

    @property
    def inventory_data(self):
        return self._inventory_data

    @inventory_data.setter
    def inventory_data(self, new_data):
        self._inventory_data = new_data

    @property
    def build_buy_unlocks(self):
        return self._build_buy_unlocks

    def add_build_buy_unlock(self, unlock):
        self._build_buy_unlocks.add(unlock)

    @property
    def is_simulating(self):
        sim_inst = self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED)
        if sim_inst is not None:
            return sim_inst.is_simulating
        if self.is_baby:
            if self.is_selectable:
                return True
        return False

    def get_statistic(self, stat, add=True):
        tracker = self.get_tracker(stat)
        return tracker.get_statistic(stat, add=add)

    @caches.cached
    def all_skills(self):
        if self.commodity_tracker is None:
            return tuple()
        return tuple((stat for stat in self.commodity_tracker if isinstance(stat, statistics.skill.Skill)))

    def get_sim_instance(self, *, allow_hidden_flags=0):
        if self._sim_ref:
            sim = self._sim_ref()
            if sim is not None:
                if not sim.is_hidden(allow_hidden_flags=allow_hidden_flags):
                    return sim

    def is_instanced(self, *, allow_hidden_flags=0):
        sim = self.get_sim_instance(allow_hidden_flags=allow_hidden_flags)
        return sim is not None

    def add_topic(self, *args, **kwargs):
        if not self._sim_ref or self._sim_ref() is None:
            return
        return (self._sim_ref().add_topic)(*args, **kwargs)

    def remove_topic(self, *args, **kwargs):
        if not self._sim_ref or self._sim_ref() is None:
            return
        return (self._sim_ref().remove_topic)(*args, **kwargs)

    def set_sub_action_lockout(self, *args, **kwargs):
        if not self._sim_ref or self._sim_ref() is None:
            return
        return (self._sim_ref().set_sub_action_lockout)(*args, **kwargs)

    def add_statistic_component(self):
        logger.error('Sim Info {}: called add_statistic_component(). This is not supported.', self)

    def can_add_component(self, component_definition):
        if self.lod == SimInfoLODLevel.MINIMUM:
            return False
        return True

    def create_sim_instance(self, position, sim_spawner_tags=None, saved_spawner_tags=None, spawn_action=None, sim_location=None, additional_fgl_search_flags=None, from_load=False, use_fgl=True, spawn_point_override=None, pre_add_fn=None, spawn_at_lot=True, use_random_sim_spawner_tag=True):
        if self.household is None:
            logger.callstack('Creating a Sim instance with a None household. This will cause problems.\n   Sim: {}\n   Household id: {}\n   Creation Source: {}', self,
              (self.household_id), (self.creation_source), level=(sims4.log.LEVEL_ERROR),
              owner='tingyul')
        else:
            self.can_instantiate_sim or logger.error('Failed attempt to instantiate a MINIMUM LOD sim_info: {}', self)
            return False
        sim_info = self

        def init(obj):
            trans = None
            orient = None
            start_routing_surface = None
            total_spawner_tags = []
            try:
                zone = services.current_zone()
                starting_position = position
                if sim_location is not None:
                    logger.info('Sim {} spawning with sim_location {}', sim_info, sim_location)
                    starting_position = sim_location.transform.translation
                    starting_orientation = sim_location.transform.orientation
                    start_routing_surface = sim_location.routing_surface
                    if start_routing_surface.type == routing.SurfaceType.SURFACETYPE_WORLD and start_routing_surface.primary_id != sim_info.zone_id:
                        if sim_info.world_id != zone.open_street_id:
                            logger.warn("Sim {} spawning in zone {} but the sim's startup sim location had zone saved as {}. Setting sim location routing surface to use new zone.", sim_info, sim_info.zone_id, start_routing_surface.primary_id)
                        start_routing_surface = routing.SurfaceIdentifier(sim_info.zone_id, start_routing_surface.secondary_id, routing.SurfaceType.SURFACETYPE_WORLD)
                else:
                    logger.info('Sim {} spawning with no sim_location'.format(sim_info))
                    starting_orientation = None
                    start_routing_surface = None
                if not use_fgl:
                    trans = starting_position
                    orient = starting_orientation
                else:
                    if starting_position is not None:
                        logger.info('Sim {} spawning with starting_position {}', sim_info, starting_position)
                        fgl_search_flags = placement.FGLSearchFlagsDefault | placement.FGLSearchFlag.USE_SIM_FOOTPRINT | placement.FGLSearchFlag.STAY_IN_CURRENT_BLOCK
                        if additional_fgl_search_flags is not None:
                            fgl_search_flags = fgl_search_flags | additional_fgl_search_flags
                        additional_avoid_sim_radius = routing.get_default_agent_radius() if from_load else routing.get_sim_extra_clearance_distance()
                        starting_location = placement.create_starting_location(position=starting_position, orientation=starting_orientation,
                          routing_surface=start_routing_surface)
                        fgl_context = placement.create_fgl_context_for_sim(starting_location, self, search_flags=fgl_search_flags,
                          additional_avoid_sim_radius=additional_avoid_sim_radius)
                        trans, orient = placement.find_good_location(fgl_context)
                        logger.info('Sim {} spawning FGL returned {}, {}', sim_info, trans, orient)
                    if trans is None:
                        zone = services.current_zone()
                        default_tags = SimInfoSpawnerTags.SIM_SPAWNER_TAGS
                        lot_id = None
                        total_spawner_tags = sim_spawner_tags or list(default_tags)
                        if spawn_at_lot:
                            lot_id = zone.lot.lot_id
                        else:
                            total_spawner_tags = sim_spawner_tags
                        if spawn_at_lot and not SpawnPoint.ARRIVAL_SPAWN_POINT_TAG in total_spawner_tags:
                            if SpawnPoint.VISITOR_ARRIVAL_SPAWN_POINT_TAG in total_spawner_tags:
                                lot_id = zone.lot.lot_id
                            logger.info('Sim {} looking for spawn point relative to lot_id {} tags {}', sim_info, lot_id, total_spawner_tags)
                            if spawn_point_override is None:
                                spawn_point = zone.get_spawn_point(lot_id=lot_id, sim_spawner_tags=total_spawner_tags, spawning_sim_info=self, spawn_point_request_reason=(SpawnPointRequestReason.SPAWN),
                                  use_random_sim_spawner_tag=use_random_sim_spawner_tag)
                            else:
                                spawn_point = spawn_point_override
                            if spawn_point is not None:
                                trans, orient = spawn_point.next_spawn_spot()
                                start_routing_surface = spawn_point.routing_surface
                                sim_info.spawn_point_id = spawn_point.spawn_point_id
                                logger.info('Sim {} spawning from spawn point {} transform {}', sim_info, spawn_point.spawn_point_id, trans)
                            else:
                                trans, orient = self._find_place_on_lot_for_sim()
                                logger.info('Sim {} spawn point determined using FGL at {} {}', sim_info, trans, orient)
            except:
                logger.exception('Error in create_sim_instance/find_good_location:')

            if trans is None:
                logger.error('find_good_location Failed, Setting Sim Position to Default')
                translation = DEFAULT if position is None else position
            else:
                translation = trans
            orientation = DEFAULT if orient is None else orient
            routing_surface = DEFAULT if start_routing_surface is None else start_routing_surface
            obj.move_to(translation=translation, orientation=orientation,
              routing_surface=routing_surface)
            obj.sim_info = sim_info
            obj.opacity = 0
            if not (from_load and sim_info.spawner_tags):
                sim_info.spawner_tags = saved_spawner_tags or total_spawner_tags
            if pre_add_fn is not None:
                pre_add_fn(obj)

        run_baby_spawn_behavior(self)
        sim_info.handle_regional_outfits()
        self.handle_career_outfits()
        sim_inst = create_object((self.get_sim_definition(self.extended_species)), (self.sim_id), init=init)
        if sim_info.is_ghost:
            sim_inst.routing_context.ghost_route = True
        sim_inst.on_start_up.append((lambda _: sim_inst.fade_in()) if spawn_action is None else spawn_action)
        sim_info.deploy_vehicle_from_travel(sim_inst)
        self._sim_ref = sim_inst.ref()
        services.daycare_service().on_sim_spawn(self)
        travel_group = self.travel_group
        if travel_group:
            travel_group.give_instanced_sim_loot(self)
        return True

    def _find_place_on_lot_for_sim(self):
        zone = services.current_zone()
        center_pos = sims4.math.Vector3.ZERO()
        if zone.lot is not None:
            center_pos = zone.lot.center
        position = sims4.math.Vector3(center_pos.x, services.terrain_service.terrain_object().get_height_at(center_pos.x, center_pos.z), center_pos.z)
        starting_location = placement.create_starting_location(position=position)
        fgl_context = placement.create_fgl_context_for_sim(starting_location, self, additional_avoid_sim_radius=(routing.get_sim_extra_clearance_distance()))
        return placement.find_good_location(fgl_context)

    def deploy_vehicle_from_travel(self, sim):
        if self._vehicle_id is None:
            return
        else:
            inventory_manager = services.inventory_manager()
            vehicle = inventory_manager.get(self._vehicle_id)
            if vehicle is not None and sim.inventory_component.try_remove_object_by_id(vehicle.id):
                routing_surface = sim.routing_surface
                starting_location = placement.create_starting_location(position=(sim.position), orientation=(sim.orientation),
                  routing_surface=routing_surface)
                fgl_context = placement.create_fgl_context_for_object(starting_location, vehicle)
                trans, orient = placement.find_good_location(fgl_context)
                if trans is not None:
                    if orient is not None:
                        vehicle.location = sims4.math.Location(sims4.math.Transform(trans, orient), routing_surface)
                        return vehicle
                logger.warn('Failed to place vehicle {} from travel', vehicle, owner='rmccord')
                sim.inventory.player_try_add_object(vehicle)
        self._vehicle_id = None

    def _get_fit_fat(self):
        physique = [x for x in self.physique.split(',')]
        max_fat = ConsumableComponent.FAT_COMMODITY.max_value_tuning
        max_fit = ConsumableComponent.FIT_COMMODITY.max_value_tuning
        min_fat = ConsumableComponent.FAT_COMMODITY.min_value_tuning
        min_fit = ConsumableComponent.FIT_COMMODITY.min_value_tuning
        heavy = float(physique[SimInfo.BodyBlendTypes.BODYBLENDTYPE_HEAVY])
        lean = float(physique[SimInfo.BodyBlendTypes.BODYBLENDTYPE_LEAN])
        fit = float(physique[SimInfo.BodyBlendTypes.BODYBLENDTYPE_FIT])
        bony = float(physique[SimInfo.BodyBlendTypes.BODYBLENDTYPE_BONY])
        self.fat = (1 + heavy - lean) * max_fat + min_fat
        self.fit = (1 + fit - bony) * max_fit + min_fit

    def _set_fit_fat(self):
        sim = self.get_sim_instance()
        if sim is not None:
            self.fat = sim.commodity_tracker.get_value(ConsumableComponent.FAT_COMMODITY)
            self.fit = sim.commodity_tracker.get_value(ConsumableComponent.FIT_COMMODITY)
        physique = [x for x in self.physique.split(',')]
        max_fat = ConsumableComponent.FAT_COMMODITY.max_value_tuning
        max_fit = ConsumableComponent.FIT_COMMODITY.max_value_tuning
        min_fat = ConsumableComponent.FAT_COMMODITY.min_value_tuning
        min_fit = ConsumableComponent.FIT_COMMODITY.min_value_tuning
        fat_range = max_fat - min_fat
        fit_range = max_fit - min_fit
        fat_base = max_fat - fat_range / 2
        fit_base = max_fit - fit_range / 2
        heavy = 0.0 if self.fat <= fat_base else (self.fat - fat_base) / (max_fat - fat_base)
        lean = 0.0 if self.fat >= fat_base else (fat_base - self.fat) / (fat_base - min_fat)
        fit = 0.0 if self.fit <= fit_base else (self.fit - fit_base) / (max_fit - fit_base)
        bony = 0.0 if self.fit >= fit_base else (fit_base - self.fit) / (fit_base - min_fit)
        physique_range = 1000
        physique[SimInfo.BodyBlendTypes.BODYBLENDTYPE_HEAVY] = str(math.trunc(heavy * physique_range) / physique_range)
        physique[SimInfo.BodyBlendTypes.BODYBLENDTYPE_LEAN] = str(math.trunc(lean * physique_range) / physique_range)
        physique[SimInfo.BodyBlendTypes.BODYBLENDTYPE_FIT] = str(math.trunc(fit * physique_range) / physique_range)
        physique[SimInfo.BodyBlendTypes.BODYBLENDTYPE_BONY] = str(math.trunc(bony * physique_range) / physique_range)
        physique = ','.join([x for x in physique])
        self.physique = physique

    def _create_additional_statistics(self):
        sim_resolver = self.get_resolver()
        for init_stat in self.INITIAL_STATISTICS:
            if init_stat.tests is None or init_stat.tests.run_tests(sim_resolver):
                tracker = self.get_tracker(init_stat.statistic)
                tracker.add_statistic(init_stat.statistic)

    def _setup_fitness_commodities(self):
        self.commodity_tracker.set_value(ConsumableComponent.FAT_COMMODITY, self.fat)
        self.commodity_tracker.set_value(ConsumableComponent.FIT_COMMODITY, self.fit)
        fitness_commodity = self.commodity_tracker.get_statistic(ConsumableComponent.FIT_COMMODITY)
        if self._initial_fitness_value is None:
            self._initial_fitness_value = self.fit
        elif self._initial_fitness_value > self.MAXIMUM_SAFE_FITNESS_VALUE:
            fitness_commodity.convergence_value = self.MAXIMUM_SAFE_FITNESS_VALUE
        else:
            fitness_commodity.convergence_value = self._initial_fitness_value
        fatness_commodity = self.commodity_tracker.get_statistic(ConsumableComponent.FAT_COMMODITY)
        fatness_commodity.core = True
        fitness_commodity.core = True

    def _fixup_gender_preference_traits(self, gender_preference_statistic, is_attracted=False):
        stat_gender = None
        for gender, statistic in GlobalGenderPreferenceTuning.GENDER_PREFERENCE.items():
            if statistic == gender_preference_statistic.stat_type:
                stat_gender = gender
                break

        attraction_traits_map = GlobalGenderPreferenceTuning.ROMANTIC_PREFERENCE_TRAITS_MAPPING
        if is_attracted:
            trait_to_remove = attraction_traits_map[stat_gender].not_attracted_trait
            trait_to_add = attraction_traits_map[stat_gender].is_attracted_trait
        else:
            trait_to_remove = attraction_traits_map[stat_gender].is_attracted_trait
            trait_to_add = attraction_traits_map[stat_gender].not_attracted_trait
        self.remove_trait(trait_to_remove)
        self.add_trait(trait_to_add)

    def _add_gender_preference_traits(self, stat):
        self._fixup_gender_preference_traits(stat, is_attracted=True)

    def _remove_gender_preference_traits(self, stat):
        self._fixup_gender_preference_traits(stat, is_attracted=False)

    def _add_gender_preference_listeners(self):
        has_preference_threshold = Threshold(GlobalGenderPreferenceTuning.GENDER_PREFERENCE_THRESHOLD, operator.ge)
        no_preference_threshold = Threshold(GlobalGenderPreferenceTuning.GENDER_PREFERENCE_THRESHOLD, operator.lt)
        for _, stat_type in GlobalGenderPreferenceTuning.GENDER_PREFERENCE.items():
            self.statistic_tracker.create_and_add_listener(stat_type, has_preference_threshold, self._add_gender_preference_traits)
            self.statistic_tracker.create_and_add_listener(stat_type, no_preference_threshold, self._remove_gender_preference_traits)

    def get_attracted_genders(self, preference_type):
        preference_map = None
        if preference_type == GenderPreferenceType.ROMANTIC:
            preference_map = GlobalGenderPreferenceTuning.ROMANTIC_PREFERENCE_TRAITS_MAPPING
        else:
            if preference_type == GenderPreferenceType.WOOHOO:
                preference_map = GlobalGenderPreferenceTuning.WOOHOO_PREFERENCE_TRAITS_MAPPING
        if preference_map is None:
            logger.error('Unavailable gender preference type when retrieving genders Sim is attracted to: {}', preference_type,
              owner='amwu')
            return singletons.EMPTY_SET
        genders = set()
        for gender, trait_tuple in preference_map.items():
            if self.has_trait(trait_tuple.is_attracted_trait):
                genders.add(gender)

        return frozenset(genders)

    @property
    def household_id(self):
        return self._household_id

    def assign_to_household(self, household, assign_is_npc=True):
        self._prior_household_zone_id = None if self.household is None else self.household.home_zone_id
        self._household_id = None if household is None else household.id
        if assign_is_npc:
            self.resend_is_npc()
        sim = self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is not None:
            for inv_obj in sim.inventory_component:
                inv_obj_current_household_id = inv_obj.get_household_owner_id()
                if inv_obj_current_household_id is not None:
                    if inv_obj_current_household_id != self._household_id:
                        inv_obj.set_household_owner_id(self._household_id)
                    else:
                        logger.error('Sim: {} has inventory object: {} already set to household id: {} when assigning sim to household.', sim, inv_obj, self._household_id)

    @property
    def travel_group_id(self):
        return self._travel_group_id

    def is_in_travel_group(self):
        if self._travel_group_id == 0:
            return False
        if self.travel_group is None:
            return False
        return True

    def assign_to_travel_group(self, travel_group):
        if self._travel_group_id != 0:
            travel_group.id != self._travel_group_id or game_services.service_manager.is_traveling or logger.error(('Attempting to add a Sim to a second travel group. Sim: {}, Travel Group: {}'.format(self, travel_group)), owner='rmccord')
            return False
        self._travel_group_id = travel_group.id
        return True

    def remove_from_travel_group(self, travel_group):
        if self._travel_group_id != travel_group.id:
            logger.error('Attempting to remove a Sim from a travel group they are not a part of.', owner='rmccord')
            return False
        self._travel_group_id = 0
        return True

    @property
    def is_at_home(self):
        if self.household is not None:
            if self.household.home_zone_id != 0:
                if self.household.home_zone_id == self.zone_id:
                    return True
        return self.is_renting_zone(self.zone_id)

    @property
    def lives_here(self):
        current_zone_id = services.current_zone_id()
        if self.household is not None:
            if self.household.home_zone_id != 0:
                if current_zone_id == self.household.home_zone_id:
                    return True
        return self.is_renting_zone(current_zone_id)

    @property
    def vacation_zone_id(self):
        if self.travel_group is None:
            return 0
        return self.travel_group.zone_id

    @property
    def vacation_or_home_zone_id(self):
        travel_group = self.travel_group
        if travel_group is not None:
            return travel_group.zone_id
        else:
            if self.household is None:
                return 0
            home_zone_id = self.household.home_zone_id
            return home_zone_id or self.roommate_zone_id
        return home_zone_id

    @property
    def can_care_for_toddler_at_home(self):
        if not self.can_live_alone:
            return False
        if self.household is None or self.household.home_zone_id != self.zone_id:
            return False
        if self._career_tracker.get_currently_at_work_career():
            return False
        return True

    @property
    def can_live_alone(self):
        return self.is_teen_or_older and self.is_human

    def get_home_lot(self):
        if self.household is None or self.household.home_zone_id == 0:
            return
        zone = services.get_zone_manager().get((self.household.home_zone_id), allow_uninstantiated_zones=True)
        if zone is None or zone.lot is None:
            return
        return zone.lot

    def can_go_to_work(self, zone_id=DEFAULT):
        if self.household is None:
            return False
        if zone_id is DEFAULT:
            zone_id = services.current_zone_id()
        return self.household.home_zone_id == zone_id

    def should_send_home_to_rabbit_hole(self):
        if self.travel_group_id != 0:
            return False
        return True

    def should_add_foreign_zone_buff(self, zone_id):
        if self.household.home_zone_id == zone_id:
            return False
        travel_group = self.travel_group
        if travel_group is not None:
            if travel_group.zone_id == zone_id:
                return False
        return True

    def is_renting_zone(self, zone_id):
        travel_group = self.travel_group
        if travel_group is not None:
            return travel_group.zone_id == zone_id
        if self.household is not None:
            if not self.household.home_zone_id:
                return self.roommate_zone_id == zone_id
        return False

    @property
    def story_progression_tracker(self):
        return self._story_progression_tracker

    @property
    def genealogy(self):
        return self._genealogy_tracker

    @property
    def generation(self):
        return self._generation

    @generation.setter
    def generation(self, value):
        self._generation = value

    def set_and_propagate_family_relation(self, relation, sim_info):
        self._genealogy_tracker.set_and_propagate_family_relation(relation, sim_info)

    def get_family_sim_ids(self, include_self=False):
        return self._genealogy_tracker.get_family_sim_ids(include_self=include_self)

    def get_relation(self, relation):
        return self._genealogy_tracker.get_relation(relation)

    def incest_prevention_test(self, sim_info_b):
        sim_a_fam_data = set(self.get_family_sim_ids(include_self=True))
        sim_b_fam_data = set(sim_info_b.get_family_sim_ids(include_self=True))
        rel_union = sim_a_fam_data & sim_b_fam_data
        if None in rel_union:
            rel_union.remove(None)
        if rel_union:
            return False
        return True

    def set_freeze_fame(self, should_freeze, force=False):
        if not force:
            if should_freeze:
                if self.get_gameplay_option(SimInfoGameplayOptions.FREEZE_FAME):
                    return
            elif not self.get_gameplay_option(SimInfoGameplayOptions.FREEZE_FAME):
                return
        self.set_gameplay_option(SimInfoGameplayOptions.FREEZE_FAME, should_freeze)
        if should_freeze:
            self.lock_statistic(FameTunables.FAME_RANKED_STATISTIC, StatisticLockAction.DO_NOT_CHANGE_VALUE, 'locked by sim_info.py:set_freeze_fame at {}'.format(services.time_service().sim_now))
        else:
            stat = self.get_statistic(FameTunables.FAME_RANKED_STATISTIC)
            if stat is None:
                logger.error('Trying to unfreeze fame for {}, but was unable to get or create a fame statistic', self)
            if self.is_in_locked_commodities(stat):
                self.unlock_statistic(FameTunables.FAME_RANKED_STATISTIC, 'unlocked by sim_info.py:set_freeze_fame at {}'.format(services.time_service().sim_now))

    def force_allow_fame(self, allow_fame):
        self.allow_fame = allow_fame
        self.set_gameplay_option(SimInfoGameplayOptions.FORCE_CURRENT_ALLOW_FAME_SETTING, True)

    @distributor.fields.Field(op=(distributor.ops.SetAllowFame))
    def allow_fame(self):
        return self.get_gameplay_option(SimInfoGameplayOptions.ALLOW_FAME)

    @allow_fame.setter
    def allow_fame(self, value):
        self.set_gameplay_option(SimInfoGameplayOptions.ALLOW_FAME, value)
        if FameTunables.FAME_RANKED_STATISTIC is None:
            return
            if self.lod < FameTunables.FAME_RANKED_STATISTIC.min_lod_value:
                return
            tracker = self.get_tracker(FameTunables.FAME_RANKED_STATISTIC)
            stat = tracker.get_statistic(FameTunables.FAME_RANKED_STATISTIC)
            if value:
                if self.is_stat_type_locked(FameTunables.FAME_RANKED_STATISTIC):
                    self.unlock_statistic(FameTunables.FAME_RANKED_STATISTIC, 'unlocked in sim_info.py:allow_fame at {}'.format(services.time_service().sim_now))
        else:
            self.set_freeze_fame(False)
            if not self.is_stat_type_locked(FameTunables.FAME_RANKED_STATISTIC):
                self.lock_statistic(FameTunables.FAME_RANKED_STATISTIC, StatisticLockAction.USE_MIN_VALUE_TUNING, 'locked in sim_info.py:allow_fame at {}'.format(services.time_service().sim_now))

    @distributor.fields.Field(op=(distributor.ops.SetAllowReputation))
    def allow_reputation(self):
        return self.get_gameplay_option(SimInfoGameplayOptions.ALLOW_REPUTATION)

    @allow_reputation.setter
    def allow_reputation(self, value):
        self.set_gameplay_option(SimInfoGameplayOptions.ALLOW_REPUTATION, value)
        if value:
            stat = self.get_statistic(ReputationTunables.REPUTATION_RANKED_STATISTIC)
            if self.is_in_locked_commodities(stat):
                self.unlock_statistic(ReputationTunables.REPUTATION_RANKED_STATISTIC, 'unlocked in sim_info.py:allow_reputation at {}'.format(services.time_service().sim_now))
        else:
            self.lock_statistic(ReputationTunables.REPUTATION_RANKED_STATISTIC, StatisticLockAction.DO_NOT_CHANGE_VALUE, 'locked in sim_info.py:allow_reputation at {}'.format(services.time_service().sim_now))

    def get_gameplay_option(self, gameplay_option):
        if self._gameplay_options & gameplay_option:
            return True
        return False

    def set_gameplay_option(self, gameplay_option, value):
        if value == (True if self._gameplay_options & gameplay_option else False):
            return
        elif value:
            self._gameplay_options |= gameplay_option
        else:
            self._gameplay_options &= ~gameplay_option

    def add_sim_info_id_to_squad(self, sim_info_id):
        self._squad_members.add(sim_info_id)

    def remove_sim_info_id_from_squad(self, sim_info_id):
        if sim_info_id in self._squad_members:
            self._squad_members.remove(sim_info_id)

    @property
    def squad_members(self):
        return self._squad_members

    def _get_persisted_lod(self):
        if self.lod == SimInfoLODLevel.ACTIVE:
            return SimInfoLODLevel.FULL
        return self.lod

    def save_sim(self, for_cloning=False, full_service=False):
        if self.lod > SimInfoLODLevel.MINIMUM:
            if self._aspiration_tracker is not None:
                self._aspiration_tracker.update_timers()
        else:
            attributes_msg = self._save_sim_attributes()
            if attributes_msg is None:
                return
                outfit_msg = self.save_outfits()
                if outfit_msg is None:
                    return
                if self.lod == SimInfoLODLevel.MINIMUM:
                    return self._save_sim_base(attributes_msg=attributes_msg, outfit_msg=outfit_msg)
                inventory_msg = self.inventory_data
                interactions_msg = None
                location_data = None
                sim = self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
                if sim is not None:
                    inventory_msg = sim.get_inventory_proto_for_save()
                    if inventory_msg is None:
                        return
                    self.inventory_data = inventory_msg
                    interactions_msg = sim.si_state.save_interactions()
                    if interactions_msg is None:
                        return
                    if full_service:
                        self._serialization_option = self._get_serialization_option()
                    if self._zone_id == services.current_zone_id():
                        location_data = gameplay_serialization.WorldLocation()
                        position, orientation, level, surface_id = sim.get_location_for_save()
                        location_data.x = position.x
                        location_data.y = position.y
                        location_data.z = position.z
                        location_data.rot_x = orientation.x
                        location_data.rot_y = orientation.y
                        location_data.rot_z = orientation.z
                        location_data.rot_w = orientation.w
                        location_data.level = level
                        location_data.surface_id = surface_id
            elif self._serialization_option != SimSerializationOption.UNDECLARED:
                if self._transform_on_load is not None:
                    location_data = gameplay_serialization.WorldLocation()
                    transform = self._transform_on_load
                    location_data.x = transform.translation.x
                    location_data.y = transform.translation.y
                    location_data.z = transform.translation.z
                    location_data.rot_x = transform.orientation.x
                    location_data.rot_y = transform.orientation.y
                    location_data.rot_z = transform.orientation.z
                    location_data.rot_w = transform.orientation.w
                    location_data.level = self._level_on_load
                    location_data.surface_id = self._surface_id_on_load
        sim_msg = self._save_sim_base(attributes_msg=attributes_msg, outfit_msg=outfit_msg,
          inventory_msg=inventory_msg,
          interactions_msg=interactions_msg,
          location_data=location_data,
          for_cloning=for_cloning)
        return sim_msg

    def _save_sim_base(self, attributes_msg=None, outfit_msg=None, inventory_msg=None, interactions_msg=None, location_data=None, for_cloning=False):
        self._set_fit_fat()
        sim_msg = services.get_persistence_service().get_sim_proto_buff(self.sim_id)
        if sim_msg is None:
            sim_msg = services.get_persistence_service().add_sim_proto_buff(self.sim_id)
        if for_cloning:
            clone_sim_msg = serialization.SimData()
            clone_sim_msg.MergeFrom(sim_msg)
            return self._generate_sim_protocol_buffer(clone_sim_msg, attributes_msg=attributes_msg,
              outfit_msg=outfit_msg,
              inventory_msg=inventory_msg,
              interactions_msg=interactions_msg,
              location_data=location_data,
              for_cloning=for_cloning)
        return self._generate_sim_protocol_buffer(sim_msg, attributes_msg=attributes_msg,
          outfit_msg=outfit_msg,
          inventory_msg=inventory_msg,
          interactions_msg=interactions_msg,
          location_data=location_data,
          for_cloning=for_cloning)

    def _generate_sim_protocol_buffer(self, sim_msg, attributes_msg=None, outfit_msg=None, inventory_msg=None, interactions_msg=None, location_data=None, for_cloning=False):
        global SAVE_ACTIVE_HOUSEHOLD_COMMAND
        if self._satisfaction_tracker is None:
            old_bucks_count = sim_msg.gameplay_data.whim_bucks
        else:
            sim_msg.Clear()
            sim_msg.sim_id = self.sim_id
            sim_msg.zone_id = self._zone_id
            sim_msg.world_id = self._world_id
            sim_msg.first_name = self._base.first_name
            sim_msg.last_name = self._base.last_name
            sim_msg.breed_name = self._base.breed_name
            sim_msg.first_name_key = self._base.first_name_key
            sim_msg.last_name_key = self._base.last_name_key
            sim_msg.full_name_key = self._base.full_name_key
            sim_msg.breed_name_key = self._base.breed_name_key
            sim_msg.pronouns.MergeFromString(self._base.pronouns)
            sim_msg.gender = self.gender
            sim_msg.extended_species = self.extended_species
            sim_msg.age = self.age
            sim_msg.skin_tone = self._base.skin_tone
            sim_msg.skin_tone_val_shift = self._base.skin_tone_val_shift
            sim_msg.pelt_layers.MergeFromString(self._base.pelt_layers)
            sim_msg.custom_texture = self._base.custom_texture
            sim_msg.voice_pitch = self._base.voice_pitch
            sim_msg.voice_actor = self._base.voice_actor
            sim_msg.voice_effect = self._base.voice_effect
            sim_msg.physique = self._base.physique
            sim_msg.facial_attr = self._base.facial_attributes or bytes(0)
            sim_msg.genetic_data.MergeFromString(self._base.genetic_data)
            sim_msg.fix_relationship = False
            sim_msg.generation = self._generation
            sim_msg.sim_lod = self._get_persisted_lod()
            sim_msg.outfits = outfit_msg
            sim_msg.flags = self._base.flags
            household_id = self._household_id if self._household_id is not None else 0
            sim_msg.household_id = household_id
            household = self.household
            sim_msg.household_name = household.name if household is not None else ''
            sim_msg.nucleus_id = self.account_id
            self._revision += 1
            sim_msg.revision = self._revision
            sim_msg.attributes = attributes_msg
            if self.spouse_sim_id is not None:
                sim_msg.significant_other = self.spouse_sim_id
            else:
                if self.fiance_sim_id is not None:
                    sim_msg.fiance = self.fiance_sim_id
                sim_msg.gameplay_data.serialization_option = self._serialization_option
                SimInfoCreationSource.save_creation_source(self.creation_source, sim_msg)
                sim_msg.created = services.time_service().sim_now.absolute_ticks()
                sim_msg.gameplay_data.old_household_id = household_id
                sim_msg.gameplay_data.premade_sim_template_id = self.premade_sim_template_id
                if self.lod == SimInfoLODLevel.MINIMUM:
                    return sim_msg
                sim_msg.pregnancy_progress = self.pregnancy_progress
                sim_msg.age_progress = self._age_progress.get_value()
                sim_msg.needs_age_progress_randomized = False
                sim_msg.inventory = inventory_msg
                sim_msg.primary_aspiration = self._primary_aspiration.guid64 if self._primary_aspiration is not None else 0
                outfit_type, outfit_index = self._current_outfit
                if outfit_type == OutfitCategory.SPECIAL:
                    if outfit_index == SpecialOutfitIndex.DEFAULT:
                        outfit_type, outfit_index = self.get_previous_outfit()
                    if outfit_type == OutfitCategory.BATHING:
                        outfit_type = OutfitCategory.EVERYDAY
                        outfit_index = 0
                    outfit_category_tuning = OutfitTuning.OUTFIT_CATEGORY_TUNING.get(outfit_type)
                    if outfit_category_tuning.save_outfit_category is None:
                        sim_msg.current_outfit_type = outfit_type
                else:
                    sim_msg.current_outfit_type = outfit_category_tuning.save_outfit_category
            sim_msg.current_outfit_index = outfit_index
            sim_msg.gameplay_data.inventory_value = self.inventory_value()
            if interactions_msg is not None:
                sim_msg.gameplay_data.interaction_state = interactions_msg
                if not for_cloning:
                    self._si_state.Clear()
                    self._si_state.MergeFrom(interactions_msg)
                    self._has_loaded_si_state = True
                sim_msg.gameplay_data.additional_bonus_days = self._additional_bonus_days
                if self.spawn_point_id is not None:
                    sim_msg.gameplay_data.spawn_point_id = self.spawn_point_id
                sim_msg.gameplay_data.spawn_point_option = self.spawn_point_option
                sim_msg.gameplay_data.spawner_tags.extend(self.spawner_tags)
                sim_msg.gameplay_data.build_buy_unlock_list = ResourceKeyList()
                for unlock in self.build_buy_unlocks:
                    if isinstance(unlock, int):
                        continue
                    key_proto = sims4.resources.get_protobuff_for_key(unlock)
                    sim_msg.gameplay_data.build_buy_unlock_list.resource_keys.append(key_proto)

                if self._satisfaction_tracker is not None:
                    sim_msg.gameplay_data.whim_bucks = self.get_satisfaction_points()
            else:
                sim_msg.gameplay_data.whim_bucks = old_bucks_count
        if self._whim_tracker is not None:
            self._whim_tracker.save_whims_info_to_proto(sim_msg.gameplay_data.whim_tracker)
        if self._away_action_tracker is not None:
            self._away_action_tracker.save_away_action_info_to_proto(sim_msg.gameplay_data.away_action_tracker)
        now_time = services.time_service().sim_now
        sim_msg.gameplay_data.zone_time_stamp.time_sim_info_was_saved = now_time.absolute_ticks()
        if self.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
            sim_msg.gameplay_data.zone_time_stamp.time_sim_was_saved = now_time.absolute_ticks()
        else:
            if self._time_sim_was_saved is not None:
                sim_msg.gameplay_data.zone_time_stamp.time_sim_was_saved = self._time_sim_was_saved.absolute_ticks()
            elif household is not None and household.home_zone_id != self._zone_id:
                if self.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                    time_expire = self._get_time_to_go_home()
                    sim_msg.gameplay_data.zone_time_stamp.game_time_expire = time_expire.absolute_ticks()
            else:
                if self.game_time_bring_home is not None:
                    sim_msg.gameplay_data.zone_time_stamp.game_time_expire = self.game_time_bring_home
                if location_data is not None:
                    sim_msg.gameplay_data.location = location_data
                current_mood = self.get_mood()
                current_mood_intensity = self.get_mood_intensity()
                sim_msg.current_mood = current_mood.guid64
                try:
                    sim_msg.current_mood_intensity = current_mood_intensity
                except ValueError:
                    logger.error('Mood intensity is {} for {}. Setting to 0', current_mood_intensity, current_mood)
                    sim_msg.current_mood_intensity = 0

            if self._initial_fitness_value is not None:
                sim_msg.initial_fitness_value = self._initial_fitness_value
            self.update_time_alive()
            sim_msg.gameplay_data.time_alive = self._time_alive.in_ticks()
            self.save_favorite(sim_msg.gameplay_data.favorite_data)
            if self._bucks_tracker is not None:
                self._bucks_tracker.save_data(sim_msg.gameplay_data)
            sim_msg.gameplay_data.gameplay_options = self._gameplay_options
            if self._squad_members:
                sim_msg.gameplay_data.squad_members.extend([sim_info_id for sim_info_id in self._squad_members])
            if SAVE_ACTIVE_HOUSEHOLD_COMMAND:
                sim_msg.sim_creation_path = serialization.SimData.SIMCREATION_PRE_MADE
                persist_fields_for_custom_option(sim_msg, custom_options.persist_for_new_game)
            if for_cloning:
                sim_msg.sim_creation_path = serialization.SimData.SIMCREATION_CLONED
                persist_fields_for_custom_option(sim_msg, custom_options.persist_for_cloned_sim)
            return sim_msg

    def _save_sim_attributes(self):
        sim_pb = services.get_persistence_service().get_sim_proto_buff(self.sim_id)
        old_attributes_save = sim_pb.attributes if sim_pb is not None else None
        attributes_save = protocols.PersistableSimInfoAttributes()
        attributes_save.occult_tracker = self._occult_tracker.save()
        death_save = self._death_tracker.save()
        if death_save is not None:
            attributes_save.death_tracker = self._death_tracker.save()
        attributes_save.genealogy_tracker = self._genealogy_tracker.save_genealogy()
        if self.lod == SimInfoLODLevel.MINIMUM:
            return attributes_save
        attributes_save.pregnancy_tracker = self._pregnancy_tracker.save()
        attributes_save.sim_careers = self._career_tracker.save()
        attributes_save.trait_tracker = self._trait_tracker.save()
        for tag, obj_id in self._autonomy_scoring_preferences.items():
            with ProtocolBufferRollback(attributes_save.object_preferences.preferences) as (entry):
                entry.tag = tag
                entry.object_id = obj_id

        for tag, obj_id in self._autonomy_use_preferences.items():
            with ProtocolBufferRollback(attributes_save.object_ownership.owned_object) as (entry):
                entry.tag = tag
                entry.object_id = obj_id

        stored_object_info_component = self.get_component(objects.components.types.STORED_OBJECT_INFO_COMPONENT)
        if stored_object_info_component is not None:
            attributes_save.stored_object_info_component = stored_object_info_component.get_save_data()
        commodites, skill_statistics, ranked_statistics = self.commodity_tracker.save()
        attributes_save.commodity_tracker.commodities.extend(commodites)
        regular_statistics = self.statistic_tracker.save()
        attributes_save.statistics_tracker.statistics.extend(regular_statistics)
        attributes_save.skill_tracker.skills.extend(skill_statistics)
        attributes_save.ranked_statistic_tracker.ranked_statistics.extend(ranked_statistics)
        if self.is_human:
            self.trait_statistic_tracker.save(attributes_save.trait_statistic_tracker)
        attributes_save.suntan_tracker = self._suntan_tracker.save()
        if self._familiar_tracker is not None:
            attributes_save.familiar_tracker = self._familiar_tracker.save()
        else:
            if old_attributes_save is not None:
                attributes_save.familiar_tracker.MergeFrom(old_attributes_save.familiar_tracker)
            elif self._favorites_tracker is not None:
                favorites_save = self._favorites_tracker.save()
                if self.get_sim_instance() is None:
                    if old_attributes_save is not None:
                        favorites_save.stack_favorites.extend(old_attributes_save.favorites_tracker.stack_favorites)
                attributes_save.favorites_tracker = favorites_save
            else:
                if old_attributes_save is not None:
                    attributes_save.favorites_tracker.MergeFrom(old_attributes_save.favorites_tracker)
                if self._aspiration_tracker is not None:
                    self._aspiration_tracker.save(attributes_save.event_data_tracker)
                else:
                    if old_attributes_save is not None:
                        attributes_save.event_data_tracker.MergeFrom(old_attributes_save.event_data_tracker)
        if self._unlock_tracker is not None:
            attributes_save.unlock_tracker = self._unlock_tracker.save_unlock()
        else:
            if old_attributes_save is not None:
                attributes_save.unlock_tracker.MergeFrom(old_attributes_save.unlock_tracker)
            elif self._notebook_tracker is not None:
                attributes_save.notebook_tracker = self._notebook_tracker.save_notebook()
            else:
                if old_attributes_save is not None:
                    attributes_save.notebook_tracker.MergeFrom(old_attributes_save.notebook_tracker)
        if self._adventure_tracker is not None:
            attributes_save.adventure_tracker = self._adventure_tracker.save()
        else:
            if old_attributes_save is not None:
                attributes_save.adventure_tracker.MergeFrom(old_attributes_save.adventure_tracker)
            elif self._royalty_tracker is not None:
                attributes_save.royalty_tracker = self._royalty_tracker.save()
            else:
                if old_attributes_save is not None:
                    attributes_save.royalty_tracker.MergeFrom(old_attributes_save.royalty_tracker)
        if self._relic_tracker is not None:
            attributes_save.relic_tracker = self._relic_tracker.save()
        else:
            if old_attributes_save is not None:
                attributes_save.relic_tracker.MergeFrom(old_attributes_save.relic_tracker)
            elif self._sickness_tracker is not None:
                if self._sickness_tracker.should_persist_data():
                    attributes_save.sickness_tracker = self._sickness_tracker.sickness_tracker_save_data()
            else:
                if old_attributes_save is not None:
                    attributes_save.sickness_tracker.MergeFrom(old_attributes_save.sickness_tracker)
                if self._lifestyle_brand_tracker is not None:
                    attributes_save.lifestyle_brand_tracker = self._lifestyle_brand_tracker.save()
                else:
                    if old_attributes_save is not None:
                        attributes_save.lifestyle_brand_tracker.MergeFrom(old_attributes_save.lifestyle_brand_tracker)
        if self._degree_tracker is not None:
            attributes_save.degree_tracker = self._degree_tracker.save()
        else:
            if old_attributes_save is not None:
                attributes_save.degree_tracker.MergeFrom(old_attributes_save.degree_tracker)
            elif self._organization_tracker is not None:
                attributes_save.organization_tracker = self._organization_tracker.save()
            else:
                if old_attributes_save is not None:
                    attributes_save.organization_tracker.MergeFrom(old_attributes_save.organization_tracker)
        if self._fixup_tracker is not None:
            attributes_save.fixup_tracker = self._fixup_tracker.save()
        else:
            if old_attributes_save is not None:
                attributes_save.fixup_tracker.MergeFrom(old_attributes_save.fixup_tracker)
            else:
                attributes_save.appearance_tracker = self.appearance_tracker.save_appearance_tracker()
                if self._story_progression_tracker is not None:
                    story_progression_data = SimObjectAttributes_pb2.PersistableStoryProgressionTracker()
                    self._story_progression_tracker.save(story_progression_data)
                    attributes_save.story_progression_tracker = story_progression_data
                else:
                    if old_attributes_save is not None:
                        attributes_save.story_progression_tracker.MergeFrom(old_attributes_save.story_progression_tracker)
        if self._lunar_effect_tracker is not None and self._lunar_effect_tracker.has_data_to_save:
            lunar_effect_data = SimObjectAttributes_pb2.PersistableLunarEffectTracker()
            self._lunar_effect_tracker.save_lunar_effects(lunar_effect_data)
            attributes_save.lunar_effect_tracker = lunar_effect_data
        else:
            if old_attributes_save is not None:
                attributes_save.lunar_effect_tracker.MergeFrom(old_attributes_save.lunar_effect_tracker)
            return attributes_save

    def _get_serialization_option(self):
        sim = self.get_sim_instance(allow_hidden_flags=(HiddenReasonFlag.RABBIT_HOLE))
        if sim is None:
            return self._serialization_option
        owning_household = services.current_zone().get_active_lot_owner_household()
        situation_manager = services.get_zone_situation_manager()
        current_zone_id = services.current_zone_id()
        if not (sim.is_selectable or owning_household) is not None or self in owning_household or self.is_renting_zone(current_zone_id):
            if sim.is_on_active_lot() or sim.has_hidden_flags(HiddenReasonFlag.RABBIT_HOLE):
                return SimSerializationOption.LOT
            return SimSerializationOption.OPEN_STREETS
        return situation_manager.get_sim_serialization_option(sim)

    def _save_for_travel(self):
        sim = self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED)
        if sim is None:
            return
        interactions_msg = sim.si_state.save_interactions()
        if interactions_msg is None:
            return
        inventory_msg = sim.get_inventory_proto_for_save()
        if inventory_msg is None:
            return
        sim_msg = services.get_persistence_service().get_sim_proto_buff(self.sim_id)
        if sim_msg is None:
            self.save_sim()
        self._si_state.Clear()
        self._si_state.MergeFrom(interactions_msg)
        self._has_loaded_si_state = True
        self.inventory_data = inventory_msg
        self._serialization_option = self._get_serialization_option()
        position, orientation, level, surface_id = sim.get_location_for_save()
        world_coord = sims4.math.Transform(position, orientation)
        self._transform_on_load = world_coord
        self._level_on_load = level
        self._surface_id_on_load = surface_id
        sim_msg.gameplay_data.interaction_state = interactions_msg
        sim_msg.inventory = inventory_msg
        location_data = gameplay_serialization.WorldLocation()
        location_data.x = position.x
        location_data.y = position.y
        location_data.z = position.z
        location_data.rot_x = orientation.x
        location_data.rot_y = orientation.y
        location_data.rot_z = orientation.z
        location_data.rot_w = orientation.w
        location_data.level = level
        location_data.surface_id = surface_id
        sim_msg.gameplay_data.location = location_data
        if self.household is not None:
            if self.household.home_zone_id != self._zone_id:
                self.game_time_bring_home = self._get_time_to_go_home()
        vehicle = sim.parented_vehicle
        if vehicle is not None and vehicle.routing_surface.type == SurfaceType.SURFACETYPE_WORLD:
            sim_msg.gameplay_data.vehicle_id = vehicle.id
            self._vehicle_id = vehicle.id
        else:
            self._vehicle_id = None

    def load_for_travel_to_current_zone(self):
        sim_proto = services.get_persistence_service().get_sim_proto_buff(self.sim_id)
        if sim_proto is None:
            logger.error("Missing persistence for {}. Can't update due to travel", self)
            return
        self._zone_id = sim_proto.zone_id
        self.zone_name = sim_proto.zone_name
        self._world_id = sim_proto.world_id

    def load_sim_info(self, sim_proto, is_clone=False, default_lod=SimInfoLODLevel.BACKGROUND):
        time_stamp = time.time()
        self._base.species = sim_proto.extended_species
        self._species = SpeciesExtended.get_species(self.extended_species)
        required_pack = SpeciesExtended.get_required_pack(self.extended_species)
        if required_pack is not None:
            if not is_available_pack(required_pack):
                raise UnavailablePackError('Cannot load Sims with species {}'.format(self.extended_species))
        if indexed_manager.capture_load_times:
            species_def = self.get_sim_definition(self.species)
            if species_def not in indexed_manager.object_load_times:
                indexed_manager.object_load_times[species_def] = ObjectLoadData()
        self._sim_creation_path = sim_proto.sim_creation_path
        self._lod = SimInfoLODLevel(sim_proto.sim_lod) if sim_proto.HasField('sim_lod') else default_lod
        self._initialize_sim_info_trackers(self._lod)
        skip_load = self._sim_creation_path != serialization.SimData.SIMCREATION_NONE
        if sim_proto.gender == types.Gender.MALE or sim_proto.gender == types.Gender.FEMALE:
            self._base.gender = sim_proto.gender
        self._base.age = types.Age(sim_proto.age)
        if not INJECT_LOD_NAME_IN_CALLSTACK:
            self._load_sim_info(sim_proto, skip_load, is_clone=is_clone)
            time_elapsed = time.time() - time_stamp
            if indexed_manager.capture_load_times:
                indexed_manager.object_load_times[species_def].time_spent_loading += time_elapsed
                indexed_manager.object_load_times[species_def].loads += 1
            lod_logger.info('Loaded {} with lod {} in {} seconds.', self.full_name, self._lod.name, time_elapsed)
            return
        name_f = create_custom_named_profiler_function('Load LOD {} SimInfo'.format(self._lod.name))
        name_f(lambda : self._load_sim_info(sim_proto, skip_load, is_clone=is_clone))
        if indexed_manager.capture_load_times:
            time_elapsed = time.time() - time_stamp
            indexed_manager.object_load_times[species_def].time_spent_loading += time_elapsed
            indexed_manager.object_load_times[species_def].loads += 1
            lod_logger.info('Loaded {} with lod {} in {} seconds.', self.full_name, self._lod.name, time_elapsed)

    def _load_sim_info--- This code section failed: ---

 L.3348         0  LOAD_FAST                'sim_proto'
                2  LOAD_ATTR                first_name
                4  LOAD_FAST                'self'
                6  LOAD_ATTR                _base
                8  STORE_ATTR               first_name

 L.3349        10  LOAD_FAST                'sim_proto'
               12  LOAD_ATTR                last_name
               14  LOAD_FAST                'self'
               16  LOAD_ATTR                _base
               18  STORE_ATTR               last_name

 L.3350        20  LOAD_FAST                'sim_proto'
               22  LOAD_ATTR                breed_name
               24  LOAD_FAST                'self'
               26  LOAD_ATTR                _base
               28  STORE_ATTR               breed_name

 L.3351        30  LOAD_FAST                'sim_proto'
               32  LOAD_ATTR                first_name_key
               34  LOAD_FAST                'self'
               36  LOAD_ATTR                _base
               38  STORE_ATTR               first_name_key

 L.3352        40  LOAD_FAST                'sim_proto'
               42  LOAD_ATTR                last_name_key
               44  LOAD_FAST                'self'
               46  LOAD_ATTR                _base
               48  STORE_ATTR               last_name_key

 L.3353        50  LOAD_FAST                'sim_proto'
               52  LOAD_ATTR                full_name_key
               54  LOAD_FAST                'self'
               56  LOAD_ATTR                _base
               58  STORE_ATTR               full_name_key

 L.3354        60  LOAD_FAST                'sim_proto'
               62  LOAD_ATTR                breed_name_key
               64  LOAD_FAST                'self'
               66  LOAD_ATTR                _base
               68  STORE_ATTR               breed_name_key

 L.3355        70  LOAD_FAST                'sim_proto'
               72  LOAD_ATTR                pronouns
               74  LOAD_METHOD              SerializeToString
               76  CALL_METHOD_0         0  '0 positional arguments'
               78  LOAD_FAST                'self'
               80  LOAD_ATTR                _base
               82  STORE_ATTR               pronouns

 L.3356        84  LOAD_FAST                'sim_proto'
               86  LOAD_ATTR                zone_id
               88  LOAD_FAST                'self'
               90  STORE_ATTR               _zone_id

 L.3357        92  LOAD_FAST                'sim_proto'
               94  LOAD_ATTR                zone_name
               96  LOAD_FAST                'self'
               98  STORE_ATTR               zone_name

 L.3358       100  LOAD_FAST                'sim_proto'
              102  LOAD_ATTR                world_id
              104  LOAD_FAST                'self'
              106  STORE_ATTR               _world_id

 L.3359       108  LOAD_FAST                'sim_proto'
              110  LOAD_ATTR                household_id
              112  LOAD_FAST                'self'
              114  STORE_ATTR               _household_id

 L.3360       116  LOAD_FAST                'sim_proto'
              118  LOAD_ATTR                gameplay_data
              120  LOAD_ATTR                serialization_option
              122  LOAD_FAST                'self'
              124  STORE_ATTR               _serialization_option

 L.3361       126  LOAD_FAST                'sim_proto'
              128  LOAD_ATTR                skin_tone
              130  LOAD_FAST                'self'
              132  LOAD_ATTR                _base
              134  STORE_ATTR               skin_tone

 L.3362       136  LOAD_FAST                'sim_proto'
              138  LOAD_ATTR                skin_tone_val_shift
              140  LOAD_FAST                'self'
              142  LOAD_ATTR                _base
              144  STORE_ATTR               skin_tone_val_shift

 L.3363       146  LOAD_FAST                'sim_proto'
              148  LOAD_ATTR                pelt_layers
              150  LOAD_METHOD              SerializeToString
              152  CALL_METHOD_0         0  '0 positional arguments'
              154  LOAD_FAST                'self'
              156  LOAD_ATTR                _base
              158  STORE_ATTR               pelt_layers

 L.3364       160  LOAD_FAST                'sim_proto'
              162  LOAD_ATTR                custom_texture
              164  LOAD_FAST                'self'
              166  LOAD_ATTR                _base
              168  STORE_ATTR               custom_texture

 L.3365       170  LOAD_FAST                'sim_proto'
              172  LOAD_ATTR                voice_pitch
              174  LOAD_FAST                'self'
              176  LOAD_ATTR                _base
              178  STORE_ATTR               voice_pitch

 L.3366       180  LOAD_FAST                'sim_proto'
              182  LOAD_ATTR                voice_actor
              184  LOAD_FAST                'self'
              186  LOAD_ATTR                _base
              188  STORE_ATTR               voice_actor

 L.3367       190  LOAD_FAST                'sim_proto'
              192  LOAD_ATTR                voice_effect
              194  LOAD_FAST                'self'
              196  LOAD_ATTR                _base
              198  STORE_ATTR               voice_effect

 L.3368       200  LOAD_FAST                'sim_proto'
              202  LOAD_ATTR                physique
              204  LOAD_FAST                'self'
              206  LOAD_ATTR                _base
              208  STORE_ATTR               physique

 L.3369       210  LOAD_FAST                'sim_proto'
              212  LOAD_ATTR                facial_attr
              214  LOAD_FAST                'self'
              216  LOAD_ATTR                _base
              218  STORE_ATTR               facial_attributes

 L.3370       220  LOAD_FAST                'sim_proto'
              222  LOAD_ATTR                generation
              224  LOAD_FAST                'self'
              226  STORE_ATTR               _generation

 L.3371       228  LOAD_FAST                'sim_proto'
              230  LOAD_ATTR                fix_relationship
              232  LOAD_FAST                'self'
              234  STORE_ATTR               _fix_relationships

 L.3375       236  LOAD_FAST                'self'
              238  LOAD_ATTR                _sim_creation_path
              240  LOAD_GLOBAL              serialization
              242  LOAD_ATTR                SimData
              244  LOAD_ATTR                SIMCREATION_NONE
              246  COMPARE_OP               !=
              248  LOAD_FAST                'self'
              250  STORE_ATTR               do_first_sim_info_load_fixups

 L.3377       252  LOAD_FAST                'self'
              254  LOAD_METHOD              _get_fit_fat
              256  CALL_METHOD_0         0  '0 positional arguments'
              258  POP_TOP          

 L.3379       260  LOAD_FAST                'sim_proto'
              262  LOAD_ATTR                attributes
              264  STORE_FAST               'sim_attribute_data'

 L.3380       266  LOAD_FAST                'sim_attribute_data'
              268  LOAD_CONST               None
              270  COMPARE_OP               is-not
          272_274  POP_JUMP_IF_FALSE   310  'to 310'

 L.3385       276  LOAD_FAST                'self'
              278  LOAD_ATTR                set_trait_ids_on_base
              280  LOAD_GLOBAL              list
              282  LOAD_GLOBAL              set
              284  LOAD_GLOBAL              itertools
              286  LOAD_METHOD              chain
              288  LOAD_FAST                'sim_attribute_data'
              290  LOAD_ATTR                trait_tracker
              292  LOAD_ATTR                trait_ids
              294  LOAD_FAST                'self'
              296  LOAD_ATTR                trait_ids
              298  CALL_METHOD_2         2  '2 positional arguments'
              300  CALL_FUNCTION_1       1  '1 positional argument'
              302  CALL_FUNCTION_1       1  '1 positional argument'
              304  LOAD_CONST               ('trait_ids_override',)
              306  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              308  POP_TOP          
            310_0  COME_FROM           272  '272'

 L.3390       310  LOAD_FAST                'sim_proto'
              312  LOAD_ATTR                genetic_data
              314  LOAD_METHOD              SerializeToString
              316  CALL_METHOD_0         0  '0 positional arguments'
              318  LOAD_FAST                'self'
              320  LOAD_ATTR                _base
              322  STORE_ATTR               genetic_data

 L.3391       324  LOAD_FAST                'sim_proto'
              326  LOAD_ATTR                flags
              328  LOAD_FAST                'self'
              330  LOAD_ATTR                _base
              332  STORE_ATTR               flags

 L.3396       334  LOAD_FAST                'self'
              336  LOAD_METHOD              load_outfits
              338  LOAD_FAST                'sim_proto'
              340  LOAD_ATTR                outfits
              342  CALL_METHOD_1         1  '1 positional argument'
              344  POP_TOP          

 L.3398       346  LOAD_GLOBAL              SimInfoCreationSource
              348  LOAD_METHOD              load_creation_source
              350  LOAD_FAST                'sim_proto'
              352  CALL_METHOD_1         1  '1 positional argument'
              354  LOAD_FAST                'self'
              356  STORE_ATTR               creation_source

 L.3399       358  LOAD_FAST                'sim_proto'
              360  LOAD_ATTR                nucleus_id
              362  LOAD_FAST                'self'
              364  STORE_ATTR               _nucleus_id

 L.3400       366  LOAD_FAST                'sim_proto'
              368  LOAD_ATTR                gameplay_data
              370  LOAD_ATTR                premade_sim_template_id
              372  LOAD_FAST                'self'
              374  STORE_ATTR               premade_sim_template_id

 L.3401       376  LOAD_FAST                'sim_proto'
              378  LOAD_ATTR                revision
              380  LOAD_FAST                'self'
              382  STORE_ATTR               _revision

 L.3403       384  LOAD_FAST                'sim_attribute_data'
              386  LOAD_CONST               None
              388  COMPARE_OP               is-not
          390_392  POP_JUMP_IF_FALSE   500  'to 500'

 L.3404       394  LOAD_FAST                'self'
              396  LOAD_ATTR                _relationship_tracker
              398  LOAD_METHOD              load
              400  LOAD_FAST                'sim_attribute_data'
              402  LOAD_ATTR                relationship_tracker
              404  LOAD_ATTR                relationships
              406  CALL_METHOD_1         1  '1 positional argument'
              408  POP_TOP          

 L.3405       410  LOAD_FAST                'self'
              412  LOAD_ATTR                _genealogy_tracker
              414  LOAD_METHOD              load_genealogy
              416  LOAD_FAST                'sim_attribute_data'
              418  LOAD_ATTR                genealogy_tracker
              420  CALL_METHOD_1         1  '1 positional argument'
              422  POP_TOP          

 L.3406       424  LOAD_FAST                'self'
              426  LOAD_ATTR                _death_tracker
              428  LOAD_METHOD              load
              430  LOAD_FAST                'sim_attribute_data'
              432  LOAD_ATTR                death_tracker
              434  CALL_METHOD_1         1  '1 positional argument'
              436  POP_TOP          

 L.3407       438  LOAD_FAST                'self'
              440  LOAD_ATTR                _occult_tracker
              442  LOAD_METHOD              load
              444  LOAD_FAST                'sim_attribute_data'
              446  LOAD_ATTR                occult_tracker
              448  CALL_METHOD_1         1  '1 positional argument'
              450  POP_TOP          

 L.3408       452  LOAD_FAST                'sim_proto'
              454  LOAD_ATTR                significant_other
              456  LOAD_CONST               0
              458  COMPARE_OP               !=
          460_462  POP_JUMP_IF_FALSE   476  'to 476'

 L.3409       464  LOAD_FAST                'self'
              466  LOAD_METHOD              update_spouse_sim_id
              468  LOAD_FAST                'sim_proto'
              470  LOAD_ATTR                significant_other
              472  CALL_METHOD_1         1  '1 positional argument'
              474  POP_TOP          
            476_0  COME_FROM           460  '460'

 L.3410       476  LOAD_FAST                'sim_proto'
              478  LOAD_ATTR                fiance
              480  LOAD_CONST               0
              482  COMPARE_OP               !=
          484_486  POP_JUMP_IF_FALSE   500  'to 500'

 L.3411       488  LOAD_FAST                'self'
              490  LOAD_METHOD              update_fiance_sim_id
              492  LOAD_FAST                'sim_proto'
              494  LOAD_ATTR                fiance
              496  CALL_METHOD_1         1  '1 positional argument'
              498  POP_TOP          
            500_0  COME_FROM           484  '484'
            500_1  COME_FROM           390  '390'

 L.3417       500  LOAD_GLOBAL              Ghost
              502  LOAD_METHOD              make_ghost_if_needed
              504  LOAD_FAST                'self'
              506  CALL_METHOD_1         1  '1 positional argument'
              508  POP_TOP          

 L.3419       510  LOAD_FAST                'self'
              512  LOAD_ATTR                lod
              514  LOAD_GLOBAL              SimInfoLODLevel
              516  LOAD_ATTR                MINIMUM
              518  COMPARE_OP               ==
          520_522  POP_JUMP_IF_FALSE   542  'to 542'

 L.3422       524  LOAD_GLOBAL              services
              526  LOAD_METHOD              sim_info_manager
              528  CALL_METHOD_0         0  '0 positional arguments'
              530  LOAD_METHOD              add_sim_info_if_not_in_manager
              532  LOAD_FAST                'self'
              534  CALL_METHOD_1         1  '1 positional argument'
              536  POP_TOP          

 L.3423       538  LOAD_CONST               None
              540  RETURN_VALUE     
            542_0  COME_FROM           520  '520'

 L.3425       542  LOAD_FAST                'sim_proto'
              544  LOAD_ATTR                age_progress
              546  STORE_FAST               'age_progress'

 L.3429       548  LOAD_FAST                'sim_proto'
              550  LOAD_ATTR                needs_age_progress_randomized
          552_554  POP_JUMP_IF_FALSE   572  'to 572'

 L.3430       556  LOAD_FAST                'self'
              558  LOAD_METHOD              get_randomized_progress
              560  LOAD_FAST                'age_progress'
              562  CALL_METHOD_1         1  '1 positional argument'
              564  STORE_FAST               'age_progress'

 L.3431       566  LOAD_CONST               False
              568  LOAD_FAST                'sim_proto'
              570  STORE_ATTR               needs_age_progress_randomized
            572_0  COME_FROM           552  '552'

 L.3432       572  LOAD_FAST                'self'
              574  LOAD_ATTR                _age_progress
              576  LOAD_METHOD              set_value
              578  LOAD_FAST                'age_progress'
              580  CALL_METHOD_1         1  '1 positional argument'
              582  POP_TOP          

 L.3433       584  LOAD_GLOBAL              set
              586  CALL_FUNCTION_0       0  '0 positional arguments'
              588  LOAD_FAST                'self'
              590  STORE_ATTR               _build_buy_unlocks

 L.3436       592  LOAD_GLOBAL              set
              594  LOAD_GLOBAL              list
              596  LOAD_FAST                'sim_proto'
              598  LOAD_ATTR                gameplay_data
              600  LOAD_ATTR                build_buy_unlocks
              602  CALL_FUNCTION_1       1  '1 positional argument'
              604  CALL_FUNCTION_1       1  '1 positional argument'
              606  STORE_FAST               'old_unlocks'

 L.3437       608  SETUP_LOOP          666  'to 666'
              610  LOAD_FAST                'old_unlocks'
              612  GET_ITER         
            614_0  COME_FROM           626  '626'
              614  FOR_ITER            664  'to 664'
              616  STORE_FAST               'unlock'

 L.3438       618  LOAD_GLOBAL              isinstance
              620  LOAD_FAST                'unlock'
              622  LOAD_GLOBAL              int
              624  CALL_FUNCTION_2       2  '2 positional arguments'
          626_628  POP_JUMP_IF_FALSE   614  'to 614'

 L.3439       630  LOAD_GLOBAL              sims4
              632  LOAD_ATTR                resources
              634  LOAD_METHOD              Key
              636  LOAD_GLOBAL              Types
              638  LOAD_ATTR                OBJCATALOG
              640  LOAD_FAST                'unlock'
              642  LOAD_CONST               0
              644  CALL_METHOD_3         3  '3 positional arguments'
              646  STORE_FAST               'key'

 L.3440       648  LOAD_FAST                'self'
              650  LOAD_ATTR                _build_buy_unlocks
              652  LOAD_METHOD              add
              654  LOAD_FAST                'key'
              656  CALL_METHOD_1         1  '1 positional argument'
              658  POP_TOP          
          660_662  JUMP_BACK           614  'to 614'
              664  POP_BLOCK        
            666_0  COME_FROM_LOOP      608  '608'

 L.3441       666  LOAD_GLOBAL              hasattr
              668  LOAD_FAST                'sim_proto'
              670  LOAD_ATTR                gameplay_data
              672  LOAD_STR                 'build_buy_unlock_list'
              674  CALL_FUNCTION_2       2  '2 positional arguments'
          676_678  POP_JUMP_IF_FALSE   736  'to 736'

 L.3442       680  SETUP_LOOP          736  'to 736'
              682  LOAD_FAST                'sim_proto'
              684  LOAD_ATTR                gameplay_data
              686  LOAD_ATTR                build_buy_unlock_list
              688  LOAD_ATTR                resource_keys
              690  GET_ITER         
              692  FOR_ITER            734  'to 734'
              694  STORE_FAST               'key_proto'

 L.3443       696  LOAD_GLOBAL              sims4
              698  LOAD_ATTR                resources
              700  LOAD_METHOD              Key
              702  LOAD_FAST                'key_proto'
              704  LOAD_ATTR                type
              706  LOAD_FAST                'key_proto'
              708  LOAD_ATTR                instance
              710  LOAD_FAST                'key_proto'
              712  LOAD_ATTR                group
              714  CALL_METHOD_3         3  '3 positional arguments'
              716  STORE_FAST               'key'

 L.3444       718  LOAD_FAST                'self'
              720  LOAD_ATTR                _build_buy_unlocks
              722  LOAD_METHOD              add
              724  LOAD_FAST                'key'
              726  CALL_METHOD_1         1  '1 positional argument'
              728  POP_TOP          
          730_732  JUMP_BACK           692  'to 692'
              734  POP_BLOCK        
            736_0  COME_FROM_LOOP      680  '680'
            736_1  COME_FROM           676  '676'

 L.3446       736  LOAD_GLOBAL              services
              738  LOAD_METHOD              get_instance_manager
              740  LOAD_GLOBAL              sims4
              742  LOAD_ATTR                resources
              744  LOAD_ATTR                Types
              746  LOAD_ATTR                ASPIRATION_TRACK
              748  CALL_METHOD_1         1  '1 positional argument'
              750  LOAD_METHOD              get
              752  LOAD_FAST                'sim_proto'
              754  LOAD_ATTR                primary_aspiration
              756  CALL_METHOD_1         1  '1 positional argument'
              758  LOAD_FAST                'self'
              760  STORE_ATTR               _primary_aspiration

 L.3451       762  LOAD_FAST                'self'
              764  LOAD_ATTR                _primary_aspiration
              766  LOAD_CONST               None
              768  COMPARE_OP               is
          770_772  POP_JUMP_IF_TRUE    786  'to 786'
              774  LOAD_FAST                'self'
              776  LOAD_ATTR                _primary_aspiration
              778  LOAD_METHOD              is_available
              780  CALL_METHOD_0         0  '0 positional arguments'
          782_784  POP_JUMP_IF_TRUE    886  'to 886'
            786_0  COME_FROM           770  '770'

 L.3452       786  LOAD_FAST                'self'
              788  LOAD_ATTR                is_human
          790_792  POP_JUMP_IF_FALSE   886  'to 886'

 L.3453       794  LOAD_FAST                'self'
              796  LOAD_ATTR                is_toddler_or_younger
          798_800  POP_JUMP_IF_TRUE    886  'to 886'

 L.3454       802  BUILD_LIST_0          0 
              804  STORE_FAST               'available_aspirations'

 L.3456       806  LOAD_GLOBAL              services
              808  LOAD_METHOD              get_instance_manager
              810  LOAD_GLOBAL              sims4
              812  LOAD_ATTR                resources
              814  LOAD_ATTR                Types
              816  LOAD_ATTR                ASPIRATION_TRACK
              818  CALL_METHOD_1         1  '1 positional argument'
              820  STORE_FAST               'aspiration_track_manager'

 L.3457       822  SETUP_LOOP          874  'to 874'
              824  LOAD_FAST                'aspiration_track_manager'
              826  LOAD_ATTR                types
              828  LOAD_METHOD              values
              830  CALL_METHOD_0         0  '0 positional arguments'
              832  GET_ITER         
            834_0  COME_FROM           854  '854'
            834_1  COME_FROM           842  '842'
              834  FOR_ITER            872  'to 872'
              836  STORE_FAST               'aspiration_track'

 L.3459       838  LOAD_FAST                'aspiration_track'
              840  LOAD_ATTR                is_hidden_unlockable
          842_844  POP_JUMP_IF_TRUE    834  'to 834'
              846  LOAD_FAST                'aspiration_track'
              848  LOAD_METHOD              is_valid_for_sim
              850  LOAD_FAST                'self'
              852  CALL_METHOD_1         1  '1 positional argument'
          854_856  POP_JUMP_IF_FALSE   834  'to 834'

 L.3460       858  LOAD_FAST                'available_aspirations'
              860  LOAD_METHOD              append
              862  LOAD_FAST                'aspiration_track'
              864  CALL_METHOD_1         1  '1 positional argument'
              866  POP_TOP          
          868_870  JUMP_BACK           834  'to 834'
              872  POP_BLOCK        
            874_0  COME_FROM_LOOP      822  '822'

 L.3462       874  LOAD_GLOBAL              random
              876  LOAD_METHOD              choice
              878  LOAD_FAST                'available_aspirations'
              880  CALL_METHOD_1         1  '1 positional argument'
              882  LOAD_FAST                'self'
              884  STORE_ATTR               _primary_aspiration
            886_0  COME_FROM           798  '798'
            886_1  COME_FROM           790  '790'
            886_2  COME_FROM           782  '782'

 L.3463       886  LOAD_FAST                'sim_proto'
              888  LOAD_ATTR                gameplay_data
              890  LOAD_ATTR                inventory_value
              892  LOAD_FAST                'self'
              894  STORE_ATTR               _cached_inventory_value

 L.3469       896  LOAD_FAST                'skip_load'
          898_900  POP_JUMP_IF_TRUE    930  'to 930'
              902  LOAD_FAST                'self'
              904  LOAD_ATTR                _away_action_tracker
              906  LOAD_CONST               None
              908  COMPARE_OP               is-not
          910_912  POP_JUMP_IF_FALSE   930  'to 930'

 L.3470       914  LOAD_FAST                'self'
              916  LOAD_ATTR                _away_action_tracker
              918  LOAD_METHOD              load_away_action_info_from_proto
              920  LOAD_FAST                'sim_proto'
              922  LOAD_ATTR                gameplay_data
              924  LOAD_ATTR                away_action_tracker
              926  CALL_METHOD_1         1  '1 positional argument'
              928  POP_TOP          
            930_0  COME_FROM           910  '910'
            930_1  COME_FROM           898  '898'

 L.3472       930  LOAD_FAST                'sim_proto'
              932  LOAD_ATTR                gameplay_data
              934  LOAD_METHOD              HasField
              936  LOAD_STR                 'spawn_point_id'
              938  CALL_METHOD_1         1  '1 positional argument'
          940_942  POP_JUMP_IF_FALSE   952  'to 952'
              944  LOAD_FAST                'sim_proto'
              946  LOAD_ATTR                gameplay_data
              948  LOAD_ATTR                spawn_point_id
              950  JUMP_FORWARD        954  'to 954'
            952_0  COME_FROM           940  '940'
              952  LOAD_CONST               None
            954_0  COME_FROM           950  '950'
              954  LOAD_FAST                'self'
              956  STORE_ATTR               spawn_point_id

 L.3473       958  LOAD_FAST                'sim_proto'
              960  LOAD_ATTR                gameplay_data
              962  LOAD_METHOD              HasField
              964  LOAD_STR                 'spawn_point_option'
              966  CALL_METHOD_1         1  '1 positional argument'
          968_970  POP_JUMP_IF_FALSE   984  'to 984'
              972  LOAD_GLOBAL              SpawnPointOption
              974  LOAD_FAST                'sim_proto'
              976  LOAD_ATTR                gameplay_data
              978  LOAD_ATTR                spawn_point_option
              980  CALL_FUNCTION_1       1  '1 positional argument'
              982  JUMP_FORWARD        988  'to 988'
            984_0  COME_FROM           968  '968'
              984  LOAD_GLOBAL              SpawnPointOption
              986  LOAD_ATTR                SPAWN_ANY_POINT_WITH_CONSTRAINT_TAGS
            988_0  COME_FROM           982  '982'
              988  LOAD_FAST                'self'
              990  STORE_ATTR               spawn_point_option

 L.3474       992  BUILD_LIST_0          0 
              994  LOAD_FAST                'self'
              996  STORE_ATTR               spawner_tags

 L.3476       998  LOAD_FAST                'sim_proto'
             1000  LOAD_METHOD              HasField
             1002  LOAD_STR                 'initial_fitness_value'
             1004  CALL_METHOD_1         1  '1 positional argument'
         1006_1008  POP_JUMP_IF_FALSE  1018  'to 1018'

 L.3477      1010  LOAD_FAST                'sim_proto'
             1012  LOAD_ATTR                initial_fitness_value
             1014  LOAD_FAST                'self'
             1016  STORE_ATTR               _initial_fitness_value
           1018_0  COME_FROM          1006  '1006'

 L.3481      1018  LOAD_FAST                'sim_proto'
             1020  LOAD_ATTR                gameplay_data
             1022  LOAD_METHOD              HasField
             1024  LOAD_STR                 'time_alive'
             1026  CALL_METHOD_1         1  '1 positional argument'
         1028_1030  POP_JUMP_IF_FALSE  1046  'to 1046'

 L.3482      1032  LOAD_GLOBAL              TimeSpan
             1034  LOAD_FAST                'sim_proto'
             1036  LOAD_ATTR                gameplay_data
             1038  LOAD_ATTR                time_alive
             1040  CALL_FUNCTION_1       1  '1 positional argument'
             1042  STORE_FAST               'time_alive'
             1044  JUMP_FORWARD       1050  'to 1050'
           1046_0  COME_FROM          1028  '1028'

 L.3484      1046  LOAD_CONST               None
             1048  STORE_FAST               'time_alive'
           1050_0  COME_FROM          1044  '1044'

 L.3485      1050  LOAD_FAST                'self'
             1052  LOAD_METHOD              load_time_alive
             1054  LOAD_FAST                'time_alive'
             1056  CALL_METHOD_1         1  '1 positional argument'
             1058  POP_TOP          

 L.3487      1060  SETUP_LOOP         1098  'to 1098'
             1062  LOAD_FAST                'sim_proto'
             1064  LOAD_ATTR                gameplay_data
             1066  LOAD_ATTR                spawner_tags
             1068  GET_ITER         
             1070  FOR_ITER           1096  'to 1096'
             1072  STORE_FAST               'spawner_tag'

 L.3488      1074  LOAD_FAST                'self'
             1076  LOAD_ATTR                spawner_tags
             1078  LOAD_METHOD              append
             1080  LOAD_GLOBAL              tag
             1082  LOAD_METHOD              Tag
             1084  LOAD_FAST                'spawner_tag'
             1086  CALL_METHOD_1         1  '1 positional argument'
             1088  CALL_METHOD_1         1  '1 positional argument'
             1090  POP_TOP          
         1092_1094  JUMP_BACK          1070  'to 1070'
             1096  POP_BLOCK        
           1098_0  COME_FROM_LOOP     1060  '1060'

 L.3490      1098  SETUP_FINALLY      1168  'to 1168'

 L.3491      1100  LOAD_CONST               True
             1102  LOAD_FAST                'self'
             1104  LOAD_ATTR                Buffs
             1106  STORE_ATTR               load_in_progress

 L.3495      1108  LOAD_CONST               True
             1110  LOAD_FAST                'self'
             1112  LOAD_ATTR                commodity_tracker
             1114  STORE_ATTR               load_in_progress

 L.3499      1116  LOAD_FAST                'self'
             1118  LOAD_METHOD              on_base_characteristic_changed
             1120  CALL_METHOD_0         0  '0 positional arguments'
             1122  POP_TOP          

 L.3501      1124  LOAD_GLOBAL              services
             1126  LOAD_METHOD              relationship_service
             1128  CALL_METHOD_0         0  '0 positional arguments'
             1130  LOAD_METHOD              suppress_client_updates_context_manager
             1132  CALL_METHOD_0         0  '0 positional arguments'
             1134  SETUP_WITH         1158  'to 1158'
             1136  POP_TOP          

 L.3502      1138  LOAD_FAST                'self'
             1140  LOAD_ATTR                _trait_tracker
             1142  LOAD_METHOD              load
             1144  LOAD_FAST                'sim_attribute_data'
             1146  LOAD_ATTR                trait_tracker
             1148  LOAD_FAST                'skip_load'
             1150  CALL_METHOD_2         2  '2 positional arguments'
             1152  POP_TOP          
             1154  POP_BLOCK        
             1156  LOAD_CONST               None
           1158_0  COME_FROM_WITH     1134  '1134'
             1158  WITH_CLEANUP_START
             1160  WITH_CLEANUP_FINISH
             1162  END_FINALLY      
             1164  POP_BLOCK        
             1166  LOAD_CONST               None
           1168_0  COME_FROM_FINALLY  1098  '1098'

 L.3504      1168  LOAD_CONST               False
             1170  LOAD_FAST                'self'
             1172  LOAD_ATTR                Buffs
             1174  STORE_ATTR               load_in_progress

 L.3505      1176  LOAD_CONST               False
             1178  LOAD_FAST                'self'
             1180  LOAD_ATTR                commodity_tracker
             1182  STORE_ATTR               load_in_progress
             1184  END_FINALLY      

 L.3507      1186  LOAD_FAST                'self'
             1188  LOAD_METHOD              _create_additional_statistics
             1190  CALL_METHOD_0         0  '0 positional arguments'
             1192  POP_TOP          

 L.3510      1194  LOAD_FAST                'self'
             1196  LOAD_ATTR                _whim_tracker
             1198  LOAD_CONST               None
             1200  COMPARE_OP               is-not
         1202_1204  POP_JUMP_IF_FALSE  1226  'to 1226'

 L.3511      1206  LOAD_FAST                'self'
             1208  LOAD_ATTR                _whim_tracker
             1210  LOAD_ATTR                cache_whim_goal_proto
             1212  LOAD_FAST                'sim_proto'
             1214  LOAD_ATTR                gameplay_data
             1216  LOAD_ATTR                whim_tracker
             1218  LOAD_FAST                'skip_load'
             1220  LOAD_CONST               ('skip_load',)
             1222  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
             1224  POP_TOP          
           1226_0  COME_FROM          1202  '1202'

 L.3514      1226  LOAD_FAST                'self'
             1228  LOAD_ATTR                _satisfaction_tracker
             1230  LOAD_CONST               None
             1232  COMPARE_OP               is-not
         1234_1236  POP_JUMP_IF_FALSE  1258  'to 1258'

 L.3515      1238  LOAD_FAST                'self'
             1240  LOAD_ATTR                _satisfaction_tracker
             1242  LOAD_METHOD              set_satisfaction_points
             1244  LOAD_FAST                'sim_proto'
             1246  LOAD_ATTR                gameplay_data
             1248  LOAD_ATTR                whim_bucks
             1250  LOAD_GLOBAL              SetWhimBucks
             1252  LOAD_ATTR                LOAD
             1254  CALL_METHOD_2         2  '2 positional arguments'
             1256  POP_TOP          
           1258_0  COME_FROM          1234  '1234'

 L.3517      1258  LOAD_FAST                'sim_proto'
             1260  LOAD_METHOD              HasField
             1262  LOAD_STR                 'current_outfit_type'
             1264  CALL_METHOD_1         1  '1 positional argument'
         1266_1268  POP_JUMP_IF_FALSE  1296  'to 1296'

 L.3518      1270  LOAD_FAST                'sim_proto'
             1272  LOAD_ATTR                current_outfit_type
             1274  STORE_FAST               'outfit_type'

 L.3519      1276  LOAD_FAST                'sim_proto'
             1278  LOAD_ATTR                current_outfit_index
             1280  STORE_FAST               'outfit_index'

 L.3520      1282  LOAD_FAST                'self'
             1284  LOAD_METHOD              _set_current_outfit_without_distribution
             1286  LOAD_FAST                'outfit_type'
             1288  LOAD_FAST                'outfit_index'
             1290  BUILD_TUPLE_2         2 
             1292  CALL_METHOD_1         1  '1 positional argument'
             1294  POP_TOP          
           1296_0  COME_FROM          1266  '1266'

 L.3522      1296  LOAD_FAST                'self'
             1298  LOAD_METHOD              _load_inventory
             1300  LOAD_FAST                'sim_proto'
             1302  LOAD_FAST                'skip_load'
             1304  CALL_METHOD_2         2  '2 positional arguments'
             1306  POP_TOP          

 L.3523      1308  LOAD_FAST                'sim_proto'
             1310  LOAD_ATTR                gameplay_data
             1312  LOAD_ATTR                additional_bonus_days
             1314  LOAD_FAST                'self'
             1316  STORE_ATTR               _additional_bonus_days

 L.3524      1318  LOAD_FAST                'self'
             1320  LOAD_METHOD              load_favorite
             1322  LOAD_FAST                'sim_proto'
             1324  LOAD_ATTR                gameplay_data
             1326  LOAD_ATTR                favorite_data
             1328  CALL_METHOD_1         1  '1 positional argument'
             1330  POP_TOP          

 L.3528      1332  LOAD_FAST                'skip_load'
         1334_1336  POP_JUMP_IF_TRUE   1370  'to 1370'
             1338  LOAD_FAST                'sim_proto'
             1340  LOAD_ATTR                gameplay_data
             1342  LOAD_ATTR                zone_time_stamp
             1344  LOAD_METHOD              HasField
             1346  LOAD_STR                 'time_sim_was_saved'
             1348  CALL_METHOD_1         1  '1 positional argument'
         1350_1352  POP_JUMP_IF_FALSE  1370  'to 1370'

 L.3529      1354  LOAD_GLOBAL              DateAndTime
             1356  LOAD_FAST                'sim_proto'
             1358  LOAD_ATTR                gameplay_data
             1360  LOAD_ATTR                zone_time_stamp
             1362  LOAD_ATTR                time_sim_was_saved
             1364  CALL_FUNCTION_1       1  '1 positional argument'
             1366  LOAD_FAST                'self'
             1368  STORE_ATTR               _time_sim_was_saved
           1370_0  COME_FROM          1350  '1350'
           1370_1  COME_FROM          1334  '1334'

 L.3531      1370  LOAD_FAST                'sim_proto'
             1372  LOAD_ATTR                gameplay_data
             1374  LOAD_ATTR                zone_time_stamp
             1376  LOAD_ATTR                game_time_expire
             1378  LOAD_CONST               0
             1380  COMPARE_OP               !=
         1382_1384  POP_JUMP_IF_FALSE  1398  'to 1398'

 L.3534      1386  LOAD_FAST                'sim_proto'
             1388  LOAD_ATTR                gameplay_data
             1390  LOAD_ATTR                zone_time_stamp
             1392  LOAD_ATTR                game_time_expire
             1394  LOAD_FAST                'self'
             1396  STORE_ATTR               game_time_bring_home
           1398_0  COME_FROM          1382  '1382'

 L.3537      1398  LOAD_FAST                'sim_attribute_data'
         1400_1402  POP_JUMP_IF_FALSE  2290  'to 2290'

 L.3539  1404_1406  SETUP_FINALLY      2274  'to 2274'
         1408_1410  SETUP_EXCEPT       2242  'to 2242'

 L.3540      1412  LOAD_CONST               True
             1414  LOAD_FAST                'self'
             1416  LOAD_ATTR                Buffs
             1418  STORE_ATTR               load_in_progress

 L.3542      1420  LOAD_FAST                'self'
             1422  LOAD_METHOD              get_blacklisted_statistics
             1424  CALL_METHOD_0         0  '0 positional arguments'
             1426  LOAD_FAST                'self'
             1428  STORE_ATTR               _blacklisted_statistics_cache

 L.3545      1430  LOAD_FAST                'self'
             1432  LOAD_ATTR                commodity_tracker
             1434  LOAD_ATTR                load
             1436  LOAD_FAST                'sim_attribute_data'
             1438  LOAD_ATTR                commodity_tracker
             1440  LOAD_ATTR                commodities
             1442  LOAD_FAST                'skip_load'
             1444  LOAD_CONST               False
             1446  LOAD_CONST               ('skip_load', 'update_affordance_cache')
             1448  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
             1450  POP_TOP          

 L.3546      1452  LOAD_FAST                'self'
             1454  LOAD_ATTR                lod
             1456  LOAD_GLOBAL              SimInfoLODLevel
             1458  LOAD_ATTR                BASE
             1460  COMPARE_OP               >
         1462_1464  POP_JUMP_IF_FALSE  1506  'to 1506'

 L.3547      1466  SETUP_LOOP         1506  'to 1506'
             1468  LOAD_GLOBAL              tuple
             1470  LOAD_FAST                'self'
             1472  LOAD_ATTR                commodity_tracker
             1474  CALL_FUNCTION_1       1  '1 positional argument'
             1476  GET_ITER         
           1478_0  COME_FROM          1488  '1488'
             1478  FOR_ITER           1504  'to 1504'
             1480  STORE_FAST               'commodity'

 L.3548      1482  LOAD_FAST                'commodity'
             1484  LOAD_METHOD              has_auto_satisfy_value
             1486  CALL_METHOD_0         0  '0 positional arguments'
         1488_1490  POP_JUMP_IF_FALSE  1478  'to 1478'

 L.3549      1492  LOAD_FAST                'commodity'
             1494  LOAD_METHOD              set_to_auto_satisfy_value
             1496  CALL_METHOD_0         0  '0 positional arguments'
             1498  POP_TOP          
         1500_1502  JUMP_BACK          1478  'to 1478'
             1504  POP_BLOCK        
           1506_0  COME_FROM_LOOP     1466  '1466'
           1506_1  COME_FROM          1462  '1462'

 L.3551      1506  LOAD_FAST                'self'
             1508  LOAD_ATTR                statistic_tracker
             1510  LOAD_ATTR                load
             1512  LOAD_FAST                'sim_attribute_data'
             1514  LOAD_ATTR                statistics_tracker
             1516  LOAD_ATTR                statistics
             1518  LOAD_FAST                'skip_load'
             1520  LOAD_CONST               ('skip_load',)
             1522  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
             1524  POP_TOP          

 L.3553      1526  LOAD_FAST                'self'
             1528  LOAD_ATTR                commodity_tracker
             1530  LOAD_ATTR                load
             1532  LOAD_FAST                'sim_attribute_data'
             1534  LOAD_ATTR                skill_tracker
             1536  LOAD_ATTR                skills
             1538  LOAD_CONST               False
             1540  LOAD_CONST               ('update_affordance_cache',)
             1542  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
             1544  POP_TOP          

 L.3555      1546  LOAD_FAST                'self'
             1548  LOAD_ATTR                commodity_tracker
             1550  LOAD_ATTR                load
             1552  LOAD_FAST                'sim_attribute_data'
             1554  LOAD_ATTR                ranked_statistic_tracker
             1556  LOAD_ATTR                ranked_statistics
             1558  LOAD_CONST               True
             1560  LOAD_CONST               ('update_affordance_cache',)
             1562  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
             1564  POP_TOP          

 L.3557      1566  LOAD_FAST                'self'
             1568  LOAD_ATTR                is_human
         1570_1572  POP_JUMP_IF_FALSE  1588  'to 1588'

 L.3558      1574  LOAD_FAST                'self'
             1576  LOAD_ATTR                trait_statistic_tracker
             1578  LOAD_METHOD              load
             1580  LOAD_FAST                'sim_attribute_data'
             1582  LOAD_ATTR                trait_statistic_tracker
             1584  CALL_METHOD_1         1  '1 positional argument'
             1586  POP_TOP          
           1588_0  COME_FROM          1570  '1570'

 L.3560      1588  LOAD_FAST                'self'
             1590  LOAD_ATTR                _suntan_tracker
             1592  LOAD_METHOD              load
             1594  LOAD_FAST                'sim_attribute_data'
             1596  LOAD_ATTR                suntan_tracker
             1598  CALL_METHOD_1         1  '1 positional argument'
             1600  POP_TOP          

 L.3563      1602  LOAD_LISTCOMP            '<code_object <listcomp>>'
             1604  LOAD_STR                 'SimInfo._load_sim_info.<locals>.<listcomp>'
             1606  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
             1608  LOAD_FAST                'self'
             1610  LOAD_ATTR                commodity_tracker
             1612  LOAD_METHOD              get_all_commodities
             1614  CALL_METHOD_0         0  '0 positional arguments'
             1616  GET_ITER         
             1618  CALL_FUNCTION_1       1  '1 positional argument'
             1620  STORE_FAST               'skills_to_check_for_unlocks'

 L.3564      1622  LOAD_FAST                'skills_to_check_for_unlocks'
         1624_1626  POP_JUMP_IF_FALSE  1644  'to 1644'

 L.3565      1628  LOAD_FAST                'self'
             1630  LOAD_METHOD              _check_skills_for_unlock
             1632  LOAD_FAST                'skills_to_check_for_unlocks'
             1634  LOAD_FAST                'sim_attribute_data'
             1636  LOAD_ATTR                skill_tracker
             1638  LOAD_ATTR                skills
             1640  CALL_METHOD_2         2  '2 positional arguments'
             1642  POP_TOP          
           1644_0  COME_FROM          1624  '1624'

 L.3567      1644  LOAD_FAST                'self'
             1646  LOAD_ATTR                _pregnancy_tracker
             1648  LOAD_METHOD              load
             1650  LOAD_FAST                'sim_attribute_data'
             1652  LOAD_ATTR                pregnancy_tracker
             1654  CALL_METHOD_1         1  '1 positional argument'
             1656  POP_TOP          

 L.3568      1658  LOAD_FAST                'self'
             1660  LOAD_ATTR                appearance_tracker
             1662  LOAD_METHOD              load_appearance_tracker
             1664  LOAD_FAST                'sim_attribute_data'
             1666  LOAD_ATTR                appearance_tracker
             1668  CALL_METHOD_1         1  '1 positional argument'
             1670  POP_TOP          

 L.3570      1672  LOAD_FAST                'sim_attribute_data'
             1674  LOAD_METHOD              HasField
             1676  LOAD_STR                 'sickness_tracker'
             1678  CALL_METHOD_1         1  '1 positional argument'
         1680_1682  POP_JUMP_IF_FALSE  1720  'to 1720'

 L.3572      1684  LOAD_FAST                'self'
             1686  LOAD_ATTR                sickness_tracker
             1688  LOAD_METHOD              load_sickness_tracker_data
             1690  LOAD_FAST                'sim_attribute_data'
             1692  LOAD_ATTR                sickness_tracker
             1694  CALL_METHOD_1         1  '1 positional argument'
             1696  POP_TOP          

 L.3574      1698  LOAD_FAST                'self'
             1700  LOAD_METHOD              has_sickness_tracking
             1702  CALL_METHOD_0         0  '0 positional arguments'
         1704_1706  POP_JUMP_IF_FALSE  1720  'to 1720'

 L.3575      1708  LOAD_FAST                'self'
             1710  LOAD_ATTR                current_sickness
             1712  LOAD_METHOD              on_sim_info_loaded
             1714  LOAD_FAST                'self'
             1716  CALL_METHOD_1         1  '1 positional argument'
             1718  POP_TOP          
           1720_0  COME_FROM          1704  '1704'
           1720_1  COME_FROM          1680  '1680'

 L.3578      1720  LOAD_FAST                'sim_attribute_data'
             1722  LOAD_METHOD              HasField
             1724  LOAD_STR                 'stored_object_info_component'
             1726  CALL_METHOD_1         1  '1 positional argument'
         1728_1730  POP_JUMP_IF_FALSE  1776  'to 1776'

 L.3579      1732  LOAD_GLOBAL              objects
             1734  LOAD_ATTR                components
             1736  LOAD_ATTR                types
             1738  LOAD_ATTR                STORED_OBJECT_INFO_COMPONENT
             1740  STORE_FAST               'component_def'

 L.3580      1742  LOAD_FAST                'self'
             1744  LOAD_METHOD              add_dynamic_component
             1746  LOAD_FAST                'component_def'
             1748  CALL_METHOD_1         1  '1 positional argument'
         1750_1752  POP_JUMP_IF_FALSE  1776  'to 1776'

 L.3581      1754  LOAD_FAST                'self'
             1756  LOAD_METHOD              get_component
             1758  LOAD_FAST                'component_def'
             1760  CALL_METHOD_1         1  '1 positional argument'
             1762  STORE_FAST               'stored_object_info_component'

 L.3582      1764  LOAD_FAST                'stored_object_info_component'
             1766  LOAD_METHOD              load_stored_object_info
             1768  LOAD_FAST                'sim_attribute_data'
             1770  LOAD_ATTR                stored_object_info_component
             1772  CALL_METHOD_1         1  '1 positional argument'
             1774  POP_TOP          
           1776_0  COME_FROM          1750  '1750'
           1776_1  COME_FROM          1728  '1728'

 L.3585      1776  SETUP_LOOP         1810  'to 1810'
             1778  LOAD_FAST                'sim_attribute_data'
             1780  LOAD_ATTR                object_preferences
             1782  LOAD_ATTR                preferences
             1784  GET_ITER         
             1786  FOR_ITER           1808  'to 1808'
             1788  STORE_FAST               'entry'

 L.3586      1790  LOAD_FAST                'entry'
             1792  LOAD_ATTR                object_id
             1794  LOAD_FAST                'self'
             1796  LOAD_ATTR                _autonomy_scoring_preferences
             1798  LOAD_FAST                'entry'
             1800  LOAD_ATTR                tag
             1802  STORE_SUBSCR     
         1804_1806  JUMP_BACK          1786  'to 1786'
             1808  POP_BLOCK        
           1810_0  COME_FROM_LOOP     1776  '1776'

 L.3588      1810  SETUP_LOOP         1844  'to 1844'
             1812  LOAD_FAST                'sim_attribute_data'
             1814  LOAD_ATTR                object_ownership
             1816  LOAD_ATTR                owned_object
             1818  GET_ITER         
             1820  FOR_ITER           1842  'to 1842'
             1822  STORE_FAST               'entry'

 L.3589      1824  LOAD_FAST                'entry'
             1826  LOAD_ATTR                object_id
             1828  LOAD_FAST                'self'
             1830  LOAD_ATTR                _autonomy_use_preferences
             1832  LOAD_FAST                'entry'
             1834  LOAD_ATTR                tag
             1836  STORE_SUBSCR     
         1838_1840  JUMP_BACK          1820  'to 1820'
             1842  POP_BLOCK        
           1844_0  COME_FROM_LOOP     1810  '1810'

 L.3590      1844  LOAD_FAST                'self'
             1846  LOAD_ATTR                _career_tracker
             1848  LOAD_ATTR                load
             1850  LOAD_FAST                'sim_attribute_data'
             1852  LOAD_ATTR                sim_careers
             1854  LOAD_FAST                'skip_load'
             1856  LOAD_CONST               ('skip_load',)
             1858  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
             1860  POP_TOP          

 L.3591      1862  LOAD_FAST                'self'
             1864  LOAD_ATTR                _adventure_tracker
             1866  LOAD_CONST               None
             1868  COMPARE_OP               is-not
         1870_1872  POP_JUMP_IF_FALSE  1888  'to 1888'

 L.3592      1874  LOAD_FAST                'self'
             1876  LOAD_ATTR                _adventure_tracker
             1878  LOAD_METHOD              load
             1880  LOAD_FAST                'sim_attribute_data'
             1882  LOAD_ATTR                adventure_tracker
             1884  CALL_METHOD_1         1  '1 positional argument'
             1886  POP_TOP          
           1888_0  COME_FROM          1870  '1870'

 L.3593      1888  LOAD_FAST                'self'
             1890  LOAD_ATTR                _notebook_tracker
             1892  LOAD_CONST               None
             1894  COMPARE_OP               is-not
         1896_1898  POP_JUMP_IF_FALSE  1914  'to 1914'

 L.3594      1900  LOAD_FAST                'self'
             1902  LOAD_ATTR                _notebook_tracker
             1904  LOAD_METHOD              load_notebook
             1906  LOAD_FAST                'sim_attribute_data'
             1908  LOAD_ATTR                notebook_tracker
             1910  CALL_METHOD_1         1  '1 positional argument'
             1912  POP_TOP          
           1914_0  COME_FROM          1896  '1896'

 L.3595      1914  LOAD_FAST                'self'
             1916  LOAD_ATTR                _royalty_tracker
             1918  LOAD_CONST               None
             1920  COMPARE_OP               is-not
         1922_1924  POP_JUMP_IF_FALSE  1946  'to 1946'
             1926  LOAD_FAST                'skip_load'
         1928_1930  POP_JUMP_IF_TRUE   1946  'to 1946'

 L.3596      1932  LOAD_FAST                'self'
             1934  LOAD_ATTR                _royalty_tracker
             1936  LOAD_METHOD              load
             1938  LOAD_FAST                'sim_attribute_data'
             1940  LOAD_ATTR                royalty_tracker
             1942  CALL_METHOD_1         1  '1 positional argument'
             1944  POP_TOP          
           1946_0  COME_FROM          1928  '1928'
           1946_1  COME_FROM          1922  '1922'

 L.3597      1946  LOAD_FAST                'self'
             1948  LOAD_ATTR                _unlock_tracker
             1950  LOAD_CONST               None
             1952  COMPARE_OP               is-not
         1954_1956  POP_JUMP_IF_FALSE  1988  'to 1988'

 L.3598      1958  LOAD_FAST                'skip_load'
         1960_1962  JUMP_IF_FALSE_OR_POP  1968  'to 1968'
             1964  LOAD_FAST                'is_clone'
             1966  UNARY_NOT        
           1968_0  COME_FROM          1960  '1960'
             1968  STORE_FAST               'skip_load'

 L.3599      1970  LOAD_FAST                'self'
             1972  LOAD_ATTR                _unlock_tracker
             1974  LOAD_ATTR                load_unlock
             1976  LOAD_FAST                'sim_attribute_data'
             1978  LOAD_ATTR                unlock_tracker
             1980  LOAD_FAST                'skip_load'
             1982  LOAD_CONST               ('skip_load',)
             1984  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
             1986  POP_TOP          
           1988_0  COME_FROM          1954  '1954'

 L.3600      1988  LOAD_FAST                'self'
             1990  LOAD_ATTR                _relic_tracker
             1992  LOAD_CONST               None
             1994  COMPARE_OP               is-not
         1996_1998  POP_JUMP_IF_FALSE  2020  'to 2020'
             2000  LOAD_FAST                'skip_load'
         2002_2004  POP_JUMP_IF_TRUE   2020  'to 2020'

 L.3601      2006  LOAD_FAST                'self'
             2008  LOAD_ATTR                _relic_tracker
             2010  LOAD_METHOD              load
             2012  LOAD_FAST                'sim_attribute_data'
             2014  LOAD_ATTR                relic_tracker
             2016  CALL_METHOD_1         1  '1 positional argument'
             2018  POP_TOP          
           2020_0  COME_FROM          2002  '2002'
           2020_1  COME_FROM          1996  '1996'

 L.3602      2020  LOAD_FAST                'self'
             2022  LOAD_ATTR                _lifestyle_brand_tracker
             2024  LOAD_CONST               None
             2026  COMPARE_OP               is-not
         2028_2030  POP_JUMP_IF_FALSE  2052  'to 2052'
             2032  LOAD_FAST                'skip_load'
         2034_2036  POP_JUMP_IF_TRUE   2052  'to 2052'

 L.3603      2038  LOAD_FAST                'self'
             2040  LOAD_ATTR                _lifestyle_brand_tracker
             2042  LOAD_METHOD              load
             2044  LOAD_FAST                'sim_attribute_data'
             2046  LOAD_ATTR                lifestyle_brand_tracker
             2048  CALL_METHOD_1         1  '1 positional argument'
             2050  POP_TOP          
           2052_0  COME_FROM          2034  '2034'
           2052_1  COME_FROM          2028  '2028'

 L.3604      2052  LOAD_FAST                'self'
             2054  LOAD_ATTR                _favorites_tracker
             2056  LOAD_CONST               None
             2058  COMPARE_OP               is-not
         2060_2062  POP_JUMP_IF_FALSE  2084  'to 2084'
             2064  LOAD_FAST                'skip_load'
         2066_2068  POP_JUMP_IF_TRUE   2084  'to 2084'

 L.3605      2070  LOAD_FAST                'self'
             2072  LOAD_ATTR                _favorites_tracker
             2074  LOAD_METHOD              load
             2076  LOAD_FAST                'sim_attribute_data'
             2078  LOAD_ATTR                favorites_tracker
             2080  CALL_METHOD_1         1  '1 positional argument'
             2082  POP_TOP          
           2084_0  COME_FROM          2066  '2066'
           2084_1  COME_FROM          2060  '2060'

 L.3606      2084  LOAD_FAST                'self'
             2086  LOAD_ATTR                _degree_tracker
             2088  LOAD_CONST               None
             2090  COMPARE_OP               is-not
         2092_2094  POP_JUMP_IF_FALSE  2110  'to 2110'

 L.3607      2096  LOAD_FAST                'self'
             2098  LOAD_ATTR                degree_tracker
             2100  LOAD_METHOD              load
             2102  LOAD_FAST                'sim_attribute_data'
             2104  LOAD_ATTR                degree_tracker
             2106  CALL_METHOD_1         1  '1 positional argument'
             2108  POP_TOP          
           2110_0  COME_FROM          2092  '2092'

 L.3608      2110  LOAD_FAST                'self'
             2112  LOAD_ATTR                _organization_tracker
             2114  LOAD_CONST               None
             2116  COMPARE_OP               is-not
         2118_2120  POP_JUMP_IF_FALSE  2142  'to 2142'
             2122  LOAD_FAST                'skip_load'
         2124_2126  POP_JUMP_IF_TRUE   2142  'to 2142'

 L.3609      2128  LOAD_FAST                'self'
             2130  LOAD_ATTR                _organization_tracker
             2132  LOAD_METHOD              load
             2134  LOAD_FAST                'sim_attribute_data'
             2136  LOAD_ATTR                organization_tracker
             2138  CALL_METHOD_1         1  '1 positional argument'
             2140  POP_TOP          
           2142_0  COME_FROM          2124  '2124'
           2142_1  COME_FROM          2118  '2118'

 L.3610      2142  LOAD_FAST                'self'
             2144  LOAD_ATTR                _fixup_tracker
             2146  LOAD_CONST               None
             2148  COMPARE_OP               is-not
         2150_2152  POP_JUMP_IF_FALSE  2174  'to 2174'
             2154  LOAD_FAST                'skip_load'
         2156_2158  POP_JUMP_IF_TRUE   2174  'to 2174'

 L.3611      2160  LOAD_FAST                'self'
             2162  LOAD_ATTR                _fixup_tracker
             2164  LOAD_METHOD              load
             2166  LOAD_FAST                'sim_attribute_data'
             2168  LOAD_ATTR                fixup_tracker
             2170  CALL_METHOD_1         1  '1 positional argument'
             2172  POP_TOP          
           2174_0  COME_FROM          2156  '2156'
           2174_1  COME_FROM          2150  '2150'

 L.3612      2174  LOAD_FAST                'self'
             2176  LOAD_ATTR                _story_progression_tracker
             2178  LOAD_CONST               None
             2180  COMPARE_OP               is-not
         2182_2184  POP_JUMP_IF_FALSE  2206  'to 2206'
             2186  LOAD_FAST                'skip_load'
         2188_2190  POP_JUMP_IF_TRUE   2206  'to 2206'

 L.3613      2192  LOAD_FAST                'self'
             2194  LOAD_ATTR                _story_progression_tracker
             2196  LOAD_METHOD              load
             2198  LOAD_FAST                'sim_attribute_data'
             2200  LOAD_ATTR                story_progression_tracker
             2202  CALL_METHOD_1         1  '1 positional argument'
             2204  POP_TOP          
           2206_0  COME_FROM          2188  '2188'
           2206_1  COME_FROM          2182  '2182'

 L.3614      2206  LOAD_FAST                'self'
             2208  LOAD_ATTR                _lunar_effect_tracker
             2210  LOAD_CONST               None
             2212  COMPARE_OP               is-not
         2214_2216  POP_JUMP_IF_FALSE  2238  'to 2238'
             2218  LOAD_FAST                'skip_load'
         2220_2222  POP_JUMP_IF_TRUE   2238  'to 2238'

 L.3615      2224  LOAD_FAST                'self'
             2226  LOAD_ATTR                _lunar_effect_tracker
             2228  LOAD_METHOD              load_lunar_effects
             2230  LOAD_FAST                'sim_attribute_data'
             2232  LOAD_ATTR                lunar_effect_tracker
             2234  CALL_METHOD_1         1  '1 positional argument'
             2236  POP_TOP          
           2238_0  COME_FROM          2220  '2220'
           2238_1  COME_FROM          2214  '2214'
             2238  POP_BLOCK        
             2240  JUMP_FORWARD       2270  'to 2270'
           2242_0  COME_FROM_EXCEPT   1408  '1408'

 L.3617      2242  POP_TOP          
             2244  POP_TOP          
             2246  POP_TOP          

 L.3618      2248  LOAD_GLOBAL              logger
             2250  LOAD_METHOD              exception
             2252  LOAD_STR                 'Failed to load attributes for sim {}.'
             2254  LOAD_FAST                'self'
             2256  LOAD_ATTR                _base
             2258  LOAD_ATTR                first_name
             2260  CALL_METHOD_2         2  '2 positional arguments'
             2262  POP_TOP          
             2264  POP_EXCEPT       
             2266  JUMP_FORWARD       2270  'to 2270'
             2268  END_FINALLY      
           2270_0  COME_FROM          2266  '2266'
           2270_1  COME_FROM          2240  '2240'
             2270  POP_BLOCK        
             2272  LOAD_CONST               None
           2274_0  COME_FROM_FINALLY  1404  '1404'

 L.3620      2274  LOAD_CONST               None
             2276  LOAD_FAST                'self'
             2278  STORE_ATTR               _blacklisted_statistics_cache

 L.3621      2280  LOAD_CONST               False
             2282  LOAD_FAST                'self'
             2284  LOAD_ATTR                Buffs
             2286  STORE_ATTR               load_in_progress
             2288  END_FINALLY      
           2290_0  COME_FROM          1400  '1400'

 L.3626      2290  LOAD_FAST                'self'
             2292  LOAD_METHOD              _setup_fitness_commodities
             2294  CALL_METHOD_0         0  '0 positional arguments'
             2296  POP_TOP          

 L.3632      2298  LOAD_FAST                'self'
             2300  LOAD_ATTR                _trait_tracker
             2302  LOAD_METHOD              fixup_gender_preference_statistics
             2304  CALL_METHOD_0         0  '0 positional arguments'
             2306  POP_TOP          

 L.3634      2308  LOAD_FAST                'self'
             2310  LOAD_METHOD              _add_gender_preference_listeners
             2312  CALL_METHOD_0         0  '0 positional arguments'
             2314  POP_TOP          

 L.3636      2316  LOAD_FAST                'skip_load'
         2318_2320  POP_JUMP_IF_TRUE   2458  'to 2458'

 L.3637      2322  LOAD_FAST                'sim_proto'
             2324  LOAD_ATTR                gameplay_data
             2326  LOAD_METHOD              HasField
             2328  LOAD_STR                 'location'
             2330  CALL_METHOD_1         1  '1 positional argument'
         2332_2334  POP_JUMP_IF_FALSE  2458  'to 2458'

 L.3638      2336  LOAD_FAST                'self'
             2338  LOAD_ATTR                _serialization_option
             2340  LOAD_GLOBAL              SimSerializationOption
             2342  LOAD_ATTR                UNDECLARED
             2344  COMPARE_OP               !=
         2346_2348  POP_JUMP_IF_FALSE  2458  'to 2458'

 L.3639      2350  LOAD_GLOBAL              sims4
             2352  LOAD_ATTR                math
             2354  LOAD_METHOD              Transform
             2356  CALL_METHOD_0         0  '0 positional arguments'
             2358  STORE_FAST               'world_coord'

 L.3640      2360  LOAD_FAST                'sim_proto'
             2362  LOAD_ATTR                gameplay_data
             2364  LOAD_ATTR                location
             2366  STORE_FAST               'location'

 L.3641      2368  LOAD_GLOBAL              sims4
             2370  LOAD_ATTR                math
             2372  LOAD_METHOD              Vector3
             2374  LOAD_FAST                'location'
             2376  LOAD_ATTR                x

 L.3642      2378  LOAD_FAST                'location'
             2380  LOAD_ATTR                y

 L.3643      2382  LOAD_FAST                'location'
             2384  LOAD_ATTR                z
             2386  CALL_METHOD_3         3  '3 positional arguments'
             2388  LOAD_FAST                'world_coord'
             2390  STORE_ATTR               translation

 L.3645      2392  LOAD_GLOBAL              sims4
             2394  LOAD_ATTR                math
             2396  LOAD_METHOD              Quaternion
             2398  LOAD_FAST                'location'
             2400  LOAD_ATTR                rot_x

 L.3646      2402  LOAD_FAST                'location'
             2404  LOAD_ATTR                rot_y

 L.3647      2406  LOAD_FAST                'location'
         2408_2410  LOAD_ATTR                rot_z

 L.3648      2412  LOAD_FAST                'location'
         2414_2416  LOAD_ATTR                rot_w
             2418  CALL_METHOD_4         4  '4 positional arguments'
             2420  LOAD_FAST                'world_coord'
         2422_2424  STORE_ATTR               orientation

 L.3649      2426  LOAD_FAST                'world_coord'
             2428  LOAD_FAST                'self'
         2430_2432  STORE_ATTR               _transform_on_load

 L.3650      2434  LOAD_FAST                'location'
         2436_2438  LOAD_ATTR                level
             2440  LOAD_FAST                'self'
         2442_2444  STORE_ATTR               _level_on_load

 L.3651      2446  LOAD_FAST                'location'
         2448_2450  LOAD_ATTR                surface_id
             2452  LOAD_FAST                'self'
         2454_2456  STORE_ATTR               _surface_id_on_load
           2458_0  COME_FROM          2346  '2346'
           2458_1  COME_FROM          2332  '2332'
           2458_2  COME_FROM          2318  '2318'

 L.3653  2458_2460  LOAD_GLOBAL              gameplay_serialization
         2462_2464  LOAD_METHOD              SuperInteractionSaveState
             2466  CALL_METHOD_0         0  '0 positional arguments'
             2468  LOAD_FAST                'self'
         2470_2472  STORE_ATTR               _si_state

 L.3654      2474  LOAD_FAST                'sim_proto'
             2476  LOAD_ATTR                gameplay_data
             2478  LOAD_METHOD              HasField
             2480  LOAD_STR                 'interaction_state'
             2482  CALL_METHOD_1         1  '1 positional argument'
         2484_2486  POP_JUMP_IF_FALSE  2518  'to 2518'

 L.3660      2488  LOAD_CONST               True
             2490  LOAD_FAST                'self'
         2492_2494  STORE_ATTR               _has_loaded_si_state

 L.3661      2496  LOAD_FAST                'self'
         2498_2500  LOAD_ATTR                _si_state
         2502_2504  LOAD_METHOD              MergeFrom
             2506  LOAD_FAST                'sim_proto'
             2508  LOAD_ATTR                gameplay_data
         2510_2512  LOAD_ATTR                interaction_state
             2514  CALL_METHOD_1         1  '1 positional argument'
             2516  POP_TOP          
           2518_0  COME_FROM          2484  '2484'

 L.3663      2518  LOAD_GLOBAL              services
             2520  LOAD_METHOD              sim_info_manager
             2522  CALL_METHOD_0         0  '0 positional arguments'
             2524  LOAD_METHOD              add_sim_info_if_not_in_manager
             2526  LOAD_FAST                'self'
             2528  CALL_METHOD_1         1  '1 positional argument'
             2530  POP_TOP          

 L.3665  2532_2534  LOAD_GLOBAL              len
             2536  LOAD_FAST                'sim_proto'
             2538  LOAD_ATTR                gameplay_data
         2540_2542  LOAD_ATTR                bucks_data
             2544  CALL_FUNCTION_1       1  '1 positional argument'
             2546  LOAD_CONST               0
             2548  COMPARE_OP               >
         2550_2552  POP_JUMP_IF_FALSE  2582  'to 2582'

 L.3666      2554  LOAD_FAST                'self'
         2556_2558  LOAD_ATTR                get_bucks_tracker
             2560  LOAD_CONST               True
             2562  LOAD_CONST               ('add_if_none',)
             2564  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
             2566  STORE_FAST               'bucks_tracker'

 L.3667      2568  LOAD_FAST                'bucks_tracker'
         2570_2572  LOAD_METHOD              load_data
             2574  LOAD_FAST                'sim_proto'
             2576  LOAD_ATTR                gameplay_data
             2578  CALL_METHOD_1         1  '1 positional argument'
             2580  POP_TOP          
           2582_0  COME_FROM          2550  '2550'

 L.3669      2582  LOAD_FAST                'sim_proto'
             2584  LOAD_ATTR                gameplay_data
             2586  LOAD_METHOD              HasField
             2588  LOAD_STR                 'gameplay_options'
             2590  CALL_METHOD_1         1  '1 positional argument'
         2592_2594  POP_JUMP_IF_FALSE  2696  'to 2696'

 L.3670      2596  LOAD_FAST                'sim_proto'
             2598  LOAD_ATTR                gameplay_data
         2600_2602  LOAD_ATTR                gameplay_options
             2604  LOAD_FAST                'self'
         2606_2608  STORE_ATTR               _gameplay_options

 L.3673      2610  LOAD_FAST                'self'
         2612_2614  LOAD_METHOD              get_gameplay_option
         2616_2618  LOAD_GLOBAL              SimInfoGameplayOptions
         2620_2622  LOAD_ATTR                FORCE_CURRENT_ALLOW_FAME_SETTING
             2624  CALL_METHOD_1         1  '1 positional argument'
         2626_2628  POP_JUMP_IF_FALSE  2660  'to 2660'

 L.3674      2630  LOAD_FAST                'self'
         2632_2634  LOAD_METHOD              get_gameplay_option
         2636_2638  LOAD_GLOBAL              SimInfoGameplayOptions
         2640_2642  LOAD_ATTR                ALLOW_FAME
             2644  CALL_METHOD_1         1  '1 positional argument'
         2646_2648  POP_JUMP_IF_TRUE   2660  'to 2660'

 L.3676      2650  LOAD_CONST               False
             2652  LOAD_FAST                'self'
         2654_2656  STORE_ATTR               allow_fame
             2658  JUMP_FORWARD       2696  'to 2696'
           2660_0  COME_FROM          2646  '2646'
           2660_1  COME_FROM          2626  '2626'

 L.3677      2660  LOAD_FAST                'self'
         2662_2664  LOAD_METHOD              get_gameplay_option
         2666_2668  LOAD_GLOBAL              SimInfoGameplayOptions
         2670_2672  LOAD_ATTR                FREEZE_FAME
             2674  CALL_METHOD_1         1  '1 positional argument'
         2676_2678  POP_JUMP_IF_FALSE  2696  'to 2696'

 L.3678      2680  LOAD_FAST                'self'
         2682_2684  LOAD_ATTR                set_freeze_fame
             2686  LOAD_CONST               True
             2688  LOAD_CONST               True
             2690  LOAD_CONST               ('force',)
             2692  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
             2694  POP_TOP          
           2696_0  COME_FROM          2676  '2676'
           2696_1  COME_FROM          2658  '2658'
           2696_2  COME_FROM          2592  '2592'

 L.3680      2696  SETUP_LOOP         2730  'to 2730'
             2698  LOAD_FAST                'sim_proto'
             2700  LOAD_ATTR                gameplay_data
         2702_2704  LOAD_ATTR                squad_members
             2706  GET_ITER         
             2708  FOR_ITER           2728  'to 2728'
             2710  STORE_FAST               'squad_member_id'

 L.3681      2712  LOAD_FAST                'self'
         2714_2716  LOAD_METHOD              add_sim_info_id_to_squad
             2718  LOAD_FAST                'squad_member_id'
             2720  CALL_METHOD_1         1  '1 positional argument'
             2722  POP_TOP          
         2724_2726  JUMP_BACK          2708  'to 2708'
             2728  POP_BLOCK        
           2730_0  COME_FROM_LOOP     2696  '2696'

 L.3683      2730  LOAD_FAST                'sim_proto'
             2732  LOAD_ATTR                gameplay_data
             2734  LOAD_METHOD              HasField
             2736  LOAD_STR                 'vehicle_id'
             2738  CALL_METHOD_1         1  '1 positional argument'
         2740_2742  POP_JUMP_IF_FALSE  2758  'to 2758'

 L.3684      2744  LOAD_FAST                'sim_proto'
             2746  LOAD_ATTR                gameplay_data
         2748_2750  LOAD_ATTR                vehicle_id
             2752  LOAD_FAST                'self'
         2754_2756  STORE_ATTR               _vehicle_id
           2758_0  COME_FROM          2740  '2740'

 L.3686      2758  LOAD_FAST                'self'
         2760_2762  LOAD_METHOD              _post_load
             2764  CALL_METHOD_0         0  '0 positional arguments'
             2766  POP_TOP          

Parse error at or near `SETUP_LOOP' instruction at offset 2696

    def _get_time_to_go_home(self):
        random_minutes = PersistenceTuning.MINUTES_STAY_ON_LOT_BEFORE_GO_HOME.random_int()
        random_minutes_time_span = date_and_time.create_time_span(minutes=random_minutes)
        return services.time_service().sim_now + random_minutes_time_span

    def get_blacklisted_statistics(self):
        if self._blacklisted_statistics_cache is not None:
            return self._blacklisted_statistics_cache
        blacklisted_statistics = set()
        for trait in self.trait_tracker:
            blacklisted_statistics.update(trait.initial_commodities_blacklist)

        return tuple(blacklisted_statistics)

    def _initialize_sim_info_trackers(self, lod):
        for tracker_attr, tracker_type in SimInfo.SIM_INFO_TRACKERS.items():
            if not any((is_available_pack(pack) for pack in tracker_type.required_packs)):
                continue
            if tracker_type.is_valid_for_lod(lod):
                setattr(self, tracker_attr, tracker_type(self))

    def report_telemetry(self, report_source_string):
        with telemetry_helper.begin_hook(simulation_error_writer, TELEMETRY_SIMULATION_ERROR, sim_info=self, valid_for_npc=True) as (hook):
            hook.write_int('smid', self.sim_id)
            hook.write_string('snam', self.full_name)
            hook.write_string('hoid', str(self._household_id))
            hook.write_int('crid', self._sim_creation_path)
            self.creation_source.write_creation_source(hook)
            hook.write_string('csrc', report_source_string)

    def load_from_resource(self, resource_key):
        super().load_from_resource(resource_key)
        self._get_fit_fat()
        self._setup_fitness_commodities()
        aspiration_manager = services.get_instance_manager(sims4.resources.Types.ASPIRATION_TRACK)
        aspiration = aspiration_manager.get(self._base.aspiration_id)
        if aspiration is not None:
            if aspiration.is_available():
                self.primary_aspiration = aspiration
        for trait in tuple(self.trait_tracker):
            if aspiration is None:
                if trait.is_aspiration_trait:
                    continue
            self.remove_trait(trait)

        trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
        for trait_id in self._base.base_trait_ids:
            trait = trait_manager.get(trait_id)
            if trait is not None:
                self.add_trait(trait)

        self._update_age_trait(self.age)
        self.on_base_characteristic_changed()

    def push_to_relgraph(self):
        if RelgraphService.RELGRAPH_ENABLED:
            self._base.push_to_relgraph()

    def _load_inventory(self, sim_proto, skip_load):
        inventory_data = serialization.ObjectList()
        if not skip_load:
            inventory_data.MergeFrom(sim_proto.inventory)
        if sim_proto.gameplay_data.HasField('old_household_id'):
            old_household_id = sim_proto.gameplay_data.old_household_id
            if old_household_id != self._household_id:
                for inv_obj in inventory_data.objects:
                    if inv_obj.owner_id == old_household_id:
                        inv_obj.owner_id = self._household_id

        self._inventory_data = inventory_data

    def apply_fixup_actions(self, fixup_source):
        for trait in tuple(self.trait_tracker):
            if trait.should_apply_fixup_actions(fixup_source):
                trait.apply_fixup_actions(self)
                self.remove_trait(trait)

        if self.fixup_tracker is not None:
            self.fixup_tracker.apply_all_appropriate_fixups(fixup_source)

    def fixup_inventory(self):
        if self.inventory_data is None:
            return
        pruned_inventory = serialization.ObjectList()
        object_manager = services.object_manager()
        count = 0
        for inv_obj in self.inventory_data.objects:
            if not self.is_player_sim:
                def_id = build_buy.get_vetted_object_defn_guid(inv_obj.object_id, inv_obj.guid or inv_obj.type)
                if def_id is None:
                    count += 1
                    continue
                if InventoryItemComponent.should_item_be_removed_from_inventory(def_id):
                    count += 1
                    continue
            attribute_data = protocols.PersistenceMaster()
            attribute_data.ParseFromString(inv_obj.attributes)
            if object_manager.has_inventory_item_failed_claiming(inv_obj.object_id, attribute_data.data):
                count += 1
                continue
            pruned_inventory.objects.append(inv_obj)

        if count > 0:
            logger.info('Inventory Purge: NPC {} lost {} objects from inventory.', str(self), count)
        self.inventory_data = pruned_inventory

    def _check_skills_for_unlock(self, skills, commodity_loading_data):
        open_set = set(skills)
        closed_set = set()
        while open_set:
            current_skill = open_set.pop()
            closed_set.add(current_skill)
            if not current_skill.reached_max_level:
                continue
            for skill_to_unlock in current_skill.skill_unlocks_on_max:
                if skill_to_unlock not in closed_set:
                    self.commodity_tracker.add_statistic(skill_to_unlock, force_add=True)
                    skill_data_object = [sdo for sdo in commodity_loading_data if sdo.name_hash == skill_to_unlock.guid64]
                    self.commodity_tracker.load(skill_data_object)
                    open_set.add(skill_to_unlock)

    def _post_load(self):
        self.refresh_age_settings()
        self.publish_all_commodities()
        services.sim_info_manager().try_set_sim_fame_option_to_global_option(self)

    def on_all_sim_infos_loaded(self):
        if self.lod == SimInfoLODLevel.MINIMUM:
            return
        self.career_tracker.remove_invalid_careers()
        if self.familiar_tracker is not None:
            self.familiar_tracker.on_all_sim_infos_loaded()

    def refresh_age_settings(self):
        aging_service = services.get_aging_service()
        self._auto_aging_enabled = aging_service.is_aging_enabled_for_sim_info(self)
        self._age_speed_setting = aging_service.aging_speed
        self.update_age_callbacks()

    def on_zone_unload(self):
        if self.lod == SimInfoLODLevel.MINIMUM:
            return
        else:
            if game_services.service_manager.is_traveling:
                self._save_for_travel()
            if self.body_type_level_tracker is not None:
                self.body_type_level_tracker.on_zone_unload()
            self._career_tracker.on_zone_unload()
            if self._aspiration_tracker is not None:
                self._aspiration_tracker.on_zone_unload()
            if self.whim_tracker is not None:
                self.whim_tracker.on_zone_unload()
            self.trait_tracker.on_zone_unload()
            if self.Buffs is not None:
                self.Buffs.on_zone_unload()
            if game_services.service_manager.is_traveling:
                self.commodity_tracker.remove_statistics_on_travel()
                self.statistic_tracker.remove_statistics_on_travel()
                self.static_commodity_tracker.remove_statistics_on_travel()
                if self.away_action_tracker is not None:
                    self.away_action_tracker.stop_current_away_action()

    def on_zone_load(self):
        if self.lod == SimInfoLODLevel.MINIMUM:
            return
        else:
            self.startup_sim_location = self._get_startup_location()
            if self.Buffs is not None:
                self.Buffs.on_zone_load()
            if self._aspiration_tracker is not None:
                self._aspiration_tracker.on_zone_load()
            self._career_tracker.on_zone_load()
            if self._bucks_tracker is not None:
                self._bucks_tracker.on_zone_load()
            if self._sickness_tracker is not None and self.has_sickness_tracking():
                self.current_sickness.on_zone_load(self)
        if self.commodity_tracker is not None:
            self.commodity_tracker.on_zone_load()
        if self.organization_tracker is not None:
            self.organization_tracker.on_zone_load()
        if self.story_progression_tracker is not None:
            self.story_progression_tracker.on_zone_load()
        if self.body_type_level_tracker is not None:
            self.body_type_level_tracker.on_zone_load()
        self.trait_tracker.on_zone_load()

    def _get_startup_location(self):
        current_zone = services.current_zone()
        if self._transform_on_load is not None:
            if self._level_on_load is not None:
                if current_zone.id == self._zone_id or current_zone.open_street_id == self._world_id:
                    routing_surface = routing.SurfaceIdentifier(current_zone.id, self._level_on_load, routing.SurfaceType(self._surface_id_on_load))
                    return sims4.math.Location(self._transform_on_load, routing_surface)

    def on_all_households_and_sim_infos_loaded(self):
        if self.lod == SimInfoLODLevel.MINIMUM:
            return
        else:
            if self._bucks_tracker is not None:
                self._bucks_tracker.on_all_households_and_sim_infos_loaded()
            self._pregnancy_tracker.refresh_pregnancy_data()
            self.premade_sim_template_id or self.update_school_data()
        if self._trait_tracker is not None:
            self._trait_tracker.on_all_households_and_sim_infos_loaded()

    def update_school_data(self):
        school_data = self.get_school_data()
        if school_data is not None:
            school_data.update_school_data(self)

    def set_relgraph_family_edges(self):
        with genealogy_caching():
            for sim_id in self._genealogy_tracker.get_parent_sim_ids_gen():
                RelgraphService.relgraph_set_edge(self.sim_id, sim_id, SimRelBitFlags.SIMRELBITS_PARENT)

            for sim_id in self._genealogy_tracker.get_children_sim_ids_gen():
                RelgraphService.relgraph_set_edge(self.sim_id, sim_id, SimRelBitFlags.SIMRELBITS_CHILD)

            if self.spouse_sim_id is not None:
                RelgraphService.relgraph_set_edge(self.sim_id, self.spouse_sim_id, SimRelBitFlags.SIMRELBITS_SPOUSE)
            if self.fiance_sim_id is not None:
                RelgraphService.relgraph_set_edge(self.sim_id, self.fiance_sim_id, SimRelBitFlags.SIMRELBITS_FIANCE)

    def on_sim_added_to_skewer(self):
        self.Buffs.on_sim_added_to_skewer()
        for stat_inst in self.commodity_tracker:
            if stat_inst.is_skill:
                stat_value = stat_inst.get_value()
                stat_inst.refresh_threshold_callback()
                self._publish_commodity_update(type(stat_inst), stat_value, stat_value)

        if FameTunables.END_FEUD_LOOT is not None:
            feud_target = self.get_feud_target()
            if feud_target is not None:
                if feud_target.household is self.household:
                    resolver = DoubleSimResolver(self, feud_target)
                    FameTunables.END_FEUD_LOOT.apply_to_resolver(resolver)

    def publish_all_commodities(self):
        for stat_inst in self.commodity_tracker:
            if self.is_npc:
                if not getattr(stat_inst, 'update_client_for_npcs', False):
                    continue
            stat_value = stat_inst.get_value()
            self._publish_commodity_update(type(stat_inst), stat_value, stat_value)

    def _publish_commodity_update(self, stat_type, old_value, new_value):
        stat_type.send_commodity_update_message(self, old_value, new_value)

    def _publish_statistic_update(self, stat_type, old_value, new_value):
        if not self.is_npc:
            services.get_event_manager().process_event((test_events.TestEvent.StatValueUpdate), sim_info=self,
              statistic=stat_type,
              custom_keys=(
             stat_type,))

    def update_spouse_sim_id(self, spouse_sim_id):
        mgr = services.sim_info_manager()
        if spouse_sim_id is not None:
            if self._relationship_tracker.spouse_sim_id is not None:
                if self._relationship_tracker.spouse_sim_id != spouse_sim_id:
                    logger.error('Naughty! {} already has a spouse but being assigned another one. Original: {} (id: {}). New: {} (id: {}).', self, mgr.get(self._relationship_tracker.spouse_sim_id), self._relationship_tracker.spouse_sim_id, mgr.get(spouse_sim_id), spouse_sim_id)
                    return
        else:
            ex_spouse_id = self._relationship_tracker.spouse_sim_id
            self._relationship_tracker.spouse_sim_id = spouse_sim_id
            if spouse_sim_id is None:
                RelgraphService.relgraph_set_marriage(self.sim_id, ex_spouse_id, False)
            else:
                RelgraphService.relgraph_set_marriage(self.sim_id, spouse_sim_id, True)
        services.get_event_manager().process_event((test_events.TestEvent.SpouseEvent), sim_info=self)

    def update_fiance_sim_id(self, fiance_sim_id):
        mgr = services.sim_info_manager()
        if fiance_sim_id is not None:
            if self._relationship_tracker.fiance_sim_id is not None:
                if self._relationship_tracker.fiance_sim_id != fiance_sim_id:
                    logger.error('Naughty! {} already has a fiance but being assigned another one. Original: {} (id: {}). New: {} (id: {}).', self, mgr.get(self._relationship_tracker.fiance_sim_id), self._relationship_tracker.fiance_sim_id, mgr.get(fiance_sim_id), fiance_sim_id)
                    return
        else:
            ex_fiance_id = self._relationship_tracker.fiance_sim_id
            self._relationship_tracker.fiance_sim_id = fiance_sim_id
            if fiance_sim_id is None:
                RelgraphService.relgraph_set_engagement(self.sim_id, ex_fiance_id, False)
            else:
                RelgraphService.relgraph_set_engagement(self.sim_id, fiance_sim_id, True)

    def get_significant_other_sim_info(self):
        spouse_sim_info = self.get_spouse_sim_info()
        if spouse_sim_info is not None:
            return spouse_sim_info
        for rel in self._relationship_tracker:
            for bit in RelationshipGlobalTuning.SIGNIFICANT_OTHER_RELATIONSHIP_BITS:
                if rel.has_bit(self.sim_id, bit):
                    return rel.get_other_sim_info(self.sim_id)

    def get_fiance_sim_info(self):
        fiance_id = self.fiance_sim_id
        if fiance_id:
            sim_info_manager = services.sim_info_manager()
            if sim_info_manager is not None:
                fiance = sim_info_manager.get(fiance_id)
                if fiance is not None:
                    return fiance
        else:
            bit = RelationshipGlobalTuning.ENGAGEMENT_RELATIONSHIP_BIT
            for rel in self._relationship_tracker:
                if rel.has_bit(self.sim_id, bit):
                    logger.warn('Sim {} is engaged, but fiance_id was set to None.', self)
                    return rel.get_other_sim_info(self.sim_id)

    @property
    def fiance_sim_id(self):
        return self._relationship_tracker.fiance_sim_id

    @property
    def spouse_sim_id(self):
        return self._relationship_tracker.spouse_sim_id

    def get_spouse_sim_info(self):
        signficant_other_id = self.spouse_sim_id
        if signficant_other_id:
            sim_info_manager = services.sim_info_manager()
            if sim_info_manager is not None:
                significant_other = sim_info_manager.get(signficant_other_id)
                if significant_other is not None:
                    return significant_other

    def get_feud_target(self):
        if RelationshipGlobalTuning.FEUD_TARGET is None:
            return
        for rel in self._relationship_tracker:
            if rel.has_bit(self.sim_id, RelationshipGlobalTuning.FEUD_TARGET):
                return rel.get_other_sim_info(self.sim_id)

    def get_random_pc_social_media_target(self):
        friends = self.get_pc_social_media_friends()
        if len(friends) > 0:
            return random.choice(friends)

    def get_pc_social_media_friends(self):
        friends = self.get_social_media_friends()
        pc_friends = []
        for friend in friends:
            if not friend.is_npc:
                pc_friends.append(friend)

        return pc_friends

    def get_social_media_friends(self):
        if SocialMediaTunables.SOCIAL_MEDIA_REL_BIT is None:
            return
        friends = []
        for rel in self._relationship_tracker:
            if rel.has_bit(self.sim_id, SocialMediaTunables.SOCIAL_MEDIA_REL_BIT):
                friends.append(rel.get_other_sim_info(self.sim_id))

        return friends

    def get_gender_preference(self, gender):
        return self.get_statistic(GlobalGenderPreferenceTuning.GENDER_PREFERENCE[gender])

    def get_gender_preferences_gen(self):
        for gender, gender_preference_statistic in GlobalGenderPreferenceTuning.GENDER_PREFERENCE.items():
            yield (
             gender, self.get_statistic(gender_preference_statistic))

    @property
    def is_exploring_sexuality(self):
        is_exploring_trait = GlobalGenderPreferenceTuning.EXPLORING_SEXUALITY_TRAITS_MAPPING.get(SexualityStatus.EXPLORING)
        return self.has_trait(is_exploring_trait)

    @staticmethod
    def add_known_traits(sim_info, family_member):
        return_value = False
        trait_tracker = family_member.trait_tracker
        for trait_type in TraitTracker.KNOWLEDGE_TRAIT_TYPES:
            for house_member_trait in trait_tracker.get_traits_of_type(trait_type):
                return_value |= sim_info.relationship_tracker.add_known_trait(house_member_trait, (family_member.id), notify_client=False)

        return return_value

    def set_household_trait_knowledge(self):
        for house_member in itertools.chain(self.household.sim_info_gen(), self._genealogy_tracker.get_parent_sim_infos_gen()):
            if house_member is self:
                continue
            self.add_known_traits(self, house_member)

    def set_default_data(self):
        if self._sim_creation_path == serialization.SimData.SIMCREATION_NONE:
            if self._fix_relationships:
                self.set_default_relationships(reciprocal=True, from_load=True)
                self._fix_relationships = False
            else:
                self.set_household_trait_knowledge()
            return
        self.set_default_relationships(reciprocal=True, from_load=True)
        if self._sim_creation_path != serialization.SimData.SIMCREATION_PRE_MADE:
            self.premade_sim_template_id = 0
        self.creation_source = SimInfoCreationSource.get_creation_source_from_creation_path(self._sim_creation_path)
        if self.creation_source.is_creation_source(SimInfoCreationSource.GALLERY):
            for commodity in list(self.commodity_tracker):
                if commodity.is_skill:
                    continue
                if not commodity.core:
                    continue
                if isinstance(commodity, ConsumableComponent.FAT_COMMODITY):
                    continue
                if isinstance(commodity, ConsumableComponent.FIT_COMMODITY):
                    continue
                if not commodity.set_to_auto_satisfy_value():
                    commodity.set_value(commodity.get_initial_value())

        self._sim_creation_path = serialization.SimData.SIMCREATION_NONE

    def _add_default_knowledge(self, sim_info):
        relationship_tracker = self.relationship_tracker
        knowledge_changed = self.add_known_traits(self, sim_info)
        knowledge_changed |= relationship_tracker.add_knows_career((sim_info.id), notify_client=False)
        knowledge_changed |= relationship_tracker.add_knows_major((sim_info.id), notify_client=False)
        return knowledge_changed

    def set_default_relationships(self, reciprocal=False, update_romance=True, from_load=False, default_track_overrides=None, processed_sim_infos=set()):
        if self.household is None:
            return
        sim_id = self.id
        relationship_tracker = self.relationship_tracker
        sims_to_process = set(self.household.sim_info_gen())
        sims_to_process.update(self._genealogy_tracker.get_parent_sim_infos_gen())
        sims_to_process.discard(self)
        sims_to_process.difference_update(processed_sim_infos)
        for house_member in sims_to_process:
            member_knowledge_changed = self._add_default_knowledge(house_member)
            if reciprocal:
                self_knowledge_changed = house_member._add_default_knowledge(self)
            else:
                house_member_id = house_member.id
                if self.is_pet == house_member.is_pet:
                    test_track = RelationshipGlobalTuning.REL_INSPECTOR_TRACK
                else:
                    test_track = RelationshipGlobalTuning.DEFAULT_PET_TO_SIM_TRACK
            track = relationship_tracker.get_relationship_track(house_member_id, track=test_track, add=False)
            if track is not None:
                if member_knowledge_changed:
                    relationship_tracker.send_relationship_info(house_member_id)
                elif reciprocal:
                    if self_knowledge_changed:
                        house_member.relationship_tracker.send_relationship_info(sim_id)
                        continue
                else:
                    return
            family_member = house_member.add_family_link(self, from_load=from_load)
            relationship_tracker.set_default_tracks(house_member, update_romance=update_romance, family_member=family_member, default_track_overrides=default_track_overrides)
            relationship_tracker.send_relationship_info(house_member_id)
            if reciprocal:
                self.add_family_link(house_member, from_load=from_load)
                house_member.relationship_tracker.set_default_tracks(self, update_romance=update_romance, family_member=family_member, bits_only=True)
                house_member.relationship_tracker.send_relationship_info(sim_id)

    def add_family_link(self, target_sim_info, from_load=False):
        bit = self.genealogy.get_family_relationship_bit(target_sim_info.id)
        if bit is None:
            return False
        if target_sim_info.relationship_tracker.has_bit(self.id, bit):
            return True
        target_sim_info.relationship_tracker.add_relationship_bit((self.id), bit, from_load=from_load)
        return True

    def add_parent_relations(self, parent_a, parent_b):
        parent_a_relation = FamilyRelationshipIndex.MOTHER if parent_a.is_female else FamilyRelationshipIndex.FATHER
        self.set_and_propagate_family_relation(parent_a_relation, parent_a)
        if parent_b is not None:
            if parent_a is not parent_b:
                parent_b_relation = FamilyRelationshipIndex.MOTHER if parent_a_relation == FamilyRelationshipIndex.FATHER else FamilyRelationshipIndex.FATHER
                self.set_and_propagate_family_relation(parent_b_relation, parent_b)

    def is_busy(self, start_time_ticks=None, end_time_ticks=None):
        if services.hidden_sim_service().is_hidden(self.id):
            return (True, None)
        if self.career_tracker is not None:
            for career in self.careers.values():
                busy_times = career.get_busy_time_periods()
                if start_time_ticks is not None and end_time_ticks is not None:
                    for busy_start_time, busy_end_time in busy_times:
                        if start_time_ticks <= busy_end_time and end_time_ticks >= busy_start_time:
                            return (
                             True, career)

                else:
                    if not career.currently_at_work:
                        continue
                    current_time = services.time_service().sim_now
                    current_time_in_ticks = current_time.time_since_beginning_of_week().absolute_ticks()
                    for busy_start_time, busy_end_time in busy_times:
                        if busy_start_time <= current_time_in_ticks <= busy_end_time:
                            return (
                             True, career)

        return (False, None)

    def debug_apply_away_action(self, away_action):
        if self._away_action_tracker is not None:
            self._away_action_tracker.create_and_apply_away_action(away_action)

    def debug_apply_default_away_action(self):
        if self._away_action_tracker is not None:
            self._away_action_tracker.reset_to_default_away_action()

    def get_default_away_action(self, on_travel_away=False):
        is_instance = self.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS) and not on_travel_away
        highest_advertising_value = None
        highest_advertising_away_action = None
        if services.hidden_sim_service().default_away_action(self.id) is not None:
            return services.hidden_sim_service().default_away_action(self.id)
        if not is_instance:
            if services.daycare_service().is_sim_info_at_daycare(self):
                return services.daycare_service().default_away_action(self)
        for commodity, away_action in SimInfo.DEFAULT_AWAY_ACTION.items():
            if is_instance:
                if not away_action.available_when_instanced:
                    continue
            commodity_instance = self.get_statistic(commodity, add=False)
            if commodity_instance is None:
                continue
            if not away_action.test(sim_info=self, target=None):
                continue
            advertising_value = commodity_instance.autonomous_desire
            if highest_advertising_value is None or highest_advertising_value < advertising_value:
                highest_advertising_value = advertising_value
                highest_advertising_away_action = away_action

        return highest_advertising_away_action

    def debug_get_current_situations_string(self):
        current_situations = ''
        sit_man = services.get_zone_situation_manager()
        if sit_man is not None:
            sim = self.get_sim_instance()
            if sim is not None:
                current_situations = ','.join((str(sit) for sit in sit_man.get_situations_sim_is_in(sim)))
        return current_situations

    def send_travel_switch_to_zone_op(self, zone_id=DEFAULT):
        if zone_id is DEFAULT:
            zone_id = self.zone_id
            world_id = self.world_id
        else:
            world_id = services.get_persistence_service().get_world_id_from_zone(zone_id)
        if zone_id == 0:
            return
        op = distributor.ops.TravelSwitchToZone((self.id,
         self.household_id,
         zone_id,
         world_id))
        distributor.ops.record(self, op)

    def send_travel_live_to_nhd_to_live_op(self, household_id=DEFAULT):
        if household_id is DEFAULT:
            household_id = self.household_id
        op = distributor.ops.TravelLiveToNhdToLive(self.id, household_id)
        distributor.ops.record(self, op)

    def flush_to_client_on_teardown(self):
        buff_component = self.Buffs
        if buff_component is not None:
            buff_component.on_sim_removed(immediate=True)

    def get_culling_immunity_reasons(self):
        reasons = []
        if self.is_player_sim:
            reasons.append(CullingReasons.PLAYER)
        immune_to_culling = any((trait.culling_behavior.is_immune_to_culling() for trait in self.trait_tracker))
        if immune_to_culling:
            reasons.append(CullingReasons.TRAIT_IMMUNE)
        if self.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
            reasons.append(CullingReasons.INSTANCED)
        if self.is_in_travel_group():
            reasons.append(CullingReasons.IN_TRAVEL_GROUP)
        return reasons

    def remove_permanently(self, household=None):
        if household is None:
            household = self.household
        if gsi_handlers.sim_info_lifetime_handlers.archiver.enabled:
            gsi_handlers.sim_info_lifetime_handlers.archive_sim_info_event(self, 'remove sim info')
        household.remove_sim_info(self, destroy_if_empty_household=True)
        social_media_service = services.get_social_media_service()
        if social_media_service is not None:
            social_media_service.on_sim_removed(self.sim_id)
        services.sim_info_manager().remove_permanently(self)
        services.get_persistence_service().del_sim_proto_buff(self.id)

    def log_sim_info(self, logger_func, additional_msg=None):
        sim_info_strings = []
        if additional_msg is not None:
            sim_info_strings.append(additional_msg)
        sim_info_strings.append('Sim info for {}'.format(self))
        sim = self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is not None:
            sim_info_strings.append('Simulation state: {}'.format(sim._simulation_state))
            sim_info_strings.append('Interaction queue:')
            for interaction in sim.queue:
                sim_info_strings.append('    {}'.format(interaction))

        else:
            sim_info_strings.append('Simulation state: UNINSTANTIATED')
        sim_info_strings.append('Traits:')
        for trait in self.trait_tracker:
            sim_info_strings.append('    {}'.format(trait))

        sim_info_strings.append('Buffs:')
        for buff in self.Buffs:
            sim_info_strings.append('    {}'.format(buff))

        sim_info_strings.append('Death Type = {}'.format(self.death_type))
        logger_func('\n'.join(sim_info_strings))

    def is_valid_statistic_to_remove(self, statistic):
        if statistic is ConsumableComponent.FAT_COMMODITY:
            return False
        if statistic is ConsumableComponent.FIT_COMMODITY:
            return False
        return True

    def discourage_route_to_join_social_group(self):
        if any((buff.discourage_route_to_join_social_group for buff in self.Buffs)):
            return True
        return False

    def get_bucks_tracker(self, add_if_none=False):
        if self._bucks_tracker is None:
            if add_if_none:
                self._bucks_tracker = SimInfoBucksTracker(self)
        return self._bucks_tracker

    def transfer_to_hidden_household(self):
        household = services.household_manager().create_household(self.account)
        household.set_to_hidden()
        household.add_sim_info(self)
        self.assign_to_household(household)
        return household


def save_active_household_command_start():
    global SAVE_ACTIVE_HOUSEHOLD_COMMAND
    SAVE_ACTIVE_HOUSEHOLD_COMMAND = True


def save_active_household_command_stop():
    global SAVE_ACTIVE_HOUSEHOLD_COMMAND
    SAVE_ACTIVE_HOUSEHOLD_COMMAND = False


class AccountConnection(enum.Int, export=False):
    SAME_LOT = 1
    DIFFERENT_LOT = 2
    OFFLINE = 3