# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\primitives\persistence_primitives.py
# Compiled at: 2014-12-16 12:20:24
# Size of source mod 2**32: 610 bytes
try:
    import _persistence_primitives
except ImportError:

    class _persistence_primitives:
        PersistVersion = 0


class PersistVersion:
    UNKNOWN = 0
    kPersistVersion_Implementation = 1
    SaveObjectDepreciation = 2
    SaveObjectCreateFromLotTemplate = 3
    SaveLoadSIFirstPass = 4
    GlobalSaveData = 5