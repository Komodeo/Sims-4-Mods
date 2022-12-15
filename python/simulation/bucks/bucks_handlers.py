# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\bucks_handlers.py
# Compiled at: 2020-06-04 18:30:23
# Size of source mod 2**32: 6660 bytes
from bucks.bucks_enums import BucksType, BucksTrackerType
from bucks.bucks_utils import BucksUtils
from gsi_handlers.gameplay_archiver import GameplayArchiver
from gsi_handlers.gsi_utils import parse_filter_to_list
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import services, sims4.log
logger = sims4.log.Logger('GSI/Bucks')
bucks_perks = GsiGridSchema(label='Bucks Perks', sim_specific=True)
bucks_perks.add_field('sim_id', label='simID', hidden=True)
bucks_perks.add_field('name', label='Name', type=(GsiFieldVisualizers.STRING))
bucks_perks.add_field('bucks_type', label='bucksType', type=(GsiFieldVisualizers.STRING))
bucks_perks.add_field('bucks_type_value', label='bucksTypeValue', type=(GsiFieldVisualizers.STRING), hidden=True)
bucks_perks.add_field('bucks_tracker_name', label='Bucks Tracker Name', type=(GsiFieldVisualizers.STRING))
bucks_perks.add_field('is_unlocked', label='isUnlocked', type=(GsiFieldVisualizers.STRING))
for bucks_type in BucksType:
    bucks_perks.add_filter(str(bucks_type))

bucks_perks.add_filter('Unlocked Only')
with bucks_perks.add_view_cheat('bucks.unlock_perk', label='Unlock Perk', dbl_click=True, refresh_view=False) as cheat:
    cheat.add_token_param('name')
    cheat.add_static_param(True)
    cheat.add_token_param('bucks_type_value')
    cheat.add_token_param('sim_id')
bucks = GsiGridSchema(label='Bucks', sim_specific=True)
bucks.add_field('bucks_type', label='bucksType', type=(GsiFieldVisualizers.STRING))
bucks.add_field('bucks_tracker_type', label='Bucks Tracker Type', type=(GsiFieldVisualizers.STRING))
bucks.add_field('bucks_amount', label='bucksAmount', type=(GsiFieldVisualizers.INT))
bucksLog = GsiGridSchema(label='Bucks Log', sim_specific=True)
bucksLog.add_field('sim_id', label='simID', type=(GsiFieldVisualizers.INT), hidden=True)
bucksLog.add_field('bucks_type', label='bucksType', type=(GsiFieldVisualizers.STRING))
bucksLog.add_field('bucks_tracker_type', label='bucksTrackerType', type=(GsiFieldVisualizers.STRING))
bucksLog.add_field('bucks_start_amount', label='bucksStartAmount', type=(GsiFieldVisualizers.INT))
bucksLog.add_field('bucks_change_amount', label='bucksChange', type=(GsiFieldVisualizers.INT))
bucksLog.add_field('bucks_final_amount', label='bucksFinalAmount', type=(GsiFieldVisualizers.INT))

@GsiHandler('bucks_perks', bucks_perks)
def generate_bucks_perks_view--- This code section failed: ---

 L.  50         0  LOAD_GLOBAL              parse_filter_to_list
                2  LOAD_FAST                'filter'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  STORE_FAST               'filter_list'

 L.  51         8  BUILD_LIST_0          0 
               10  STORE_FAST               'bucks_perks_data'

 L.  52        12  LOAD_GLOBAL              services
               14  LOAD_METHOD              get_instance_manager
               16  LOAD_GLOBAL              sims4
               18  LOAD_ATTR                resources
               20  LOAD_ATTR                Types
               22  LOAD_ATTR                BUCKS_PERK
               24  CALL_METHOD_1         1  '1 positional argument'
               26  STORE_FAST               'perks_instance_manager'

 L.  53        28  LOAD_CONST               None
               30  STORE_FAST               'previous_bucks_type'

 L.  54        32  SETUP_LOOP          228  'to 228'
               34  LOAD_FAST                'perks_instance_manager'
               36  LOAD_ATTR                types
               38  LOAD_METHOD              values
               40  CALL_METHOD_0         0  '0 positional arguments'
               42  GET_ITER         
             44_0  COME_FROM           224  '224'
             44_1  COME_FROM           158  '158'
             44_2  COME_FROM           140  '140'
             44_3  COME_FROM           112  '112'
             44_4  COME_FROM           100  '100'
               44  FOR_ITER            226  'to 226'
               46  STORE_FAST               'perk'

 L.  55        48  LOAD_FAST                'perk'
               50  LOAD_ATTR                associated_bucks_type
               52  LOAD_FAST                'previous_bucks_type'
               54  COMPARE_OP               !=
               56  POP_JUMP_IF_FALSE    78  'to 78'

 L.  56        58  LOAD_GLOBAL              BucksUtils
               60  LOAD_METHOD              get_tracker_for_bucks_type
               62  LOAD_FAST                'perk'
               64  LOAD_ATTR                associated_bucks_type
               66  LOAD_FAST                'sim_id'
               68  CALL_METHOD_2         2  '2 positional arguments'
               70  STORE_FAST               'perk_specific_bucks_tracker'

 L.  57        72  LOAD_FAST                'perk'
               74  LOAD_ATTR                associated_bucks_type
               76  STORE_FAST               'previous_bucks_type'
             78_0  COME_FROM            56  '56'

 L.  59        78  LOAD_FAST                'filter_list'
               80  LOAD_CONST               None
               82  COMPARE_OP               is-not
               84  POP_JUMP_IF_FALSE   160  'to 160'

 L.  60        86  LOAD_STR                 'Unlocked Only'
               88  LOAD_FAST                'filter_list'
               90  COMPARE_OP               in
               92  POP_JUMP_IF_FALSE   144  'to 144'

 L.  61        94  LOAD_FAST                'perk_specific_bucks_tracker'
               96  LOAD_CONST               None
               98  COMPARE_OP               is
              100  POP_JUMP_IF_TRUE_LOOP    44  'to 44'

 L.  62       102  LOAD_FAST                'perk_specific_bucks_tracker'
              104  LOAD_METHOD              is_perk_unlocked
              106  LOAD_FAST                'perk'
              108  CALL_METHOD_1         1  '1 positional argument'
              110  POP_JUMP_IF_TRUE    114  'to 114'

 L.  63       112  CONTINUE             44  'to 44'
            114_0  COME_FROM           110  '110'

 L.  65       114  LOAD_GLOBAL              len
              116  LOAD_FAST                'filter_list'
              118  CALL_FUNCTION_1       1  '1 positional argument'
              120  LOAD_CONST               1
              122  COMPARE_OP               >
              124  POP_JUMP_IF_FALSE   160  'to 160'

 L.  66       126  LOAD_GLOBAL              str
              128  LOAD_FAST                'perk'
              130  LOAD_ATTR                associated_bucks_type
              132  CALL_FUNCTION_1       1  '1 positional argument'
              134  LOAD_FAST                'filter_list'
              136  COMPARE_OP               not-in
              138  POP_JUMP_IF_FALSE   160  'to 160'

 L.  67       140  CONTINUE             44  'to 44'
              142  JUMP_FORWARD        160  'to 160'
            144_0  COME_FROM            92  '92'

 L.  68       144  LOAD_GLOBAL              str
              146  LOAD_FAST                'perk'
              148  LOAD_ATTR                associated_bucks_type
              150  CALL_FUNCTION_1       1  '1 positional argument'
              152  LOAD_FAST                'filter_list'
              154  COMPARE_OP               not-in
              156  POP_JUMP_IF_FALSE   160  'to 160'

 L.  69       158  CONTINUE             44  'to 44'
            160_0  COME_FROM           156  '156'
            160_1  COME_FROM           142  '142'
            160_2  COME_FROM           138  '138'
            160_3  COME_FROM           124  '124'
            160_4  COME_FROM            84  '84'

 L.  71       160  LOAD_FAST                'bucks_perks_data'
              162  LOAD_METHOD              append

 L.  72       164  LOAD_GLOBAL              str
              166  LOAD_FAST                'sim_id'
              168  CALL_FUNCTION_1       1  '1 positional argument'

 L.  73       170  LOAD_FAST                'perk'
              172  LOAD_ATTR                __name__

 L.  74       174  LOAD_GLOBAL              str
              176  LOAD_FAST                'perk'
              178  LOAD_ATTR                associated_bucks_type
              180  CALL_FUNCTION_1       1  '1 positional argument'

 L.  75       182  LOAD_GLOBAL              int
              184  LOAD_FAST                'perk'
              186  LOAD_ATTR                associated_bucks_type
              188  CALL_FUNCTION_1       1  '1 positional argument'

 L.  76       190  LOAD_GLOBAL              str
              192  LOAD_FAST                'perk_specific_bucks_tracker'
              194  CALL_FUNCTION_1       1  '1 positional argument'

 L.  77       196  LOAD_FAST                'perk_specific_bucks_tracker'
              198  LOAD_CONST               None
              200  COMPARE_OP               is-not
              202  POP_JUMP_IF_FALSE   214  'to 214'
              204  LOAD_FAST                'perk_specific_bucks_tracker'
              206  LOAD_METHOD              is_perk_unlocked
              208  LOAD_FAST                'perk'
              210  CALL_METHOD_1         1  '1 positional argument'
              212  JUMP_FORWARD        216  'to 216'
            214_0  COME_FROM           202  '202'
              214  LOAD_CONST               False
            216_0  COME_FROM           212  '212'
              216  LOAD_CONST               ('sim_id', 'name', 'bucks_type', 'bucks_type_value', 'bucks_tracker_name', 'is_unlocked')
              218  BUILD_CONST_KEY_MAP_6     6 
              220  CALL_METHOD_1         1  '1 positional argument'
              222  POP_TOP          
              224  JUMP_LOOP            44  'to 44'
              226  POP_BLOCK        
            228_0  COME_FROM_LOOP       32  '32'

 L.  80       228  LOAD_FAST                'bucks_perks_data'
              230  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `JUMP_LOOP' instruction at offset 224


@GsiHandler('bucks', bucks)
def generate_bucks_view(sim_id: int=None):
    bucks_data = []
    for bucks in BucksType:
        specific_bucks_tracker = BucksUtils.get_tracker_for_bucks_typebuckssim_id
        bucks_amount = None
        if specific_bucks_tracker is not None:
            bucks_amount = specific_bucks_tracker.get_bucks_amount_for_type(bucks)
        bucks_tracker_type = BucksUtils.BUCK_TYPE_TO_TRACKER_MAP.get(bucks)
        if not bucks_tracker_type == BucksTrackerType.HOUSEHOLD:
            if bucks_tracker_type == BucksTrackerType.SIM:
                pass
        bucks_data.append({'bucks_type':str(bucks), 
         'bucks_tracker_type':str(bucks_tracker_type), 
         'bucks_amount':bucks_amount})

    return bucks_data


archiver = GameplayArchiver('bucks_log', bucksLog)

def add_bucks_data(bucks_tracker_owner, bucks_type, bucks_change_amount, bucks_final_amount):
    bucks_start_amount = bucks_final_amount - bucks_change_amount
    bucks_tracker_type = BucksUtils.BUCK_TYPE_TO_TRACKER_MAP.get(bucks_type)
    if bucks_tracker_type == BucksTrackerType.HOUSEHOLD:
        for sim in bucks_tracker_owner:
            _assign_bucks_data(sim, bucks_type, bucks_tracker_type, bucks_start_amount, bucks_change_amount, bucks_final_amount)

    else:
        if bucks_tracker_type == BucksTrackerType.SIM:
            _assign_bucks_data(bucks_tracker_owner, bucks_type, bucks_tracker_type, bucks_start_amount, bucks_change_amount, bucks_final_amount)


def _assign_bucks_data(sim, bucks_type, bucks_tracker_type, bucks_start_amount, bucks_change_amount, bucks_final_amount):
    entry = {}
    entry['sim_id'] = sim.id
    entry['bucks_type'] = str(bucks_type)
    entry['bucks_tracker_type'] = str(bucks_tracker_type)
    entry['bucks_start_amount'] = bucks_start_amount
    entry['bucks_change_amount'] = bucks_change_amount
    entry['bucks_final_amount'] = bucks_final_amount
    archiver.archive(data=entry, object_id=(sim.id))