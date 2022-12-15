# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\faction_reputation\faction_rep_tuning.py
# Compiled at: 2020-04-08 13:35:37
# Size of source mod 2**32: 1359 bytes
from sims4.tuning.tunable import TunablePackSafeReference, TunableColor
from sims4.tuning.tunable_base import ExportModes
import services, sims4.resources

class FactionRepModuleTuning:
    FIRST_ORDER_REPUTATION = TunablePackSafeReference(description='\n        Ranked statistic for first order reputation.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('RankedStatistic', ),
      export_modes=(ExportModes.All))
    RESISTANCE_REPUTATION = TunablePackSafeReference(description='\n        Ranked statistic for resistance reputation.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('RankedStatistic', ),
      export_modes=(ExportModes.All))
    SCOUNDREL_REPUTATION = TunablePackSafeReference(description='\n        Ranked statistic for scoundrel reputation.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('RankedStatistic', ),
      export_modes=(ExportModes.All))