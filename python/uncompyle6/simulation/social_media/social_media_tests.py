# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\social_media\social_media_tests.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 1866 bytes
import services
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingleSim
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry

class NewSocialMediaPostTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject': TunableEnumEntry(description='\n            The subject who we are checking for new posts.\n            ',
                  tunable_type=ParticipantTypeSingleSim,
                  default=(ParticipantTypeSingleSim.Actor))}

    def get_expected_args(self):
        return {'subject': self.subject}

    def __call__(self, subject=None):
        social_media_service = services.get_social_media_service()
        if social_media_service is None:
            return TestResult(False, 'No social media service available.',
              tooltip=(self.tooltip))
        subject = next(iter(subject))
        if not (subject is None or subject).is_sim or subject.is_npc:
            return TestResult(False, 'Subject {} is not a sim.',
              subject,
              tooltip=(self.tooltip))
            if social_media_service.get_sim_has_new_posts(subject.sim_id) or social_media_service.get_sim_has_new_messages(subject.sim_id):
                return TestResult.TRUE
        return TestResult(False, 'Subject {} does not have new posts.',
          tooltip=(self.tooltip))