# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\bouncer\bouncer_client.py
# Compiled at: 2013-07-05 18:27:35
# Size of source mod 2**32: 2216 bytes


class IBouncerClient:

    def on_sim_assigned_to_request(self, sim, request):
        raise NotImplementedError

    def on_sim_unassigned_from_request(self, sim, request):
        raise NotImplementedError

    def on_sim_replaced_in_request(self, old_sim, new_sim, request):
        raise NotImplementedError

    def on_failed_to_spawn_sim_for_request(self, request):
        raise NotImplementedError

    def on_tardy_request(self, request):
        raise NotImplementedError

    def on_first_assignment_pass_completed(self):
        raise NotImplementedError