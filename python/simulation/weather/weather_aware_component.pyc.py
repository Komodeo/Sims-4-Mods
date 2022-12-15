# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\weather\weather_aware_component.py
# Compiled at: 2020-04-20 15:05:42
# Size of source mod 2**32: 30914 bytes
from _sims4_collections import frozendict
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableMapping, TunableEnumEntry, TunableList, TunableTuple, OptionalTunable
import enum, sims4.log, sims4.math
from build_buy import is_location_outside
from event_testing.resolver import SingleObjectResolver, SingleSimResolver
from interactions.utils.loot import LootActions, LootOperationList
from objects.components import Component, componentmethod_with_fallback
from objects.components.types import WEATHER_AWARE_COMPONENT
from routing import SurfaceType
from routing.portals.portal_tuning import PortalFlags
from routing.route_enums import RouteEventType, RoutingStageEvent
from routing.route_events.route_event import RouteEvent
from routing.route_events.route_event_provider import RouteEventProviderMixin
from tunable_multiplier import TunableMultiplier
from vfx import PlayEffect
from weather.weather_enums import WeatherType
import services
logger = sims4.log.Logger('WeatherAwareComponent', default_owner='nabaker')

class WeatherAwareComponent(RouteEventProviderMixin, Component, HasTunableFactory, AutoFactoryInit, component_name=WEATHER_AWARE_COMPONENT):

    class TunableWeatherAwareMapping(TunableMapping):

        def __init__(self, start_description=None, end_description=None, **kwargs):
            (super().__init__)(key_type=TunableEnumEntry(description='\n                    The weather type we are interested in.\n                    ',
  tunable_type=WeatherType,
  default=(WeatherType.UNDEFINED)), 
             value_type=TunableTuple(start_loot=TunableList(description=start_description, tunable=LootActions.TunableReference(description='\n                            The loot action applied.\n                            ',
  pack_safe=True)),
  end_loot=TunableList(description=end_description, tunable=LootActions.TunableReference(description='\n                            The loot action applied.\n                            ',
  pack_safe=True))), **kwargs)
            self.cache_key = 'TunableWeatherAwareMapping'

        def load_etree_node(self, node, source, expect_error):
            value = super().load_etree_node(node, source, expect_error)
            modified_dict = {}
            for weather_type, loots in value.items():
                if not loots.start_loot:
                    if loots.end_loot:
                        pass
                modified_dict[weather_type] = loots

            return frozendict(modified_dict)

    FACTORY_TUNABLES = {'inside_loot':TunableWeatherAwareMapping(description="\n            A tunable mapping linking a weather type to the loot actions the \n            component owner should get when inside.\n            \n            WeatherType will be UNDEFINED if weather isn't installed.\n            ",
       start_description='\n                Loot actions the owner should get when the weather \n                starts if inside or when the object moves inside \n                during the specified weather.\n                ',
       end_description='\n                Loot actions the owner should get when the weather \n                ends if inside or when the object moves outside \n                during the specified weather.\n                '), 
     'outside_loot':TunableWeatherAwareMapping(description="\n            A tunable mapping linking a weather type to the loot actions the \n            component owner should get when outside.\n            \n            WeatherType will be UNDEFINED if weather isn't installed.\n            ",
       start_description='\n                Loot actions the owner should get when the weather \n                starts if outside or when the object moves outside \n                during the specified weather.\n                ',
       end_description='\n                Loot actions the owner should get when the weather \n                ends if outside or when the object moves inside \n                during the specified weather.\n                '), 
     'anywhere_loot':TunableWeatherAwareMapping(description="\n            A tunable mapping linking a weather type to the loot actions the \n            component owner should get regardless of inside/outside location.\n            \n            WeatherType will be UNDEFINED if weather isn't installed.\n            Anywhere actions happen after inside/outside actions when weather starts.\n            Anywhere actions happen before inside/outside actions when weather ends.\n            ",
       start_description='\n                Loot actions the owner should get when the weather \n                starts regardless of location.\n                ',
       end_description='\n                Loot actions the owner should get when the weather \n                ends regardless of location.\n                '), 
     'disable_loot':TunableList(description='\n            A list of loot actions to apply to the owner of this component when\n            the component is disabled.\n            ',
       tunable=LootActions.TunableReference(description='\n                The loot action applied.\n                ',
       pack_safe=True)), 
     'enable_loot':TunableList(description='\n            A list of loot actions to apply to the owner of this component when\n            the component is enabled.\n            ',
       tunable=LootActions.TunableReference(description='\n                The loot action applied.\n                ',
       pack_safe=True)), 
     'lightning_strike_loot':TunableList(description='\n            A list of loot actions to apply to the owner of this component when\n            they are struck by lightning.\n            ',
       tunable=LootActions.TunableReference(description='\n                The loot action applied.\n                ',
       pack_safe=True)), 
     'umbrella_route_events':OptionalTunable(description='\n            If tuned, we will consider points around inside/outside threshold\n            to handle umbrella route events.\n            ',
       tunable=TunableTuple(description='\n                Data used to populate fields on the path plan context.\n                ',
       enter_carry_event=RouteEvent.TunablePackSafeReference(description='\n                    To be moved into weather aware component.\n                    Route event to trigger umbrella carry.\n                    '),
       exit_carry_event=RouteEvent.TunablePackSafeReference(description='\n                    To be moved into weather aware component.\n                    Route event to trigger umbrella carry.\n                    '))), 
     'lightning_strike_multiplier':OptionalTunable(description='\n            If enabled, we will modify the chance that this object is struck by\n            lightning. Note that the object must be tagged as an object that\n            can be struck. See Lightning module tuning.\n            ',
       tunable=TunableMultiplier.TunableFactory(description='\n                A multiplier to the weight for this object to be struck by\n                lightning instead of other objects. \n                \n                Note that this affects Sims as well, but will affect the chance\n                this Sim is struck vs. other Sims, not other objects.\n                ')), 
     'lightning_effect_override':OptionalTunable(description='\n            If enabled, when this object is struck by lightning we will play \n            this tuned effect instead of the one specified in module lightning \n            tuning.\n            ',
       tunable=PlayEffect.TunableFactory(description='\n                The effect we want to play when this object is struck by \n                lightning.\n                '))}

    class LocationUpdateStatus(enum.Int, export=False):
        NOT_IN_PROGRESS = 0
        IN_PROGRESS = 1
        PENDING = 2

    def __init__(self, *args, parent=True, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._is_outside = None
        self._location_update_status = WeatherAwareComponent.LocationUpdateStatus.NOT_IN_PROGRESS
        self._inside_sensitive = True if (self.outside_loot or self.inside_loot) else False
        self._disabled_count = 0
        self._safety_umbrella_putaway_event = None

    def is_valid_to_add(self):
        if not super().is_valid_to_add():
            return False
        if not self.inside_loot:
            if not self.outside_loot:
                if not self.anywhere_loot:
                    if not self.lightning_strike_loot:
                        if self.umbrella_route_events is None:
                            return False
                        if not self.umbrella_route_events.enter_carry_event:
                            if not self.umbrella_route_events.exit_carry_event:
                                return False
            return True

    def enable(self, value):
        if not value:
            if self.enabled:
                if self.owner.manager is not None:
                    if services.current_zone().is_zone_running:
                        self._update_location(disabling=True)
                        if self.owner.is_sim:
                            resolver = SingleSimResolver(self.owner.sim_info)
                        else:
                            resolver = SingleObjectResolver(self.owner)
                        loot_ops_list = LootOperationList(resolver, self.disable_loot)
                        loot_ops_list.apply_operations()
                self.on_remove()
            self._disabled_count += 1
        else:
            self._disabled_count -= 1
            if self.enabled:
                if self.owner.is_sim:
                    resolver = SingleSimResolver(self.owner.sim_info)
                else:
                    resolver = SingleObjectResolver(self.owner)
                loot_ops_list = LootOperationList(resolver, self.enable_loot)
                loot_ops_list.apply_operations()
                self.on_add()
                if self._inside_sensitive:
                    self.on_location_changed_callback()
            else:
                if self._disabled_count < 0:
                    logger.error('Unbalanced enabled/disable in weathercomponent.  Called disable once more than enable.')
                    self._disabled_count = 0

    @property
    def enabled(self):
        return self._disabled_count == 0

    def on_add(self):
        if self.enabled:
            if self._inside_sensitive:
                self.owner.register_on_location_changed(self.on_location_changed_callback)
            else:
                self.on_location_changed_callback()
            if self._has_routing_events():
                self.owner.routing_component.register_routing_stage_event(RoutingStageEvent.ROUTE_END, self._on_route_finished)

    def on_remove(self):
        if self.enabled:
            self._stop()
            if self.owner.is_on_location_changed_callback_registered(self.on_location_changed_callback):
                self.owner.unregister_on_location_changed(self.on_location_changed_callback)
            if self._has_routing_events():
                self.owner.routing_component.unregister_routing_stage_event(RoutingStageEvent.ROUTE_END, self._on_route_finished)

    def _stop(self):
        weather_service = services.weather_service()
        if weather_service is not None:
            weather_service.flush_weather_aware_message(self.owner)
            if self._is_outside is not None:
                weather_types = set(self.anywhere_loot)
                if self._is_outside:
                    weather_types.update(self.outside_loot)
                else:
                    weather_types.update(self.inside_loot)
                weather_service.deregister_object(self.owner, weather_types)
        self._is_outside = None

    def on_added_to_inventory(self):
        if self.enabled:
            if not self._inside_sensitive:
                self.on_location_changed_callback()
            self._stop()

    def on_removed_from_inventory(self):
        if self.enabled:
            self.on_location_changed_callback()

    def on_finalize_load(self):
        if self.enabled:
            if not self.owner.is_sim:
                self._update_location()

    def on_preroll_autonomy(self):
        if self.enabled:
            is_inside_override = False
            next_interaction = self.owner.queue.peek_head()
            if next_interaction is not None:
                if next_interaction.counts_as_inside:
                    is_inside_override = True
            self._update_location(is_inside_override=is_inside_override)

    def on_buildbuy_exit(self):
        if self.enabled:
            self._update_location()

    def on_location_changed_callback(self, *_, **__):
        if self.enabled:
            if self.owner.manager is not None:
                if services.current_zone().is_zone_running:
                    self._update_location()

    def _update_location(self, is_inside_override=False, disabling=False):
        if disabling:
            is_outside = None
        else:
            if is_inside_override:
                is_outside = False
            else:
                if self.owner.is_in_inventory():
                    is_outside = None
                else:
                    if not self._inside_sensitive:
                        is_outside = True
                    else:
                        is_outside = self.owner.is_outside
        if is_outside == self._is_outside:
            return
        if self._location_update_status != WeatherAwareComponent.LocationUpdateStatus.NOT_IN_PROGRESS:
            self._location_update_status = WeatherAwareComponent.LocationUpdateStatus.PENDING
            return
        self._location_update_status = WeatherAwareComponent.LocationUpdateStatus.IN_PROGRESS
        was_outside = self._is_outside
        self._is_outside = is_outside
        recurse = False
        try:
            weather_service = services.weather_service()
            if weather_service is not None:
                weather_types = weather_service.get_current_weather_types()
                weather_service.update_weather_aware_message(self.owner)
            else:
                weather_types = {
                 WeatherType.UNDEFINED}
            if self.owner.is_sim:
                resolver = SingleSimResolver(self.owner.sim_info)
            else:
                resolver = SingleObjectResolver(self.owner)
            if was_outside is not None:
                if was_outside:
                    self._give_loot(weather_types, self.outside_loot, resolver, False)
                    if weather_service is not None:
                        weather_service.deregister_object(self.owner, self.outside_loot.keys())
                else:
                    self._give_loot(weather_types, self.inside_loot, resolver, False)
                    if weather_service is not None:
                        weather_service.deregister_object(self.owner, self.inside_loot.keys())
            if is_outside is not None:
                if is_outside:
                    self._give_loot(weather_types, self.outside_loot, resolver, True)
                    if weather_service is not None:
                        weather_service.register_object(self.owner, self.outside_loot.keys())
                        weather_service.register_object(self.owner, self.anywhere_loot.keys())
                else:
                    self._give_loot(weather_types, self.inside_loot, resolver, True)
                    if weather_service is not None:
                        weather_service.register_object(self.owner, self.inside_loot.keys())
                        weather_service.register_object(self.owner, self.anywhere_loot.keys())
                if was_outside is None:
                    self._give_loot(weather_types, self.anywhere_loot, resolver, True)
            else:
                self._give_loot(weather_types, self.anywhere_loot, resolver, False)
                if weather_service is not None:
                    weather_service.deregister_object(self.owner, self.anywhere_loot.keys())
            recurse = self._location_update_status == WeatherAwareComponent.LocationUpdateStatus.PENDING
        finally:
            self._location_update_status = WeatherAwareComponent.LocationUpdateStatus.NOT_IN_PROGRESS

        if recurse:
            self._update_location(is_inside_override=is_inside_override, disabling=disabling)

    def _give_loot(self, weather_types, loot_dict, resolver, is_start):
        for weather_type in weather_types & loot_dict.keys():
            loot = loot_dict[weather_type].start_loot if is_start else loot_dict[weather_type].end_loot
            for loot_action in loot:
                loot_action.apply_to_resolver(resolver)

    @componentmethod_with_fallback(lambda *_, **__: None
)
    def give_weather_loot(self, weather_types, is_start):
        if self._is_outside is not None:
            if self.owner.is_sim:
                resolver = SingleSimResolver(self.owner.sim_info)
            else:
                resolver = SingleObjectResolver(self.owner)
            if not is_start:
                self._give_loot(weather_types, self.anywhere_loot, resolver, is_start)
            if self._is_outside:
                self._give_loot(weather_types, self.outside_loot, resolver, is_start)
            else:
                self._give_loot(weather_types, self.inside_loot, resolver, is_start)
            if is_start:
                self._give_loot(weather_types, self.anywhere_loot, resolver, is_start)

    @componentmethod_with_fallback(lambda *_, **__: 1.0
)
    def get_lightning_strike_multiplier(self):
        if not self.enabled:
            return 0
        if self.lightning_strike_multiplier is not None:
            return self.lightning_strike_multiplier.get_multiplier(SingleObjectResolver(self.owner))
        return 1.0

    def on_struck_by_lightning(self):
        loot_ops_list = LootOperationList(SingleObjectResolver(self.owner), self.lightning_strike_loot)
        loot_ops_list.apply_operations()

    def _on_route_finished(self, *_, **__):
        self._safety_umbrella_putaway_event = None

    def is_route_event_valid(self, route_event, time, sim, path):
        if not self.enabled:
            return False
        if self._safety_umbrella_putaway_event is route_event:
            location = path.final_location
            if is_location_outside(location.transform.translation, location.routing_surface.secondary_id):
                self._safety_umbrella_putaway_event = None
                return False
            if not sims4.math.almost_equal(time, path.duration() - 0.5):
                self._safety_umbrella_putaway_event = None
                return False
            return True

    def _no_regular_put_away_scheduled(self, route_event_context):
        if self._safety_umbrella_putaway_event is None:
            return not route_event_context.route_event_already_scheduled((self.umbrella_route_events.exit_carry_event), provider=self)
        for route_event in route_event_context.route_event_of_data_type_gen(type(self._safety_umbrella_putaway_event.event_data)):
            if route_event is not self._safety_umbrella_putaway_event:
                return False

        return True

    def _has_routing_events(self):
        if not self.umbrella_route_events is None:
            if self.umbrella_route_events.enter_carry_event is None or self.umbrella_route_events.exit_carry_event is None:
                return False
            return True

    def provide_route_events--- This code section failed: ---

 L. 588         0  LOAD_FAST                'self'
                2  LOAD_ATTR                enabled
                4  POP_JUMP_IF_TRUE     10  'to 10'

 L. 589         6  LOAD_CONST               None
                8  RETURN_VALUE     
             10_0  COME_FROM             4  '4'

 L. 594        10  LOAD_FAST                'self'
               12  LOAD_METHOD              _has_routing_events
               14  CALL_METHOD_0         0  '0 positional arguments'
               16  POP_JUMP_IF_TRUE     22  'to 22'

 L. 595        18  LOAD_CONST               None
               20  RETURN_VALUE     
             22_0  COME_FROM            16  '16'

 L. 597        22  LOAD_GLOBAL              SingleSimResolver
               24  LOAD_FAST                'sim'
               26  LOAD_ATTR                sim_info
               28  CALL_FUNCTION_1       1  '1 positional argument'
               30  STORE_FAST               'resolver'

 L. 598        32  LOAD_FAST                'self'
               34  LOAD_ATTR                umbrella_route_events
               36  LOAD_ATTR                enter_carry_event
               38  LOAD_METHOD              test
               40  LOAD_FAST                'resolver'
               42  CALL_METHOD_1         1  '1 positional argument'
               44  STORE_FAST               'can_carry_umbrella'

 L. 599        46  LOAD_CONST               False
               48  STORE_FAST               'added_enter_carry'

 L. 600        50  LOAD_CONST               False
               52  STORE_FAST               'added_exit_carry'

 L. 601        54  LOAD_CONST               None
               56  STORE_FAST               'is_prev_point_outside'

 L. 602        58  LOAD_CONST               None
               60  STORE_FAST               'prev_time'

 L. 603        62  LOAD_CONST               None
               64  STORE_FAST               'node'

 L. 604        66  LOAD_CONST               None
               68  STORE_FAST               'prev_node'

 L. 605        70  LOAD_CONST               False
               72  STORE_FAST               'prev_force_no_carry'

 L. 608     74_76  SETUP_LOOP          476  'to 476'
               78  LOAD_FAST                'path'
               80  LOAD_ATTR                get_location_data_along_path_gen
               82  LOAD_CONST               0.5
               84  LOAD_FAST                'start_time'
               86  LOAD_FAST                'end_time'
               88  LOAD_CONST               ('time_step', 'start_time', 'end_time')
               90  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               92  GET_ITER         
             94_0  COME_FROM           472  '472'
             94_1  COME_FROM           300  '300'
            94_96  FOR_ITER            474  'to 474'
               98  UNPACK_SEQUENCE_3     3 
              100  STORE_FAST               'transform'
              102  STORE_FAST               'routing_surface'
              104  STORE_FAST               'time'

 L. 610       106  LOAD_FAST                'routing_surface'
              108  LOAD_ATTR                type
              110  LOAD_GLOBAL              SurfaceType
              112  LOAD_ATTR                SURFACETYPE_POOL
              114  COMPARE_OP               ==
              116  STORE_FAST               'force_no_carry'

 L. 611       118  LOAD_FAST                'force_no_carry'
              120  POP_JUMP_IF_TRUE    250  'to 250'

 L. 613       122  LOAD_FAST                'path'
              124  LOAD_METHOD              node_at_time
              126  LOAD_FAST                'time'
              128  CALL_METHOD_1         1  '1 positional argument'
              130  STORE_FAST               'node'

 L. 614       132  LOAD_FAST                'node'
              134  LOAD_FAST                'prev_node'
              136  COMPARE_OP               is
              138  POP_JUMP_IF_FALSE   146  'to 146'

 L. 616       140  LOAD_FAST                'prev_force_no_carry'
              142  STORE_FAST               'force_no_carry'
              144  JUMP_FORWARD        250  'to 250'
            146_0  COME_FROM           138  '138'

 L. 617       146  LOAD_FAST                'force_no_carry'
              148  POP_JUMP_IF_TRUE    250  'to 250'
              150  LOAD_FAST                'node'
              152  LOAD_ATTR                portal_object_id
              154  LOAD_CONST               0
              156  COMPARE_OP               !=
              158  POP_JUMP_IF_FALSE   250  'to 250'

 L. 619       160  LOAD_GLOBAL              services
              162  LOAD_METHOD              object_manager
              164  LOAD_FAST                'routing_surface'
              166  LOAD_ATTR                primary_id
              168  CALL_METHOD_1         1  '1 positional argument'
              170  LOAD_METHOD              get
              172  LOAD_FAST                'node'
              174  LOAD_ATTR                portal_object_id
              176  CALL_METHOD_1         1  '1 positional argument'
              178  STORE_FAST               'portal_object'

 L. 620       180  LOAD_FAST                'portal_object'
              182  LOAD_CONST               None
              184  COMPARE_OP               is-not
              186  POP_JUMP_IF_FALSE   250  'to 250'

 L. 621       188  LOAD_FAST                'portal_object'
              190  LOAD_METHOD              get_portal_by_id
              192  LOAD_FAST                'node'
              194  LOAD_ATTR                portal_id
              196  CALL_METHOD_1         1  '1 positional argument'
              198  STORE_FAST               'portal_instance'

 L. 622       200  LOAD_FAST                'portal_instance'
              202  LOAD_CONST               None
              204  COMPARE_OP               is-not
              206  JUMP_IF_FALSE_OR_POP   248  'to 248'

 L. 623       208  LOAD_FAST                'portal_instance'
              210  LOAD_ATTR                portal_template
              212  LOAD_CONST               None
              214  COMPARE_OP               is-not
              216  JUMP_IF_FALSE_OR_POP   248  'to 248'

 L. 624       218  LOAD_FAST                'portal_instance'
              220  LOAD_ATTR                portal_template
              222  LOAD_ATTR                required_flags
              224  LOAD_CONST               None
              226  COMPARE_OP               is-not
              228  JUMP_IF_FALSE_OR_POP   248  'to 248'

 L. 625       230  LOAD_FAST                'portal_instance'
              232  LOAD_ATTR                portal_template
              234  LOAD_ATTR                required_flags
              236  LOAD_GLOBAL              PortalFlags
              238  LOAD_ATTR                REQUIRE_NO_CARRY
              240  BINARY_AND       
              242  LOAD_GLOBAL              PortalFlags
              244  LOAD_ATTR                REQUIRE_NO_CARRY
              246  COMPARE_OP               ==
            248_0  COME_FROM           228  '228'
            248_1  COME_FROM           216  '216'
            248_2  COME_FROM           206  '206'
              248  STORE_FAST               'force_no_carry'
            250_0  COME_FROM           186  '186'
            250_1  COME_FROM           158  '158'
            250_2  COME_FROM           148  '148'
            250_3  COME_FROM           144  '144'
            250_4  COME_FROM           120  '120'

 L. 627       250  LOAD_FAST                'routing_surface'
              252  LOAD_CONST               None
              254  COMPARE_OP               is
          256_258  POP_JUMP_IF_FALSE   264  'to 264'
              260  LOAD_CONST               0
              262  JUMP_FORWARD        268  'to 268'
            264_0  COME_FROM           256  '256'
              264  LOAD_FAST                'routing_surface'
              266  LOAD_ATTR                secondary_id
            268_0  COME_FROM           262  '262'
              268  STORE_FAST               'level'

 L. 628       270  LOAD_GLOBAL              is_location_outside
              272  LOAD_FAST                'transform'
              274  LOAD_ATTR                translation
              276  LOAD_FAST                'level'
              278  CALL_FUNCTION_2       2  '2 positional arguments'
              280  STORE_FAST               'is_curr_point_outside'

 L. 629       282  LOAD_FAST                'is_prev_point_outside'
              284  LOAD_CONST               None
              286  COMPARE_OP               is
          288_290  POP_JUMP_IF_FALSE   302  'to 302'

 L. 630       292  LOAD_FAST                'is_curr_point_outside'
              294  STORE_FAST               'is_prev_point_outside'

 L. 631       296  LOAD_FAST                'time'
              298  STORE_FAST               'prev_time'

 L. 632       300  CONTINUE             94  'to 94'
            302_0  COME_FROM           288  '288'

 L. 635       302  LOAD_FAST                'can_carry_umbrella'
          304_306  POP_JUMP_IF_FALSE   370  'to 370'

 L. 636       308  LOAD_FAST                'added_enter_carry'
          310_312  POP_JUMP_IF_TRUE    370  'to 370'

 L. 637       314  LOAD_FAST                'is_curr_point_outside'
          316_318  POP_JUMP_IF_FALSE   370  'to 370'

 L. 638       320  LOAD_FAST                'route_event_context'
              322  LOAD_ATTR                route_event_already_scheduled
              324  LOAD_FAST                'self'
              326  LOAD_ATTR                umbrella_route_events
              328  LOAD_ATTR                enter_carry_event
              330  LOAD_FAST                'self'
              332  LOAD_CONST               ('provider',)
              334  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
          336_338  POP_JUMP_IF_TRUE    370  'to 370'

 L. 640       340  LOAD_FAST                'route_event_context'
              342  LOAD_METHOD              add_route_event
              344  LOAD_GLOBAL              RouteEventType
              346  LOAD_ATTR                FIRST_OUTDOOR
              348  LOAD_FAST                'self'
              350  LOAD_ATTR                umbrella_route_events
              352  LOAD_ATTR                enter_carry_event
              354  LOAD_FAST                'self'
              356  LOAD_FAST                'time'
              358  LOAD_CONST               ('provider', 'time')
              360  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              362  CALL_METHOD_2         2  '2 positional arguments'
              364  POP_TOP          

 L. 641       366  LOAD_CONST               True
              368  STORE_FAST               'added_enter_carry'
            370_0  COME_FROM           336  '336'
            370_1  COME_FROM           316  '316'
            370_2  COME_FROM           310  '310'
            370_3  COME_FROM           304  '304'

 L. 644       370  LOAD_FAST                'added_exit_carry'
          372_374  POP_JUMP_IF_TRUE    436  'to 436'

 L. 645       376  LOAD_FAST                'is_curr_point_outside'
          378_380  POP_JUMP_IF_TRUE    388  'to 388'
              382  LOAD_FAST                'is_prev_point_outside'
          384_386  POP_JUMP_IF_TRUE    394  'to 394'
            388_0  COME_FROM           378  '378'
              388  LOAD_FAST                'force_no_carry'
          390_392  POP_JUMP_IF_FALSE   436  'to 436'
            394_0  COME_FROM           384  '384'

 L. 646       394  LOAD_FAST                'self'
              396  LOAD_METHOD              _no_regular_put_away_scheduled
              398  LOAD_FAST                'route_event_context'
              400  CALL_METHOD_1         1  '1 positional argument'
          402_404  POP_JUMP_IF_FALSE   436  'to 436'

 L. 647       406  LOAD_FAST                'route_event_context'
              408  LOAD_METHOD              add_route_event
              410  LOAD_GLOBAL              RouteEventType
              412  LOAD_ATTR                LAST_OUTDOOR
              414  LOAD_FAST                'self'
              416  LOAD_ATTR                umbrella_route_events
              418  LOAD_ATTR                exit_carry_event
              420  LOAD_FAST                'self'
              422  LOAD_FAST                'prev_time'
              424  LOAD_CONST               ('provider', 'time')
              426  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              428  CALL_METHOD_2         2  '2 positional arguments'
              430  POP_TOP          

 L. 648       432  LOAD_CONST               True
              434  STORE_FAST               'added_exit_carry'
            436_0  COME_FROM           402  '402'
            436_1  COME_FROM           390  '390'
            436_2  COME_FROM           372  '372'

 L. 650       436  LOAD_FAST                'can_carry_umbrella'
          438_440  POP_JUMP_IF_FALSE   448  'to 448'
              442  LOAD_FAST                'added_enter_carry'
          444_446  POP_JUMP_IF_FALSE   456  'to 456'
            448_0  COME_FROM           438  '438'
              448  LOAD_FAST                'added_exit_carry'
          450_452  POP_JUMP_IF_FALSE   456  'to 456'

 L. 651       454  BREAK_LOOP       
            456_0  COME_FROM           450  '450'
            456_1  COME_FROM           444  '444'

 L. 653       456  LOAD_FAST                'is_curr_point_outside'
              458  STORE_FAST               'is_prev_point_outside'

 L. 654       460  LOAD_FAST                'time'
              462  STORE_FAST               'prev_time'

 L. 655       464  LOAD_FAST                'node'
              466  STORE_FAST               'prev_node'

 L. 656       468  LOAD_FAST                'force_no_carry'
              470  STORE_FAST               'prev_force_no_carry'
              472  JUMP_LOOP            94  'to 94'
              474  POP_BLOCK        
            476_0  COME_FROM_LOOP       74  '74'

 L. 658       476  LOAD_FAST                'self'
              478  LOAD_ATTR                _safety_umbrella_putaway_event
              480  LOAD_CONST               None
              482  COMPARE_OP               is
          484_486  POP_JUMP_IF_FALSE   556  'to 556'

 L. 659       488  LOAD_FAST                'path'
              490  LOAD_ATTR                final_location
              492  STORE_FAST               'location'

 L. 660       494  LOAD_GLOBAL              is_location_outside
              496  LOAD_FAST                'location'
              498  LOAD_ATTR                transform
              500  LOAD_ATTR                translation
              502  LOAD_FAST                'location'
              504  LOAD_ATTR                routing_surface
              506  LOAD_ATTR                secondary_id
              508  CALL_FUNCTION_2       2  '2 positional arguments'
          510_512  POP_JUMP_IF_TRUE    556  'to 556'

 L. 661       514  LOAD_FAST                'self'
              516  LOAD_ATTR                umbrella_route_events
              518  LOAD_ATTR                exit_carry_event
              520  LOAD_FAST                'self'
              522  LOAD_FAST                'path'
              524  LOAD_METHOD              duration
              526  CALL_METHOD_0         0  '0 positional arguments'
              528  LOAD_CONST               0.5
              530  BINARY_SUBTRACT  
              532  LOAD_CONST               ('provider', 'time')
              534  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              536  LOAD_FAST                'self'
              538  STORE_ATTR               _safety_umbrella_putaway_event

 L. 662       540  LOAD_FAST                'route_event_context'
              542  LOAD_METHOD              add_route_event
              544  LOAD_GLOBAL              RouteEventType
              546  LOAD_ATTR                LAST_OUTDOOR
              548  LOAD_FAST                'self'
              550  LOAD_ATTR                _safety_umbrella_putaway_event
              552  CALL_METHOD_2         2  '2 positional arguments'
              554  POP_TOP          
            556_0  COME_FROM           510  '510'
            556_1  COME_FROM           484  '484'

Parse error at or near `BREAK_LOOP' instruction at offset 454