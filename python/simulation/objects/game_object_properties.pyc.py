# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\game_object_properties.py
# Compiled at: 2018-11-29 13:12:01
# Size of source mod 2**32: 858 bytes
from sims4.tuning.tunable import TunableEnumEntry
from tag import Tag
import enum

class GameObjectProperty(enum.Int):
    CATALOG_PRICE = 0
    MODIFIED_PRICE = 1
    RARITY = 2
    GENRE = 3
    FISH_FRESHNESS = 4
    RECIPE_NAME = 5
    RECIPE_DESCRIPTION = 6
    OBJ_TYPE_REL_ID = 7


class GameObjectTuning:
    WALL_OBJ_LOS_TUNING_FLAG = TunableEnumEntry(description='\n        Tag that lets us know if this wall object needs a LOS test. \n        Currently it only works on wall grounded objects, but we can add y \n        position test later down the road. \n        ',
      tunable_type=Tag,
      default=(Tag.INVALID))