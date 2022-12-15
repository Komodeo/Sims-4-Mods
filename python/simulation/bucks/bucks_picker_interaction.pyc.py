# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\bucks_picker_interaction.py
# Compiled at: 2018-08-21 16:25:16
# Size of source mod 2**32: 4369 bytes
from bucks.bucks_enums import BucksType
from bucks.bucks_utils import BucksUtils
from interactions import ParticipantTypeSingleSim
from interactions.base.picker_interaction import PickerSuperInteraction
from sims4.localization import LocalizationHelperTuning
from sims4.tuning.tunable import Tunable, TunableEnumEntry, TunableList
from sims4.utils import flexmethod
from ui.ui_dialog_picker import ObjectPickerRow
from interactions.utils.tunable import TunableContinuation
from sims4.tuning.tunable_base import GroupNames

class BucksPerkPickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'is_add':Tunable(description='\n            If this interaction is trying to add a bucks perk to the sim or to\n            remove a bucks perk from the sim.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.PICKERTUNING), 
     'bucks_type':TunableEnumEntry(description='\n            The type of Bucks required to unlock/lock this perk.\n            ',
       tunable_type=BucksType,
       default=BucksType.INVALID,
       pack_safe=True,
       invalid_enums=(
      BucksType.INVALID,),
       tuning_group=GroupNames.PICKERTUNING), 
     'continuations':TunableList(description='\n            List of continuations to push if a buff is actually selected.\n            ',
       tunable=TunableContinuation(),
       tuning_group=GroupNames.PICKERTUNING), 
     'subject':TunableEnumEntry(description='\n            From whom the BucksPerks should be added/removed.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.TargetSim,
       tuning_group=GroupNames.PICKERTUNING)}

    def _run_interaction_gen(self, timeline):
        participant = self.get_participant(self.subject)
        self._show_picker_dialog(participant, target_sim=participant)
        return True
        if False:
            yield None

    @classmethod
    def _bucks_perk_selection_gen(cls, participant):
        bucks_perk_tracker = BucksUtils.get_tracker_for_bucks_type((cls.bucks_type), (participant.id), add_if_none=True)
        get_unlocked = not cls.is_add
        for perk in bucks_perk_tracker.all_perks_of_type_with_lock_state_gen(cls.bucks_type, get_unlocked):
            yield perk

    @flexmethod
    def picker_rows_gen--- This code section failed: ---

 L.  73         0  LOAD_FAST                'inst'
                2  LOAD_CONST               None
                4  COMPARE_OP               is-not
                6  POP_JUMP_IF_FALSE    12  'to 12'
                8  LOAD_FAST                'inst'
               10  JUMP_FORWARD         14  'to 14'
             12_0  COME_FROM             6  '6'
               12  LOAD_FAST                'cls'
             14_0  COME_FROM            10  '10'
               14  STORE_FAST               'inst_or_cls'

 L.  74        16  LOAD_FAST                'inst_or_cls'
               18  LOAD_ATTR                get_participant
               20  LOAD_FAST                'inst_or_cls'
               22  LOAD_ATTR                subject
               24  LOAD_FAST                'context'
               26  LOAD_ATTR                sim
               28  LOAD_FAST                'target'
               30  LOAD_CONST               ('sim', 'target')
               32  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               34  STORE_FAST               'participant'

 L.  75        36  SETUP_LOOP          108  'to 108'
               38  LOAD_FAST                'cls'
               40  LOAD_METHOD              _bucks_perk_selection_gen
               42  LOAD_FAST                'participant'
               44  CALL_METHOD_1         1  '1 positional argument'
               46  GET_ITER         
             48_0  COME_FROM           104  '104'
             48_1  COME_FROM            70  '70'
             48_2  COME_FROM            56  '56'
               48  FOR_ITER            106  'to 106'
               50  STORE_FAST               'perk'

 L.  76        52  LOAD_FAST                'perk'
               54  LOAD_ATTR                display_name
               56  POP_JUMP_IF_FALSE_LOOP    48  'to 48'

 L.  77        58  LOAD_FAST                'perk'
               60  LOAD_METHOD              display_name
               62  LOAD_FAST                'participant'
               64  CALL_METHOD_1         1  '1 positional argument'
               66  STORE_FAST               'display_name'
               68  JUMP_FORWARD         72  'to 72'

 L.  82        70  CONTINUE             48  'to 48'
             72_0  COME_FROM            68  '68'

 L.  84        72  LOAD_GLOBAL              ObjectPickerRow
               74  LOAD_FAST                'display_name'
               76  LOAD_FAST                'perk'
               78  LOAD_METHOD              perk_description
               80  LOAD_FAST                'participant'
               82  CALL_METHOD_1         1  '1 positional argument'

 L.  85        84  LOAD_FAST                'perk'
               86  LOAD_ATTR                icon
               88  LOAD_ATTR                key
               90  LOAD_FAST                'perk'
               92  LOAD_CONST               ('name', 'row_description', 'icon', 'tag')
               94  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
               96  STORE_FAST               'row'

 L.  86        98  LOAD_FAST                'row'
              100  YIELD_VALUE      
              102  POP_TOP          
              104  JUMP_LOOP            48  'to 48'
              106  POP_BLOCK        
            108_0  COME_FROM_LOOP       36  '36'

Parse error at or near `CONTINUE' instruction at offset 70

    def on_choice_selected(self, choice_tag, **kwargs):
        perk = choice_tag
        if perk is None:
            return
        participant = self.get_participant(self.subject)
        bucks_perk_tracker = BucksUtils.get_tracker_for_bucks_type(self.bucks_type, participant.id)
        if self.is_add:
            bucks_perk_tracker.pay_for_and_unlock_perk(perk)
        else:
            bucks_perk_tracker.lock_perk(perk, True)
        for continuation in self.continuations:
            self.push_tunable_continuation(continuation)