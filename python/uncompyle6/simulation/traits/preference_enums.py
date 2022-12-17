# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\preference_enums.py
# Compiled at: 2021-04-07 12:49:52
# Size of source mod 2**32: 638 bytes
from traits.trait_type import TraitType
import enum

class PreferenceTypes(enum.Int):
    LIKE = TraitType.LIKE
    DISLIKE = TraitType.DISLIKE


class PreferenceSubject(enum.Int):
    OBJECT = 0
    DECOR = 1