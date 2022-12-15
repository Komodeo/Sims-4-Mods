# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fire\fire_tuning.py
# Compiled at: 2017-04-21 12:24:14
# Size of source mod 2**32: 551 bytes
from sims4.tuning.tunable import TunableEnumWithFilter
from tag import Tag

class FireTuning:
    FLAMMABLE_TAG = TunableEnumWithFilter(description='\n        Define a tag that is automatically added to all objects that are\n        flammable.\n        ',
      tunable_type=Tag,
      default=(Tag.INVALID),
      invalid_enums=(
     Tag.INVALID,),
      filter_prefixes=('Fire', ))