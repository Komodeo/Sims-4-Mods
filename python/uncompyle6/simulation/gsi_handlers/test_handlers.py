# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\test_handlers.py
# Compiled at: 2017-08-08 12:40:45
# Size of source mod 2**32: 3896 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from interactions import ParticipantType
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import sims4.log
logger = sims4.log.Logger('GSI Test Handlers')