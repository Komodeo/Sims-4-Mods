# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\autonomy_op_list.py
# Compiled at: 2017-07-27 14:59:20
# Size of source mod 2**32: 2270 bytes


class AutonomyAdList:

    def __init__(self, stat_type):
        self._stat_type = stat_type
        self._op_list = []

    @property
    def stat(self):
        return self._stat_type

    def add_op(self, op):
        if op.tested:
            self._op_list.append(op)
        else:
            self._op_list.insert(0, op)

    def remove_op(self, op):
        if op in self._op_list:
            self._op_list.remove(op)
            return True
        return False

    def get_fulfillment_rate(self, interaction):
        return sum((op.get_fulfillment_rate(interaction) for op in self._get_valid_ops_gen(interaction)))

    def get_value(self, interaction):
        return sum((op.get_value() for op in self._get_valid_ops_gen(interaction)))

    def is_valid(self, interaction):
        for _ in self._get_valid_ops_gen(interaction):
            return True

        return False

    def _get_valid_ops_gen(self, interaction):
        resolver = interaction.get_resolver()
        for op in self._op_list:
            if op.test_resolver(resolver, ignore_chance=True):
                yield op