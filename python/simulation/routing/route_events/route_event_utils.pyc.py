# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_utils.py
# Compiled at: 2018-01-25 12:11:29
# Size of source mod 2**32: 290 bytes
import enum

class RouteEventSchedulePreference(enum.Int):
    BEGINNING = 0
    END = 1
    RANDOM = 2