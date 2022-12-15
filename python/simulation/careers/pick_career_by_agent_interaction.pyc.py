# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\pick_career_by_agent_interaction.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 5226 bytes
from event_testing.resolver import SingleSimResolver
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from traits.trait_tracker import TraitPickerSuperInteraction
from ui.ui_dialog_picker import ObjectPickerRow
import services, sims4
logger = sims4.log.Logger('PickCareerByAgentInteraction')

class PickCareerByAgentInteraction(TraitPickerSuperInteraction):
    INSTANCE_TUNABLES = {'pickable_careers': TunableList(description='\n            A list of careers whose available agents will be used to populate\n            the picker. When an available agent is selected, the sim actor will\n            be placed in the associated career. A career may have multiple\n            agents, in which case each will appear and each will correspond to\n            that career.\n            ',
                           tunable=TunableReference(manager=(services.get_instance_manager(Types.CAREER)),
                           pack_safe=True),
                           tuning_group=(GroupNames.PICKERTUNING),
                           unique_entries=True)}

    @classmethod
    def _get_agent_traits_for_career_gen(cls, sim_info, career):
        career_history = sim_info.career_tracker.career_history
        entry_level, _, career_track = next(career.get_career_entry_level(career_history=career_history, resolver=(SingleSimResolver(sim_info))))
        for agent_trait in career_track.career_levels[entry_level].agents_available:
            yield agent_trait

    @classmethod
    def _agent_trait_selection_gen(cls, target):
        for career in cls.pickable_careers:
            if target.sim_info.career_tracker.has_career_by_uid(career.guid64):
                continue
            else:
                career_selectable_result = career.is_career_selectable(sim_info=(target.sim_info))
                disabled_tooltip = None
            if not career_selectable_result:
                if career_selectable_result.tooltip is not None:
                    disabled_tooltip = career_selectable_result.tooltip
                else:
                    logger.error("{} did not pass career_selectable_tests and doesn't have disabled tooltip.", career, owner='yozhang')
                    continue
            for trait in cls._get_agent_traits_for_career_gen(target.sim_info, career):
                yield (
                 trait, disabled_tooltip)

    def on_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is None:
            return
        sim_info = self.target.sim_info
        for career in self.pickable_careers:
            if choice_tag in self._get_agent_traits_for_career_gen(sim_info, career):
                sim_info.career_tracker.add_career((career(sim_info)), post_quit_msg=False)
                (super().on_choice_selected)(choice_tag, **kwargs)
                return

    @flexmethod
    def picker_rows_gen--- This code section failed: ---

 L.  92         0  LOAD_DEREF               'target'
                2  LOAD_ATTR                sim_info
                4  LOAD_ATTR                trait_tracker
                6  STORE_FAST               'trait_tracker'

 L.  93         8  SETUP_LOOP          154  'to 154'
               10  LOAD_DEREF               'cls'
               12  LOAD_METHOD              _agent_trait_selection_gen
               14  LOAD_DEREF               'target'
               16  CALL_METHOD_1         1  '1 positional argument'
               18  GET_ITER         
             20_0  COME_FROM           150  '150'
             20_1  COME_FROM            46  '46'
             20_2  COME_FROM            32  '32'
               20  FOR_ITER            152  'to 152'
               22  UNPACK_SEQUENCE_2     2 
               24  STORE_FAST               'trait'
               26  STORE_FAST               'disabled_tooltip'

 L.  94        28  LOAD_FAST                'trait'
               30  LOAD_ATTR                display_name
               32  POP_JUMP_IF_FALSE_LOOP    20  'to 20'

 L.  95        34  LOAD_FAST                'trait'
               36  LOAD_METHOD              display_name
               38  LOAD_DEREF               'target'
               40  CALL_METHOD_1         1  '1 positional argument'
               42  STORE_FAST               'display_name'
               44  JUMP_FORWARD         48  'to 48'

 L. 101        46  CONTINUE             20  'to 20'
             48_0  COME_FROM            44  '44'

 L. 103        48  LOAD_CONST               True
               50  STORE_FAST               'is_enabled'

 L. 104        52  LOAD_CONST               None
               54  STORE_FAST               'row_tooltip'

 L. 105        56  LOAD_FAST                'trait_tracker'
               58  LOAD_METHOD              has_trait
               60  LOAD_FAST                'trait'
               62  CALL_METHOD_1         1  '1 positional argument'
               64  POP_JUMP_IF_FALSE   100  'to 100'

 L. 106        66  LOAD_CONST               False
               68  STORE_FAST               'is_enabled'

 L. 107        70  LOAD_DEREF               'cls'
               72  LOAD_ATTR                already_equipped_tooltip
               74  LOAD_CONST               None
               76  COMPARE_OP               is
               78  POP_JUMP_IF_FALSE    84  'to 84'
               80  LOAD_CONST               None
               82  JUMP_FORWARD         96  'to 96'
             84_0  COME_FROM            78  '78'
               84  LOAD_CLOSURE             'cls'
               86  LOAD_CLOSURE             'target'
               88  BUILD_TUPLE_2         2 
               90  LOAD_LAMBDA              '<code_object <lambda>>'
               92  LOAD_STR                 'PickCareerByAgentInteraction.picker_rows_gen.<locals>.<lambda>'
               94  MAKE_FUNCTION_CLOSURE        'closure'
             96_0  COME_FROM            82  '82'
               96  STORE_FAST               'row_tooltip'
               98  JUMP_FORWARD        116  'to 116'
            100_0  COME_FROM            64  '64'

 L. 108       100  LOAD_FAST                'disabled_tooltip'
              102  LOAD_CONST               None
              104  COMPARE_OP               is-not
              106  POP_JUMP_IF_FALSE   116  'to 116'

 L. 109       108  LOAD_CONST               False
              110  STORE_FAST               'is_enabled'

 L. 110       112  LOAD_FAST                'disabled_tooltip'
              114  STORE_FAST               'row_tooltip'
            116_0  COME_FROM           106  '106'
            116_1  COME_FROM            98  '98'

 L. 112       116  LOAD_GLOBAL              ObjectPickerRow
              118  LOAD_FAST                'display_name'
              120  LOAD_FAST                'trait'
              122  LOAD_METHOD              trait_description
              124  LOAD_DEREF               'target'
              126  CALL_METHOD_1         1  '1 positional argument'

 L. 113       128  LOAD_FAST                'trait'
              130  LOAD_ATTR                icon
              132  LOAD_FAST                'trait'
              134  LOAD_FAST                'is_enabled'
              136  LOAD_FAST                'row_tooltip'
              138  LOAD_CONST               ('name', 'row_description', 'icon', 'tag', 'is_enable', 'row_tooltip')
              140  CALL_FUNCTION_KW_6     6  '6 total positional and keyword args'
              142  STORE_FAST               'row'

 L. 114       144  LOAD_FAST                'row'
              146  YIELD_VALUE      
              148  POP_TOP          
              150  JUMP_LOOP            20  'to 20'
              152  POP_BLOCK        
            154_0  COME_FROM_LOOP        8  '8'

Parse error at or near `CONTINUE' instruction at offset 46