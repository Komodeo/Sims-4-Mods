# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\cafe_venue\barista_situation.py
# Compiled at: 2015-06-16 16:17:47
# Size of source mod 2**32: 947 bytes
from sims4.tuning.instances import lock_instance_tunables
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.complex.staff_member_situation import StaffMemberSituation
from situations.situation import Situation
from situations.situation_types import SituationCreationUIOption

class BaristaSituation(StaffMemberSituation):
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES


lock_instance_tunables(BaristaSituation, exclusivity=(BouncerExclusivityCategory.VENUE_EMPLOYEE),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  duration=0,
  _implies_greeted_status=False)