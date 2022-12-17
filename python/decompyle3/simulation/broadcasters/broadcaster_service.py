# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\broadcasters\broadcaster_service.py
# Compiled at: 2020-11-19 12:20:58
# Size of source mod 2**32: 31263 bytes
from _collections import defaultdict
from _weakrefset import WeakSet
from collections import namedtuple
from alarms import add_alarm_real_time, cancel_alarm, add_alarm
from clock import interval_in_real_seconds
from indexed_manager import CallbackTypes
from routing.route_enums import RouteEventType
from sims4.callback_utils import CallableList
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableRealSecond
import services, sims4.geometry, sims4.log, sims4.math
logger = sims4.log.Logger('Broadcaster', default_owner='epanero')

class BroadcasterService(Service):
    INTERVAL = TunableRealSecond(description='\n        The time between broadcaster pulses. A lower number will impact\n        performance.\n        ',
      default=5)
    DEFAULT_QUADTREE_RADIUS = 0.1

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._alarm_handle = None
        self._processing_task = None
        self._on_update_callbacks = CallableList()
        self._pending_broadcasters = []
        self._active_broadcasters = []
        self._cluster_requests = {}
        self._object_cache = None
        self._object_cache_tags = None
        self._pending_update = False
        self._quadtrees = defaultdict(sims4.geometry.QuadTree)

    def create_update_alarm(self):
        self._alarm_handle = add_alarm(self, (interval_in_real_seconds(self.INTERVAL)), (self._on_update), repeating=True, use_sleep_time=False)

    def start(self):
        self.create_update_alarm()
        object_manager = services.object_manager()
        object_manager.register_callback(CallbackTypes.ON_OBJECT_LOCATION_CHANGED, self._update_object_cache)
        object_manager.register_callback(CallbackTypes.ON_OBJECT_ADD, self._update_object_cache)
        services.current_zone().wall_contour_update_callbacks.append(self._on_wall_contours_changed)

    def stop(self):
        if self._alarm_handle is not None:
            cancel_alarm(self._alarm_handle)
            self._alarm_handle = None
        if self._processing_task is not None:
            self._processing_task.stop()
            self._processing_task = None
        object_manager = services.object_manager()
        object_manager.unregister_callback(CallbackTypes.ON_OBJECT_LOCATION_CHANGED, self._update_object_cache)
        object_manager.unregister_callback(CallbackTypes.ON_OBJECT_ADD, self._update_object_cache)
        services.current_zone().wall_contour_update_callbacks.remove(self._on_wall_contours_changed)

    def add_broadcaster(self, broadcaster):
        if broadcaster not in self._pending_broadcasters:
            self._pending_broadcasters.append(broadcaster)
            if broadcaster.immediate:
                self._pending_update = True
            self._on_update_callbacks()

    def remove_broadcaster(self, broadcaster):
        if broadcaster in self._pending_broadcasters:
            self._pending_broadcasters.remove(broadcaster)
        if broadcaster in self._active_broadcasters:
            self._remove_from_cluster_request(broadcaster)
            self._remove_broadcaster_from_quadtree(broadcaster)
            self._active_broadcasters.remove(broadcaster)
        broadcaster.on_removed()
        self._on_update_callbacks()

    def _activate_pending_broadcasters(self):
        for broadcaster in self._pending_broadcasters:
            self._active_broadcasters.append(broadcaster)
            self.update_cluster_request(broadcaster)
            self._update_object_cache()

        self._pending_broadcasters.clear()

    def _add_broadcaster_to_quadtree(self, broadcaster):
        self._remove_broadcaster_from_quadtree(broadcaster)
        broadcaster_quadtree = self._quadtrees[broadcaster.routing_surface.secondary_id]
        broadcaster_bounds = sims4.geometry.QtCircle(sims4.math.Vector2(broadcaster.position.x, broadcaster.position.z), self.DEFAULT_QUADTREE_RADIUS)
        broadcaster_quadtree.insert(broadcaster, broadcaster_bounds)
        return broadcaster_quadtree

    def _remove_broadcaster_from_quadtree(self, broadcaster):
        broadcaster_quadtree = broadcaster.quadtree
        if broadcaster_quadtree is not None:
            broadcaster_quadtree.remove(broadcaster)

    def update_cluster_request(self, broadcaster):
        if broadcaster not in self._active_broadcasters:
            return
        clustering_request = broadcaster.get_clustering()
        if clustering_request is None:
            return
        self._remove_from_cluster_request(broadcaster)
        cluster_request_key = (type(broadcaster), broadcaster.routing_surface.secondary_id)
        if cluster_request_key in self._cluster_requests:
            cluster_request = self._cluster_requests[cluster_request_key]
            cluster_request.set_object_dirty(broadcaster)
        else:
            cluster_quadtree = self._quadtrees[broadcaster.routing_surface.secondary_id]
            cluster_request = clustering_request((lambda: (self._get_broadcasters_for_cluster_request_gen)(*cluster_request_key)
), quadtree=cluster_quadtree)
            self._cluster_requests[cluster_request_key] = cluster_request
        quadtree = self._add_broadcaster_to_quadtree(broadcaster)
        broadcaster.on_added_to_quadtree_and_cluster_request(quadtree, cluster_request)

    def _remove_from_cluster_request(self, broadcaster):
        cluster_request = broadcaster.cluster_request
        if cluster_request is not None:
            cluster_request.set_object_dirty(broadcaster)

    def _is_valid_cache_object(self, obj):
        if obj.is_sim:
            return False
        if self._object_cache_tags:
            object_tags = obj.get_tags()
            if object_tags & self._object_cache_tags:
                return True
            return False
        return True

    def get_object_cache_info(self):
        return (
         self._object_cache, self._object_cache_tags)

    def _generate_object_cache(self):
        self._object_cache = WeakSet((obj for obj in services.object_manager().valid_objects() if self._is_valid_cache_object(obj)))

    def _update_object_cache(self, obj=None):
        if obj is None:
            self._object_cache = None
            self._object_cache_tags = None
            return
        if self._object_cache is not None:
            if self._is_valid_cache_object(obj):
                self._object_cache.add(obj)

    def _is_valid_broadcaster(self, broadcaster):
        broadcasting_object = broadcaster.broadcasting_object
        if not (broadcasting_object is None or broadcasting_object.visible_to_client):
            return False
        if broadcasting_object.is_in_inventory():
            return False
        if broadcasting_object.parent is not None:
            if broadcasting_object.parent.is_sim:
                return False
        return True

    def _get_broadcasters_for_cluster_request_gen(self, broadcaster_type, broadcaster_level):
        for broadcaster in self._active_broadcasters:
            if broadcaster.guid == broadcaster_type.guid:
                if broadcaster.should_cluster():
                    if broadcaster.routing_surface.secondary_id == broadcaster_level:
                        yield broadcaster

    def get_broadcasters_debug_gen(self):
        for cluster_request in self._cluster_requests.values():
            for cluster in cluster_request.get_clusters_gen():
                broadcaster_iter = cluster.objects_gen()
                yield next(broadcaster_iter)

            yield from cluster_request.get_rejects()

        for broadcaster in self._active_broadcasters:
            if not broadcaster.should_cluster():
                if self._is_valid_broadcaster(broadcaster):
                    yield broadcaster

    def get_broadcasters_gen(self):
        for cluster_request_key, cluster_request in self._cluster_requests.items():
            is_cluster_dirty = cluster_request.is_dirty()
            if is_cluster_dirty:
                for broadcaster in (self._get_broadcasters_for_cluster_request_gen)(*cluster_request_key):
                    if self._is_valid_broadcaster(broadcaster):
                        broadcaster.regenerate_constraint()

            for cluster in cluster_request.get_clusters_gen():
                linkable_broadcasters_iter = (b for b in cluster.objects_gen() if self._is_valid_broadcaster(b))
                master_broadcaster = next(linkable_broadcasters_iter, None)
                if master_broadcaster is None:
                    continue
                else:
                    master_broadcaster.set_linked_broadcasters(linkable_broadcasters_iter)
                    yield master_broadcaster

            yield from (b for b in cluster_request.get_rejects() if self._is_valid_broadcaster(b))

        for broadcaster in self._active_broadcasters:
            if not broadcaster.should_cluster():
                if self._is_valid_broadcaster(broadcaster):
                    yield broadcaster

    PathSegmentData = namedtuple('PathSegmentData', ('prev_pos', 'cur_pos', 'segment_vec',
                                                     'segment_mag_sq', 'segment_normal'))

    def get_broadcasters_along_route_gen--- This code section failed: ---

 L. 339         0  BUILD_MAP_0           0 
                2  STORE_FAST               'path_segment_datas'

 L. 343         4  LOAD_GLOBAL              max
                6  LOAD_CONST               0
                8  LOAD_FAST                'path'
               10  LOAD_METHOD              node_at_time
               12  LOAD_FAST                'start_time'
               14  CALL_METHOD_1         1  '1 positional argument'
               16  LOAD_ATTR                index
               18  LOAD_CONST               1
               20  BINARY_SUBTRACT  
               22  CALL_FUNCTION_2       2  '2 positional arguments'
               24  STORE_FAST               'start_index'

 L. 344        26  LOAD_GLOBAL              min
               28  LOAD_GLOBAL              len
               30  LOAD_FAST                'path'
               32  CALL_FUNCTION_1       1  '1 positional argument'
               34  LOAD_CONST               1
               36  BINARY_SUBTRACT  
               38  LOAD_FAST                'path'
               40  LOAD_METHOD              node_at_time
               42  LOAD_FAST                'end_time'
               44  CALL_METHOD_1         1  '1 positional argument'
               46  LOAD_ATTR                index
               48  CALL_FUNCTION_2       2  '2 positional arguments'
               50  STORE_FAST               'end_index'

 L. 345     52_54  SETUP_LOOP          784  'to 784'
               56  LOAD_FAST                'self'
               58  LOAD_METHOD              get_broadcasters_gen
               60  CALL_METHOD_0         0  '0 positional arguments'
               62  GET_ITER         
             64_0  COME_FROM           780  '780'
             64_1  COME_FROM           768  '768'
             64_2  COME_FROM           134  '134'
             64_3  COME_FROM           126  '126'
             64_4  COME_FROM           110  '110'
             64_5  COME_FROM            86  '86'
             64_6  COME_FROM            74  '74'
            64_66  FOR_ITER            782  'to 782'
               68  STORE_FAST               'broadcaster'

 L. 346        70  LOAD_FAST                'broadcaster'
               72  LOAD_ATTR                route_events
               74  POP_JUMP_IF_FALSE_LOOP    64  'to 64'
               76  LOAD_FAST                'broadcaster'
               78  LOAD_METHOD              can_affect
               80  LOAD_FAST                'sim'
               82  CALL_METHOD_1         1  '1 positional argument'
               84  POP_JUMP_IF_TRUE     88  'to 88'

 L. 348        86  CONTINUE             64  'to 64'
             88_0  COME_FROM            84  '84'

 L. 350        88  LOAD_FAST                'broadcaster'
               90  LOAD_METHOD              get_constraint
               92  CALL_METHOD_0         0  '0 positional arguments'
               94  STORE_FAST               'constraint'

 L. 351        96  LOAD_FAST                'constraint'
               98  LOAD_ATTR                geometry
              100  STORE_FAST               'geometry'

 L. 352       102  LOAD_FAST                'geometry'
              104  LOAD_CONST               None
              106  COMPARE_OP               is
              108  POP_JUMP_IF_FALSE   112  'to 112'

 L. 353       110  CONTINUE             64  'to 64'
            112_0  COME_FROM           108  '108'

 L. 355       112  LOAD_FAST                'geometry'
              114  LOAD_ATTR                polygon
              116  STORE_FAST               'polygon'

 L. 356       118  LOAD_FAST                'polygon'
              120  LOAD_CONST               None
              122  COMPARE_OP               is
              124  POP_JUMP_IF_FALSE   128  'to 128'

 L. 357       126  CONTINUE             64  'to 64'
            128_0  COME_FROM           124  '124'

 L. 359       128  LOAD_FAST                'constraint'
              130  LOAD_ATTR                valid
              132  POP_JUMP_IF_TRUE    136  'to 136'

 L. 361       134  CONTINUE             64  'to 64'
            136_0  COME_FROM           132  '132'

 L. 363       136  LOAD_CONST               None
              138  STORE_FAST               'found_time'

 L. 365       140  LOAD_FAST                'polygon'
              142  LOAD_METHOD              centroid
              144  CALL_METHOD_0         0  '0 positional arguments'
              146  STORE_FAST               'constraint_pos'

 L. 366       148  LOAD_FAST                'polygon'
              150  LOAD_METHOD              radius
              152  CALL_METHOD_0         0  '0 positional arguments'
              154  STORE_FAST               'constraint_radius_sq'

 L. 367       156  LOAD_FAST                'constraint_radius_sq'
              158  LOAD_FAST                'constraint_radius_sq'
              160  BINARY_MULTIPLY  
              162  STORE_FAST               'constraint_radius_sq'

 L. 368   164_166  SETUP_LOOP          762  'to 762'
              168  LOAD_GLOBAL              range
              170  LOAD_FAST                'end_index'
              172  LOAD_FAST                'start_index'
              174  LOAD_CONST               -1
              176  CALL_FUNCTION_3       3  '3 positional arguments'
              178  GET_ITER         
            180_0  COME_FROM           758  '758'
            180_1  COME_FROM           754  '754'
            180_2  COME_FROM           548  '548'
            180_3  COME_FROM           462  '462'
            180_4  COME_FROM           460  '460'
            180_5  COME_FROM           448  '448'
            180_6  COME_FROM           418  '418'
            180_7  COME_FROM           216  '216'
          180_182  FOR_ITER            760  'to 760'
              184  STORE_FAST               'index'

 L. 369       186  LOAD_FAST                'index'
              188  LOAD_CONST               1
              190  BINARY_SUBTRACT  
              192  STORE_FAST               'prev_index'

 L. 370       194  LOAD_FAST                'path'
              196  LOAD_ATTR                nodes
              198  LOAD_FAST                'prev_index'
              200  BINARY_SUBSCR    
              202  STORE_FAST               'prev_node'

 L. 371       204  LOAD_FAST                'constraint'
              206  LOAD_METHOD              is_routing_surface_valid
              208  LOAD_FAST                'prev_node'
              210  LOAD_ATTR                routing_surface_id
              212  CALL_METHOD_1         1  '1 positional argument'
              214  POP_JUMP_IF_TRUE    218  'to 218'

 L. 373       216  CONTINUE            180  'to 180'
            218_0  COME_FROM           214  '214'

 L. 376       218  LOAD_FAST                'prev_index'
              220  LOAD_FAST                'index'
              222  BUILD_TUPLE_2         2 
              224  STORE_FAST               'segment_key'

 L. 377       226  LOAD_FAST                'path_segment_datas'
              228  LOAD_METHOD              get
              230  LOAD_FAST                'segment_key'
              232  LOAD_CONST               None
              234  CALL_METHOD_2         2  '2 positional arguments'
              236  STORE_FAST               'segment_data'

 L. 378       238  LOAD_FAST                'segment_data'
              240  LOAD_CONST               None
              242  COMPARE_OP               is
          244_246  POP_JUMP_IF_FALSE   368  'to 368'

 L. 379       248  LOAD_FAST                'path'
              250  LOAD_ATTR                nodes
              252  LOAD_FAST                'index'
              254  BINARY_SUBSCR    
              256  STORE_FAST               'cur_node'

 L. 380       258  LOAD_GLOBAL              sims4
              260  LOAD_ATTR                math
              262  LOAD_ATTR                Vector3
              264  LOAD_FAST                'cur_node'
              266  LOAD_ATTR                position
              268  CALL_FUNCTION_EX      0  'positional arguments only'
              270  STORE_FAST               'cur_pos'

 L. 381       272  LOAD_GLOBAL              sims4
              274  LOAD_ATTR                math
              276  LOAD_ATTR                Vector3
              278  LOAD_FAST                'prev_node'
              280  LOAD_ATTR                position
              282  CALL_FUNCTION_EX      0  'positional arguments only'
              284  STORE_FAST               'prev_pos'

 L. 382       286  LOAD_FAST                'cur_pos'
              288  LOAD_FAST                'prev_pos'
              290  BINARY_SUBTRACT  
              292  STORE_FAST               'segment_vec'

 L. 383       294  LOAD_FAST                'segment_vec'
              296  LOAD_METHOD              magnitude_2d_squared
              298  CALL_METHOD_0         0  '0 positional arguments'
              300  STORE_FAST               'segment_mag_sq'

 L. 384       302  LOAD_GLOBAL              sims4
              304  LOAD_ATTR                math
              306  LOAD_METHOD              almost_equal_sq
              308  LOAD_FAST                'segment_mag_sq'
              310  LOAD_CONST               0
              312  CALL_METHOD_2         2  '2 positional arguments'
          314_316  POP_JUMP_IF_FALSE   324  'to 324'

 L. 385       318  LOAD_CONST               None
              320  STORE_FAST               'unit_segment'
              322  JUMP_FORWARD        340  'to 340'
            324_0  COME_FROM           314  '314'

 L. 387       324  LOAD_FAST                'segment_vec'
              326  LOAD_GLOBAL              sims4
              328  LOAD_ATTR                math
              330  LOAD_METHOD              sqrt
              332  LOAD_FAST                'segment_mag_sq'
              334  CALL_METHOD_1         1  '1 positional argument'
              336  BINARY_TRUE_DIVIDE
              338  STORE_FAST               'unit_segment'
            340_0  COME_FROM           322  '322'

 L. 388       340  LOAD_GLOBAL              BroadcasterService
              342  LOAD_METHOD              PathSegmentData
              344  LOAD_FAST                'prev_pos'
              346  LOAD_FAST                'cur_pos'
              348  LOAD_FAST                'segment_vec'
              350  LOAD_FAST                'segment_mag_sq'
              352  LOAD_FAST                'unit_segment'
              354  CALL_METHOD_5         5  '5 positional arguments'
              356  STORE_FAST               'segment_data'

 L. 389       358  LOAD_FAST                'segment_data'
              360  LOAD_FAST                'path_segment_datas'
              362  LOAD_FAST                'segment_key'
              364  STORE_SUBSCR     
              366  JUMP_FORWARD        382  'to 382'
            368_0  COME_FROM           244  '244'

 L. 391       368  LOAD_FAST                'segment_data'
              370  UNPACK_SEQUENCE_5     5 
              372  STORE_FAST               'prev_pos'
              374  STORE_FAST               'cur_pos'
              376  STORE_FAST               'segment_vec'
              378  STORE_FAST               'segment_mag_sq'
              380  STORE_FAST               'unit_segment'
            382_0  COME_FROM           366  '366'

 L. 393       382  LOAD_FAST                'constraint_pos'
              384  LOAD_FAST                'prev_pos'
              386  BINARY_SUBTRACT  
              388  STORE_FAST               'constraint_vec'

 L. 395       390  LOAD_FAST                'unit_segment'
              392  LOAD_CONST               None
              394  COMPARE_OP               is
          396_398  POP_JUMP_IF_FALSE   464  'to 464'

 L. 397       400  LOAD_FAST                'constraint_vec'
              402  LOAD_METHOD              magnitude_2d_squared
              404  CALL_METHOD_0         0  '0 positional arguments'
              406  STORE_FAST               'constraint_dist_sq'

 L. 398       408  LOAD_FAST                'constraint_radius_sq'
              410  LOAD_FAST                'constraint_dist_sq'
              412  COMPARE_OP               <
          414_416  POP_JUMP_IF_FALSE   420  'to 420'

 L. 399       418  CONTINUE            180  'to 180'
            420_0  COME_FROM           414  '414'

 L. 402       420  LOAD_FAST                'geometry'
              422  LOAD_METHOD              test_transform
              424  LOAD_GLOBAL              sims4
              426  LOAD_ATTR                math
              428  LOAD_METHOD              Transform
              430  LOAD_FAST                'prev_pos'
              432  LOAD_GLOBAL              sims4
              434  LOAD_ATTR                math
              436  LOAD_ATTR                Quaternion
              438  LOAD_FAST                'prev_node'
              440  LOAD_ATTR                orientation
              442  CALL_FUNCTION_EX      0  'positional arguments only'
              444  CALL_METHOD_2         2  '2 positional arguments'
              446  CALL_METHOD_1         1  '1 positional argument'
              448  POP_JUMP_IF_FALSE_LOOP   180  'to 180'

 L. 403       450  LOAD_FAST                'prev_node'
              452  LOAD_ATTR                time
              454  STORE_FAST               'found_time'

 L. 405       456  BREAK_LOOP       
              458  JUMP_FORWARD        462  'to 462'

 L. 407       460  CONTINUE            180  'to 180'
            462_0  COME_FROM           458  '458'
              462  JUMP_LOOP           180  'to 180'
            464_0  COME_FROM           396  '396'

 L. 410       464  LOAD_GLOBAL              sims4
              466  LOAD_ATTR                math
              468  LOAD_METHOD              vector_dot_2d
              470  LOAD_FAST                'constraint_vec'
              472  LOAD_FAST                'unit_segment'
              474  CALL_METHOD_2         2  '2 positional arguments'
              476  STORE_FAST               'constraint_comp'

 L. 411       478  LOAD_FAST                'constraint_comp'
              480  LOAD_CONST               0
              482  COMPARE_OP               <=
          484_486  POP_JUMP_IF_FALSE   494  'to 494'

 L. 413       488  LOAD_FAST                'prev_pos'
              490  STORE_FAST               'closest'
              492  JUMP_FORWARD        526  'to 526'
            494_0  COME_FROM           484  '484'

 L. 414       494  LOAD_FAST                'constraint_comp'
              496  LOAD_FAST                'constraint_comp'
              498  BINARY_MULTIPLY  
              500  LOAD_FAST                'segment_mag_sq'
              502  COMPARE_OP               >=
          504_506  POP_JUMP_IF_FALSE   514  'to 514'

 L. 416       508  LOAD_FAST                'cur_pos'
              510  STORE_FAST               'closest'
              512  JUMP_FORWARD        526  'to 526'
            514_0  COME_FROM           504  '504'

 L. 419       514  LOAD_FAST                'prev_pos'
              516  LOAD_FAST                'unit_segment'
              518  LOAD_FAST                'constraint_comp'
              520  BINARY_MULTIPLY  
              522  BINARY_ADD       
              524  STORE_FAST               'closest'
            526_0  COME_FROM           512  '512'
            526_1  COME_FROM           492  '492'

 L. 421       526  LOAD_FAST                'constraint_pos'
              528  LOAD_FAST                'closest'
              530  BINARY_SUBTRACT  
              532  STORE_FAST               'proj_vec'

 L. 422       534  LOAD_FAST                'constraint_radius_sq'
              536  LOAD_FAST                'proj_vec'
              538  LOAD_METHOD              magnitude_2d_squared
              540  CALL_METHOD_0         0  '0 positional arguments'
              542  COMPARE_OP               <
          544_546  POP_JUMP_IF_FALSE   550  'to 550'

 L. 423       548  CONTINUE            180  'to 180'
            550_0  COME_FROM           544  '544'

 L. 430       550  LOAD_CONST               2
              552  LOAD_GLOBAL              sims4
              554  LOAD_ATTR                math
              556  LOAD_METHOD              vector_dot_2d
              558  LOAD_FAST                'constraint_vec'
              560  LOAD_FAST                'segment_vec'
              562  CALL_METHOD_2         2  '2 positional arguments'
              564  BINARY_MULTIPLY  
              566  STORE_FAST               'b'

 L. 431       568  LOAD_FAST                'b'
              570  LOAD_FAST                'b'
              572  BINARY_MULTIPLY  
              574  LOAD_CONST               4
              576  LOAD_FAST                'segment_mag_sq'
              578  BINARY_MULTIPLY  
              580  LOAD_FAST                'constraint_vec'
              582  LOAD_METHOD              magnitude_2d_squared
              584  CALL_METHOD_0         0  '0 positional arguments'
              586  LOAD_FAST                'constraint_radius_sq'
              588  BINARY_SUBTRACT  
              590  BINARY_MULTIPLY  
              592  BINARY_SUBTRACT  
              594  STORE_FAST               'discriminant'

 L. 432       596  LOAD_GLOBAL              sims4
              598  LOAD_ATTR                math
              600  LOAD_METHOD              sqrt
              602  LOAD_FAST                'discriminant'
              604  CALL_METHOD_1         1  '1 positional argument'
              606  STORE_FAST               'discriminant'

 L. 433       608  LOAD_CONST               2
              610  LOAD_FAST                'segment_mag_sq'
              612  BINARY_MULTIPLY  
              614  STORE_FAST               'denom'

 L. 436       616  LOAD_FAST                'b'
              618  LOAD_FAST                'discriminant'
              620  BINARY_SUBTRACT  
              622  LOAD_FAST                'denom'
              624  BINARY_TRUE_DIVIDE
              626  STORE_FAST               't1'

 L. 437       628  LOAD_FAST                'b'
              630  LOAD_FAST                'discriminant'
              632  BINARY_ADD       
              634  LOAD_FAST                'denom'
              636  BINARY_TRUE_DIVIDE
              638  STORE_FAST               't2'

 L. 439       640  LOAD_CONST               (0, 1)
              642  UNPACK_SEQUENCE_2     2 
              644  STORE_FAST               'normalized_start'
              646  STORE_FAST               'normalized_end'

 L. 440       648  LOAD_FAST                't1'
              650  LOAD_CONST               0
              652  COMPARE_OP               >=
          654_656  POP_JUMP_IF_FALSE   672  'to 672'
              658  LOAD_FAST                't1'
              660  LOAD_CONST               1
              662  COMPARE_OP               <=
          664_666  POP_JUMP_IF_FALSE   672  'to 672'

 L. 441       668  LOAD_FAST                't1'
              670  STORE_FAST               'normalized_start'
            672_0  COME_FROM           664  '664'
            672_1  COME_FROM           654  '654'

 L. 442       672  LOAD_FAST                't2'
              674  LOAD_CONST               0
              676  COMPARE_OP               >=
          678_680  POP_JUMP_IF_FALSE   696  'to 696'
              682  LOAD_FAST                't2'
              684  LOAD_CONST               1
              686  COMPARE_OP               <=
          688_690  POP_JUMP_IF_FALSE   696  'to 696'

 L. 443       692  LOAD_FAST                't2'
              694  STORE_FAST               'normalized_end'
            696_0  COME_FROM           688  '688'
            696_1  COME_FROM           678  '678'

 L. 446       696  SETUP_LOOP          756  'to 756'
              698  LOAD_FAST                'path'
              700  LOAD_ATTR                get_location_data_along_segment_gen
              702  LOAD_FAST                'prev_index'
              704  LOAD_FAST                'index'

 L. 447       706  LOAD_FAST                'normalized_start'

 L. 448       708  LOAD_FAST                'normalized_end'
              710  LOAD_CONST               ('start_time', 'stop_time')
              712  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              714  GET_ITER         
            716_0  COME_FROM           748  '748'
            716_1  COME_FROM           738  '738'
              716  FOR_ITER            752  'to 752'
              718  UNPACK_SEQUENCE_3     3 
              720  STORE_FAST               'transform'
              722  STORE_FAST               '_'
              724  STORE_FAST               'time'

 L. 449       726  LOAD_FAST                'geometry'
              728  LOAD_METHOD              test_transform
              730  LOAD_FAST                'transform'
              732  CALL_METHOD_1         1  '1 positional argument'
          734_736  POP_JUMP_IF_TRUE    742  'to 742'

 L. 450   738_740  CONTINUE            716  'to 716'
            742_0  COME_FROM           734  '734'

 L. 451       742  LOAD_FAST                'time'
              744  STORE_FAST               'found_time'

 L. 452       746  BREAK_LOOP       
          748_750  JUMP_LOOP           716  'to 716'
              752  POP_BLOCK        

 L. 455       754  CONTINUE            180  'to 180'
            756_0  COME_FROM_LOOP      696  '696'

 L. 459       756  BREAK_LOOP       
              758  JUMP_LOOP           180  'to 180'
              760  POP_BLOCK        
            762_0  COME_FROM_LOOP      164  '164'

 L. 461       762  LOAD_FAST                'found_time'
              764  LOAD_CONST               None
              766  COMPARE_OP               is-not
              768  POP_JUMP_IF_FALSE_LOOP    64  'to 64'

 L. 462       770  LOAD_FAST                'found_time'
              772  LOAD_FAST                'broadcaster'
              774  BUILD_TUPLE_2         2 
              776  YIELD_VALUE      
              778  POP_TOP          
              780  JUMP_LOOP            64  'to 64'
              782  POP_BLOCK        
            784_0  COME_FROM_LOOP       52  '52'

Parse error at or near `COME_FROM' instruction at offset 464_0

    def get_pending_broadcasters_gen(self):
        yield from self._pending_broadcasters
        if False:
            yield None

    def _get_all_objects_gen(self):
        is_any_broadcaster_allowing_objects = True if self._object_cache else False
        if not is_any_broadcaster_allowing_objects:
            for broadcaster in self._active_broadcasters:
                allow_objects, allow_objects_tags = broadcaster.allow_objects.is_affecting_objects()
                if allow_objects:
                    is_any_broadcaster_allowing_objects = True
                    if allow_objects_tags is None:
                        self._object_cache_tags = None
                        break
                    else:
                        if self._object_cache_tags is None:
                            self._object_cache_tags = set()
                        self._object_cache_tags |= allow_objects_tags

        if is_any_broadcaster_allowing_objects:
            if self._object_cache is None:
                self._generate_object_cache()
            yield from list(self._object_cache)
        else:
            self._object_cache = None
            self._object_cache_tags = None
        yield from services.sim_info_manager().instanced_sims_gen()
        if False:
            yield None

    def register_callback(self, callback):
        if callback not in self._on_update_callbacks:
            self._on_update_callbacks.append(callback)

    def unregister_callback(self, callback):
        if callback in self._on_update_callbacks:
            self._on_update_callbacks.remove(callback)

    def _on_update(self, _):
        self._pending_update = True

    def _on_wall_contours_changed(self, *_, **__):
        self._update_object_cache()

    def provide_route_events(self, route_event_context, sim, path, failed_types=None, start_time=0, end_time=0, **kwargs):
        for time, broadcaster in self.get_broadcasters_along_route_gen(sim, path, start_time=start_time, end_time=end_time):
            resolver = broadcaster.get_resolver(sim)
            for route_event in broadcaster.route_events:
                if broadcaster.can_provide_route_event(route_event, failed_types, resolver):
                    if not route_event_context.route_event_already_scheduled(route_event, provider=broadcaster):
                        route_event_context.add_route_event(RouteEventType.BROADCASTER, route_event(time=time, provider=broadcaster, provider_required=True))

    def update(self):
        if self._pending_update:
            self._pending_update = False
            self._update()

    def _is_location_affected(self, constraint, transform, routing_surface):
        if constraint.geometry is not None:
            if not constraint.geometry.test_transform(transform):
                return False
            if not constraint.is_routing_surface_valid(routing_surface):
                return False
            return True

    def update_broadcasters_one_shot(self, broadcasters):
        for obj in self._get_all_objects_gen():
            object_transform = None
            routing_surface = obj.routing_surface
            for broadcaster in broadcasters:
                if broadcaster.can_affect(obj):
                    constraint = broadcaster.get_constraint()
                    if not constraint.valid:
                        continue
                    elif object_transform is None:
                        parent = obj.parent
                        if parent is None:
                            object_transform = obj.transform
                        else:
                            object_transform = parent.transform
                    if self._is_location_affected(constraint, object_transform, routing_surface):
                        broadcaster.apply_broadcaster_effect(obj)
                        broadcaster.remove_broadcaster_effect(obj)
                        if not obj.valid_for_distribution:
                            break

    def _update(self):
        try:
            self._activate_pending_broadcasters()
            current_broadcasters = set(self.get_broadcasters_gen())
            for obj in self._get_all_objects_gen():
                object_transform = None
                is_affected = False
                for broadcaster in current_broadcasters:
                    if broadcaster.can_affect(obj):
                        constraint = broadcaster.get_constraint()
                        if not constraint.valid:
                            continue
                        elif object_transform is None:
                            parent = obj.parent
                            if parent is None:
                                object_transform = obj.transform
                            else:
                                object_transform = parent.transform
                        if self._is_location_affected(constraint, object_transform, obj.routing_surface):
                            broadcaster.apply_broadcaster_effect(obj)
                            if not obj.valid_for_distribution:
                                is_affected = False
                                break
                            else:
                                is_affected = True

                if not is_affected:
                    if self._object_cache is not None:
                        self._object_cache.discard(obj)

            for broadcaster in current_broadcasters:
                broadcaster.on_processed()

        finally:
            self._on_update_callbacks()


class BroadcasterRealTimeService(BroadcasterService):

    def create_update_alarm(self):
        self._alarm_handle = add_alarm_real_time(self, (interval_in_real_seconds(self.INTERVAL)), (self._on_update), repeating=True, use_sleep_time=False)