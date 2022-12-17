# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\priority.py
# Compiled at: 2017-07-28 15:37:42
# Size of source mod 2**32: 1404 bytes
import enum

class Priority(enum.Int):
    Low = 1
    High = 2
    Critical = 3


class PriorityExtended(Priority, export=False):
    SubLow = 0


def can_priority_displace(priority_new, priority_existing, allow_clobbering=False):
    if priority_new is None:
        return False
    if allow_clobbering:
        return priority_new >= priority_existing
    return priority_new > priority_existing


def can_displace(interaction_new, interaction_existing, allow_clobbering=False):
    if not can_priority_displace((interaction_new.priority), (interaction_existing.priority), allow_clobbering=allow_clobbering):
        return False
    return not interaction_existing.is_cancel_aop