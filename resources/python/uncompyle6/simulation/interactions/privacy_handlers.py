# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\privacy_handlers.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 7548 bytes
import services, gsi_handlers, weakref, sims4
from timeit import itertools
from routing import FootprintType
from gsi_handlers.gsi_utils import parse_filter_to_list
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
ACTIVE_FILTER = 'Is Active'
HAS_VIOLATORS_FILTER = 'Has Current Violators'
NO_VIOLATORS_STR = 'No Current Violators'
privacy_management_schema = GsiGridSchema(label='Privacy Management')
privacy_management_schema.add_field('is_active', label='Is Active', width=0.02)
privacy_management_schema.add_field('privacy_interaction', label='Privacy Interaction', width=0.05)
privacy_management_schema.add_field('sim_violators', label='Current Sim Violators', width=0.05)
privacy_management_schema.add_field('vehicle_violators', label='Current Vehicle Violators', width=0.05)
privacy_management_schema.add_field('late_violators', label='Late Privacy Violators', width=0.05)
privacy_management_schema.add_field('all_past_violators', label='All Past Instance Violators', width=0.055)
privacy_management_schema.add_field('privacy_violators', label='Privacy Violators', width=0.05)
privacy_management_schema.add_field('central_object', label='Central Object', width=0.05)
privacy_management_schema.add_field('has_shooed', label='Has Shooed', width=0.03)
privacy_management_schema.add_field('max_los', label='Max Line of Sight Radius', width=0.05)
privacy_management_schema.add_field('shoo_cons', label='Shoo Constraint Radius', width=0.05)
privacy_management_schema.add_field('privacy_discouragement_cost', label='Privacy Discouragement Cost', width=0.055)
with privacy_management_schema.add_has_many('privacy_constraints', GsiGridSchema, label='Constraints') as (sub_schema):
    sub_schema.add_field('cost', label='Cost')
    sub_schema.add_field('enabled', label='Enabled')
    sub_schema.add_field('footprint_id', label='Footprint Id')
    sub_schema.add_field('footprint_type', label='Footprint Type')
    sub_schema.add_field('polygon', label='Polygon')
with privacy_management_schema.add_has_many('affordances', GsiGridSchema, label='Affordances') as (sub_schema):
    sub_schema.add_field('embarrassed_affordance', label='Embarrassed Affordance')
    sub_schema.add_field('post_route_affordance', label='Post Route Affordance')
with privacy_management_schema.add_has_many('allowed', GsiGridSchema, label='Allowed/Exempt Sims') as (sub_schema):
    sub_schema.add_field('allowed_sims', label='Allowed Sims')
    sub_schema.add_field('disallowed_sims', label='Disallowed Sims')
    sub_schema.add_field('exempt_sims', label='Sims Exempt From Shooing')
privacy_management_schema.add_filter(ACTIVE_FILTER)
privacy_management_schema.add_filter(HAS_VIOLATORS_FILTER)
with sims4.reload.protected(globals()):
    privacy_instance_to_violators = weakref.WeakKeyDictionary()

@GsiHandler('privacy_management', privacy_management_schema)
def generate_privacy_management_data(filter=None):
    privacy_management_data = []
    active_instances = []
    filter_list = parse_filter_to_list(filter)
    privacy_service = services.privacy_service()
    if privacy_service is None:
        return privacy_management_data
    for instance in privacy_service._privacy_instances:
        if instance.is_active:
            active_instances.append(instance)
        if not filter_list is None:
            if ACTIVE_FILTER not in filter_list:
                if instance.is_active:
                    continue
            if filter_list is not None:
                if HAS_VIOLATORS_FILTER in filter_list:
                    if not instance.find_violating_vehicles():
                        if not instance.find_violating_sims():
                            if not instance._late_violators:
                                continue
            entry = {'is_active':str(instance.is_active), 
             'max_los':str(instance._max_line_of_sight_radius), 
             'has_shooed':str(instance.has_shooed), 
             'privacy_violators':str(instance.privacy_violators), 
             'privacy_discouragement_cost':str(instance.privacy_discouragement_cost), 
             'privacy_interaction':str(instance._interaction), 
             'central_object':str(instance.central_object), 
             'shoo_cons':str(instance._shoo_constraint_radius or instance._SHOO_CONSTRAINT_RADIUS), 
             'affordances':{'embarrassed_affordance':str(instance._embarrassed_affordance or instance._EMBARRASSED_AFFORDANCE), 
              'post_route_affordance':str(instance._post_route_affordance)}, 
             'allowed':{'allowed_sims':gsi_handlers.gsi_utils.format_object_list_names(instance._allowed_sims) if instance._allowed_sims else 'None', 
              'disallowed_sims':gsi_handlers.gsi_utils.format_object_list_names(instance._disallowed_sims) if instance._disallowed_sims else 'None', 
              'exempt_sims':gsi_handlers.gsi_utils.format_object_list_names(instance._exempt_sims) if instance._exempt_sims else 'None'}, 
             'privacy_constraints':[]}
            populate_violators(entry, instance, active_instances)
            for constraint in instance._privacy_constraints:
                constraint_type = next((constraint_type for constraint_type, value in vars(FootprintType).items() if value == constraint.footprint_type))
                entry['privacy_constraints'].append({'cost':str(constraint.cost),  'enabled':str(constraint.enabled), 
                 'footprint_id':str(constraint.footprint_id), 
                 'footprint_type':str(constraint_type), 
                 'polygon':str(constraint.polygon)})

            privacy_management_data.append(entry)

    return privacy_management_data


def populate_violators(entry, instance, active_instances):
    global privacy_instance_to_violators
    entry['sim_violators'] = gsi_handlers.gsi_utils.format_object_list_names(instance.find_violating_sims()) if instance.find_violating_sims() else NO_VIOLATORS_STR
    entry['late_violators'] = gsi_handlers.gsi_utils.format_object_list_names(instance._late_violators) if instance._late_violators else NO_VIOLATORS_STR
    entry['vehicle_violators'] = gsi_handlers.gsi_utils.format_object_list_names(instance.find_violating_vehicles()) if instance.find_violating_vehicles() else NO_VIOLATORS_STR
    for violator in itertools.chain(instance.find_violating_sims(), instance.find_violating_vehicles(), instance._late_violators):
        if privacy_instance_to_violators and instance in privacy_instance_to_violators:
            if str(violator) not in privacy_instance_to_violators[instance]:
                privacy_instance_to_violators[instance].append(str(violator))
        else:
            privacy_instance_to_violators.update({instance: [str(violator)]})

    for key, value in privacy_instance_to_violators.items():
        if key is instance:
            entry['all_past_violators'] = [str(violator) for violator in value]
            break
    else:
        entry['all_past_violators'] = NO_VIOLATORS_STR

    privacy_instance_to_violators = {instance:violators for instance, violators in privacy_instance_to_violators.items() if instance in active_instances}