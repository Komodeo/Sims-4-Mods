# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\waypoints\waypoint_generator_lot.py
# Compiled at: 2020-03-05 18:24:04
# Size of source mod 2**32: 7886 bytes
from _collections import defaultdict
import itertools, math
from build_buy import get_all_block_polygons, get_block_id
from interactions.constraints import Anywhere, Circle
from plex import plex_enums
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase, WaypointContext
from routing.waypoints.waypoint_generator_tags import _WaypointGeneratorMultipleObjectByTag
from sims4.geometry import CompoundPolygon, random_uniform_points_in_compound_polygon, Polygon
from sims4.math import MAX_INT32
from sims4.tuning.tunable import TunableRange, OptionalTunable
import routing, services

class _WaypointGeneratorLotPoints(_WaypointGeneratorBase):
    FACTORY_TUNABLES = {'constraint_radius':TunableRange(description='\n            The radius, in meters, for each of the generated waypoint\n            constraints.\n            ',
       tunable_type=float,
       default=2,
       minimum=0), 
     'object_tag_generator':OptionalTunable(description='\n            If enabled, in addition to generating random points on the lot, this\n            generator also ensures that all constraints that would be generated\n            by the Tag generator are also hit.\n            \n            This gets you a very specific behavior: apparent randomness but the\n            guarantee that all objects with specific tags are route to.\n            ',
       tunable=_WaypointGeneratorMultipleObjectByTag.TunableFactory())}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim = self._context.sim

    def get_start_constraint(self):
        return self.get_water_constraint()

    def _get_polygons_for_lot(self):
        lot = services.active_lot()
        return [
         (
          CompoundPolygon(Polygon(list(reversed(lot.corners)))), self._routing_surface)]

    def _get_waypoint_constraints_from_polygons--- This code section failed: ---

 L.  67         0  LOAD_GLOBAL              dict
                2  LOAD_FAST                'object_constraints'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  STORE_FAST               'object_constraints'

 L.  70         8  LOAD_GLOBAL              sum
               10  LOAD_GENEXPR             '<code_object <genexpr>>'
               12  LOAD_STR                 '_WaypointGeneratorLotPoints._get_waypoint_constraints_from_polygons.<locals>.<genexpr>'
               14  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               16  LOAD_GLOBAL              itertools
               18  LOAD_ATTR                chain
               20  LOAD_METHOD              from_iterable
               22  LOAD_FAST                'polygons'
               24  LOAD_METHOD              values
               26  CALL_METHOD_0         0  '0 positional arguments'
               28  CALL_METHOD_1         1  '1 positional argument'
               30  GET_ITER         
               32  CALL_FUNCTION_1       1  '1 positional argument'
               34  CALL_FUNCTION_1       1  '1 positional argument'
               36  STORE_FAST               'total_area'

 L.  71        38  LOAD_FAST                'self'
               40  LOAD_ATTR                _sim
               42  LOAD_ATTR                routing_location
               44  STORE_FAST               'sim_location'

 L.  72        46  LOAD_FAST                'self'
               48  LOAD_ATTR                _sim
               50  LOAD_METHOD              get_routing_context
               52  CALL_METHOD_0         0  '0 positional arguments'
               54  STORE_FAST               'sim_routing_context'

 L.  76        56  LOAD_CONST               None
               58  STORE_FAST               'restriction'

 L.  77        60  LOAD_FAST                'self'
               62  LOAD_ATTR                object_tag_generator
               64  LOAD_CONST               None
               66  COMPARE_OP               is-not
               68  POP_JUMP_IF_FALSE    78  'to 78'

 L.  78        70  LOAD_FAST                'self'
               72  LOAD_ATTR                object_tag_generator
               74  LOAD_ATTR                placement_restriction
               76  STORE_FAST               'restriction'
             78_0  COME_FROM            68  '68'

 L.  80        78  BUILD_LIST_0          0 
               80  STORE_FAST               'final_constraints'

 L.  81        82  SETUP_LOOP          338  'to 338'
               84  LOAD_FAST                'polygons'
               86  LOAD_METHOD              items
               88  CALL_METHOD_0         0  '0 positional arguments'
               90  GET_ITER         
             92_0  COME_FROM           334  '334'
             92_1  COME_FROM           148  '148'
             92_2  COME_FROM           132  '132'
               92  FOR_ITER            336  'to 336'
               94  UNPACK_SEQUENCE_2     2 
               96  STORE_FAST               'block_id'
               98  STORE_FAST               'block_data'

 L.  83       100  LOAD_FAST                'object_constraints'
              102  LOAD_METHOD              pop
              104  LOAD_FAST                'block_id'
              106  LOAD_CONST               ()
              108  CALL_METHOD_2         2  '2 positional arguments'
              110  STORE_FAST               'block_object_constraints'

 L.  85       112  LOAD_FAST                'restriction'
              114  LOAD_CONST               None
              116  COMPARE_OP               is-not
              118  POP_JUMP_IF_FALSE   150  'to 150'

 L.  86       120  LOAD_FAST                'restriction'
              122  POP_JUMP_IF_FALSE   136  'to 136'
              124  LOAD_FAST                'block_id'
              126  LOAD_CONST               0
              128  COMPARE_OP               ==
              130  POP_JUMP_IF_FALSE   136  'to 136'

 L.  88       132  CONTINUE             92  'to 92'
              134  JUMP_FORWARD        150  'to 150'
            136_0  COME_FROM           130  '130'
            136_1  COME_FROM           122  '122'

 L.  89       136  LOAD_FAST                'restriction'
              138  POP_JUMP_IF_TRUE    150  'to 150'
              140  LOAD_FAST                'block_id'
              142  LOAD_CONST               0
              144  COMPARE_OP               !=
              146  POP_JUMP_IF_FALSE   150  'to 150'

 L.  91       148  CONTINUE             92  'to 92'
            150_0  COME_FROM           146  '146'
            150_1  COME_FROM           138  '138'
            150_2  COME_FROM           134  '134'
            150_3  COME_FROM           118  '118'

 L.  93       150  SETUP_LOOP          324  'to 324'
              152  LOAD_FAST                'block_data'
              154  GET_ITER         
            156_0  COME_FROM           320  '320'
              156  FOR_ITER            322  'to 322'
              158  UNPACK_SEQUENCE_2     2 
              160  STORE_FAST               'polygon'
              162  STORE_FAST               'routing_surface'

 L.  94       164  LOAD_GLOBAL              math
              166  LOAD_METHOD              ceil
              168  LOAD_FAST                'waypoint_count'
              170  LOAD_FAST                'polygon'
              172  LOAD_METHOD              area
              174  CALL_METHOD_0         0  '0 positional arguments'
              176  LOAD_FAST                'total_area'
              178  BINARY_TRUE_DIVIDE
              180  BINARY_MULTIPLY  
              182  CALL_METHOD_1         1  '1 positional argument'
              184  STORE_FAST               'polygon_waypoint_count'

 L.  95       186  SETUP_LOOP          320  'to 320'
              188  LOAD_GLOBAL              random_uniform_points_in_compound_polygon
              190  LOAD_FAST                'polygon'
              192  LOAD_GLOBAL              int
              194  LOAD_FAST                'polygon_waypoint_count'
              196  CALL_FUNCTION_1       1  '1 positional argument'
              198  LOAD_CONST               ('num',)
              200  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              202  GET_ITER         
            204_0  COME_FROM           316  '316'
            204_1  COME_FROM           240  '240'
              204  FOR_ITER            318  'to 318'
              206  STORE_FAST               'position'

 L. 105       208  LOAD_GLOBAL              routing
              210  LOAD_ATTR                test_connectivity_pt_pt
              212  LOAD_FAST                'sim_location'
              214  LOAD_GLOBAL              routing
              216  LOAD_ATTR                Location
              218  LOAD_FAST                'position'
              220  LOAD_FAST                'self'
              222  LOAD_ATTR                _routing_surface
              224  LOAD_CONST               ('routing_surface',)
              226  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              228  LOAD_FAST                'sim_routing_context'
              230  LOAD_FAST                'self'
              232  LOAD_ATTR                _sim
              234  LOAD_CONST               ('ignore_objects',)
              236  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              238  POP_JUMP_IF_TRUE    242  'to 242'

 L. 106       240  CONTINUE            204  'to 204'
            242_0  COME_FROM           238  '238'

 L. 107       242  LOAD_GLOBAL              Circle
              244  LOAD_FAST                'position'
              246  LOAD_FAST                'self'
              248  LOAD_ATTR                constraint_radius
              250  LOAD_FAST                'routing_surface'
              252  LOAD_CONST               ('routing_surface',)
              254  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              256  STORE_FAST               'position_constraint'

 L. 108       258  SETUP_LOOP          306  'to 306'
              260  LOAD_GLOBAL              tuple
              262  LOAD_FAST                'block_object_constraints'
              264  CALL_FUNCTION_1       1  '1 positional argument'
              266  GET_ITER         
            268_0  COME_FROM           300  '300'
            268_1  COME_FROM           286  '286'
              268  FOR_ITER            304  'to 304'
              270  STORE_FAST               'block_object_constraint'

 L. 109       272  LOAD_FAST                'block_object_constraint'
              274  LOAD_METHOD              intersect
              276  LOAD_FAST                'position_constraint'
              278  CALL_METHOD_1         1  '1 positional argument'
              280  STORE_FAST               'intersection'

 L. 110       282  LOAD_FAST                'intersection'
              284  LOAD_ATTR                valid
          286_288  POP_JUMP_IF_FALSE_LOOP   268  'to 268'

 L. 111       290  LOAD_FAST                'block_object_constraints'
              292  LOAD_METHOD              remove
              294  LOAD_FAST                'block_object_constraint'
              296  CALL_METHOD_1         1  '1 positional argument'
              298  POP_TOP          
          300_302  JUMP_LOOP           268  'to 268'
              304  POP_BLOCK        
            306_0  COME_FROM_LOOP      258  '258'

 L. 112       306  LOAD_FAST                'final_constraints'
              308  LOAD_METHOD              append
              310  LOAD_FAST                'position_constraint'
              312  CALL_METHOD_1         1  '1 positional argument'
              314  POP_TOP          
              316  JUMP_LOOP           204  'to 204'
              318  POP_BLOCK        
            320_0  COME_FROM_LOOP      186  '186'
              320  JUMP_LOOP           156  'to 156'
              322  POP_BLOCK        
            324_0  COME_FROM_LOOP      150  '150'

 L. 114       324  LOAD_FAST                'final_constraints'
              326  LOAD_METHOD              extend
              328  LOAD_FAST                'block_object_constraints'
              330  CALL_METHOD_1         1  '1 positional argument'
              332  POP_TOP          
              334  JUMP_LOOP            92  'to 92'
              336  POP_BLOCK        
            338_0  COME_FROM_LOOP       82  '82'

 L. 117       338  LOAD_FAST                'final_constraints'
              340  LOAD_METHOD              extend
              342  LOAD_GLOBAL              itertools
              344  LOAD_ATTR                chain
              346  LOAD_METHOD              from_iterable
              348  LOAD_FAST                'object_constraints'
              350  LOAD_METHOD              values
              352  CALL_METHOD_0         0  '0 positional arguments'
              354  CALL_METHOD_1         1  '1 positional argument'
              356  CALL_METHOD_1         1  '1 positional argument'
              358  POP_TOP          

 L. 118       360  LOAD_FAST                'final_constraints'
              362  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `JUMP_LOOP' instruction at offset 334

    def get_waypoint_constraints_gen(self, routing_agent, waypoint_count):
        zone_id = services.current_zone_id()
        object_constraints = defaultdict(list)
        if self.object_tag_generator is not None:
            object_tag_generator = self.object_tag_generatorWaypointContext(self._sim)None
            for constraint in itertools.chain(object_tag_generator.get_start_constraint(),)object_tag_generator.get_waypoint_constraints_genrouting_agentMAX_INT32:
                level = constraint.routing_surface.secondary_id
                block_id = get_block_id(zone_id, constraint.average_position, level)
                object_constraints[block_id].appendconstraint

        plex_id = services.get_plex_service().get_active_zone_plex_id() or plex_enums.INVALID_PLEX_ID
        block_data = get_all_block_polygons(plex_id)
        polygons = defaultdict(list)
        if self._routing_surface.secondary_id == 0:
            polygons[0] = self._get_polygons_for_lot()
        for block_id, (polys, level) in block_data.items():
            if level != self._routing_surface.secondary_id:
                continue
            else:
                polygon = CompoundPolygon([Polygon(list(reversed(p))) for p in polys])
            if not polygon.area():
                continue
            else:
                polygons[block_id].append(polygon, self._routing_surface)

        if not polygons:
            return False
        final_constraints = self._get_waypoint_constraints_from_polygons(polygons, object_constraints, waypoint_count)
        final_constraints = self.apply_water_constraintfinal_constraints
        yield from final_constraints
        if False:
            yield None