# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\civic_policies\base_civic_policy_utilities.py
# Compiled at: 2020-10-19 11:06:43
# Size of source mod 2**32: 2977 bytes
import sims4
from civic_policies.base_civic_policy import BaseCivicPolicy
from civic_policies.base_civic_policy_provider import BaseCivicPolicyProvider
import enum

class CivicPolicyProviderListSelector(enum.Int):
    All = 0
    Balloted = 1
    Enacted = 2
    UpForRepeal = 3
    Dormant = 4


def debug_get_policy_name_list(provider: BaseCivicPolicyProvider, list_selector: CivicPolicyProviderListSelector=None):
    if list_selector == CivicPolicyProviderListSelector.Balloted:
        policies = provider.get_balloted_policies(tuning=True)
    else:
        if list_selector == CivicPolicyProviderListSelector.Enacted:
            policies = provider.get_enacted_policies(tuning=True)
        else:
            if list_selector == CivicPolicyProviderListSelector.UpForRepeal:
                policies = provider.get_up_for_repeal_policies(tuning=True)
            else:
                if list_selector == CivicPolicyProviderListSelector.Dormant:
                    policies = provider.get_dormant_policies(tuning=True)
                else:
                    policies = provider.get_civic_policies(tuning=True)
    ret = []
    for policy in policies:
        ret.append(policy.__name__)

    return ret


def debug_automation_output_policy_name_list(provider: BaseCivicPolicyProvider, list_selector: CivicPolicyProviderListSelector=None, _connection=None):
    if provider:
        name_list = debug_get_policy_name_list(provider, list_selector)
        for name in name_list:
            sims4.commands.automation_output('Policy; Data : {}'.format(name), _connection)
            sims4.commands.cheat_output(name, _connection)

    sims4.commands.automation_output('Policy; Data : END', _connection)


def debug_get_policy_vote_info(provider: BaseCivicPolicyProvider, policy: BaseCivicPolicy):
    count = 0
    stat = None
    if provider:
        stat = policy.vote_count_statistic
        if stat is None:
            count = 0
        else:
            count = int(provider.get_stat_value(stat))
    return (
     stat, count)


def debug_automation_output_vote_info(provider: BaseCivicPolicyProvider, policy: BaseCivicPolicy, _connection=None):
    stat, count = debug_get_policy_vote_info(provider, policy)
    sims4.commands.automation_output('VoteCount; Policy : {}, Stat : {}, Count : {}'.format(policy.__name__, stat.__name__, count), _connection)
    sims4.commands.cheat_output('{} : {}'.format(stat.__name__, count), _connection)