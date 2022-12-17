# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\club_enums.py
# Compiled at: 2015-10-21 16:16:44
# Size of source mod 2**32: 2117 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class ClubRuleEncouragementStatus(enum.Int):
    ENCOURAGED = 0
    DISCOURAGED = 1
    NO_EFFECT = 2


class ClubHangoutSetting(enum.Int, export=False):
    HANGOUT_NONE = 0
    HANGOUT_VENUE = 1
    HANGOUT_LOT = 2


class ClubGatheringKeys:
    ASSOCIATED_CLUB_ID = 'associated_club_id'
    DISBAND_TICKS = 'disband_ticks'
    GATHERING_BUFF = 'gathering_buff'
    GATHERING_VIBE = 'gathering_vibe'
    START_SOURCE = 'start_source'
    HOUSEHOLD_ID_OVERRIDE = 'household_id_override'


class ClubGatheringStartSource(enum.Int, export=False):
    DEFAULT = 0
    APPLY_FOR_INVITE = 1


class ClubOutfitSetting(enum.Int):
    NO_OUTFIT = 0
    STYLE = 1
    COLOR = 2
    OVERRIDE = 3


class ClubGatheringVibe(DynamicEnum):
    NO_VIBE = 0