# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\forwarding.py
# Compiled at: 2017-10-04 10:45:02
# Size of source mod 2**32: 940 bytes
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit
from tunable_utils.tunable_object_filter import TunableObjectFilterVariant
import sims4.log
logger = sims4.log.Logger('Interactions')

class Forwarding(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'object_filter': TunableObjectFilterVariant(description='\n            The object we want to forward this interaction *on* must satisfy\n            this filter.\n            ',
                        default=(TunableObjectFilterVariant.FILTER_ALL))}

    def is_allowed_to_forward(self, interaction, obj):
        if not self.object_filter.is_object_valid(obj):
            return False
        return True