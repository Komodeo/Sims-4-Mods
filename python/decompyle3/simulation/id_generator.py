# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\id_generator.py
# Compiled at: 2013-04-30 20:04:56
# Size of source mod 2**32: 588 bytes
try:
    import _guid
except ImportError:
    _object_count = 0

    class _guid:

        @staticmethod
        def generate_s4guid():
            global _object_count
            _object_count += 1
            return _object_count


def __reload__(old_module_vars):
    pass


def generate_object_id():
    return _guid.generate_s4guid()