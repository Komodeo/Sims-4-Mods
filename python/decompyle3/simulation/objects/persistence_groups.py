# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\persistence_groups.py
# Compiled at: 2014-03-03 16:40:53
# Size of source mod 2**32: 350 bytes
import enum

class PersistenceGroups(enum.Int, export=False):
    NONE = 0
    OBJECT = 1
    SIM = 2
    IN_OPEN_STREET = 3