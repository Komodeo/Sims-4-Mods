# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\native\routing\connectivity.py
# Compiled at: 2014-12-15 16:27:05
# Size of source mod 2**32: 457 bytes
try:
    from _pathing import connectivity_handle as Handle, connectivity_handle_list as HandleList
except ImportError:

    class Handle:

        def __init__(self, location):
            self.location = location


    class HandleList:

        def __init__(self):
            pass