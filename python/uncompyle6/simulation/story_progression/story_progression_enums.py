# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_enums.py
# Compiled at: 2022-03-10 17:35:10
# Size of source mod 2**32: 916 bytes
import enum
from collections import namedtuple
CullImmunityInfo = namedtuple('CullImmunityInfo', ('telemetry_hook', 'gsi_reason'))

class CullingReasons:
    PLAYER = CullImmunityInfo('imsp', 'Player SimInfo')
    LIVES_IN_WORLD = CullImmunityInfo('imsw', 'Resident of some world')
    TRAIT_IMMUNE = CullImmunityInfo('imsa', 'Possess an immune trait')
    INSTANCED = CullImmunityInfo('imsn', 'Instanced in the game')
    IN_TRAVEL_GROUP = CullImmunityInfo('imst', 'Part of some travel group')
    ALL_CULLING_REASONS = [
     PLAYER, LIVES_IN_WORLD, TRAIT_IMMUNE, INSTANCED, IN_TRAVEL_GROUP]


class StoryType(enum.Int, export=False):
    SIM_BASED = ...
    HOUSEHOLD_BASED = ...