# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\social_media\__init__.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 923 bytes
import enum

class SocialMediaNarrative(enum.Int):
    FRIENDLY = 0
    FLIRTY = 1
    MEAN = 2
    PROUD = 3
    EMBARRASSED = 4
    EXCITED = 5
    HAPPY = 6
    SAD = 7
    STRESSED = 8
    FUNNY = 9
    UNCOMFORTABLE = 10
    PRANK = 11


class SocialMediaPostType(enum.Int):
    DEFAULT = 0
    DIRECT_MESSAGE = 1
    FRIEND_REQUEST = 2
    FOLLOWERS_UPDATE = 3
    PUBLIC_POST = 4


class SocialMediaPolarity(enum.Int):
    POSITIVE = 0
    NEGATIVE = 1