# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\drama_node_do_nothing.py
# Compiled at: 2021-04-12 13:05:24
# Size of source mod 2**32: 513 bytes
from drama_scheduler.drama_node import BaseDramaNode, DramaNodeRunOutcome
from sims4.utils import classproperty

class DoNothingDramaNode(BaseDramaNode):

    @classproperty
    def simless(cls):
        return True

    def _run(self):
        return DramaNodeRunOutcome.SUCCESS_NODE_COMPLETE