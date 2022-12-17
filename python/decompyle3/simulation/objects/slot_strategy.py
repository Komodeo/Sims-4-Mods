# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\slot_strategy.py
# Compiled at: 2021-06-04 12:34:11
# Size of source mod 2**32: 17072 bytes
from build_buy import _buildbuy, remove_object_from_household_inventory
from objects.gallery_tuning import ContentSource
from random import shuffle
from event_testing.resolver import InteractionResolver, DoubleObjectResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType, ParticipantTypeSingle
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableEnumEntry, TunableReference, OptionalTunable, TunableVariant, TunableList, Tunable, TunableRange
import services, sims4.log, sims4.resources
logger = sims4.log.Logger('SlotStrategy', default_owner='amwu')

class SlotStrategyVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, slot_type_strategy=SlotStrategyTargetSlotType.TunableFactory(), 
         auto_slotting=SlotStrategyAutoSlot.TunableFactory(), 
         default='slot_type_strategy', **kwargs)


class SelectObjectVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, object_participant=SelectSourceParticipant.TunableFactory(), 
         inventory_objects=SelectInventoryObjects.TunableFactory(), 
         default='object_participant', **kwargs)


class SelectObjectBase:

    def __init__(self, resolver, slot_target, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.resolver = resolver
        self.slot_target = slot_target

    def get_objects(self, *args, **kwargs):
        raise NotImplementedError


class SelectSourceParticipant(HasTunableFactory, AutoFactoryInit, SelectObjectBase):
    FACTORY_TUNABLES = {'transfer_participant': TunableEnumEntry(description='\n            A participant to be slotted.\n            ',
                               tunable_type=ParticipantType,
                               default=(ParticipantType.Object))}

    def get_objects(self, *args, **kwargs):
        return {participant for participant in self.resolver.get_participants(self.transfer_participant)}


class SelectInventoryObjects(HasTunableFactory, AutoFactoryInit, SelectObjectBase):
    FACTORY_TUNABLES = {'inventory_participant':TunableEnumEntry(description='\n            The participant with the inventory we want to pull objects from.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'object_tests':TunableTestSet(description='\n            Tests whether or not an object in the inventory should be\n            transferred to a target slot or not.\n            \n            If this is being tuned in an interaction, the object in question\n            will be the Picked Item participant. This is so that we can keep\n            the resolver in case we want to test the actor or target as well.\n            \n            In other cases, the participant will be Actor, and the slot target\n            will be Object.\n            ')}

    def get_objects(self, *args, preferred_slots=None, **kwargs):
        inventory_owner = self.resolver.get_participant(self.inventory_participant)
        if inventory_owner is None:
            logger.error('Inventory Participant {} is None for slot object selection {}', self.inventory_participant, self.resolver)
            return set()
        is_interaction_resolver = isinstance(self.resolver, InteractionResolver)
        if is_interaction_resolver:
            interaction_params = self.resolver.interaction_parameters.copy()
            inventory_owner = self.resolver.interaction.get_participant(self.inventory_participant)
        valid_objects = set()
        if inventory_owner.inventory_component is None:
            logger.error('Inventory Component for Participant {} is None for slot object selection {}', self.inventory_participant, self.resolver)
            return set()
        for obj in inventory_owner.inventory_component:
            if is_interaction_resolver:
                interaction_parameters = {'picked_item_ids': [obj.id]}
                self.resolver.interaction_parameters.update(interaction_parameters)
                resolver = self.resolver
            else:
                resolver = DoubleObjectResolver(obj, self.slot_target)
            if not self.object_tests.run_tests(resolver):
                continue
            if preferred_slots is not None:
                if not any([slot_type in obj.all_valid_slot_types for slot_type in preferred_slots]):
                    continue
                valid_objects.add(obj)

        if is_interaction_resolver:
            self.resolver.interaction_parameters = interaction_params
        return valid_objects


class SlotStrategyBase(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'max_number_of_objects':TunableRange(description='\n            The number of objects we would like to slot into the target.\n            Obviously the number of valid objects available and the number of\n            free slots must accommodate this interval. However, it will fail\n            silently if we run out of either. This is essentially a firemeter\n            on how many objects we care to try and slot.\n            ',
       tunable_type=int,
       default=15,
       minimum=1,
       maximum=20), 
     'objects_to_slot':SelectObjectVariant(description='\n            The selection for objects to be slotted into the slot target.\n            '), 
     'slot_target':TunableEnumEntry(description='\n            The participant we want to slot objects into.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Object), 
     'require_claiming':OptionalTunable(description='\n            If enabled, if True:\n            Object slotted by this strategy will require claiming on load \n            (by some 3rd party) or they will be destroyed on load.\n            \n            If False:\n            If previously requiring claiming on load, objects slotted by this\n            strategy will no longer require claiming on load, and thus will \n            persist without fetters.\n            ',
       tunable=Tunable(description='\n                If checked, objects that are slotted by this strategy will\n                require claiming on load or they will be destroyed.\n                \n                If unchecked, objects that are slotted by this strategy will \n                no longer require claiming on load to avoid destruction if \n                they previously did.\n                ',
       tunable_type=bool,
       default=False)), 
     'use_part_owner':Tunable(description='\n            If enabled and slot target is a part, we will slot objects to the part owner\n            instead of the part.\n            ',
       tunable_type=bool,
       default=False)}

    def __init__(self, resolver, target=None, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.target = target
        if target is None:
            self.target = resolver.get_participant(self.slot_target)
        if self.use_part_owner:
            if self.target is not None:
                if self.target.is_part:
                    self.target = self.target.part_owner
        self.source = self.objects_to_slot(resolver, self.target)

    def slot_objects(self):
        raise NotImplementedError

    def _do_claim(self, obj):
        if self.require_claiming is None:
            return
        if self.require_claiming is False:
            obj.remove_claim_requirement()
        else:
            obj.claim()

    def _retrieve_from_household_inventory(self, obj):
        object_id = obj.id
        household_id = obj.get_household_owner_id()
        household_manager = services.household_manager()
        object_data_raw = _buildbuy.get_object_data_in_household_inventory(object_id, household_id)
        if object_data_raw is None:
            logger.error('Failed to retrieve object data for {} from household inventory.', object_id)
            return
        obj.destroy()
        removed = remove_object_from_household_inventory(object_id, (household_manager.get(household_id)), update_funds=False)
        if not removed:
            logger.error('Failed to remove object {} from household inventory.', object_id)
            return
        obj = household_manager.create_object_from_raw_inv_data(object_id, object_data_raw, load_object=True)
        return obj


class SlotStrategyTargetSlotType(SlotStrategyBase):
    FACTORY_TUNABLES = {'target_slot_type': TunableReference(description='\n            Slot type to place the transfered objects into the participant\n            target. Obviously the slot type must be available on the target\n            object and the source must support it.\n            ',
                           manager=(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE)))}

    def slot_objects--- This code section failed: ---

 L. 279         0  LOAD_CONST               0
                2  STORE_FAST               'num_slotted'

 L. 280         4  SETUP_LOOP          208  'to 208'
                6  LOAD_FAST                'self'
                8  LOAD_ATTR                source
               10  LOAD_ATTR                get_objects
               12  LOAD_FAST                'self'
               14  LOAD_ATTR                target_slot_type
               16  BUILD_TUPLE_1         1 
               18  LOAD_CONST               ('preferred_slots',)
               20  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               22  GET_ITER         
             24_0  COME_FROM           204  '204'
               24  FOR_ITER            206  'to 206'
               26  STORE_FAST               'obj'

 L. 281        28  LOAD_FAST                'num_slotted'
               30  LOAD_FAST                'self'
               32  LOAD_ATTR                max_number_of_objects
               34  COMPARE_OP               >=
               36  POP_JUMP_IF_FALSE    40  'to 40'

 L. 282        38  BREAK_LOOP       
             40_0  COME_FROM            36  '36'

 L. 283        40  LOAD_FAST                'obj'
               42  LOAD_METHOD              get_inventory
               44  CALL_METHOD_0         0  '0 positional arguments'
               46  STORE_FAST               'inventory'

 L. 284        48  SETUP_LOOP          204  'to 204'
               50  LOAD_FAST                'self'
               52  LOAD_ATTR                target
               54  LOAD_ATTR                get_runtime_slots_gen
               56  LOAD_FAST                'self'
               58  LOAD_ATTR                target_slot_type
               60  BUILD_SET_1           1 
               62  LOAD_CONST               ('slot_types',)
               64  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               66  GET_ITER         
             68_0  COME_FROM           200  '200'
             68_1  COME_FROM            86  '86'
               68  FOR_ITER            202  'to 202'
               70  STORE_FAST               'runtime_slot'

 L. 285        72  LOAD_FAST                'runtime_slot'
               74  LOAD_ATTR                is_valid_for_placement
               76  LOAD_FAST                'obj'
               78  LOAD_CONST               ('obj',)
               80  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               82  STORE_FAST               'result'

 L. 286        84  LOAD_FAST                'result'
               86  POP_JUMP_IF_FALSE_LOOP    68  'to 68'

 L. 287        88  LOAD_FAST                'inventory'
               90  LOAD_CONST               None
               92  COMPARE_OP               is-not
               94  POP_JUMP_IF_FALSE   126  'to 126'
               96  LOAD_FAST                'inventory'
               98  LOAD_METHOD              try_remove_object_by_id
              100  LOAD_FAST                'obj'
              102  LOAD_ATTR                id
              104  CALL_METHOD_1         1  '1 positional argument'
              106  POP_JUMP_IF_TRUE    126  'to 126'

 L. 288       108  LOAD_GLOBAL              logger
              110  LOAD_METHOD              error
              112  LOAD_STR                 'Failed to remove object {} from inventory'
              114  LOAD_FAST                'obj'
              116  LOAD_FAST                'inventory'
              118  CALL_METHOD_3         3  '3 positional arguments'
              120  POP_TOP          

 L. 289       122  BREAK_LOOP       
              124  JUMP_FORWARD        170  'to 170'
            126_0  COME_FROM           106  '106'
            126_1  COME_FROM            94  '94'

 L. 291       126  LOAD_FAST                'obj'
              128  LOAD_ATTR                content_source
              130  LOAD_GLOBAL              ContentSource
              132  LOAD_ATTR                HOUSEHOLD_INVENTORY_PROXY
              134  COMPARE_OP               ==
              136  POP_JUMP_IF_FALSE   170  'to 170'

 L. 292       138  LOAD_FAST                'self'
              140  LOAD_METHOD              _retrieve_from_household_inventory
              142  LOAD_FAST                'obj'
              144  CALL_METHOD_1         1  '1 positional argument'
              146  STORE_FAST               'obj'

 L. 293       148  LOAD_FAST                'obj'
              150  LOAD_CONST               None
              152  COMPARE_OP               is
              154  POP_JUMP_IF_FALSE   170  'to 170'

 L. 294       156  LOAD_GLOBAL              logger
              158  LOAD_METHOD              error
              160  LOAD_STR                 'Failed to remove object {} from household inventory'
              162  LOAD_FAST                'obj'
              164  CALL_METHOD_2         2  '2 positional arguments'
              166  POP_TOP          

 L. 295       168  BREAK_LOOP       
            170_0  COME_FROM           154  '154'
            170_1  COME_FROM           136  '136'
            170_2  COME_FROM           124  '124'

 L. 296       170  LOAD_FAST                'runtime_slot'
              172  LOAD_METHOD              add_child
              174  LOAD_FAST                'obj'
              176  CALL_METHOD_1         1  '1 positional argument'
              178  POP_TOP          

 L. 297       180  LOAD_FAST                'self'
              182  LOAD_METHOD              _do_claim
              184  LOAD_FAST                'obj'
              186  CALL_METHOD_1         1  '1 positional argument'
              188  POP_TOP          

 L. 298       190  LOAD_FAST                'num_slotted'
              192  LOAD_CONST               1
              194  INPLACE_ADD      
              196  STORE_FAST               'num_slotted'

 L. 299       198  BREAK_LOOP       
              200  JUMP_LOOP            68  'to 68'
              202  POP_BLOCK        
            204_0  COME_FROM_LOOP       48  '48'
              204  JUMP_LOOP            24  'to 24'
              206  POP_BLOCK        
            208_0  COME_FROM_LOOP        4  '4'

 L. 301       208  LOAD_FAST                'num_slotted'
              210  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `BREAK_LOOP' instruction at offset 198


class SlotStrategyAutoSlot(SlotStrategyBase):
    FACTORY_TUNABLES = {'slot_types':TunableList(description='\n            The slot types we want to fill. Order denotes priority, as we will grab unique objects that fill those slots.\n            ',
       tunable=TunableReference(description='\n                Slot type to place the transfered objects into the participant\n                target. Obviously the slot type must be available on the target\n                object and the source must support it.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE))),
       unique_entries=True), 
     'evenly_distribute_slot_types':Tunable(description='\n            If enabled, we will attempt to go down the slot types list\n            one at a time and pull a unique object, then repeat the\n            list until the desired number of objects has been slotted,\n            we run out of objects, or we run out of slots.\n            ',
       tunable_type=bool,
       default=True)}

    def slot_objects--- This code section failed: ---

 L. 333         0  LOAD_FAST                'self'
                2  LOAD_ATTR                target
                4  LOAD_METHOD              get_provided_slot_types
                6  CALL_METHOD_0         0  '0 positional arguments'
                8  STORE_DEREF              'provided_slot_types'

 L. 334        10  LOAD_CLOSURE             'provided_slot_types'
               12  BUILD_TUPLE_1         1 
               14  LOAD_LISTCOMP            '<code_object <listcomp>>'
               16  LOAD_STR                 'SlotStrategyAutoSlot.slot_objects.<locals>.<listcomp>'
               18  MAKE_FUNCTION_CLOSURE        'closure'
               20  LOAD_FAST                'self'
               22  LOAD_ATTR                slot_types
               24  GET_ITER         
               26  CALL_FUNCTION_1       1  '1 positional argument'
               28  STORE_FAST               'desired_slot_types'

 L. 336        30  LOAD_CONST               0
               32  STORE_FAST               'num_slotted'

 L. 337        34  LOAD_CONST               True
               36  STORE_FAST               'continue_slotting'

 L. 338        38  LOAD_GLOBAL              set
               40  CALL_FUNCTION_0       0  '0 positional arguments'
               42  STORE_FAST               'slotted_objects'

 L. 339     44_46  SETUP_LOOP          360  'to 360'
             48_0  COME_FROM           356  '356'
               48  LOAD_FAST                'num_slotted'
               50  LOAD_FAST                'self'
               52  LOAD_ATTR                max_number_of_objects
               54  COMPARE_OP               <
            56_58  POP_JUMP_IF_FALSE   358  'to 358'
               60  LOAD_FAST                'continue_slotting'
            62_64  POP_JUMP_IF_FALSE   358  'to 358'

 L. 342        66  LOAD_CONST               False
               68  STORE_FAST               'continue_slotting'

 L. 345     70_72  SETUP_LOOP          356  'to 356'
               74  LOAD_FAST                'desired_slot_types'
               76  GET_ITER         
             78_0  COME_FROM           352  '352'
             78_1  COME_FROM           122  '122'
            78_80  FOR_ITER            354  'to 354'
               82  STORE_FAST               'slot_type'

 L. 346        84  LOAD_LISTCOMP            '<code_object <listcomp>>'
               86  LOAD_STR                 'SlotStrategyAutoSlot.slot_objects.<locals>.<listcomp>'
               88  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               90  LOAD_FAST                'self'
               92  LOAD_ATTR                target
               94  LOAD_ATTR                get_runtime_slots_gen
               96  LOAD_FAST                'slot_type'
               98  BUILD_SET_1           1 
              100  LOAD_CONST               ('slot_types',)
              102  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              104  GET_ITER         
              106  CALL_FUNCTION_1       1  '1 positional argument'
              108  STORE_FAST               'available_slots'

 L. 347       110  LOAD_GLOBAL              shuffle
              112  LOAD_FAST                'available_slots'
              114  CALL_FUNCTION_1       1  '1 positional argument'
              116  POP_TOP          

 L. 348       118  LOAD_FAST                'available_slots'
              120  POP_JUMP_IF_TRUE    124  'to 124'

 L. 350       122  CONTINUE             78  'to 78'
            124_0  COME_FROM           120  '120'

 L. 352       124  LOAD_FAST                'self'
              126  LOAD_ATTR                source
              128  LOAD_ATTR                get_objects
              130  LOAD_FAST                'slot_type'
              132  BUILD_TUPLE_1         1 
              134  LOAD_CONST               ('preferred_slots',)
              136  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              138  STORE_FAST               'objects_to_slot'

 L. 353       140  LOAD_FAST                'objects_to_slot'
              142  LOAD_METHOD              difference_update
              144  LOAD_FAST                'slotted_objects'
              146  CALL_METHOD_1         1  '1 positional argument'
              148  POP_TOP          

 L. 354       150  SETUP_LOOP          352  'to 352'
              152  LOAD_FAST                'objects_to_slot'
              154  GET_ITER         
            156_0  COME_FROM           348  '348'
            156_1  COME_FROM           344  '344'
            156_2  COME_FROM           340  '340'
              156  FOR_ITER            350  'to 350'
              158  STORE_FAST               'obj'

 L. 355       160  SETUP_LOOP          324  'to 324'
              162  LOAD_FAST                'available_slots'
              164  GET_ITER         
            166_0  COME_FROM           320  '320'
            166_1  COME_FROM           224  '224'
            166_2  COME_FROM           180  '180'
              166  FOR_ITER            322  'to 322'
              168  STORE_FAST               'runtime_slot'

 L. 356       170  LOAD_FAST                'runtime_slot'
              172  LOAD_ATTR                is_valid_for_placement
              174  LOAD_FAST                'obj'
              176  LOAD_CONST               ('obj',)
              178  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              180  POP_JUMP_IF_FALSE_LOOP   166  'to 166'

 L. 357       182  LOAD_FAST                'obj'
              184  LOAD_METHOD              get_inventory
              186  CALL_METHOD_0         0  '0 positional arguments'
              188  STORE_FAST               'inventory'

 L. 358       190  LOAD_FAST                'inventory'
              192  LOAD_CONST               None
              194  COMPARE_OP               is-not
              196  POP_JUMP_IF_FALSE   228  'to 228'
              198  LOAD_FAST                'inventory'
              200  LOAD_METHOD              try_remove_object_by_id
              202  LOAD_FAST                'obj'
              204  LOAD_ATTR                id
              206  CALL_METHOD_1         1  '1 positional argument'
              208  POP_JUMP_IF_TRUE    228  'to 228'

 L. 359       210  LOAD_GLOBAL              logger
              212  LOAD_METHOD              error
              214  LOAD_STR                 'Failed to remove object {} from inventory'
              216  LOAD_FAST                'obj'
              218  LOAD_FAST                'inventory'
              220  CALL_METHOD_3         3  '3 positional arguments'
              222  POP_TOP          

 L. 360       224  CONTINUE            166  'to 166'
              226  JUMP_FORWARD        276  'to 276'
            228_0  COME_FROM           208  '208'
            228_1  COME_FROM           196  '196'

 L. 362       228  LOAD_FAST                'obj'
              230  LOAD_ATTR                content_source
              232  LOAD_GLOBAL              ContentSource
              234  LOAD_ATTR                HOUSEHOLD_INVENTORY_PROXY
              236  COMPARE_OP               ==
          238_240  POP_JUMP_IF_FALSE   276  'to 276'

 L. 363       242  LOAD_FAST                'self'
              244  LOAD_METHOD              _retrieve_from_household_inventory
              246  LOAD_FAST                'obj'
              248  CALL_METHOD_1         1  '1 positional argument'
              250  STORE_FAST               'obj'

 L. 364       252  LOAD_FAST                'obj'
              254  LOAD_CONST               None
              256  COMPARE_OP               is
          258_260  POP_JUMP_IF_FALSE   276  'to 276'

 L. 365       262  LOAD_GLOBAL              logger
              264  LOAD_METHOD              error
              266  LOAD_STR                 'Failed to remove object {} from household inventory'
              268  LOAD_FAST                'obj'
              270  CALL_METHOD_2         2  '2 positional arguments'
              272  POP_TOP          

 L. 366       274  BREAK_LOOP       
            276_0  COME_FROM           258  '258'
            276_1  COME_FROM           238  '238'
            276_2  COME_FROM           226  '226'

 L. 367       276  LOAD_FAST                'runtime_slot'
              278  LOAD_METHOD              add_child
              280  LOAD_FAST                'obj'
              282  CALL_METHOD_1         1  '1 positional argument'
              284  POP_TOP          

 L. 368       286  LOAD_FAST                'self'
              288  LOAD_METHOD              _do_claim
              290  LOAD_FAST                'obj'
              292  CALL_METHOD_1         1  '1 positional argument'
              294  POP_TOP          

 L. 369       296  LOAD_FAST                'num_slotted'
              298  LOAD_CONST               1
              300  INPLACE_ADD      
              302  STORE_FAST               'num_slotted'

 L. 370       304  LOAD_FAST                'slotted_objects'
              306  LOAD_METHOD              add
              308  LOAD_FAST                'obj'
              310  CALL_METHOD_1         1  '1 positional argument'
              312  POP_TOP          

 L. 371       314  LOAD_CONST               True
              316  STORE_FAST               'continue_slotting'

 L. 372       318  BREAK_LOOP       
              320  JUMP_LOOP           166  'to 166'
              322  POP_BLOCK        
            324_0  COME_FROM_LOOP      160  '160'

 L. 377       324  LOAD_FAST                'num_slotted'
              326  LOAD_FAST                'self'
              328  LOAD_ATTR                max_number_of_objects
              330  COMPARE_OP               >=
          332_334  POP_JUMP_IF_TRUE    346  'to 346'
              336  LOAD_FAST                'self'
              338  LOAD_ATTR                evenly_distribute_slot_types
              340  POP_JUMP_IF_FALSE_LOOP   156  'to 156'
              342  LOAD_FAST                'continue_slotting'
              344  POP_JUMP_IF_FALSE_LOOP   156  'to 156'
            346_0  COME_FROM           332  '332'

 L. 378       346  BREAK_LOOP       
              348  JUMP_LOOP           156  'to 156'
              350  POP_BLOCK        
            352_0  COME_FROM_LOOP      150  '150'
              352  JUMP_LOOP            78  'to 78'
              354  POP_BLOCK        
            356_0  COME_FROM_LOOP       70  '70'
              356  JUMP_LOOP            48  'to 48'
            358_0  COME_FROM            62  '62'
            358_1  COME_FROM            56  '56'
              358  POP_BLOCK        
            360_0  COME_FROM_LOOP       44  '44'

 L. 380       360  LOAD_FAST                'num_slotted'
              362  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `BREAK_LOOP' instruction at offset 318