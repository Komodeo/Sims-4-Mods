# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\selectable_sim_background_situation.py
# Compiled at: 2018-11-27 11:39:23
# Size of source mod 2**32: 2860 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.utils import classproperty
from situations.base_situation import _RequestUserData
from situations.bouncer.bouncer_request import SelectableSimRequestFactory
from situations.situation import Situation
from situations.situation_complex import SituationState, SituationComplexCommon, TunableSituationJobAndRoleState, SituationStateData
from situations.situation_types import SituationCreationUIOption, SituationSerializationOption

class _SelectableSimsBackgroundSituationState(SituationState):
    pass


class SelectableSimBackgroundSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'job_and_role': TunableSituationJobAndRoleState(description='\n            The job and role that the selectable Sims will be given.\n            ')}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classproperty
    def situation_serialization_option(cls):
        return SituationSerializationOption.DONT

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _SelectableSimsBackgroundSituationState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.job_and_role.job, cls.job_and_role.role_state)]

    @classmethod
    def default_job(cls):
        pass

    def start_situation(self):
        super().start_situation()
        self._change_state(_SelectableSimsBackgroundSituationState())

    def _issue_requests(self):
        request = SelectableSimRequestFactory(self, callback_data=_RequestUserData(role_state_type=(self.job_and_role.role_state)),
          job_type=(self.job_and_role.job),
          exclusivity=(self.exclusivity))
        self.manager.bouncer.submit_request(request)


lock_instance_tunables(SelectableSimBackgroundSituation, creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)