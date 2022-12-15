# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\household_milestones\household_milestone_tracker.py
# Compiled at: 2020-07-27 12:08:26
# Size of source mod 2**32: 2098 bytes
from event_testing import test_events
from event_testing.event_data_tracker import EventDataTracker
from event_testing.resolver import SingleSimResolver
import services, sims4.resources

class HouseholdMilestoneTracker(EventDataTracker):

    def _get_milestone_manager(self):
        return services.get_instance_manager(sims4.resources.Types.HOUSEHOLD_MILESTONE)

    @property
    def simless(self):
        return True

    @property
    def owner_sim_info(self):
        client = services.client_manager().get_first_client()
        if client is not None:
            return client.active_sim_info

    def post_to_gsi(self, message):
        pass

    def send_if_dirty(self):
        pass

    def update_objective(self, objective, current_value, objective_value, is_money, show_progress, from_init=False):
        pass

    def complete_milestone(self, milestone, sim_info):
        super().complete_milestone(milestone, sim_info)
        if milestone.notification is not None:
            dialog = milestone.notification(sim_info, SingleSimResolver(sim_info))
            dialog.show_dialog()
        services.get_event_manager().process_event((test_events.TestEvent.UnlockEvent), sim_info=sim_info, unlocked=milestone)