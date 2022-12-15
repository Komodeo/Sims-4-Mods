# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\lot_decoration_enums.py
# Compiled at: 2018-03-07 11:29:55
# Size of source mod 2**32: 566 bytes
import enum
from sims4.tuning.dynamic_enum import DynamicEnum

class DecorationLocation(enum.Int):
    FOUNDATIONS = 0
    EAVES = 1
    FRIEZES = 2
    FENCES = 3
    SPANDRELS = 4
    COLUMNS = 5


class DecorationPickerCategory(DynamicEnum):
    ALL = 0


LOT_DECORATION_DEFAULT_ID = 0