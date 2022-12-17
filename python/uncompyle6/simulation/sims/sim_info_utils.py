# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_info_utils.py
# Compiled at: 2017-04-18 12:11:56
# Size of source mod 2**32: 1876 bytes
import functools, inspect, services

def sim_info_auto_finder(fn):
    is_generator = inspect.isgeneratorfunction(fn)
    if is_generator:

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            sim_info_manager = services.sim_info_manager()
            for sim_id in fn(*args, **kwargs):
                sim_info = sim_info_manager.get(sim_id)
                if sim_info is not None:
                    yield sim_info

    else:

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            sim_ids = fn(*args, **kwargs)
            if sim_ids is None:
                return
            sim_info_manager = services.sim_info_manager()
            sim_infos = []
            for sim_id in sim_ids:
                sim_info = sim_info_manager.get(sim_id)
                if sim_info is not None:
                    sim_infos.append(sim_info)

            return tuple(sim_infos)

    return wrapped


def apply_super_affordance_commodity_flags(sim, key, super_affordances):
    if sim is not None:
        if super_affordances:
            flags = set()
            for affordance in super_affordances:
                flags |= affordance.commodity_flags

            if flags:
                sim.add_dynamic_commodity_flags(key, flags)


def remove_super_affordance_commodity_flags(sim, key):
    if sim is not None:
        sim.remove_dynamic_commodity_flags(key)