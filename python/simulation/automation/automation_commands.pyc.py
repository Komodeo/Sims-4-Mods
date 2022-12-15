# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\automation\automation_commands.py
# Compiled at: 2017-05-26 14:30:18
# Size of source mod 2**32: 651 bytes
from automation import automation_utils
import sims4.commands

@sims4.commands.Command('qa.automation.enable_events', command_type=(sims4.commands.CommandType.Automation))
def automation_events(enabled: bool=True, _connection=None):
    automation_utils.dispatch_automation_events = enabled