# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\balloon\balloon_enums.py
# Compiled at: 2020-07-31 21:42:59
# Size of source mod 2**32: 998 bytes
from protocolbuffers import Sims_pb2
import enum

class BalloonTypeEnum(enum.Int):
    THOUGHT = 0
    SPEECH = 1
    DISTRESS = 2
    SENTIMENT = 3


BALLOON_TYPE_LOOKUP = {BalloonTypeEnum.THOUGHT: (Sims_pb2.AddBalloon.THOUGHT_TYPE, Sims_pb2.AddBalloon.THOUGHT_PRIORITY), 
 BalloonTypeEnum.SPEECH: (Sims_pb2.AddBalloon.SPEECH_TYPE, Sims_pb2.AddBalloon.SPEECH_PRIORITY), 
 BalloonTypeEnum.DISTRESS: (Sims_pb2.AddBalloon.DISTRESS_TYPE, Sims_pb2.AddBalloon.MOTIVE_FAILURE_PRIORITY), 
 BalloonTypeEnum.SENTIMENT: (Sims_pb2.AddBalloon.SENTIMENT_TYPE, Sims_pb2.AddBalloon.SENTIMENT_PRIORITY)}