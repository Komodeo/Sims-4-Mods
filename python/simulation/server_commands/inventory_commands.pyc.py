# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\inventory_commands.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 38406 bytes
from bucks.bucks_utils import BucksUtils
from cas.cas import get_tags_from_outfit
from collections import Counter
from distributor.ops import SendUIMessage
from distributor.system import Distributor
from fashion_trends.fashion_trend_tuning import FashionThriftStoreTuning, FashionTrendTuning
from google.protobuf import text_format
from interactions.base.picker_interaction import PickerInteractionDeliveryMethod
from objects.components.inventory_storage import InventoryStorage
from protocolbuffers import Consts_pb2
from protocolbuffers import SimObjectAttributes_pb2
from protocolbuffers import UI_pb2
from objects.components.inventory_enums import StackScheme
from objects.system import create_object
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, RequiredTargetParam, TunableInstanceParam, OptionalSimInfoParam
from server_commands.ui_commands import ui_dialog_respond
from sims.outfits.outfit_enums import OutfitCategory
from sims4.commands import CommandType
import services, sims4.commands
from sims4.localization import LocalizationHelperTuning

@sims4.commands.Command('inventory.create_in_hidden')
def create_object_in_hidden_inventory(definition_id: int, _connection=None):
    lot = services.active_lot()
    if lot is not None:
        return lot.create_object_in_hidden_inventory(definition_id) is not None
    return False


@sims4.commands.Command('inventory.list_hidden')
def list_objects_in_hidden_inventory(_connection=None):
    lot = services.active_lot()
    if lot is not None:
        hidden_inventory = lot.get_hidden_inventory()
        if hidden_inventory is not None:
            for obj in hidden_inventory:
                sims4.commands.output(str(obj), _connection)

            return True
    return False


@sims4.commands.Command('qa.objects.inventory.list', command_type=(sims4.commands.CommandType.Automation))
def automation_list_active_situations(inventory_obj_id: int=None, _connection=None):
    manager = services.object_manager()
    if inventory_obj_id not in manager:
        sims4.commands.automation_output('ObjectInventory; Status:NoObject, ObjectId:{}'.format(inventory_obj_id), _connection)
        return
    inventory_obj = manager.get(inventory_obj_id)
    if inventory_obj.inventory_component != None:
        sims4.commands.automation_output('ObjectInventory; Status:Begin, ObjectId:{}'.format(inventory_obj_id), _connection)
        for obj in inventory_obj.inventory_component:
            sims4.commands.automation_output('ObjectInventory; Status:Data, Id:{}, DefId:{}'.format(obj.id, obj.definition.id), _connection)

        sims4.commands.automation_output('ObjectInventory; Status:End', _connection)
    else:
        sims4.commands.automation_output('ObjectInventory; Status:NoInventory, ObjectId:{}'.format(inventory_obj_id), _connection)


@sims4.commands.Command('inventory.purge', command_type=(sims4.commands.CommandType.Cheat))
def purge_sim_inventory(opt_target: OptionalTargetParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection)
    if target is not None:
        target.inventory_component.purge_inventory()
    return False


@sims4.commands.Command('inventory.purchase_picker_response', command_type=(sims4.commands.CommandType.Live))
def purchase_picker_response(inventory_target: RequiredTargetParam, mailman_purchase: bool=False, *def_ids_and_amounts: int, _connection=None):
    total_price = 0
    current_purchased = 0
    objects_to_buy = []
    definition_manager = services.definition_manager()
    for def_id, amount in zip(def_ids_and_amounts[::2], def_ids_and_amounts[1::2]):
        definition = definition_manager.get(def_id)
        if definition is None:
            sims4.commands.output('inventory.purchase_picker_response: Definition not found with id {}'.format(def_id), _connection)
            return False
        else:
            purchase_price = definition.price * amount
            total_price += purchase_price
            objects_to_buy.append((definition, amount))

    client = services.client_manager().get(_connection)
    if client is None:
        sims4.commands.output('inventory.purchase_picker_response: No client found to make purchase.', _connection)
        return False
    household = client.household
    if household.funds.money < total_price:
        sims4.commands.output('inventory.purchase_picker_response: Insufficient funds for household to purchase items.', _connection)
        return False
    if mailman_purchase:
        inventory = services.active_lot().get_hidden_inventory()
    else:
        inventory_owner = inventory_target.get_target()
        inventory = inventory_owner.inventory_component
    if inventory is None:
        sims4.commands.output('inventory.purchase_picker_response: Inventory not found for items to be purchased into.', _connection)
        return False
    for definition, amount in objects_to_buy:
        obj = create_object(definition)
        if obj is None:
            sims4.commands.output('inventory.purchase_picker_response: Failed to create object with definition {}.'.format(definition), _connection)
            continue
        else:
            obj.set_stack_count(amount)
        if not inventory.player_try_add_object(obj):
            sims4.commands.output('inventory.purchase_picker_response: Failed to add object into inventory: {}'.format(obj), _connection)
            obj.destroy(source=inventory, cause='inventory.purchase_picker_response: Failed to add object into inventory.')
            continue
        else:
            obj.set_household_owner_id(household.id)
            obj.try_post_bb_fixup(force_fixup=True, active_household_id=(services.active_household_id()))
            purchase_price = definition.price * amount
            current_purchased += purchase_price

    return household.funds.try_remove(current_purchased, Consts_pb2.TELEMETRY_OBJECT_BUY)


USE_DEFINITION_PRICE = -1

@sims4.commands.Command('inventory.purchase_picker_response_by_ids', command_type=(sims4.commands.CommandType.Live))
def purchase_picker_response_by_ids--- This code section failed: ---

 L. 189         0  LOAD_CONST               0
                2  STORE_FAST               'total_price'

 L. 190         4  LOAD_CONST               0
                6  STORE_FAST               'current_purchased'

 L. 191         8  BUILD_LIST_0          0 
               10  STORE_FAST               'objects_to_buy'

 L. 192        12  LOAD_GLOBAL              services
               14  LOAD_METHOD              definition_manager
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  STORE_FAST               'definition_manager'

 L. 193        20  LOAD_GLOBAL              services
               22  LOAD_METHOD              inventory_manager
               24  CALL_METHOD_0         0  '0 positional arguments'
               26  STORE_FAST               'inventory_manager'

 L. 198        28  SETUP_LOOP          212  'to 212'
               30  LOAD_GLOBAL              zip
               32  LOAD_FAST                'ids_and_amounts_and_price'
               34  LOAD_CONST               None
               36  LOAD_CONST               None
               38  LOAD_CONST               3
               40  BUILD_SLICE_3         3 
               42  BINARY_SUBSCR    

 L. 199        44  LOAD_FAST                'ids_and_amounts_and_price'
               46  LOAD_CONST               1
               48  LOAD_CONST               None
               50  LOAD_CONST               3
               52  BUILD_SLICE_3         3 
               54  BINARY_SUBSCR    

 L. 200        56  LOAD_FAST                'ids_and_amounts_and_price'
               58  LOAD_CONST               2
               60  LOAD_CONST               None
               62  LOAD_CONST               3
               64  BUILD_SLICE_3         3 
               66  BINARY_SUBSCR    
               68  CALL_FUNCTION_3       3  '3 positional arguments'
               70  GET_ITER         
             72_0  COME_FROM           208  '208'
               72  FOR_ITER            210  'to 210'
               74  UNPACK_SEQUENCE_3     3 
               76  STORE_FAST               'def_or_obj_id'
               78  STORE_FAST               'amount'
               80  STORE_FAST               'price'

 L. 201        82  LOAD_FAST                'object_ids_or_definition_ids'
               84  POP_JUMP_IF_FALSE    98  'to 98'

 L. 202        86  LOAD_FAST                'inventory_manager'
               88  LOAD_METHOD              get
               90  LOAD_FAST                'def_or_obj_id'
               92  CALL_METHOD_1         1  '1 positional argument'
               94  STORE_FAST               'obj_or_definition'
               96  JUMP_FORWARD        108  'to 108'
             98_0  COME_FROM            84  '84'

 L. 204        98  LOAD_FAST                'definition_manager'
              100  LOAD_METHOD              get
              102  LOAD_FAST                'def_or_obj_id'
              104  CALL_METHOD_1         1  '1 positional argument'
              106  STORE_FAST               'obj_or_definition'
            108_0  COME_FROM            96  '96'

 L. 208       108  LOAD_FAST                'obj_or_definition'
              110  LOAD_CONST               None
              112  COMPARE_OP               is
              114  POP_JUMP_IF_FALSE   160  'to 160'

 L. 209       116  LOAD_GLOBAL              sims4
              118  LOAD_ATTR                commands
              120  LOAD_METHOD              output
              122  LOAD_STR                 'inventory.purchase_picker_response: Object or Definition not found with id {}'
              124  LOAD_METHOD              format
              126  LOAD_FAST                'def_or_obj_id'
              128  CALL_METHOD_1         1  '1 positional argument'
              130  LOAD_FAST                '_connection'
              132  CALL_METHOD_2         2  '2 positional arguments'
              134  POP_TOP          

 L. 210       136  LOAD_GLOBAL              sims4
              138  LOAD_ATTR                commands
              140  LOAD_METHOD              automation_output
              142  LOAD_STR                 'PurchasePickerResponseInfo; Status:Failed, Message:Object or Definition not found with id {}'
              144  LOAD_METHOD              format
              146  LOAD_FAST                'def_or_obj_id'
              148  CALL_METHOD_1         1  '1 positional argument'
              150  LOAD_FAST                '_connection'
              152  CALL_METHOD_2         2  '2 positional arguments'
              154  POP_TOP          

 L. 211       156  LOAD_CONST               False
              158  RETURN_VALUE     
            160_0  COME_FROM           114  '114'

 L. 214       160  LOAD_FAST                'price'
              162  LOAD_GLOBAL              USE_DEFINITION_PRICE
              164  COMPARE_OP               ==
              166  POP_JUMP_IF_FALSE   176  'to 176'

 L. 215       168  LOAD_FAST                'obj_or_definition'
              170  LOAD_ATTR                definition
              172  LOAD_ATTR                price
              174  STORE_FAST               'price'
            176_0  COME_FROM           166  '166'

 L. 219       176  LOAD_FAST                'price'
              178  LOAD_FAST                'amount'
              180  BINARY_MULTIPLY  
              182  STORE_FAST               'purchase_price'

 L. 220       184  LOAD_FAST                'total_price'
              186  LOAD_FAST                'purchase_price'
              188  INPLACE_ADD      
              190  STORE_FAST               'total_price'

 L. 223       192  LOAD_FAST                'objects_to_buy'
              194  LOAD_METHOD              append
              196  LOAD_FAST                'obj_or_definition'
              198  LOAD_FAST                'price'
              200  LOAD_FAST                'amount'
              202  BUILD_TUPLE_3         3 
              204  CALL_METHOD_1         1  '1 positional argument'
              206  POP_TOP          
              208  JUMP_LOOP            72  'to 72'
              210  POP_BLOCK        
            212_0  COME_FROM_LOOP       28  '28'

 L. 225       212  LOAD_GLOBAL              services
              214  LOAD_METHOD              client_manager
              216  CALL_METHOD_0         0  '0 positional arguments'
              218  LOAD_METHOD              get
              220  LOAD_FAST                '_connection'
              222  CALL_METHOD_1         1  '1 positional argument'
              224  STORE_FAST               'client'

 L. 226       226  LOAD_FAST                'client'
              228  LOAD_CONST               None
              230  COMPARE_OP               is
          232_234  POP_JUMP_IF_FALSE   268  'to 268'

 L. 227       236  LOAD_GLOBAL              sims4
              238  LOAD_ATTR                commands
              240  LOAD_METHOD              output
              242  LOAD_STR                 'inventory.purchase_picker_response: No client found to make purchase.'
              244  LOAD_FAST                '_connection'
              246  CALL_METHOD_2         2  '2 positional arguments'
              248  POP_TOP          

 L. 228       250  LOAD_GLOBAL              sims4
              252  LOAD_ATTR                commands
              254  LOAD_METHOD              automation_output
              256  LOAD_STR                 'PurchasePickerResponseInfo; Status:Failed, Message:No client found to make purchase.'
              258  LOAD_FAST                '_connection'
              260  CALL_METHOD_2         2  '2 positional arguments'
              262  POP_TOP          

 L. 229       264  LOAD_CONST               False
              266  RETURN_VALUE     
            268_0  COME_FROM           232  '232'

 L. 231       268  LOAD_FAST                'client'
              270  LOAD_ATTR                household
              272  STORE_FAST               'household'

 L. 232       274  LOAD_FAST                'household'
              276  LOAD_METHOD              get_currency_amount
              278  LOAD_FAST                'currency_type'
              280  CALL_METHOD_1         1  '1 positional argument'
              282  LOAD_FAST                'total_price'
              284  COMPARE_OP               <
          286_288  POP_JUMP_IF_FALSE   322  'to 322'

 L. 233       290  LOAD_GLOBAL              sims4
              292  LOAD_ATTR                commands
              294  LOAD_METHOD              output
              296  LOAD_STR                 'inventory.purchase_picker_response: Insufficient funds for household to purchase items.'
              298  LOAD_FAST                '_connection'
              300  CALL_METHOD_2         2  '2 positional arguments'
              302  POP_TOP          

 L. 234       304  LOAD_GLOBAL              sims4
              306  LOAD_ATTR                commands
              308  LOAD_METHOD              automation_output
              310  LOAD_STR                 'PurchasePickerResponseInfo; Status:Failed, Message:Insufficient funds for household to purchase items.'
              312  LOAD_FAST                '_connection'
              314  CALL_METHOD_2         2  '2 positional arguments'
              316  POP_TOP          

 L. 235       318  LOAD_CONST               False
              320  RETURN_VALUE     
            322_0  COME_FROM           286  '286'

 L. 237       322  LOAD_FAST                'delivery_method'
              324  LOAD_GLOBAL              PickerInteractionDeliveryMethod
              326  LOAD_ATTR                MAILMAN
              328  COMPARE_OP               ==
          330_332  POP_JUMP_IF_FALSE   348  'to 348'

 L. 238       334  LOAD_GLOBAL              services
              336  LOAD_METHOD              active_lot
              338  CALL_METHOD_0         0  '0 positional arguments'
              340  LOAD_METHOD              get_hidden_inventory
              342  CALL_METHOD_0         0  '0 positional arguments'
              344  STORE_FAST               'to_inventory'
              346  JUMP_FORWARD        374  'to 374'
            348_0  COME_FROM           330  '330'

 L. 239       348  LOAD_FAST                'delivery_method'
              350  LOAD_GLOBAL              PickerInteractionDeliveryMethod
              352  LOAD_ATTR                INVENTORY
              354  COMPARE_OP               ==
          356_358  POP_JUMP_IF_FALSE   374  'to 374'

 L. 240       360  LOAD_FAST                'inventory_target'
              362  LOAD_METHOD              get_target
              364  CALL_METHOD_0         0  '0 positional arguments'
              366  STORE_FAST               'to_inventory_owner'

 L. 241       368  LOAD_FAST                'to_inventory_owner'
              370  LOAD_ATTR                inventory_component
              372  STORE_FAST               'to_inventory'
            374_0  COME_FROM           356  '356'
            374_1  COME_FROM           346  '346'

 L. 243       374  LOAD_FAST                'delivery_method'
              376  LOAD_GLOBAL              PickerInteractionDeliveryMethod
              378  LOAD_ATTR                INVENTORY
              380  COMPARE_OP               ==
          382_384  POP_JUMP_IF_TRUE    398  'to 398'
              386  LOAD_FAST                'delivery_method'
              388  LOAD_GLOBAL              PickerInteractionDeliveryMethod
              390  LOAD_ATTR                MAILMAN
              392  COMPARE_OP               ==
          394_396  POP_JUMP_IF_FALSE   520  'to 520'
            398_0  COME_FROM           382  '382'

 L. 244       398  LOAD_FAST                'to_inventory'
              400  LOAD_CONST               None
              402  COMPARE_OP               is
          404_406  POP_JUMP_IF_FALSE   440  'to 440'

 L. 245       408  LOAD_GLOBAL              sims4
              410  LOAD_ATTR                commands
              412  LOAD_METHOD              output
              414  LOAD_STR                 'inventory.purchase_picker_response: Inventory not found for items to be purchased into.'
              416  LOAD_FAST                '_connection'
              418  CALL_METHOD_2         2  '2 positional arguments'
              420  POP_TOP          

 L. 246       422  LOAD_GLOBAL              sims4
              424  LOAD_ATTR                commands
              426  LOAD_METHOD              automation_output
              428  LOAD_STR                 'PurchasePickerResponseInfo; Status:Failed, Message:Inventory not found for items to be purchased into.'
              430  LOAD_FAST                '_connection'
              432  CALL_METHOD_2         2  '2 positional arguments'
              434  POP_TOP          

 L. 247       436  LOAD_CONST               False
              438  RETURN_VALUE     
            440_0  COME_FROM           404  '404'

 L. 249       440  LOAD_FAST                'inventory_source'
              442  LOAD_ATTR                target_id
              444  LOAD_CONST               0
              446  COMPARE_OP               !=
          448_450  POP_JUMP_IF_FALSE   468  'to 468'

 L. 250       452  LOAD_FAST                'inventory_source'
              454  LOAD_METHOD              get_target
              456  CALL_METHOD_0         0  '0 positional arguments'
              458  STORE_FAST               'from_inventory_owner'

 L. 251       460  LOAD_FAST                'from_inventory_owner'
              462  LOAD_ATTR                inventory_component
              464  STORE_FAST               'from_inventory'
              466  JUMP_FORWARD        472  'to 472'
            468_0  COME_FROM           448  '448'

 L. 253       468  LOAD_CONST               None
              470  STORE_FAST               'from_inventory'
            472_0  COME_FROM           466  '466'

 L. 255       472  LOAD_FAST                'object_ids_or_definition_ids'
          474_476  POP_JUMP_IF_FALSE   520  'to 520'
              478  LOAD_FAST                'from_inventory'
              480  LOAD_CONST               None
              482  COMPARE_OP               is
          484_486  POP_JUMP_IF_FALSE   520  'to 520'

 L. 256       488  LOAD_GLOBAL              sims4
              490  LOAD_ATTR                commands
              492  LOAD_METHOD              output
              494  LOAD_STR                 'inventory.purchase_picker_response: Source Inventory not found for items to be cloned from.'
              496  LOAD_FAST                '_connection'
              498  CALL_METHOD_2         2  '2 positional arguments'
              500  POP_TOP          

 L. 257       502  LOAD_GLOBAL              sims4
              504  LOAD_ATTR                commands
              506  LOAD_METHOD              automation_output
              508  LOAD_STR                 'PurchasePickerResponseInfo; Status:Failed, Message:Source Inventory not found for items to be cloned from.'
              510  LOAD_FAST                '_connection'
              512  CALL_METHOD_2         2  '2 positional arguments'
              514  POP_TOP          

 L. 258       516  LOAD_CONST               False
              518  RETURN_VALUE     
            520_0  COME_FROM           484  '484'
            520_1  COME_FROM           474  '474'
            520_2  COME_FROM           394  '394'

 L. 260       520  LOAD_GLOBAL              dict
              522  CALL_FUNCTION_0       0  '0 positional arguments'
              524  STORE_FAST               'obj_purchased'

 L. 261   526_528  SETUP_LOOP         1058  'to 1058'
              530  LOAD_FAST                'objects_to_buy'
              532  GET_ITER         
            534_0  COME_FROM          1052  '1052'
          534_536  FOR_ITER           1056  'to 1056'
              538  UNPACK_SEQUENCE_3     3 
              540  STORE_FAST               'obj_or_def'
              542  STORE_FAST               'price'
              544  STORE_FAST               'amount'

 L. 262       546  LOAD_FAST                'amount'
              548  STORE_FAST               'amount_left'

 L. 264   550_552  SETUP_LOOP         1052  'to 1052'
            554_0  COME_FROM          1046  '1046'
            554_1  COME_FROM           872  '872'
            554_2  COME_FROM           694  '694'
              554  LOAD_FAST                'amount_left'
              556  LOAD_CONST               0
              558  COMPARE_OP               >
          560_562  POP_JUMP_IF_FALSE  1050  'to 1050'

 L. 265       564  LOAD_FAST                'delivery_method'
              566  LOAD_GLOBAL              PickerInteractionDeliveryMethod
              568  LOAD_ATTR                INVENTORY
              570  COMPARE_OP               ==
          572_574  POP_JUMP_IF_TRUE    588  'to 588'

 L. 266       576  LOAD_FAST                'delivery_method'
              578  LOAD_GLOBAL              PickerInteractionDeliveryMethod
              580  LOAD_ATTR                MAILMAN
              582  COMPARE_OP               ==
          584_586  POP_JUMP_IF_FALSE   632  'to 632'
            588_0  COME_FROM           572  '572'
              588  LOAD_FAST                'object_ids_or_definition_ids'
          590_592  POP_JUMP_IF_FALSE   632  'to 632'

 L. 270       594  LOAD_FAST                'from_inventory'
              596  LOAD_METHOD              try_remove_object_by_id
              598  LOAD_FAST                'obj_or_def'
              600  LOAD_ATTR                id
              602  LOAD_FAST                'obj_or_def'
              604  LOAD_METHOD              stack_count
              606  CALL_METHOD_0         0  '0 positional arguments'
              608  CALL_METHOD_2         2  '2 positional arguments'
              610  POP_TOP          

 L. 271       612  LOAD_FAST                'obj_or_def'
              614  LOAD_METHOD              clone
              616  CALL_METHOD_0         0  '0 positional arguments'
              618  STORE_FAST               'obj'

 L. 272       620  LOAD_FAST                'from_inventory'
              622  LOAD_METHOD              system_add_object
              624  LOAD_FAST                'obj_or_def'
              626  CALL_METHOD_1         1  '1 positional argument'
              628  POP_TOP          
              630  JUMP_FORWARD        698  'to 698'
            632_0  COME_FROM           590  '590'
            632_1  COME_FROM           584  '584'

 L. 274       632  LOAD_GLOBAL              create_object
              634  LOAD_FAST                'obj_or_def'
              636  CALL_FUNCTION_1       1  '1 positional argument'
              638  STORE_FAST               'obj'

 L. 275       640  LOAD_FAST                'obj'
              642  LOAD_CONST               None
              644  COMPARE_OP               is
          646_648  POP_JUMP_IF_FALSE   698  'to 698'

 L. 276       650  LOAD_GLOBAL              sims4
              652  LOAD_ATTR                commands
              654  LOAD_METHOD              output
              656  LOAD_STR                 'inventory.purchase_picker_response: Failed to create object with definition {}.'
              658  LOAD_METHOD              format
              660  LOAD_FAST                'obj_or_def'
              662  CALL_METHOD_1         1  '1 positional argument'
              664  LOAD_FAST                '_connection'
              666  CALL_METHOD_2         2  '2 positional arguments'
              668  POP_TOP          

 L. 277       670  LOAD_GLOBAL              sims4
              672  LOAD_ATTR                commands
              674  LOAD_METHOD              automation_output
              676  LOAD_STR                 'PurchasePickerResponseInfo; Status:Failed, Message:Failed to create object with definition {}.'
              678  LOAD_METHOD              format
              680  LOAD_FAST                'obj_or_def'
              682  CALL_METHOD_1         1  '1 positional argument'
              684  LOAD_FAST                '_connection'
              686  CALL_METHOD_2         2  '2 positional arguments'
              688  POP_TOP          

 L. 278       690  LOAD_CONST               0
              692  STORE_FAST               'amount_left'

 L. 279   694_696  CONTINUE            554  'to 554'
            698_0  COME_FROM           646  '646'
            698_1  COME_FROM           630  '630'

 L. 282       698  LOAD_FAST                'obj'
              700  LOAD_ATTR                inventoryitem_component
              702  LOAD_CONST               None
              704  COMPARE_OP               is
          706_708  POP_JUMP_IF_TRUE    728  'to 728'
              710  LOAD_FAST                'obj'
              712  LOAD_ATTR                inventoryitem_component
              714  LOAD_METHOD              get_stack_scheme
              716  CALL_METHOD_0         0  '0 positional arguments'
              718  LOAD_GLOBAL              StackScheme
              720  LOAD_ATTR                NONE
              722  COMPARE_OP               ==
          724_726  POP_JUMP_IF_FALSE   738  'to 738'
            728_0  COME_FROM           706  '706'

 L. 283       728  LOAD_FAST                'amount_left'
              730  LOAD_CONST               1
              732  BINARY_SUBTRACT  
              734  STORE_FAST               'amount_left'
              736  JUMP_FORWARD        752  'to 752'
            738_0  COME_FROM           724  '724'

 L. 287       738  LOAD_FAST                'obj'
              740  LOAD_METHOD              set_stack_count
              742  LOAD_FAST                'amount'
              744  CALL_METHOD_1         1  '1 positional argument'
              746  POP_TOP          

 L. 290       748  LOAD_CONST               0
              750  STORE_FAST               'amount_left'
            752_0  COME_FROM           736  '736'

 L. 294       752  LOAD_FAST                'obj'
              754  LOAD_METHOD              set_household_owner_id
              756  LOAD_FAST                'household'
              758  LOAD_ATTR                id
              760  CALL_METHOD_1         1  '1 positional argument'
              762  POP_TOP          

 L. 296       764  LOAD_FAST                'obj'
              766  LOAD_ATTR                try_post_bb_fixup
              768  LOAD_CONST               True
              770  LOAD_GLOBAL              services
              772  LOAD_METHOD              active_household_id
              774  CALL_METHOD_0         0  '0 positional arguments'
              776  LOAD_CONST               ('force_fixup', 'active_household_id')
              778  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              780  POP_TOP          

 L. 298       782  LOAD_FAST                'delivery_method'
              784  LOAD_GLOBAL              PickerInteractionDeliveryMethod
              786  LOAD_ATTR                INVENTORY
              788  COMPARE_OP               ==
          790_792  POP_JUMP_IF_TRUE    806  'to 806'
              794  LOAD_FAST                'delivery_method'
              796  LOAD_GLOBAL              PickerInteractionDeliveryMethod
              798  LOAD_ATTR                MAILMAN
              800  COMPARE_OP               ==
          802_804  POP_JUMP_IF_FALSE   876  'to 876'
            806_0  COME_FROM           790  '790'

 L. 299       806  LOAD_FAST                'to_inventory'
              808  LOAD_METHOD              player_try_add_object
              810  LOAD_FAST                'obj'
              812  CALL_METHOD_1         1  '1 positional argument'
          814_816  POP_JUMP_IF_TRUE    876  'to 876'

 L. 300       818  LOAD_GLOBAL              sims4
              820  LOAD_ATTR                commands
              822  LOAD_METHOD              output
              824  LOAD_STR                 'inventory.purchase_picker_response: Failed to add object into inventory: {}'
              826  LOAD_METHOD              format
              828  LOAD_FAST                'obj'
              830  CALL_METHOD_1         1  '1 positional argument'
              832  LOAD_FAST                '_connection'
              834  CALL_METHOD_2         2  '2 positional arguments'
              836  POP_TOP          

 L. 301       838  LOAD_GLOBAL              sims4
              840  LOAD_ATTR                commands
              842  LOAD_METHOD              automation_output
              844  LOAD_STR                 'PurchasePickerResponseInfo; Status:Failed, Message:Failed to add object into inventory: {}'
              846  LOAD_METHOD              format
              848  LOAD_FAST                'obj'
              850  CALL_METHOD_1         1  '1 positional argument'
              852  LOAD_FAST                '_connection'
              854  CALL_METHOD_2         2  '2 positional arguments'
              856  POP_TOP          

 L. 302       858  LOAD_FAST                'obj'
              860  LOAD_ATTR                destroy
              862  LOAD_FAST                'to_inventory'
              864  LOAD_STR                 'inventory.purchase_picker_response: Failed to add object into inventory.'
              866  LOAD_CONST               ('source', 'cause')
              868  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              870  POP_TOP          

 L. 303   872_874  CONTINUE            554  'to 554'
            876_0  COME_FROM           814  '814'
            876_1  COME_FROM           802  '802'

 L. 305       876  LOAD_FAST                'obj'
              878  LOAD_ATTR                definition
              880  LOAD_ATTR                id
              882  LOAD_FAST                'obj_purchased'
              884  COMPARE_OP               not-in
          886_888  POP_JUMP_IF_FALSE   910  'to 910'

 L. 306       890  LOAD_CONST               0
              892  LOAD_CONST               0
              894  BUILD_LIST_0          0 
              896  LOAD_CONST               ('price', 'amount', 'obj_ids')
              898  BUILD_CONST_KEY_MAP_3     3 
              900  LOAD_FAST                'obj_purchased'
              902  LOAD_FAST                'obj'
              904  LOAD_ATTR                definition
              906  LOAD_ATTR                id
              908  STORE_SUBSCR     
            910_0  COME_FROM           886  '886'

 L. 310       910  LOAD_FAST                'obj'
              912  LOAD_ATTR                inventoryitem_component
              914  LOAD_METHOD              get_stack_scheme
              916  CALL_METHOD_0         0  '0 positional arguments'
              918  LOAD_GLOBAL              StackScheme
              920  LOAD_ATTR                NONE
              922  COMPARE_OP               ==
          924_926  POP_JUMP_IF_FALSE   958  'to 958'

 L. 311       928  LOAD_FAST                'price'
              930  STORE_FAST               'purchase_price'

 L. 312       932  LOAD_FAST                'obj_purchased'
              934  LOAD_FAST                'obj'
              936  LOAD_ATTR                definition
              938  LOAD_ATTR                id
              940  BINARY_SUBSCR    
              942  LOAD_STR                 'amount'
              944  DUP_TOP_TWO      
              946  BINARY_SUBSCR    
              948  LOAD_CONST               1
              950  INPLACE_ADD      
              952  ROT_THREE        
              954  STORE_SUBSCR     
              956  JUMP_FORWARD        990  'to 990'
            958_0  COME_FROM           924  '924'

 L. 314       958  LOAD_FAST                'price'
              960  LOAD_FAST                'amount'
              962  BINARY_MULTIPLY  
              964  STORE_FAST               'purchase_price'

 L. 315       966  LOAD_FAST                'obj_purchased'
              968  LOAD_FAST                'obj'
              970  LOAD_ATTR                definition
              972  LOAD_ATTR                id
              974  BINARY_SUBSCR    
              976  LOAD_STR                 'amount'
              978  DUP_TOP_TWO      
              980  BINARY_SUBSCR    
              982  LOAD_FAST                'amount'
              984  INPLACE_ADD      
              986  ROT_THREE        
              988  STORE_SUBSCR     
            990_0  COME_FROM           956  '956'

 L. 316       990  LOAD_FAST                'obj_purchased'
              992  LOAD_FAST                'obj'
              994  LOAD_ATTR                definition
              996  LOAD_ATTR                id
              998  BINARY_SUBSCR    
             1000  LOAD_STR                 'price'
             1002  DUP_TOP_TWO      
             1004  BINARY_SUBSCR    
             1006  LOAD_FAST                'purchase_price'
             1008  INPLACE_ADD      
             1010  ROT_THREE        
             1012  STORE_SUBSCR     

 L. 317      1014  LOAD_FAST                'obj_purchased'
             1016  LOAD_FAST                'obj'
             1018  LOAD_ATTR                definition
             1020  LOAD_ATTR                id
             1022  BINARY_SUBSCR    
             1024  LOAD_STR                 'obj_ids'
             1026  BINARY_SUBSCR    
             1028  LOAD_METHOD              append
             1030  LOAD_FAST                'obj'
             1032  LOAD_ATTR                id
             1034  CALL_METHOD_1         1  '1 positional argument'
             1036  POP_TOP          

 L. 318      1038  LOAD_FAST                'current_purchased'
             1040  LOAD_FAST                'purchase_price'
             1042  INPLACE_ADD      
             1044  STORE_FAST               'current_purchased'
         1046_1048  JUMP_LOOP           554  'to 554'
           1050_0  COME_FROM           560  '560'
             1050  POP_BLOCK        
           1052_0  COME_FROM_LOOP      550  '550'
         1052_1054  JUMP_LOOP           534  'to 534'
             1056  POP_BLOCK        
           1058_0  COME_FROM_LOOP      526  '526'

 L. 321      1058  BUILD_LIST_0          0 
             1060  STORE_FAST               'choice_list'

 L. 322      1062  BUILD_LIST_0          0 
             1064  STORE_FAST               'choice_counts'

 L. 323      1066  BUILD_LIST_0          0 
             1068  STORE_FAST               'object_ids'

 L. 324      1070  SETUP_LOOP         1132  'to 1132'
             1072  LOAD_FAST                'obj_purchased'
             1074  LOAD_METHOD              items
             1076  CALL_METHOD_0         0  '0 positional arguments'
             1078  GET_ITER         
           1080_0  COME_FROM          1126  '1126'
             1080  FOR_ITER           1130  'to 1130'
             1082  UNPACK_SEQUENCE_2     2 
             1084  STORE_FAST               'obj_def_id'
             1086  STORE_FAST               'data'

 L. 325      1088  LOAD_FAST                'choice_list'
             1090  LOAD_METHOD              append
             1092  LOAD_FAST                'obj_def_id'
             1094  CALL_METHOD_1         1  '1 positional argument'
             1096  POP_TOP          

 L. 326      1098  LOAD_FAST                'choice_counts'
             1100  LOAD_METHOD              append
             1102  LOAD_FAST                'data'
             1104  LOAD_STR                 'amount'
             1106  BINARY_SUBSCR    
             1108  CALL_METHOD_1         1  '1 positional argument'
             1110  POP_TOP          

 L. 327      1112  LOAD_FAST                'object_ids'
             1114  LOAD_METHOD              append
             1116  LOAD_FAST                'data'
             1118  LOAD_STR                 'obj_ids'
             1120  BINARY_SUBSCR    
             1122  CALL_METHOD_1         1  '1 positional argument'
             1124  POP_TOP          
         1126_1128  JUMP_LOOP          1080  'to 1080'
             1130  POP_BLOCK        
           1132_0  COME_FROM_LOOP     1070  '1070'

 L. 328      1132  LOAD_GLOBAL              services
             1134  LOAD_METHOD              current_zone
             1136  CALL_METHOD_0         0  '0 positional arguments'
             1138  STORE_FAST               'zone'

 L. 329      1140  LOAD_FAST                'zone'
             1142  LOAD_ATTR                ui_dialog_service
             1144  LOAD_METHOD              dialog_pick_result_def_ids_and_counts
             1146  LOAD_FAST                'dialog_id'
             1148  LOAD_FAST                'choice_list'
             1150  LOAD_FAST                'object_ids'
             1152  LOAD_FAST                'choice_counts'
             1154  CALL_METHOD_4         4  '4 positional arguments'
             1156  POP_TOP          

 L. 330      1158  LOAD_GLOBAL              sims4
             1160  LOAD_ATTR                commands
             1162  LOAD_METHOD              automation_output
             1164  LOAD_STR                 'PurchasePickerResponseInfo; Status:Success'
             1166  LOAD_FAST                '_connection'
             1168  CALL_METHOD_2         2  '2 positional arguments'
             1170  POP_TOP          

 L. 331      1172  LOAD_FAST                'household'
             1174  LOAD_ATTR                try_remove_currency_amount
             1176  LOAD_FAST                'currency_type'
             1178  LOAD_FAST                'current_purchased'
             1180  LOAD_GLOBAL              Consts_pb2
             1182  LOAD_ATTR                TELEMETRY_OBJECT_BUY
             1184  LOAD_FAST                'obj_purchased'
             1186  LOAD_CONST               ('reason', 'obj_purchased')
             1188  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
             1190  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `CONTINUE' instruction at offset 872_874


@sims4.commands.Command('inventory.sell_picker_response_by_ids', command_type=(sims4.commands.CommandType.Live))
def sell_picker_response_by_ids(inventory_source, currency_type, dialog_id, *ids_and_amounts_and_price, _connection=None):
    total_price = 0
    inventory_manager = services.inventory_manager()
    client = services.client_manager().get(_connection)
    if client is None:
        sims4.commands.output('inventory.sell_picker_response: No client found to make selling.', _connection)
        return False
    if inventory_source.target_id != 0:
        source_inventory_owner = inventory_source.get_target()
        source_inventory = source_inventory_owner.inventory_component
    else:
        source_inventory = None
    if source_inventory is None:
        sims4.commands.output('inventory.sell_picker_response: Source Inventory not found for items to be sold from.', _connection)
        return False
    for obj_id, amount, price in zipids_and_amounts_and_price[::3]ids_and_amounts_and_price[1::3]ids_and_amounts_and_price[2::3]:
        obj = inventory_manager.get(obj_id)
        if obj is None:
            sims4.commands.output('inventory.purchase_picker_response: Object or Definition not found with id {}'.format(obj_id), _connection)
            return False
        else:
            if price == USE_DEFINITION_PRICE:
                price = obj.definition.price
            total_price += price * amount

    client.household.add_currency_amount(currency_type, total_price, Consts_pb2.TELEMETRY_OBJECT_SELL)
    zone = services.current_zone()
    sell_dialog = zone.ui_dialog_service.get_dialog(dialog_id)
    if sell_dialog is not None:
        sell_dialog.ids_and_amounts_and_price = ids_and_amounts_and_price
        sell_dialog.source_inventory = source_inventory
    return total_price


@sims4.commands.Command('inventory.open_ui', command_type=(sims4.commands.CommandType.Live))
def open_inventory_ui(inventory_obj: RequiredTargetParam, _connection=None):
    obj = inventory_obj.get_target()
    if obj is None:
        sims4.commands.output('Failed to get inventory_obj: {}.'.format(inventory_obj), _connection)
        return False
    comp = obj.inventory_component
    if comp is None:
        sims4.commands.output('inventory_obj does not have an inventory component: {}.'.format(inventory_obj), _connection)
        return False
    comp.open_ui_panel()
    return True


@sims4.commands.Command('inventory.view_update', command_type=(sims4.commands.CommandType.Live))
def inventory_view_update(obj_id: int=0, _connection=None):
    obj = services.current_zone().find_object(obj_id)
    if obj is not None:
        obj.inventory_view_update()
        return True
    return False


@sims4.commands.Command('inventory.sim_inventory_sell_multiple', command_type=(sims4.commands.CommandType.Live))
def sim_inventory_sell_multiple(msg: str, _connection=None):
    proto = UI_pb2.InventorySellRequest()
    text_format.Merge(msg, proto)
    if proto is None:
        return
    sim_info = services.sim_info_manager().get(proto.sim_id)
    if sim_info is None:
        return
    inventory_component = sim_info.get_sim_instance().inventory_component
    if inventory_component is None:
        return
    sell_value = 0
    objs = []
    inventory_stack_items = inventory_component.get_stack_items_map(proto.stacks)
    if proto.stacks is not None:
        for stack_id in proto.stacks:
            stack_items = inventory_stack_items.get(stack_id, None)
            if stack_items is None:
                continue
            else:
                for item in stack_items:
                    if item.non_deletable_by_user:
                        break
                    else:
                        sell_value += item.current_value * item.stack_count()
                        objs.append(item)

    if proto.items is not None:
        inventory_manager = services.inventory_manager()
        for item_data in proto.items:
            if item_data not in inventory_component:
                continue
            else:
                item = inventory_manager.get(item_data.id)
            if item is None:
                continue
            if item.non_deletable_by_user:
                continue
            else:
                sell_value += item.current_value * item_data.count
                item.update_stack_count(-item_data.count)
            if item.stack_count() < 1:
                objs.append(item)
            else:
                inventory_component.push_inventory_item_update_msg(item)

    if objs:
        services.active_household().add_currency_amountproto.currency_typesell_valueConsts_pb2.TELEMETRY_OBJECT_SELLsim_info
        services.get_reset_and_delete_service().trigger_batch_destroy(objs)
    op = SendUIMessage('InventorySellItemsComplete')
    Distributor.instance().add_op_with_no_owner(op)


@sims4.commands.Command('inventory.sim_inventory_favorite_multiple', command_type=(sims4.commands.CommandType.Live))
def sim_inventory_favorite_multiple(sim_id: int=0, is_add: bool=False, *items: int, _connection=None):
    sim_info = services.sim_info_manager().get(sim_id)
    if sim_info is None:
        return
    favorites_tracker = sim_info.favorites_tracker
    if favorites_tracker is None:
        return
    inventory_component = sim_info.get_sim_instance().inventory_component
    if inventory_component is None:
        return
    inventory_manager = services.inventory_manager()
    for item_id in items:
        item = inventory_manager.get(item_id)
        if is_add:
            favorites_tracker.set_favorite_stack(item)
        else:
            favorites_tracker.unset_favorite_stack(item)
        inventory_component.push_inventory_item_stack_update_msg(item)


@sims4.commands.Command('inventory.sim_inventory_census.instanced_sims', command_type=(CommandType.Automation))
def sim_inventory_census_instances_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    for sim in services.sim_info_manager().instanced_sims_gen():
        inv_comp = sim.inventory_component
        output('{:50} Inventory: {:4} Shelved: {:4}'.format(inv_comp, len(inv_comp), inv_comp.get_shelved_object_count()))


@sims4.commands.Command('inventory.sim_inventory_census.save_slot', command_type=(CommandType.Automation))
def sim_inventory_census_save_slot(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    definition_manager = services.definition_manager()
    active_household_id = services.active_household_id()
    total_objs = 0
    total_objs_active_house = 0
    total_objs_all_player_houses = 0
    counter = Counter
    stack_counter = Counter
    for sim_info in services.sim_info_manager().values():
        inventory_objs = len(sim_info.inventory_data.objects)
        for obj in sim_info.inventory_data.objects:
            obj_def = definition_manager.get(obj.guid)
            if obj_def is not None:
                counter[obj_def] += 1
            else:
                save_data = SimObjectAttributes_pb2.PersistenceMaster()
                save_data.ParseFromString(obj.attributes)
                for data in save_data.data:
                    if data.type == SimObjectAttributes_pb2.PersistenceMaster.PersistableData.InventoryItemComponent:
                        comp_data = data.Extensions[SimObjectAttributes_pb2.PersistableInventoryItemComponent.persistable_data]
                        stack_counter[obj_def] += comp_data.stack_count

        total_objs += inventory_objs
        if sim_info.is_player_sim:
            total_objs_all_player_houses += inventory_objs
        if sim_info.household.id == active_household_id:
            total_objs_active_house += inventory_objs

    dump = []
    dump.append(('#inventory objs', total_objs))
    dump.append(('#inventory objs active house', total_objs_active_house))
    dump.append(('#inventory objs all player houses', total_objs_all_player_houses))
    for name, value in dump:
        output('{:50} : {}'.format(name, value))

    output('{}'.format('----------------------------------------------------------------------------------------------------'))
    output('{:75} : {} / {}'.format('Obj Definition', 'PlayerFacing', 'Stacks'))
    for obj_def, count in stack_counter.most_common():
        output('{:75} : {:4} / {:4}'.format(obj_def, count, counter.get(obj_def)))

    return dump


@sims4.commands.Command('inventory.create_and_add_object_to_inventory')
def create_and_add_object_to_inventory(to_inventory_object_id: RequiredTargetParam, definition_id: int, _connection=None):
    to_inventory_owner = to_inventory_object_id.get_target()
    to_inventory = to_inventory_owner.inventory_component
    if to_inventory is None:
        sims4.commands.output('to inventory object does not have an inventory component: {}'.format(to_inventory_owner), _connection)
        return False
    obj = create_object(definition_id)
    if not to_inventory.player_try_add_object(obj):
        sims4.commands.output('object failed to be placed into inventory: {}'.format(obj), _connection)
        obj.destroy(source=to_inventory, cause='object failed to be placed into inventory')
        return False
    sims4.commands.output('object {} placed into inventory'.format(obj), _connection)
    return True


@sims4.commands.Command('qa.object_def.valid_inventory_types', command_type=(sims4.commands.CommandType.Automation))
def qa_object_def_valid_inventory_types(object_definition: TunableInstanceParam(sims4.resources.Types.OBJECT), _connection=None):
    sims4.commands.automation_output('QaObjDefValidInventoryTypes; Status:Begin', _connection)
    if object_definition is None:
        sims4.commands.automation_output('QaObjDefValidInventoryTypes; Status:End')
        return False
    if object_definition.cls._components.inventory_item is not None:
        valid_inventory_types = object_definition.cls._components.inventory_item._tuned_values.valid_inventory_types
        if valid_inventory_types is not None:
            for inventory_type in valid_inventory_types:
                sims4.commands.automation_output('QaObjDefValidInventoryTypes; Status:Data, InventoryType:{}'.format(inventory_type), _connection)

    sims4.commands.automation_output('QaObjDefValidInventoryTypes; Status:End', _connection)


@sims4.commands.Command('inventory.check_fashion_outfits', command_type=(sims4.commands.CommandType.DebugOnly))
def check_fashion_outfits_inventory(_connection=None):
    sim = services.get_active_sim()
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sim_inventory = sim.inventory_component
    if sim_inventory is None:
        sims4.commands.output('No valid inventory for sim.', _connection)
        return False
    sim_inventory.open_ui_panel()
    for inventory_item in sim_inventory:
        mannequin = inventory_item.mannequin_component
        sims4.commands.output('inventory_item {} - {}'.format(inventory_item, mannequin), _connection)
        if mannequin is not None:
            outfits = mannequin.get_outfits()
            if outfits is None:
                sims4.commands.output('there are no outfits on mannequin {}'.format(mannequin.id), _connection)
                return False
            else:
                output = sims4.commands.Output(_connection)
                output('Outfits: {}'.format(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)))
                for outfit_index, outfit_data in enumerate(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)):
                    output('\t\t{}: {}'.format(outfit_index, ', '.join((str(part) for part in outfit_data.part_ids))))

    return True


@sims4.commands.Command('inventory.get_inventory_outfit_tags', command_type=(sims4.commands.CommandType.DebugOnly))
def get_inventory_outfit_tags(_connection=None):
    sim = services.get_active_sim()
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    dominant_trend_cost = {}
    for dominant_trend_tag, trend_cost in FashionThriftStoreTuning.DOMINANT_TREND_ITEM_COST.items():
        dominant_trend_cost[dominant_trend_tag] = trend_cost
        sims4.commands.output('{}:{} = {}'.format(dominant_trend_tag, dominant_trend_tag.value, trend_cost), _connection)

    sim_inventory = sim.inventory_component
    if sim_inventory is None:
        sims4.commands.output('No valid inventory for sim.', _connection)
        return False
    fashion_trend_service = services.fashion_trend_service()
    if fashion_trend_service is None:
        sims4.commands.output('Could not access fashion trend service', _connection)
        return False
    sim_inventory.open_ui_panel()
    for inventory_item in sim_inventory:
        mannequin = inventory_item.mannequin_component
        sims4.commands.output('inventory_item {} - {}'.format(inventory_item, mannequin), _connection)
        if mannequin is not None:
            outfits = mannequin.get_outfits()
            if outfits is None:
                sims4.commands.output('there are no outfits on mannequin {}'.format(mannequin.id), _connection)
                return False
            else:
                output = sims4.commands.Output(_connection)
                output('Outfits: {}'.format(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)))
                for outfit_index, outfit_data in enumerate(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)):
                    output('\t\t{}: {}'.format(outfit_index, ', '.join((str(part) for part in outfit_data.part_ids))))

                tags = get_tags_from_outfitoutfits._baseOutfitCategory.EVERYDAY0
                sims4.commands.output('Tags for outfit are: {}'.format(tags), _connection)
                inventory_outfit_data = outfits.get_outfit(OutfitCategory.EVERYDAY, 0)
                prevalent_trend_tag = fashion_trend_service.get_outfit_trend(inventory_outfit_data)
                sims4.commands.output('The dominant trend tag is: {}'.format(prevalent_trend_tag), _connection)
                all_trend_style_tags = fashion_trend_service.get_outfit_all_trend_styles(tags)
                sims4.commands.output('The trend style tags for this outfit are: {}'.format(all_trend_style_tags), _connection)
                if prevalent_trend_tag is not None:
                    prevalent_trend_tag_hash = FashionTrendTuning.TRENDS[prevalent_trend_tag].trend_name
                    prevalent_trend_tag_loc_object = LocalizationHelperTuning.get_raw_text(prevalent_trend_tag_hash)
                    sims4.commands.output('The dominant trend hash is: {}'.format(prevalent_trend_tag_hash), _connection)
                    sims4.commands.output('The dominant trend localized string object is: {}'.format(prevalent_trend_tag_loc_object), _connection)
                    sims4.commands.output('Trend Icon: {}'.format(inventory_item.icon), _connection)
                sims4.commands.output('', _connection)

    return True


@sims4.commands.Command('inventory.check_hidden_inventory_outfits', command_type=(sims4.commands.CommandType.DebugOnly))
def check_hidden_inventory_outfits(_connection=None):
    sim = services.get_active_sim()
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sim_inventory = sim.inventory_component
    if sim_inventory is None:
        sims4.commands.output('No valid inventory for sim.', _connection)
        return False
    for inventory_item in sim_inventory:
        inventory_item_hidden = inventory_item.inventoryitem_component.is_hidden
        if inventory_item_hidden:
            sims4.commands.output('Outfit {} is hidden'.format(inventory_item), _connection)
            mannequin = inventory_item.mannequin_component
            sims4.commands.output('inventory_item {} - {}'.format(inventory_item, mannequin), _connection)
            if mannequin is not None:
                outfits = mannequin.get_outfits()
                if outfits is None:
                    sims4.commands.output('there are no outfits on mannequin {}'.format(mannequin.id), _connection)
                    return False
                else:
                    output = sims4.commands.Output(_connection)
                    output('Outfits: {}'.format(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)))
                    for outfit_index, outfit_data in enumerate(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)):
                        output('\t\t{}: {}'.format(outfit_index, ', '.join((str(part) for part in outfit_data.part_ids))))

                    sims4.commands.output('', _connection)

    return True


@sims4.commands.Command('inventory.open_ui_with_preselection', command_type=(sims4.commands.CommandType.Live))
def open_ui_with_preselection(opt_sim: OptionalSimInfoParam=None, filter_tag: int=None, _connection=None):
    sim_info = get_optional_target(opt_target=opt_sim, _connection=_connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sim = sim_info.get_sim_instance()
    if sim is None:
        sims4.commands.output('No valid sim specified.', _connection)
        return False
    sim_inventory = sim.inventory_component
    if sim_inventory is None:
        sims4.commands.output('No valid inventory for sim.', _connection)
        return False
    if filter_tag is None:
        sims4.commands.output('No valid filter tag supplied.', _connection)
        return False
    sim_inventory.open_ui_panel_with_preselected_filters(filter_tag=filter_tag)
    return True