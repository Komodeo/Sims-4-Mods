# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\venue_constants.py
# Compiled at: 2019-11-04 11:47:54
# Size of source mod 2**32: 1532 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableReference
import enum, services, sims4.resources

class ZoneDirectorRequestType(enum.Int, export=False):
    CAREER_EVENT = ...
    GO_DANCING = ...
    DRAMA_SCHEDULER = ...
    AMBIENT_SUB_VENUE = ...
    AMBIENT_VENUE = ...


class NPCSummoningPurpose(DynamicEnum):
    DEFAULT = 0
    PLAYER_BECOMES_GREETED = 1
    BRING_PLAYER_SIM_TO_LOT = 2
    ZONE_FIXUP = 3