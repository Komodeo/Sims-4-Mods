# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\preference_utils.py
# Compiled at: 2021-09-01 10:58:18
# Size of source mod 2**32: 701 bytes
import services, sims4.resources
from traits.preference_enums import PreferenceTypes

def preferences_gen():
    trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
    if trait_manager is None:
        return
    for trait in trait_manager.types.values():
        if trait.is_preference_trait:
            yield trait


def get_preferences_by_category(category):
    return [p for p in preferences_gen() if p.preference_category is category]