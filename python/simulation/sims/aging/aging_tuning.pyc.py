# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\aging\aging_tuning.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 2236 bytes
from sims.aging.aging_data import AgingData
from sims.sim_info_types import Species
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, Tunable, TunableSimMinute
from sims4.tuning.tunable_base import EnumBinaryExportType
from sims.aging.aging_enums import AgeSpeeds

class AgingTuning:
    AGING_DATA = TunableMapping(description='\n        On a per-species level, define all age-related data.\n        ',
      key_type=TunableEnumEntry(description='\n            The species this aging data applies to.\n            ',
      tunable_type=Species,
      default=(Species.HUMAN),
      invalid_enums=(
     Species.INVALID,),
      binary_type=(EnumBinaryExportType.EnumUint32)),
      value_type=(AgingData.TunableFactory()),
      tuple_name='AgingDataMapping')
    AGING_SAVE_LOCK_TOOLTIP = TunableLocalizedStringFactory(description='\n        The tooltip to show in situations where save-lock during Age Up is\n        necessary, i.e. when babies or non-NPC Sims age up.\n        \n        This tooltip is provided one token: the Sim that is aging up.\n        ')
    AGE_SPEED_SETTING = TunableEnumEntry(description='\n        The speed at which all Sims (human, cat, dog, fox) age. Specific values tuned on aging_transition.\n        ',
      tunable_type=AgeSpeeds,
      default=(AgeSpeeds.NORMAL))
    AGE_PROGRESS_UPDATE_TIME = Tunable(description='\n        The update rate, in Sim Days, of age progression in the UI.\n        ',
      tunable_type=float,
      default=0.2)
    AGE_SUPPRESSION_ALARM_TIME = TunableSimMinute(description='\n        Amount of time in sim seconds to suppress aging.\n        ',
      default=5,
      minimum=1)

    @classmethod
    def get_aging_data(cls, species):
        return cls.AGING_DATA[species]

    @classmethod
    def get_age_speed(cls):
        return cls.AGE_SPEED_SETTING