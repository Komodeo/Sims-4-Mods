# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\satisfy_constraint_interaction.py
# Compiled at: 2019-07-08 13:12:44
# Size of source mod 2**32: 19728 bytes
from _math import Vector3
from animation.posture_manifest_constants import STAND_OR_SIT_CONSTRAINT, STAND_OR_MOVING_STAND_CONSTRAINT, STAND_AT_NONE_CONSTRAINT
from event_testing.results import TestResult
from interactions import ParticipantType
from interactions.base.super_interaction import SuperInteraction
from interactions.base.tuningless_interaction import create_tuningless_superinteraction
from interactions.constraints import Constraint, build_weighted_cone, WaterDepthIntervals, OceanStartLocationConstraint, ANYWHERE, Nowhere
from interactions.utils.routing import PlanRoute
from objects.pools import pool_utils
from sims4.collections import frozendict
from sims4.tuning.instances import lock_instance_tunables
from sims4.utils import flexmethod, classproperty
from singletons import DEFAULT
import element_utils, interactions, routing, services, sims4.geometry, sims4.log, sims4.math
logger = sims4.log.Logger('SatisfyConstraintInteraction')
PRIVACY_MIN_DISTANCE = 1

class SitOrStandSuperInteraction(SuperInteraction):

    @classmethod
    def _is_linked_to(cls, super_affordance):
        return True

    @classmethod
    def _test(cls, target, context, allow_posture_changes=False, **kwargs):
        if not context.sim.posture.mobile:
            if not allow_posture_changes:
                return TestResult(False, 'Sims can only satisfy constraints when they are mobile.')
            if context.sim.is_dying:
                return TestResult(False, 'Sims cannot satisfy constraints when they are dying.')
            return (super()._test)(target, context, **kwargs)

    @classproperty
    def super_affordance_can_share_target(cls):
        return True

    def is_adjustment_interaction(self):
        return self._is_adjustment_interaction

    def __init__(self, *args, constraint_to_satisfy=DEFAULT, run_element=None, is_adjustment_interaction=False, **kwargs):
        (super().__init__)(*args, **kwargs)
        if constraint_to_satisfy is DEFAULT:
            constraint_to_satisfy = STAND_OR_SIT_CONSTRAINT
        self._constraint_to_satisfy = constraint_to_satisfy
        self._run_element = run_element
        self._is_adjustment_interaction = is_adjustment_interaction

    @flexmethod
    def constraint_intersection(cls, inst, sim=DEFAULT, participant_type=ParticipantType.Actor, **kwargs):
        if not inst is None:
            if participant_type != ParticipantType.Actor or inst._constraint_to_satisfy is None:
                return ANYWHERE
            if inst._constraint_to_satisfy is not DEFAULT:
                return inst._constraint_to_satisfy
            if sim is DEFAULT:
                sim = inst.get_participant(participant_type)
            return sim.si_state.get_total_constraint(to_exclude=inst)

    def _run_interaction_gen(self, timeline):
        self.sim.routing_component.on_slot = None
        result = yield from super()._run_interaction_gen(timeline)
        if not result:
            return False
        if self._run_element is not None:
            result = yield from element_utils.run_child(timeline, self._run_element)
            return result
        return True
        if False:
            yield None


lock_instance_tunables(SitOrStandSuperInteraction, _constraints=(frozendict()), _constraints_actor=(ParticipantType.Object))

class SatisfyConstraintSuperInteraction(SitOrStandSuperInteraction):
    INSTANCE_SUBCLASSES_ONLY = True


create_tuningless_superinteraction(SatisfyConstraintSuperInteraction)

class ForceSatisfyConstraintSuperInteraction(SatisfyConstraintSuperInteraction):
    INSTANCE_SUBCLASSES_ONLY = True

    @classmethod
    def is_adjustment_interaction(cls):
        return False


create_tuningless_superinteraction(ForceSatisfyConstraintSuperInteraction)

class ExitMobilePostureSuperInteraction(SuperInteraction):
    PERIMETER_WIDTH = 2.0

    def __init__(self, *args, run_element=None, is_adjustment_interaction=False, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._run_element = run_element
        self._is_adjustment_interaction = is_adjustment_interaction

    @classmethod
    def _is_linked_to(cls, super_affordance):
        return True

    @classproperty
    def super_affordance_can_share_target(cls):
        return True

    @classmethod
    def _get_exit_mobile_posture_constraint(cls, sim, participant_type=ParticipantType.Actor):
        posture_graph_service = services.current_zone().posture_graph_service
        posture_obj = posture_graph_service.get_compatible_mobile_posture_target(sim)
        if posture_obj is not None:
            return posture_obj.get_edge_constraint(sim=sim)
        return STAND_AT_NONE_CONSTRAINT

    @flexmethod
    def constraint_intersection(cls, inst, sim=DEFAULT, participant_type=ParticipantType.Actor, **kwargs):
        if participant_type != ParticipantType.Actor:
            return ANYWHERE
        inst_or_cls = inst if inst is not None else cls
        if sim is DEFAULT:
            sim = inst_or_cls.get_participant(participant_type)
        exit_posture_constraint = inst_or_cls._get_exit_mobile_posture_constraint(sim, participant_type=participant_type)
        return exit_posture_constraint

    def is_adjustment_interaction(self):
        return self._is_adjustment_interaction

    def _run_interaction_gen(self, timeline):
        self.sim.routing_component.on_slot = None
        result = yield from super()._run_interaction_gen(timeline)
        if not result:
            return False
        if self._run_element is not None:
            result = yield from element_utils.run_child(timeline, self._run_element)
            return result
        return True
        if False:
            yield None


class BuildAndForceSatisfyShooConstraintInteraction(SuperInteraction):
    INSTANCE_SUBCLASSES_ONLY = True
    TRIVIAL_SHOO_RADIUS = 0.5
    PLEX_LOT_CORNER_ADJUSTMENT = 2.0

    def __init__(self, *args, privacy_inst=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._must_run_instance = True
        self._privacy = privacy_inst

    def _run_interaction_gen(self, timeline):
        result = yield from super()._run_interaction_gen(timeline)
        if not result:
            return False
        if self._privacy is not None:
            constraint_to_satisfy = yield from self._create_constraint_set(self.context.sim, timeline)
            if not constraint_to_satisfy.valid:
                constraint_to_satisfy = Nowhere('BuildAndForceSatisfyShooConstraintInteraction._run_interaction_gen, constraint_to_satisfy({}) is not valid, SI: {}', constraint_to_satisfy, self)
                logger.warn('Failed to generate a valid Shoo constraint. Defaulting to Nowhere().')
        else:
            logger.error('Trying to create a BuildAndForceSatisfyShooConstraintInteraction without a valid privacy instance.', owner='tastle')
            constraint_to_satisfy = Nowhere('BuildAndForceSatisfyShooConstraintInteraction._run_interaction_gen, SI has no valid privacy instance: {}', self)
        context = self.context.clone_for_continuation(self)
        constraint_to_satisfy = constraint_to_satisfy.intersect(STAND_OR_MOVING_STAND_CONSTRAINT)
        result = self.sim.push_super_affordance(ForceSatisfyConstraintSuperInteraction, None, context, allow_posture_changes=True, constraint_to_satisfy=constraint_to_satisfy,
          name_override='ShooFromPrivacy')
        if not result:
            logger.debug('Failed to push ForceSatisfyConstraintSuperInteraction on Sim {} to route them out of a privacy area.  Result: {}', (self.sim), result, owner='tastle')
        return result
        if False:
            yield None

    def _find_close_position--- This code section failed: ---

 L. 233         0  LOAD_CONST               False
                2  STORE_FAST               'found_new_position'

 L. 234         4  LOAD_CONST               False
                6  STORE_FAST               'invalid_pos'

 L. 235         8  LOAD_CONST               False
               10  STORE_FAST               'valid_pos'

 L. 236        12  SETUP_LOOP          140  'to 140'
             14_0  COME_FROM           136  '136'
             14_1  COME_FROM           122  '122'
               14  LOAD_FAST                'found_new_position'
               16  POP_JUMP_IF_TRUE    138  'to 138'

 L. 238        18  LOAD_GLOBAL              sims4
               20  LOAD_ATTR                math
               22  LOAD_METHOD              Vector3
               24  LOAD_FAST                'p1'
               26  LOAD_ATTR                x
               28  LOAD_FAST                'p2'
               30  LOAD_ATTR                x
               32  BINARY_ADD       
               34  LOAD_CONST               2
               36  BINARY_TRUE_DIVIDE
               38  LOAD_FAST                'p1'
               40  LOAD_ATTR                y
               42  LOAD_FAST                'p1'
               44  LOAD_ATTR                z
               46  LOAD_FAST                'p2'
               48  LOAD_ATTR                z
               50  BINARY_ADD       
               52  LOAD_CONST               2
               54  BINARY_TRUE_DIVIDE
               56  CALL_METHOD_3         3  '3 positional arguments'
               58  STORE_FAST               'p3'

 L. 239        60  LOAD_FAST                'p1'
               62  LOAD_FAST                'p3'
               64  BINARY_SUBTRACT  
               66  LOAD_METHOD              magnitude_2d
               68  CALL_METHOD_0         0  '0 positional arguments'
               70  LOAD_GLOBAL              PRIVACY_MIN_DISTANCE
               72  COMPARE_OP               <=
               74  POP_JUMP_IF_FALSE    80  'to 80'

 L. 246        76  LOAD_FAST                'p1'
               78  RETURN_VALUE     
             80_0  COME_FROM            74  '74'

 L. 248        80  LOAD_GLOBAL              sims4
               82  LOAD_ATTR                geometry
               84  LOAD_METHOD              test_point_in_compound_polygon
               86  LOAD_FAST                'p3'
               88  LOAD_FAST                'self'
               90  LOAD_ATTR                _privacy
               92  LOAD_ATTR                constraint
               94  LOAD_ATTR                geometry
               96  LOAD_ATTR                polygon
               98  CALL_METHOD_2         2  '2 positional arguments'
              100  POP_JUMP_IF_TRUE    124  'to 124'

 L. 249       102  LOAD_CONST               True
              104  STORE_FAST               'valid_pos'

 L. 250       106  LOAD_FAST                'p3'
              108  STORE_FAST               'p1'

 L. 253       110  LOAD_FAST                'invalid_pos'
              112  POP_JUMP_IF_FALSE   136  'to 136'
              114  LOAD_FAST                'valid_pos'
              116  POP_JUMP_IF_FALSE   136  'to 136'

 L. 254       118  LOAD_CONST               True
              120  STORE_FAST               'found_new_position'
              122  JUMP_LOOP            14  'to 14'
            124_0  COME_FROM           100  '100'

 L. 260       124  LOAD_FAST                'valid_pos'
              126  POP_JUMP_IF_FALSE   132  'to 132'

 L. 261       128  LOAD_CONST               True
              130  STORE_FAST               'invalid_pos'
            132_0  COME_FROM           126  '126'

 L. 262       132  LOAD_FAST                'p3'
              134  STORE_FAST               'p2'
            136_0  COME_FROM           116  '116'
            136_1  COME_FROM           112  '112'
              136  JUMP_LOOP            14  'to 14'
            138_0  COME_FROM            16  '16'
              138  POP_BLOCK        
            140_0  COME_FROM_LOOP       12  '12'

 L. 263       140  LOAD_FAST                'p3'
              142  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `POP_BLOCK' instruction at offset 138

    def _create_constraint_set(self, sim, timeline):
        orient = sims4.math.Quaternion.IDENTITY()
        positions = services.current_zone().lot.corners
        position = positions[0]
        routing_surface = self._privacy.constraint.get_world_routing_surface(force_world=True)
        if self._privacy._routing_surface_only:
            routing_surfaces = (
             routing_surface,)
        else:
            routing_surfaces = self._privacy.constraint.get_all_valid_routing_surfaces()
        goals = []
        center_pos = services.current_zone().lot.position
        for pos in positions:
            plex_service = services.get_plex_service()
            if plex_service.is_active_zone_a_plex():
                towards_center_vec = sims4.math.vector_normalize(center_pos - pos)
                pos = pos + towards_center_vec * self.PLEX_LOT_CORNER_ADJUSTMENT
                pos.y = services.terrain_service.terrain_object().get_routing_surface_height_atpos.xpos.zrouting_surface
            if not sims4.geometry.test_point_in_compound_polygon(pos, self._privacy.constraint.geometry.polygon):
                for surface in routing_surfaces:
                    goals.append(routing.Goal(routing.Locationposorientsurface))

        obj_pos = self._privacy.central_object.position
        for offset in self._privacy.additional_exit_offsets:
            goals.append(routing.Goal(routing.Location(obj_pos + Vector3(offset.x, 0, offset.y))orientsurface))

        if not goals:
            return Nowhere('BuildAndForceSatisfyShooConstraintInteraction, Could not generate goals to exit a privacy region, Sim: {} Privacy Region: {}', sim, self._privacy.constraint.geometry.polygon)
        route = routing.Route((sim.routing_location), goals, routing_context=(sim.routing_context))
        plan_primitive = PlanRoute(route, sim, reserve_final_location=False, interaction=self)
        yield from element_utils.run_child(timeline, plan_primitive)
        max_distance = self._privacy._max_line_of_sight_radius * self._privacy._max_line_of_sight_radius * 4
        nodes = []
        path = plan_primitive.path
        while path is not None:
            nodes.extend(path.nodes)
            path = path.next_path

        if nodes:
            previous_node = nodes[0]
            for node in nodes:
                node_vector = sims4.math.Vector3node.position[0]node.position[1]node.position[2]
                if not sims4.geometry.test_point_in_compound_polygon(node_vector, self._privacy.constraint.geometry.polygon):
                    position = node_vector
                    if node.portal_id != 0:
                        continue
                    else:
                        circle_constraint = interactions.constraints.Circlepositionself.TRIVIAL_SHOO_RADIUSnode.routing_surface_id
                    if circle_constraint.intersect(self._privacy.constraint).valid:
                        continue
                    break
                else:
                    previous_node = node

            position2 = sims4.math.Vector3previous_node.position[0]previous_node.position[1]previous_node.position[2]
            if (position - position2).magnitude_2d_squared() > max_distance:
                position = self._find_close_position(position, position2)
        else:
            if (position - sim.position).magnitude_2d_squared() > max_distance:
                position = self._find_close_position(position, sim.position)
        p1 = position
        p2 = self._privacy.central_object.position
        forward = sims4.math.vector_normalize(p1 - p2)
        radius_min = 0
        radius_max = self._privacy.shoo_constraint_radius
        angle = sims4.math.PI
        cone_geometry, cost_functions = build_weighted_cone(position, forward, radius_min, radius_max, angle, ideal_radius_min=0,
          ideal_radius_max=0,
          ideal_angle=1)
        subtracted_cone_polygon_list = []
        for cone_polygon in cone_geometry.polygon:
            for privacy_polygon in self._privacy.constraint.geometry.polygon:
                subtracted_cone_polygons = cone_polygon.subtract(privacy_polygon)
                if subtracted_cone_polygons:
                    subtracted_cone_polygon_list.extend(subtracted_cone_polygons)

        compound_subtracted_cone_polygon = sims4.geometry.CompoundPolygon(subtracted_cone_polygon_list)
        subtracted_cone_geometry = sims4.geometry.RestrictedPolygon(compound_subtracted_cone_polygon, [])
        subtracted_cone_constraint = Constraint(geometry=subtracted_cone_geometry, scoring_functions=cost_functions,
          routing_surface=routing_surface,
          debug_name='ShooedSimsCone',
          multi_surface=True,
          los_reference_point=position)
        point_cost = 5
        point_constraint = interactions.constraints.Position(position, routing_surface=routing_surface, multi_surface=True)
        point_constraint = point_constraint.generate_constraint_with_cost(point_cost)
        constraints = (
         subtracted_cone_constraint, point_constraint)
        return interactions.constraints.create_constraint_set(constraints, debug_name='ShooPositions')
        if False:
            yield None

    @classmethod
    def _is_linked_to(cls, super_affordance):
        return True


create_tuningless_superinteraction(BuildAndForceSatisfyShooConstraintInteraction)