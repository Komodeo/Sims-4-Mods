# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\whims\whim_tests.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 2750 bytes
import services, sims4
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantType
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry, TunableSet, TunableReference, Tunable
logger = sims4.log.Logger('WhimTests')

class WhimTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'who':TunableEnumEntry(description='\n            The sim(s) to test.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'whims':TunableSet(description='\n            If any of the whims in this list are active on the sim(s), then the test\n            will pass.\n            ',
       tunable=TunableReference(description='\n                A whim, that if active, will cause the test to return True.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.WHIM)),
       pack_safe=True),
       minlength=1), 
     'invert':Tunable(description='\n            If true, will take the output of the test and invert it.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'test_targets': self.who}

    def __call__(self, test_targets=()):
        test_result = TestResult.TRUE
        if len(self.whims) > 0:
            for target in test_targets:
                tracker = target.whim_tracker
                if tracker is None:
                    test_result = TestResult(False, 'Target {} did not have a whim tracker.', target)
                    break
                for whim in self.whims:
                    if tracker.is_whim_active(whim):
                        break
                else:
                    test_result = TestResult(False, 'Target {} did not have any of the supplied whims active.', target)
                    break

        else:
            test_result = TestResult(False, 'Either no whims were added to the test or they were all from packs that are not present.')
        if self.invert:
            if test_result:
                test_result = TestResult(False, 'Initial test result passed, but test is inverted.')
            else:
                test_result = TestResult.TRUE
        return test_result