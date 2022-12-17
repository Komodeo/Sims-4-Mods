# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\base\interaction_constants.py
# Compiled at: 2019-02-05 11:05:58
# Size of source mod 2**32: 327 bytes
import enum

class InteractionQueuePreparationStatus(enum.Int, export=False):
    FAILURE = 0
    SUCCESS = 1
    NEEDS_DERAIL = 2
    PUSHED_REPLACEMENT = 3