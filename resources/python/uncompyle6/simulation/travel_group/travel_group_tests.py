# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\travel_group\travel_group_tests.py
# Compiled at: 2020-11-12 07:43:22
# Size of source mod 2**32: 8657 bytes
import sims4.math
from event_testing.test_base import BaseTest
from event_testing.results import TestResult
from caches import cached_test
from interactions import ParticipantType
from sims4.tuning.tunable import HasTunableSingletonFactory, TunableEnumEntry, AutoFactoryInit, Tunable, TunableVariant, TunableThreshold, TunableRange
from singletons import EMPTY_SET

class _TravelGroupTestVariantBase(HasTunableSingletonFactory, AutoFactoryInit):

    @property
    def additional_expected_args(self):
        return EMPTY_SET

    @property
    def requires_existing_travel_group(self):
        return True

    def _test_travel_group(self, participant, travel_group, tooltip, **kwargs):
        raise NotImplementedError


class _TravelGroupExists(_TravelGroupTestVariantBase):
    FACTORY_TUNABLES = {'exists': Tunable(description='\n            If checked, this test will fail if the Sim is not in a\n            travel group. If unchecked, this test will fail if the Sim\n            is in a travel group.\n            ',
                 tunable_type=bool,
                 default=True)}

    @property
    def requires_existing_travel_group(self):
        return self.exists

    def _test_travel_group--- This code section failed: ---

 L.  65         0  LOAD_FAST                'travel_group'
                2  LOAD_CONST               None
                4  COMPARE_OP               is
                6  POP_JUMP_IF_FALSE    14  'to 14'
                8  LOAD_FAST                'self'
               10  LOAD_ATTR                exists
               12  POP_JUMP_IF_TRUE     28  'to 28'
             14_0  COME_FROM             6  '6'

 L.  66        14  LOAD_FAST                'travel_group'
               16  LOAD_CONST               None
               18  COMPARE_OP               is-not
               20  POP_JUMP_IF_FALSE    44  'to 44'
               22  LOAD_FAST                'self'
               24  LOAD_ATTR                exists
               26  POP_JUMP_IF_TRUE     44  'to 44'
             28_0  COME_FROM            12  '12'

 L.  67        28  LOAD_GLOBAL              TestResult
               30  LOAD_CONST               False
               32  LOAD_STR                 'Participant {} is not in a travel group as expected.'
               34  LOAD_FAST                'participant'
               36  LOAD_FAST                'tooltip'
               38  LOAD_CONST               ('tooltip',)
               40  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
               42  RETURN_VALUE     
             44_0  COME_FROM            26  '26'
             44_1  COME_FROM            20  '20'

 L.  68        44  LOAD_GLOBAL              TestResult
               46  LOAD_ATTR                TRUE
               48  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 48


class _TravelGroupAddParticipant(_TravelGroupTestVariantBase):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant to be added.\n            ',
                      tunable_type=ParticipantType,
                      default=(ParticipantType.TargetSim))}

    @property
    def additional_expected_args(self):
        return {'targets': self.participant}

    def _test_travel_group(self, participant, travel_group, tooltip, targets=(), **kwargs):
        if not targets or any((not t.is_sim or not travel_group.can_add_to_travel_group(t) for t in targets)):
            return TestResult(False, 'Target cannot be added to travel group {}', travel_group, tooltip=tooltip)
        return TestResult.TRUE


class _TravelGroupFreeSlots(_TravelGroupTestVariantBase):
    FACTORY_TUNABLES = {'count': TunableThreshold(description='\n            The number of required free slots for the specified\n            travel group.\n            ',
                value=TunableRange(description='\n                The range of required free slots.\n                ',
                tunable_type=int,
                minimum=0,
                default=1),
                default=(sims4.math.Threshold(1, sims4.math.Operator.GREATER_OR_EQUAL.function)))}

    def _test_travel_group(self, participant, travel_group, tooltip, **kwargs):
        free_slot_count = travel_group.free_slot_count
        if not self.count.compare(free_slot_count):
            return TestResult(False, "Travel Group doesn't meet free slot count requirement.", tooltip=tooltip)
        return TestResult.TRUE


class _TravelGroupCanExtendStay(_TravelGroupTestVariantBase):

    def _test_travel_group(self, participant, travel_group, tooltip, **kwargs):
        if travel_group.end_timestamp is None:
            return TestResult(False, 'Travel group {} has no end time set and cannot be extended', travel_group, tooltip=tooltip)
        return TestResult.TRUE


class TravelGroupTest(BaseTest, HasTunableSingletonFactory):
    test_events = ()
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The subject whose travel group is the object of this test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'include_household_travel_group':Tunable(description="\n            If checked, the travel group that any sims in the participant's\n            household will be used in the event that the participant is not\n            actually on vacation.\n            ",
       tunable_type=bool,
       default=False), 
     'test_type':TunableVariant(description="\n            The type of test to determine what about this travel group's size\n            we care about.\n            ",
       in_travel_group=_TravelGroupExists.TunableFactory(description='\n                Use this option when testing to see if the participant exists\n                in the travel group or not.\n                '),
       participant=_TravelGroupAddParticipant.TunableFactory(description="\n                Use this option when you're testing a specific Sim being added\n                to the travel group.\n                "),
       count=_TravelGroupFreeSlots.TunableFactory(description="\n                Use this option when you're testing for a specific number of\n                free slots in the travel group.\n                "),
       can_extend=_TravelGroupCanExtendStay.TunableFactory(description='\n                Use this option to check whether or not a participant can\n                extend their vacation. This test will fail if the participant is\n                not in a travel group or their travel group does not have\n                an end time specified.\n                '),
       default='count')}

    def __init__(self, participant, test_type, include_household_travel_group, **kwargs):
        (super().__init__)(**kwargs)
        self.participant = participant
        self.include_household_travel_group = include_household_travel_group
        self.test_type = test_type
        self._expected_args = {'participants': self.participant}
        if test_type.additional_expected_args:
            self._expected_args.update(test_type.additional_expected_args)

    def get_expected_args(self):
        return self._expected_args

    @cached_test
    def __call__(self, participants=(), targets=()):
        for participant in participants:
            if not participant.is_sim:
                return TestResult(False, 'Participant {} is not a sim.', participant, tooltip=(self.tooltip))
                travel_group = participant.travel_group
                if travel_group is None:
                    if self.include_household_travel_group:
                        travel_group = participant.household.get_travel_group()
                if travel_group is None:
                    if self.test_type.requires_existing_travel_group:
                        return TestResult(False, 'Participant {} is not in a travel group.', participant, tooltip=(self.tooltip))
                test_result = self.test_type._test_travel_group(participant, travel_group, (self.tooltip), targets=targets)
                return test_result or test_result

        return TestResult.TRUE