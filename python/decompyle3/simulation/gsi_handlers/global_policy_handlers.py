# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\global_policy_handlers.py
# Compiled at: 2019-01-10 15:00:34
# Size of source mod 2**32: 1424 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
import services
global_policy_archive_schema = GsiGridSchema(label='Global Policy Log', auto_refresh=True)
global_policy_archive_schema.add_field('policy', label='Global Policy')
global_policy_archive_schema.add_field('progress_value', label='Progress Value')
global_policy_archive_schema.add_field('decay_days', label='Decay Days')
global_policy_archive_schema.add_field('progress_state', label='Progress State')

@GsiHandler('global_policy_log', global_policy_archive_schema)
def generate_global_policy_data():
    policy_data = []
    for policy in services.global_policy_service().get_global_policies():
        entry = {'policy':repr(policy).split('sims4.tuning.instances.', 1)[1].split('object', 1)[0], 
         'progress_value':str(policy.progress_value) + '/' + str(policy.progress_max_value), 
         'decay_days':0 if policy.decay_handler is None or policy.decay_handler.when is None else str(policy.decay_handler.when - services.time_service().sim_now), 
         'progress_state':str(policy.progress_state)}
        policy_data.append(entry)

    return policy_data