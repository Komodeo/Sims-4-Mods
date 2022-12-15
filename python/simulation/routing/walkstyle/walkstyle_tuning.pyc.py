# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\walkstyle\walkstyle_tuning.py
# Compiled at: 2019-06-06 10:53:41
# Size of source mod 2**32: 1922 bytes
from sims4.tuning.tunable import TunableResourceKey
from sims4.tuning.tunable_hash import _Hash
import routing, sims4.resources

class Walkstyle(_Hash):

    @property
    def animation_parameter(self):
        return self.unhash


class TunableWalkstyle(TunableResourceKey):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, resource_types=(sims4.resources.Types.WALKSTYLE,), **kwargs)

    @property
    def validate_pack_safe(self):
        return False

    def load_etree_node(self, node, source, expect_error):
        value = super().load_etree_node(node, source, expect_error)
        if value is not None:
            walkstyle_hash = routing.get_walkstyle_hash_from_resource(value)
            walkstyle_name = routing.get_walkstyle_name_from_resource(value)
            value = Walkstyle(walkstyle_name, walkstyle_hash)
        return value