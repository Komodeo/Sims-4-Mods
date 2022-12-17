# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\rewards\reward_enums.py
# Compiled at: 2019-04-22 16:22:37
# Size of source mod 2**32: 992 bytes
import enum

class RewardDestination(enum.Int):
    SIM = 0
    HOUSEHOLD = 1
    MAILBOX = 2


class RewardType(enum.Int, export=False):
    MONEY = 0
    OBJECT_DEFINITION = 1
    TRAIT = 2
    CAS_PART = 3
    BUILD_BUY_OBJECT = 4
    BUILD_BUY_MAGAZINE_COLLECTION = 5
    DISPLAY_TEXT = 6
    ADDITIONAL_EMPLOYEE_SLOT = 7
    ADDITIONAL_BUSINESS_CUSTOMER_COUNT = 8
    ADDITIONAL_BUSINESS_MARKUP = 9
    SET_CLUB_GATHERING_VIBE = 10
    BUCKS = 11
    BUFF = 12
    WHIM_BUCKS = 13