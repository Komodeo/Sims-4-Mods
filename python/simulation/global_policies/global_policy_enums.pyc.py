# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_policies\global_policy_enums.py
# Compiled at: 2019-01-16 17:35:04
# Size of source mod 2**32: 440 bytes
import enum

class GlobalPolicyProgressEnum(enum.Int):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    COMPLETE = 2


class GlobalPolicyTokenType(enum.Int):
    NAME = 0
    PROGRESS = 1