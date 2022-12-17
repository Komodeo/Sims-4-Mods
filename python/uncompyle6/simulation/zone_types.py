# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\zone_types.py
# Compiled at: 2021-06-14 13:41:53
# Size of source mod 2**32: 957 bytes
import enum

class ZoneState(enum.Int, export=False):
    ZONE_INIT = 0
    OBJECTS_LOADED = 1
    CLIENT_CONNECTED = 2
    HOUSEHOLDS_AND_SIM_INFOS_LOADED = 3
    ALL_SIMS_SPAWNED = 4
    HITTING_THEIR_MARKS = 5
    RUNNING = 6
    SHUTDOWN_STARTED = 7