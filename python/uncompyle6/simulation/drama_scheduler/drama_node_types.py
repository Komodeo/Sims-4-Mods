# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\drama_node_types.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 653 bytes
import enum

class DramaNodeType(enum.Int, export=False):
    DEFAULT = ...
    SITUATION = ...
    DIALOG = ...
    CLUB = ...
    FESTIVAL = ...
    INTERACTION = ...
    HOLIDAY = ...
    PLAYER_PLANNED = ...
    TUTORIAL = ...
    AUDITION = ...
    PICKER = ...
    VENUE_EVENT = ...
    CALENDAR = ...