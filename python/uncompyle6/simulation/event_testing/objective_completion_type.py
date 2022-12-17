# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\objective_completion_type.py
# Compiled at: 2020-07-07 17:33:58
# Size of source mod 2**32: 411 bytes
import enum

class ObjectiveCompletionType(enum.Int, export=False):
    OBJECTIVE_COMPLETE = 0
    MILESTONE_COMPLETE = 1