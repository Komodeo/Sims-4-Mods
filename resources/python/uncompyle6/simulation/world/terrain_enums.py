# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\terrain_enums.py
# Compiled at: 2020-03-12 18:42:34
# Size of source mod 2**32: 1536 bytes
from sims4 import hash_util
import enum

class TerrainTag(enum.Int):
    INVALID = 0
    BRICK = hash_util.hash32('brick')
    CARPET = hash_util.hash32('carpet')
    CEMENT = hash_util.hash32('cement')
    DEEPSNOW = hash_util.hash32('deepsnow')
    DIRT = hash_util.hash32('dirt')
    GRASS = hash_util.hash32('grass')
    GRAVEL = hash_util.hash32('gravel')
    HARDWOOD = hash_util.hash32('hardwood')
    LEAVES = hash_util.hash32('leaves')
    LINOLEUM = hash_util.hash32('linoleum')
    MARBLE = hash_util.hash32('marble')
    METAL = hash_util.hash32('metal')
    PUDDLE = hash_util.hash32('puddle')
    SAND = hash_util.hash32('sand')
    SNOW = hash_util.hash32('snow')
    STONE = hash_util.hash32('stone')
    WOOD_DECK = hash_util.hash32('wood deck')