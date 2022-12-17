# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\distributor\distributor_service.py
# Compiled at: 2014-06-09 00:06:26
# Size of source mod 2**32: 951 bytes
from sims4.service_manager import Service
import distributor.system

class DistributorService(Service):

    def start(self):
        import animation.arb
        animation.arb.set_tag_functions(distributor.system.get_next_tag_id, distributor.system.get_current_tag_set)
        distributor.system._distributor_instance = distributor.system.Distributor()

    def stop(self):
        distributor.system._distributor_instance = None

    def on_tick(self):
        distributor.system._distributor_instance.process()