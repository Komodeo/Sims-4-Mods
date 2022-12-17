# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_tuning.py
# Compiled at: 2022-03-10 17:35:10
# Size of source mod 2**32: 2257 bytes
import enum
from interactions.utils.death import DeathType
from sims4.localization import TunableLocalizedStringFactoryVariant
from sims4.tuning.tunable import Tunable, TunableMapping, TunableEnumEntry, TunableTuple
from sims4.tuning.tunable_base import ExportModes
from tunable_time import TunableTimeSpan

class StoryProgressionDomainType(enum.Int):
    MY_HOUSEHOLDS = 0
    OTHER_HOUSEHOLDS = 1


class StoryProgTunables:
    DOMAIN_ENABLEMENT_DEFAULTS = TunableMapping(description='\n        Default enablement states for all story progression domains that can be enabled/disabled.\n        ',
      key_type=TunableEnumEntry(tunable_type=StoryProgressionDomainType,
      default=(StoryProgressionDomainType.MY_HOUSEHOLDS)),
      value_type=Tunable(tunable_type=bool,
      default=True),
      tuple_name='CategoryEnablementDefaultTuple',
      export_modes=(ExportModes.ClientBinary))
    HISTORY = TunableTuple(chapter_history_lifetime=TunableTimeSpan(description="\n            How long a chapter's history will be stored in persistence.\n            ",
      default_days=5),
      no_history_discovery_string=TunableLocalizedStringFactoryVariant(description='\n            String to display when there are no historical arcs to discover.\n            '),
      death_type_discovery_string_map=TunableMapping(description='\n            Mapping of death type to a discovery string. \n            ',
      key_type=TunableEnumEntry(tunable_type=DeathType,
      default=(DeathType.NONE)),
      value_type=(TunableLocalizedStringFactoryVariant())))