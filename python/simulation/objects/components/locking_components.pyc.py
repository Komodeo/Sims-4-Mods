# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\locking_components.py
# Compiled at: 2021-04-06 14:57:51
# Size of source mod 2**32: 20980 bytes
import functools, weakref
from animation.animation_constants import CreatureType
from protocolbuffers import SimObjectAttributes_pb2
from event_testing.test_events import TestEvent
from objects.components import Component, componentmethod, componentmethod_with_fallback
from objects.components.portal_lock_data import LockAllWithSimIdExceptionData, LockSimInfoData, LockAllWithClubException, LockResult, LockAllWithSituationJobExceptionData, IndividualSimDoorLockData, LockAllWithGenusException, LockRankedStatisticData, LockAllWithBuffExceptionData, LockCreatureData
from objects.components.portal_locking_enums import LockPriority, LockSide, LockType, ClearLock
from objects.components.types import PORTAL_LOCKING_COMPONENT, OBJECT_LOCKING_COMPONENT
from objects.mixins import SuperAffordanceProviderMixin
from sims.sim_info_tests import MatchType
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableList, TunableVariant
import services, sims4
logger = sims4.log.Logger('LockComponents', default_owner='cjiang')

class BaseLockingComponent(Component, HasTunableFactory, AutoFactoryInit):
    DEFAULT_LOCK = LockAllWithSimIdExceptionData(except_actor=False, except_household=False,
      lock_priority=(LockPriority.SYSTEM_LOCK),
      lock_sides=(LockSide.LOCK_BOTH),
      should_persist=True)
    FACTORY_TUNABLES = {'preset_lock_datas': TunableList(description='\n            The preset lock data on the component. If the priority is set to\n            SYSTEM_LOCK, the lock will always exist. If the priority is set to\n            PLAYER_LOCK, then upon load, any preset data is trumped by whatever\n            might have been set by the player.\n            ',
                            tunable=TunableVariant(lock_siminfo=(LockSimInfoData.TunableFactory()),
                            lock_clubs=(LockAllWithClubException.TunableFactory()),
                            lock_situation_job=(LockAllWithSituationJobExceptionData.TunableFactory()),
                            lock_genus=(LockAllWithGenusException.TunableFactory()),
                            lock_ranked_statistic=(LockRankedStatisticData.TunableFactory()),
                            lock_buff=(LockAllWithBuffExceptionData.TunableFactory()),
                            lock_creature=(LockCreatureData.TunableFactory()),
                            default='lock_siminfo'))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.lock_datas = {}
        self._disallowed_sims = weakref.WeakKeyDictionary()
        self._lock_refresh_events = set()
        for preset_lock_data in self.preset_lock_datas:
            self.add_lock_data((preset_lock_data()), refresh=False, clear_existing_locks=(ClearLock.CLEAR_NONE))

    def on_remove(self, *_, **__):
        services.get_event_manager().unregister(self, self._lock_refresh_events)

    def remove_disallowed_sim(self, sim, disallower):
        raise NotImplementedError

    def add_disallowed_sim(self, sim, disallower, lock_both=False):
        if sim not in self._disallowed_sims:
            self._disallowed_sims[sim] = dict()
        self._disallowed_sims[sim][disallower] = lock_both

    @componentmethod
    def add_lock_data(self, lock_data, replace_same_lock_type=True, refresh=True, clear_existing_locks=ClearLock.CLEAR_ALL):
        if clear_existing_locks != ClearLock.CLEAR_NONE:
            for existing_lock_data in list(self.lock_datas.values()):
                if existing_lock_data.lock_priority == LockPriority.PLAYER_LOCK:
                    clear_lock = True
                    if clear_existing_locks == ClearLock.CLEAR_OTHER_LOCK_TYPES:
                        clear_lock = existing_lock_data.lock_type != lock_data.lock_type
                    if clear_lock:
                        del self.lock_datas[existing_lock_data.lock_type]

        if not replace_same_lock_type:
            existing_data = self.lock_datas.get(lock_data.lock_type)
            if existing_data is not None:
                lock_data.update(existing_data)
        self.lock_datas[lock_data.lock_type] = lock_data
        if refresh:
            self.refresh_locks()
        self._lock_refresh_events.update(lock_data.REFRESH_EVENTS)
        services.get_event_manager().register(self, self._lock_refresh_events)

    @componentmethod_with_fallback(lambda: None
)
    def refresh_locks(self, update_objects=True):
        self._clear_locks_on_all_sims(update_objects)
        self._lock_every_sim(update_objects)

    def _clear_locks_on_all_sims(self, update_objects=True):
        for target_sim in services.sim_info_manager().instanced_sims_gen():
            self.remove_disallowed_sim(target_sim, self)

        if update_objects:
            for obj in services.get_object_routing_service().routable_objects_gen():
                self.remove_disallowed_sim(obj, self)

    def _lock_every_sim(self, update_objects=True):
        for target_sim in services.sim_info_manager().instanced_sims_gen():
            self.lock_sim(target_sim)

        if update_objects:
            for obj in services.get_object_routing_service().routable_objects_gen():
                self.lock_sim(obj)

    @componentmethod_with_fallback(lambda *_, **__: None
)
    def lock_sim(self, sim):
        lock_result = self.test_lock(sim)
        if lock_result:
            self.add_disallowed_sim(sim, self, lock_both=(lock_result.is_locking_both()))

    @componentmethod
    def test_lock(self, sim):
        current_system_lock_result = LockResult.NONE
        current_player_lock_result = LockResult.NONE
        for lock_data in self.lock_datas.values():
            if not lock_data.check_lock_permission(sim):
                continue
            else:
                lock_result = lock_data.test_lock(sim)
            if lock_result is None:
                continue
            if lock_result.is_player_lock():
                if current_player_lock_result == LockResult.NONE:
                    current_player_lock_result = lock_result
                else:
                    if current_player_lock_result.is_locked and not lock_result.is_locked:
                        current_player_lock_result = lock_result
                    else:
                        pass
                if current_player_lock_result.is_locked:
                    if lock_result.is_locked and lock_result.is_locking_both():
                        current_player_lock_result = lock_result
                    else:
                        if current_system_lock_result == LockResult.NONE:
                            current_system_lock_result = lock_result
                        else:
                            if not current_system_lock_result.is_locked or lock_result.is_locked:
                                current_system_lock_result = lock_result
                            else:
                                if current_system_lock_result.is_locked:
                                    if lock_result.is_locked:
                                        if lock_result.is_locking_both():
                                            current_system_lock_result = lock_result

        if current_system_lock_result.is_locked:
            if current_player_lock_result.is_locked:
                if current_player_lock_result.is_locking_both():
                    return current_player_lock_result
            return current_system_lock_result
        else:
            if current_player_lock_result.is_locked:
                return current_player_lock_result
        return LockResult.NONE

    @componentmethod
    def get_disallowed_sims(self):
        return self._disallowed_sims

    def handle_event(self, sim_info, event_type, resolver):
        if event_type == TestEvent.BuffBeganEvent or event_type == TestEvent.BuffEndedEvent:
            buff = resolver.event_kwargs['buff']
            if buff is not None:
                if buff.refresh_lock:
                    self.refresh_locks(update_objects=False)

    @componentmethod_with_fallback(lambda: False
)
    def has_locking_component(self):
        return True

    @componentmethod_with_fallback(lambda: None
)
    def get_locking_component(self):
        return self

    @componentmethod_with_fallback(lambda: None
)
    def lock(self):
        self.add_lock_data(BaseLockingComponent.DEFAULT_LOCK)

    @componentmethod_with_fallback(lambda: None
)
    def unlock(self):
        if self.lock_datas:
            self._clear_locks_on_all_sims()
            self.lock_datas.clear()

    @componentmethod_with_fallback(lambda *_, **__: False
)
    def has_lock_data(self, lock_priority=None, lock_types=None):
        for lock_data in self.lock_datas.values():
            if not lock_priority is None:
                if lock_data.lock_priority == lock_priority:
                    pass
            if lock_types is None or lock_data.lock_type in lock_types:
                return True

        return False

    @componentmethod
    def remove_locks(self, lock_type=None, lock_priority=None):
        if not self.lock_datas:
            return
        self._clear_locks_on_all_sims()
        for lock_data in list(self.lock_datas.values()):
            if not lock_priority is None:
                if lock_data.lock_priority == lock_priority:
                    pass
            if not lock_type is None:
                if lock_data.lock_type == lock_type:
                    pass
            del self.lock_datas[lock_data.lock_type]

        self._lock_every_sim()

    def _save(self, persistence_master_message, cmp_lock_data, persistable_data):
        for lock_data in self.lock_datas.values():
            if not lock_data.should_persist:
                continue
            if lock_data.lock_priority == LockPriority.PLAYER_LOCK:
                persist_lock_data = cmp_lock_data.lock_data.add()
                persist_lock_data.lock_type = lock_data.lock_type
                lock_data.save(persist_lock_data)

        persistence_master_message.data.extend([persistable_data])

    def _load--- This code section failed: ---

 L. 300         0  LOAD_FAST                'self'
                2  LOAD_ATTR                remove_locks
                4  LOAD_GLOBAL              LockPriority
                6  LOAD_ATTR                PLAYER_LOCK
                8  LOAD_CONST               ('lock_priority',)
               10  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               12  POP_TOP          

 L. 302     14_16  SETUP_LOOP          328  'to 328'
               18  LOAD_FAST                'cmp_lock_data'
               20  LOAD_ATTR                lock_data
               22  GET_ITER         
             24_0  COME_FROM           324  '324'
             24_1  COME_FROM           270  '270'
             24_2  COME_FROM           252  '252'
            24_26  FOR_ITER            326  'to 326'
               28  STORE_FAST               'persist_lock_data'

 L. 303        30  LOAD_FAST                'persist_lock_data'
               32  LOAD_ATTR                lock_type
               34  LOAD_GLOBAL              LockType
               36  LOAD_ATTR                LOCK_ALL_WITH_SIMID_EXCEPTION
               38  COMPARE_OP               ==
               40  POP_JUMP_IF_FALSE    64  'to 64'

 L. 304        42  LOAD_GLOBAL              functools
               44  LOAD_ATTR                partial
               46  LOAD_GLOBAL              LockAllWithSimIdExceptionData

 L. 305        48  LOAD_FAST                'persist_lock_data'
               50  LOAD_ATTR                except_actor

 L. 306        52  LOAD_FAST                'persist_lock_data'
               54  LOAD_ATTR                except_household
               56  LOAD_CONST               ('except_actor', 'except_household')
               58  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               60  STORE_FAST               'create_lock_data'
               62  JUMP_FORWARD        272  'to 272'
             64_0  COME_FROM            40  '40'

 L. 307        64  LOAD_FAST                'persist_lock_data'
               66  LOAD_ATTR                lock_type
               68  LOAD_GLOBAL              LockType
               70  LOAD_ATTR                LOCK_ALL_WITH_SITUATION_JOB_EXCEPTION
               72  COMPARE_OP               ==
               74  POP_JUMP_IF_FALSE    96  'to 96'

 L. 308        76  LOAD_GLOBAL              functools
               78  LOAD_ATTR                partial
               80  LOAD_GLOBAL              LockAllWithSituationJobExceptionData

 L. 309        82  LOAD_CONST               None

 L. 310        84  LOAD_FAST                'persist_lock_data'
               86  LOAD_ATTR                except_retail_employee
               88  LOAD_CONST               ('situation_job_test', 'except_business_employee')
               90  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               92  STORE_FAST               'create_lock_data'
               94  JUMP_FORWARD        272  'to 272'
             96_0  COME_FROM            74  '74'

 L. 311        96  LOAD_FAST                'persist_lock_data'
               98  LOAD_ATTR                lock_type
              100  LOAD_GLOBAL              LockType
              102  LOAD_ATTR                LOCK_ALL_WITH_CLUBID_EXCEPTION
              104  COMPARE_OP               ==
              106  POP_JUMP_IF_FALSE   124  'to 124'

 L. 312       108  LOAD_GLOBAL              functools
              110  LOAD_ATTR                partial
              112  LOAD_GLOBAL              LockAllWithClubException

 L. 313       114  LOAD_CONST               ()
              116  LOAD_CONST               ('except_club_seeds',)
              118  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              120  STORE_FAST               'create_lock_data'
              122  JUMP_FORWARD        272  'to 272'
            124_0  COME_FROM           106  '106'

 L. 314       124  LOAD_FAST                'persist_lock_data'
              126  LOAD_ATTR                lock_type
              128  LOAD_GLOBAL              LockType
              130  LOAD_ATTR                INDIVIDUAL_SIM
              132  COMPARE_OP               ==
              134  POP_JUMP_IF_FALSE   148  'to 148'

 L. 315       136  LOAD_GLOBAL              functools
              138  LOAD_METHOD              partial
              140  LOAD_GLOBAL              IndividualSimDoorLockData
              142  CALL_METHOD_1         1  '1 positional argument'
              144  STORE_FAST               'create_lock_data'
              146  JUMP_FORWARD        272  'to 272'
            148_0  COME_FROM           134  '134'

 L. 316       148  LOAD_FAST                'persist_lock_data'
              150  LOAD_ATTR                lock_type
              152  LOAD_GLOBAL              LockType
              154  LOAD_ATTR                LOCK_ALL_WITH_GENUS_EXCEPTION
              156  COMPARE_OP               ==
              158  POP_JUMP_IF_FALSE   184  'to 184'

 L. 317       160  LOAD_GLOBAL              functools
              162  LOAD_ATTR                partial
              164  LOAD_GLOBAL              LockAllWithGenusException

 L. 318       166  LOAD_CONST               0
              168  LOAD_CONST               None
              170  LOAD_CONST               None

 L. 319       172  LOAD_GLOBAL              MatchType
              174  LOAD_ATTR                MATCH_ALL
              176  LOAD_CONST               ('gender', 'ages', 'species', 'match_type')
              178  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
              180  STORE_FAST               'create_lock_data'
              182  JUMP_FORWARD        272  'to 272'
            184_0  COME_FROM           158  '158'

 L. 320       184  LOAD_FAST                'persist_lock_data'
              186  LOAD_ATTR                lock_type
              188  LOAD_GLOBAL              LockType
              190  LOAD_ATTR                LOCK_RANK_STATISTIC
              192  COMPARE_OP               ==
              194  POP_JUMP_IF_FALSE   214  'to 214'

 L. 321       196  LOAD_GLOBAL              functools
              198  LOAD_ATTR                partial
              200  LOAD_GLOBAL              LockRankedStatisticData

 L. 322       202  LOAD_CONST               None
              204  LOAD_CONST               None
              206  LOAD_CONST               ('ranked_stat', 'rank_threshold')
              208  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              210  STORE_FAST               'create_lock_data'
              212  JUMP_FORWARD        272  'to 272'
            214_0  COME_FROM           194  '194'

 L. 323       214  LOAD_FAST                'persist_lock_data'
              216  LOAD_ATTR                lock_type
              218  LOAD_GLOBAL              LockType
              220  LOAD_ATTR                LOCK_ALL_WITH_BUFF_EXCEPTION
              222  COMPARE_OP               ==
              224  POP_JUMP_IF_FALSE   242  'to 242'

 L. 324       226  LOAD_GLOBAL              functools
              228  LOAD_ATTR                partial
              230  LOAD_GLOBAL              LockAllWithBuffExceptionData

 L. 325       232  LOAD_CONST               None
              234  LOAD_CONST               ('except_buffs',)
              236  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              238  STORE_FAST               'create_lock_data'
              240  JUMP_FORWARD        272  'to 272'
            242_0  COME_FROM           224  '224'

 L. 326       242  LOAD_FAST                'persist_lock_data'
              244  LOAD_ATTR                lock_type
              246  LOAD_GLOBAL              LockType
              248  LOAD_ATTR                LOCK_CREATURE
              250  COMPARE_OP               ==
              252  POP_JUMP_IF_FALSE_LOOP    24  'to 24'

 L. 327       254  LOAD_GLOBAL              functools
              256  LOAD_ATTR                partial
              258  LOAD_GLOBAL              LockCreatureData

 L. 328       260  LOAD_CONST               None
              262  LOAD_CONST               ('creature_types',)
              264  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              266  STORE_FAST               'create_lock_data'
              268  JUMP_FORWARD        272  'to 272'

 L. 330       270  CONTINUE             24  'to 24'
            272_0  COME_FROM           268  '268'
            272_1  COME_FROM           240  '240'
            272_2  COME_FROM           212  '212'
            272_3  COME_FROM           182  '182'
            272_4  COME_FROM           146  '146'
            272_5  COME_FROM           122  '122'
            272_6  COME_FROM            94  '94'
            272_7  COME_FROM            62  '62'

 L. 332       272  LOAD_FAST                'create_lock_data'
              274  LOAD_GLOBAL              LockPriority
              276  LOAD_FAST                'persist_lock_data'
              278  LOAD_ATTR                priority
              280  CALL_FUNCTION_1       1  '1 positional argument'

 L. 333       282  LOAD_GLOBAL              LockSide
              284  LOAD_FAST                'persist_lock_data'
              286  LOAD_ATTR                sides
              288  CALL_FUNCTION_1       1  '1 positional argument'

 L. 334       290  LOAD_CONST               True
              292  LOAD_CONST               ('lock_priority', 'lock_sides', 'should_persist')
              294  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              296  STORE_FAST               'lock_data'

 L. 335       298  LOAD_FAST                'lock_data'
              300  LOAD_METHOD              load
              302  LOAD_FAST                'persist_lock_data'
              304  CALL_METHOD_1         1  '1 positional argument'
              306  POP_TOP          

 L. 336       308  LOAD_FAST                'self'
              310  LOAD_ATTR                add_lock_data
              312  LOAD_FAST                'lock_data'
              314  LOAD_GLOBAL              ClearLock
              316  LOAD_ATTR                CLEAR_NONE
              318  LOAD_CONST               ('clear_existing_locks',)
              320  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              322  POP_TOP          
              324  JUMP_LOOP            24  'to 24'
              326  POP_BLOCK        
            328_0  COME_FROM_LOOP       14  '14'

Parse error at or near `CONTINUE' instruction at offset 270


class ObjectLockingComponent(BaseLockingComponent, HasTunableFactory, AutoFactoryInit, SuperAffordanceProviderMixin, component_name=OBJECT_LOCKING_COMPONENT, persistence_key=SimObjectAttributes_pb2.PersistenceMaster.PersistableData.ObjectLockingComponent):

    def on_add(self, *_, **__):
        self.owner.update_component_commodity_flags()

    @componentmethod_with_fallback(lambda *_, **__: None
)
    def remove_disallowed_sim(self, sim, disallower):
        disallowing_objects = self._disallowed_sims.get(sim)
        if disallowing_objects is None:
            return
        if disallower not in disallowing_objects:
            return
        del disallowing_objects[disallower]
        if not disallowing_objects:
            del self._disallowed_sims[sim]

    def component_super_affordances_gen(self, context=None, **kwargs):
        if context is None:
            yield from self.super_affordances
        else:
            if context.sim is not None:
                if not self.test_lock(context.sim).is_locked:
                    yield from self.super_affordances
        if False:
            yield None

    def save(self, persistence_master_message):
        persistable_data = SimObjectAttributes_pb2.PersistenceMaster.PersistableData()
        persistable_data.type = SimObjectAttributes_pb2.PersistenceMaster.PersistableData.ObjectLockingComponent
        lock_data = persistable_data.Extensions[SimObjectAttributes_pb2.PersistableObjectLockingComponent.persistable_data]
        self._save(persistence_master_message, lock_data, persistable_data)

    def load(self, persistence_master_message):
        lock_data = persistence_master_message.Extensions[SimObjectAttributes_pb2.PersistableObjectLockingComponent.persistable_data]
        self._load(lock_data)


class PortalLockingComponent(BaseLockingComponent, HasTunableFactory, AutoFactoryInit, component_name=PORTAL_LOCKING_COMPONENT, persistence_key=SimObjectAttributes_pb2.PersistenceMaster.PersistableData.PortalLockingComponent):

    def on_add(self, *_, **__):
        services.object_manager().add_portal_to_cache(self.owner)

    @componentmethod
    def add_disallowed_sim(self, sim, disallower, lock_both=False):
        super().add_disallowed_sim(sim, disallower, lock_both)
        for portal_pair in self.owner.get_portal_pairs():
            sim.routing_component.routing_context.lock_portal(portal_pair.there)
            if lock_both:
                if portal_pair.back is not None:
                    sim.routing_component.routing_context.lock_portal(portal_pair.back)

    def has_bidirectional_lock(self, sim):
        return any(self._disallowed_sims[sim].values())

    @componentmethod_with_fallback(lambda *_, **__: None
)
    def remove_disallowed_sim(self, sim, disallower):
        disallowing_objects = self._disallowed_sims.get(sim)
        if disallowing_objects is None:
            return
        if disallower not in disallowing_objects:
            return
        del disallowing_objects[disallower]
        if not disallowing_objects:
            for portal_pair in self.owner.get_portal_pairs():
                sim.routing_component.routing_context.unlock_portal(portal_pair.there)
                if portal_pair.back is not None:
                    sim.routing_component.routing_context.unlock_portal(portal_pair.back)

            del self._disallowed_sims[sim]

    def save(self, persistence_master_message):
        persistable_data = SimObjectAttributes_pb2.PersistenceMaster.PersistableData()
        persistable_data.type = SimObjectAttributes_pb2.PersistenceMaster.PersistableData.PortalLockingComponent
        portal_lock_data = persistable_data.Extensions[SimObjectAttributes_pb2.PersistablePortalLockingComponent.persistable_data]
        self._save(persistence_master_message, portal_lock_data, persistable_data)

    def load(self, persistence_master_message):
        portal_lock_data = persistence_master_message.Extensions[SimObjectAttributes_pb2.PersistablePortalLockingComponent.persistable_data]
        self._load(portal_lock_data)