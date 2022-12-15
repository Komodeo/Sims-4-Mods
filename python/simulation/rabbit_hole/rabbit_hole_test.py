# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\rabbit_hole\rabbit_hole_test.py
# Compiled at: 2019-07-20 15:23:21
# Size of source mod 2**32: 1829 bytes
import services
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingle
from sims4.tuning.tunable import TunableEnumEntry, HasTunableSingletonFactory, AutoFactoryInit, Tunable

class RabbitHoleTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description="\n            The subject who's familiar tracker we are checking.\n            ",
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'negate':Tunable(description='\n            If checked then we will negate the results of this test.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subject': self.subject}

    def __call__(self, subject=None):
        rabbit_hole_service = services.get_rabbit_hole_service()
        for sim in subject:
            if rabbit_hole_service.is_in_rabbit_hole(sim.sim_id):
                if self.negate:
                    return TestResult(False, '{} is in a rabbit hole.',
                      sim,
                      tooltip=(self.tooltip))
            else:
                if not self.negate:
                    return TestResult(False, '{} is in a rabbit hole.',
                      sim,
                      tooltip=(self.tooltip))

        return TestResult.TRUE