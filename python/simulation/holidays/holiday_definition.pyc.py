# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\holidays\holiday_definition.py
# Compiled at: 2018-04-11 16:29:28
# Size of source mod 2**32: 4047 bytes
from audio.primitive import TunablePlayAudio
from interactions.utils.display_mixin import get_display_mixin
from interactions.utils.tunable_icon import TunableIconAllPacks
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, Tunable, TunableList, TunableReference, OptionalTunable, TunableResourceKey
from sims4.tuning.tunable_base import ExportModes
from sims4.utils import classproperty
import services, sims4.resources
logger = sims4.log.Logger('Holiday')
HolidayDefinitionDisplayMixin = get_display_mixin(has_icon=True)

class HolidayDefinition(HasTunableReference, HolidayDefinitionDisplayMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.HOLIDAY_DEFINITION)):
    POSSIBLE_ICONS = TunableList(description='\n        A list of tunable icons that can be selected for a holiday.\n        ',
      tunable=TunableIconAllPacks(description='\n            An icon that can be selected for a holiday.\n            ',
      export_modes=(ExportModes.All)),
      export_modes=(ExportModes.All))
    INSTANCE_TUNABLES = {'traditions':TunableList(description='\n            List of default traditions for this holiday.\n            ',
       tunable=TunableReference(description='\n                A default tradition for this holiday.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.HOLIDAY_TRADITION))),
       unique_entries=True,
       maxlength=5), 
     'time_off_work':Tunable(description='\n            If checked, Sims will have the day off from work, both part time\n            and full time.\n            ',
       tunable_type=bool,
       default=False), 
     'time_off_school':Tunable(description='\n            If checked, Sims will have the day off from school for the holiday.\n            ',
       tunable_type=bool,
       default=False), 
     'can_be_modified':Tunable(description='\n            If checked, this holiday can be modified by the player.\n            ',
       tunable_type=bool,
       default=False), 
     'decoration_preset':OptionalTunable(description='\n            The decoration preset that this holiday is set to by default.\n            \n            If disabled, this holiday does not do decorations.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(Types.LOT_DECORATION_PRESET)))), 
     'calendar_alert_description':OptionalTunable(description='\n            If tuned, there will be a calendar alert description.\n            ',
       tunable=TunableLocalizedStringFactory(description='\n                Description that shows up in the calendar alert.\n                0 - Holiday Name\n                ')), 
     'audio_sting':TunableResourceKey(description='\n            The sound to play.\n            ',
       default=None,
       resource_types=(
      sims4.resources.Types.PROPX,))}

    @classproperty
    def display_name(cls):
        return cls._display_data.instance_display_name

    @classproperty
    def display_icon(cls):
        return cls._display_data.instance_display_icon