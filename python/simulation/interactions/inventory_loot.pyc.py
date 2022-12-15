# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\inventory_loot.py
# Compiled at: 2014-03-21 18:17:43
# Size of source mod 2**32: 2677 bytes
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
import interactions, sims4.log
logger = sims4.log.Logger('LootOperations')

class InventoryLoot(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'description': '\n            Loot option for transfering an object from an owner Sim to a \n            target Sim.\n            \n            If objects are in the inventory it will try to do a transfer \n            from inventory-inventory.\n            If not it will try to mail the gift to other Sim\n            \n            e.g. Give gift interaction, you want to give an object from sim A \n            inventory to Sim B\n            '}

    @staticmethod
    def tuning_loaded_callback(instance_class, tunable_name, source, value):
        pass

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if target is None:
            logger.error('{} has no participant {} which is required in the InventoryLoot as the object to switch in between inventories', resolver, self.target_participant_type)
            return False
        current_inventory = target.get_inventory()
        if current_inventory is not None:
            if not current_inventory.try_remove_object_by_id(target.id):
                logger.error('{} fail to remove object {} from inventory {}', resolver, target, current_inventory)
                return False
            if subject is None:
                logger.error('{} has no participant {} which is required in the InventoryLoot as the object to switch in between inventories', resolver, self.target_participant_type)
                return False
            if subject.is_sim:
                subject = subject.get_sim_instance()
            if subject is None or subject.inventory_component is None:
                logger.error('{} InventoryLoot fail. {} has no inventory', resolver, subject)
                return False
            return subject.inventory_component.player_try_add_object(target)