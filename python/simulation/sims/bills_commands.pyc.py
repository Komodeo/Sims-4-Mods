# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\bills_commands.py
# Compiled at: 2020-02-05 21:13:37
# Size of source mod 2**32: 1745 bytes
import services
from sims.bills_enums import UtilityEndOfBillAction
from sims.household_utilities.utility_types import Utilities
from sims4.commands import CommandType, Command, output

@Command('bills.sell_excess_utility', command_type=(CommandType.Live))
def sell_excess_utility(utility: Utilities, _connection=None):
    active_household = services.active_household()
    if active_household is None:
        output('Attempting to sell excess utilities when there is no active household.', _connection)
        return
    active_household.bills_manager.sell_excess_utility(utility)


@Command('bills.set_utility_end_bill_action', command_type=(CommandType.Live))
def set_utility_end_bill_action(utility: Utilities, utility_action: UtilityEndOfBillAction, _connection=None):
    active_household = services.active_household()
    if active_household is None:
        output('Attempting to sell excess utilities when there is no active household.', _connection)
        return
    active_household.bills_manager.set_utility_end_bill_action(utility, utility_action)


@Command('bills.show_bills_dialog', command_type=(CommandType.Live))
def show_bills_dialog(_connection=None):
    active_household = services.active_household()
    if active_household is None:
        output('Attempting to show bills dialog when there is no active household.', _connection)
        return
    active_household.bills_manager.show_bills_dialog()