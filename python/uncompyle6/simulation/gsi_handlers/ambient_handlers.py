# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\ambient_handlers.py
# Compiled at: 2016-10-19 17:36:30
# Size of source mod 2**32: 798 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema
ambient_archive_schema = GsiGridSchema(label='Situations/Ambient Log')
ambient_archive_schema.add_field('sources', label='Sources')
ambient_archive_schema.add_field('created_situation', label='Created Situation')
archiver = GameplayArchiver('ambient', ambient_archive_schema)

def archive_ambient_data(description, created_situation=''):
    entry = {}
    entry['sources'] = description
    entry['created_situation'] = created_situation
    archiver.archive(data=entry)