# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_component_shoot.py
# Compiled at: 2018-02-01 14:40:39
# Size of source mod 2**32: 804 bytes
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from objects.gardening.gardening_component import _GardeningComponent
import objects.components.types

class GardeningShootComponent(_GardeningComponent, component_name=objects.components.types.GARDENING_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.GardeningComponent):

    @property
    def is_shoot(self):
        return True