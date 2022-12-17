# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\pools\pool_utils.py
# Compiled at: 2021-02-02 16:19:39
# Size of source mod 2**32: 832 bytes
from _weakrefset import WeakSet
import services, sims4.log, sims4.reload
logger = sims4.log.Logger('Pool Utils', default_owner='skorman')
with sims4.reload.protected(globals()):
    cached_pool_objects = WeakSet()
POOL_LANDING_SURFACE = 'Water'

def get_main_pool_objects_gen():
    yield from cached_pool_objects
    if False:
        yield None


def get_pool_by_block_id(block_id):
    for pool in get_main_pool_objects_gen():
        if pool.block_id == block_id:
            return pool

    logger.error('No Pool Matching block Id: {}', block_id, owner='camilogarcia')