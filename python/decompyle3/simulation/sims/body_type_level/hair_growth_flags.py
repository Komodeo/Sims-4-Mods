# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\body_type_level\hair_growth_flags.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 922 bytes
import enum
from sims.outfits.outfit_enums import BodyType

class HairGrowthFlags(enum.IntFlags, export=False):
    NONE = 0
    FACIAL_HAIR = 256
    ARM_HAIR = 512
    LEG_HAIR = 1024
    TORSOFRONT_HAIR = 2048
    TORSOBACK_HAIR = 4096
    ALL = FACIAL_HAIR | ARM_HAIR | LEG_HAIR | TORSOFRONT_HAIR | TORSOBACK_HAIR


HAIR_GROWTH_TO_BODY_TYPE = {HairGrowthFlags.NONE: BodyType.NONE, 
 HairGrowthFlags.FACIAL_HAIR: BodyType.FACIAL_HAIR, 
 HairGrowthFlags.ARM_HAIR: BodyType.BODYHAIR_ARM, 
 HairGrowthFlags.LEG_HAIR: BodyType.BODYHAIR_LEG, 
 HairGrowthFlags.TORSOFRONT_HAIR: BodyType.BODYHAIR_TORSOFRONT, 
 HairGrowthFlags.TORSOBACK_HAIR: BodyType.BODYHAIR_TORSOBACK}