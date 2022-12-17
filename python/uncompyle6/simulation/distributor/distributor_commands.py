# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\distributor\distributor_commands.py
# Compiled at: 2018-04-23 14:37:24
# Size of source mod 2**32: 2323 bytes
from protocolbuffers import DistributorOps_pb2
from gsi_handlers import distributor_handlers
import sims4.commands

def lookup_op_enum(op_type_name):
    descriptor = DistributorOps_pb2.Operation.DESCRIPTOR.enum_values_by_name.get(op_type_name)
    if descriptor is not None:
        return descriptor.number


@sims4.commands.Command('distributor.gsi.toggle_op_details')
def gsi_distributor_toggle_op_details(_connection=None):
    output = sims4.commands.Output(_connection)
    distributor_handlers.LOG_OP_DETAILS = not distributor_handlers.LOG_OP_DETAILS
    output('Op details are {}'.format('enabled' if distributor_handlers.LOG_OP_DETAILS else 'disabled'))


@sims4.commands.Command('distributor.gsi.hide_op')
def gsi_distributor_hide_op(op_type: str, _connection=None):
    output = sims4.commands.Output(_connection)
    op_number = lookup_op_enum(op_type)
    if op_number is not None:
        distributor_handlers.EXCLUDE_OP_TYPES.add(op_number)
        output('Logging disabled for Op {} ({})'.format(op_type, op_number))
    else:
        output('Could not find Op {}'.format(op_type))


@sims4.commands.Command('distributor.gsi.show_op')
def gsi_distributor_show_op(op_type: str, _connection=None):
    output = sims4.commands.Output(_connection)
    op_number = lookup_op_enum(op_type)
    if op_number is not None:
        distributor_handlers.EXCLUDE_OP_TYPES.discard(op_number)
        output('Logging enabled for Op {} ({})'.format(op_type, op_number))
    else:
        output('Could not find Op {}'.format(op_type))


@sims4.commands.Command('distributor.gsi.show_all_ops')
def gsi_distributor_show_all_ops(_connection=None):
    output = sims4.commands.Output(_connection)
    distributor_handlers.EXCLUDE_OP_TYPES.clear()
    output('Logging for all Op types is enabled')