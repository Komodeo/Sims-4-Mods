# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\organizations\organization_enums.py
# Compiled at: 2019-06-25 11:16:07
# Size of source mod 2**32: 524 bytes
from sims4.tuning.dynamic_enum import DynamicEnumLocked

class OrganizationStatusEnum(DynamicEnumLocked):
    ACTIVE = 0
    INACTIVE = 1
    NONMEMBER = 2


class OrganizationMembershipActionEnum(DynamicEnumLocked):
    JOIN = 0
    LEAVE = 1
    UPDATE = 2