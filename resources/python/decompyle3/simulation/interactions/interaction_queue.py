# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\interaction_queue.py
# Compiled at: 2020-02-25 18:42:10
# Size of source mod 2**32: 81649 bytes
from _weakrefset import WeakSet
from contextlib import contextmanager
import weakref
from carry.pick_up_sim_liability import PickUpSimLiability
from clock import ClockSpeedMode
from event_testing.resolver import InteractionResolver
from event_testing.results import TestResult
from interactions import ParticipantType, PipelineProgress
from interactions.base.interaction import InteractionFailureOptions
from interactions.base.interaction_constants import InteractionQueuePreparationStatus
from interactions.constraints import Nowhere
from interactions.context import InteractionBucketType, InteractionContext, InteractionSource, QueueInsertStrategy
from interactions.interaction_finisher import FinishingType
from interactions.priority import Priority, can_priority_displace, can_displace
from interactions.utils.interaction_liabilities import CANCEL_AOP_LIABILITY
from postures.transition_sequence import TransitionSequenceController, DerailReason
from sims.sim_log import log_interaction
from sims4.callback_utils import CallableList
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableRange, Tunable
from singletons import UNSET
import clock, element_utils, elements, gsi_handlers.sim_timeline_handlers, performance.counters, scheduling, services, sims4.log
__all__ = [
 'InteractionQueue', 'QueueView']
logger = sims4.log.Logger('Interaction Queue')

class BucketBase:
    __slots__ = '_sim_ref'

    def __init__(self, sim):
        self._sim_ref = sim.ref()

    @property
    def _sim(self):
        if self._sim_ref is not None:
            return self._sim_ref()

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def get_next_unblocked_interaction(self, blocked_sims_callback=None):
        for interaction in self:
            interaction.notify_queue_head()
            if interaction.is_finishing:
                continue
            return interaction

    def get_next_unblocked_interaction_cancel_incompatible(self, blocked_sims_callback=None):
        result = None
        to_cancel = []
        for interaction in self:
            interaction.notify_queue_head()
            if interaction.is_finishing:
                continue
            if interaction.is_super:
                if interaction.is_affordance_locked:
                    continue
                else:
                    sims_with_invalid_paths = interaction.get_sims_with_invalid_paths()
                if sims_with_invalid_paths:
                    if blocked_sims_callback is not None:
                        blocked_sims_callback(sims_with_invalid_paths)
                    else:
                        to_cancel.append(interaction)
                        logger.debug('Canceling incompatible interaction {} in bucket {}', interaction, self, owner='PI')
                    continue
            result = interaction
            break

        for interaction in to_cancel:
            interaction.cancel(FinishingType.INTERACTION_INCOMPATIBILITY, 'Canceled an incompatible interaction in a base bucket')

        return result

    def _append(self, interaction):
        raise NotImplementedError()

    def append(self, interaction):
        log_interaction('Enqueue', interaction)
        result = self._append(interaction)
        return result

    def _insert_next(self, interaction, insert_after=None):
        raise NotImplementedError()

    def insert_next(self, interaction, **kwargs):
        log_interaction('Enqueue_Next', interaction)
        result = (self._insert_next)(interaction, **kwargs)
        return result

    def _clear_interaction(self, interaction):
        raise NotImplementedError()

    def clear_interaction(self, interaction):
        ret = self._clear_interaction(interaction)
        if ret:
            interaction.on_removed_from_queue()
        return ret

    def remove_for_perform(self, interaction):
        if self._clear_interaction(interaction):
            return interaction

    def on_reset(self):
        for interaction in list(self):
            try:
                log_interaction('Reset', interaction)
                self.clear_interaction(interaction)
                interaction.on_reset()
            except Exception:
                logger.exception('Exception caught while clearing interaction from bucket:')


class BucketSingle(BucketBase):
    __slots__ = ('_interaction', )

    def __init__(self, sim):
        super().__init__(sim)
        self._interaction = None

    def __iter__(self):
        if self._interaction is not None:
            yield self._interaction

    def __len__(self):
        if self._interaction is not None:
            return 1
        return 0

    def _enqueue(self, interaction):
        if self._interaction is not None:
            if not self._interaction.is_finishing:
                if not self._interaction.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg=('Bucket Single Enqueue: {}'.format(interaction))):
                    return TestResult(False, 'Unable to cancel existing interaction ({}) in BucketSingle.'.format(self._interaction))
            self._interaction = interaction
            return TestResult.TRUE

    def _append(self, interaction):
        result = self._enqueue(interaction)
        return result

    def _insert_next(self, interaction, insert_after=None):
        return self._enqueue(interaction)

    def _clear_interaction(self, interaction):
        if self._interaction is interaction:
            self._interaction = None
            interaction.on_removed_from_queue()
            return True
        return False


class BucketList(BucketBase):
    __slots__ = ('_interactions', )

    def __init__(self, sim):
        self._sim_ref = sim.ref()
        self._interactions = []

    def __iter__(self):
        return iter(self._interactions)

    def __len__(self):
        return len(self._interactions)

    def _append(self, interaction):
        self._interactions.append(interaction)
        return TestResult.TRUE

    def _insert_next(self, interaction, insert_after=None):
        index = 0
        if insert_after is not None:
            for i, queued_interaction in enumerate(self._interactions):
                if not interaction.group_id == queued_interaction.group_id:
                    if queued_interaction is insert_after:
                        pass
                index = i + 1

        self._interactions.insert(index, interaction)
        return TestResult.TRUE

    def _clear_interaction(self, interaction):
        if not self._interactions or interaction not in self._interactions:
            return False
        self._interactions.remove(interaction)
        interaction.on_removed_from_queue()
        return True


class InteractionBucket(BucketList):
    __slots__ = ()

    def _append(self, interaction):
        if interaction.is_super or not len(self._interactions) == 0 or interaction.should_insert_in_queue_on_append():
            self._interactions.append(interaction)
        else:
            for i, queued_interaction in enumerate(self._interactions):
                if queued_interaction.is_super:
                    if queued_interaction.context.insert_strategy == QueueInsertStrategy.LAST:
                        if queued_interaction.transition is not None:
                            if queued_interaction.transition.running:
                                continue
                        self._interactions.insert(i, interaction)
                        break
            else:
                self._interactions.append(interaction)
            return TestResult.TRUE

    def get_next_unblocked_interaction(self, blocked_sims_callback=None):
        interactions_iter = iter(self)
        for interaction in interactions_iter:
            interaction.notify_queue_head()
            if interaction.is_finishing:
                continue
            if interaction.is_super:
                if interaction.is_affordance_locked:
                    continue
                else:
                    sims_with_invalid_paths = interaction.get_sims_with_invalid_paths()
                if sims_with_invalid_paths:
                    if blocked_sims_callback is not None:
                        blocked_sims_callback(sims_with_invalid_paths)
                    else:
                        interaction.on_incompatible_in_queue()
                    break
            return interaction

        for interaction in interactions_iter:
            if not interaction.is_super:
                interaction.notify_queue_head()
                if not interaction.is_finishing:
                    if interaction.super_interaction is not None:
                        if interaction.super_interaction in self._sim.si_state:
                            if not interaction.super_interaction.is_finishing:
                                return interaction


class AutonomyBucket(BucketList):
    __slots__ = ()
    get_next_unblocked_interaction = BucketBase.get_next_unblocked_interaction_cancel_incompatible


class SocialAdjustmentBucket(BucketSingle):
    __slots__ = ()
    get_next_unblocked_interaction = BucketBase.get_next_unblocked_interaction_cancel_incompatible


class VehicleBodyCancelAOPBucket(BucketSingle):
    __slots__ = ()


class BodyCancelAOPBucket(BucketList):
    __slots__ = ()


class CarryCancelAOPBucket(BucketList):
    __slots__ = ()


class InteractionQueue(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'max_interactions':TunableRange(description='\n            The maximum number of visible interactions in the queue, including\n            running interactions. If this value is greater than 10, the\n            interaction queue .swf must be updated.\n            ',
       tunable_type=int,
       default=8,
       minimum=0,
       maximum=10), 
     'always_start_inertial':Tunable(description="\n            If this is checked, interactions queued on this Sim always start\n            inertial, regardless of what the content's tuning might say.\n            \n            This makes Sims more responsive to commands but less sticky and less\n            likely to complete any given task.\n            ",
       tunable_type=bool,
       default=False)}

    def __init__(self, sim, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim_ref = sim.ref()
        self._running = None
        self._social_adjustment = SocialAdjustmentBucket(sim)
        self._carry_cancel_replacements = CarryCancelAOPBucket(sim)
        self._interactions = InteractionBucket(sim)
        self._body_cancel_replacements = BodyCancelAOPBucket(sim)
        self._vehicle_cancel_replacements = VehicleBodyCancelAOPBucket(sim)
        self._autonomy = AutonomyBucket(sim)
        self._buckets = (
         self._social_adjustment,
         self._carry_cancel_replacements,
         self._vehicle_cancel_replacements,
         self._interactions,
         self._body_cancel_replacements,
         self._autonomy)
        self.transition_controller = None
        self._locked = False
        self._being_destroyed = False
        self._must_run_next_interaction = None
        self.on_head_changed = CallableList()
        self._head_cache = UNSET
        self._si_state_changed_callback_sims = set()
        self._suppress_head_depth = None

    @property
    def sim(self):
        if self._sim_ref is not None:
            return self._sim_ref()

    def __repr__(self):
        return 'InteractionQueue for {}'.format(self.sim)

    def __iter__(self):
        if self.running is not None:
            yield self.running
        for bucket in self._buckets:
            for interaction in bucket:
                if interaction is self.running:
                    continue
                else:
                    yield interaction

    def __len__(self):
        return len(set(self))

    def log_interaction_queue(self, logger_func):
        logger_func('Interaction queue info for {}', self.sim)
        for bucket in list(self._buckets):
            for interaction in bucket:
                logger_func('    {}'.format(interaction))

        if self.running is not None:
            logger_func('Running interaction {}', self.sim)
            logger_func('    {}'.format(self.running))

    def _process_one_interaction_gen(self, timeline, interaction):
        result = False
        entered_si = False
        required_sims = None
        performance.counters.add_counter('PerfNumInteractions', 1)
        try:
            interaction.pipeline_progress = PipelineProgress.RUNNING
            if interaction.is_super:
                entered_si = yield from interaction.enter_si_gen(timeline)
            else:
                entered_si = True
            if entered_si:
                required_sims = interaction.required_sims(for_threading=True)
                for sim in required_sims:
                    sim.queue.running = interaction

                result = yield from self.run_interaction_gen(timeline, interaction)
        finally:
            if not result:
                interaction.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg='process_one_interaction_gen: interaction failed to run.')
            if not entered_si:
                interaction.on_removed_from_queue()
            if required_sims:
                for sim in required_sims:
                    sim.queue.running = None

        return result
        if False:
            yield None

    def run_interaction_gen(self, timeline, interaction, source_interaction=None, apply_posture_state=True):
        if interaction.is_finishing:
            return False
        interaction_parameters = {}
        interaction_parameters['interaction_starting'] = True
        result = (interaction.test)(skip_safe_tests=True, **interaction_parameters)
        if not result:
            msg = 'Test failed at run_interaction: {}'.format(result)
            interaction.cancel((FinishingType.FAILED_TESTS), cancel_reason_msg=msg)
            log_interaction('Failed', interaction, msg=msg)
            return False
        log_interaction('Running', interaction)
        if interaction.target:
            if interaction.target.objectage_component:
                interaction.target.update_last_used()
        if not interaction.disable_transitions:
            interaction.apply_posture_state(self.sim.posture_state)
        if not interaction.is_superand self._must_run_next_interaction is not Noneand interaction.transition is not None and self._must_run_next_interaction is not None or interaction is not self._must_run_next_interaction:
            if source_interaction is None or self._must_run_next_interaction is not source_interaction:
                self._must_run_next_interaction.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg=('InteractionQueue: run_interaction: must_run_next: {} canceled by {}'.format(self._must_run_next_interaction, interaction)))
                self._must_run_next_interaction = None
            try:
                result, failure_reason = yield from interaction.perform_gen(timeline)
            finally:
                interaction.on_removed_from_queue()

            if result:
                if interaction.is_super and interaction.suspended:
                    log_interaction('Staged', interaction)
                else:
                    log_interaction('Done', interaction)
            else:
                log_interaction('Failed', interaction, msg=failure_reason)
            return result
        if False:
            yield None

    def process_one_interaction_gen--- This code section failed: ---

 L. 631         0  LOAD_FAST                'self'
                2  LOAD_METHOD              get_head
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'head_first'

 L. 634      8_10  SETUP_LOOP         1084  'to 1084'
             12_0  COME_FROM          1080  '1080'
             12_1  COME_FROM           704  '704'
             12_2  COME_FROM           698  '698'
             12_3  COME_FROM           688  '688'
             12_4  COME_FROM           480  '480'
             12_5  COME_FROM           416  '416'
             12_6  COME_FROM           354  '354'
             12_7  COME_FROM           336  '336'
             12_8  COME_FROM           186  '186'
             12_9  COME_FROM           170  '170'
            12_10  COME_FROM           158  '158'
            12_11  COME_FROM           142  '142'
            12_12  COME_FROM           136  '136'
            12_13  COME_FROM           130  '130'

 L. 641        12  LOAD_FAST                'self'
               14  LOAD_METHOD              get_head
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  STORE_FAST               'head'

 L. 643        20  LOAD_FAST                'head'
               22  LOAD_CONST               None
               24  COMPARE_OP               is
               26  POP_JUMP_IF_TRUE     42  'to 42'
               28  LOAD_FAST                'head'
               30  LOAD_ATTR                is_finishing
               32  POP_JUMP_IF_TRUE     42  'to 42'
               34  LOAD_FAST                'head'
               36  LOAD_FAST                'head_first'
               38  COMPARE_OP               is-not
               40  POP_JUMP_IF_FALSE    44  'to 44'
             42_0  COME_FROM            32  '32'
             42_1  COME_FROM            26  '26'

 L. 647        42  BREAK_LOOP       
             44_0  COME_FROM            40  '40'

 L. 651        44  LOAD_FAST                'head'
               46  LOAD_ATTR                test
               48  LOAD_FAST                'head'
               50  LOAD_METHOD              skip_test_on_execute
               52  CALL_METHOD_0         0  '0 positional arguments'
               54  LOAD_CONST               ('skip_safe_tests',)
               56  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               58  STORE_FAST               'result'

 L. 652        60  LOAD_FAST                'result'
               62  POP_JUMP_IF_TRUE    188  'to 188'

 L. 656        64  LOAD_FAST                'head'
               66  LOAD_METHOD              get_name
               68  CALL_METHOD_0         0  '0 positional arguments'
               70  STORE_FAST               'old_name'

 L. 657        72  LOAD_FAST                'head'
               74  LOAD_METHOD              get_icon_info
               76  CALL_METHOD_0         0  '0 positional arguments'
               78  STORE_FAST               'old_icon_info'

 L. 658        80  LOAD_FAST                'result'
               82  LOAD_ATTR                reason
               84  LOAD_CONST               None
               86  COMPARE_OP               is-not
               88  POP_JUMP_IF_FALSE    96  'to 96'
               90  LOAD_FAST                'result'
               92  LOAD_ATTR                reason
               94  JUMP_FORWARD         98  'to 98'
             96_0  COME_FROM            88  '88'
               96  LOAD_STR                 'Interaction Queue head interaction failed tests'
             98_0  COME_FROM            94  '94'
               98  STORE_FAST               'reason'

 L. 659       100  LOAD_FAST                'head'
              102  LOAD_ATTR                cancel
              104  LOAD_GLOBAL              FinishingType
              106  LOAD_ATTR                FAILED_TESTS
              108  LOAD_FAST                'reason'
              110  LOAD_CONST               ('cancel_reason_msg',)
              112  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              114  POP_TOP          

 L. 660       116  LOAD_FAST                'self'
              118  LOAD_METHOD              remove_for_perform
              120  LOAD_FAST                'head'
              122  CALL_METHOD_1         1  '1 positional argument'
              124  POP_TOP          

 L. 661       126  LOAD_FAST                'head'
              128  LOAD_ATTR                is_user_directed
              130  POP_JUMP_IF_FALSE_LOOP    12  'to 12'
              132  LOAD_FAST                'head'
              134  LOAD_ATTR                visible
              136  POP_JUMP_IF_FALSE_LOOP    12  'to 12'
              138  LOAD_FAST                'head'
              140  LOAD_ATTR                is_super
              142  POP_JUMP_IF_FALSE_LOOP    12  'to 12'

 L. 668       144  LOAD_FAST                'head'
              146  LOAD_ATTR                target_in_inventory_when_queued
              148  POP_JUMP_IF_FALSE   172  'to 172'

 L. 669       150  LOAD_FAST                'head'
              152  LOAD_ATTR                target
              154  LOAD_CONST               None
              156  COMPARE_OP               is
              158  POP_JUMP_IF_TRUE_LOOP    12  'to 12'
              160  LOAD_FAST                'head'
              162  LOAD_ATTR                target
              164  LOAD_METHOD              is_in_inventory
              166  CALL_METHOD_0         0  '0 positional arguments'
              168  POP_JUMP_IF_TRUE    172  'to 172'

 L. 670       170  CONTINUE             12  'to 12'
            172_0  COME_FROM           168  '168'
            172_1  COME_FROM           148  '148'

 L. 671       172  LOAD_FAST                'self'
              174  LOAD_METHOD              insert_route_failure_interaction
              176  LOAD_FAST                'head'
              178  LOAD_FAST                'old_name'
              180  LOAD_FAST                'old_icon_info'
              182  CALL_METHOD_3         3  '3 positional arguments'
              184  POP_TOP          

 L. 672       186  CONTINUE             12  'to 12'
            188_0  COME_FROM            62  '62'

 L. 676       188  LOAD_FAST                'self'
              190  LOAD_ATTR                sim
              192  LOAD_ATTR                si_state
              194  LOAD_METHOD              process_gen
              196  LOAD_FAST                'timeline'
              198  CALL_METHOD_1         1  '1 positional argument'
              200  GET_YIELD_FROM_ITER
              202  LOAD_CONST               None
              204  YIELD_FROM       
              206  POP_TOP          

 L. 678       208  LOAD_FAST                'head'
              210  LOAD_ATTR                is_super
          212_214  POP_JUMP_IF_TRUE    418  'to 418'

 L. 679       216  LOAD_FAST                'head'
              218  LOAD_ATTR                pipeline_progress
              220  LOAD_GLOBAL              PipelineProgress
              222  LOAD_ATTR                QUEUED
              224  COMPARE_OP               ==
          226_228  POP_JUMP_IF_FALSE   356  'to 356'

 L. 680       230  LOAD_GLOBAL              log_interaction
              232  LOAD_STR                 'Preparing'
              234  LOAD_FAST                'head'
              236  CALL_FUNCTION_2       2  '2 positional arguments'
              238  POP_TOP          

 L. 682       240  SETUP_EXCEPT        262  'to 262'

 L. 683       242  LOAD_FAST                'head'
              244  LOAD_METHOD              prepare_gen
              246  LOAD_FAST                'timeline'
              248  CALL_METHOD_1         1  '1 positional argument'
              250  GET_YIELD_FROM_ITER
              252  LOAD_CONST               None
              254  YIELD_FROM       
              256  STORE_FAST               'result'
              258  POP_BLOCK        
              260  JUMP_FORWARD        288  'to 288'
            262_0  COME_FROM_EXCEPT    240  '240'

 L. 684       262  POP_TOP          
              264  POP_TOP          
              266  POP_TOP          

 L. 685       268  LOAD_GLOBAL              logger
              270  LOAD_METHOD              exception
              272  LOAD_STR                 'Error in prepare_gen for mixer interaction'
              274  CALL_METHOD_1         1  '1 positional argument'
              276  POP_TOP          

 L. 686       278  LOAD_CONST               False
              280  STORE_FAST               'result'
              282  POP_EXCEPT       
              284  JUMP_FORWARD        288  'to 288'
              286  END_FINALLY      
            288_0  COME_FROM           284  '284'
            288_1  COME_FROM           260  '260'

 L. 687       288  LOAD_FAST                'result'
              290  LOAD_GLOBAL              InteractionQueuePreparationStatus
              292  LOAD_ATTR                FAILURE
              294  COMPARE_OP               !=
          296_298  POP_JUMP_IF_FALSE   338  'to 338'

 L. 691       300  LOAD_FAST                'result'
              302  LOAD_GLOBAL              InteractionQueuePreparationStatus
              304  LOAD_ATTR                SUCCESS
              306  COMPARE_OP               ==
          308_310  POP_JUMP_IF_FALSE   320  'to 320'

 L. 692       312  LOAD_GLOBAL              PipelineProgress
              314  LOAD_ATTR                PREPARED
              316  LOAD_FAST                'head'
              318  STORE_ATTR               pipeline_progress
            320_0  COME_FROM           308  '308'

 L. 693       320  LOAD_FAST                'result'
              322  LOAD_GLOBAL              InteractionQueuePreparationStatus
              324  LOAD_ATTR                NEEDS_DERAIL
              326  COMPARE_OP               ==
          328_330  POP_JUMP_IF_FALSE   354  'to 354'

 L. 694       332  LOAD_CONST               None
              334  RETURN_VALUE     
              336  JUMP_LOOP            12  'to 12'
            338_0  COME_FROM           296  '296'

 L. 696       338  LOAD_FAST                'head'
              340  LOAD_ATTR                cancel
              342  LOAD_GLOBAL              FinishingType
              344  LOAD_ATTR                INTERACTION_QUEUE
              346  LOAD_STR                 'Failed to Prepare Interaction.'
              348  LOAD_CONST               ('cancel_reason_msg',)
              350  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              352  POP_TOP          
            354_0  COME_FROM           328  '328'

 L. 697       354  CONTINUE             12  'to 12'
            356_0  COME_FROM           226  '226'

 L. 699       356  LOAD_FAST                'head'
              358  LOAD_ATTR                prepared
          360_362  POP_JUMP_IF_FALSE  1080  'to 1080'

 L. 700       364  LOAD_FAST                'head'
              366  LOAD_METHOD              pre_process_interaction
              368  CALL_METHOD_0         0  '0 positional arguments'
              370  POP_TOP          

 L. 702       372  SETUP_FINALLY       396  'to 396'

 L. 703       374  LOAD_FAST                'self'
              376  LOAD_METHOD              _process_one_interaction_gen
              378  LOAD_FAST                'timeline'
              380  LOAD_FAST                'head'
              382  CALL_METHOD_2         2  '2 positional arguments'
              384  GET_YIELD_FROM_ITER
              386  LOAD_CONST               None
              388  YIELD_FROM       
              390  POP_TOP          
              392  POP_BLOCK        
              394  LOAD_CONST               None
            396_0  COME_FROM_FINALLY   372  '372'

 L. 705       396  LOAD_FAST                'self'
              398  LOAD_METHOD              remove_for_perform
              400  LOAD_FAST                'head'
              402  CALL_METHOD_1         1  '1 positional argument'
              404  POP_TOP          
              406  END_FINALLY      

 L. 707       408  LOAD_FAST                'head'
              410  LOAD_METHOD              post_process_interaction
              412  CALL_METHOD_0         0  '0 positional arguments'
              414  POP_TOP          
              416  JUMP_LOOP            12  'to 12'
            418_0  COME_FROM           212  '212'

 L. 709       418  LOAD_FAST                'head'
              420  LOAD_ATTR                pipeline_progress
              422  LOAD_GLOBAL              PipelineProgress
              424  LOAD_ATTR                QUEUED
              426  COMPARE_OP               ==
          428_430  POP_JUMP_IF_FALSE   496  'to 496'

 L. 710       432  LOAD_GLOBAL              PipelineProgress
              434  LOAD_ATTR                PRE_TRANSITIONING
              436  LOAD_FAST                'head'
              438  STORE_ATTR               pipeline_progress

 L. 711       440  LOAD_FAST                'head'
              442  LOAD_METHOD              run_pre_transition_behavior
              444  CALL_METHOD_0         0  '0 positional arguments'
          446_448  POP_JUMP_IF_TRUE    482  'to 482'

 L. 712       450  LOAD_GLOBAL              log_interaction
              452  LOAD_STR                 'PreTransition'
              454  LOAD_FAST                'head'
              456  LOAD_STR                 'Failed'
              458  LOAD_CONST               ('msg',)
              460  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              462  POP_TOP          

 L. 713       464  LOAD_FAST                'head'
              466  LOAD_ATTR                cancel
              468  LOAD_GLOBAL              FinishingType
              470  LOAD_ATTR                TRANSITION_FAILURE
              472  LOAD_STR                 'Pre Transition Behavior Failed.'
              474  LOAD_CONST               ('cancel_reason_msg',)
              476  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              478  POP_TOP          

 L. 714       480  CONTINUE             12  'to 12'
            482_0  COME_FROM           446  '446'

 L. 715       482  LOAD_GLOBAL              log_interaction
              484  LOAD_STR                 'PreTransition'
              486  LOAD_FAST                'head'
              488  LOAD_STR                 'Succeeded'
              490  LOAD_CONST               ('msg',)
              492  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              494  POP_TOP          
            496_0  COME_FROM           428  '428'

 L. 717       496  LOAD_FAST                'head'
              498  LOAD_ATTR                pipeline_progress
              500  LOAD_GLOBAL              PipelineProgress
              502  LOAD_ATTR                PRE_TRANSITIONING
              504  COMPARE_OP               ==
          506_508  POP_JUMP_IF_FALSE   700  'to 700'

 L. 719       510  LOAD_GLOBAL              log_interaction
              512  LOAD_STR                 'Preparing'
              514  LOAD_FAST                'head'
              516  CALL_FUNCTION_2       2  '2 positional arguments'
              518  POP_TOP          

 L. 720       520  SETUP_EXCEPT        546  'to 546'

 L. 721       522  LOAD_FAST                'head'
              524  LOAD_ATTR                prepare_gen
              526  LOAD_FAST                'timeline'
              528  LOAD_CONST               True
              530  LOAD_CONST               ('cancel_incompatible_carry_interactions',)
              532  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              534  GET_YIELD_FROM_ITER
              536  LOAD_CONST               None
              538  YIELD_FROM       
              540  STORE_FAST               'result'
              542  POP_BLOCK        
              544  JUMP_FORWARD        608  'to 608'
            546_0  COME_FROM_EXCEPT    520  '520'

 L. 722       546  DUP_TOP          
              548  LOAD_GLOBAL              scheduling
              550  LOAD_ATTR                HardStopError
              552  COMPARE_OP               exception-match
          554_556  POP_JUMP_IF_FALSE   570  'to 570'
              558  POP_TOP          
              560  POP_TOP          
              562  POP_TOP          

 L. 723       564  RAISE_VARARGS_0       0  'reraise'
              566  POP_EXCEPT       
              568  JUMP_FORWARD        608  'to 608'
            570_0  COME_FROM           554  '554'

 L. 724       570  DUP_TOP          
              572  LOAD_GLOBAL              Exception
              574  COMPARE_OP               exception-match
          576_578  POP_JUMP_IF_FALSE   606  'to 606'
              580  POP_TOP          
              582  POP_TOP          
              584  POP_TOP          

 L. 725       586  LOAD_GLOBAL              logger
              588  LOAD_METHOD              exception
              590  LOAD_STR                 'Exception in prepare_gen for super interaction.'
              592  CALL_METHOD_1         1  '1 positional argument'
              594  POP_TOP          

 L. 726       596  LOAD_GLOBAL              InteractionQueuePreparationStatus
              598  LOAD_ATTR                FAILURE
              600  STORE_FAST               'result'
              602  POP_EXCEPT       
              604  JUMP_FORWARD        608  'to 608'
            606_0  COME_FROM           576  '576'
              606  END_FINALLY      
            608_0  COME_FROM           604  '604'
            608_1  COME_FROM           568  '568'
            608_2  COME_FROM           544  '544'

 L. 727       608  LOAD_FAST                'result'
              610  LOAD_GLOBAL              InteractionQueuePreparationStatus
              612  LOAD_ATTR                NEEDS_DERAIL
              614  COMPARE_OP               ==
          616_618  POP_JUMP_IF_FALSE   660  'to 660'

 L. 730       620  LOAD_FAST                'head'
              622  LOAD_ATTR                sim
              624  LOAD_ATTR                get_idle_element
              626  LOAD_CONST               1
              628  LOAD_CONST               ('duration',)
              630  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              632  UNPACK_SEQUENCE_2     2 
              634  STORE_FAST               'idle_element'
              636  STORE_FAST               '_'

 L. 731       638  LOAD_GLOBAL              element_utils
              640  LOAD_METHOD              run_child
              642  LOAD_FAST                'timeline'
              644  LOAD_FAST                'idle_element'
              646  CALL_METHOD_2         2  '2 positional arguments'
              648  GET_YIELD_FROM_ITER
              650  LOAD_CONST               None
              652  YIELD_FROM       
              654  POP_TOP          

 L. 732       656  LOAD_CONST               None
              658  RETURN_VALUE     
            660_0  COME_FROM           616  '616'

 L. 733       660  LOAD_FAST                'result'
              662  LOAD_GLOBAL              InteractionQueuePreparationStatus
              664  LOAD_ATTR                FAILURE
              666  COMPARE_OP               ==
          668_670  POP_JUMP_IF_FALSE   690  'to 690'

 L. 734       672  LOAD_FAST                'head'
              674  LOAD_ATTR                cancel
              676  LOAD_GLOBAL              FinishingType
              678  LOAD_ATTR                INTERACTION_QUEUE
              680  LOAD_STR                 'Failed to Prepare Interaction.'
              682  LOAD_CONST               ('cancel_reason_msg',)
              684  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              686  POP_TOP          
              688  JUMP_LOOP            12  'to 12'
            690_0  COME_FROM           668  '668'

 L. 736       690  LOAD_GLOBAL              PipelineProgress
              692  LOAD_ATTR                PREPARED
              694  LOAD_FAST                'head'
              696  STORE_ATTR               pipeline_progress

 L. 737       698  CONTINUE             12  'to 12'
            700_0  COME_FROM           506  '506'

 L. 739       700  LOAD_FAST                'head'
              702  LOAD_ATTR                prepared
              704  POP_JUMP_IF_FALSE_LOOP    12  'to 12'

 L. 740       706  LOAD_FAST                'head'
              708  LOAD_ATTR                required_sims
              710  LOAD_CONST               True
              712  LOAD_CONST               ('for_threading',)
              714  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              716  STORE_FAST               'required_sims'

 L. 742       718  LOAD_FAST                'head'
              720  LOAD_ATTR                transition
              722  LOAD_CONST               None
              724  COMPARE_OP               is
          726_728  POP_JUMP_IF_FALSE   740  'to 740'

 L. 743       730  LOAD_GLOBAL              TransitionSequenceController
              732  LOAD_FAST                'head'
              734  CALL_FUNCTION_1       1  '1 positional argument'
              736  LOAD_FAST                'head'
              738  STORE_ATTR               transition
            740_0  COME_FROM           726  '726'

 L. 745       740  SETUP_LOOP          766  'to 766'
              742  LOAD_FAST                'required_sims'
              744  GET_ITER         
            746_0  COME_FROM           760  '760'
              746  FOR_ITER            764  'to 764'
              748  STORE_FAST               'required_sim'

 L. 746       750  LOAD_FAST                'head'
              752  LOAD_ATTR                transition
              754  LOAD_FAST                'required_sim'
              756  LOAD_ATTR                queue
              758  STORE_ATTR               transition_controller
          760_762  JUMP_LOOP           746  'to 746'
              764  POP_BLOCK        
            766_0  COME_FROM_LOOP      740  '740'

 L. 748       766  LOAD_GLOBAL              services
              768  LOAD_METHOD              game_clock_service
              770  CALL_METHOD_0         0  '0 positional arguments'
              772  LOAD_ATTR                clock_speed
              774  LOAD_GLOBAL              ClockSpeedMode
              776  LOAD_ATTR                PAUSED
              778  COMPARE_OP               ==
          780_782  POP_JUMP_IF_FALSE   844  'to 844'

 L. 749       784  LOAD_GLOBAL              services
              786  LOAD_METHOD              current_zone
              788  CALL_METHOD_0         0  '0 positional arguments'
              790  LOAD_ATTR                force_process_transitions
          792_794  POP_JUMP_IF_TRUE    844  'to 844'

 L. 751       796  LOAD_GLOBAL              element_utils
              798  LOAD_METHOD              build_element
              800  LOAD_GLOBAL              element_utils
              802  LOAD_METHOD              sleep_until_next_tick_element
              804  CALL_METHOD_0         0  '0 positional arguments'

 L. 752       806  LOAD_GLOBAL              elements
              808  LOAD_METHOD              SoftSleepElement
              810  LOAD_GLOBAL              clock
              812  LOAD_METHOD              interval_in_sim_seconds
              814  LOAD_CONST               1.0
              816  CALL_METHOD_1         1  '1 positional argument'
              818  CALL_METHOD_1         1  '1 positional argument'
              820  BUILD_TUPLE_2         2 
              822  CALL_METHOD_1         1  '1 positional argument'
              824  STORE_FAST               'sleep_paused_element'

 L. 753       826  LOAD_GLOBAL              element_utils
              828  LOAD_METHOD              run_child
              830  LOAD_FAST                'timeline'
              832  LOAD_FAST                'sleep_paused_element'
              834  CALL_METHOD_2         2  '2 positional arguments'
              836  GET_YIELD_FROM_ITER
              838  LOAD_CONST               None
              840  YIELD_FROM       
              842  POP_TOP          
            844_0  COME_FROM           792  '792'
            844_1  COME_FROM           780  '780'

 L. 755       844  LOAD_FAST                'head'
              846  LOAD_ATTR                transition
              848  LOAD_CONST               None
              850  COMPARE_OP               is
          852_854  POP_JUMP_IF_FALSE   878  'to 878'

 L. 756       856  LOAD_GLOBAL              logger
              858  LOAD_ATTR                error
              860  LOAD_STR                 'Interaction {} transition is None.'
              862  LOAD_FAST                'head'
              864  LOAD_STR                 'jdimailig'
              866  LOAD_CONST               ('owner',)
              868  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              870  POP_TOP          

 L. 757       872  LOAD_CONST               False
              874  STORE_FAST               'result'
              876  JUMP_FORWARD        942  'to 942'
            878_0  COME_FROM           852  '852'

 L. 759       878  LOAD_GLOBAL              gsi_handlers
              880  LOAD_ATTR                sim_timeline_handlers
              882  LOAD_METHOD              archive_sim_timeline_context_manager
              884  LOAD_FAST                'self'
              886  LOAD_ATTR                sim
              888  LOAD_STR                 'InteractionQueue'
              890  LOAD_STR                 'Run Transition'
              892  LOAD_FAST                'head'
              894  CALL_METHOD_4         4  '4 positional arguments'
              896  SETUP_WITH          936  'to 936'
              898  POP_TOP          

 L. 761       900  LOAD_FAST                'head'
              902  LOAD_ATTR                sim
              904  LOAD_ATTR                ui_manager
              906  LOAD_METHOD              running_transition
              908  LOAD_FAST                'head'
              910  CALL_METHOD_1         1  '1 positional argument'
              912  POP_TOP          

 L. 763       914  LOAD_FAST                'head'
              916  LOAD_ATTR                transition
              918  LOAD_METHOD              run_transitions
              920  LOAD_FAST                'timeline'
              922  CALL_METHOD_1         1  '1 positional argument'
              924  GET_YIELD_FROM_ITER
              926  LOAD_CONST               None
              928  YIELD_FROM       
              930  STORE_FAST               'result'
              932  POP_BLOCK        
              934  LOAD_CONST               None
            936_0  COME_FROM_WITH      896  '896'
              936  WITH_CLEANUP_START
              938  WITH_CLEANUP_FINISH
              940  END_FINALLY      
            942_0  COME_FROM           876  '876'

 L. 765       942  SETUP_LOOP          966  'to 966'
              944  LOAD_FAST                'required_sims'
              946  GET_ITER         
            948_0  COME_FROM           960  '960'
              948  FOR_ITER            964  'to 964'
              950  STORE_FAST               'required_sim'

 L. 766       952  LOAD_CONST               None
              954  LOAD_FAST                'required_sim'
              956  LOAD_ATTR                queue
              958  STORE_ATTR               transition_controller
          960_962  JUMP_LOOP           948  'to 948'
              964  POP_BLOCK        
            966_0  COME_FROM_LOOP      942  '942'

 L. 768       966  LOAD_FAST                'head'
              968  LOAD_ATTR                transition
              970  LOAD_CONST               None
              972  COMPARE_OP               is-not
          974_976  POP_JUMP_IF_FALSE  1010  'to 1010'

 L. 769       978  LOAD_FAST                'head'
              980  LOAD_ATTR                transition
              982  LOAD_ATTR                canceled
          984_986  POP_JUMP_IF_FALSE   996  'to 996'

 L. 770       988  LOAD_CONST               None
              990  LOAD_FAST                'head'
              992  STORE_ATTR               transition
              994  JUMP_FORWARD       1010  'to 1010'
            996_0  COME_FROM           984  '984'

 L. 771       996  LOAD_FAST                'head'
              998  LOAD_ATTR                transition
             1000  LOAD_ATTR                any_derailed
         1002_1004  POP_JUMP_IF_FALSE  1010  'to 1010'

 L. 772      1006  LOAD_CONST               None
             1008  RETURN_VALUE     
           1010_0  COME_FROM          1002  '1002'
           1010_1  COME_FROM           994  '994'
           1010_2  COME_FROM           974  '974'

 L. 774      1010  LOAD_FAST                'result'
         1012_1014  POP_JUMP_IF_TRUE   1024  'to 1024'
             1016  LOAD_FAST                'head'
             1018  LOAD_ATTR                is_finishing
         1020_1022  POP_JUMP_IF_FALSE  1060  'to 1060'
           1024_0  COME_FROM          1012  '1012'

 L. 775      1024  LOAD_CONST               None
             1026  LOAD_FAST                'head'
             1028  STORE_ATTR               transition

 L. 777      1030  LOAD_FAST                'head'
             1032  LOAD_ATTR                is_finishing
         1034_1036  POP_JUMP_IF_FALSE  1050  'to 1050'

 L. 782      1038  LOAD_FAST                'self'
             1040  LOAD_METHOD              on_interaction_canceled
             1042  LOAD_FAST                'head'
             1044  CALL_METHOD_1         1  '1 positional argument'
             1046  POP_TOP          
             1048  JUMP_FORWARD       1060  'to 1060'
           1050_0  COME_FROM          1034  '1034'

 L. 784      1050  LOAD_FAST                'self'
             1052  LOAD_METHOD              remove_for_perform
             1054  LOAD_FAST                'head'
             1056  CALL_METHOD_1         1  '1 positional argument'
             1058  POP_TOP          
           1060_0  COME_FROM          1048  '1048'
           1060_1  COME_FROM          1020  '1020'

 L. 786      1060  LOAD_FAST                'self'
             1062  LOAD_ATTR                sim
             1064  LOAD_ATTR                si_state
             1066  LOAD_METHOD              process_gen
             1068  LOAD_FAST                'timeline'
             1070  CALL_METHOD_1         1  '1 positional argument'
             1072  GET_YIELD_FROM_ITER
             1074  LOAD_CONST               None
             1076  YIELD_FROM       
             1078  POP_TOP          
           1080_0  COME_FROM           360  '360'
             1080  JUMP_LOOP            12  'to 12'
             1082  POP_BLOCK        
           1084_0  COME_FROM_LOOP        8  '8'

 L. 791      1084  LOAD_FAST                'self'
             1086  LOAD_ATTR                sim
             1088  LOAD_ATTR                si_state
             1090  LOAD_METHOD              process_gen
             1092  LOAD_FAST                'timeline'
             1094  CALL_METHOD_1         1  '1 positional argument'
             1096  GET_YIELD_FROM_ITER
             1098  LOAD_CONST               None
             1100  YIELD_FROM       
             1102  POP_TOP          

Parse error at or near `CONTINUE' instruction at offset 354

    def insert_route_failure_interaction(self, interaction, interaction_name, interaction_icon_info):
        resolver = InteractionResolver(interaction.aop.affordance, interaction)
        anim_overrides = None
        for test_and_override in InteractionFailureOptions.FAILURE_REASON_TESTS:
            result = test_and_override.test_set.run_tests(resolver)
            if result:
                anim_overrides = test_and_override.anim_override
                break

        context = InteractionContext((interaction.sim), (InteractionContext.SOURCE_SCRIPT),
          (Priority.High),
          insert_strategy=(QueueInsertStrategy.NEXT))
        result = self.sim.push_super_affordance((InteractionFailureOptions.ROUTE_FAILURE_AFFORDANCE), (interaction.target),
          context, anim_overrides=anim_overrides,
          interaction_name=interaction_name,
          interaction_icon_info=interaction_icon_info)

    def needs_cancel_aop(self, aop, context):
        bucket = self._get_bucket_for_context(context)
        for cancel_si in bucket:
            if context.group_id == cancel_si.group_id:
                return False

        if self.sim.si_state.is_running_affordance((aop.affordance), target=(aop.target)):
            return False
        return True

    @property
    def transition_in_progress(self):
        return self.transition_controller is not None and not self.transition_controller.canceled

    @property
    def running(self):
        if self.transition_controller is not None:
            return self.transition_controller.interaction
        return self._running

    @running.setter
    def running(self, value):
        self._running = value
        if value is not None:
            if value.is_super:
                if self._must_run_next_interaction is not None:
                    if value is not self._must_run_next_interaction:
                        self._must_run_next_interaction.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg='Interaction is not the must_run_next interaction')

    def visible_len(self):
        return sum((1 for interaction in self if interaction.visible_as_interaction if self.running != interaction))

    def can_queue_visible_interaction(self):
        return self.visible_len() < self.max_interactions

    @contextmanager
    def _head_change_watcher(self, defer_on_head_change_call=False):
        if self._suppress_head_depth is None:
            old_head = self.get_head()
            if defer_on_head_change_call:
                self._suppress_head_depth = 1
        else:
            self._suppress_head_depth += 1
        try:
            yield
        finally:
            if self._suppress_head_depth is not None:
                self._suppress_head_depth -= 1
                if self._suppress_head_depth == 0:
                    self._suppress_head_depth = None
            if self._suppress_head_depth is None:
                if self._get_head() != old_head:
                    self.on_head_changed()

    def remove_for_perform(self, interaction):
        with self._head_change_watcher():
            for bucket in self._buckets:
                if bucket.remove_for_perform(interaction):
                    if interaction is self._must_run_next_interaction:
                        self._must_run_next_interaction = None
                    else:
                        return interaction

    def clear_must_run_next_interaction(self, interaction):
        if interaction is self._must_run_next_interaction:
            self._must_run_next_interaction = None

    def _set_si_state_on_changed_callbacks_for_head(self, sims):
        for sim in self._si_state_changed_callback_sims:
            if sim not in sims:
                sim.si_state.on_changed.remove(self.on_si_phase_change)

        self._si_state_changed_callback_sims &= sims
        for sim in sims:
            if sim in self._si_state_changed_callback_sims:
                continue
            else:
                sim.si_state.on_changed.append(self.on_si_phase_change)
                self._si_state_changed_callback_sims.add(sim)

    def clear_head_cache(self):
        self._head_cache = UNSET
        self._set_si_state_on_changed_callbacks_for_head(set())

    def peek_head(self):
        if self._head_cache is UNSET:
            return
        return self._head_cache

    def get_head(self):
        if self._head_cache is UNSET:
            return self._get_head()
        return self._head_cache

    def _get_head(self):
        self.clear_head_cache()
        self._head_cache = None
        next_unblocked_interaction = None
        for bucket in self._buckets:
            next_unblocked_interaction = bucket.get_next_unblocked_interaction(blocked_sims_callback=(self._set_si_state_on_changed_callbacks_for_head))
            if next_unblocked_interaction is not None:
                break

        if self._head_cache is not None:
            if self._head_cache is not UNSET:
                return self._head_cache
        if next_unblocked_interaction is not None:
            required_sims = WeakSet(next_unblocked_interaction.required_sims())

            def clear_and_remove(si, self_ref=weakref.ref(self)):
                for sim in required_sims:
                    if sim.si_state is not None:
                        sim.si_state.on_changed.remove(clear_and_remove)

                self = self_ref()
                if self is not None:
                    self.clear_head_cache()

            for sim in required_sims:
                if sim.si_state is not None:
                    sim.si_state.on_changed.append(clear_and_remove)

            for sim in required_sims:
                if sim.si_state is None:
                    raise RuntimeError('Deleted sim:{} found in required sims of interaction:{} {} {}'.formatsimnext_unblocked_interactionnext_unblocked_interaction._pipeline_progressnext_unblocked_interaction._required_sims)

        self._head_cache = next_unblocked_interaction
        return next_unblocked_interaction

    def _resolve_priority_pressure(self):
        highest_priority_interaction = None
        for interaction in reversed(list(self)):
            allow_clobbering = interaction.interruptible
            super_priority = interaction.super_interaction.priority if interaction.super_interaction is not None else Priority.Low
            interaction_priority = interaction.priority
            max_priority = max(super_priority, interaction_priority)
            if highest_priority_interaction is not None:
                if not interaction.is_related_to(highest_priority_interaction):
                    if can_priority_displace((highest_priority_interaction.priority), max_priority, allow_clobbering=allow_clobbering):
                        if not interaction.source == InteractionSource.CARRY_CANCEL_AOP:
                            if not interaction.source == InteractionSource.BODY_CANCEL_AOP:
                                if interaction.source == InteractionSource.VEHCILE_CANCEL_AOP:
                                    continue
                                else:
                                    interaction.displace(highest_priority_interaction, cancel_reason_msg='Interaction Queue displaced from resolving priority pressure.')
                                continue
                if not highest_priority_interaction is None:
                    if interaction.priority > highest_priority_interaction.priority:
                        pass
                highest_priority_interaction = interaction

    def _resolve_collapsible_interaction(self):
        if len(self._interactions) <= 1:
            return
        for si_a, si_b in zip(self._interactions, list(self._interactions)[1:]):
            if si_a.visible:
                if not si_b.visible:
                    continue
                if not si_a.is_finishing:
                    if si_b.is_finishing:
                        continue
                    if si_a.is_super:
                        if si_a.collapsible:
                            if si_b.is_super:
                                if si_b.collapsible:
                                    si_a.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg='Interaction Queue canceled because interaction is collapsible.')
                                    break

    def _can_sis_pass_combinable_compatability_tests(self, first_si, second_si):
        if first_si.collapsible:
            return False
        if not self.sim.si_state.are_sis_compatible(first_si, second_si):
            return False
        return True

    def _attempt_combination(self, combined_sis, si_to_evaluate, combination_constraint):
        if not (si_to_evaluate.visible and si_to_evaluate.allowed_to_combine):
            return Nowhere('SI is not visible({}), or not allowed to combine({}), SI: {}', si_to_evaluate.visible, si_to_evaluate.allowed_to_combine, si_to_evaluate)
        for combined_si in combined_sis:
            if si_to_evaluate.continuation_id is not None:
                if si_to_evaluate.continuation_id == combined_si.continuation_id:
                    return Nowhere('Cannot combine two interactions from the same continuation chain. SI_A: {}, SI_B: {}', si_to_evaluate, combined_si)
            if not self._can_sis_pass_combinable_compatability_tests(combined_si, si_to_evaluate):
                return Nowhere('Two SIs we tried to combine cannot pass combinable compatibility tests. SI_A: {}, SI_B: {}', si_to_evaluate, combined_si)

        si_to_evaluate_constraint = si_to_evaluate.constraint_intersection(sim=(self.sim), posture_state=None)
        if not si_to_evaluate_constraint.valid:
            return si_to_evaluate_constraint
        test_constraint = si_to_evaluate_constraint.intersect(combination_constraint)
        return test_constraint

    def _combine_compatible_interactions(self):
        head_interaction = self.get_head()
        if not head_interaction is None:
            if not head_interaction.is_putdown:
                if head_interaction.visible:
                    if not (head_interaction.is_super and head_interaction.allowed_to_combine):
                        return
        original_head_combinables = WeakSet(head_interaction.combinable_interactions)
        head_interaction.combinable_interactions.clear()
        head_constraint = head_interaction.constraint_intersection(sim=(self.sim), posture_state=None)
        if not head_constraint.valid:
            return
        combined_included_sis = WeakSet((head_interaction,))
        if head_interaction.transition is not None:
            final_included_sis = head_interaction.transition.get_final_included_sis_for_sim(self.sim)
            if final_included_sis is not None:
                for final_si in final_included_sis:
                    if final_si.is_finishing:
                        continue
                    else:
                        final_si_constraint = final_si.constraint_intersection(sim=(self.sim), posture_state=None)
                        if not final_si_constraint.valid:
                            return
                        head_constraint = self._attempt_combinationcombined_included_sisfinal_sihead_constraint
                        if not head_constraint.valid:
                            return
                        combined_included_sis.add(final_si)

        combined_carry_targets = set()
        head_carryable = head_interaction.targeted_carryable
        if head_carryable is not None:
            combined_carry_targets.add(head_carryable)
        combined_interactions = WeakSet((head_interaction,))
        combined_constraint = head_constraint
        for queued_interaction in self._interactions:
            if not queued_interaction is head_interaction:
                if not queued_interaction.is_super:
                    continue
                if queued_interaction.is_putdown:
                    break
                else:
                    queued_interaction.combinable_interactions.clear()
                    test_intersection = self._attempt_combinationcombined_interactionsqueued_interactioncombined_constraint
                if not test_intersection.valid:
                    break
                else:
                    combined_constraint = test_intersection
                    combined_interactions.add(queued_interaction)
                    queued_carryable = queued_interaction.targeted_carryable
                if queued_carryable is not None:
                    combined_carry_targets.add(queued_carryable)
                    if len(combined_carry_targets) > 1:
                        break

        if len(combined_interactions) == 1:
            return
        for interaction in combined_interactions:
            interaction.combinable_interactions = combined_interactions

        if original_head_combinables:
            if original_head_combinables != combined_interactions:
                if head_interaction.transition is not None:
                    if len(combined_carry_targets) > 1:
                        posture_graph_service = services.current_zone().posture_graph_service
                        posture_graph_service.clear_goal_costs()
                    head_interaction.transition.derail(DerailReason.PROCESS_QUEUE, self.sim)

    def _get_bucket_for_context(self, context):
        bucket_type = context.bucket_type
        if bucket_type == InteractionBucketType.BASED_ON_SOURCE:
            source = context.source
            if source == InteractionContext.SOURCE_AUTONOMY:
                bucket_type = InteractionBucketType.AUTONOMY
            else:
                if source == InteractionContext.SOURCE_SOCIAL_ADJUSTMENT:
                    bucket_type = InteractionBucketType.SOCIAL_ADJUSTMENT
                else:
                    if source == InteractionContext.SOURCE_BODY_CANCEL_AOP:
                        bucket_type = InteractionBucketType.BODY_CANCEL_REPLACEMENT
                    else:
                        if source == InteractionContext.SOURCE_CARRY_CANCEL_AOP:
                            bucket_type = InteractionBucketType.CARRY_CANCEL_REPLACEMENT
                        else:
                            if source == InteractionContext.SOURCE_VEHICLE_CANCEL_AOP:
                                bucket_type = InteractionBucketType.VEHICLE_CANCEL_REPLACEMENT
                            else:
                                bucket_type = InteractionBucketType.DEFAULT
        if bucket_type == InteractionBucketType.AUTONOMY:
            bucket = self._autonomy
        else:
            if bucket_type == InteractionBucketType.SOCIAL_ADJUSTMENT:
                bucket = self._social_adjustment
            else:
                if bucket_type == InteractionBucketType.VEHICLE_CANCEL_REPLACEMENT:
                    bucket = self._vehicle_cancel_replacements
                else:
                    if bucket_type == InteractionBucketType.BODY_CANCEL_REPLACEMENT:
                        bucket = self._body_cancel_replacements
                    else:
                        if bucket_type == InteractionBucketType.CARRY_CANCEL_REPLACEMENT:
                            bucket = self._carry_cancel_replacements
                        else:
                            if bucket_type == InteractionBucketType.DEFAULT:
                                bucket = self._interactions
                            else:
                                raise ValueError('Unrecognized bucket_type: {}'.format(bucket_type))
        return bucket

    def _get_bucket_for_interaction(self, interaction):
        if interaction.context.bucket_type not in InteractionBucketType.values:
            logger.error('Invalid interaction bucket in context for {}', interaction, owner='rez')
        bucket = self._get_bucket_for_context(interaction.context)
        return bucket

    def append(self, interaction):
        if self.locked:
            return TestResult(False, 'Interaction queue is locked.')
        if interaction.is_finishing:
            return TestResult(False, 'Interaction is already finishing.')
        target_queue = self._get_bucket_for_interaction(interaction)
        with self._head_change_watcher():
            if interaction.context.insert_strategy == QueueInsertStrategy.NEXT or interaction.context.insert_strategy == QueueInsertStrategy.FIRST:
                self._refresh_bucket_constraints()
                if interaction.context.insert_strategy != QueueInsertStrategy.FIRST:
                    insert_after_interaction = self.running
                else:
                    insert_after_interaction = None
                success = target_queue.insert_next(interaction, insert_after=insert_after_interaction)
            else:
                insert_after_interaction = None
                success = target_queue.append(interaction)
            if not success:
                interaction.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg='InteractionQueue: failed to append interaction')
                return success
            interaction_id_to_insert_after = insert_after_interaction.id if insert_after_interaction is not None else None
            interaction.on_added_to_queue(interaction_id_to_insert_after=interaction_id_to_insert_after)
            if interaction.is_user_directed:
                self._on_user_driven_action()
            if interaction.context.must_run_next:
                if self._must_run_next_interaction is not None:
                    self._must_run_next_interaction.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg=('must_run_next inserted again: {} canceled by {}'.format(self._must_run_next_interaction, interaction)))
                    self._must_run_next_interaction = None
                self._must_run_next_interaction = interaction
            self._resolve_priority_pressure()
            self._resolve_collapsible_interaction()
            self._combine_compatible_interactions()
        if interaction.is_finishing:
            return TestResult(False, 'Interaction finished during append.  Finishing Info: {}'.format(interaction._finisher))
        return TestResult.TRUE

    def _refresh_bucket_constraints(self):
        for interaction in list(self._autonomy):
            interaction.refresh_constraints()

        for interaction in list(self._interactions):
            interaction.refresh_constraints()

    def _on_user_driven_action(self):
        for interaction in list(self._autonomy):
            interaction.cancel((FinishingType.PRIORITY), cancel_reason_msg='User-directed action takes precedence over autonomous interactions.')

        for interaction in list(self._social_adjustment):
            interaction.cancel((FinishingType.PRIORITY), cancel_reason_msg='User-directed action takes precedence over social adjustment interactions.')

    def mixer_interactions_gen(self):
        for interaction in self:
            if not interaction.is_super:
                yield interaction

    def find_sub_interaction(self, super_id, aop_id):
        for interaction in self:
            if interaction.super_interaction.id == super_id:
                if interaction.aop.aop_id == aop_id:
                    return interaction

    def find_continuation_by_id(self, source_id):
        for interaction in self:
            if interaction.is_continuation_by_id(source_id):
                return interaction

    def find_pushed_interaction_by_id(self, group_id):
        for interaction in self:
            if interaction.group_id == group_id:
                return interaction

    def find_interaction_by_id(self, id_to_find):
        for interaction in self:
            if interaction.id == id_to_find:
                return interaction

        if self.transition_controller is not None:
            if self.transition_controller.interaction.id == id_to_find:
                return self.transition_controller.interaction

    def has_adjustment_interaction(self):
        return len(self._social_adjustment) > 0

    def cancel_all(self):
        self.clear_head_cache()
        interactions = list(self)
        for interaction in interactions:
            interaction.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg='InteractionQueue: all interactions canceled')

    def on_reset(self, being_destroyed=False):
        self._being_destroyed = being_destroyed
        with self._head_change_watcher(defer_on_head_change_call=True):
            if self.transition_controller is not None:
                self.transition_controller.on_reset()
                self.transition_controller.interaction.on_reset()
                self.transition_controller = None
            if self._running is not None:
                self._running.on_reset()
                self._running = None
            self.clear_head_cache()
            for bucket in self._buckets:
                try:
                    bucket.on_reset()
                except Exception:
                    logger.error('Exception caught while reseting interaction bucket. ListBucket.reset is not allowed to throw an exception and must always clear the bucket:')
                    raise

    def on_interaction_canceled(self, interaction):
        self.clear_must_run_next_interaction(interaction)
        if self.running is interaction:
            return
        if interaction.is_super:
            si_order_changed = True
        else:
            si_order_changed = False
        log_interaction('Dequeue_Clear', interaction)
        with self._head_change_watcher():
            for bucket in self._buckets:
                if interaction in bucket:
                    if bucket.clear_interaction(interaction):
                        break

        if self.running is not None:
            if self.running.should_cancel_on_si_cancel(interaction):
                self.running.cancel((FinishingType.INTERACTION_QUEUE), cancel_reason_msg='Interaction Queue cancel running interaction to expedite SI cancel.')
        if not self._being_destroyed:
            if si_order_changed:
                self._combine_compatible_interactions()
                self._resolve_collapsible_interaction()

    @property
    def locked(self):
        return self._locked

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def on_si_phase_change(self, si):
        for interaction in self:
            if not interaction.is_super:
                continue
            else:
                interaction.on_other_si_phase_change(si)

        with self._head_change_watcher():
            self._apply_next_pressure()

    def on_element_priority_changed(self, interaction):
        with self._head_change_watcher():
            self._apply_next_pressure()

    def _on_head_changed(self):
        if services.current_zone().is_zone_shutting_down:
            return
        with self._head_change_watcher():
            self._apply_next_pressure()
        self.on_head_changed()
        self._combine_compatible_interactions()

    @staticmethod
    def _should_head_dispace_running(sim, next_interaction, running_interaction):
        if running_interaction.disable_displace(next_interaction):
            return False
        if not running_interaction.is_super:
            if not running_interaction.interruptible:
                return False
            if next_interaction.super_interaction is running_interaction:
                return False
            pick_up_sim_liability = running_interaction.get_liability(PickUpSimLiability.LIABILITY_TOKEN)
            if pick_up_sim_liability is not None:
                if pick_up_sim_liability.original_interaction is next_interaction:
                    return False
            cancel_aop_liability = next_interaction.get_liability(CANCEL_AOP_LIABILITY)
            if cancel_aop_liability is not None:
                if cancel_aop_liability.interaction_to_cancel is running_interaction:
                    return True
            if next_interaction.is_cancel_aop and not running_interaction.disable_transitions:
                allow_clobbering = True
            else:
                allow_clobbering = running_interaction.interruptible
            if running_interaction.is_super:
                if running_interaction.is_guaranteed():
                    if not can_displace(next_interaction, running_interaction, allow_clobbering=allow_clobbering):
                        return False
                    if next_interaction.is_related_to(running_interaction):
                        return False
                    if running_interaction.is_super:
                        if next_interaction.is_super:
                            participant_type_a = running_interaction.get_participant_type(sim)
                            participant_type_b = next_interaction.get_participant_type(sim)
                            compatible = sim.si_state.are_sis_compatible(running_interaction, next_interaction,
                              participant_type_a=participant_type_a,
                              participant_type_b=participant_type_b)
                            if compatible:
                                return False
            return True

    def _apply_next_pressure(self):
        next_interaction = self.get_head()
        if next_interaction is None:
            return
        for sim in next_interaction.required_sims():
            running_interaction = sim.queue.running
            if next_interaction is running_interaction:
                continue
            if not running_interaction is None:
                if running_interaction.must_run:
                    continue
                if not self._should_head_dispace_runningsimnext_interactionrunning_interaction:
                    if running_interaction.transition is not None:
                        if running_interaction.sim is self.sim:
                            if not running_interaction.is_adjustment_interaction():
                                if not next_interaction.is_related_to(running_interaction):
                                    running_interaction.transition.derail(DerailReason.PREEMPTED, sim)
                                    continue
                else:
                    running_interaction.displace(next_interaction, cancel_reason_msg=('InteractionQueue: pressure to cancel running interaction from {}'.format(next_interaction)))

    def on_required_sims_changed(self, interaction):
        self.clear_head_cache()
        if self.get_head() is interaction:
            self._on_head_changed()

    def cancel_aop_exists_for_si(self, si):
        for interaction in self:
            cancel_liability = interaction.get_liability(CANCEL_AOP_LIABILITY)
            if cancel_liability is not None:
                if si is cancel_liability.interaction_to_cancel:
                    return True

        return False

    def queued_super_interactions_gen(self):
        for si in self._interactions:
            if si.is_super:
                yield si

    def has_duplicate_super_affordance(self, super_affordance, actor, target):
        for si in self._interactions:
            if si.affordance is super_affordance:
                if si.target is target:
                    if si.context.sim is actor:
                        return True

        return False