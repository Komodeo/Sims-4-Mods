# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\drama_enums.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 2721 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum, sims4.log
logger = sims4.log.Logger('Drama Node Enums')

class DramaNodeRunOutcome(enum.Int, export=False):
    FAILURE = ...
    RESCHEDULED = ...
    SUCCESS_NODE_COMPLETE = ...
    SUCCESS_NODE_INCOMPLETE = ...


class DramaNodeUiDisplayType(enum.Int):
    NO_UI = 0
    EVENT = 1
    POP_UP_HOLIDAY = 2
    HOLIDAY = 3
    ALERTS_ONLY = 4
    VACATION = 5
    FESTIVAL = 6
    WEDDING = 7
    WORK_EVENT = 8


class DramaNodeScoringBucket(DynamicEnum):
    DEFAULT = 0


class WeeklySchedulingGroup(DynamicEnum):
    DEFAULT = 0


class DramaNodeParticipantOption(enum.Int):
    DRAMA_PARTICIPANT_OPTION_NONE = ...
    DRAMA_PARTICIPANT_OPTION_PARTICIPANT_TYPE = ...
    DRAMA_PARTICIPANT_OPTION_FILTER = ...


class TimeSelectionOption(enum.Int):
    SCHEDULE = ...
    SINGLE_TIME = ...


class CooldownOption(enum.Int):
    ON_RUN = 0
    ON_DIALOG_RESPONSE = 1
    ON_SCHEDULE = 2


class CooldownGroup(DynamicEnum):
    INVALID = 0


class SenderSimInfoType(enum.Int):
    UNINSTANCED_ONLY = 0
    INSTANCED_ALLOWED = 1