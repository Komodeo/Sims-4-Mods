# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\drama_node_tests.py
# Compiled at: 2022-02-09 10:21:47
# Size of source mod 2**32: 24176 bytes
from date_and_time import TimeSpan
from drama_scheduler.drama_enums import DramaNodeScoringBucket
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.results import TestResult
from event_testing.test_events import TestEvent
from caches import cached_test
from interactions import ParticipantTypeSingleSim
from sims4.tuning.tunable import Tunable, OptionalTunable, TunableTuple, TunableReference, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableList, TunableThreshold
import event_testing.test_base, services, sims4
from tunable_time import TunableTimeSpanSingleton
logger = sims4.log.Logger('DramaNodeTests', default_owner='jjacobson')

class FestivalRunningTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node':OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at all of the festival drama nodes.\n            ',
       tunable=TunableReference(description='\n                Reference to the festival drama node that we want to be running.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', )),
       enabled_by_default=True), 
     'check_if_on_festival_street':OptionalTunable(description="\n            If enabled, test against if the player is on the festival's street.\n            ",
       tunable=Tunable(description="\n                If checked, this test will pass only if the player is on the\n                festival's street. If unchecked, the test will pass only if the\n                player is not on the festival street.\n                ",
       tunable_type=bool,
       default=True)), 
     'valid_time_blocks':TunableTuple(description='\n            Festival drama nodes have a tunable pre-festival duration that\n            delay festival start to some point after the drama node has\n            started. For example, if the festival drama node has a pre-festival\n            duration of 2 hours and the drama node runs at 8am, the festival\n            will not start until 10am.\n\n            By default, this test passes if the festival drama node is running,\n            regardless if the festival is in its pre-festival duration. This\n            tuning changes that behavior.\n            ',
       pre_festival=Tunable(description='\n                If the festival is currently in its pre-festival duration,\n                test can pass if this is checked and fails if unchecked.\n                ',
       tunable_type=bool,
       default=True),
       running=Tunable(description='\n                If the festival is running (it is past its pre-festival\n                duration), test can pass if this is checked and fails if\n                unchecked.\n                ',
       tunable_type=bool,
       default=True)), 
     'negate':Tunable(description='\n            If enabled this test will pass if no festivals of the tuned\n            requirements are running.\n            ',
       tunable_type=bool,
       default=False), 
     'festivals_to_check':OptionalTunable(description='\n            If enabled then we will only check a subset of all festival drama nodes referenced here.\n            This will only apply if there is no specific drama node specified.\n            ',
       tunable=TunableList(description='\n                A list of festival drama nodes that we want to check against.\n                ',
       tunable=TunableReference(description='\n                    Reference to the festival drama node that we want to check against.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', ))))}
    test_events = (
     TestEvent.FestivalStarted,)

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__--- This code section failed: ---

 L. 110         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              drama_scheduler_service
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'drama_scheduler'

 L. 111         8  SETUP_LOOP          170  'to 170'
               10  LOAD_FAST                'drama_scheduler'
               12  LOAD_METHOD              active_nodes_gen
               14  CALL_METHOD_0         0  '0 positional arguments'
               16  GET_ITER         
             18_0  COME_FROM           144  '144'
             18_1  COME_FROM           132  '132'
             18_2  COME_FROM           114  '114'
             18_3  COME_FROM            88  '88'
             18_4  COME_FROM            70  '70'
             18_5  COME_FROM            44  '44'
               18  FOR_ITER            168  'to 168'
               20  STORE_FAST               'node'

 L. 114        22  LOAD_FAST                'self'
               24  LOAD_ATTR                drama_node
               26  LOAD_CONST               None
               28  COMPARE_OP               is
               30  POP_JUMP_IF_FALSE    74  'to 74'

 L. 115        32  LOAD_FAST                'node'
               34  LOAD_ATTR                drama_node_type
               36  LOAD_GLOBAL              DramaNodeType
               38  LOAD_ATTR                FESTIVAL
               40  COMPARE_OP               !=
               42  POP_JUMP_IF_FALSE    46  'to 46'

 L. 116        44  CONTINUE             18  'to 18'
             46_0  COME_FROM            42  '42'

 L. 117        46  LOAD_FAST                'self'
               48  LOAD_ATTR                festivals_to_check
               50  LOAD_CONST               None
               52  COMPARE_OP               is-not
               54  POP_JUMP_IF_FALSE    90  'to 90'
               56  LOAD_GLOBAL              type
               58  LOAD_FAST                'node'
               60  CALL_FUNCTION_1       1  '1 positional argument'
               62  LOAD_FAST                'self'
               64  LOAD_ATTR                festivals_to_check
               66  COMPARE_OP               not-in
               68  POP_JUMP_IF_FALSE    90  'to 90'

 L. 118        70  CONTINUE             18  'to 18'
               72  JUMP_FORWARD         90  'to 90'
             74_0  COME_FROM            30  '30'

 L. 120        74  LOAD_GLOBAL              type
               76  LOAD_FAST                'node'
               78  CALL_FUNCTION_1       1  '1 positional argument'
               80  LOAD_FAST                'self'
               82  LOAD_ATTR                drama_node
               84  COMPARE_OP               is-not
               86  POP_JUMP_IF_FALSE    90  'to 90'

 L. 121        88  CONTINUE             18  'to 18'
             90_0  COME_FROM            86  '86'
             90_1  COME_FROM            72  '72'
             90_2  COME_FROM            68  '68'
             90_3  COME_FROM            54  '54'

 L. 123        90  LOAD_FAST                'self'
               92  LOAD_ATTR                check_if_on_festival_street
               94  LOAD_CONST               None
               96  COMPARE_OP               is-not
               98  POP_JUMP_IF_FALSE   116  'to 116'

 L. 124       100  LOAD_FAST                'self'
              102  LOAD_ATTR                check_if_on_festival_street
              104  LOAD_FAST                'node'
              106  LOAD_METHOD              is_on_festival_street
              108  CALL_METHOD_0         0  '0 positional arguments'
              110  COMPARE_OP               !=
              112  POP_JUMP_IF_FALSE   116  'to 116'

 L. 125       114  CONTINUE             18  'to 18'
            116_0  COME_FROM           112  '112'
            116_1  COME_FROM            98  '98'

 L. 128       116  LOAD_FAST                'node'
              118  LOAD_METHOD              is_during_pre_festival
              120  CALL_METHOD_0         0  '0 positional arguments'
              122  POP_JUMP_IF_FALSE   136  'to 136'

 L. 129       124  LOAD_FAST                'self'
              126  LOAD_ATTR                valid_time_blocks
              128  LOAD_ATTR                pre_festival
              130  POP_JUMP_IF_TRUE    146  'to 146'

 L. 130       132  CONTINUE             18  'to 18'
              134  JUMP_FORWARD        146  'to 146'
            136_0  COME_FROM           122  '122'

 L. 132       136  LOAD_FAST                'self'
              138  LOAD_ATTR                valid_time_blocks
              140  LOAD_ATTR                running
              142  POP_JUMP_IF_TRUE    146  'to 146'

 L. 133       144  CONTINUE             18  'to 18'
            146_0  COME_FROM           142  '142'
            146_1  COME_FROM           134  '134'
            146_2  COME_FROM           130  '130'

 L. 135       146  LOAD_FAST                'self'
              148  LOAD_ATTR                negate
              150  POP_JUMP_IF_FALSE   162  'to 162'

 L. 136       152  LOAD_GLOBAL              TestResult
              154  LOAD_CONST               False

 L. 137       156  LOAD_STR                 'Drama nodes match the required conditions.'
              158  CALL_FUNCTION_2       2  '2 positional arguments'
              160  RETURN_VALUE     
            162_0  COME_FROM           150  '150'

 L. 138       162  LOAD_GLOBAL              TestResult
              164  LOAD_ATTR                TRUE
              166  RETURN_VALUE     
              168  POP_BLOCK        
            170_0  COME_FROM_LOOP        8  '8'

 L. 139       170  LOAD_FAST                'self'
              172  LOAD_ATTR                negate
              174  POP_JUMP_IF_FALSE   182  'to 182'

 L. 140       176  LOAD_GLOBAL              TestResult
              178  LOAD_ATTR                TRUE
              180  RETURN_VALUE     
            182_0  COME_FROM           174  '174'

 L. 141       182  LOAD_GLOBAL              TestResult
              184  LOAD_CONST               False

 L. 142       186  LOAD_STR                 'No drama nodes match the required conditions.'
              188  CALL_FUNCTION_2       2  '2 positional arguments'
              190  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `CONTINUE' instruction at offset 114


class NextFestivalTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node':OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at all of the festival drama nodes.\n            ',
       tunable=TunableReference(description='\n                Reference to the festival drama node that we want to be the\n                next one.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', )),
       enabled_by_default=True), 
     'negate':Tunable(description='\n            If enabled this test will pass if the next festival is not one of\n            the tuned nodes.\n            ',
       tunable_type=bool,
       default=False), 
     'festivals_to_check':OptionalTunable(description='\n            If enabled then we will only check a subset of all festival drama nodes referenced here.\n            ',
       tunable=TunableList(description='\n                A list of festival drama nodes that we want to check against.\n                ',
       tunable=TunableReference(description='\n                    Reference to the festival drama node that we want to check against.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', ))))}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        drama_scheduler = services.drama_scheduler_service
        best_time = None
        best_nodes = [type(node) for node in drama_scheduler.active_nodes_gen if node.drama_node_type == DramaNodeType.FESTIVAL if not self.festivals_to_check is None if type(node) in self.festivals_to_check]
        if not best_nodes:
            for node in drama_scheduler.scheduled_nodes_gen:
                if node.drama_node_type != DramaNodeType.FESTIVAL:
                    continue
                if self.festivals_to_check is not None:
                    if type(node) not in self.festivals_to_check:
                        continue
                new_time = node._selected_time - services.time_service.sim_now
                if best_time is None or new_time < best_time:
                    best_nodes = [
                     type(node)]
                    best_time = new_time
                if new_time == best_time:
                    best_nodes.append(type(node))

        if not best_nodes:
            if self.negate:
                return TestResult.TRUE
            return TestResultFalse'No scheduled Festivals.'
        if self.drama_node is None or self.drama_node in best_nodes:
            if self.negate:
                return TestResultFalse'Next scheduled Festival matches requested.'
            return TestResult.TRUE
        if self.negate:
            return TestResult.TRUE
        return TestResultFalse"Next scheduled Festival doesn't match requested."


class TimeUntilFestivalTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node':OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at any of the festival drama nodes.\n            ',
       tunable=TunableReference(description='\n                Reference to the festival drama node that we want to test.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', )),
       enabled_by_default=True), 
     'max_time':Tunable(description='\n            Maximum time in hours between when the test occurs to the start of\n            the festival in order for the test to return true.\n            ',
       tunable_type=float,
       default=18.0), 
     'negate':Tunable(description='\n            If enabled this test will pass if the requested festival will not\n            start within the specified time.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        drama_scheduler = services.drama_scheduler_service
        best_time = None
        for node in drama_scheduler.scheduled_nodes_gen:
            if node.drama_node_type != DramaNodeType.FESTIVAL:
                continue
            if not self.drama_node is None:
                if self.drama_node is type(node):
                    pass
            new_time = node.get_time_remaining
            if not best_time is None:
                if new_time < best_time:
                    pass
            best_time = new_time

        if best_time is None:
            if not self.negate:
                return TestResult(False, 'No scheduled Festivals of type {}.', (self.drama_node),
                  tooltip=(self.tooltip))
        else:
            pass
        if best_time.in_hours < self.max_time:
            if self.negate:
                return TestResult(False, 'Next scheduled Festival is within specified time',
                  tooltip=(self.tooltip))
        else:
            if not self.negate:
                return TestResult(False, "Next scheduled Festival isn't within specified time",
                  tooltip=(self.tooltip))
        return TestResult.TRUE


class DramaNodeTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_nodes':TunableList(description='\n            The types of drama nodes that we want to check.\n            ',
       tunable=TunableReference(description='\n                A Drama node type we want to check.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       pack_safe=True)), 
     'check_scheduled_nodes':Tunable(description='\n            Check against nodes that are scheduled, but not actively running.\n            ',
       tunable_type=bool,
       default=True), 
     'check_active_nodes':Tunable(description='\n            Check against nodes that are actively running.\n            ',
       tunable_type=bool,
       default=True), 
     'situation_type':OptionalTunable(description='\n            If a situation exists on the drama node, specify the type of situation to check.\n            ',
       tunable=TunableReference(description='\n                The type of situation the drama node has. \n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)))), 
     'situation_host_sim':OptionalTunable(description='\n            If a situation exist on the drama node, specify who the host of that situation should be.\n            ',
       tunable=TunableEnumEntry(description='\n                The required host of the situation. \n                ',
       tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.Actor))), 
     'situation_special_object_exists':OptionalTunable(description='\n            If enabled and a situation exists on the drama node, specify if\n            the situation should have a special object associated with it. \n            ',
       tunable=Tunable(description='\n                If checked, require the situation to have a special object. \n                ',
       tunable_type=bool,
       default=True)), 
     'exists':Tunable(description='\n            If checked then this drama node will pass if a node meeting the requirements exists.\n            Otherwise it will pass if there is not a node meeting the requirements.\n            ',
       tunable_type=bool,
       default=True), 
     'receiver_sim':OptionalTunable(description='\n            If enabled we will check that the receiver Sim is the tuned Sim.\n            ',
       tunable=TunableEnumEntry(description='\n                The Sim that we will make sure is the receiver Sim.\n                ',
       tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.TargetSim))), 
     'time_to_run':OptionalTunable(description='\n            If enabled then we will check against the remaining time until the the drama node is scheduled to run.\n            ',
       tunable=TunableTuple(threshold=TunableThreshold(description='\n                    A threshold to compare the amount of time left for this drma node to be run.\n                    ',
       value=TunableTimeSpanSingleton(description='\n                        The amount of time to compare against.\n                        '),
       default=(sims4.math.Threshold(TimeSpan.ZERO, sims4.math.Operator.GREATER_OR_EQUAL.function))),
       additional_threshold=OptionalTunable(description='\n                    If enabled then we will have a second threshold to compare against.\n                    ',
       tunable=TunableThreshold(description='\n                        A threshold to compare the amount of time left for this drma node to be run.\n                        ',
       value=TunableTimeSpanSingleton(description='\n                            The amount of time to compare against.\n                            '),
       default=(sims4.math.Threshold(TimeSpan.ZERO, sims4.math.Operator.GREATER_OR_EQUAL.function))))))}

    def get_expected_args(self):
        expected_args = {}
        if self.situation_host_sim is not None:
            expected_args['situation_host_sims'] = self.situation_host_sim
        if self.receiver_sim is not None:
            expected_args['receiver_sim'] = self.receiver_sim
        return expected_args

    @cached_test
    def __call__(self, receiver_sim=None, situation_host_sims=None):
        if not self.drama_nodes:
            if self.exists:
                return TestResult(False, 'No drama node exists meeting the requirements.',
                  tooltip=(self.tooltip))
            return TestResult.TRUE
        drama_scheduler = services.drama_scheduler_service
        if self.check_scheduled_nodes and self.check_active_nodes:
            drama_node_gen = drama_scheduler.all_nodes_gen
        else:
            if self.check_scheduled_nodes:
                drama_node_gen = drama_scheduler.scheduled_nodes_gen
            else:
                if self.check_active_nodes:
                    drama_node_gen = drama_scheduler.active_nodes_gen
                else:
                    if self.exists:
                        return TestResult(False, 'No drama node exists meeting the requirements.',
                          tooltip=(self.tooltip))
                    return TestResult.TRUE
        if receiver_sim is not None:
            receiver_sim = next(iter(receiver_sim))
        now = services.time_service.sim_now
        for drama_node in drama_node_gen():
            if type(drama_node) not in self.drama_nodes:
                continue
            else:
                situation_seed = drama_node.get_situation_seed
            if situation_seed is not None:
                if self.situation_type is not None:
                    if situation_seed.situation_type != self.situation_type:
                        continue
                if situation_host_sims is not None:
                    if situation_seed.host_sim_id not in [host_sim.id for host_sim in situation_host_sims]:
                        continue
                if self.situation_special_object_exists is not None:
                    if self.situation_special_object_exists:
                        if situation_seed.special_object_definition_id is None:
                            continue
                    else:
                        if situation_seed.special_object_definition_id is not None:
                            continue
            else:
                if not self.situation_type is not None:
                    if not situation_host_sims is not None:
                        if self.situation_special_object_exists is not None:
                            continue
            if receiver_sim is not None:
                if drama_node.get_receiver_sim_info is not receiver_sim:
                    continue
            if self.time_to_run is not None:
                time_to_node = drama_node.selected_time - now
                if not self.time_to_run.threshold.compare(time_to_node):
                    continue
                if self.time_to_run.additional_threshold is not None:
                    if not self.time_to_run.additional_threshold.compare(time_to_node):
                        continue
                    if self.exists:
                        return TestResult.TRUE
                    else:
                        return TestResult(False, 'Drama node meeting the requirements exists when we are asking for non-existence.', tooltip=(self.tooltip))

        if self.exists:
            return TestResult(False, 'No drama node exists meeting the requirements.',
              tooltip=(self.tooltip))
        return TestResult.TRUE


class DramaNodeBucketTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'buckets':TunableList(description='\n            List of drama node buckets to test against.\n            ',
       tunable=TunableEnumEntry(description='\n                Bucket to test against.\n                ',
       tunable_type=DramaNodeScoringBucket,
       default=(DramaNodeScoringBucket.DEFAULT)),
       unique_entries=True), 
     'use_only_scheduled':Tunable(description='\n            If checked, this test will only consider drama nodes that have been \n            scheduled by the drama scheduler service.\n            ',
       tunable_type=bool,
       default=True), 
     'run_visibility_tests':Tunable(description='\n            If checked, run the visibility tests on a drama node to decide \n            whether it would be shown. Otherwise, all drama nodes will be \n            available.\n            ',
       tunable_type=bool,
       default=True)}

    def get_expected_args(self):
        return {'participants': self.participant}

    @cached_test
    def __call__(self, participants):
        sim = next(iter(participants))
        if self.use_only_scheduled:
            drama_nodes = iter(services.drama_scheduler_service.all_nodes_gen)
        else:
            drama_node_manager = services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)
            drama_nodes = (drama_node() for drama_node in drama_node_manager.types.values)
        for drama_node in drama_nodes:
            if self.buckets:
                if not drama_node.scoring is None:
                    if drama_node.scoring.bucket not in self.buckets:
                        continue
            result = drama_node.create_picker_row(owner=sim, run_visibility_tests=(self.run_visibility_tests))
            if result is not None:
                return TestResult.TRUE

        return TestResult(False, 'No drama nodes available in the given buckets.', tooltip=(self.tooltip))