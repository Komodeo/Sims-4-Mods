# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\call_to_action\call_to_action.py
# Compiled at: 2022-08-26 15:13:12
# Size of source mod 2**32: 14623 bytes
from distributor.ops import SetCallToAction
from distributor.system import Distributor
from event_testing.resolver import DoubleSimResolver
from event_testing.test_variants import TunableSituationJobTest
from filters.tunable import TunableSimFilter
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableRange, TunableColor, Tunable, TunableList, OptionalTunable, TunableTuple, TunableEnumEntry, TunableReference
from interactions import ParticipantType
import relationships.relationship_tests, enum, services, sims4.log, sims.sim_info_tests, tag
from vfx import TunablePlayEffectVariant
logger = sims4.log.Logger('call_to_action', default_owner='nabaker')

class TunableCallToActionTestVariant(sims4.tuning.tunable.TunableVariant):

    def __init__(self, description='A tunable test support for choosing sims to be highlighted', **kwargs):
        (super().__init__)(has_buff=sims.sim_info_tests.BuffTest.TunableFactory(), has_job=TunableSituationJobTest(locked_args={'participant': ParticipantType.Actor}), 
         relationship=relationships.relationship_tests.TunableRelationshipTest(locked_args={'subject':ParticipantType.Actor,  'target_sim':ParticipantType.TargetSim}), 
         description=description, **kwargs)


class CallToActionActorType(enum.Int):
    ACTIVE_SIM = 0
    SCENARIO_SIM = 1


class CallToAction(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CALL_TO_ACTION)):
    INSTANCE_TUNABLES = {'_color':TunableColor(description='\n            The color of the call to action.\n            '), 
     '_pulse_frequency':TunableRange(description='\n            The frequency at which the highlight pulses.\n            ',
       tunable_type=float,
       default=1.0,
       minimum=0.1), 
     '_thickness':TunableRange(description='\n            The thickness of the highlight.\n            ',
       tunable_type=float,
       default=0.002,
       minimum=0.001,
       maximum=0.005), 
     '_tags':tag.TunableTags(description='\n            The set of tags that are used to determine which objects to highlight.\n            '), 
     '_on_active_lot':Tunable(description='\n            Whether or not objects on active lot should be highlighted.\n            ',
       tunable_type=bool,
       default=True), 
     '_on_open_street':Tunable(description='\n            Whether or not objects on open street should be highlighted.\n            ',
       tunable_type=bool,
       default=True), 
     '_tutorial_text':OptionalTunable(description='\n            Text for a tutorial call to action.  If this is enabled, the\n            CTA will be a tutorial CTA with the specified text.\n            ',
       tunable=TunableLocalizedString()), 
     '_sim_filter':OptionalTunable(description='\n            Filter to select one or more sims to recieve the CTA.\n            ',
       tunable=TunableSimFilter.TunablePackSafeReference()), 
     '_sim_tests':TunableList(description='\n            Tests used to determine which sims to allow in the call to action.\n            ',
       tunable=TunableTuple(description='\n                A combination of a test and information to choose a sim as the test target.\n                ',
       test=(TunableCallToActionTestVariant()),
       target_type=TunableEnumEntry(description='\n                    How to determine which sim should be chosen as the target of this test.\n                    ',
       tunable_type=CallToActionActorType,
       default=(CallToActionActorType.ACTIVE_SIM)),
       scenario_role=TunableReference(description='\n                    When set and Target Type is SCENARIO_SIM this will be the role used to determine\n                    what sim to target for the test.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioRole', ),
       allow_none=True))), 
     '_max_highlighted_objects':TunableRange(description='\n            The maximum number of objects that will be highlighted by this call to action.\n            0 means no limit.\n            ',
       tunable_type=int,
       minimum=0,
       default=0), 
     'highlighted_object_vfx':OptionalTunable(description='\n            If enabled, we will play an effect on the objects highlighted by this call to action.\n            ',
       tunable=TunablePlayEffectVariant(description='\n                Effect to play on the objects when they are highlighted.\n                '))}

    def __init__(self):
        super().__init__()
        self._owner = None
        self._sim_ids = []
        self._num_highlighted_objects = 0
        self._object_vfx_handlers = []

    def get_sim_filter_gsi_name(self):
        return str(self)

    @property
    def owner(self):
        return self._owner

    def sim_passes_tests(self, sim_to_test):
        active_sim = services.client_manager().get_first_client().active_sim.sim_info
        scenario = None
        if active_sim.household:
            if active_sim.household.scenario_tracker:
                scenario = active_sim.household.scenario_tracker.active_scenario
        for test_info in self._sim_tests:
            target_sim = active_sim
            if test_info.target_type == CallToActionActorType.SCENARIO_SIM:
                if scenario is None or test_info.scenario_role is None:
                    return False
                scenario_sims = frozenset(scenario.sim_infos_of_interest_gen([test_info.scenario_role]))
                if active_sim not in scenario_sims:
                    target_sim = next(iter(scenario_sims), None)
            if target_sim is None:
                return False
            if not DoubleSimResolver(sim_to_test, target_sim)(test_info.test):
                return False

        return True

    def reached_max_highlighted_objects(self):
        return self._max_highlighted_objects != 0 and self._num_highlighted_objects >= self._max_highlighted_objects

    def turn_on(self, owner):
        self._owner = owner
        for script_object in (services.object_manager().get_objects_with_tags_gen)(*self._tags):
            if script_object.visible_to_client:
                self._turn_on_object(script_object)
                if self.reached_max_highlighted_objects():
                    return

        self._sim_ids = []
        if self._sim_filter is not None:
            constrained_sims = tuple((sim_info.sim_id for sim_info in services.sim_info_manager().instanced_sims_gen()))
            active_sim = services.client_manager().get_first_client().active_sim.sim_info
            filter_result = services.sim_filter_service().submit_filter(sim_filter=(self._sim_filter), callback=None,
              sim_constraints=constrained_sims,
              allow_yielding=False,
              requesting_sim_info=active_sim,
              gsi_source_fn=(self.get_sim_filter_gsi_name))
            for result in filter_result:
                if self.sim_passes_tests(result.sim_info):
                    self._sim_ids.append(result.sim_info.sim_id)

        else:
            if self._sim_tests:
                for instanced_sim in services.sim_info_manager().instanced_sims_gen():
                    if self.sim_passes_tests(instanced_sim.sim_info):
                        self._sim_ids.append(instanced_sim.sim_id)

        if self._sim_ids:
            object_manager = services.object_manager()
            for sim_id in self._sim_ids:
                sim = object_manager.get(sim_id)
                self._turn_on_object(sim)
                if self.reached_max_highlighted_objects():
                    return

    def turn_off(self):
        if self._owner is not None:
            self._owner.on_cta_ended(self.guid64)
        for script_object in (services.object_manager().get_objects_with_tags_gen)(*self._tags):
            Distributor.instance().add_op(script_object, SetCallToAction(0, 0, 0, None))

        object_manager = services.object_manager()
        for sim_id in self._sim_ids:
            sim = object_manager.get(sim_id)
            if sim is not None:
                Distributor.instance().add_op(sim, SetCallToAction(0, 0, 0))

        for object_vfx in self._object_vfx_handlers:
            object_vfx.stop()

        self._sim_ids = []
        self._num_highlighted_objects = 0
        self._object_vfx_handlers = []

    def turn_on_object_on_create(self, script_object):
        if (script_object.definition.has_build_buy_tag)(*self._tags):
            script_object.register_on_location_changed(self._object_location_changed)
        else:
            if script_object.is_sim and self._sim_filter is not None:
                active_sim = services.client_manager().get_first_client().active_sim.sim_info
                results = services.sim_filter_service().submit_filter(sim_filter=(self._sim_filter), callback=None,
                  sim_constraints=(
                 script_object.sim_info.sim_id,),
                  allow_yielding=False,
                  requesting_sim_info=active_sim,
                  gsi_source_fn=(self.get_sim_filter_gsi_name))
                if not results or self.sim_passes_tests(script_object.sim_info):
                    script_object.register_on_location_changed(self._object_location_changed)
            else:
                if script_object.is_sim:
                    if self._sim_tests:
                        if self.sim_passes_tests(script_object.sim_info):
                            script_object.register_on_location_changed(self._object_location_changed)

    def _turn_on_object(self, script_object):
        if script_object.is_on_active_lot():
            if not self._on_active_lot:
                return
        else:
            if not self._on_open_street:
                return
        Distributor.instance().add_op(script_object, SetCallToAction((self._color), (self._pulse_frequency),
          (self._thickness),
          tutorial_text=(self._tutorial_text)))
        if self.highlighted_object_vfx is not None:
            object_vfx = self.highlighted_object_vfx(script_object)
            object_vfx.start()
            self._object_vfx_handlers.append(object_vfx)
        self._num_highlighted_objects += 1

    def _object_location_changed(self, script_object, old_loc, new_loc):
        script_object.unregister_on_location_changed(self._object_location_changed)
        if script_object.is_sim:
            self._sim_ids.append(script_object.sim_info.sim_id)
        if self.reached_max_highlighted_objects():
            return
        self._turn_on_object(script_object)

    def turn_off_object_on_remove(self, script_object):
        if self._max_highlighted_objects == 0:
            return
        is_matching_object = False
        if (script_object.definition.has_build_buy_tag)(*self._tags):
            is_matching_object = True
        else:
            if script_object.is_sim:
                if script_object.sim_info.sim_id in self._sim_ids:
                    is_matching_object = True
        if is_matching_object:
            if self._num_highlighted_objects > 0:
                self._num_highlighted_objects -= 1
                if self._num_highlighted_objects == self._max_highlighted_objects - 1:
                    self._num_highlighted_objects = 0
                    self.turn_on(self._owner)