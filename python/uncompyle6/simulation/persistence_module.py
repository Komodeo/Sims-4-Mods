# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\persistence_module.py
# Compiled at: 2014-06-10 21:50:20
# Size of source mod 2**32: 1889 bytes
try:
    import _persistence_module
except ImportError as err:
    try:

        class _persistence_module:

            @staticmethod
            def run_persistence_operation(persistence_op_type, protocol_buffer, save_slot_id, callback):
                callback(save_slot_id, False)
                return False


    finally:
        err = None
        del err

class PersistenceOpType:
    kPersistenceOpInvalid = 0
    kPersistenceOpLoad = 1
    kPersistenceOpSave = 2
    kPersistenceOpLoadZoneObjects = 3
    kPersistenceOpSaveZoneObjects = 4
    kPersistenceOpSaveGameplayGlobalData = 5
    kPersistenceOpLoadGameplayGlobalData = 6
    kPersistenceOpSaveHousehold = 1000


run_persistence_operation = _persistence_module.run_persistence_operation