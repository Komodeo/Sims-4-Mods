# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\context.py
# Compiled at: 2012-07-23 13:36:34
# Size of source mod 2**32: 1031 bytes
from interactions.context import InteractionContext
from interactions.priority import Priority

class PostureContext:
    __slots__ = ('source', 'priority', 'pick')

    def __init__(self, source=InteractionContext.SOURCE_SCRIPT, priority=Priority.Low, pick=None):
        self.source = source
        self.priority = priority
        self.pick = pick

    def __repr__(self):
        return '{0}.{1}({2}, {3})'.format(self.__module__, self.__class__.__name__, self.source, repr(self.priority))