# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\aging\aging_service.py
# Compiled at: 2022-07-28 19:35:21
# Size of source mod 2**32: 5872 bytes
from protocolbuffers import GameplaySaveData_pb2
from sims.aging.aging_enums import AgeSpeeds
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_types import Species
from sims4.service_manager import Service
import enum, game_services, services
game_play_options_enums = GameplaySaveData_pb2.GameplayOptions

class PlayedHouseholdSimAgingOptions(enum.Int, export=False):
    DISABLED = ...
    ALL_PLAYED = ...
    ACTIVE_FAMILY_ONLY = ...

    @classmethod
    def convert_protocol_option_to_aging_option(cls, option_allow_aging):
        if option_allow_aging == game_play_options_enums.DISABLED:
            return cls.DISABLED
        if option_allow_aging == game_play_options_enums.ENABLED:
            return cls.ALL_PLAYED
        if option_allow_aging == game_play_options_enums.FOR_ACTIVE_FAMILY:
            return cls.ACTIVE_FAMILY_ONLY

    @classmethod
    def convert_aging_option_to_protocol_option(cls, aging_option):
        if aging_option == cls.DISABLED:
            return game_play_options_enums.DISABLED
        if aging_option == cls.ALL_PLAYED:
            return game_play_options_enums.ENABLED
        if aging_option == cls.ACTIVE_FAMILY_ONLY:
            return game_play_options_enums.FOR_ACTIVE_FAMILY


class AgingService(Service):

    def __init__(self):
        self._aging_speed = AgeSpeeds.NORMAL
        self._played_household_aging_option = PlayedHouseholdSimAgingOptions.ACTIVE_FAMILY_ONLY
        self._unplayed_aging_enabled = False
        self._species_aging_enabled = {}

    @property
    def aging_speed(self):
        return self._aging_speed

    def set_unplayed_aging_enabled(self, enabled_option):
        self._unplayed_aging_enabled = enabled_option
        services.sim_info_manager().set_aging_enabled_on_all_sims(self.is_aging_enabled_for_sim_info)

    def set_aging_enabled(self, enabled_option):
        self._played_household_aging_option = PlayedHouseholdSimAgingOptions(enabled_option)
        services.sim_info_manager().set_aging_enabled_on_all_sims(self.is_aging_enabled_for_sim_info)

    def set_species_aging_enabled(self, species, enabled_option):
        self._species_aging_enabled[species] = enabled_option
        services.sim_info_manager().set_aging_enabled_on_all_sims(self.is_aging_enabled_for_sim_info)

    def is_aging_enabled_for_sim_info(self, sim_info):
        if sim_info.household is None:
            return False
        if sim_info.lod == SimInfoLODLevel.MINIMUM:
            return False
        enabled = self._species_aging_enabled.get(sim_info.species)
        if enabled is not None:
            return enabled
        if not sim_info.is_played_sim:
            return self._unplayed_aging_enabled
        if self._played_household_aging_option == PlayedHouseholdSimAgingOptions.ACTIVE_FAMILY_ONLY:
            return not sim_info.is_npc
        return self._played_household_aging_option == PlayedHouseholdSimAgingOptions.ALL_PLAYED

    def set_aging_speed(self, speed: AgeSpeeds):
        self._aging_speed = speed
        services.sim_info_manager().set_aging_speed_on_all_sims(self._aging_speed)

    def save_options(self, options_proto):
        options_proto.sim_life_span = self._aging_speed
        options_proto.allow_aging = PlayedHouseholdSimAgingOptions.convert_aging_option_to_protocol_option(self._played_household_aging_option)
        options_proto.unplayed_aging_enabled = self._unplayed_aging_enabled

    def load_options(self, options_proto):
        if game_services.service_manager.is_traveling:
            return
        self._aging_speed = AgeSpeeds(options_proto.sim_life_span)
        self._played_household_aging_option = PlayedHouseholdSimAgingOptions.convert_protocol_option_to_aging_option(options_proto.allow_aging)
        self._unplayed_aging_enabled = options_proto.unplayed_aging_enabled
        self._species_aging_enabled[Species.FOX] = options_proto.creature_aging_enabled

    def on_all_households_and_sim_infos_loaded(self, client):
        services.sim_info_manager().set_aging_enabled_on_all_sims((self.is_aging_enabled_for_sim_info), update_callbacks=False)
        services.sim_info_manager().set_aging_speed_on_all_sims(self._aging_speed)