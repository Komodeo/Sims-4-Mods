# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\visiting\visiting_situation_common.py
# Compiled at: 2016-10-24 16:40:56
# Size of source mod 2**32: 755 bytes
from situations.situation import Situation
import situations.situation_complex, situations.situation_types

class VisitingNPCSituation(situations.situation_complex.SituationComplexCommon):
    INSTANCE_SUBCLASSES_ONLY = True
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _get_greeted_status(cls):
        return situations.situation_types.GreetedStatus.GREETED