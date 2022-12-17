# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\automation\automation_utils.py
# Compiled at: 2017-05-26 14:30:18
# Size of source mod 2**32: 858 bytes
from sims4.commands import automation_output
import services, sims4.reload
with sims4.reload.protected(globals()):
    dispatch_automation_events = False

def automation_event(message, **msg_data):
    if not dispatch_automation_events:
        return
    connection = services.client_manager().get_first_client_id()
    if msg_data:
        data_str = ['{}: {}'.format(k, v) for k, v in msg_data.items()]
        data_str = ', '.join(data_str)
        automation_output('{0}; {1}'.format(message, data_str), connection)
    else:
        automation_output('{0};'.format(message), connection)