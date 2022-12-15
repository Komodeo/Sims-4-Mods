# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\favorites\favorites_tracker.py
# Compiled at: 2020-11-02 12:04:30
# Size of source mod 2**32: 12814 bytes
import build_buy, services, sims4.log
from distributor.rollback import ProtocolBufferRollback
from event_testing.test_events import TestEvent
from objects.components.inventory_enums import StackScheme
from protocolbuffers import SimObjectAttributes_pb2
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.utils import classproperty
logger = sims4.log.Logger('FavoritesTracker', default_owner='trevor')
OBJ_ID = 0
DEF_ID = 1
KEY_ID = 0
STACK_TYPE_ID = 1

class FavoritesTracker(SimInfoTracker):

    def __init__(self, sim_info):
        self._owner = sim_info
        self._favorites = None
        self._favorite_stacks = []

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.BACKGROUND

    @property
    def favorites(self):
        return self._favorites

    @property
    def favorite_stacks(self):
        return self._favorite_stacks

    def has_favorite(self, tag):
        return self._favorites and tag in self._favorites

    def set_favorite(self, tag, obj_id=None, obj_def_id=None):
        if self._favorites is None:
            self._favorites = {}
            services.get_event_manager().register_single_event(self, TestEvent.ObjectDestroyed)
        if tag in self._favorites:
            logger.debug('Old favorite with object ID {} object definition ID {} is being overwritten by object ID {} object definition ID {} for tag {}.', self._favorites[tag][OBJ_ID], self._favorites[tag][DEF_ID], obj_id, obj_def_id, tag)
        if obj_id is not None:
            if obj_def_id is None:
                obj = services.object_manager().get(obj_id)
                if obj is not None:
                    obj_def_id = obj.definition.id
        self._favorites[tag] = (
         obj_id, obj_def_id)
        return True

    def unset_favorite(self, tag, obj_id=None, obj_def_id=None):
        fav_obj_id, fav_def_id = self.get_favorite(tag)
        if not (fav_obj_id is not None and fav_obj_id == obj_id):
            if not fav_def_id is not None or fav_def_id == obj_def_id:
                del self._favorites[tag]
                if not self._favorites:
                    self.clean_up()

    def clear_favorite_type(self, tag):
        if tag in self._favorites:
            del self._favorites[tag]
            if not self._favorites:
                self.clean_up()

    def _unset_favorite_object(self, obj_id=None, obj_def_id=None):
        if self._favorites is None:
            return
        favorite_types = []
        for favorite_type, fav in self._favorites.items():
            if not (fav[OBJ_ID] is not None and fav[OBJ_ID] == obj_id):
                if fav[DEF_ID] is not None:
                    if fav[DEF_ID] == obj_def_id:
                        pass
                    favorite_types.append(favorite_type)

        for favorite_type in favorite_types:
            self.unset_favorite(favorite_type, obj_id, obj_def_id)

    def get_favorite(self, tag):
        if self._favorites is None:
            return (None, None)
        return self._favorites.get(tag, (None, None))

    def get_favorite_object_id(self, tag):
        fav_obj_id, _ = self.get_favorite(tag)
        return fav_obj_id

    def is_favorite(self, tag, obj, instance_must_match=True):
        fav_obj_id, fav_def_id = self.get_favorite(tag)
        if fav_obj_id is not None:
            if fav_obj_id == obj.id:
                return True
        if not instance_must_match:
            if fav_def_id is not None:
                if fav_def_id == obj.definition.id:
                    return True
        return False

    def get_favorite_definition_id(self, tag):
        _, fav_def_id = self.get_favorite(tag)
        return fav_def_id

    def set_favorite_stack(self, obj):
        key = self._get_stack_key(obj)
        if key is None or key in self._favorite_stacks:
            return
        self._favorite_stacks.append(key)

    def unset_favorite_stack(self, obj):
        if len(self._favorite_stacks) == 0:
            return
        key = self._get_stack_key(obj)
        if key is None or key not in self._favorite_stacks:
            return
        self._favorite_stacks.remove(key)

    def is_favorite_stack(self, obj):
        key = self._get_stack_key(obj)
        return key is not None and key in self._favorite_stacks

    def _get_stack_key(self, obj):
        inv_component = obj.inventoryitem_component
        if inv_component is None:
            return
        stack_scheme = inv_component.get_stack_scheme()
        if stack_scheme == StackScheme.NONE:
            key = obj.id
        else:
            if stack_scheme == StackScheme.VARIANT_GROUP:
                key = build_buy.get_variant_group_id(obj.definition.id)
            else:
                if stack_scheme == StackScheme.DEFINITION:
                    key = obj.definition.id
                else:
                    key = stack_scheme
        return [
         key, stack_scheme]

    def clean_up(self):
        if self._favorites is not None:
            self._favorites = None
            services.get_event_manager().unregister_single_event(self, TestEvent.ObjectDestroyed)
        if len(self._favorite_stacks) > 0:
            self._favorite_stacks = []

    def handle_event(self, _, event, resolver):
        if event == TestEvent.ObjectDestroyed:
            destroyed_obj_id = resolver.get_resolved_arg('obj').id
            self._unset_favorite_object(destroyed_obj_id)

    def on_lod_update(self, old_lod, new_lod):
        if new_lod < self._tracker_lod_threshold:
            self.clean_up()
        else:
            if old_lod < self._tracker_lod_threshold:
                msg = services.get_persistence_service().get_sim_proto_buff(self._owner.id)
                if msg is not None:
                    self.load(msg.attributes.favorites_tracker)

    def save--- This code section failed: ---

 L. 259         0  LOAD_GLOBAL              SimObjectAttributes_pb2
                2  LOAD_METHOD              PersistableFavoritesTracker
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'data'

 L. 260         8  LOAD_FAST                'self'
               10  LOAD_ATTR                _favorites
               12  LOAD_CONST               None
               14  COMPARE_OP               is-not
               16  POP_JUMP_IF_FALSE   102  'to 102'

 L. 261        18  SETUP_LOOP          102  'to 102'
               20  LOAD_FAST                'self'
               22  LOAD_ATTR                _favorites
               24  LOAD_METHOD              items
               26  CALL_METHOD_0         0  '0 positional arguments'
               28  GET_ITER         
             30_0  COME_FROM            98  '98'
               30  FOR_ITER            100  'to 100'
               32  UNPACK_SEQUENCE_2     2 
               34  STORE_FAST               'tag'
               36  UNPACK_SEQUENCE_2     2 
               38  STORE_FAST               'object_id'
               40  STORE_FAST               'object_def_id'

 L. 262        42  LOAD_GLOBAL              ProtocolBufferRollback
               44  LOAD_FAST                'data'
               46  LOAD_ATTR                favorites
               48  CALL_FUNCTION_1       1  '1 positional argument'
               50  SETUP_WITH           92  'to 92'
               52  STORE_FAST               'entry'

 L. 263        54  LOAD_FAST                'tag'
               56  LOAD_FAST                'entry'
               58  STORE_ATTR               favorite_type

 L. 265        60  LOAD_FAST                'object_id'
               62  LOAD_CONST               None
               64  COMPARE_OP               is-not
               66  POP_JUMP_IF_FALSE    74  'to 74'

 L. 266        68  LOAD_FAST                'object_id'
               70  LOAD_FAST                'entry'
               72  STORE_ATTR               favorite_id
             74_0  COME_FROM            66  '66'

 L. 268        74  LOAD_FAST                'object_def_id'
               76  LOAD_CONST               None
               78  COMPARE_OP               is-not
               80  POP_JUMP_IF_FALSE    88  'to 88'

 L. 269        82  LOAD_FAST                'object_def_id'
               84  LOAD_FAST                'entry'
               86  STORE_ATTR               favorite_def_id
             88_0  COME_FROM            80  '80'
               88  POP_BLOCK        
               90  LOAD_CONST               None
             92_0  COME_FROM_WITH       50  '50'
               92  WITH_CLEANUP_START
               94  WITH_CLEANUP_FINISH
               96  END_FINALLY      
               98  JUMP_LOOP            30  'to 30'
              100  POP_BLOCK        
            102_0  COME_FROM_LOOP       18  '18'
            102_1  COME_FROM            16  '16'

 L. 271       102  LOAD_GLOBAL              len
              104  LOAD_FAST                'self'
              106  LOAD_ATTR                _favorite_stacks
              108  CALL_FUNCTION_1       1  '1 positional argument'
              110  POP_JUMP_IF_TRUE    116  'to 116'

 L. 272       112  LOAD_FAST                'data'
              114  RETURN_VALUE     
            116_0  COME_FROM           110  '110'

 L. 274       116  LOAD_FAST                'self'
              118  LOAD_ATTR                _owner
              120  LOAD_METHOD              get_sim_instance
              122  CALL_METHOD_0         0  '0 positional arguments'
              124  STORE_FAST               'sim'

 L. 275       126  LOAD_FAST                'sim'
              128  LOAD_CONST               None
              130  COMPARE_OP               is
              132  POP_JUMP_IF_FALSE   150  'to 150'

 L. 276       134  LOAD_GLOBAL              logger
              136  LOAD_METHOD              warn
              138  LOAD_STR                 'Failed to get sim {}. Unable to save stack favorites.'
              140  LOAD_FAST                'sim'
              142  CALL_METHOD_2         2  '2 positional arguments'
              144  POP_TOP          

 L. 277       146  LOAD_FAST                'data'
              148  RETURN_VALUE     
            150_0  COME_FROM           132  '132'

 L. 279       150  LOAD_FAST                'sim'
              152  LOAD_ATTR                inventory_component
              154  STORE_FAST               'inventory'

 L. 280       156  LOAD_GLOBAL              services
              158  LOAD_METHOD              inventory_manager
              160  CALL_METHOD_0         0  '0 positional arguments'
              162  STORE_FAST               'inventory_manager'

 L. 281       164  LOAD_GLOBAL              services
              166  LOAD_METHOD              current_zone
              168  CALL_METHOD_0         0  '0 positional arguments'
              170  STORE_FAST               'zone'

 L. 285       172  SETUP_LOOP          364  'to 364'
              174  LOAD_FAST                'self'
              176  LOAD_ATTR                _favorite_stacks
              178  GET_ITER         
            180_0  COME_FROM           360  '360'
            180_1  COME_FROM           326  '326'
            180_2  COME_FROM           292  '292'
            180_3  COME_FROM           264  '264'
            180_4  COME_FROM           230  '230'
              180  FOR_ITER            362  'to 362'
              182  STORE_FAST               'key_data'

 L. 286       184  LOAD_FAST                'key_data'
              186  LOAD_GLOBAL              KEY_ID
              188  BINARY_SUBSCR    
              190  STORE_FAST               'key'

 L. 287       192  LOAD_FAST                'key_data'
              194  LOAD_GLOBAL              STACK_TYPE_ID
              196  BINARY_SUBSCR    
              198  STORE_FAST               'stack_type'

 L. 288       200  LOAD_FAST                'stack_type'
              202  LOAD_GLOBAL              StackScheme
              204  LOAD_ATTR                NONE
              206  COMPARE_OP               ==
          208_210  POP_JUMP_IF_FALSE   268  'to 268'

 L. 290       212  LOAD_FAST                'zone'
              214  LOAD_METHOD              find_object
              216  LOAD_FAST                'key'
              218  CALL_METHOD_1         1  '1 positional argument'
              220  STORE_FAST               'obj'

 L. 292       222  LOAD_FAST                'obj'
              224  LOAD_CONST               None
              226  COMPARE_OP               is
              228  POP_JUMP_IF_FALSE   232  'to 232'

 L. 293       230  CONTINUE            180  'to 180'
            232_0  COME_FROM           228  '228'

 L. 294       232  LOAD_FAST                'obj'
              234  LOAD_METHOD              get_sim_owner_id
              236  CALL_METHOD_0         0  '0 positional arguments'
              238  LOAD_FAST                'sim'
              240  LOAD_ATTR                id
              242  COMPARE_OP               !=
          244_246  POP_JUMP_IF_FALSE   328  'to 328'
              248  LOAD_FAST                'obj'
              250  LOAD_METHOD              get_household_owner_id
              252  CALL_METHOD_0         0  '0 positional arguments'
              254  LOAD_FAST                'sim'
              256  LOAD_ATTR                household_id
              258  COMPARE_OP               !=
          260_262  POP_JUMP_IF_FALSE   328  'to 328'

 L. 295       264  CONTINUE            180  'to 180'
              266  JUMP_FORWARD        328  'to 328'
            268_0  COME_FROM           208  '208'

 L. 297       268  LOAD_FAST                'inventory'
              270  LOAD_CONST               None
              272  COMPARE_OP               is
          274_276  POP_JUMP_IF_FALSE   294  'to 294'

 L. 298       278  LOAD_GLOBAL              logger
              280  LOAD_METHOD              warn
              282  LOAD_STR                 'Sim {} has no inventory component. Unable to save stack data: {}.'
              284  LOAD_FAST                'sim'
              286  LOAD_FAST                'key_data'
              288  CALL_METHOD_3         3  '3 positional arguments'
              290  POP_TOP          

 L. 299       292  CONTINUE            180  'to 180'
            294_0  COME_FROM           274  '274'

 L. 301       294  LOAD_FAST                'inventory_manager'
              296  LOAD_METHOD              get_stack_id_from_key
              298  LOAD_FAST                'key'
              300  LOAD_FAST                'stack_type'
              302  CALL_METHOD_2         2  '2 positional arguments'
              304  STORE_FAST               'stack_id'

 L. 302       306  LOAD_GLOBAL              len
              308  LOAD_FAST                'inventory'
              310  LOAD_METHOD              get_stack_items
              312  LOAD_FAST                'stack_id'
              314  CALL_METHOD_1         1  '1 positional argument'
              316  CALL_FUNCTION_1       1  '1 positional argument'
              318  LOAD_CONST               0
              320  COMPARE_OP               ==
          322_324  POP_JUMP_IF_FALSE   328  'to 328'

 L. 303       326  CONTINUE            180  'to 180'
            328_0  COME_FROM           322  '322'
            328_1  COME_FROM           266  '266'
            328_2  COME_FROM           260  '260'
            328_3  COME_FROM           244  '244'

 L. 304       328  LOAD_FAST                'data'
              330  LOAD_ATTR                stack_favorites
              332  LOAD_METHOD              add
              334  CALL_METHOD_0         0  '0 positional arguments'
              336  STORE_FAST               'stack_msg'

 L. 305       338  LOAD_FAST                'key'
              340  LOAD_CONST               None
              342  COMPARE_OP               is-not
          344_346  POP_JUMP_IF_FALSE   354  'to 354'

 L. 306       348  LOAD_FAST                'key'
              350  LOAD_FAST                'stack_msg'
              352  STORE_ATTR               key
            354_0  COME_FROM           344  '344'

 L. 307       354  LOAD_FAST                'stack_type'
              356  LOAD_FAST                'stack_msg'
              358  STORE_ATTR               stack_scheme
              360  JUMP_LOOP           180  'to 180'
              362  POP_BLOCK        
            364_0  COME_FROM_LOOP      172  '172'

 L. 309       364  LOAD_FAST                'data'
              366  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `JUMP_LOOP' instruction at offset 360

    def load(self, data):
        self.clean_up()
        for favorite in data.favorites:
            favorite_id = favorite.favorite_id
            if favorite_id is 0:
                favorite_id = None
            else:
                favorite_def_id = favorite.favorite_def_id
                if favorite_def_id is 0:
                    favorite_def_id = None
                self.set_favorite(favorite.favorite_type, favorite_id, favorite_def_id)

        for stack_favorite in data.stack_favorites:
            key = stack_favorite.key
            if key is 0:
                key = None
            else:
                stack_scheme = stack_favorite.stack_scheme
                self._favorite_stacks.append([key, stack_scheme])