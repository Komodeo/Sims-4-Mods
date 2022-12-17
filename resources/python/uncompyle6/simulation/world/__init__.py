# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\__init__.py
# Compiled at: 2021-05-06 10:56:29
# Size of source mod 2**32: 524 bytes
try:
    import _lot
except ImportError:

    class _lot:

        @staticmethod
        def get_lot_id_from_instance_id(*_, **__):
            return 0

        class Lot:
            pass


get_lot_id_from_instance_id = _lot.get_lot_id_from_instance_id