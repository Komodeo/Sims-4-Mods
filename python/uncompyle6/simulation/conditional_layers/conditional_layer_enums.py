# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\conditional_layers\conditional_layer_enums.py
# Compiled at: 2021-05-21 16:15:16
# Size of source mod 2**32: 514 bytes
import enum

class ConditionalLayerRequestSpeedType(enum.Int, export=False):
    GRADUALLY = ...
    IMMEDIATELY = ...


class ConditionalLayerRequestType(enum.Int, export=False):
    LOAD_LAYER = ...
    DESTROY_LAYER = ...