# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\eco_footprint\eco_footprint_tuning.py
# Compiled at: 2020-10-22 09:39:30
# Size of source mod 2**32: 10834 bytes
import services, sims4
from eco_footprint.eco_footprint_enums import EcoFootprintStateType, EcoFootprintDirection
from event_testing.resolver import StreetResolver
from interactions.utils.tunable_icon import TunableIconAllPacks
from sims4 import math
from sims4.localization import TunableLocalizedString
from sims4.tuning.geometric import TunableCurve
from sims4.tuning.tunable import TunableReference, TunableTuple, Tunable, TunableRange, TunableMapping, TunableEnumEntry, TunableColor
from sims4.tuning.tunable_base import ExportModes, GroupNames
from statistics.commodity import Commodity
from tunable_multiplier import TunableMultiplier, TestedSum
from tunable_time import TunableTimeSpan
logger = sims4.log.Logger('EcoFootprint', default_owner='bnguyen')

class EcoFootprintTunables:
    STREET_FOOTPRINT = Commodity.TunableReference(description='\n        A reference to the commodity that will control the eco footprint\n        state. The street footprint commodity converges toward the\n        aggregate of the lot footprints. \n        ',
      pack_safe=True)
    LOT_FOOTPRINT = Commodity.TunableReference(description="\n        A reference to the lot-level statistic. The aggregate of all lot \n        footprints on a street will determine the convergence point of\n        the street's eco footprint. \n        ",
      pack_safe=True)
    STREET_CONVERGENCE_UPDATE_TUNING = TunableTuple(description='\n        Tuning that determines how the street footprint convergence is\n        calculated. \n        ',
      update_interval=TunableTimeSpan(description="\n            How often the street footprint's convergence is recalculated\n            in sim hours.\n            ",
      default_hours=1),
      tested_sums=TestedSum.TunableFactory(description="\n            Tested sums added to the convergence point of the street's eco\n            footprint.\n            \n            These are added after the tested multipliers are applied to the\n            convergence point. \n            "),
      played_lot_weight=TunableCurve(description="\n            A curve that defines the impact of a played lot on the street \n            footprint's convergence relative to unplayed lots.\n\n            The way we define a played lot is any lot with a household\n            that has been played. Unplayed lots are everything else.\n\n            The input to the curve is the percentage of played lots on the\n            street. The output should be a value between 0 and 1 that \n            weights the relative impact of played lots.\n            "),
      convergence_rate_tuning=TunableMapping(description='\n            Mapping that maps the convergence direction to modifiers to apply\n            to the rate of convergence when converging in that direction.\n            ',
      key_type=TunableEnumEntry(description='\n                An EcoFootprintDirection.\n                ',
      tunable_type=EcoFootprintDirection,
      default=(EcoFootprintDirection.AT_CONVERGENCE),
      invalid_enums=(
     EcoFootprintDirection.AT_CONVERGENCE,)),
      value_type=TunableTuple(description='\n                Tuple for modifiers to apply.\n                ',
      per_lot_modifiers=TunableMultiplier.TunableFactory(description="\n                    Tested multipliers applied on a per lot basis to the\n                    convergence rate of the street's\n                    eco footprint.  Picked Zone ID will be the zone_id of the\n                    zone in question.\n                    ")),
      minlength=2))
    ECO_FOOTPRINT_STATE_DATA = TunableTuple(description='\n        Tuning that defines the different Eco Footprint States,\n        their effects, and the thresholds on the lot/street footprint\n        statistics that determine when a street or lot is considered green,\n        neutral, or industrial.\n        ',
      eco_footprint_states=TunableMapping(description='\n            A mapping from EcoFootprintStateType to EcoFootprintState.\n            ',
      key_type=TunableEnumEntry(description='\n                An EcoFootprintStateType.\n                ',
      tunable_type=EcoFootprintStateType,
      default=(EcoFootprintStateType.NEUTRAL)),
      value_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
      class_restrictions=('EcoFootprintState', ),
      pack_safe=True),
      key_name='Eco Footprint State Type',
      value_name='Eco Footprint State'),
      green_threshold=Tunable(description='\n            The number at or below which a street or lot is considered\n            green.\n            ',
      tunable_type=int,
      default=(-400)),
      industrial_threshold=Tunable(description='\n            The number at or above which a street or lot is considered\n            industrial.\n            ',
      tunable_type=int,
      default=400),
      additional_footprint_change_on_state_change=TunableRange(description="\n            A value that is multiplied by the direction of the street \n            footprint's convergence and added to the street footprint\n            whenever the state changes. The purpose of this value is to\n            prevent rapid flickering between states when the street eco \n            footprint value is borderline by nudging the eco footprint further\n            in its current direction.\n            ",
      tunable_type=float,
      default=0,
      minimum=0,
      maximum=None))
    ECO_FOOTPRINT_UI_TUNABLES = TunableMapping(description='\n        Mapping of ECO_FOOTPRINT state to UI tunables.\n        ',
      key_type=TunableEnumEntry(tunable_type=EcoFootprintStateType,
      default=(EcoFootprintStateType.NEUTRAL)),
      value_type=TunableTuple(street_descriptor_tuning=TunableTuple(description='\n                Tunables associated with eco footprint street descriptors.  Street Descriptors are displayed on the map\n                when mousing over a street in the eco footprint toggle mode.\n                ',
      name_text_color=TunableColor.TunableColorRGBA(description='\n                    Street descriptor name text color for this eco footprint state.\n                    '),
      description_text=TunableLocalizedString(description='\n                    Street descriptor description text for this eco footprint state.  \n                    '),
      description_text_color=TunableColor.TunableColorRGBA(description='\n                    Street descriptor description text color for this eco footprint state.\n                    '),
      background_color=TunableColor.TunableColorRGBA(description='\n                    Street descriptor background color for this eco footprint state.\n                    '),
      export_class_name='StreetDescriptorTuningTuple'),
      HUD_tooltip_description_text=TunableLocalizedString(description='\n                Tooltip description text for the eco footprint tooltip for this eco footprint state.  This tooltip is\n                displayed when mousing over the TimeControls widget in live mode.\n                '),
      street_highlight_color=TunableColor.TunableColorRGBA(description='\n                Street highlight color displayed in the eco footprint toggle mode on the map for this eco footprint state.\n                '),
      icon=TunableIconAllPacks(description='\n                Icon associated with this eco footprint state.\n                ',
      allow_none=False),
      name_text=TunableLocalizedString(description='\n                Name text for this eco footprint state.\n                '),
      export_class_name='EcoFootprintStateTuningTuple'),
      tuning_group=(GroupNames.UI),
      tuple_name='EcoFootprintUITuningMapping',
      export_modes=(ExportModes.ClientBinary))

    @classmethod
    def _get_value_of_tested_sums(cls, street_resolver):
        return cls.STREET_CONVERGENCE_UPDATE_TUNING.tested_sums.get_modified_value(street_resolver)

    @classmethod
    def get_modified_convergence_value(cls, street_footprint_stat, unmodified_convergence_value, street):
        street_resolver = StreetResolver(street)
        modified_convergence_value = unmodified_convergence_value + EcoFootprintTunables._get_value_of_tested_sums(street_resolver)
        modified_convergence_value = math.clamp(street_footprint_stat.min_value, modified_convergence_value, street_footprint_stat.max_value)
        return modified_convergence_value

    @classmethod
    def get_state_of_type(cls, eco_footprint_state_type):
        return cls.ECO_FOOTPRINT_STATE_DATA.eco_footprint_states.get(eco_footprint_state_type, None)

    @classmethod
    def eco_footprint_value_to_state(cls, value):
        if value <= cls.ECO_FOOTPRINT_STATE_DATA.green_threshold:
            return EcoFootprintStateType.GREEN
        if value >= cls.ECO_FOOTPRINT_STATE_DATA.industrial_threshold:
            return EcoFootprintStateType.INDUSTRIAL
        return EcoFootprintStateType.NEUTRAL