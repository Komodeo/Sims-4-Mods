# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\bills_enums.py
# Compiled at: 2020-01-14 14:00:10
# Size of source mod 2**32: 664 bytes
import enum
from sims4.tuning.dynamic_enum import DynamicEnum

class AdditionalBillSource(DynamicEnum):
    Miscellaneous = 0


class UtilityEndOfBillAction(enum.Int, export=False):
    SELL = 0
    STORE = 1