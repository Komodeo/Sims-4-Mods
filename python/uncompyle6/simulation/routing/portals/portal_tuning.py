# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_tuning.py
# Compiled at: 2022-06-13 15:18:17
# Size of source mod 2**32: 1894 bytes
from sims4.tuning.dynamic_enum import DynamicEnumFlags
from sims4.tuning.tunable import TunableRange
import enum

class PortalTuning:
    SURFACE_PORTAL_HEIGH_OFFSET = TunableRange(description='\n        A height offset on meters increase the height of the raycast test\n        to consider two connecting portals valid over an objects footprint.\n        For example this height is high enough so two portals on counters pass\n        a raycast test over a stove or a sink (low objects), but is not high\n        enough to pass over a microwave (which would cause our sims to clip\n        through the object when transitioning through the portal.\n        ',
      tunable_type=float,
      default=0.2,
      minimum=0)


class PortalFlags(DynamicEnumFlags):
    DEFAULT = 0
    REQUIRE_NO_CARRY = 1
    STAIRS_PORTAL_LONG = 2
    STAIRS_PORTAL_SHORT = 4
    SPECIES_HUMAN = 8
    SPECIES_DOG = 16
    SPECIES_CAT = 32
    SPECIES_SMALLDOG = 64
    AGE_TODDLER = 128
    AGE_CHILD = 256
    AGE_TYAE = 512
    CLEARANCE_HIGH = 1024
    CLEARANCE_MEDIUM = 2048
    CLEARANCE_LOW = 4096
    SPECIES_FOX = 8192


class PortalType(enum.Int, export=False):
    PortalType_Wormhole = 0
    PortalType_Walk = 1
    PortalType_Animate = 2