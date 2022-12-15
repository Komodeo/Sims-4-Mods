# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_type.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 872 bytes
import enum

class TraitType(enum.Int):
    PERSONALITY = 0
    GAMEPLAY = 1
    WALKSTYLE = 2
    HIDDEN = 4
    GHOST = 5
    ASPIRATION = 6
    TAILSTYLE = 7
    GENDER_OPTIONS = 8
    SIM_PHONE = 9
    PHASE = 10
    AGENT = 11
    INFECTION = 12
    CURSE = 13
    ROOMMATE = 14
    ROBOT_MODULE = 15
    ROBOT = 16
    PROFESSOR = 17
    UNIVERSITY_DEGREE = 18
    ROBOT_MODULE_LOCKED = 19
    BATUU_ALIEN = 20
    LIFESTYLE = 21
    LIKE = 22
    DISLIKE = 23
    FOOD_RESTRICTION = 24
    TRADITION = 25
    TEMPERAMENT = 26
    PACK_MEMBER = 27
    PACK_FRIEND = 28
    FEAR = 29
    HIGH_SCHOOL = 30