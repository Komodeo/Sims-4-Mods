# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\weekly_schedule_zone_director.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 51796 bytes
import itertools
from _collections import defaultdict
from careers.career_event_zone_director import CareerEventZoneDirectorMixin
from date_and_time import create_date_and_time, create_time_span, DATE_AND_TIME_ZERO, sim_ticks_per_day, DateAndTime
from event_testing.resolver import GlobalResolver, SingleSimResolver, DoubleSimResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType
from sims4 import random
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, TunableInterval, TunableMapping, TunableEnumEntry, HasTunableReference, OptionalTunable, TunableRange, Tunable
from situations.bouncer.bouncer_types import RequestSpawningOption, BouncerRequestPriority
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo
from situations.situation_serialization import GLOBAL_SITUATION_LINKED_SIM_ID
from tunable_multiplier import TunableMultiplier
from tunable_time import Days, TunableTimeOfDayMapping, TunableTimeOfDay
from zone_director import ZoneDirectorBase
import alarms, enum, sims4.tuning, services, sims4.resources
logger = sims4.log.Logger('WeeklyScheduleZoneDirector', default_owner='nabaker')

class UserFacingType(enum.Int):
    NEVER = 0
    ALWAYS = 1
    LINK_SELECTABLE_SIMS = 2
    LINK_CAREER_SIMS = 3


class WeeklyScheduleSituationData(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'situation':TunableReference(description='\n            Situation to run.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION)), 
     'user_facing':TunableEnumEntry(description='\n            NEVER: Never make user facing.\n            ALWAYS: Make user facing if at least 1 selectable sim in in situation.\n            LINK_SELECTABLE_SIMS: Make user facing and link to selectable sim if only 1 selectable sim is in the situation.\n            LINK_CAREER_SIMS: Make user facing and link to career sim if only 1 career sim is in the situation.\n            ',
       tunable_type=UserFacingType,
       default=UserFacingType.NEVER), 
     'job_assignments':TunableList(description='\n            List of jobs with associated test of sims who can fulfill that job and min/max number of\n            sims assigned to that job.\n            \n            Will make two passes attempting to assign instantiated sims to jobs.  The first pass will\n            assign instantiated sims that pass the test into jobs until the jobs meets the minimum requirements.\n            The second pass will assign instantiated sims into jobs until the job meets the maximum requirements.\n            ',
       tunable=TunableTuple(job=TunableReference(description='\n                    The situation job. \n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB))),
       tests=TunableTestSet(description='\n                    Tests used to determine if the instanced sim should be assigned to this job.\n                    '),
       sim_count=TunableInterval(description='\n                    Number of sims for this job.\n                    Minimum of 0 means job is optional.\n                    Will attempt to assign up to the max before moving on to next job/situation.\n                    ',
       tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0),
       upper_bound_count_modifiers=TunableList(description='\n                    Reduce Max sim count by 1 for every sim previously assigned (in this time period)\n                    to specified situation/job.\n                    ',
       tunable=TunableTuple(situation=TunableReference(description='\n                            The Situation.\n                            ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION))),
       job=TunableReference(description='\n                            The situation job. \n                            ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))))))}

    @classmethod
    def _tuning_loaded_callback(cls):
        cls.default_job_order = []
        cls.default_met_minimum_jobs = {}
        cls.default_need_minimum_jobs = {}
        for entry in cls.job_assignments:
            cls.default_job_order.append(entry.job)
            if entry.sim_count.lower_bound == 0:
                cls.default_met_minimum_jobs[entry.job] = entry
            else:
                cls.default_need_minimum_jobs[entry.job] = entry

    @classmethod
    def try_start(cls, sims, sim_info, duration, additional_sim_ids, situation_job_count):
        minimum_required_sims = 0
        modified_upper_bounds = {}
        num_sims = len(sims)
        job_order = cls.default_job_order.copy()
        for entry in cls.job_assignments:
            upper_bound = entry.sim_count.upper_bound
            lower_bound = entry.sim_count.lower_bound
            for upper_bound_count_modifier in entry.upper_bound_count_modifiers:
                upper_bound -= situation_job_count[(upper_bound_count_modifier.situation, upper_bound_count_modifier.job)]
                if upper_bound <= 0:
                    if lower_bound > 0:
                        return
                    else:
                        job_order.remove(entry.job)
                        if not job_order:
                            return
                    break
                if upper_bound < lower_bound:
                    return

            modified_upper_bounds[entry.job] = upper_bound
            minimum_required_sims += lower_bound
            if minimum_required_sims > num_sims:
                return

        job_assignments = defaultdict(list)
        assigned_sims = set()
        need_minimum_jobs = cls.default_need_minimum_jobs.copy()
        met_minimum_jobs = cls.default_met_minimum_jobs.copy()
        for sim in sims:
            resolver = DoubleSimResolver(sim.sim_info, sim_info)
            assigned_job_entry = None
            for job in job_order:
                job_entry = need_minimum_jobs.get(job)
                if job_entry is None:
                    continue
                if job_entry.tests.run_tests(resolver):
                    assigned_job_entry = job_entry
                    if len(job_assignments[job]) + 1 >= job_entry.sim_count.lower_bound:
                        met_minimum_jobs[job] = job_entry
                        del need_minimum_jobs[job]
                    break
            else:
                for job in job_order:
                    job_entry = met_minimum_jobs.get(job)
                    if job_entry is None:
                        continue
                    if job_entry.tests.run_tests(resolver):
                        assigned_job_entry = job_entry
                        break

            if assigned_job_entry is not None:
                job = assigned_job_entry.job
                job_assignments[job].append(sim)
                assigned_sims.add(sim)
                if len(job_assignments[job]) >= modified_upper_bounds[job]:
                    job_order.remove(job)
                    if not job_order:
                        break

        if need_minimum_jobs:
            return
        if sim_info is None:
            requesting_sim_id = None
        else:
            requesting_sim_id = sim_info.sim_id
        guest_list = SituationGuestList(invite_only=True,
          filter_requesting_sim_id=requesting_sim_id)
        sim_ids_of_interest = []
        for job, sim_list in job_assignments.items():
            for sim in sim_list:
                guest_list.add_guest_info(SituationGuestInfo(sim.sim_id, job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))
                if cls.user_facing == UserFacingType.LINK_CAREER_SIMS:
                    if sim.sim_id in additional_sim_ids:
                        sim_ids_of_interest.append(sim.sim_id)
                else:
                    if sim.is_selectable:
                        sim_ids_of_interest.append(sim.sim_id)

        if not guest_list:
            return
        if cls.user_facing == UserFacingType.NEVER:
            linked_sim_id = GLOBAL_SITUATION_LINKED_SIM_ID
            user_facing = False
        else:
            if cls.user_facing == UserFacingType.ALWAYS:
                linked_sim_id = GLOBAL_SITUATION_LINKED_SIM_ID
                user_facing = bool(sim_ids_of_interest)
            else:
                if len(sim_ids_of_interest) == 1:
                    linked_sim_id = sim_ids_of_interest[0]
                    user_facing = True
                else:
                    linked_sim_id = GLOBAL_SITUATION_LINKED_SIM_ID
                    user_facing = False
        situation_manager = services.get_zone_situation_manager()
        situation_id = situation_manager.create_situation((cls.situation),
          user_facing=user_facing,
          duration_override=duration,
          guest_list=guest_list,
          spawn_sims_during_zone_spin_up=True,
          linked_sim_id=linked_sim_id,
          creation_source=(str(cls)))
        if situation_id is not None:
            sims.difference_update(assigned_sims)
            for job, sim_list in job_assignments.items():
                situation_job_count[(cls.situation, job)] += len(sim_list)

        return situation_id


class WeeklyScheduleSituationSet(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'required_situations':TunableList(description='\n            Situations that will always attempt to run as long as required jobs are sufficiently filled.\n            ',
       tunable=TunableTuple(situation_data=WeeklyScheduleSituationData.TunableReference(description='\n                    The situation data to run.\n                    '),
       max_created=OptionalTunable(description='\n                    Maximum number of this situation to create.\n                    ',
       tunable=TunableTuple(count=TunableRange(description='\n                            Maximum number of this situation to create.\n                            ',
       tunable_type=int,
       default=1,
       minimum=1),
       count_modifiers=TunableList(description='\n                            Reduce number of situations by 1 for every sim previously assigned (in this time period)\n                            to specified situation/job.\n                            ',
       tunable=TunableTuple(situation=TunableReference(description='\n                                    The Situation.\n                                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION))),
       job=TunableReference(description='\n                                    The situation job. \n                                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))))),
       enabled_by_default=True,
       disabled_name='unlimited',
       enabled_name='limited'))), 
     'random_situations':TunableList(description='\n            Situations in which remaining instantiated sims will attempt to be placed\n            ',
       tunable=TunableTuple(weight=TunableMultiplier.TunableFactory(description='\n                    Weight for this situation. Used for random selection until all\n                    available sims are used.\n                    '),
       situation_data=WeeklyScheduleSituationData.TunableReference(description='\n                    The situation data to run.\n                    '))), 
     'start_on_time_loot':TunableList(description="\n             A list of loot operations that will be given if the situation set\n             starts at the beginning of it's scheduled time.  (i.e. Didn't \n             travel to the lot mid period.)\n             ",
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'start_any_time_loot':TunableList(description="\n             A list of loot operations that will be given when this situation \n             set starts regardless of whether it's at the start.  (i.e. Even if \n             user travelled to the lot mid period.)\n             ",
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True))}

    @classmethod
    def start(cls, resolver, sim_info, duration, additional_sim_ids, sims=None, start=True, on_time=False, delayed_loots=None):
        started_situation_ids = []
        if sims is None:
            sims = set(services.sim_info_manager().instanced_sims_gen())
        situation_job_count = defaultdict(int)
        for situation_data_info in cls.required_situations:
            max_created = situation_data_info.max_created
            if max_created is not None:
                count = max_created.count
                for count_modifier in max_created.count_modifiers:
                    count -= situation_job_count[(count_modifier.situation, count_modifier.job)]

            while max_created is None or count > 0:
                situation_id = situation_data_info.situation_data.try_start(sims, sim_info, duration, additional_sim_ids, situation_job_count)
                if situation_id is not None:
                    if max_created is not None:
                        count -= 1
                    else:
                        started_situation_ids.append(situation_id)
                    if not sims:
                        break
                    break

            if not sims:
                break

        if sims:
            weighted_options = []
            for entry in cls.random_situations:
                weight = entry.weight.get_multiplier(resolver)
                if weight > 0:
                    weighted_options.append((weight, entry.situation_data))

            while sims:
                if weighted_options:
                    situation_data = sims4.random.pop_weighted(weighted_options)
                    situation_id = situation_data.try_start(sims, sim_info, duration, additional_sim_ids, situation_job_count)
                    if situation_id is not None:
                        started_situation_ids.append(situation_id)

        if start:
            for loot_action in cls.start_any_time_loot:
                if delayed_loots is not None:
                    delayed_loots.append(loot_action)
                else:
                    loot_action.apply_to_resolver(resolver)

            if on_time:
                for loot_action in cls.start_on_time_loot:
                    if delayed_loots is not None:
                        delayed_loots.append(loot_action)
                    else:
                        loot_action.apply_to_resolver(resolver)

        return started_situation_ids


class WeeklyScheduleDay(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'schedule':TunableTimeOfDayMapping.TunableFactory(description='\n            Each entry in the map has 3 columns. The first column is\n            the hour of the day (0-24), 2nd column is minute of that hour, and\n            the third maps to a weighted selection of situations for that time slot.\n            \n            The entry with starting hour that is closest to, but before\n            the current hour will be chosen.\n            \n            Given this tuning: \n                hour_of_day           possible situation sets\n                6                     [(w1, s1), (w2, s2)]\n                10                    [(w1, s2)]\n                14                    [(w2, s5)]\n                20                    [(w9, s0)]\n                \n            If the current hour is 11, hour_of_day will be 10 and desired is [(w1, s2)].\n            If the current hour is 19, hour_of_day will be 14 and desired is [(w2, s5)].\n            If the current hour is 23, hour_of_day will be 20 and desired is [(w9, s0)].\n            If the current hour is 2, hour_of_day will be 20 and desired is [(w9, s0)]. (uses 20 tuning because it is not 6 yet)\n            \n            The entries will be automatically sorted by time.\n            ',
       hours={'value_name':'Situation_sets', 
      'value_type':TunableList(tunable=TunableTuple(weight=TunableMultiplier.TunableFactory(description='\n                            Weight for this set of situations.\n                            '),
        situation_set=WeeklyScheduleSituationSet.TunableReference(description='\n                            Set of situations for this time period.\n                            ')))}), 
     'long_term_situations':TunableList(description='\n            Long term situations that exist outside the schedule.\n            ',
       tunable=TunableTuple(situation=TunableReference(description='\n                    Situation to run.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)),
       pack_safe=True),
       start_time=TunableTimeOfDay(description='\n                    Time when this situation should start running.\n                    '),
       stop_time=TunableTimeOfDay(description='\n                    Time when this situation should stop running. 0:00 means\n                    should stop at end of day midnight.\n                    '),
       count=TunableInterval(description='\n                    Number of this situation to spin up.\n                    ',
       tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0),
       count_modifiers=TunableList(description='\n                    For each sim/siminfo that is a valid participant that \n                    passes the test, reduce max and min count by 1.\n                      \n                    Participant based on SingleSimResolver \n                    using either sim in career event or active sim.\n                    ',
       tunable=TunableTuple(subject=TunableEnumEntry(description='\n                            Who or what to apply this test to.\n                            ',
       tunable_type=ParticipantType,
       default=(ParticipantType.Actor)),
       tests=TunableTestSet(description='\n                            Tests used to determine if specified participant(s)\n                            should be counted.\n                            ')))))}
    MIN_COUNT_INDEX = 0
    MAX_COUNT_INDEX = 1
    SITUATION_INDEX = 2

    @classmethod
    def get_current_situation_sets(cls):
        return cls.schedule.get_entry_data(services.time_service().sim_now + create_time_span(minutes=1))

    @classmethod
    def start_situations(cls, situation_sets, resolver, sim_info, duration, additional_sim_ids, on_time, delayed_loots=None):
        weighted_options = [(entry.weight.get_multiplier(resolver), entry.situation_set) for entry in situation_sets]
        situation_set = sims4.random.weighted_random_item(weighted_options)
        return (
         situation_set.start(resolver, sim_info, duration, additional_sim_ids, on_time=on_time, delayed_loots=delayed_loots), situation_set)

    @classmethod
    def start_long_term_situation(cls, situation, start_time, stop_time, min_count, max_count, requesting_sim_info, situation_ids):
        now = services.time_service().sim_now.time_of_day()
        time_span = now.time_till_next_day_time(stop_time, rollover_same_time=True)
        duration = time_span.in_minutes()
        if requesting_sim_info is None:
            requesting_sim_id = None
        else:
            requesting_sim_id = requesting_sim_info.sim_id
        situation_manager = services.get_zone_situation_manager()
        for _ in range(random.random.randint(min_count, max_count)):
            guest_list = SituationGuestList(filter_requesting_sim_id=requesting_sim_id)
            situation_id = situation_manager.create_situation(situation, guest_list=guest_list,
              spawn_sims_during_zone_spin_up=True,
              user_facing=False,
              duration_override=duration,
              creation_source=(str(cls)))
            if situation_id is not None:
                situation_ids.append(situation_id)

    @classmethod
    def get_long_term_situation_count(cls, long_term_situation_data, resolver):
        min_count = long_term_situation_data.count.lower_bound
        max_count = long_term_situation_data.count.upper_bound
        valid_sim_infos = set()
        for count_modifier in long_term_situation_data.count_modifiers:
            for sim in resolver.get_participants(count_modifier.subject):
                test_resolver = SingleSimResolver(sim.sim_info)
                if count_modifier.tests.run_tests(test_resolver):
                    valid_sim_infos.add(sim.sim_info)

        delta = len(valid_sim_infos)
        max_count -= delta
        min_count -= delta
        if min_count < 0:
            min_count = 0
        return (min_count, max_count)

    @classmethod
    def request_new_long_term_situations(cls, time_to_start, resolver, requesting_sim_info, situation_ids):
        next_time = DATE_AND_TIME_ZERO + create_time_span(hours=24)
        for long_term_situation_data in cls.long_term_situations:
            if long_term_situation_data.start_time != time_to_start:
                if time_to_start< long_term_situation_data.start_time < next_time:
                    next_time = long_term_situation_data.start_time
                    continue
            else:
                min_count, max_count = cls.get_long_term_situation_count(long_term_situation_data, resolver)
            if max_count <= 0:
                continue
            else:
                cls.start_long_term_situation(long_term_situation_data.situation, long_term_situation_data.start_time, long_term_situation_data.stop_time, min_count, max_count, requesting_sim_info, situation_ids)

        return next_time

    @classmethod
    def get_expected_situations(cls, resolver):
        now = services.time_service().sim_now.time_of_day()
        next_time = DATE_AND_TIME_ZERO + create_time_span(hours=24)
        expected_situations = {}
        for long_term_situation_data in cls.long_term_situations:
            stop_time = long_term_situation_data.stop_time
            start_time = long_term_situation_data.start_time
            if now > stop_time:
                if stop_time != DATE_AND_TIME_ZERO:
                    continue
            if now < start_time:
                if start_time < next_time:
                    next_time = start_time
                    continue
                min_count, max_count = cls.get_long_term_situation_count(long_term_situation_data, resolver)
                if max_count <= 0:
                    continue
                else:
                    guid = long_term_situation_data.situation.guid64
                    situation_times = expected_situations.get(guid)
                    if situation_times is None:
                        situation_times = {}
                        expected_situations[guid] = situation_times
                        situation_datas = None
                    else:
                        situation_datas = situation_times.get(stop_time)
                if situation_datas is not None:
                    situation_datas[cls.MIN_COUNT_INDEX] += min_count
                    situation_datas[cls.MAX_COUNT_INDEX] += max_count
                else:
                    situation_times[stop_time] = [
                     min_count, max_count, long_term_situation_data.situation]

        return (
         expected_situations, next_time)

    @classmethod
    def request_initial_long_term_situations(cls, resolver, requesting_sim_info, existing_ids):
        requested_situations, next_time = cls.get_expected_situations(resolver)
        situation_manager = services.get_zone_situation_manager()
        now = services.time_service().sim_now.time_of_day()
        was_existing = bool(existing_ids)
        existing_situations = [situation_manager.get(uid) for uid in existing_ids if uid in situation_manager]
        existing_ids.clear()
        while existing_situations:
            situation = existing_situations.pop()
            situation_times = requested_situations.get(situation.guid64)
            if situation_times is None:
                situation_manager.destroy_situation_by_id(situation.id)
                continue
            else:
                closest_time = None
                closest_ticks = sim_ticks_per_day() * 2
                closest_situation_data = None
                for time, situation_data in situation_times.items():
                    new_ticks = abs((now + situation.get_remaining_time() - time).in_ticks())
                    if new_ticks < closest_ticks:
                        closest_ticks = new_ticks
                        closest_time = time
                        closest_situation_data = situation_data

                closest_situation_data[cls.MIN_COUNT_INDEX] -= 1
            if closest_situation_data[cls.MAX_COUNT_INDEX] == 1:
                del situation_times[closest_time]
                if not situation_times:
                    del requested_situations[situation.guid64]
                closest_situation_data[cls.MAX_COUNT_INDEX] -= 1
                situation.change_duration(now.time_till_next_day_time(closest_time).in_minutes())
                existing_ids.append(situation.id)

        for _, situation_times in requested_situations.items():
            for time, situation_data in situation_times.items():
                if was_existing:
                    if situation_data[cls.MIN_COUNT_INDEX] < 1:
                        continue
                cls.start_long_term_situation(situation_data[cls.SITUATION_INDEX], now, time, situation_data[cls.MIN_COUNT_INDEX], situation_data[cls.MIN_COUNT_INDEX] if was_existing else situation_data[cls.MAX_COUNT_INDEX], requesting_sim_info, existing_ids)

        return next_time


class WeeklyScheduleZoneDirector(CareerEventZoneDirectorMixin, ZoneDirectorBase):
    SCHEDULE_SPINUP_DELAY = 5
    SCHEDULED_SITUATION_LIST_GUID = 4213659598
    LONG_TERM_SITUATION_LIST_GUID = 1568893620
    CURRENT_HOUR_TOKEN = 'current_hour'
    CURRENT_DAY_TOKEN = 'current_day'
    SCHEDULE_GUID_TOKEN = 'schedule_guid'
    SITUATION_SET_GUID_TOKEN = 'situation_set_guid'
    INSTANCE_TUNABLES = {'scheduled_situations':TunableMapping(description='\n            Mapping of week to possible schedule of situations for that day of the week.\n            ',
       key_type=TunableEnumEntry(description='\n                Day of the week.\n                ',
       tunable_type=Days,
       default=(Days.SUNDAY)),
       value_type=TunableList(tunable=TunableTuple(weight=TunableMultiplier.TunableFactory(description='\n                        Weight for this daily schedule.\n                        '),
       schedule=WeeklyScheduleDay.TunableReference(description='\n                        A schedule for the day.\n                        ')))), 
     'allow_open_street_director':Tunable(description="\n            When set this will allow a weekly schedule zone director to start an open street \n            director. However if this is False then the open street zone director won't start up\n            and that can lead to things like seasonal conditional layers not spawning and such.\n            ",
       tunable_type=bool,
       default=False)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._long_term_situation_ids = list()
        self._situation_ids = []
        self._long_term_situation_alarm_handle = None
        self._situation_alarm_handle = None
        self._schedule = None
        self._situation_set = None
        self._current_hour = None
        self._current_day = None
        self._next_long_term_time = None
        self._delayed_loots = []

    def on_startup(self):
        super().on_startup()
        if services.current_zone().is_zone_running:
            self._on_scheduled_situation_request()
            services.sim_spawner_service().register_sim_spawned_callback(self.on_sim_spawned)

    def _update_schedule(self):
        time_of_day = services.time_service().sim_now
        day = time_of_day.day()
        if self._current_day != day:
            self._current_day = day
            if day in self.scheduled_situations:
                resolver = self._get_resolver()
                weighted_options = [(entry.weight.get_multiplier(resolver), entry.schedule) for entry in self.scheduled_situations[day]]
                self._schedule = sims4.random.weighted_random_item(weighted_options)
            else:
                self._schedule = None

    def on_shutdown(self):
        if self._situation_alarm_handle is not None:
            alarms.cancel_alarm(self._situation_alarm_handle)
            self._situation_alarm_handle = None
        if self._long_term_situation_alarm_handle is not None:
            alarms.cancel_alarm(self._long_term_situation_alarm_handle)
            self._long_term_situation_alarm_handle = None
        situation_manager = services.get_zone_situation_manager()
        for uid in itertools.chain(self._long_term_situation_ids, self._situation_ids):
            situation = situation_manager.get(uid)
            if situation:
                situation_manager.destroy_situation_by_id(situation.id)

        services.sim_spawner_service().unregister_sim_spawned_callback(self.on_sim_spawned)
        super().on_shutdown()

    @property
    def supports_open_street_director(self):
        return self.allow_open_street_director

    def _load_custom_zone_director(self, zone_director_proto, reader):
        for situation_data_proto in zone_director_proto.situations:
            if situation_data_proto.situation_list_guid == self.SCHEDULED_SITUATION_LIST_GUID:
                self._situation_ids.extend(situation_data_proto.situation_ids)
            if situation_data_proto.situation_list_guid == self.LONG_TERM_SITUATION_LIST_GUID:
                self._long_term_situation_ids.extend(situation_data_proto.situation_ids)

        self._current_hour = None
        current_hour_ticks = reader.read_uint32(self.CURRENT_HOUR_TOKEN, None)
        if current_hour_ticks is not None:
            self._current_hour = DateAndTime(current_hour_ticks)
        else:
            self._current_hour = None
        self._current_day = reader.read_uint32(self.CURRENT_DAY_TOKEN, None)
        schedule_guid = reader.read_uint64(self.SCHEDULE_GUID_TOKEN, None)
        if schedule_guid:
            self._schedule = services.get_instance_manager(sims4.resources.Types.SNIPPET).get(schedule_guid)
            _, current_hour, _ = self._schedule.get_current_situation_sets()
            if current_hour != self._current_hour:
                self._situation_ids.clear()
            else:
                situation_set_guid = reader.read_uint64(self.SITUATION_SET_GUID_TOKEN, None)
                if situation_set_guid:
                    self._situation_set = services.get_instance_manager(sims4.resources.Types.SNIPPET).get(situation_set_guid)
        super()._load_custom_zone_director(zone_director_proto, reader)

    def _save_custom_zone_director(self, zone_director_proto, writer):
        if self._current_hour is not None:
            writer.write_uint32(self.CURRENT_HOUR_TOKEN, self._current_hour)
        if self._current_day is not None:
            writer.write_uint32(self.CURRENT_DAY_TOKEN, self._current_day)
        if self._schedule is not None:
            writer.write_uint64(self.SCHEDULE_GUID_TOKEN, self._schedule.guid64)
        if self._situation_set is not None:
            writer.write_uint64(self.SITUATION_SET_GUID_TOKEN, self._situation_set.guid64)
        situation_data_proto = zone_director_proto.situations.add()
        situation_data_proto.situation_list_guid = self.SCHEDULED_SITUATION_LIST_GUID
        situation_data_proto.situation_ids.extend(self._prune_stale_situations(self._situation_ids))
        long_term_data_proto = zone_director_proto.situations.add()
        long_term_data_proto.situation_list_guid = self.LONG_TERM_SITUATION_LIST_GUID
        long_term_data_proto.situation_ids.extend(self._prune_stale_situations(self._long_term_situation_ids))
        super()._save_custom_zone_director(zone_director_proto, writer)

    def _get_resolver(self):
        sim_info = self._get_relevant_sim_info()
        if sim_info is not None:
            return SingleSimResolver(sim_info)
        return GlobalResolver()

    def _get_relevant_sim_info(self):
        for career_event in self._career_events:
            career_sim_info = career_event.sim_info
            if career_sim_info:
                return career_sim_info

        client = services.client_manager().get_first_client()
        if client is not None:
            return client.active_sim_info

    def _on_scheduled_situation_request(self, *_, delayed_loots=None, **__):
        self._situation_ids = self._prune_stale_situations(self._situation_ids)
        self._update_schedule()
        now = services.time_service().sim_now
        if self._schedule is None:
            time_span = create_date_and_time(days=1) - now.time_of_day()
            self._situation_alarm_handle = alarms.add_alarm(self, time_span, self._on_scheduled_situation_request)
            self._situation_set = None
            return
        situation_sets, current_hour, next_hour = self._schedule.get_current_situation_sets()
        time_span = now.time_till_next_day_time(next_hour, rollover_same_time=True)
        self._situation_alarm_handle = alarms.add_alarm(self, time_span, self._on_scheduled_situation_request)
        if self._situation_ids:
            if current_hour == self._current_hour:
                return
        self._current_hour = current_hour
        if not situation_sets:
            self._situation_ids.clear()
            self._situation_set = None
            return
        on_time = abs((now.time_of_day() - current_hour).in_minutes()) < 1
        self._situation_ids, self._situation_set = self._schedule.start_situations(situation_sets, (self._get_resolver()),
          (self._get_relevant_sim_info()),
          (time_span.in_minutes()),
          (set((career_event.sim_info.sim_id for career_event in self._career_events if career_event.sim_info is not None))),
          on_time,
          delayed_loots=delayed_loots)

    def _decide_whether_to_load_zone_situation_seed(self, seed):
        if not super()._decide_whether_to_load_zone_situation_seed(seed):
            return False
        if not self._is_career_event_seed(seed):
            if seed.situation_id in self._situation_ids or seed.situation_id in self._long_term_situation_ids:
                return True
            return False

    def _decide_whether_to_load_open_street_situation_seed(self, seed):
        return False

    def _request_long_term_situations(self, *_, **__):
        self._long_term_situation_ids = self._prune_stale_situations(self._long_term_situation_ids)
        self._update_schedule()
        now = services.time_service().sim_now
        if self._schedule is None:
            time_span = create_date_and_time(days=1) - now.time_of_day()
            self._long_term_situation_alarm_handle = alarms.add_alarm(self, time_span, self._request_long_term_situations)
            return
        if self._next_long_term_time is None:
            self._next_long_term_time = self._schedule.request_initial_long_term_situations(self._get_resolver(), self._get_relevant_sim_info(), self._long_term_situation_ids)
        else:
            self._next_long_term_time = self._schedule.request_new_long_term_situations(self._next_long_term_time.time_of_day(), self._get_resolver(), self._get_relevant_sim_info(), self._long_term_situation_ids)
        time_span = now.time_till_next_day_time((self._next_long_term_time), rollover_same_time=True)
        self._long_term_situation_alarm_handle = alarms.add_alarm(self, time_span, self._request_long_term_situations)

    def transfer_from_zone_director(self, zone_director):
        if isinstance(zone_director, WeeklyScheduleZoneDirector):
            self._long_term_situation_ids = zone_director._long_term_situation_ids.copy()
            zone_director._long_term_situation_ids.clear()

    def create_situations_during_zone_spin_up(self):
        self._request_long_term_situations()
        return super().create_situations_during_zone_spin_up()

    def create_situations(self):
        self._request_long_term_situations()
        return super().create_situations()

    def on_spawn_sim_for_zone_spin_up_completed(self):
        super().on_spawn_sim_for_zone_spin_up_completed()
        self._delayed_loots = []
        self._on_scheduled_situation_request(delayed_loots=(self._delayed_loots))
        services.sim_spawner_service().register_sim_spawned_callback(self.on_sim_spawned)

    def on_bouncer_assigned_all_sims_during_zone_spin_up(self):
        resolver = self._get_resolver()
        for delayed_loot in self._delayed_loots:
            delayed_loot.apply_to_resolver(resolver)

    def on_sim_spawned(self, sim):
        if self._situation_set:
            if sim.is_selectable:
                time_span = self._situation_alarm_handle.get_remaining_time()
                self._situation_ids.extend(self._situation_set.start((self._get_resolver()), (self._get_relevant_sim_info()),
                  (time_span.in_minutes()),
                  (set((career_event.sim_info.sim_id for career_event in self._career_events if career_event.sim_info is not None))),
                  sims={
                 sim},
                  start=False))