# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\ranked_statistic_display_info.py
# Compiled at: 2020-05-07 13:13:14
# Size of source mod 2**32: 7817 bytes
import services, sims4
from bucks.bucks_enums import BucksType
from sims4.localization import TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableReference, TunableMapping, TunableEnumEntry, TunableTuple, OptionalTunable, TunableResourceKey
from sims4.tuning.tunable_base import ExportModes, GroupNames

class RankedStatisticPanelIconInfo(TunableTuple):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, default_icon=TunableResourceKey(description='\n                The icon to use on the Sim Info panel when there are changes \n                to this Ranked Statistic.\n                ',
  resource_types=(sims4.resources.CompoundTypes.IMAGE)), 
         over_icon=TunableResourceKey(description='\n                The icon to use on the Sim Info panel when there are changes\n                to this Ranked Statistic and the mouse is over the button.\n                ',
  resource_types=(sims4.resources.CompoundTypes.IMAGE)), 
         export_class_name='SimInfoPanelIconsTuple', **kwargs)


class RankedStatisticDisplayInfo(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.USER_INTERFACE_INFO)):
    INSTANCE_TUNABLES = {'perks_panel_bucks_perk_info':TunableMapping(description='\n            A mapping of bucks type to info for that bucks type.\n            ',
       key_type=TunableEnumEntry(description='\n                The buck type this data corresponds to.\n                ',
       tunable_type=BucksType,
       default=(BucksType.INVALID)),
       value_type=TunableTuple(description='\n                Info used to display Bucks and BucksPerks in the Perks Panel.\n                ',
       bucks_text=(OptionalTunable(TunableLocalizedString(description="\n                    Text containing a currency type token, to display the \n                    bucks balance in the Perks Panel.\n                    If not present, the points balance for this buck type \n                    won't be shown in the Perks Panel.\n                    "))),
       bucks_tooltip=(OptionalTunable(TunableLocalizedString(description='\n                    Tooltip on the "Help" icon related for this buck type \n                    in the Perks Panel. Explains how this currency works.\n                    Can be none if no additional information is needed for\n                    this buck type.  \n                    '))),
       perk_currency_label=(OptionalTunable(TunableLocalizedString(description='\n                    Title text to display currency type on the Motive Panel.\n                    Such as "Power Points:" in "Power Points: 10"\n                    Can be none if we don\'t need to show this buck\'s balance on the Motive Panel.\n                    '))),
       perk_remove_tooltip=(OptionalTunable(TunableLocalizedString(description="\n                    Tooltip on the removal button on the perk cell in the Perks Panel.\n                    Can be none if perks don't need a special removal tooltip.\n                    "))),
       export_class_name='TunableRankedStatBucksInfoTuple'),
       tuple_name='RankedStatBucksToBucksInfoTuple',
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'perks_panel_revert_tooltip':OptionalTunable(TunableLocalizedString(description='\n            Tooltip shown on the revert button in the Perks Panel.\n            If not present, the revert button is unused and hidden.\n            '),
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'perks_panel_disabled_confirm_tooltip':OptionalTunable(description='\n            If enabled, allows tuning the tooltip shown on the confirm button in \n            the perks panel when it is disabled.\n            ',
       tunable=TunableLocalizedString(description='\n                The tooltip shown on the confirm button in the perks panel when \n                it is disabled.\n                '),
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'perks_panel_title':OptionalTunable(description='\n            If enabled, allows tuning the title shown in the Perks Panel for \n            this statistic.\n            ',
       tunable=TunableLocalizedString(description='\n                The title shown in the Perks Panel for this statistic. \n                '),
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'perks_panel_subtitle':OptionalTunable(description='\n            If enabled, allows tuning the subtitle shown in the Perks Panel for \n            this statistic.\n            ',
       tunable=TunableLocalizedString(description='\n                The subtitle shown in the Perks Panel for this statistic.\n                '),
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'sim_info_panel_icons':OptionalTunable(description='\n            If enabled, allows tuning icons that will show on the Sim Info panel\n            when there are changes in rank for this Ranked Statistic.\n            ',
       tunable=RankedStatisticPanelIconInfo(description='\n                The icons that will show on the Sim Info panel when there are\n                changes in rank for this Ranked Statistic.\n                '),
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'sim_info_panel_icons_negative':OptionalTunable(description='\n            If enabled, allows tuning icons that will show on the Sim Info panel\n            when there are negatives changes in rank for this Ranked Statistic.\n            If there are positive changes in rank while this is enabled, Sim\n            Info Panel Icons will be used.\n            If this is disabled, Sim Info Panel Icons will be used for both positive\n            and negative changes.\n            ',
       tunable=RankedStatisticPanelIconInfo(description='\n                The icons that will show on the Sim Info panel when there are\n                negative changes in rank for this Ranked Statistic.\n                '),
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'ranked_statistic_reference':TunableReference(description='\n            The ranked statistic gameplay tuning reference ID.\n            ',
       manager=services.get_instance_manager(Types.STATISTIC),
       class_restrictions=('RankedStatistic', ),
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI)}