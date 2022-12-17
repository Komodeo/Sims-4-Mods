# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_type_picker_interaction.py
# Compiled at: 2020-07-17 13:31:28
# Size of source mod 2**32: 5292 bytes
import enum
from interactions.base.picker_interaction import PickerSuperInteraction
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableEnumEntry, OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from traits.trait_type import TraitType
from ui.ui_dialog_picker import ObjectPickerRow
import services, sims4

class TraitsToShow(enum.Int):
    ALL_TRAITS = ...
    EQUIPPED_ONLY = ...
    UNEQUIPPED_ONLY = ...


class TraitTypePickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'trait_type':TunableEnumEntry(description='\n            The type of traits to display in this picker.\n            ',
       tunable_type=TraitType,
       default=TraitType.PERSONALITY,
       tuning_group=GroupNames.PICKERTUNING), 
     'disabled_row_tooltip':OptionalTunable(description='\n            If enabled, the tooltip to display if the row is disabled.\n            ',
       tunable=TunableLocalizedStringFactory(),
       tuning_group=GroupNames.PICKERTUNING), 
     'traits_to_show':TunableEnumEntry(description='\n            Which traits should be shown in the picker.\n            ',
       tunable_type=TraitsToShow,
       default=TraitsToShow.ALL_TRAITS,
       tuning_group=GroupNames.PICKERTUNING)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._equipped_traits = set()

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.sim), target_sim=(self.sim))
        return True
        if False:
            yield None

    @classmethod
    def _trait_selection_gen(cls, target):
        trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
        for trait in trait_manager.types.values():
            if trait.trait_type == cls.trait_type:
                yield trait

    @flexmethod
    def picker_rows_gen--- This code section failed: ---

 L.  73         0  LOAD_FAST                'target'
                2  LOAD_ATTR                sim_info
                4  LOAD_ATTR                trait_tracker
                6  STORE_FAST               'trait_tracker'

 L.  74         8  SETUP_LOOP          192  'to 192'
               10  LOAD_FAST                'cls'
               12  LOAD_METHOD              _trait_selection_gen
               14  LOAD_FAST                'target'
               16  CALL_METHOD_1         1  '1 positional argument'
               18  GET_ITER         
             20_0  COME_FROM           188  '188'
             20_1  COME_FROM            82  '82'
             20_2  COME_FROM            74  '74'
             20_3  COME_FROM            50  '50'
               20  FOR_ITER            190  'to 190'
               22  STORE_FAST               'trait'

 L.  77        24  LOAD_FAST                'trait_tracker'
               26  LOAD_METHOD              has_trait
               28  LOAD_FAST                'trait'
               30  CALL_METHOD_1         1  '1 positional argument'
               32  STORE_FAST               'is_selected'

 L.  78        34  LOAD_FAST                'cls'
               36  LOAD_ATTR                traits_to_show
               38  LOAD_GLOBAL              TraitsToShow
               40  LOAD_ATTR                UNEQUIPPED_ONLY
               42  COMPARE_OP               ==
               44  POP_JUMP_IF_FALSE    60  'to 60'

 L.  79        46  LOAD_FAST                'is_selected'
               48  POP_JUMP_IF_FALSE    54  'to 54'

 L.  80        50  CONTINUE             20  'to 20'
               52  JUMP_FORWARD         90  'to 90'
             54_0  COME_FROM            48  '48'

 L.  82        54  LOAD_CONST               False
               56  STORE_FAST               'selected_status'
               58  JUMP_FORWARD         90  'to 90'
             60_0  COME_FROM            44  '44'

 L.  83        60  LOAD_FAST                'cls'
               62  LOAD_ATTR                traits_to_show
               64  LOAD_GLOBAL              TraitsToShow
               66  LOAD_ATTR                EQUIPPED_ONLY
               68  COMPARE_OP               ==
               70  POP_JUMP_IF_FALSE    86  'to 86'

 L.  84        72  LOAD_FAST                'is_selected'
               74  POP_JUMP_IF_FALSE_LOOP    20  'to 20'

 L.  85        76  LOAD_CONST               False
               78  STORE_FAST               'selected_status'
               80  JUMP_FORWARD         90  'to 90'

 L.  87        82  CONTINUE             20  'to 20'
               84  JUMP_FORWARD         90  'to 90'
             86_0  COME_FROM            70  '70'

 L.  89        86  LOAD_FAST                'is_selected'
               88  STORE_FAST               'selected_status'
             90_0  COME_FROM            84  '84'
             90_1  COME_FROM            80  '80'
             90_2  COME_FROM            58  '58'
             90_3  COME_FROM            52  '52'

 L.  91        90  LOAD_FAST                'is_selected'
               92  POP_JUMP_IF_FALSE   114  'to 114'
               94  LOAD_FAST                'inst'
               96  LOAD_CONST               None
               98  COMPARE_OP               is-not
              100  POP_JUMP_IF_FALSE   114  'to 114'

 L.  92       102  LOAD_FAST                'inst'
              104  LOAD_ATTR                _equipped_traits
              106  LOAD_METHOD              add
              108  LOAD_FAST                'trait'
              110  CALL_METHOD_1         1  '1 positional argument'
              112  POP_TOP          
            114_0  COME_FROM           100  '100'
            114_1  COME_FROM            92  '92'

 L.  96       114  LOAD_CONST               True
              116  STORE_FAST               'is_enabled'

 L.  97       118  LOAD_FAST                'is_selected'
              120  POP_JUMP_IF_TRUE    132  'to 132'

 L.  98       122  LOAD_FAST                'trait_tracker'
              124  LOAD_METHOD              can_add_trait
              126  LOAD_FAST                'trait'
              128  CALL_METHOD_1         1  '1 positional argument'
              130  STORE_FAST               'is_enabled'
            132_0  COME_FROM           120  '120'

 L. 100       132  LOAD_CONST               None
              134  STORE_FAST               'row_tooltip'

 L. 101       136  LOAD_FAST                'is_enabled'
              138  POP_JUMP_IF_TRUE    146  'to 146'

 L. 102       140  LOAD_FAST                'cls'
              142  LOAD_ATTR                disabled_row_tooltip
              144  STORE_FAST               'row_tooltip'
            146_0  COME_FROM           138  '138'

 L. 104       146  LOAD_GLOBAL              ObjectPickerRow
              148  LOAD_FAST                'trait'
              150  LOAD_METHOD              display_name
              152  LOAD_FAST                'target'
              154  CALL_METHOD_1         1  '1 positional argument'

 L. 105       156  LOAD_FAST                'trait'
              158  LOAD_METHOD              trait_description
              160  LOAD_FAST                'target'
              162  CALL_METHOD_1         1  '1 positional argument'

 L. 106       164  LOAD_FAST                'trait'
              166  LOAD_ATTR                icon

 L. 107       168  LOAD_FAST                'trait'

 L. 108       170  LOAD_FAST                'selected_status'

 L. 109       172  LOAD_FAST                'is_enabled'

 L. 110       174  LOAD_FAST                'row_tooltip'
              176  LOAD_CONST               ('name', 'row_description', 'icon', 'tag', 'is_selected', 'is_enable', 'row_tooltip')
              178  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
              180  STORE_FAST               'row'

 L. 111       182  LOAD_FAST                'row'
              184  YIELD_VALUE      
              186  POP_TOP          
              188  JUMP_LOOP            20  'to 20'
              190  POP_BLOCK        
            192_0  COME_FROM_LOOP        8  '8'

Parse error at or near `JUMP_FORWARD' instruction at offset 84

    def _update_traits(self, selected_traits):
        traits_to_remove = self._equipped_traits - selected_traits
        for trait in traits_to_remove:
            self.target.sim_info.remove_trait(trait)

        traits_to_add = selected_traits - self._equipped_traits
        for trait in traits_to_add:
            self.target.sim_info.add_trait(trait)

    def on_choice_selected(self, choice_tag, **kwargs):
        selected_traits = set((choice_tag,))
        self._update_traits(selected_traits)

    def on_multi_choice_selected(self, choice_tags, **kwargs):
        selected_traits = set(choice_tags)
        self._update_traits(selected_traits)