# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\organizations\organization_commands.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 2011 bytes
from distributor.ops import AskAboutClubsDialog
from distributor.system import Distributor
from drama_scheduler.drama_node_types import DramaNodeType
from organizations.organization_enums import OrganizationStatusEnum
from server_commands.argument_helpers import TunableInstanceParam, RequiredTargetParam
from sims4.commands import CommandType
import services, sims4
logger = sims4.log.Logger('OrganizationCommands', default_owner='shipark')

@sims4.commands.Command('ui.leave_organization', command_type=(sims4.commands.CommandType.Live))
def ui_leave_organization(org_id: int, _connection=None):
    active_sim = services.get_active_sim()
    if active_sim is None:
        logger.error('Active Sim is None and cannot be.')
        return False
    org_tracker = active_sim.sim_info.organization_tracker
    if org_tracker is None:
        logger.error("({})'s organization tracker is None and cannot be.", active_sim.full_name)
        return False
    org_tracker.leave_organization(org_id)
    return org_tracker.get_organization_status(org_id) != OrganizationStatusEnum.ACTIVE


@sims4.commands.Command('orgs.show_orgs_events_dialog', command_type=(CommandType.Live))
def show_orgs_events_dialog(sim: RequiredTargetParam, _connection=None):
    sim_info = sim.get_target(manager=(services.sim_info_manager()))
    if sim_info is None:
        sims4.commands.output('Sim with id {} is not found to show organizations events dialog.'.format(sim.target_id), _connection)
        return False
    op = AskAboutClubsDialog((sim_info.id), show_orgs=True)
    Distributor.instance().add_op_with_no_owner(op)