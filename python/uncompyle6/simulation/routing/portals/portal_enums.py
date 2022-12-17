# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_enums.py
# Compiled at: 2020-02-21 13:24:37
# Size of source mod 2**32: 1852 bytes
import enum
from animation import animation_constants

class PathSplitType(enum.Int, export=False):
    PathSplitType_DontSplit = 0
    PathSplitType_Split = 1
    PathSplitType_LadderSplit = 2


class PortalAlignment(enum.Int):
    PA_FRONT = 0
    PA_LEFT = 1
    PA_RIGHT = 2

    @staticmethod
    def get_asm_parameter_string(alignment):
        if alignment is PortalAlignment.PA_FRONT:
            return animation_constants.ASM_LADDER_PORTAL_ALIGNMENT_FRONT
        if alignment is PortalAlignment.PA_LEFT:
            return animation_constants.ASM_LADDER_PORTAL_ALIGNMENT_LEFT
        if alignment is PortalAlignment.PA_RIGHT:
            return animation_constants.ASM_LADDER_PORTAL_ALIGNMENT_RIGHT
        return

    @staticmethod
    def get_bit_flag(alignment):
        return 1 << alignment


class LadderType(enum.Int, export=False):
    LADDER_OCEAN = 0
    LADDER_BUILD = 1