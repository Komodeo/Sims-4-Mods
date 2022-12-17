# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\native\performance\counters.py
# Compiled at: 2014-12-15 16:27:05
# Size of source mod 2**32: 965 bytes
try:
    from _perf_api import set_counter
except:

    def set_counter(name: str, value: int):
        pass


try:
    from _perf_api import add_counter
except:

    def add_counter(name: str, value: int):
        pass


try:
    from _perf_api import subtract_counter
except:

    def subtract_counter(name: str, value: int):
        pass


class CounterIDs:
    AUTONOMY_QUEUE_LENGTH = 'autonomyQueueLength64'
    AUTONOMY_QUEUE_TIME = 'autonomyQueueTime64'
    EVENT_TIME_DEVIATION = 'eventTimeDeviation64'
    NUM_PENDING_EVENTS = 'numPendingEvents64'
    NUM_PRIMITIVES = 'numPrimitives64'