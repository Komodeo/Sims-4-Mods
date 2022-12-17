# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\body_type_level\body_type_level_tracker.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 8199 bytes
import alarms, services, sims4
from cas.cas import change_bodytype_level
from date_and_time import create_time_span
from sims.body_type_level.body_type_level_commodity import BODY_TYPE_TO_LEVEL_COMMODITY
from sims.body_type_level.hair_growth_flags import HairGrowthFlags, HAIR_GROWTH_TO_BODY_TYPE
from sims.outfits.outfit_enums import BodyType
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.common import Pack
from sims4.tuning.tunable import Tunable
from sims4.utils import classproperty
from statistics.statistic_enums import StatisticLockAction
logger = sims4.log.Logger('BodyTypeLevelTracker', default_owner='skorman')

class BodyTypeLevelTracker(SimInfoTracker):
    COLLECT_REQUESTS_MINUTES = Tunable(description='\n        The number of in-game minutes to wait before sending pending body type \n        level change requests after receiving the first one. This is a \n        performance optimization so client can process multiple requests at the \n        same time.\n        ',
      tunable_type=float,
      default=0.5)

    def __init__(self, sim_info):
        self._sim_info = sim_info
        self._pending_requests = None
        self._send_pending_requests_alarm_handle = None

    @classproperty
    def required_packs(cls):
        return (
         Pack.EP12,)

    def request_client_level_change(self, body_type, new_level):
        request = {body_type: new_level}
        if self._pending_requests is None:
            self._pending_requests = request
            self._send_pending_requests_alarm_handle = alarms.add_alarm(self, create_time_span(minutes=(self.COLLECT_REQUESTS_MINUTES)),
              (lambda _: self._send_body_type_level_update()
),
              cross_zone=True)
        else:
            self._pending_requests.update(request)

    def _send_body_type_level_update(self):
        change_bodytype_level(self._sim_info._base, self._pending_requests)
        self._sim_info.resend_current_occult_types()
        self._sim_info.resend_physical_attributes()
        self._pending_requests = None
        self._send_pending_requests_alarm_handle = None

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.ACTIVE

    def on_lod_update(self, old_lod, new_lod):
        if new_lod < self._tracker_lod_threshold:
            for body_type, level_commodity_type in BODY_TYPE_TO_LEVEL_COMMODITY.items():
                reason = 'locked in body_type_level_tracker.py:on_lod_update at {}'.format(services.time_service().sim_now)
                self._sim_info.lock_statistic(level_commodity_type, StatisticLockAction.DO_NOT_CHANGE_VALUE, reason)

        else:
            if old_lod < self._tracker_lod_threshold:
                acne_stat_type = BODY_TYPE_TO_LEVEL_COMMODITY.get(BodyType.SKINDETAIL_ACNE_PUBERTY)
                acne_stat = self._sim_info.get_statistic(acne_stat_type)
                if self._sim_info.is_in_locked_commodities(acne_stat):
                    reason = 'unlocked in body_type_level_tracker.py:on_lod_update at {}'.format(services.time_service().sim_now)
                    self._sim_info.unlock_statistic(acne_stat_type, reason)
                self.refresh_hair_growth_commodities()

    def set_acne_enabled(self, is_enabled):
        acne_stat_type = BODY_TYPE_TO_LEVEL_COMMODITY.get(BodyType.SKINDETAIL_ACNE_PUBERTY)
        if acne_stat_type is None:
            logger.error('Failed to set acne enabled. No matching BodyTypeLevelCommodity found.')
        acne_stat = self._sim_info.get_statistic(acne_stat_type)
        if is_enabled:
            if self._sim_info.is_in_locked_commodities(acne_stat):
                reason = f"unlocked in body_type_level_tracker.py:set_acne_enabled at {services.time_service().sim_now}"
                self._sim_info.unlock_statistic(acne_stat_type, reason)
        else:
            reason = f"locked in body_type_level_tracker.py:set_acne_enabled at {services.time_service().sim_now}"
            self._sim_info.lock_statistic(acne_stat_type, StatisticLockAction.USE_MIN_VALUE_TUNING, reason)

    def refresh_hair_growth_commodities(self):
        active_growth_flags = HairGrowthFlags.ALL & self._sim_info.flags
        growth_enabled_body_types = [body_type for growth_flag, body_type in HAIR_GROWTH_TO_BODY_TYPE.items() if active_growth_flags & growth_flag]
        potential_hair_growth_body_types = HAIR_GROWTH_TO_BODY_TYPE.values()
        for body_type, level_commodity_type in BODY_TYPE_TO_LEVEL_COMMODITY.items():
            if body_type not in potential_hair_growth_body_types:
                continue
            else:
                stat = self._sim_info.get_statistic(level_commodity_type)
                if body_type in growth_enabled_body_types:
                    if self._sim_info.is_in_locked_commodities(stat):
                        reason = f"unlocked by body_type_level_tracker.py: refresh_hair_growth_commodities at {services.time_service().sim_now}"
                        self._sim_info.unlock_statistic(level_commodity_type, reason)
                else:
                    reason = f"locked by body_type_level_tracker.py: refresh_hair_growth_commodities at {services.time_service().sim_now}"
                    self._sim_info.lock_statistic(level_commodity_type, StatisticLockAction.DO_NOT_CHANGE_VALUE, reason)
                level = self._sim_info._base.get_current_growth_level(body_type)
                stat.set_level(level)

    def on_zone_load(self):
        self.refresh_hair_growth_commodities()

    def on_zone_unload(self):
        if self._pending_requests is not None:
            self._send_body_type_level_update()