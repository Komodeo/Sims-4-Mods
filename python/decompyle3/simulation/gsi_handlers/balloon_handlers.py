# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\balloon_handlers.py
# Compiled at: 2019-05-24 13:25:04
# Size of source mod 2**32: 2422 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
balloon_archive_schema = GsiGridSchema(label='Balloons', sim_specific=True)
balloon_archive_schema.add_field('sim', label='Sim', width=2)
balloon_archive_schema.add_field('interaction', label='Interaction', width=2)
balloon_archive_schema.add_field('balloon_type', label='Type', width=2)
balloon_archive_schema.add_field('icon', label='Icon', width=2)
balloon_archive_schema.add_field('balloon_category', label='Category', width=2)
balloon_archive_schema.add_field('weight', label='Weight', type=(GsiFieldVisualizers.INT), width=1)
balloon_archive_schema.add_field('total_weight', label='Total Weight', type=(GsiFieldVisualizers.INT), width=1)
with balloon_archive_schema.add_has_many('Considered', GsiGridSchema) as sub_schema:
    sub_schema.add_field('test_result', label='Test Result', width=2)
    sub_schema.add_field('balloon_type', label='Type', width=2)
    sub_schema.add_field('icon', label='Icon', width=2)
    sub_schema.add_field('weight', label='Weight', type=(GsiFieldVisualizers.INT), width=1)
    sub_schema.add_field('balloon_category', label='Category', width=2)
archiver = GameplayArchiver('balloon', balloon_archive_schema)

def archive_balloon_data(balloon_object, interaction, result, icon, entries):
    if not balloon_object.is_sim:
        return
    if result is not None:
        weight = result.weight
        balloon_type = str(result.balloon_type)
        gsi_category = result.gsi_category
    else:
        weight = 0
        balloon_type = 'None'
        gsi_category = 'None'
    entry = {}
    entry['sim'] = str(balloon_object)
    entry['interaction'] = str(interaction)
    entry['weight'] = weight
    entry['balloon_type'] = balloon_type
    entry['icon'] = str(icon)
    entry['balloon_category'] = gsi_category
    entry['total_weight'] = sum((entry['weight'] for entry in entries))
    entry['Considered'] = entries
    archiver.archive(data=entry, object_id=(balloon_object.id))