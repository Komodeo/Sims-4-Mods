# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_spawner.py
# Compiled at: 2021-06-02 15:23:25
# Size of source mod 2**32: 3796 bytes
from objects.components import types
from objects.components.spawner_component import SpawnerTuning
from objects.components.spawner_component_enums import SpawnerType
from objects.gardening.gardening_tuning import GardeningTuning
from objects.object_enums import ItemLocation
from objects.system import create_object
from sims4.utils import flexmethod
import sims4.log
logger = sims4.log.Logger('Gardening', default_owner='camilogarcia')

class FruitSpawnerData(SpawnerTuning):
    INSTANCE_SUBCLASSES_ONLY = True

    class _SpawnerOption:
        spawn_type = SpawnerType.SLOT
        slot_type = None
        state_mapping = None
        force_initialization_spawn = None

    def __init__(self, *, spawn_weight, tests):
        spawner_option = self._SpawnerOption()
        spawner_option.slot_type = GardeningTuning.GARDENING_SLOT
        super().__init__(object_reference=(), spawn_weight=spawn_weight,
          spawn_chance=100,
          spawner_option=spawner_option,
          spawn_times=None,
          tests=tests)

    def set_fruit(self, fruit_definition):
        self.object_reference += (fruit_definition,)

    @flexmethod
    def create_spawned_object(cls, inst, mother, definition, loc_type=ItemLocation.ON_LOT):
        scale = GardeningTuning.SCALE_COMMODITY.default_value
        child = None
        try:
            child = create_object(definition, loc_type=loc_type)
            gardening_component = child.get_component(types.GARDENING_COMPONENT)
            if not gardening_component.is_shoot:
                if mother.has_state(GardeningTuning.QUALITY_STATE_VALUE):
                    quality_state = mother.get_state(GardeningTuning.QUALITY_STATE_VALUE)
                    child.set_state(quality_state.state, quality_state)
                    scale *= GardeningTuning.SCALE_VARIANCE.random_float()
                    child.set_stat_value(GardeningTuning.SCALE_COMMODITY, scale)
            mother.spawner_component._spawned_objects.add(child)
        except:
            logger.exception('Failed to spawn.')
            if child is not None:
                child.destroy(source=mother, cause='Exception spawning child fruit.')
                child = None

        return child

    @property
    def main_spawner(self):
        return self.object_reference[0]