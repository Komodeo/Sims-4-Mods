# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\civic_policies\venue_civic_policy_commands.py
# Compiled at: 2020-10-02 09:44:04
# Size of source mod 2**32: 6364 bytes
import sims4
from civic_policies.base_civic_policy_utilities import CivicPolicyProviderListSelector, debug_automation_output_policy_name_list, debug_automation_output_vote_info
from distributor.ops import CommunityBoardDialog
from distributor.system import Distributor
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target, TunableInstanceParam
from sims4.common import Pack
import services

@sims4.commands.Command('civic_policy.venue.enact', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def venue_civic_policy_enact(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), _connection=None):
    source_venue = services.venue_service().source_venue
    if source_venue is None or not source_venue.civic_policy_provider is None or source_venue.civic_policy_provider.enact(policy):
        sims4.commands.automation_output('Status; Result:Failed', _connection)
        sims4.commands.cheat_output('{} not enacted'.format(policy), _connection)
    else:
        sims4.commands.automation_output('Status; Result:Success', _connection)


@sims4.commands.Command('civic_policy.venue.repeal', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def venue_civic_policy_repeal(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), _connection=None):
    source_venue = services.venue_service().source_venue
    if source_venue is None or not source_venue.civic_policy_provider is None or source_venue.civic_policy_provider.repeal(policy):
        sims4.commands.automation_output('Status; Result:Failed', _connection)
        sims4.commands.cheat_output('{} not repealed'.format(policy), _connection)
    else:
        sims4.commands.automation_output('Status; Result:Success', _connection)


@sims4.commands.Command('civic_policy.venue.vote', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def venue_civic_policy_vote(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), count: int=1, _connection=None):
    count = int(count)
    source_venue = services.venue_service().source_venue
    if source_venue is None or not source_venue.civic_policy_provider is None or source_venue.civic_policy_provider.vote(policy, count):
        sims4.commands.cheat_output('Could not add vote to {}'.format(policy), _connection)
        sims4.commands.automation_output('Status; Result:Failed', _connection)
    else:
        sims4.commands.automation_output('Status; Result:Success', _connection)


@sims4.commands.Command('civic_policy.venue.force_end_voting', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def venue_civic_policy_force_end_voting(_connection=None):
    source_venue = services.venue_service().source_venue
    if source_venue is None:
        return False
    provider = source_venue.civic_policy_provider
    if provider is None:
        return False

    def output_enacted_policy_list():
        policies = provider.get_enacted_policies()
        for policy in policies:
            sims4.commands.cheat_output('    {}'.format(policy), _connection)

    sims4.commands.cheat_output('Before Enacted Policies', _connection)
    output_enacted_policy_list()
    provider.close_voting()
    sims4.commands.cheat_output('After Enacted Policies', _connection)
    output_enacted_policy_list()


@sims4.commands.Command('civic_policy.venue.show_community_board', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def venue_civic_policy_show_community_board(opt_sim: OptionalSimInfoParam=None, opt_target_id: int=0, _connection=None):
    street_service = services.street_service()
    if street_service is None:
        sims4.commands.automation_output('Pack not loaded', _connection)
        sims4.commands.cheat_output('Pack not loaded', _connection)
        return
    sim_info = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    source_venue = services.venue_service().source_venue
    if source_venue is None:
        return
    provider = source_venue.civic_policy_provider
    if provider is None:
        return
    op = CommunityBoardDialog(provider, sim_info, opt_target_id)
    Distributor.instance().add_op_with_no_owner(op)


@sims4.commands.Command('civic_policy.venue.policy_list', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def civic_policy_list(selector: CivicPolicyProviderListSelector=None, _connection=None):
    source_venue = services.venue_service().source_venue
    if source_venue is None:
        return False
    provider = source_venue.civic_policy_provider
    if provider is None:
        return False
    debug_automation_output_policy_name_list(provider, selector, _connection)


@sims4.commands.Command('civic_policy.venue.vote_count', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def street_civic_policy_vote_count(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), _connection=None):
    provider = None
    source_venue = services.venue_service().source_venue
    if source_venue is not None:
        provider = source_venue.civic_policy_provider
    debug_automation_output_vote_info(provider, policy, _connection)