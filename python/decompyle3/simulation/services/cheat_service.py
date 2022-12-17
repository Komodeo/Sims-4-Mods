# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\cheat_service.py
# Compiled at: 2020-06-08 13:31:54
# Size of source mod 2**32: 3072 bytes
from protocolbuffers import Consts_pb2, Sims_pb2
from sims4.service_manager import Service
from sims4.utils import classproperty
import persistence_error_types, services

class CheatService(Service):

    def __init__(self):
        self.cheats_enabled = False
        self.cheats_ever_enabled = False

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_CHEAT_SERVICE

    def enable_cheats(self):
        self.cheats_enabled = True
        self.cheats_ever_enabled = True

    def disable_cheats(self):
        self.cheats_enabled = False

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        account_data_msg = services.get_persistence_service().get_account_proto_buff()
        gameplay_account_data = account_data_msg.gameplay_account_data
        if hasattr(gameplay_account_data, 'cheats_enabled'):
            gameplay_account_data.cheats_enabled = self.cheats_enabled
            gameplay_account_data.cheats_ever_enabled = self.cheats_ever_enabled

    def load(self, zone_data=None):
        account_data_msg = services.get_persistence_service().get_account_proto_buff()
        gameplay_account_data = account_data_msg.gameplay_account_data
        if gameplay_account_data is not None:
            if hasattr(gameplay_account_data, 'cheats_enabled'):
                self.cheats_enabled = gameplay_account_data.cheats_enabled
                self.cheats_ever_enabled = gameplay_account_data.cheats_ever_enabled

    def send_to_client(self, client):
        if hasattr(Sims_pb2, 'CheatStatusUpdate'):
            cheat_status_update = Sims_pb2.CheatStatusUpdate()
            cheat_status_update.cheats_enabled = self.cheats_enabled
            client.send_message(Consts_pb2.MSG_SET_CHEAT_STATUS, cheat_status_update)