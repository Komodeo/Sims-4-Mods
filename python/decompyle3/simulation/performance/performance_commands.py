# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\performance\performance_commands.py
# Compiled at: 2022-08-26 15:13:12
# Size of source mod 2**32: 64377 bytes
from collections import Counter, namedtuple
from itertools import combinations
from gameplay_scenarios import scenario
from interactions.utils import loot_basic_op
from numbers import Number
import collections
from adaptive_clock_speed import AdaptiveClockSpeed
from clock import ClockSpeedMultiplierType, ClockSpeedMode
from gsi_handlers.performance_handlers import generate_statistics
from interactions.utils.death import DeathType
from relationships.global_relationship_tuning import RelationshipGlobalTuning
from relationships.relationship_enums import RelationshipBitCullingPrevention, RelationshipDecayMetricKeys, RelationshipDirection
from server_commands.autonomy_commands import show_queue, autonomy_distance_estimates_enable, autonomy_distance_estimates_dump
from server_commands.cache_commands import cache_status
from sims.household_telemetry import HouseholdRegionTelemetryData
from sims.occult.occult_enums import OccultType
from sims.sim_info import SimInfo
from sims.sim_info_lod import SimInfoLODLevel
from sims4.commands import CommandType
from sims4.profiler_utils import create_custom_named_profiler_function
from sims4.utils import create_csv
from statistics.base_statistic import BaseStatistic
from story_progression.story_progression_action_relationship_culling import StoryProgressionRelationshipCulling
from zone import freeze_game_time_in_pause
import autonomy.autonomy_util, enum, event_testing
import performance.performance_constants as consts
import services, sims4.commands, caches
CLIENT_STATE_OPS_TO_IGNORE = [
 'autonomy_modifiers']
RelationshipMetrics = namedtuple('RelationshipMetrics', ('rels', 'rels_active', 'rels_played',
                                                         'rels_unplayed', 'rel_bits_one_way',
                                                         'rel_bits_bi', 'rel_tracks',
                                                         'avg_meaningful_rels', 'played_sims_with_sentiments',
                                                         'rels_on_played_sims_with_sentiments',
                                                         'num_sentiments_on_player_sims',
                                                         'num_sims_with_sentiments',
                                                         'rels_with_sentiments',
                                                         'total_num_sentiments'))

@sims4.commands.Command('performance.log_alarms')
def log_alarms(enabled: bool=True, check_cooldown: bool=True, _connection=None):
    services.current_zone().alarm_service._log = enabled
    return True


@sims4.commands.Command('performance.log_object_statistics', command_type=(CommandType.Automation))
def log_object_statistics(outputFile=None, _connection=None):
    result = generate_statistics()
    if outputFile is not None:
        cheat_output = sims4.commands.FileOutput(outputFile, _connection)
    else:
        cheat_output = sims4.commands.CheatOutput(_connection)
    automation_output = sims4.commands.AutomationOutput(_connection)
    automation_output('PerfLogObjStats; Status:Begin')
    for name, value in result:
        eval_value = eval(value)
        if isinstance(eval_value, Number):
            automation_output('PerfLogObjStats; Status:Data, Name:{}, Value:{}'.format(name, value))
            cheat_output('{} : {}'.format(name, value))
        else:
            if isinstance(eval_value, (list, tuple)):
                automation_output('PerfLogObjStats; Status:ListBegin, Name:{}'.format(name))
                cheat_output('Name : {}'.format(name))
                for obj_freq in eval_value:
                    object_name = obj_freq.get('name')
                    frequency = obj_freq.get('frequency')
                    automation_output('PerfLogObjStats; Status:ListData, Name:{}, Frequency:{}'.format(object_name, frequency))
                    cheat_output('{} : {}'.format(object_name, frequency))

                automation_output('PerfLogObjStats; Status:ListEnd, Name:{}'.format(name))
        cheat_output('\n')

    automation_output('PerfLogObjStats; Status:End')


@sims4.commands.Command('performance.log_object_statistics_summary', command_type=(CommandType.Automation))
def log_object_statistics_summary(object_breakdown: bool=False, _connection=None):
    result = generate_statistics()
    nodes, edges = services.current_zone().posture_graph_service.get_nodes_and_edges()
    result.append((consts.POSTURE_GRAPH_NODES, nodes))
    result.append((consts.POSTURE_GRAPH_EDGES, edges))
    output = sims4.commands.CheatOutput(_connection)
    ignore = set([x for x in consts.OBJECT_CLASSIFICATIONS])
    ignore.add(consts.TICKS_PER_SECOND)
    ignore.add(consts.COUNT_PROPS)
    ignore.add(consts.COUNT_OBJECTS_PROPS)
    f = '{:50} : {:5} : {:5}'
    breakdown_key = {}
    if object_breakdown:
        breakdown_key[consts.OBJS_ACTIVE_LOT_INTERACTIVE] = (consts.OBJS_INTERACTIVE, consts.LOCATION_ACTIVE_LOT)
        breakdown_key[consts.OBJS_ACTIVE_LOT_DECORATIVE] = (consts.OBJS_DECORATIVE, consts.LOCATION_ACTIVE_LOT)
        breakdown_key[consts.OBJS_OPEN_STREET_INTERACTIVE] = (consts.OBJS_INTERACTIVE, consts.LOCATION_OPEN_STREET)
        breakdown_key[consts.OBJS_OPEN_STREET_DECORATIVE] = (consts.OBJS_DECORATIVE, consts.LOCATION_OPEN_STREET)
        f = '{:75} : {:5} : {:5}'
        d = '  {:73} : {:5}'
    output(f.format('Metric', 'Value', 'Budget'))
    if object_breakdown:
        output(d.format('Object Name', ''))
    for name, value in result:
        if name in ignore:
            continue
        else:
            budget = consts.BUDGETS.get(name, '')
            output(f.format(name, value, budget))
        if name not in breakdown_key:
            continue
        else:
            breakdown_name, location = breakdown_key[name]
            for detail_name, detail_result in result:
                if detail_name != breakdown_name:
                    continue
                else:
                    detail_result_dict_list = eval(detail_result)
                    for detail in detail_result_dict_list:
                        if detail.get(consts.FIELD_LOCATION) == location:
                            output(d.format(detail.get(consts.FIELD_NAME), detail.get(consts.FIELD_FREQUENCY)))

    output('\nDetailed info in GSI: Performance Metrics panel, |performance.log_object_statistics, |performance.posture_graph_summary, RedDwarf: World Coverage Report')


@sims4.commands.Command('performance.add_automation_profiling_marker', command_type=(CommandType.Automation))
def add_automation_profiling_marker(message: str='Unspecified', _connection=None):
    name_f = create_custom_named_profiler_function(message)
    return name_f(lambda: None
)


class SortStyle(enum.Int, export=False):
    ALL = 0
    AVERAGE_TIME = 1
    TOTAL_TIME = 2
    COUNT = 3


@sims4.commands.Command('performance.test_profile.dump', command_type=(CommandType.Automation))
def dump_tests_profile(sort: SortStyle=SortStyle.ALL, _connection=None):
    create_profile_results(profile_name='test', profile=(event_testing.resolver.test_profile), sort=sort,
      _connection=_connection)


@sims4.commands.Command('performance.test_profile.dump_resolver', command_type=(CommandType.Automation))
def dump_test_resolver_profiles(_connection=None):
    TIME_MULTIPLIER = 1000

    def average_time(time, count):
        if time == 0 or count == 0:
            return 0
        return time * TIME_MULTIPLIER / count

    resolver_types = set()
    for test_name, test_metrics in event_testing.resolver.test_profile.items():
        resolver_types |= test_metrics.resolvers.keys()

    resolver_types = list(resolver_types)
    resolver_types.sort()

    def callback(file):
        file.write('Test,Count,AvgTime,ResolveTime,TestTime,{}\n'.format(','.join(('{}Count,{}'.format(x, x) for x in resolver_types))))
        for test_name, test_metrics in event_testing.resolver.test_profile.items():
            metrics = test_metrics.metrics
            file.write('{},{},{},{},{}'.format(test_name, metrics.count, average_time(metrics.get_total_time(), metrics.count), average_time(metrics.resolve_time, metrics.count), average_time(metrics.test_time, metrics.count)))
            for resolver_type in resolver_types:
                sub_metrics = test_metrics.resolvers.get(resolver_type)
                if sub_metrics is None:
                    file.write(',,')
                else:
                    count = sum((m.count for m in sub_metrics.values()))
                    resolve_time = sum((m.resolve_time for m in sub_metrics.values()))
                    file.write(',{},{}'.format(count, average_time(resolve_time, count)))

            file.write('\n')

    filename = 'test_resolver_profile'
    create_csv(filename, callback=callback, connection=_connection)


@sims4.commands.Command('performance.test_profile.enable', command_type=(CommandType.Automation))
def enable_test_profile(_connection=None):
    event_testing.resolver.test_profile = dict()
    output = sims4.commands.CheatOutput(_connection)
    output('Test profiling enabled. Dump the profile any time using performance.test_profile.dump')


@sims4.commands.Command('performance.test_profile.disable', command_type=(CommandType.Automation))
def disable_test_profile(_connection=None):
    event_testing.resolver.test_profile = None
    output = sims4.commands.CheatOutput(_connection)
    output('Test profiling disabled.')


@sims4.commands.Command('performance.test_profile.clear', command_type=(CommandType.Automation))
def clear_tests_profile(_connection=None):
    if event_testing.resolver.test_profile is not None:
        event_testing.resolver.test_profile.clear()
    output = sims4.commands.CheatOutput(_connection)
    output('Test profile metrics have been cleared.')


@sims4.commands.Command('performance.loot_profile.enable', command_type=(CommandType.Automation))
def enable_loot_profile(_connection=None):
    loot_basic_op.loot_profile = dict()
    output = sims4.commands.CheatOutput(_connection)
    output('Loot profiling enabled. Dump the profile any time using performance.loot_profile.dump')


@sims4.commands.Command('performance.loot_profile.disable', command_type=(CommandType.Automation))
def disable_loot_profile(_connection=None):
    loot_basic_op.loot_profile = None
    output = sims4.commands.CheatOutput(_connection)
    output('Loot profiling disabled.')


@sims4.commands.Command('performance.loot_profile.dump', command_type=(CommandType.Automation))
def dump_loots_profile(sort: SortStyle=SortStyle.ALL, _connection=None):
    create_profile_results(profile_name='loot', profile=(loot_basic_op.loot_profile), sort=sort,
      _connection=_connection,
      should_create_interaction_view=False)


@sims4.commands.Command('performance.scenario.enable', command_type=(CommandType.Automation))
def enable_scenario_profile(_connection=None):
    scenario.scenario_profiles = dict()
    output = sims4.commands.CheatOutput(_connection)
    output('Scenario profiling enabled. Dump the profile any time using performance.scenario.dump')
    freeze_game_time_in_pause(True)


@sims4.commands.Command('performance.scenario.disable', command_type=(CommandType.Automation))
def disable_scenario_profile(_connection=None):
    scenario.scenario_profiles = None
    output = sims4.commands.CheatOutput(_connection)
    output('Scenario profiling disabled.')


@sims4.commands.Command('performance.scenario.dump', command_type=(CommandType.Automation))
def dump_scenario_profile(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if scenario.scenario_profiles is None:
        output('scenario profiling is currently disabled. Use |performance.scenario.enable')
        return
    if len(scenario.scenario_profiles) == 0:
        output('scenario profiling is currently enabled but has no records.')
        return
    profile = None

    def scenario_callback(file):
        file.write('Phase Name,Final Debt,Max Debt,10%,20%,30%,40%,50%,60%,70%,80%,90%\n')
        for test_name, test_metrics in profile.items():
            perf_percentage_list = test_metrics.perf_percentage_list
            if len(perf_percentage_list) != 0:
                file.write('{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(test_name, test_metrics.get_final_time(), perf_percentage_list[9], perf_percentage_list[8], perf_percentage_list[7], perf_percentage_list[6], perf_percentage_list[5], perf_percentage_list[4], perf_percentage_list[3], perf_percentage_list[2], perf_percentage_list[1], perf_percentage_list[0]))

    for scenario_name, scenario_profile in scenario.scenario_profiles.items():
        filename = 'scenario_profile_{}'.format(scenario_name)
        profile = scenario_profile
        create_csv(filename, callback=scenario_callback, connection=_connection)


def create_profile_results(profile_name, profile, sort: SortStyle=SortStyle.ALL, _connection=None, should_create_interaction_view=True, should_create_sim_resolver_view=True):
    output = sims4.commands.CheatOutput(_connection)
    if profile is None:
        output('{} profiling is currently disabled. Use |performance.{}_profile.enable'.format(profile_name, profile_name))
        return
    if len(profile) == 0:
        output('{} profiling is currently enabled but has no records.'.format(profile_name))
        return

    def get_sort_style(metric):
        if sort == SortStyle.AVERAGE_TIME:
            return metric.get_average_time()
        if sort == SortStyle.TOTAL_TIME:
            return metric.get_total_time()
        if sort == SortStyle.COUNT:
            return metric.count

    TIME_MULTIPLIER = 1000

    def test_callback(file):
        file.write('{},Count,AverageTime(ms),TotalTime(ms),Resolver,Key,Count,AverageTime(ms),TotalTime(ms),MaxTime(ms)\n'.format(profile_name))
        for test_name, test_metrics in sorted((profile.items()), key=(lambda t: get_sort_style(t[1].metrics)
),
          reverse=True):
            file.write('{},{},{},{},,,,,\n'.format(test_name, test_metrics.metrics.count, test_metrics.metrics.get_average_time() * TIME_MULTIPLIER, test_metrics.metrics.get_total_time() * TIME_MULTIPLIER))
            for resolver in sorted(test_metrics.resolvers.keys()):
                data = test_metrics.resolvers[resolver]
                for key, metrics in sorted((data.items()), key=(lambda t: get_sort_style(t[1])
), reverse=True):
                    if metrics.get_average_time() > 0:
                        file.write(',,,,{},{},{},{},{},{}\n'.format(resolver, key, metrics.count, metrics.get_average_time() * TIME_MULTIPLIER, metrics.get_total_time() * TIME_MULTIPLIER, metrics.get_max_time() * TIME_MULTIPLIER))

    def create_test_view(sort_style):
        if sort_style != SortStyle.ALL:
            filename = profile_name + '_profile_' + str(sort_style).replace('.', '_')
            create_csv(filename, callback=test_callback, connection=_connection)

    interactions = collections.defaultdict(list)

    def interaction_callback(file):
        file.write('Interaction,TotalTime(ms),Test,Count,AverageTime(ms),AverageResolveTime(ms),TotalTime(ms),MaxTime(ms)\n')
        for iname, tests in sorted((interactions.items()), reverse=True,
          key=(lambda t: sum((m.get_total_time(include_test_set=False) for _, m in t[1]))
)):
            file.write('{},{},,,,,\n'.format(iname, sum((m.get_total_time(include_test_set=False) for _, m in tests)) * TIME_MULTIPLIER))
            for test, met in sorted(tests, reverse=True,
              key=(lambda t: (
             not t[1].is_test_set, t[1].get_total_time())
)):
                file.write(',,{},{},{},{},{},{}\n'.format(test, met.count, met.get_average_time() * TIME_MULTIPLIER, met.resolve_time * TIME_MULTIPLIER / met.count, met.get_total_time() * TIME_MULTIPLIER, met.get_max_time() * TIME_MULTIPLIER))

    def create_interaction_view():
        for tname, tmetrics in profile.items():
            interaction_resolver = tmetrics.resolvers.get('InteractionResolver')
            if interaction_resolver is None:
                continue
            else:
                for interaction, metrics in interaction_resolver.items():
                    interactions[interaction].append((tname, metrics))

        filename = '{}_profile_interactions'.format(profile_name)
        create_csv(filename, callback=interaction_callback, connection=_connection)

    sim_resolvers = collections.defaultdict(list)

    def sim_resolver_callback(file):
        file.write('ResolverInfo,TotalTime(ms),Test,Count,AverageTime(ms),TotalTime(ms),MaxTime(ms)\n')
        for rname, tests in sorted((sim_resolvers.items()), reverse=True, key=(lambda t: sum((m.get_total_time(include_test_set=False) for _, m in t[1]))
)):
            file.write('{},{},,,,\n'.format(rname, sum((m.get_total_time(include_test_set=False) for _, m in tests)) * TIME_MULTIPLIER))
            for test, met in sorted(tests, reverse=True,
              key=(lambda t: (
             not t[1].is_test_set, t[1].get_total_time())
)):
                file.write(',,{},{},{},{},{}\n'.format(test, met.count, met.get_average_time() * TIME_MULTIPLIER, met.get_total_time() * TIME_MULTIPLIER, met.get_max_time() * TIME_MULTIPLIER))

    def create_sim_resolver_view():
        for tname, tmetrics in profile.items():
            datum_prefix = 'SingleSimResolver:'
            sim_resolver = tmetrics.resolvers.get('SingleSimResolver')
            if sim_resolver is None:
                datum_prefix = 'DoubleSimResolver:'
                sim_resolver = tmetrics.resolvers.get('DoubleSimResolver')
            if sim_resolver is None:
                continue
            else:
                for resolver_datum, metrics in sim_resolver.items():
                    sim_resolvers[datum_prefix + resolver_datum].append((tname, metrics))

        filename = '{}_profile_sim_resolvers'.format(profile_name)
        create_csv(filename, callback=sim_resolver_callback, connection=_connection)

    if sort == SortStyle.ALL:
        for sort in SortStyle.values:
            create_test_view(sort)

    else:
        create_test_view(sort)
    if should_create_interaction_view:
        create_interaction_view()
    if should_create_sim_resolver_view:
        create_sim_resolver_view()


@sims4.commands.Command('performance.loot_profile.clear', command_type=(CommandType.Automation))
def clear_loots_profile(_connection=None):
    if loot_basic_op.loot_profile is not None:
        loot_basic_op.loot_profile.clear()
    output = sims4.commands.CheatOutput(_connection)
    output('Loot profile metrics have been cleared.')


@sims4.commands.Command('performance.print_player_household_metrics', command_type=(CommandType.Automation))
def player_household_metrics(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    active_sim_count, player_sim_count, played_sim_count = (0, 0, 0)
    active_household_count, player_household_count, played_household_count = (0, 0,
                                                                              0)
    households = services.household_manager().get_all()
    for household in households:
        if household.is_active_household:
            active_household_count += 1
            active_sim_count += len(household)
        elif household.is_player_household:
            player_household_count += 1
            player_sim_count += len(household)
        if household.is_played_household:
            played_household_count += 1
            played_sim_count += len(household)

    for name, value in (('#sim_infos', len(services.sim_info_manager())), ('#active sim_infos', active_sim_count),
     (
      '#player sim_infos', player_sim_count),
     (
      '#played sim_infos', played_sim_count),
     (
      '#households', len(households)),
     (
      '#active households', active_household_count),
     (
      '#player households', player_household_count),
     (
      '#played households', played_household_count)):
        output('{:50} : {}'.format(name, value))

    return True


def get_relationship_decay_metrics(output=None):
    total_relationships = 0
    metrics = collections.defaultdict(Counter)
    for x, y in combinations(services.sim_info_manager().values(), 2):
        x_y = x.relationship_tracker.relationship_decay_metrics(y.id)
        y_x = y.relationship_tracker.relationship_decay_metrics(x.id)
        decay_metrics = x_y if x_y is not None else y_x
        if decay_metrics is not None:
            active_counter = None
            total_relationships += 1
            if not (x.is_npc and y.is_npc):
                active_counter = metrics['active']
            else:
                if x.is_played_sim or y.is_played_sim:
                    active_counter = metrics['played']
                else:
                    active_counter = metrics['unplayed']
            if active_counter is None:
                continue
            else:
                active_counter += decay_metrics
                active_counter[RelationshipDecayMetricKeys.RELS] += 1
                long_term_tracks_decaying = decay_metrics[RelationshipDecayMetricKeys.LONG_TERM_TRACKS_DECAYING]
            if long_term_tracks_decaying > 0:
                active_counter[RelationshipDecayMetricKeys.RELS_WITH_DECAY] += 1

    return (
     total_relationships, metrics)


@sims4.commands.Command('performance.relationship_decay_metrics')
def print_relationship_decay_metrics(long_version: bool=False, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    total_tracks, metrics = get_relationship_decay_metrics(output=output)
    output('TOTAL_RELS = {:10}'.format(total_tracks))
    for status, metric in metrics.items():
        long_term_tracks = metric[RelationshipDecayMetricKeys.LONG_TERM_TRACKS]
        short_term_tracks = metric[RelationshipDecayMetricKeys.LONG_TERM_TRACKS]
        long_term_tracks_decaying = metric[RelationshipDecayMetricKeys.LONG_TERM_TRACKS_DECAYING]
        short_term_tracks_decaying = metric[RelationshipDecayMetricKeys.SHORT_TERM_TRACKS_DECAYING]
        long_term_tracks_decaying_at_convergence = metric[RelationshipDecayMetricKeys.LONG_TERM_TRACKS_AT_CONVERGENCE]
        short_term_tracks_decaying_at_convergence = metric[RelationshipDecayMetricKeys.SHORT_TERM_TRACKS_AT_CONVERGENCE]
        if not long_version:
            output('{:30} : {:5} : #decaying:{:4}: #tracks:{:4} : #tracks_decaying:{:4} : #tracks_at_convergence:{:4}'.format(str(status), metric[RelationshipDecayMetricKeys.RELS], metric[RelationshipDecayMetricKeys.RELS_WITH_DECAY], long_term_tracks + short_term_tracks, long_term_tracks_decaying + short_term_tracks_decaying, long_term_tracks_decaying_at_convergence + short_term_tracks_decaying_at_convergence))
            continue
        else:
            output('{:30} : {:5} : #decaying:{:4}: #tracks:{:4} : #tracks_decaying:{:4} : #tracks_at_convergence:{:4}: #long_term:{:4} : #long_term_decaying:{:4} : #long_term_at_convergence:{:4}: #short_term:{:4} : #short_term_decaying:{:4} : #short_term_at_convergence:{:4}'.format(str(status), metric[RelationshipDecayMetricKeys.RELS], metric[RelationshipDecayMetricKeys.RELS_WITH_DECAY], long_term_tracks + short_term_tracks, long_term_tracks_decaying + short_term_tracks_decaying, long_term_tracks_decaying_at_convergence + short_term_tracks_decaying_at_convergence, long_term_tracks, long_term_tracks_decaying, long_term_tracks_decaying_at_convergence, short_term_tracks, short_term_tracks_decaying, short_term_tracks_decaying_at_convergence))

    return metrics


@sims4.commands.Command('performance.relationship_object_per_sim')
def dump_relationship_object_information_per_sim(_connection=None):

    def callback(file):
        entries = []
        active_rel_objs = 0
        playable_rel_objs = 0
        unplayed_rel_obj = 0
        one_way_rel_obj = 0
        for x in services.sim_info_manager().values():
            total_rels = 0
            household_rels = 0
            rels_can_be_culled = 0
            rels_decaying = 0
            rels_target_unplayable = 0
            family_rels = 0
            rels_with_no_long_term_tracks = 0
            rels_target_playable = 0
            rels_target_active = 0
            for relationship in x.relationship_tracker:
                total_rels += 1
                decay_information = x.relationship_tracker.relationship_decay_metrics(relationship.get_other_sim_id(x.sim_id))
                if decay_information is not None:
                    decay_enabled, _, possible_tracks_decaying, _ = decay_information
                    if decay_enabled:
                        rels_decaying += 1
                    else:
                        if possible_tracks_decaying == 0:
                            rels_with_no_long_term_tracks += 1
                target_sim_info = relationship.get_other_sim_info(x.sim_id)
                if target_sim_info is not None:
                    if target_sim_info.household_id == x.household_id:
                        household_rels += 1
                    else:
                        if any((bit.relationship_culling_prevention == RelationshipBitCullingPrevention.PLAYED_AND_UNPLAYED for bit in relationship._bits.values())):
                            family_rels += 1
                        else:
                            rels_can_be_culled += 1
                    if not target_sim_info.is_npc:
                        rels_target_active += 1
                    else:
                        if target_sim_info.is_played_sim:
                            rels_target_playable += 1
                        else:
                            rels_target_unplayable += 1
                    if not (x.is_npc and target_sim_info.is_npc):
                        active_rel_objs += 1
                    else:
                        if x.is_played_sim or target_sim_info.is_played_sim:
                            playable_rel_objs += 1
                        else:
                            unplayed_rel_obj += 1
                else:
                    one_way_rel_obj += 1

            entries.append('a{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(x.id, x.first_name, x.last_name, total_rels, rels_can_be_culled, household_rels, family_rels, rels_target_active, rels_target_playable, rels_target_unplayable, rels_decaying, rels_with_no_long_term_tracks))

        total_rel_objects = active_rel_objs + playable_rel_objs + unplayed_rel_obj + one_way_rel_obj
        file.write('Metrics\n')
        file.write('#relationship python objs:,{}\n'.format(total_rel_objects))
        file.write('#relationships one way objects:,{}\n'.format(one_way_rel_obj))
        file.write('#relationships active objects:,{}\n'.format(active_rel_objs))
        file.write('#relationships played objects:,{}\n'.format(playable_rel_objs))
        file.write('#relationships unplayed objects:,{}\n\n'.format(unplayed_rel_obj))
        file.write('SimID,FirstName,LastName,Played,RelationshipObjects,#Cullable,HouseholdConnected,BitPreventingCulling,WithActive,WithPlayable,WithUnplayayble,#Decaying,#NoLongTermTracks\n')
        for row_entry in entries:
            file.write(row_entry)

    create_csv('relationship_objects_per_sim', callback=callback, connection=_connection)


def get_relationship_metrics--- This code section failed: ---

 L. 722         0  LOAD_CONST               0
                2  STORE_FAST               'rels'

 L. 723         4  LOAD_CONST               0
                6  STORE_FAST               'rels_active'

 L. 724         8  LOAD_CONST               0
               10  STORE_FAST               'rels_played'

 L. 725        12  LOAD_CONST               0
               14  STORE_FAST               'rels_unplayed'

 L. 726        16  LOAD_CONST               0
               18  STORE_FAST               'rel_bits_one_way'

 L. 727        20  LOAD_CONST               0
               22  STORE_FAST               'rel_bits_bi'

 L. 728        24  LOAD_CONST               0
               26  STORE_FAST               'rel_tracks'

 L. 729        28  LOAD_GLOBAL              collections
               30  LOAD_METHOD              defaultdict
               32  LOAD_GLOBAL              int
               34  CALL_METHOD_1         1  '1 positional argument'
               36  STORE_FAST               'meaningful_rels'

 L. 730        38  LOAD_GLOBAL              set
               40  CALL_FUNCTION_0       0  '0 positional arguments'
               42  STORE_FAST               'played_sims_with_sentiments'

 L. 731        44  LOAD_CONST               0
               46  STORE_FAST               'rels_on_played_sims_with_sentiments'

 L. 732        48  LOAD_CONST               0
               50  STORE_FAST               'num_sentiments_on_player_sims'

 L. 733        52  LOAD_GLOBAL              set
               54  CALL_FUNCTION_0       0  '0 positional arguments'
               56  STORE_FAST               'sims_with_sentiments'

 L. 734        58  LOAD_CONST               0
               60  STORE_FAST               'rels_with_sentiments'

 L. 735        62  LOAD_CONST               0
               64  STORE_FAST               'total_num_sentiments'

 L. 737        66  LOAD_GLOBAL              services
               68  LOAD_METHOD              relationship_service
               70  CALL_METHOD_0         0  '0 positional arguments'
               72  STORE_FAST               'rel_service'

 L. 738     74_76  SETUP_LOOP          640  'to 640'
               78  LOAD_FAST                'rel_service'
               80  GET_ITER         
             82_0  COME_FROM           636  '636'
             82_1  COME_FROM           626  '626'
             82_2  COME_FROM           528  '528'
            82_84  FOR_ITER            638  'to 638'
               86  STORE_FAST               'relationship'

 L. 739        88  LOAD_FAST                'relationship'
               90  LOAD_METHOD              find_sim_info_a
               92  CALL_METHOD_0         0  '0 positional arguments'
               94  STORE_FAST               'x'

 L. 740        96  LOAD_FAST                'x'
               98  LOAD_ATTR                sim_id
              100  STORE_FAST               'x_id'

 L. 741       102  LOAD_FAST                'relationship'
              104  LOAD_METHOD              find_sim_info_b
              106  CALL_METHOD_0         0  '0 positional arguments'
              108  STORE_FAST               'y'

 L. 742       110  LOAD_FAST                'y'
              112  LOAD_ATTR                sim_id
              114  STORE_FAST               'y_id'

 L. 743       116  LOAD_GLOBAL              set
              118  LOAD_FAST                'relationship'
              120  LOAD_METHOD              get_bits
              122  LOAD_FAST                'x_id'
              124  CALL_METHOD_1         1  '1 positional argument'
              126  CALL_FUNCTION_1       1  '1 positional argument'
              128  STORE_FAST               'x_bits'

 L. 744       130  LOAD_GLOBAL              set
              132  LOAD_FAST                'relationship'
              134  LOAD_METHOD              get_bits
              136  LOAD_FAST                'y_id'
              138  CALL_METHOD_1         1  '1 positional argument'
              140  CALL_FUNCTION_1       1  '1 positional argument'
              142  STORE_FAST               'y_bits'

 L. 745       144  LOAD_FAST                'rel_bits_bi'
              146  LOAD_GLOBAL              sum
              148  LOAD_GENEXPR             '<code_object <genexpr>>'
              150  LOAD_STR                 'get_relationship_metrics.<locals>.<genexpr>'
              152  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              154  LOAD_FAST                'x_bits'
              156  GET_ITER         
              158  CALL_FUNCTION_1       1  '1 positional argument'
              160  CALL_FUNCTION_1       1  '1 positional argument'
              162  INPLACE_ADD      
              164  STORE_FAST               'rel_bits_bi'

 L. 746       166  LOAD_FAST                'rel_bits_one_way'
              168  LOAD_GLOBAL              sum
              170  LOAD_GENEXPR             '<code_object <genexpr>>'
              172  LOAD_STR                 'get_relationship_metrics.<locals>.<genexpr>'
              174  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              176  LOAD_FAST                'x_bits'
              178  GET_ITER         
              180  CALL_FUNCTION_1       1  '1 positional argument'
              182  CALL_FUNCTION_1       1  '1 positional argument'
              184  LOAD_GLOBAL              sum
              186  LOAD_GENEXPR             '<code_object <genexpr>>'
              188  LOAD_STR                 'get_relationship_metrics.<locals>.<genexpr>'
              190  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              192  LOAD_FAST                'y_bits'
              194  GET_ITER         
              196  CALL_FUNCTION_1       1  '1 positional argument'
              198  CALL_FUNCTION_1       1  '1 positional argument'
              200  BINARY_ADD       
              202  INPLACE_ADD      
              204  STORE_FAST               'rel_bits_one_way'

 L. 747       206  LOAD_FAST                'rel_tracks'
              208  LOAD_GLOBAL              len
              210  LOAD_FAST                'relationship'
              212  LOAD_ATTR                relationship_track_tracker
              214  CALL_FUNCTION_1       1  '1 positional argument'
              216  INPLACE_ADD      
              218  STORE_FAST               'rel_tracks'

 L. 748       220  LOAD_GLOBAL              len
              222  LOAD_FAST                'relationship'
              224  LOAD_METHOD              sentiment_track_tracker
              226  LOAD_FAST                'x_id'
              228  CALL_METHOD_1         1  '1 positional argument'
              230  CALL_FUNCTION_1       1  '1 positional argument'
              232  STORE_FAST               'x_sentiment_count'

 L. 749       234  LOAD_GLOBAL              len
              236  LOAD_FAST                'relationship'
              238  LOAD_METHOD              sentiment_track_tracker
              240  LOAD_FAST                'y_id'
              242  CALL_METHOD_1         1  '1 positional argument'
              244  CALL_FUNCTION_1       1  '1 positional argument'
              246  STORE_FAST               'y_sentiment_count'

 L. 750       248  LOAD_FAST                'x_sentiment_count'
              250  LOAD_CONST               0
              252  COMPARE_OP               >
          254_256  POP_JUMP_IF_TRUE    268  'to 268'
              258  LOAD_FAST                'y_sentiment_count'
              260  LOAD_CONST               0
              262  COMPARE_OP               >
          264_266  POP_JUMP_IF_FALSE   424  'to 424'
            268_0  COME_FROM           254  '254'

 L. 751       268  LOAD_FAST                'x_sentiment_count'
              270  LOAD_CONST               0
              272  COMPARE_OP               >
          274_276  POP_JUMP_IF_FALSE   330  'to 330'

 L. 752       278  LOAD_FAST                'rel_tracks'
              280  LOAD_FAST                'x_sentiment_count'
              282  INPLACE_ADD      
              284  STORE_FAST               'rel_tracks'

 L. 753       286  LOAD_FAST                'total_num_sentiments'
              288  LOAD_FAST                'x_sentiment_count'
              290  INPLACE_ADD      
              292  STORE_FAST               'total_num_sentiments'

 L. 754       294  LOAD_FAST                'sims_with_sentiments'
              296  LOAD_METHOD              add
              298  LOAD_FAST                'x_id'
              300  CALL_METHOD_1         1  '1 positional argument'
              302  POP_TOP          

 L. 755       304  LOAD_FAST                'x'
              306  LOAD_ATTR                is_played_sim
          308_310  POP_JUMP_IF_FALSE   330  'to 330'

 L. 756       312  LOAD_FAST                'played_sims_with_sentiments'
              314  LOAD_METHOD              add
              316  LOAD_FAST                'x_id'
              318  CALL_METHOD_1         1  '1 positional argument'
              320  POP_TOP          

 L. 757       322  LOAD_FAST                'num_sentiments_on_player_sims'
              324  LOAD_FAST                'x_sentiment_count'
              326  INPLACE_ADD      
              328  STORE_FAST               'num_sentiments_on_player_sims'
            330_0  COME_FROM           308  '308'
            330_1  COME_FROM           274  '274'

 L. 758       330  LOAD_FAST                'y_sentiment_count'
              332  LOAD_CONST               0
              334  COMPARE_OP               >
          336_338  POP_JUMP_IF_FALSE   392  'to 392'

 L. 759       340  LOAD_FAST                'rel_tracks'
              342  LOAD_FAST                'y_sentiment_count'
              344  INPLACE_ADD      
              346  STORE_FAST               'rel_tracks'

 L. 760       348  LOAD_FAST                'total_num_sentiments'
              350  LOAD_FAST                'y_sentiment_count'
              352  INPLACE_ADD      
              354  STORE_FAST               'total_num_sentiments'

 L. 761       356  LOAD_FAST                'sims_with_sentiments'
              358  LOAD_METHOD              add
              360  LOAD_FAST                'y_id'
              362  CALL_METHOD_1         1  '1 positional argument'
              364  POP_TOP          

 L. 762       366  LOAD_FAST                'y'
              368  LOAD_ATTR                is_played_sim
          370_372  POP_JUMP_IF_FALSE   392  'to 392'

 L. 763       374  LOAD_FAST                'played_sims_with_sentiments'
              376  LOAD_METHOD              add
              378  LOAD_FAST                'y_id'
              380  CALL_METHOD_1         1  '1 positional argument'
              382  POP_TOP          

 L. 764       384  LOAD_FAST                'num_sentiments_on_player_sims'
              386  LOAD_FAST                'y_sentiment_count'
              388  INPLACE_ADD      
              390  STORE_FAST               'num_sentiments_on_player_sims'
            392_0  COME_FROM           370  '370'
            392_1  COME_FROM           336  '336'

 L. 765       392  LOAD_FAST                'x'
              394  LOAD_ATTR                is_played_sim
          396_398  POP_JUMP_IF_TRUE    408  'to 408'
              400  LOAD_FAST                'y'
              402  LOAD_ATTR                is_played_sim
          404_406  POP_JUMP_IF_FALSE   416  'to 416'
            408_0  COME_FROM           396  '396'

 L. 766       408  LOAD_FAST                'rels_on_played_sims_with_sentiments'
              410  LOAD_CONST               1
              412  INPLACE_ADD      
              414  STORE_FAST               'rels_on_played_sims_with_sentiments'
            416_0  COME_FROM           404  '404'

 L. 767       416  LOAD_FAST                'rels_with_sentiments'
              418  LOAD_CONST               1
              420  INPLACE_ADD      
              422  STORE_FAST               'rels_with_sentiments'
            424_0  COME_FROM           264  '264'

 L. 768       424  LOAD_FAST                'rels'
              426  LOAD_CONST               1
              428  INPLACE_ADD      
              430  STORE_FAST               'rels'

 L. 769       432  LOAD_FAST                'x'
              434  LOAD_ATTR                is_npc
          436_438  POP_JUMP_IF_FALSE   448  'to 448'
              440  LOAD_FAST                'y'
              442  LOAD_ATTR                is_npc
          444_446  POP_JUMP_IF_TRUE    530  'to 530'
            448_0  COME_FROM           436  '436'

 L. 770       448  LOAD_FAST                'rels_active'
              450  LOAD_CONST               1
              452  INPLACE_ADD      
              454  STORE_FAST               'rels_active'

 L. 771       456  LOAD_FAST                'x'
              458  LOAD_ATTR                is_npc
          460_462  POP_JUMP_IF_TRUE    492  'to 492'
              464  LOAD_GLOBAL              RelationshipGlobalTuning
              466  LOAD_ATTR                MEANINGFUL_RELATIONSHIP_BITS
              468  LOAD_FAST                'x_bits'
              470  BINARY_AND       
          472_474  POP_JUMP_IF_FALSE   492  'to 492'

 L. 772       476  LOAD_FAST                'meaningful_rels'
              478  LOAD_FAST                'x_id'
              480  DUP_TOP_TWO      
              482  BINARY_SUBSCR    
              484  LOAD_CONST               1
              486  INPLACE_ADD      
              488  ROT_THREE        
              490  STORE_SUBSCR     
            492_0  COME_FROM           472  '472'
            492_1  COME_FROM           460  '460'

 L. 773       492  LOAD_FAST                'y'
              494  LOAD_ATTR                is_npc
          496_498  POP_JUMP_IF_TRUE    636  'to 636'
              500  LOAD_GLOBAL              RelationshipGlobalTuning
              502  LOAD_ATTR                MEANINGFUL_RELATIONSHIP_BITS
              504  LOAD_FAST                'y_bits'
              506  BINARY_AND       
          508_510  POP_JUMP_IF_FALSE   636  'to 636'

 L. 774       512  LOAD_FAST                'meaningful_rels'
              514  LOAD_FAST                'y_id'
              516  DUP_TOP_TWO      
              518  BINARY_SUBSCR    
              520  LOAD_CONST               1
              522  INPLACE_ADD      
              524  ROT_THREE        
              526  STORE_SUBSCR     
              528  JUMP_LOOP            82  'to 82'
            530_0  COME_FROM           444  '444'

 L. 775       530  LOAD_FAST                'x'
              532  LOAD_ATTR                is_played_sim
          534_536  POP_JUMP_IF_TRUE    546  'to 546'
              538  LOAD_FAST                'y'
              540  LOAD_ATTR                is_played_sim
          542_544  POP_JUMP_IF_FALSE   628  'to 628'
            546_0  COME_FROM           534  '534'

 L. 776       546  LOAD_FAST                'rels_played'
              548  LOAD_CONST               1
              550  INPLACE_ADD      
              552  STORE_FAST               'rels_played'

 L. 777       554  LOAD_FAST                'x'
              556  LOAD_ATTR                is_played_sim
          558_560  POP_JUMP_IF_FALSE   590  'to 590'
              562  LOAD_GLOBAL              RelationshipGlobalTuning
              564  LOAD_ATTR                MEANINGFUL_RELATIONSHIP_BITS
              566  LOAD_FAST                'x_bits'
              568  BINARY_AND       
          570_572  POP_JUMP_IF_FALSE   590  'to 590'

 L. 778       574  LOAD_FAST                'meaningful_rels'
              576  LOAD_FAST                'x_id'
              578  DUP_TOP_TWO      
              580  BINARY_SUBSCR    
              582  LOAD_CONST               1
              584  INPLACE_ADD      
              586  ROT_THREE        
              588  STORE_SUBSCR     
            590_0  COME_FROM           570  '570'
            590_1  COME_FROM           558  '558'

 L. 779       590  LOAD_FAST                'y'
              592  LOAD_ATTR                is_played_sim
          594_596  POP_JUMP_IF_FALSE   636  'to 636'
              598  LOAD_GLOBAL              RelationshipGlobalTuning
              600  LOAD_ATTR                MEANINGFUL_RELATIONSHIP_BITS
              602  LOAD_FAST                'y_bits'
              604  BINARY_AND       
          606_608  POP_JUMP_IF_FALSE   636  'to 636'

 L. 780       610  LOAD_FAST                'meaningful_rels'
              612  LOAD_FAST                'y_id'
              614  DUP_TOP_TWO      
              616  BINARY_SUBSCR    
              618  LOAD_CONST               1
              620  INPLACE_ADD      
              622  ROT_THREE        
              624  STORE_SUBSCR     
              626  JUMP_LOOP            82  'to 82'
            628_0  COME_FROM           542  '542'

 L. 782       628  LOAD_FAST                'rels_unplayed'
              630  LOAD_CONST               1
              632  INPLACE_ADD      
              634  STORE_FAST               'rels_unplayed'
            636_0  COME_FROM           606  '606'
            636_1  COME_FROM           594  '594'
            636_2  COME_FROM           508  '508'
            636_3  COME_FROM           496  '496'
              636  JUMP_LOOP            82  'to 82'
              638  POP_BLOCK        
            640_0  COME_FROM_LOOP       74  '74'

 L. 784       640  LOAD_FAST                'meaningful_rels'
          642_644  POP_JUMP_IF_FALSE   670  'to 670'
              646  LOAD_GLOBAL              sum
              648  LOAD_FAST                'meaningful_rels'
              650  LOAD_METHOD              values
              652  CALL_METHOD_0         0  '0 positional arguments'
              654  CALL_FUNCTION_1       1  '1 positional argument'
              656  LOAD_GLOBAL              float
              658  LOAD_GLOBAL              len
              660  LOAD_FAST                'meaningful_rels'
              662  CALL_FUNCTION_1       1  '1 positional argument'
              664  CALL_FUNCTION_1       1  '1 positional argument'
              666  BINARY_TRUE_DIVIDE
              668  JUMP_FORWARD        672  'to 672'
            670_0  COME_FROM           642  '642'
              670  LOAD_CONST               0
            672_0  COME_FROM           668  '668'
              672  STORE_FAST               'avg_meaningful_rels'

 L. 785       674  LOAD_GLOBAL              len
              676  LOAD_FAST                'played_sims_with_sentiments'
              678  CALL_FUNCTION_1       1  '1 positional argument'
              680  STORE_FAST               'num_player_sims_with_sentiments'

 L. 786       682  LOAD_GLOBAL              len
              684  LOAD_FAST                'sims_with_sentiments'
              686  CALL_FUNCTION_1       1  '1 positional argument'
              688  STORE_FAST               'num_sims_with_sentiments'

 L. 788       690  LOAD_GLOBAL              RelationshipMetrics
              692  LOAD_FAST                'rels'

 L. 789       694  LOAD_FAST                'rels_active'

 L. 790       696  LOAD_FAST                'rels_played'

 L. 791       698  LOAD_FAST                'rels_unplayed'

 L. 792       700  LOAD_FAST                'rel_bits_one_way'

 L. 793       702  LOAD_FAST                'rel_bits_bi'

 L. 794       704  LOAD_FAST                'rel_tracks'

 L. 795       706  LOAD_FAST                'avg_meaningful_rels'

 L. 796       708  LOAD_FAST                'num_player_sims_with_sentiments'

 L. 797       710  LOAD_FAST                'rels_on_played_sims_with_sentiments'

 L. 798       712  LOAD_FAST                'num_sentiments_on_player_sims'

 L. 799       714  LOAD_FAST                'num_sims_with_sentiments'

 L. 800       716  LOAD_FAST                'rels_with_sentiments'

 L. 801       718  LOAD_FAST                'total_num_sentiments'
              720  CALL_FUNCTION_14     14  '14 positional arguments'
              722  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 640_0


@sims4.commands.Command('performance.relationship_status', command_type=(CommandType.Automation))
def relationship_status(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    metrics = get_relationship_metrics(output=output)
    dump = []
    dump.append(('#relationships', metrics.rels))
    dump.append(('#relationships active sims', metrics.rels_active))
    dump.append(('#relationships played sims', metrics.rels_played))
    dump.append(('#relationships unplayed sims', metrics.rels_unplayed))
    dump.append(('#relationships rel bits one-way', metrics.rel_bits_one_way))
    dump.append(('#relationships rel bits bi-directional', metrics.rel_bits_bi))
    dump.append(('#relationships rel tracks', metrics.rel_tracks))
    dump.append(('#average meaningful rels', metrics.avg_meaningful_rels))
    for name, value in dump:
        output('{:40} : {}'.format(name, value))

    return dump


def get_sim_info_creation_sources():
    counter = Counter()
    for sim_info in services.sim_info_manager().values():
        counter[str(sim_info.creation_source)] += 1

    return counter


@sims4.commands.Command('performance.print_sim_info_creation_sources', command_type=(CommandType.Automation))
def print_sim_info_creation_sources(_connection=None):
    counter = get_sim_info_creation_sources()
    output = sims4.commands.CheatOutput(_connection)
    automation_output = sims4.commands.AutomationOutput(_connection)
    output('Total sim_infos: {}'.format(sum(counter.values())))
    output('--------------------')
    automation_output('SimInfoPerformance; Status:Begin, TotalSimInfos:{}'.format(sum(counter.values())))
    for source, count in counter.most_common():
        automation_source = source
        if source == '':
            source = 'Unknown - Is empty string'
            automation_source = 'Unknown'
        else:
            output('{:100} : {}'.format(source, count))
            if ': ' in automation_source:
                automation_source = automation_source.replace(': ', '(') + ')'
            automation_output('SimInfoPerformance; Status:Data, Source:{}, Count:{}'.format(automation_source, count))

    automation_output('SimInfoPerformance; Status:End')
    return counter


@sims4.commands.Command('performance.print_census_report', command_type=(CommandType.Automation))
def print_census_report(_connection=None):
    age = Counter()
    gender = Counter()
    ghost = Counter()
    occult = Counter()
    lod = Counter()
    sim_types = Counter()
    household_types = Counter()
    output = sims4.commands.CheatOutput(_connection)
    for sim_info in services.sim_info_manager().values():
        age[sim_info.age] += 1
        gender[sim_info.gender] += 1
        if sim_info.is_ghost:
            death_type = sim_info.death_tracker._death_type
            if death_type is not None:
                ghost[DeathType(death_type)] += 1
            else:
                output('{} is a ghost with no death_type.'.format(sim_info))
        for ot in OccultType:
            if sim_info.occult_types & ot:
                occult[ot] += 1

        lod[sim_info.lod] += 1

    for household in services.household_manager().values():
        if household.is_active_household:
            household_types['active'] += 1
            sim_types['active'] += len(household)
        else:
            if household.is_player_household:
                household_types['player'] += 1
                sim_types['player'] += len(household)
            else:
                household_types['unplayed'] += 1
                sim_types['unplayed'] += len(household)

    formatting = '{:14} : {:^10} : {}'
    output(formatting.format('Classification', 'Total', 'Histogram'))

    def _print(classification, counter):
        output(formatting.format(classification, sum(counter.values()), counter.most_common()))

    result = []
    result.append(('Households', household_types))
    result.append(('Sims', sim_types))
    result.append(('LOD', lod))
    result.append(('Age', age))
    result.append(('Gender', gender))
    result.append(('Occult', occult))
    result.append(('Ghost', ghost))
    for name, counter in result:
        _print(name, counter)

    return result


@sims4.commands.Command('performance.clock_status', command_type=(CommandType.Automation))
def clock_status(_connection=None):
    stats = []
    game_clock = services.game_clock_service()
    clock_speed = ClockSpeedMode(game_clock.clock_speed)
    deviance, threshold, current_duration, duration = AdaptiveClockSpeed.get_debugging_metrics()
    output = sims4.commands.CheatOutput(_connection)
    stats.append(('Clock Speed',
     clock_speed,
     '(Current player-facing clock speed)'))
    stats.append(('Speed Multiplier Type',
     ClockSpeedMultiplierType(game_clock.clock_speed_multiplier_type),
     '(Decides the speed 2/3/SS3 multipliers for adaptive speed)'))
    stats.append(('Clock Speed Multiplier',
     game_clock.current_clock_speed_scale(),
     '(Current Speed scaled with appropriate speed settings)'))
    stats.append(('Simulation Deviance',
     '{:>7} / {:<7}'.format(deviance, threshold),
     '(Simulation clock deviance from time service clock / Tuning Threshold [units: ticks])'))
    stats.append(('Deviance Duration',
     '{:>7} / {:<7}'.format(str(current_duration), duration),
     '(Current duration in multiplier phase / Tuning Duration [units: ticks])'))
    for name, value, description in stats:
        output('{:25} {!s:40} {}'.format(name, value, description))

    sims4.commands.automation_output('Performance; ClockSpeed:{}'.format(clock_speed), _connection)


@sims4.commands.Command('performance.status', command_type=(CommandType.Automation))
def status(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('==Clock==')
    clock_status(_connection=_connection)
    output('==AutonomyQueue==')
    show_queue(_connection=_connection)
    output('==ACC&BCC==')
    cache_status(_connection=_connection)


@sims4.commands.Command('performance.trigger_sim_info_firemeter', command_type=(CommandType.Automation))
def trigger_sim_info_firemeter(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim_info_manager = services.sim_info_manager()
    lod_counts = {lod: sim_info_manager.get_num_sim_infos_with_lod(lod) for lod in }
    sim_info_manager.trigger_firemeter()
    output('LOD counts Before/After firemeter:')
    for lod in SimInfoLODLevel:
        new_count = sim_info_manager.get_num_sim_infos_with_lod(lod)
        output('{}: {} -> {}'.format(lod.name, lod_counts[lod], new_count))


@sims4.commands.Command('performance.trigger_npc_relationship_culling', command_type=(CommandType.Automation))
def trigger_npc_relationship_culling(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('Before relationship culling')
    relationship_status(_connection=_connection)
    StoryProgressionRelationshipCulling.trigger_npc_relationship_culling()
    output('After relationship culling')
    relationship_status(_connection=_connection)


@sims4.commands.Command('performance.posture_graph_summary', command_type=(CommandType.Automation))
def posture_graph_summary(outputFile=None, _connection=None):
    if outputFile is not None:
        output = sims4.commands.FileOutput(outputFile, _connection)
    else:
        output = sims4.commands.CheatOutput(_connection)
    services.current_zone().posture_graph_service.print_summary(output)
    sims4.commands.automation_output('PostureGraphSummary; Status:End', _connection)


@sims4.commands.Command('performance.sub_autonomy_tracking_start', 'autonomy.sub_autonomy_tracking_start', command_type=(sims4.commands.CommandType.Automation))
def record_autonomy_ping_data(_connection=None):
    autonomy.autonomy_util.record_autonomy_ping_data(services.time_service().sim_now)


@sims4.commands.Command('performance.sub_autonomy_tracking_print', 'autonomy.sub_autonomy_tracking_print', command_type=(sims4.commands.CommandType.Automation))
def print_sub_autonomy_output(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    autonomy.autonomy_util.print_sub_autonomy_ping_data(services.time_service().sim_now, output)


@sims4.commands.Command('performance.sub_autonomy_tracking_stop', 'autonomy.sub_autonomy_tracking_stop', command_type=(sims4.commands.CommandType.Automation))
def stop_recording_autonomy_ping_data(_connection=None):
    autonomy.autonomy_util.stop_sub_autonomy_ping_data()


@sims4.commands.Command('performance.autonomy_profile.enable', command_type=(CommandType.Automation))
def enable_autonomy_profiling_data(_connection=None):
    autonomy.autonomy_util.record_autonomy_profiling_data()
    output = sims4.commands.CheatOutput(_connection)
    output('Autonomy profiling enabled. Dump the profile any time using performance.autonomy_profile.dump')


@sims4.commands.Command('performance.autonomy_profile.disable', command_type=(CommandType.Automation))
def disable_autonomy_profiling_data(_connection=None):
    autonomy.autonomy_util.g_autonomy_profile_data = None
    output = sims4.commands.CheatOutput(_connection)
    output('Autonomy profiling disabled.')


@sims4.commands.Command('performance.autonomy_profile.clear', command_type=(CommandType.Automation))
def autonomy_autonomy_profiling_data_clear(_connection=None):
    if autonomy.autonomy_util.g_autonomy_profile_data is not None:
        autonomy.autonomy_util.g_autonomy_profile_data.reset_profiling_data()
    output = sims4.commands.CheatOutput(_connection)
    output('Autonomy profile metrics have been cleared.')


@sims4.commands.Command('performance.autonomy_profile.dump', command_type=(CommandType.Automation))
def dump_autonomy_profiling_data(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    if autonomy.autonomy_util.g_autonomy_profile_data is None:
        output('Autonomy profiling is currently disabled. Use |performance.autonomy_profile.enable')
        return
    if not autonomy.autonomy_util.g_autonomy_profile_data.autonomy_requests:
        output('Autonomy profiling is currently enabled but has no records.')
        return

    def callback(file):
        autonomy.autonomy_util.g_autonomy_profile_data.write_profiling_data_to_file(file)

    filename = 'autonomy_profile'
    create_csv(filename, callback=callback, connection=_connection)


@sims4.commands.Command('performance.send_household_region_telemetry', command_type=(CommandType.Automation))
def send_region_sim_info_telemetry(_connection=None):
    HouseholdRegionTelemetryData.send_household_region_telemetry()


def print_commodity_census(predicate=lambda x: x
, most_common=10, _connection=None):
    counter = collections.Counter()
    initial_counter = collections.Counter()
    commodity_counter = collections.Counter()
    commodity_initial_counter = collections.Counter()
    core_commodity_counter = collections.Counter()
    nonsim_stat_counter = collections.Counter()

    def compile_tracker(tracker, non_sim):
        try:
            for t in tracker:
                if not predicate(t):
                    continue
                else:
                    stat_type = t.stat_type if hasattr(t, 'stat_type') else t
                    counter[stat_type] += 1
                    if hasattr(t, 'initial_value'):
                        if t.get_value() == t.initial_value:
                            initial_counter[stat_type] += 1
                if non_sim:
                    nonsim_stat_counter[stat_type] += 1

        except TypeError:
            pass

    def compile_obj_state_trackers(obj):
        if hasattr(obj, 'commodity_tracker'):
            if obj.commodity_tracker is not None:
                compile_tracker(obj.commodity_tracker, not obj.is_sim)
                for commodity in obj.commodity_tracker:
                    if not predicate(commodity):
                        continue
                    else:
                        commodity_counter[commodity.stat_type] += 1
                        if hasattr(commodity, 'initial_value'):
                            if commodity.get_value() == commodity.initial_value:
                                commodity_initial_counter[commodity.stat_type] += 1
                    if commodity.core:
                        core_commodity_counter[commodity.stat_type] += 1

        if hasattr(obj, 'statistic_tracker'):
            if obj.statistic_tracker is not None:
                compile_tracker(obj.statistic_tracker, not obj.is_sim)

    for sim_info in services.sim_info_manager().values():
        for tracker_name in SimInfo.SIM_INFO_TRACKERS:
            tracker = getattr(sim_info, tracker_name)
            if tracker is None:
                continue
            else:
                compile_tracker(tracker, False)

        compile_obj_state_trackers(sim_info)

    for mgr in services.client_object_managers():
        for obj in mgr.get_all():
            if hasattr(obj, 'is_sim'):
                if not obj.is_sim:
                    compile_obj_state_trackers(obj)

    dump = []
    num_statistics = sum(counter.values())
    num_statistics_initial = sum(initial_counter.values())
    dump.append(('Total count', num_statistics))
    dump.append(('Initial count', num_statistics_initial))
    dump.append(('Non-initial count', num_statistics - num_statistics_initial))
    num_commodities = sum(commodity_counter.values())
    num_commodities_initial = sum(commodity_initial_counter.values())
    dump.append(('Total commodities count', num_commodities))
    dump.append(('Initial commodities count', num_commodities_initial))
    dump.append(('Non-initial commodities count', num_commodities - num_commodities_initial))
    num_non_sim_commodities = sum(nonsim_stat_counter.values())
    dump.append(('Total non-sim commodities count', num_non_sim_commodities))
    num_core_commodities = sum(core_commodity_counter.values())
    dump.append(('Total core commodities count', num_core_commodities))
    output = sims4.commands.CheatOutput(_connection)
    for name, value in dump:
        output('{:35} : {}'.format(name, value))

    output('\nMost common:')
    for commodity, num in counter.most_common(most_common):
        name = commodity.__name__ if hasattr(commodity, '__name__') else str(commodity)
        output('{:50} : {}'.format(name, num))

    output('\nMost common core:')
    for commodity, num in core_commodity_counter.most_common(most_common):
        name = commodity.__name__ if hasattr(commodity, '__name__') else str(commodity)
        output('{:50} : {}'.format(name, num))

    output('\nMost common at initial value:')
    for commodity, num in initial_counter.most_common(most_common):
        name = commodity.__name__ if hasattr(commodity, '__name__') else str(commodity)
        output('{:50} : {}'.format(name, num))


def print_base_statistic_tuning(skill, _connection=None):
    lod_to_set_map = {}
    lod_to_persisted_count = {}
    for stat_type in services.get_instance_manager(sims4.resources.Types.STATISTIC).types.values():
        if not issubclass(stat_type, BaseStatistic):
            continue
        if stat_type.is_skill != skill:
            continue
        if hasattr(stat_type, 'remove_on_convergence'):
            if stat_type.remove_on_convergence:
                continue
        min_lod_value = stat_type.min_lod_value if hasattr(stat_type, 'min_lod_value') else None
        if min_lod_value not in lod_to_set_map:
            lod_to_set_map[min_lod_value] = set()
            lod_to_persisted_count[min_lod_value] = 0
        else:
            try:
                if stat_type.persisted:
                    name = '{} (p)'.format(stat_type.__name__)
                    lod_to_persisted_count[min_lod_value] += 1
                else:
                    name = stat_type.__name__
            except:
                name = stat_type.__name__

            lod_to_set_map[min_lod_value].add(name)

    output = sims4.commands.CheatOutput(_connection)
    output('Tuned {} Base Statistics'.format('Skill' if skill else 'Non-Skill'))
    for key, val in lod_to_set_map.items():
        output('{} : {} ({} persisted)'.format(key, len(val), lod_to_persisted_count[key]))
        for entry in sorted(list(val)):
            output('    {}'.format(entry))


@sims4.commands.Command('performance.analyze.global', command_type=(CommandType.Automation))
def analyze_global(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('==Census==')
    print_census_report(_connection=_connection)
    output('==Relationships==')
    relationship_status(_connection=_connection)
    output('==Commodities==')
    commodity_status(_connection=_connection)
    output('==Environment==')
    log_object_statistics_summary(_connection=_connection)
    output('-==Object Score==-')
    from performance.object_score_commands import score_objects_in_world
    score_objects_in_world(verbose=False, _connection=_connection)


@sims4.commands.Command('performance.analyze.runtime.enable', command_type=(CommandType.Automation))
def analyze_begin(_connection=None):
    enable_test_profile(_connection=_connection)
    enable_loot_profile(_connection=_connection)
    autonomy_distance_estimates_enable(_connection=_connection)
    enable_test_cache(_connection=_connection)


@sims4.commands.Command('performance.analyze.runtime.dump', command_type=(CommandType.Automation))
def analyze_dump(_connection=None):
    dump_tests_profile(_connection=_connection)
    dump_loots_profile(_connection=_connection)
    dump_test_resolver_profiles(_connection=_connection)
    autonomy_distance_estimates_dump(_connection=_connection)


@sims4.commands.Command('performance.test_caches.dump', command_type=(CommandType.Automation))
def test_cache_dump(_connection=None):

    def callback(file):
        file.write('Function Key,Number of valid cached value missed')
        sorted_list = sorted((caches.cache_clear_misses.items()), key=(lambda x: x[1]
), reverse=True)
        for function_key, cache_miss_number in sorted_list:
            file.write('\n {},{}'.format(str(function_key).replace(',', '_'), cache_miss_number))

    output = sims4.commands.CheatOutput(_connection)
    if caches.cache_clear_misses is None:
        output('Caches profiling is currently disabled. Use |performance.test_caches.enable')
        return
    if len(caches.cache_clear_misses) == 0:
        output('Caches profiling is currently enabled but has no records.')
        return
    create_csv('cache_profile', callback=callback, connection=_connection)


@sims4.commands.Command('performance.test_caches.enable', command_type=(CommandType.Automation))
def enable_test_cache(_connection=None):
    caches.cache_clear_misses = {}


@sims4.commands.Command('performance.test_caches.disable', command_type=(CommandType.Automation))
def disable_test_cache(_connection=None):
    test_cache_dump(_connection)
    caches.cache_clear_misses = None


@sims4.commands.Command('performance.commodity_status', command_type=(CommandType.Automation))
def commodity_status(most_common: int=10, include_tuning: bool=False, _connection=None):

    def predicate(commodity):
        return not (hasattr(commodity, 'is_skill') and commodity.is_skill)

    print_commodity_census(predicate=predicate, most_common=most_common, _connection=_connection)
    if include_tuning:
        print_base_statistic_tuning(skill=False, _connection=_connection)


@sims4.commands.Command('performance.skill_status', command_type=(CommandType.Automation))
def skill_status(most_common: int=10, include_tuning: bool=False, _connection=None):

    def predicate(commodity):
        return hasattr(commodity, 'is_skill') and commodity.is_skill

    print_commodity_census(predicate=predicate, most_common=most_common, _connection=_connection)
    if include_tuning:
        print_base_statistic_tuning(skill=True, _connection=_connection)