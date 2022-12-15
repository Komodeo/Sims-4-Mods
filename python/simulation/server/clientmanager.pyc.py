# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server\clientmanager.py
# Compiled at: 2015-08-20 15:14:28
# Size of source mod 2**32: 1975 bytes
from objects.object_manager import DistributableObjectManager
from server.client import Client

class ClientManager(DistributableObjectManager):

    def create_client(self, client_id, account, household_id):
        new_client = Client(client_id, account, household_id)
        self.add(new_client)
        return new_client

    def get_client_by_household(self, household):
        for client in self._objects.values():
            if client.household is household:
                return client

    def get_client_by_household_id(self, household_id):
        for client in self._objects.values():
            if client.household_id == household_id:
                return client

    def get_client_by_account(self, account_id):
        for client in self._objects.values():
            if client.account.id == account_id:
                return client

    def get_first_client(self):
        for client in self._objects.values():
            return client

    def get_first_client_id(self):
        for client in self._objects.values():
            return client.id