# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\posture_errors.py
# Compiled at: 2018-02-20 15:22:03
# Size of source mod 2**32: 1046 bytes


class PostureGraphError(Exception):
    pass


class PostureGraphBoundaryConditionError(PostureGraphError):
    pass


class PostureGraphMiddlePathError(PostureGraphError):
    pass