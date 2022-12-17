# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\households\household_tests.py
# Compiled at: 2020-11-12 07:43:20
# Size of source mod 2**32: 1391 bytes
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory
import services

class PlayerPopulationTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        culling_service = services.get_culling_service()
        max_player_population = culling_service.get_max_player_population()
        if max_player_population:
            household_manager = services.household_manager()
            player_population = sum((len(household) for household in household_manager.values() if household.is_player_household))
            if player_population >= max_player_population:
                return TestResult(False, 'Over the maximum player population ({}/{})', player_population, max_player_population, tooltip=(lambda *_, **__: self.tooltip(player_population, max_player_population)))
        return TestResult.TRUE