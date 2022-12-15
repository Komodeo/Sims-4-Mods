# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_zone_loaded.py
# Compiled at: 2015-02-26 15:07:38
# Size of source mod 2**32: 1449 bytes
from event_testing import test_events
import services
from sims4.tuning.tunable_base import GroupNames
from situations.situation_goal import SituationGoal
from situations.situation_goal_actor import TunableSituationGoalActorPostTestSet

class SituationGoalZoneLoaded(SituationGoal):
    INSTANCE_TUNABLES = {'_post_tests': TunableSituationGoalActorPostTestSet(description='\n                A set of tests that must all pass when zone has finished loading.\n                ',
                      tuning_group=(GroupNames.TESTS))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._test_events = set()

    def setup(self):
        super().setup()
        self._test_events.add(test_events.TestEvent.SimTravel)
        services.get_event_manager().register(self, self._test_events)

    def _decommision(self):
        services.get_event_manager().unregister(self, self._test_events)
        super()._decommision()