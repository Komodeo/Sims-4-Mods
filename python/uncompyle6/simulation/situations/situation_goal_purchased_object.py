# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_purchased_object.py
# Compiled at: 2020-07-15 13:36:24
# Size of source mod 2**32: 1514 bytes
from sims4.tuning.tunable_base import GroupNames
import event_testing.tests, objects.object_tests, services, sims4.tuning.instances, situations.situation_goal

class SituationGoalPurchasedObject(situations.situation_goal.SituationGoal):
    INSTANCE_TUNABLES = {'purchased_object_test': objects.object_tests.ObjectPurchasedTest.TunableFactory(tuning_group=(GroupNames.TESTS))}

    def setup(self):
        super().setup()
        services.get_event_manager().register(self, self.purchased_object_test.test_events)

    def _decommision(self):
        services.get_event_manager().unregister(self, self.purchased_object_test.test_events)
        super()._decommision()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not resolver(self.purchased_object_test):
            return False
        return super()._run_goal_completion_tests(sim_info, event, resolver)

    @property
    def numerical_token(self):
        return int(self.purchased_object_test.value)


sims4.tuning.instances.lock_instance_tunables(SituationGoalPurchasedObject, _iterations=1,
  _post_tests=(event_testing.tests.TestList()))