# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\__init__.py
# Compiled at: 2018-02-13 19:05:18
# Size of source mod 2**32: 2136 bytes
from collections import namedtuple
from sims4.tuning.tunable import TunableSingletonFactory, TunableRealSecond
import sims4.log
decorations_logger = sims4.log.Logger('Lot Decorations', default_owner='jdimailig')
ClientLotDecorationParams = namedtuple('ClientLotDecorationParams', ('fade_duration',
                                                                     'fade_variation_range',
                                                                     'client_fade_delay'))
DECORATE_IMMEDIATELY = ClientLotDecorationParams(0, 0, 0)

class TunableClientLotDecorationParams(TunableSingletonFactory):
    FACTORY_TYPE = ClientLotDecorationParams

    def __init__(self, default_fade_duration=0, default_fade_variation_range=0, default_client_fade_delay=0, **kwargs):
        (super().__init__)(fade_duration=TunableRealSecond(description='\n                Amount of time alloted for fading in a decoration on a lot.\n                ',
  minimum=0,
  default=default_fade_duration), 
         fade_variation_range=TunableRealSecond(description="\n                Randomized variation time range for fade in that is used \n                so that all deco trims on a lot don't fade in at the same time.\n                ",
  minimum=0,
  default=default_fade_variation_range), 
         client_fade_delay=TunableRealSecond(description="\n                After an lot decoration request is made, this is the delay \n                amount given to the client decoration system before it starts \n                to fade in the lot decorations.\n                \n                Note when the request is processed, gameplay has already saved \n                that the lot is 'decorated', so there are save/load implications\n                when this is set to a large value.\n                ",
  minimum=0,
  default=default_client_fade_delay), **kwargs)