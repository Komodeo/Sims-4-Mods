# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_mixins.py
# Compiled at: 2019-03-18 12:20:10
# Size of source mod 2**32: 3046 bytes
from event_testing.results import TestResult
from sims4.math import MAX_INT32

class RouteEventBase:

    def __init__(self, time=None, *args, **kwargs):
        self.time = time
        self.event_data = None
        self._run_duration = MAX_INT32

    @property
    def duration(self):
        return self._run_duration

    def copy_from(self, other):
        self.time = other.time
        self.event_data = other.event_data
        self._run_duration = other.duration


class RouteEventDataBase:

    @classmethod
    def test(cls, actor, event_data_tuning):
        return TestResult.TRUE

    def prepare(self, actor):
        raise NotImplementedError

    def is_valid_for_scheduling(self, actor, path):
        return True

    def should_remove_on_execute(self):
        return True

    def execute(self, actor, **kwargs):
        raise NotImplementedError

    def process(self, actor):
        raise NotImplementedError