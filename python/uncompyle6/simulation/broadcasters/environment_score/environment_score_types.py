# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\broadcasters\environment_score\environment_score_types.py
# Compiled at: 2014-06-11 16:40:18
# Size of source mod 2**32: 335 bytes
import enum

class EnvironmentScoreType(enum.Int):
    MOOD_SCORING = 1
    NEGATIVE_SCORING = 2
    POSITIVE_SCORING = 3