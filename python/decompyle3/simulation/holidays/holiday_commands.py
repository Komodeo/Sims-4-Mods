# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\holidays\holiday_commands.py
# Compiled at: 2018-03-22 15:30:43
# Size of source mod 2**32: 2819 bytes
from protocolbuffers import GameplaySaveData_pb2, DistributorOps_pb2
from google.protobuf import text_format
from seasons.seasons_enums import SeasonType
from server_commands.argument_helpers import TunableInstanceParam, OptionalSimInfoParam, get_optional_target
import services, sims4.commands

@sims4.commands.Command('holiday.get_holiday_data', command_type=(sims4.commands.CommandType.Live))
def get_holiday_data(holiday_id: int, _connection=None):
    holiday_service = services.holiday_service()
    if holiday_service is None:
        return
    holiday_service.send_holiday_info_message(holiday_id)


@sims4.commands.Command('holiday.get_active_holiday_data', command_type=(sims4.commands.CommandType.Live))
def get_active_holiday_data(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('Failed to find SimInfo.')
        return
    sim_info.household.holiday_tracker.send_active_holiday_info_message(DistributorOps_pb2.SendActiveHolidayInfo.START)


@sims4.commands.Command('holiday.update_holiday', command_type=(sims4.commands.CommandType.Live))
def update_holiday(holiday_data: str, _connection=None):
    holiday_service = services.holiday_service()
    if holiday_service is None:
        return
    proto = GameplaySaveData_pb2.Holiday()
    text_format.Merge(holiday_data, proto)
    holiday_service.modify_holiday(proto)


@sims4.commands.Command('holiday.add_holiday', command_type=(sims4.commands.CommandType.Live))
def add_holiday(holiday_data: str, season: SeasonType, day: int, _connection=None):
    holiday_service = services.holiday_service()
    if holiday_service is None:
        return
    proto = GameplaySaveData_pb2.Holiday()
    text_format.Merge(holiday_data, proto)
    holiday_service.add_a_holiday(proto, season, day)


@sims4.commands.Command('holiday.remove_holiday', command_type=(sims4.commands.CommandType.Live))
def remove_holiday(holiday_id: int, _connection=None):
    holiday_service = services.holiday_service()
    if holiday_service is None:
        return
    holiday_service.remove_a_holiday(holiday_id)