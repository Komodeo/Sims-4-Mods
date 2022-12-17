# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\acting\performance_object_data.py
# Compiled at: 2018-09-17 15:30:33
# Size of source mod 2**32: 2272 bytes
import services

class PerformanceObjectData:

    def __init__(self, objects, pre_performance_states, performance_states, post_performance_states):
        self._objects = objects
        self._pre_performance_states = pre_performance_states
        self._performance_states = performance_states
        self._post_performance_states = post_performance_states

    def set_performance_states(self):
        self._set_states(self._performance_states)

    def set_pre_performance_states(self):
        bucks_tracker = services.active_sim_info().get_bucks_tracker()
        for state_data in self._pre_performance_states:
            skip_perk = state_data.skip_with_perk
            state_value = state_data.state_value
            if skip_perk is not None:
                if bucks_tracker is not None:
                    if bucks_tracker.is_perk_unlocked(skip_perk):
                        continue
            for obj in self._objects:
                if obj.has_state(state_value.state):
                    obj.set_state((state_value.state), state_value, immediate=True, force_update=True)

    def set_post_performance_states(self):
        self._set_states(self._post_performance_states)

    def _set_states(self, states):
        for state_value in states:
            for obj in self._objects:
                if obj.has_state(state_value.state):
                    obj.set_state((state_value.state), state_value, immediate=True, force_update=True)