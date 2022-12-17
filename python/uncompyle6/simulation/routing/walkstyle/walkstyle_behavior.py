# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\walkstyle\walkstyle_behavior.py
# Compiled at: 2022-11-01 17:51:01
# Size of source mod 2**32: 35451 bytes
import itertools, build_buy, operator
from gsi_handlers.walkstyle_handlers import WalkstyleGSIArchiver
from objects.pools.pond_utils import PondUtils
from primitives.routing_utils import get_block_id_for_node
from routing import SurfaceType, Location
from routing.walkstyle.walkstyle_enums import WalkStyleRunAllowedFlags
from routing.walkstyle.walkstyle_tuning import TunableWalkstyle
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableRange, TunableMapping, TunableList, TunableTuple, TunableEnumFlags, OptionalTunable, TunableReference, TunableEnumEntry, TunableSet
from terrain import get_water_depth_at_location, get_water_depth, is_terrain_tag_at_position
from world.ocean_tuning import OceanTuning
import gsi_handlers, services, sims4.math
from world.terrain_enums import TerrainTag
logger = sims4.log.Logger('WalkstyleBehavior')

class WalksStyleBehavior(HasTunableSingletonFactory, AutoFactoryInit):
    CARRY_INCOMPATIBLE_WALKSTYLES = TunableSet(description='\n        List of walkstyles that should be considered incompatible with the Sim carrying anything.\n        ',
      tunable=TunableWalkstyle(pack_safe=True))
    WALKSTYLE_COST = TunableMapping(description='\n        Associate a specific walkstyle to a statistic cost before the walkstyle\n        can be activated.\n        ',
      key_type=TunableWalkstyle(description='\n            The walkstyle that should have a specified cost when triggered.\n            ',
      pack_safe=True),
      value_type=TunableTuple(description='\n            Cost data of the specified walkstyle.\n            ',
      walkstyle_cost_statistic=TunableReference(description='\n                The statistic we are operating on when the walkstyle is\n                triggered.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      pack_safe=True),
      cost=TunableRange(description='\n                When the walkstyle is triggered during a route, this is the\n                cost that will be substracted from the specified statistic. \n                ',
      tunable_type=int,
      default=1,
      minimum=0)))
    TERRAIN_TAG_WALKSTYLES = TunableList(description='\n        Associate a terrain tag to a specific walkstyle.\n        ',
      tunable=TunableTuple(description='\n            The terrain tags and walkstyles that are associated.\n            ',
      terrain_tag=TunableEnumEntry(description='\n                The terrain tag that applies the tuned walkstyle.\n                ',
      tunable_type=TerrainTag,
      default=(TerrainTag.INVALID),
      invalid_enums=(
     TerrainTag.INVALID,)),
      walkstyle_to_use=TunableWalkstyle(description='\n                The walkstyle that should be used on the given terrain type.\n                ',
      pack_safe=True)))
    WALKSTYLES_OVERRIDE_TELEPORT = TunableList(description='\n        Any walkstyles found here will be able to override the teleport styles\n        if they are specified.\n        ',
      tunable=TunableWalkstyle(pack_safe=True))
    FACTORY_TUNABLES = {'carry_walkstyle_behavior':OptionalTunable(description='\n            Define the walkstyle the Sim plays whenever they are being carried\n            by another Sim.\n            \n            If this is set to "no behavior", the Sim will not react to the\n            parent\'s walkstyle at all. They will play no walkstyle, and rely on\n            posture idles to animate.\n            \n            If this is set, Sims have the ability to modify their walkstyle\n            whenever their parent is routing.\n            ',
       tunable=TunableTuple(description='\n                Specify how this Sim behaves when being carried by another Sim.\n                ',
       default_carry_walkstyle=TunableWalkstyle(description='\n                    Unless an override is specified, this is the walkstyle\n                    applied to the Sim whenever they are being carried.\n                    '),
       carry_walkstyle_overrides=TunableMapping(description='\n                    Define carry walkstyle overrides. For instance, we might\n                    want to specify a different carry walkstyle if the parent is\n                    frantically running, for example.\n                    ',
       key_type=TunableWalkstyle(description='\n                        The walkstyle that this carry walkstyle override applies to.\n                        ',
       pack_safe=True),
       value_type=TunableWalkstyle(description='\n                        The carry walkstyle override.\n                        ',
       pack_safe=True))),
       enabled_name='Apply_Carry_Walkstyle',
       disabled_name='No_Behavior'), 
     'combo_walkstyle_replacements':TunableList(description='\n            The prioritized list of the combo walkstyle replacement rules. We\n            use this list to decide if a Sim should use a combo walk style based\n            on the the highest priority walkstyle request, and other walkstyles\n            that might affect the replacement based on the key combo rules.\n            ',
       tunable=TunableTuple(description='\n                The n->1 mapping of walkstyle replacement. \n                ',
       key_combo_list=TunableList(description='\n                    The list of the walkstyles used as key combos. If the\n                    current highest priority walkstyle exists in this list, and\n                    the Sim has every other walkstyle in the key list, then we\n                    replace this with the result walkstyle tuned in the tuple.\n                    ',
       tunable=TunableWalkstyle(pack_safe=True)),
       result=TunableWalkstyle(description='\n                    The mapped combo walkstyle.\n                    ',
       pack_safe=True))), 
     'default_walkstyle':TunableWalkstyle(description='\n            The underlying walkstyle for this Sim. This is most likely going to\n            be overridden by the CAS walkstyle, emotional walkstyles, buff\n            walkstyles, etc...\n            '), 
     'run_allowed_flags':TunableEnumFlags(description="\n            Define where the Sim is allowed to run. Certain buffs might suppress\n            a Sim's ability to run.\n            ",
       enum_type=WalkStyleRunAllowedFlags,
       default=WalkStyleRunAllowedFlags.RUN_ALLOWED_OUTDOORS,
       allow_no_flags=True), 
     'run_required_total_distance':TunableRange(description='\n            For an entire route, the minimum distance required for Sim to run.\n            ',
       tunable_type=float,
       minimum=0,
       default=20), 
     'run_required_segment_distance':TunableRange(description='\n            For a specific route segment, the minimum distance required for the\n            Sim to run.\n            ',
       tunable_type=float,
       minimum=0,
       default=10), 
     'run_walkstyle':TunableWalkstyle(description='\n            The walkstyle to use when this Sim is supposed to be running.\n            '), 
     'wading_walkstyle':OptionalTunable(description='\n            If enabled, the routing agent will play a different walkstyle when\n            walking through water.\n            ',
       tunable=TunableWalkstyle(description='\n                The walkstyle to use when wading through water.\n                ')), 
     'wading_walkstyle_buff':OptionalTunable(description='\n            A buff which, if tuned, will be on the sim if the sim is currently\n            in wading level water.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.BUFF)))), 
     'short_walkstyle':TunableWalkstyle(description='\n            The walkstyle to use when Sims are routing over a distance shorter\n            than the one defined in "Short Walkstyle Distance" or any of the\n            overrides.\n            \n            This value is used if no override is tuned in "Short Walkstyle Map".\n            '), 
     'short_walkstyle_distance':TunableRange(description="\n            Any route whose distance is less than this value will request the\n            short version of the Sim's current walkstyle.\n            ",
       tunable_type=float,
       minimum=0,
       default=7), 
     'short_walkstyle_distance_override_map':TunableMapping(description="\n            If a Sim's current walkstyle is any of the ones specified in here,\n            use the associated value to determine if the short version of the\n            walkstyle is to be requested.\n            ",
       key_type=TunableWalkstyle(description='\n                The walkstyle that this distance override applies to.\n                ',
       pack_safe=True),
       value_type=TunableRange(description="\n                Any route whose distance is less than this value will request\n                the short version of the Sim's current walkstyle, provided the\n                Sim's current walkstyle is the associated walkstyle.\n                ",
       tunable_type=float,
       minimum=0,
       default=7)), 
     'short_walkstyle_map':TunableMapping(description='\n            Associate a specific short version of a walkstyle to walkstyles.\n            ',
       key_type=TunableWalkstyle(description='\n                The walkstyle that this short walkstyle mapping applies to.\n                ',
       pack_safe=True),
       value_type=TunableWalkstyle(description='\n                The short version of the associated walkstyle.\n                ',
       pack_safe=True))}

    def _get_walkstyle_overrides(self, actor):
        if actor.is_sim:
            return tuple((buff.walkstyle_behavior_override for buff in actor.get_active_buff_types() if buff.walkstyle_behavior_override is not None))
        return ()

    def _apply_run_walkstyle_to_path(self, actor, path, walkstyle_overrides, time_offset=None):
        run_allowed_flags = self.run_allowed_flags
        for walkstyle_override in walkstyle_overrides:
            run_allowed_flags |= walkstyle_override.additional_run_flags

        for walkstyle_override in walkstyle_overrides:
            run_allowed_flags &= ~walkstyle_override.removed_run_flags

        if not run_allowed_flags:
            return
        run_walkstyle = self._try_get_posture_compatible_run_walkstyle(actor)
        if run_walkstyle is None:
            return
        run_required_total_distance = sims4.math.safe_max((override for override in walkstyle_overrides if override.run_required_total_distance is not None), key=(operator.attrgetter('walkstyle_behavior_priority')),
          default=self).run_required_total_distance
        if path.length() < run_required_total_distance:
            return
        run_required_segment_distance = sims4.math.safe_max((override for override in walkstyle_overrides if override.run_required_segment_distance is not None), key=(operator.attrgetter('walkstyle_behavior_priority')),
          default=self).run_required_segment_distance
        path_nodes = list(path.nodes)
        all_path_node_data = []
        for start_node, end_node in zip(path_nodes, path_nodes[1:]):
            switch_routing_surface = start_node.routing_surface_id != end_node.routing_surface_id
            is_outside = start_node.portal_id == 0 and get_block_id_for_node(start_node) == 0
            route_key = (switch_routing_surface, is_outside)
            all_path_node_data.append((route_key, start_node, end_node))

        for (_, is_outside), path_node_data in itertools.groupby(all_path_node_data, key=(operator.itemgetter(0))):
            if is_outside:
                if not run_allowed_flags & WalkStyleRunAllowedFlags.RUN_ALLOWED_OUTDOORS:
                    continue
            if not is_outside:
                if not run_allowed_flags & WalkStyleRunAllowedFlags.RUN_ALLOWED_INDOORS:
                    continue
                path_node_data = list(path_node_data)
                segment_length = sum((((sims4.math.Vector3)(*start_node.position) - (sims4.math.Vector3)(*end_node.position)).magnitude_2d() for _, start_node, end_node in path_node_data))
                if segment_length < run_required_segment_distance:
                    continue
                for _, path_node, _ in path_node_data:
                    if not time_offset is None:
                        if path_node.time >= time_offset:
                            pass
                        path_node.walkstyle = run_walkstyle

    def check_for_wading(self, sim, *_, **__):
        routing_component = sim.routing_component
        if not routing_component.last_route_has_wading_nodes:
            if not routing_component.wading_buff_handle:
                return
            elif bool(build_buy.get_pond_id(sim.position)):
                wading_interval = PondUtils.get_actor_wading_interval(sim)
            else:
                wading_interval = OceanTuning.get_actor_wading_interval(sim)
            if wading_interval is None:
                return
            water_height = get_water_depth_at_location(sim.location)
            if water_height in wading_interval:
                if routing_component.wading_buff_handle is None:
                    routing_component.wading_buff_handle = sim.add_buff(self.wading_walkstyle_buff)
        elif routing_component.wading_buff_handle is not None:
            sim.remove_buff(routing_component.wading_buff_handle)
            routing_component.wading_buff_handle = None

    def _apply_terrain_walkstyle_to_path(self, actor, path, default_walkstyle, time_offset=None):
        tags = WalksStyleBehavior.TERRAIN_TAG_WALKSTYLES
        path_nodes = list(path.nodes)
        transition_tags = []
        transition_indices = []
        node_index = 0
        for n in path_nodes:
            if n.tracked_terrain_tags is not None:
                transition_tags.append(n.tracked_terrain_tags)
                transition_indices.append(node_index)
            node_index += 1

        transition_occurs = False
        for pair in tags:
            for tag_list in transition_tags:
                if any((int(pair.terrain_tag) in x for x in tag_list)):
                    transition_occurs = True
                    break

            start_in_walkstyle = is_terrain_tag_at_position(path_nodes[0].position[0], path_nodes[0].position[2], (pair.terrain_tag,))
            if not transition_occurs:
                if not start_in_walkstyle:
                    continue
            first_occurrence_index = None
            last_occurrence_index = None
            curr_index = 0
            if transition_occurs:
                for node_index in transition_indices:
                    if any((int(pair.terrain_tag) in x for x in transition_tags[curr_index])):
                        if first_occurrence_index is None:
                            first_occurrence_index = start_in_walkstyle or node_index
                        else:
                            last_occurrence_index = node_index
                    curr_index += 1

            for n in path_nodes[first_occurrence_index:last_occurrence_index]:
                if not time_offset is None:
                    if n.time >= time_offset:
                        pass
                    n.walkstyle = pair.walkstyle_to_use

    def _apply_wading_walkstyle_to_path(self, actor, path, default_walkstyle, time_offset=None):
        if actor.is_sim:
            if actor.sim_info.is_ghost:
                return False
        else:
            wading_interval_ocean = OceanTuning.get_actor_wading_interval(actor)
            wading_interval_pond = PondUtils.get_actor_wading_interval(actor)
            wading_walkstyle = self._get_wading_walkstyle(actor)
            if wading_walkstyle is None:
                return False

            def should_wade_at_position(position, level=0):
                depth = get_water_depth(position[0], position[2], level)
                if bool(build_buy.get_pond_id(sims4.math.Vector3(position[0], position[1], position[2]))):
                    wading_interval = wading_interval_pond
                else:
                    wading_interval = wading_interval_ocean
                if wading_interval is None:
                    return False
                return depth in wading_interval

            def get_node_water_height(path_node):
                return get_water_depth(path_node.position[0], path_node.position[2], path_node.routing_surface_id.secondary_id)

            path_nodes = list(path.nodes)
            start_wading = should_wade_at_position(path_nodes[0].position, path_nodes[0].routing_surface_id.secondary_id)
            end_wading = should_wade_at_position(path_nodes[(-1)].position, path_nodes[(-1)].routing_surface_id.secondary_id)
            if not start_wading:
                if not end_wading:
                    return False
        path_contains_wading = False
        for start_node, end_node in zip(path_nodes, path_nodes[1:]):
            if time_offset is not None:
                if end_node.time < time_offset:
                    continue
            if start_node.routing_surface_id.type == SurfaceType.SURFACETYPE_POOL:
                continue
            if start_node.portal_object_id != 0:
                continue
            start_wading = should_wade_at_position(start_node.position, start_node.routing_surface_id.secondary_id)
            end_wading = should_wade_at_position(end_node.position, end_node.routing_surface_id.secondary_id)
            if not start_wading:
                if not end_wading:
                    continue
                is_wading = start_wading
                if is_wading:
                    start_node.walkstyle = wading_walkstyle
                    path_contains_wading = True
                nodes_to_add = []
                for transform, routing_surface, time in path.get_location_data_along_segment_gen((start_node.index), (end_node.index), time_step=0.3):
                    should_wade = should_wade_at_position(transform.translation)
                    if is_wading:
                        if not should_wade:
                            is_wading = False
                            nodes_to_add.append((Location(transform.translation, transform.orientation, routing_surface), time, 0, default_walkstyle, 0, 0, end_node.index))
                    if is_wading or should_wade:
                        is_wading = True
                        nodes_to_add.append((Location(transform.translation, transform.orientation, routing_surface), time, 0, wading_walkstyle, 0, 0, end_node.index))
                        path_contains_wading = True

                running_index_offset = 0
                for loc, time, node_type, walkstyle, portal_obj_id, portal_id, index in nodes_to_add:
                    node_index = index + running_index_offset
                    path.nodes.add_node(loc, time, node_type, walkstyle, portal_obj_id, portal_id, node_index)
                    node = path.nodes[node_index]
                    node.is_procedural = False
                    running_index_offset += 1

        return path_contains_wading

    def apply_walkstyle_to_path(self, actor, path, time_offset=None):
        gsi_archiver = None
        can_archive = gsi_handlers.walkstyle_handlers.archiver.enabled and actor.is_sim
        if can_archive:
            gsi_archiver = WalkstyleGSIArchiver(actor)
        walkstyle = self.get_walkstyle_for_path(actor, path, gsi_archiver)
        if can_archive:
            gsi_archiver.gsi_archive_entry()
        path_nodes = list(path.nodes)
        for path_node in path_nodes:
            if time_offset is None or path_node.time >= time_offset:
                path_node.walkstyle = walkstyle

        walkstyle_overrides = self._get_walkstyle_overrides(actor)
        self._apply_run_walkstyle_to_path(actor, path, walkstyle_overrides, time_offset=time_offset)
        if actor.is_sim:
            self._apply_terrain_walkstyle_to_path(actor, path, walkstyle, time_offset=time_offset)
            actor.routing_component.last_route_has_wading_nodes = self._apply_wading_walkstyle_to_path(actor, path, walkstyle, time_offset=time_offset)
        return walkstyle

    def get_combo_replacement(self, highest_priority_walkstyle, walkstyle_list, exact_matches_only=True):
        for combo_tuple in self.combo_walkstyle_replacements:
            key_combo_list = combo_tuple.key_combo_list
            if highest_priority_walkstyle in key_combo_list:
                if exact_matches_only:
                    if all((ws in walkstyle_list for ws in key_combo_list)):
                        return combo_tuple
                if exact_matches_only or any((ws in walkstyle_list for ws in key_combo_list)):
                    return combo_tuple

    def _get_combo_replaced_walkstyle(self, highest_priority_walkstyle, walkstyle_list, exact_matches_only=True):
        combo_tuple = self.get_combo_replacement(highest_priority_walkstyle, walkstyle_list, exact_matches_only)
        if combo_tuple is not None:
            return combo_tuple.result

    def get_default_walkstyle_and_request(self, actor, gsi_archiver=None):
        walkstyle, request = actor.get_valid_walkstyle_and_request(WalksStyleBehavior.WALKSTYLE_COST)
        walkstyle_list = actor.get_walkstyle_list()
        replaced_walkstyle = self._get_combo_replaced_walkstyle(walkstyle, walkstyle_list)
        if gsi_archiver is not None:
            gsi_archiver.default_walkstyle = walkstyle
            gsi_archiver.combo_replacement_walkstyle_found = replaced_walkstyle
        if replaced_walkstyle is not None:
            walkstyle = replaced_walkstyle
            request = None
        return (walkstyle, request)

    def get_short_walkstyle(self, walkstyle, actor):
        short_walkstyle = self._get_property_override(actor, 'short_walkstyle')
        return self.short_walkstyle_map.get(walkstyle, short_walkstyle)

    def _try_get_posture_compatible_run_walkstyle(self, actor):
        posture = None
        if actor.is_sim:
            posture = actor.posture
        else:
            run_walkstyle = self._get_property_override(actor, 'run_walkstyle')
            return self._is_walkstyle_compatible_with_potential_posture(run_walkstyle, actor) or None
        return run_walkstyle

    def _get_wading_walkstyle(self, actor):
        wading_walkstyle = self._get_property_override(actor, 'wading_walkstyle')
        return wading_walkstyle

    def supports_wading_walkstyle_buff(self, actor):
        has_wading_data = OceanTuning.get_actor_wading_interval(actor) or PondUtils.get_actor_wading_interval(actor)
        return self.wading_walkstyle_buff is not None and has_wading_data

    def incompatible_with_carry(self, walkstyle_request):
        return walkstyle_request.walkstyle in self.CARRY_INCOMPATIBLE_WALKSTYLES

    def _get_property_override(self, actor, property_name):
        overrides = self._get_walkstyle_overrides(actor)
        override = sims4.math.safe_max((override for override in overrides if getattr(override, property_name) is not None), key=(operator.attrgetter('walkstyle_behavior_priority')),
          default=self)
        property_value = getattr(override, property_name)
        return property_value

    def _apply_walkstyle_cost(self, actor, walkstyle):
        walkstyle_cost = WalksStyleBehavior.WALKSTYLE_COST.get(walkstyle, None)
        if walkstyle_cost is not None:
            stat_instance = actor.get_stat_instance(walkstyle_cost.walkstyle_cost_statistic)
            if stat_instance is None:
                logger.error('Statistic {}, not found on Sim {} for walkstyle cost', (walkstyle_cost.walkstyle_cost_statistic), actor, owner='camilogarcia')
                return
            stat_instance.add_value(-walkstyle_cost.cost)

    def get_walkstyle_for_path(self, actor, path, gsi_archiver=None):
        walkstyle, request = self.get_default_walkstyle_and_request(actor, gsi_archiver)
        if gsi_archiver is not None:
            gsi_archiver.walkstyle_requests = actor.routing_component.get_walkstyle_requests()
        short_walk_distance = self.short_walkstyle_distance_override_map.get(walkstyle, self.short_walkstyle_distance)
        if path.length() < short_walk_distance:
            if request is None or request.can_replace_with_short_walkstyle:
                short_walkstyle = self._try_get_posture_compatible_short_walkstyle(walkstyle, actor)
                if short_walkstyle:
                    walkstyle = short_walkstyle
                    if gsi_archiver is not None:
                        gsi_archiver.default_walkstyle_replaced_by_short_walkstyle = walkstyle
        if actor.is_sim:
            posture = actor.posture
            if posture.mobile:
                if posture.compatible_walkstyles:
                    if walkstyle not in posture.compatible_walkstyles:
                        potential_walkstyle = posture.compatible_walkstyles[0]
                        walkstyles = actor.get_walkstyle_list()
                        replaced_walkstyle = self._get_combo_replaced_walkstyle(potential_walkstyle, walkstyles, False)
                        if replaced_walkstyle:
                            walkstyle = replaced_walkstyle
                        else:
                            walkstyle = potential_walkstyle
                        if gsi_archiver is not None:
                            if actor.in_pool:
                                gsi_archiver.default_walkstyle_replaced_by_swimming_walkstyle = walkstyle
                            else:
                                gsi_archiver.default_walkstyle_replaced_by_posture_walkstyle = walkstyle
                        return walkstyle
        return walkstyle

    def _try_get_posture_compatible_short_walkstyle(self, walkstyle, actor):
        short_walkstyle = self.get_short_walkstyle(walkstyle, actor)
        if not self._is_walkstyle_compatible_with_potential_posture(short_walkstyle, actor):
            return
        return short_walkstyle

    def _is_walkstyle_compatible_with_potential_posture(self, walkstyle, actor):
        if not actor.is_sim:
            return True
        else:
            posture = actor.posture
            return posture and posture.mobile or False
            return posture.compatible_walkstyles or True
        return walkstyle in posture.compatible_walkstyles