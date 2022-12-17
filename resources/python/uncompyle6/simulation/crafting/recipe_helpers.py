# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\recipe_helpers.py
# Compiled at: 2022-02-09 10:21:47
# Size of source mod 2**32: 642 bytes
from _collections import defaultdict
import services, sims4
with sims4.reload.protected(globals()):
    RECIPE_TAG_TO_TUNING_ID_MAP = defaultdict(set)

def get_recipes_matching_tag(tag):
    manager = services.get_instance_manager(sims4.resources.Types.RECIPE)
    recipe_guids = RECIPE_TAG_TO_TUNING_ID_MAP.get(tag)
    if recipe_guids:
        return list((manager.get(recipe_guid) for recipe_guid in recipe_guids))
    return []