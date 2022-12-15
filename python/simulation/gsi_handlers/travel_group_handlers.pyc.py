# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\travel_group_handlers.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 4761 bytes
import services, sims4.hash_util
from gsi_handlers.gsi_utils import parse_filter_to_list
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from sims4.resources import get_resource_key, Types, get_debug_name
from world.region import get_region_description_id_from_zone_id
travel_groups_schema = GsiGridSchema(label='Travel Groups')
travel_groups_schema.add_field('groupId', label='Group Id', width=1, unique_field=True)
travel_groups_schema.add_field('numSims', label='# Sims', width=1)
travel_groups_schema.add_field('zoneId', label='Zone Id', width=1)
travel_groups_schema.add_field('lot', label='Lot', width=3)
travel_groups_schema.add_field('world', label='World', width=3)
travel_groups_schema.add_field('region', label='Region', width=3)
travel_groups_schema.add_field('startTime', label='Start Time', width=2, type=(GsiFieldVisualizers.TIME))
travel_groups_schema.add_field('duration', label='Vacation Duration', width=2)
travel_groups_schema.add_field('playerGroup', label='Is Player Group', width=1)
travel_groups_schema.add_filter('played')
travel_groups_schema.add_filter('npc')
with travel_groups_schema.add_has_many('members', GsiGridSchema) as sub_schema:
    sub_schema.add_field('zoneId', label='Zone Id', width=1)
    sub_schema.add_field('sim', label='Sim', width=2)
    sub_schema.add_field('lot', label='Lot', width=2)
    sub_schema.add_field('world', label='World', width=2)
    sub_schema.add_field('region', label='Region', width=2)
    sub_schema.add_field('household', label='Household', width=4)

@GsiHandler('travel_groups', travel_groups_schema)
def generate_travel_groups_data--- This code section failed: ---

 L.  39         0  LOAD_GLOBAL              parse_filter_to_list
                2  LOAD_FAST                'filter'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  STORE_FAST               'filter_list'

 L.  40         8  BUILD_LIST_0          0 
               10  STORE_FAST               'all_group_data'

 L.  41        12  LOAD_GLOBAL              services
               14  LOAD_METHOD              get_persistence_service
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  STORE_DEREF              'persistance_service'

 L.  42        20  LOAD_CLOSURE             'persistance_service'
               22  BUILD_TUPLE_1         1 
               24  LOAD_CODE                <code_object get_region_world_and_lot_info>
               26  LOAD_STR                 'generate_travel_groups_data.<locals>.get_region_world_and_lot_info'
               28  MAKE_FUNCTION_CLOSURE        'closure'
               30  STORE_FAST               'get_region_world_and_lot_info'

 L.  51        32  LOAD_GLOBAL              services
               34  LOAD_METHOD              travel_group_manager
               36  CALL_METHOD_0         0  '0 positional arguments'
               38  STORE_FAST               'travel_group_manager'

 L.  52        40  LOAD_FAST                'travel_group_manager'
               42  LOAD_CONST               None
               44  COMPARE_OP               is
               46  POP_JUMP_IF_FALSE    52  'to 52'

 L.  53        48  LOAD_FAST                'all_group_data'
               50  RETURN_VALUE     
             52_0  COME_FROM            46  '46'

 L.  54     52_54  SETUP_LOOP          398  'to 398'
               56  LOAD_GLOBAL              tuple
               58  LOAD_FAST                'travel_group_manager'
               60  LOAD_METHOD              values
               62  CALL_METHOD_0         0  '0 positional arguments'
               64  CALL_FUNCTION_1       1  '1 positional argument'
               66  GET_ITER         
             68_0  COME_FROM           394  '394'
             68_1  COME_FROM           108  '108'
             68_2  COME_FROM           102  '102'
            68_70  FOR_ITER            396  'to 396'
               72  STORE_FAST               'travel_group'

 L.  55        74  LOAD_FAST                'filter_list'
               76  LOAD_CONST               None
               78  COMPARE_OP               is
               80  POP_JUMP_IF_TRUE    110  'to 110'

 L.  56        82  LOAD_STR                 'played'
               84  LOAD_FAST                'filter_list'
               86  COMPARE_OP               in
               88  POP_JUMP_IF_FALSE    96  'to 96'
               90  LOAD_FAST                'travel_group'
               92  LOAD_ATTR                played
               94  POP_JUMP_IF_TRUE    110  'to 110'
             96_0  COME_FROM            88  '88'

 L.  57        96  LOAD_STR                 'npc'
               98  LOAD_FAST                'filter_list'
              100  COMPARE_OP               in
              102  POP_JUMP_IF_FALSE_LOOP    68  'to 68'
              104  LOAD_FAST                'travel_group'
              106  LOAD_ATTR                played
              108  POP_JUMP_IF_TRUE_LOOP    68  'to 68'
            110_0  COME_FROM            94  '94'
            110_1  COME_FROM            80  '80'

 L.  59       110  LOAD_FAST                'travel_group'
              112  LOAD_ATTR                zone_id
              114  STORE_FAST               'zone_id'

 L.  60       116  LOAD_FAST                'get_region_world_and_lot_info'
              118  LOAD_FAST                'zone_id'
              120  CALL_FUNCTION_1       1  '1 positional argument'
              122  UNPACK_SEQUENCE_3     3 
              124  STORE_FAST               'region'
              126  STORE_FAST               'world'
              128  STORE_FAST               'lot'

 L.  62       130  LOAD_GLOBAL              str
              132  LOAD_FAST                'travel_group'
              134  LOAD_ATTR                id
              136  CALL_FUNCTION_1       1  '1 positional argument'

 L.  63       138  LOAD_GLOBAL              str
              140  LOAD_GLOBAL              len
              142  LOAD_FAST                'travel_group'
              144  CALL_FUNCTION_1       1  '1 positional argument'
              146  CALL_FUNCTION_1       1  '1 positional argument'

 L.  64       148  LOAD_GLOBAL              hex
              150  LOAD_FAST                'zone_id'
              152  CALL_FUNCTION_1       1  '1 positional argument'

 L.  65       154  LOAD_GLOBAL              get_debug_name
              156  LOAD_FAST                'lot'
              158  LOAD_GLOBAL              sims4
              160  LOAD_ATTR                hash_util
              162  LOAD_ATTR                KEYNAMEMAPTYPE_OBJECTINSTANCES
              164  LOAD_CONST               ('table_type',)
              166  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'

 L.  66       168  LOAD_GLOBAL              get_debug_name
              170  LOAD_FAST                'world'
              172  LOAD_GLOBAL              sims4
              174  LOAD_ATTR                hash_util
              176  LOAD_ATTR                KEYNAMEMAPTYPE_OBJECTINSTANCES
              178  LOAD_CONST               ('table_type',)
              180  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'

 L.  67       182  LOAD_GLOBAL              get_debug_name
              184  LOAD_FAST                'region'
              186  LOAD_GLOBAL              sims4
              188  LOAD_ATTR                hash_util
              190  LOAD_ATTR                KEYNAMEMAPTYPE_OBJECTINSTANCES
              192  LOAD_CONST               ('table_type',)
              194  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'

 L.  68       196  LOAD_GLOBAL              str
              198  LOAD_FAST                'travel_group'
              200  LOAD_ATTR                create_timestamp
              202  CALL_FUNCTION_1       1  '1 positional argument'

 L.  69       204  LOAD_FAST                'travel_group'
              206  LOAD_ATTR                end_timestamp
              208  POP_JUMP_IF_FALSE   220  'to 220'
              210  LOAD_GLOBAL              str
              212  LOAD_FAST                'travel_group'
              214  LOAD_ATTR                duration_time_span
              216  CALL_FUNCTION_1       1  '1 positional argument'
              218  JUMP_FORWARD        222  'to 222'
            220_0  COME_FROM           208  '208'
              220  LOAD_STR                 'Infinite'
            222_0  COME_FROM           218  '218'

 L.  70       222  LOAD_GLOBAL              str
              224  LOAD_FAST                'travel_group'
              226  LOAD_ATTR                played
              228  CALL_FUNCTION_1       1  '1 positional argument'
              230  LOAD_CONST               ('groupId', 'numSims', 'zoneId', 'lot', 'world', 'region', 'startTime', 'duration', 'playerGroup')
              232  BUILD_CONST_KEY_MAP_9     9 
              234  STORE_FAST               'group_entry'

 L.  72       236  BUILD_LIST_0          0 
              238  STORE_FAST               'group_members_data'

 L.  73       240  SETUP_LOOP          376  'to 376'
              242  LOAD_FAST                'travel_group'
              244  GET_ITER         
            246_0  COME_FROM           372  '372'
              246  FOR_ITER            374  'to 374'
              248  STORE_FAST               'member'

 L.  74       250  LOAD_FAST                'member'
              252  LOAD_ATTR                zone_id
              254  STORE_FAST               'sim_zone_id'

 L.  76       256  LOAD_GLOBAL              str
              258  LOAD_FAST                'member'
              260  CALL_FUNCTION_1       1  '1 positional argument'

 L.  77       262  LOAD_GLOBAL              hex
              264  LOAD_FAST                'sim_zone_id'
              266  CALL_FUNCTION_1       1  '1 positional argument'

 L.  78       268  LOAD_GLOBAL              str
              270  LOAD_FAST                'member'
              272  LOAD_ATTR                household
              274  CALL_FUNCTION_1       1  '1 positional argument'
              276  LOAD_CONST               ('sim', 'zoneId', 'household')
              278  BUILD_CONST_KEY_MAP_3     3 
              280  STORE_FAST               'member_data'

 L.  80       282  LOAD_FAST                'sim_zone_id'
          284_286  POP_JUMP_IF_FALSE   362  'to 362'

 L.  81       288  LOAD_FAST                'get_region_world_and_lot_info'
              290  LOAD_FAST                'sim_zone_id'
              292  CALL_FUNCTION_1       1  '1 positional argument'
              294  UNPACK_SEQUENCE_3     3 
              296  STORE_FAST               'sim_region'
              298  STORE_FAST               'sim_world'
              300  STORE_FAST               'sim_lot'

 L.  83       302  LOAD_GLOBAL              get_debug_name
              304  LOAD_FAST                'sim_lot'
              306  LOAD_GLOBAL              sims4
              308  LOAD_ATTR                hash_util
              310  LOAD_ATTR                KEYNAMEMAPTYPE_OBJECTINSTANCES
              312  LOAD_CONST               ('table_type',)
              314  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              316  LOAD_FAST                'member_data'
              318  LOAD_STR                 'lot'
              320  STORE_SUBSCR     

 L.  84       322  LOAD_GLOBAL              get_debug_name
              324  LOAD_FAST                'sim_world'
              326  LOAD_GLOBAL              sims4
              328  LOAD_ATTR                hash_util
              330  LOAD_ATTR                KEYNAMEMAPTYPE_OBJECTINSTANCES
              332  LOAD_CONST               ('table_type',)
              334  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              336  LOAD_FAST                'member_data'
              338  LOAD_STR                 'world'
              340  STORE_SUBSCR     

 L.  85       342  LOAD_GLOBAL              get_debug_name
              344  LOAD_FAST                'sim_region'
              346  LOAD_GLOBAL              sims4
              348  LOAD_ATTR                hash_util
              350  LOAD_ATTR                KEYNAMEMAPTYPE_OBJECTINSTANCES
              352  LOAD_CONST               ('table_type',)
              354  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              356  LOAD_FAST                'member_data'
              358  LOAD_STR                 'region'
              360  STORE_SUBSCR     
            362_0  COME_FROM           284  '284'

 L.  87       362  LOAD_FAST                'group_members_data'
              364  LOAD_METHOD              append
              366  LOAD_FAST                'member_data'
              368  CALL_METHOD_1         1  '1 positional argument'
              370  POP_TOP          
              372  JUMP_LOOP           246  'to 246'
              374  POP_BLOCK        
            376_0  COME_FROM_LOOP      240  '240'

 L.  88       376  LOAD_FAST                'group_members_data'
              378  LOAD_FAST                'group_entry'
              380  LOAD_STR                 'members'
              382  STORE_SUBSCR     

 L.  90       384  LOAD_FAST                'all_group_data'
              386  LOAD_METHOD              append
              388  LOAD_FAST                'group_entry'
              390  CALL_METHOD_1         1  '1 positional argument'
              392  POP_TOP          
              394  JUMP_LOOP            68  'to 68'
              396  POP_BLOCK        
            398_0  COME_FROM_LOOP       52  '52'

 L.  91       398  LOAD_FAST                'all_group_data'
              400  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_FAST' instruction at offset 110