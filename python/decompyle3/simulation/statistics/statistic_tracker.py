# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_tracker.py
# Compiled at: 2020-10-24 15:33:02
# Size of source mod 2**32: 6681 bytes
from protocolbuffers import SimObjectAttributes_pb2 as protocols
import services, sims, sims4.log, statistics.base_statistic_tracker
from sims.sim_info_lod import SimInfoLODLevel
logger = sims4.log.Logger('Statistic')

class StatisticTracker(statistics.base_statistic_tracker.BaseStatisticTracker):
    __slots__ = '_monetary_value_statistics'

    def __init__(self, owner=None):
        super().__init__(owner)
        self._monetary_value_statistics = []

    def save(self):
        self.check_for_unneeded_initial_statistics()
        save_list = []
        if self._statistics is not None:
            for stat_type, stat in self._statistics.items():
                if stat_type.persisted:
                    try:
                        statistic_data = protocols.Statistic()
                        statistic_data.name_hash = stat_type.guid64
                        if stat is not None:
                            statistic_data.value = stat.get_saved_value()
                        else:
                            statistic_data.ClearField('value')
                        save_list.append(statistic_data)
                    except Exception as e:
                        try:
                            logger.exception('Exception {} thrown while trying to save stat {}', e, stat, owner='rez')
                        finally:
                            e = None
                            del e

        return save_list

    def load(self, statistics, skip_load=False):
        try:
            statistics_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
            owner_lod = self._owner.lod if isinstance(self._owner, sims.sim_info.SimInfo) else None
            for statistics_data in statistics:
                stat_cls = statistics_manager.get(statistics_data.name_hash)
                if stat_cls is not None:
                    if not self._should_add_commodity_from_gallery(stat_cls, skip_load):
                        continue
                    if not stat_cls.persisted:
                        continue
                    if self.statistics_to_skip_load is not None:
                        if stat_cls in self.statistics_to_skip_load:
                            continue
                    if owner_lod is not None and owner_lod < stat_cls.min_lod_value:
                        if stat_cls.min_lod_value == SimInfoLODLevel.ACTIVE:
                            if self._delayed_active_lod_statistics is None:
                                self._delayed_active_lod_statistics = list()
                            else:
                                self._delayed_active_lod_statistics.append((statistics_data.name_hash, statistics_data.value))
                            continue
                        if statistics_data.HasField('value'):
                            self.set_value(stat_cls, (statistics_data.value), from_load=True)
                        else:
                            if self._statistics is None:
                                self._statistics = {}
                            if stat_cls not in self._statistics:
                                self._statistics[stat_cls] = None
                    else:
                        logger.info('Trying to load unavailable STATISTIC resource: {}', statistics_data.name_hash)

        finally:
            self.statistics_to_skip_load = None

        self.check_for_unneeded_initial_statistics()

    def add_statistic(self, stat_type, **kwargs):
        stat = (super().add_statistic)(stat_type, **kwargs)
        if stat is not None:
            if stat.apply_value_to_object_cost:
                if stat not in self._monetary_value_statistics:
                    self._monetary_value_statistics.append(stat)
        return stat

    def remove_statistic(self, stat_type, on_destroy=False):
        if self.has_statistic(stat_type):
            stat = self._statistics[stat_type]
            if stat is not None:
                if stat.apply_value_to_object_cost:
                    if stat in self._monetary_value_statistics:
                        self._monetary_value_statistics.remove(stat)
        super().remove_statistic(stat_type, on_destroy)

    def get_monetary_value_statistics(self):
        return self._monetary_value_statistics