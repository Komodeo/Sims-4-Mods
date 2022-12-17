# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\visiting\ungreeted_player_visiting_npc_situation.py
# Compiled at: 2016-09-07 19:20:41
# Size of source mod 2**32: 5618 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from situations.base_situation import _RequestUserData
from situations.bouncer.bouncer_request import SelectableSimRequestFactory
from situations.situation_complex import SituationStateData
from situations.situation_types import SituationCreationUIOption
from situations.visiting.visiting_situation_common import VisitingNPCSituation
import build_buy, distributor.ops, role.role_state, sims4.tuning.tunable, situations.bouncer.bouncer_types, situations.situation_complex

class UngreetedPlayerVisitingNPCSituation(VisitingNPCSituation):
    INSTANCE_TUNABLES = {'ungreeted_player_sims': sims4.tuning.tunable.TunableTuple(situation_job=situations.situation_job.SituationJob.TunableReference(description='\n                    The job given to player sims in the ungreeted situation.\n                    '),
                                role_state=role.role_state.RoleState.TunableReference(description='\n                    The role state given to player sims in the ungreeted situation.\n                    '),
                                tuning_group=(GroupNames.ROLES))}

    @classmethod
    def _get_greeted_status(cls):
        return situations.situation_types.GreetedStatus.WAITING_TO_BE_GREETED

    @classmethod
    def _states(cls):
        return (SituationStateData(1, UngreetedPlayerVisitingNPCState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.ungreeted_player_sims.situation_job, cls.ungreeted_player_sims.role_state)]

    @classmethod
    def default_job(cls):
        return cls.ungreeted_player_sims.situation_job

    @classproperty
    def distribution_override(cls):
        return True

    def start_situation(self):
        super().start_situation()
        self._change_state(UngreetedPlayerVisitingNPCState())
        build_buy.register_build_buy_enter_callback(self._on_build_buy_enter)
        build_buy.register_build_buy_exit_callback(self._on_build_buy_exit)

    def load_situation(self):
        build_buy.register_build_buy_enter_callback(self._on_build_buy_enter)
        build_buy.register_build_buy_exit_callback(self._on_build_buy_exit)
        return super().load_situation()

    def _destroy(self):
        build_buy.unregister_build_buy_exit_callback(self._on_build_buy_exit)
        build_buy.unregister_build_buy_enter_callback(self._on_build_buy_enter)
        super()._destroy()

    def _issue_requests(self):
        request = SelectableSimRequestFactory(self, callback_data=_RequestUserData(role_state_type=(self.ungreeted_player_sims.role_state)),
          job_type=(self.ungreeted_player_sims.situation_job),
          exclusivity=(self.exclusivity))
        self.manager.bouncer.submit_request(request)

    def _on_sim_removed_from_situation_prematurely(self, sim, sim_job):
        if self.num_of_sims > 0:
            return
        else:
            return self.manager.is_player_greeted() or None
        self._self_destruct()

    def get_create_op(self, *args, **kwargs):
        return distributor.ops.SetWallsUpOrDown(True)

    def get_delete_op(self):
        return distributor.ops.SetWallsUpOrDown(False)

    def _on_build_buy_enter(self):
        op = distributor.ops.SetWallsUpOrDown(False)
        distributor.system.Distributor.instance().add_op(self, op)

    def _on_build_buy_exit(self):
        op = distributor.ops.SetWallsUpOrDown(True)
        distributor.system.Distributor.instance().add_op(self, op)


lock_instance_tunables(UngreetedPlayerVisitingNPCSituation, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.UNGREETED),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  duration=0)

class UngreetedPlayerVisitingNPCState(situations.situation_complex.SituationState):
    pass