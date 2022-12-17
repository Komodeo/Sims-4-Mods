# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\stored_actor_location_component.py
# Compiled at: 2021-09-01 10:58:18
# Size of source mod 2**32: 8554 bytes
import sims4, services
from protocolbuffers import GameplaySaveData_pb2 as gameplay_serialization
from interactions.aop import AffordanceObjectPair
from interactions.constraints import Transform
from objects.components import Component, componentmethod, types
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableReference
import protocolbuffers.SimObjectAttributes_pb2 as SimObjectAttributes_pb2

class StoredActorLocationTuning:
    GO_TO_STORED_LOCATION_SI = TunableReference(description='\n        The affordance that is provided by the Stored Actor Location\n        Component when there is a set location.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      class_restrictions=('GoToStoredLocationSuperInteraction', ),
      pack_safe=True)
    UNROUTABLE_MESSAGE_OFF_LOT = TunableLocalizedStringFactory(description='\n        The tooltip used when the Stored Location SI is unavailable\n        because the stored location is not on the active lot.\n        ')
    UNROUTABLE_MESSAGE_NOT_CONNECTED = TunableLocalizedStringFactory(description='\n        The tooltip used when the Stored Location SI is unavailable because\n        the stored location does not have routing connectivity to the sim.\n        ')


class StoredLocation:

    def __init__(self, location=None):
        self._location = location

    @property
    def orientation(self):
        if self._location is None:
            logger.warn('Attempting to access the orientation of a stored location with None value.')
            return
        return self._location.transform.orientation

    @property
    def transform(self):
        if self._location is None:
            logger.warn('Attempting to access the transform of a stored location with None value.')
            return
        return self._location.transform

    @property
    def translation(self):
        if self._location is None:
            logger.warn('Attempting to access the translation of a stored location with None value.')
            return
        return self._location.transform.translation

    @property
    def routing_surface(self):
        if self._location is None:
            logger.warn('Attempting to access the routing surface type of a stored location with None value.')
            return
        return self._location.routing_surface

    def save(self, stored_location_data):
        if self._location is None:
            return stored_location_data
        stored_location_data.x = self._location.transform.translation.x
        stored_location_data.y = self._location.transform.translation.y
        stored_location_data.z = self._location.transform.translation.z
        stored_location_data.rot_x = self._location.transform.orientation.x
        stored_location_data.rot_y = self._location.transform.orientation.y
        stored_location_data.rot_z = self._location.transform.orientation.z
        stored_location_data.rot_w = self._location.transform.orientation.w
        stored_location_data.level = self._location.level
        stored_location_data.surface_type = self._location.routing_surface.type
        return stored_location_data

    def load(self, stored_location_data):
        position = sims4.math.Vector3.ZERO()
        self._location = Location(position)
        self._location.transform.translation.x = stored_location_data.x
        self._location.transform.translation.y = stored_location_data.y
        self._location.transform.translation.z = stored_location_data.z
        self._location.transform.orientation.x = stored_location_data.rot_x
        self._location.transform.orientation.y = stored_location_data.rot_y
        self._location.transform.orientation.z = stored_location_data.rot_z
        self._location.transform.orientation.w = stored_location_data.rot_w
        self._location.level = stored_location_data.level
        self._location.routing_surface.type = stored_location_data.surface_id


class StoredActorLocationComponent(Component, component_name=types.STORED_ACTOR_LOCATION_COMPONENT, allow_dynamic=True, persistence_key=SimObjectAttributes_pb2.PersistenceMaster.PersistableData.StoredInfoComponent):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._stored_location = None

    def get_stored_location(self):
        if self._stored_location is None:
            logger.warn('Attempting to get a stored location with None value from the Stored Actor Location Component on {}.', self.owner)
        return self._stored_location

    @componentmethod
    def store_actor_location(self, sim):
        self._stored_location = StoredLocation(location=(sim.location))

    @componentmethod
    def component_potential_interactions_gen(self, context, **kwargs):
        if self._stored_location is None or StoredActorLocationTuning.GO_TO_STORED_LOCATION_SI is None:
            return
        final_transform = self._stored_location.transform
        final_routing_surface = self._stored_location.routing_surface
        constraint_to_satisfy = Transform(final_transform, routing_surface=final_routing_surface)
        yield AffordanceObjectPair((StoredActorLocationTuning.GO_TO_STORED_LOCATION_SI), (self.owner), (StoredActorLocationTuning.GO_TO_STORED_LOCATION_SI), None, constraint_to_satisfy=constraint_to_satisfy)

    def save(self, persistence_master_message):
        pass

    def load(self, stored_actor_location_component_message):
        pass


def add_stored_sim_location(object, sim=None, **kwargs):
    if object is not None:
        object.add_dynamic_component(types.STORED_ACTOR_LOCATION_COMPONENT)
        if sim is not None:
            object.store_actor_location(sim)
        return True
    return False