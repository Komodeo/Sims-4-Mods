# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\high_school_graduation\graduation_handlers.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 1665 bytes
import services
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
graduate_service_schema = GsiGridSchema(label='Graduate Service', sim_specific=False)
graduate_service_schema.add_field('sim_id', label='Sim ID', unique_field=True)
graduate_service_schema.add_field('sim_first_name', label='Sim First Name')
graduate_service_schema.add_field('sim_last_name', label='Sim Last Name')
graduate_service_schema.add_field('current_graduation', label='Current Graduation')
graduate_service_schema.add_field('valedictorian', label='Is Valedictorian')
graduate_service_schema.add_field('waiting_valedictorian', label='Waiting Valedictorian')

@GsiHandler('graduation_service', graduate_service_schema)
def generate_graduation_service_view_data(sim_id: int=None):
    grad_service = services.get_graduation_service()
    if grad_service is None:
        return []
    all_grads = []
    for sim_info in grad_service.graduating_sims_gen():
        graduate_data = {}
        graduate_data['sim_id'] = sim_info.id
        graduate_data['sim_first_name'] = sim_info.first_name
        graduate_data['sim_last_name'] = sim_info.last_name
        graduate_data['current_graduation'] = grad_service.is_sim_info_graduating(sim_info)
        graduate_data['valedictorian'] = grad_service.is_current_valedictorian(sim_info)
        graduate_data['waiting_valedictorian'] = grad_service.is_waiting_valedictorian(sim_info)
        all_grads.append(graduate_data)

    return all_grads