# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\environment_score_commands.py
# Compiled at: 2014-06-05 11:17:21
# Size of source mod 2**32: 781 bytes
import sims4.commands
from broadcasters.environment_score import environment_score_mixin

@sims4.commands.Command('environment_score.enable')
def environment_score_enable(_connection=None):
    environment_score_mixin.environment_score_enabled = True


@sims4.commands.Command('environment_score.disable')
def environment_score_disable(_connection=None):
    environment_score_mixin.environment_score_enabled = False