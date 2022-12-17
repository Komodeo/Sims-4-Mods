# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\spawner_component_enums.py
# Compiled at: 2020-08-11 09:25:53
# Size of source mod 2**32: 333 bytes
import enum

class SpawnerType(enum.Int):
    GROUND = 0
    SLOT = 1
    INTERACTION = 2


class SpawnLocation(enum.Int):
    SPAWNER = 0
    PORTAL = 1