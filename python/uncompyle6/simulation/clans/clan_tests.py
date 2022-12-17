# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clans\clan_tests.py
# Compiled at: 2022-06-13 15:18:17
# Size of source mod 2**32: 1839 bytes
import services, sims4.resources
from event_testing.test_base import BaseTest
from event_testing.results import TestResult
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunablePackSafeReference, Tunable
from singletons import EMPTY_SET

class HasClanLeaderTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'clan':TunablePackSafeReference(description='\n            The clan to test against and check if a leader exists.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CLAN)), 
     'invert':Tunable(description='\n            If checked, this test will pass if a clan does not have a leader.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {}

    def __call__(self):
        clan_service = services.clan_service()
        if clan_service is None:
            return TestResult(False, 'Unable to determine clan leader, clan service is None.')
            if self.clan is None:
                return TestResult(False, 'Unable to determine clan leader, clan reference is None.')
            has_clan_leader = clan_service.has_clan_leader(self.clan)
            if self.invert:
                if has_clan_leader:
                    return TestResult(False, 'Clan {} has a clan leader, but the test is inverted.', self.clan)
        elif not has_clan_leader:
            return TestResult(False, 'Clan {} does not have a clan leader.', self.clan)
        return TestResult.TRUE