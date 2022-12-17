# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\business\business_enums.py
# Compiled at: 2017-04-26 18:36:51
# Size of source mod 2**32: 1959 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class BusinessType(enum.Int):
    INVALID = 0
    RETAIL = 1
    RESTAURANT = 2
    VET = 3


class BusinessEmployeeType(DynamicEnum):
    INVALID = 0


class BusinessCustomerStarRatingBuffBuckets(DynamicEnum):
    INVALID = 0


class BusinessAdvertisingType(DynamicEnum):
    INVALID = 0


class BusinessQualityType(DynamicEnum):
    INVALID = 0