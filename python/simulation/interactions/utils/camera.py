# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\camera.py
# Compiled at: 2021-05-06 17:19:49
# Size of source mod 2**32: 6819 bytes
from camera import focus_on_sim, focus_on_object, shake_camera, focus_on_object_from_position, focus_on_lot, walls_up_override, focus_on_position
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from objects.components.types import CAMERA_VIEW_COMPONENT
from sims4.tuning.tunable import TunableEnumEntry, Tunable, AutoFactoryInit, HasTunableFactory, HasTunableSingletonFactory, OptionalTunable, TunableRange, TunableRealSecond, TunablePackSafeReference
import services, sims4

class CameraFocusElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'\n            Focus the camera on the specified participant.\n            ', 
     'participant':TunableEnumEntry(description='\n            The participant of this interaction to focus the camera on.\n            \n            Should be some kind of object or Sim.  Can also be set to Lot\n            to do a thumbnail-style view of the lot.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'follow':Tunable(description='\n            Whether or not the camera should stick to the focused participant.\n            ',
       tunable_type=bool,
       default=False), 
     'time_to_position':TunableRealSecond(description='\n            The amount of time given for the camera to move into position.\n            \n            Only applicable when participant type is Lot\n            ',
       default=1.0), 
     'sim_filter':OptionalTunable(description='\n            If enabled, this sim filter will be used as the camera subject \n            instead of the participant.\n            ',
       tunable=TunablePackSafeReference(description='\n                The filter used to find the desired Sim.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER))))}

    def _do_behavior(self):
        subject = None
        if self.sim_filter is not None:
            for sim in services.sim_info_manager().instanced_sims_gen():
                matched = services.sim_filter_service().does_sim_match_filter((sim.id), sim_filter=(self.sim_filter),
                  gsi_source_fn=(lambda: 'CameraFocusElement: Looking for sim'
))
                if matched:
                    subject = sim
                    break

        else:
            subject = self.interaction.get_participant(self.participant)
            if subject is None:
                return
        if self.participant == ParticipantType.Lot:
            focus_on_lot(lerp_time=(self.time_to_position))
            return
        if subject.has_component(CAMERA_VIEW_COMPONENT):
            focus_on_object_from_position(obj_position=(subject.position), camera_position=(subject.get_camera_position()))
            return
        if subject.is_sim:
            focus_on_sim(sim=subject, follow=(self.follow), client=(subject.client))
        else:
            if subject.is_in_inventory():
                inventory_owner = subject.inventoryitem_component.last_inventory_owner
                focus_on_object(object=inventory_owner, follow=(self.follow))
            else:
                focus_on_object(object=subject, follow=(self.follow))


class SetWallsUpOverrideElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'enable': Tunable(description='\n            Set to True to enable the override.  False to disable it.\n            \n            A user moving the camera manually will also cancel the override.\n            ',
                 tunable_type=bool,
                 default=True)}

    def _do_behavior(self):
        walls_up_override(walls_up=(self.enable))


class TunableCameraShake(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'duration':TunableRange(description='\n            Length of time this effect should occur, in seconds.\n            ',
       tunable_type=float,
       default=1.0,
       minimum=0.0), 
     'frequency':OptionalTunable(description='\n            The times per second that the effect should occur.\n            \n            Default value is 1.0\n            ',
       tunable=TunableRange(float, 1.0, minimum=0.0),
       disabled_name='use_default',
       enabled_name='specify'), 
     'amplitude':OptionalTunable(description='\n            Strength of the shake, in Sim meters.\n            \n            Default value is 1.0\n            ',
       tunable=TunableRange(float, 1.0, minimum=0.0),
       disabled_name='use_default',
       enabled_name='specify'), 
     'octaves':OptionalTunable(description='\n            Number of octaves for the shake.\n\n            Default value is 1\n            ',
       tunable=TunableRange(int, 1, minimum=0),
       disabled_name='use_default',
       enabled_name='specify'), 
     'fade_multiplier':OptionalTunable(description='\n            Adjusts the wave function, this can be set above 1.0 to introduce\n            a plateau for the shake effect.\n\n            Default value is 1.0\n            ',
       tunable=TunableRange(float, 1.0, minimum=1.0),
       disabled_name='use_default',
       enabled_name='specify')}

    def shake_camera(self):
        shake_camera((self.duration), frequency=(self.frequency),
          amplitude=(self.amplitude),
          octaves=(self.octaves),
          fade_multiplier=(self.fade_multiplier))