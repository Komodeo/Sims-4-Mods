# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\focus\focus_ops.py
# Compiled at: 2018-04-18 14:02:11
# Size of source mod 2**32: 630 bytes
from protocolbuffers import DistributorOps_pb2
from distributor.ops import Op

class SetFocusScore(Op):

    def __init__(self, focus_score):
        super().__init__()
        self.op = DistributorOps_pb2.SetFocusScore()
        focus_score.populate_focus_score_msg(self.op)

    def write(self, msg):
        self.serialize_op(msg, self.op, DistributorOps_pb2.Operation.SET_FOCUS_SCORE)