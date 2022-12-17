# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sickness\sickness_utils.py
# Compiled at: 2017-05-16 11:54:08
# Size of source mod 2**32: 876 bytes
from sickness.sickness import Sickness
from sims4.resources import Types
import services

def all_sicknesses_gen():
    for sickness in services.get_instance_manager(Types.SICKNESS).types.values():
        if issubclass(sickness, Sickness):
            yield sickness


def all_sickness_weights_gen(resolver, criteria_func=lambda x: True
):
    for sickness in all_sicknesses_gen():
        if not criteria_func(sickness):
            continue
        else:
            weight = sickness.get_sickness_weight(resolver)
        if not weight:
            continue
        else:
            yield (
             weight, sickness)