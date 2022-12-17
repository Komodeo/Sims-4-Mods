# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\camera_view_component.py
# Compiled at: 2017-10-30 11:04:02
# Size of source mod 2**32: 1935 bytes
import math
from objects.components import Component, componentmethod
from objects.components.types import CAMERA_VIEW_COMPONENT
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, Tunable, TunableAngle
import sims4.math

class CameraViewComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=CAMERA_VIEW_COMPONENT):
    FACTORY_TUNABLES = {'rotation':TunableAngle(description='\n            The offset in degrees from the facing vector that we will use to \n            place the camera position.\n            ',
       default=0.0), 
     'distance':Tunable(description='\n            The distance from the owners position to place the camera.\n            ',
       tunable_type=float,
       default=1.0), 
     'height':Tunable(description='\n            If you want to increase the height of the camera for a specific\n            viewpoint.\n            ',
       tunable_type=float,
       default=0.0)}

    @componentmethod
    def get_camera_position(self):
        forward = self.owner.forward
        sin = math.sin(self.rotation)
        cos = math.cos(self.rotation)
        rotation = sims4.math.Vector3(forward.x * cos + forward.z * sin, forward.y, -forward.x * sin + forward.z * cos)
        final_pos = self.owner.position + rotation * self.distance
        final_pos.y += self.height
        return final_pos