# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\food_restrictions_utils.py
# Compiled at: 2021-02-22 09:43:26
# Size of source mod 2**32: 576 bytes
import services, sims4
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableReference, TunableEnumEntry, TunableMapping
logger = sims4.log.Logger('Food Restrictions')

class FoodRestrictionUtils:

    class FoodRestrictionEnum(DynamicEnum):
        INVALID = 0