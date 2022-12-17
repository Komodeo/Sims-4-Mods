# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\template_affordance_provider\tunable_affordance_template_base.py
# Compiled at: 2017-02-15 16:45:03
# Size of source mod 2**32: 691 bytes


class TunableAffordanceTemplateBase:

    def get_template_affordance(self):
        raise NotImplementedError

    def get_template_kwargs(self):
        raise NotImplementedError