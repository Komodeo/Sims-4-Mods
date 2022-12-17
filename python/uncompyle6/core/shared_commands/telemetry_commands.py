# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\shared_commands\telemetry_commands.py
# Compiled at: 2012-09-07 16:53:35
# Size of source mod 2**32: 2355 bytes
import sims4.commands, sims4.telemetry

@sims4.commands.Command('telemetry.add_filter')
def add_filter(priority: int, action: int, module_tag: str, group_tag: str, hook_tag: str, _connection=None, **kwargs):
    output = sims4.commands.Output(_connection)
    if module_tag == '*':
        module_tag = None
    if group_tag == '*':
        group_tag = None
    if hook_tag == '*':
        hook_tag = None
    filter_action = sims4.telemetry.RuleAction(action)
    fields = kwargs
    sims4.telemetry.add_filter_rule(priority, module_tag, group_tag, hook_tag, fields, filter_action)
    output('Filter added')


@sims4.commands.Command('telemetry.remove_filter')
def remove_filter(priority: int, action: int, module_tag: str, group_tag: str, hook_tag: str, _connection=None, **kwargs):
    output = sims4.commands.Output(_connection)
    if module_tag == '*':
        module_tag = None
    else:
        if group_tag == '*':
            group_tag = None
        if hook_tag == '*':
            hook_tag = None
        filter_action = sims4.telemetry.RuleAction(action)
        fields = kwargs
        result = sims4.telemetry.remove_filter_rule(priority, module_tag, group_tag, hook_tag, fields, filter_action)
        if result:
            output('Filter removed')
        else:
            output('No matching filter')


@sims4.commands.Command('telemetry.clear_filters')
def clear_filters(_connection=None):
    del sims4.telemetry._filters[:]


@sims4.commands.Command('telemetry.list_filters')
def list_filters(_connection=None):
    output = sims4.commands.Output(_connection)
    for priority, tags, fields, action in sims4.telemetry._filters:
        module_tag = group_tag = hook_tag = '*'
        if len(tags) > 0:
            module_tag = tags[0]
        if len(tags) > 1:
            group_tag = tags[1]
        if len(tags) > 2:
            hook_tag = tags[2]
        output('{:4} {:8} {:4} {:4} {:4} {}'.format(priority, action.name, module_tag, group_tag, hook_tag, fields))