# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\base_situation_goal_tracker.py
# Compiled at: 2021-11-22 18:29:05
# Size of source mod 2**32: 3180 bytes
from distributor.shared_messages import build_icon_info_msg, IconInfoData
import uid

class BaseSituationGoalTracker:

    def __init__(self, situation):
        self._situation = situation
        self._has_offered_goals = False
        self._goal_id_generator = uid.UniqueIdGenerator(1)

    def destroy(self):
        self._situation = None

    def save_to_seed(self, situation_seed):
        raise NotImplementedError

    def load_from_seedling(self, tracker_seedling):
        raise NotImplementedError

    def autocomplete_goals_on_load(self, previous_zone_id):
        pass

    def has_offered_goals(self):
        return self._has_offered_goals

    def refresh_goals(self, completed_goal=None):
        new_goals_offered = self._offer_goals()
        if new_goals_offered or completed_goal is not None:
            self.send_goal_update_to_client(completed_goal=completed_goal)

    def _offer_goals(self):
        raise NotImplementedError

    def get_goal_info(self):
        raise NotImplementedError

    def get_completed_goal_info(self):
        raise NotImplementedError

    def send_goal_update_to_client(self, completed_goal=None, goal_preferences=None):
        raise NotImplementedError

    def all_goals_gen(self):
        raise NotImplementedError

    def on_add_sim_to_situation(self, sim, job_type):
        for goal in self.all_goals_gen():
            goal.on_add_sim_to_situation(sim, job_type)

    def on_remove_sim_from_situation(self, sim, job_type):
        for goal in self.all_goals_gen():
            goal.on_remove_sim_from_situation(sim, job_type)