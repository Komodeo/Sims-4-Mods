# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sickness\sickness_enums.py
# Compiled at: 2017-03-20 10:43:00
# Size of source mod 2**32: 874 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class SicknessDiagnosticActionType(enum.Int):
    EXAM = 0
    TREATMENT = 1


class DiagnosticActionResultType(DynamicEnum):
    DEFAULT = 0
    CORRECT_TREATMENT = 1
    INCORRECT_TREATMENT = 2
    FAILED_TOO_STRESSED = 3