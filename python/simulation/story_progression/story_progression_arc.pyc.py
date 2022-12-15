# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_arc.py
# Compiled at: 2022-04-05 15:57:40
# Size of source mod 2**32: 25632 bytes
import random, services
from date_and_time import DateAndTime
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import SingleSimResolver, HouseholdResolver, DoubleSimResolver, SingleSimAndHouseholdResolver
from gsi_handlers.drama_handlers import is_scoring_archive_enabled, GSIDramaScoringData, archive_drama_scheduler_scoring
from interactions import STORY_PROGRESSION_SIM_PARTICIPANTS, ParticipantType, STORY_PROGRESSION_ZONE_PARTICIPANTS, STORY_PROGRESSION_STRING_PARTICIPANTS, get_number_of_bit_shifts_by_participant_type
from protocolbuffers.Localization_pb2 import LocalizedString
from sims4.log import Logger
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, TunableVariant, TunableList, TunableEnumEntry
from sims4.utils import classproperty, constproperty
from story_progression import StoryProgressionArcSeedReason, story_progression_telemetry
from story_progression.story_progression_candidate_selection import SelectSimCandidateFromDemographicListFunction, SelectSimCandidateFromFilterFunction, SelectHouseholdCandidateMatchingLotFromDemographicListFunction, SelectHouseholdWithHomeCandidateFromDemographicListBasedOnCullingScoreFunction
from story_progression.story_progression_enums import StoryType
from story_progression.story_progression_exclusivity import StoryProgressionExclusivityCategory
from story_progression.story_progression_log import log_story_progression_update
from story_progression.story_progression_result import StoryProgressionResultType, StoryProgressionResult
from story_progression.story_progression_tuning import StoryProgTunables
logger = Logger('StoryProgression', default_owner='jjacobson')

class BaseStoryArc(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.STORY_ARC)):
    INSTANCE_SUBCLASSES_ONLY = True
    INSTANCE_TUNABLES = {'required_rules':TunableList(description='\n            Sims/households must have these rules enabled in order to be chosen as a candidate for this arc.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(Types.USER_INTERFACE_INFO)),
       class_restrictions='StoryProgressionRuleDisplayInfo',
       pack_safe=True)), 
     'exclusivity_category':TunableEnumEntry(description='\n            The exclusivity category of this story progression arc.  Neutral means that this arc can be seeded with any\n            other arc already on the Sim/Household.  See story_progression_exclusivity for details of how this works.\n            ',
       tunable_type=StoryProgressionExclusivityCategory,
       default=StoryProgressionExclusivityCategory.NEUTRAL)}

    @classproperty
    def _initial_story_chapter(cls):
        raise NotImplementedError

    def __init__(self, tracker):
        self._tracker = tracker
        self._current_chapter = None
        self._historical_chapters = None
        self._stored_participants = None
        self._chapter_with_drama_nodes_to_schedule = None

    @property
    def historical_chapters(self):
        if self._historical_chapters is None:
            return tuple()
        return tuple(self._historical_chapters)

    @property
    def tracker(self):
        return self._tracker

    @classmethod
    def select_candidates(cls, demographic_sims, demographic_households, demographic_zones):
        return cls.candidate_selection_function(demographic_sims, demographic_households, demographic_zones, cls)

    def setup(self, **kwargs):
        initial_chapter = self._initial_story_chapter(self)
        try:
            result = (initial_chapter.setup)(**kwargs)
        except Exception as e:
            try:
                logger.exception('Exception while trying to setup story arc. {}', self)
                return StoryProgressionResult(StoryProgressionResultType.ERROR, 'Exception: {}', e)
            finally:
                e = None
                del e

        if result:
            if 'start_reason' in kwargs:
                self._set_current_chapter(initial_chapter, start_reason=(kwargs['start_reason']))
            else:
                self._set_current_chapter(initial_chapter)
        else:
            initial_chapter.cleanup()
        return result

    def _set_current_chapter(self, new_chapter, start_reason=StoryProgressionArcSeedReason.SYSTEM):
        old_chapter = self._current_chapter
        if old_chapter is not None:
            old_chapter.on_removed_from_current()
        self._current_chapter = new_chapter
        if self._current_chapter is not None:
            self._current_chapter.on_set_current()
            story_progression_telemetry.send_chapter_start_telemetry(self._current_chapter, start_reason)
        if old_chapter is not None:
            old_chapter.end_chapter()

    def update_story_arc(self):
        updated_chapter = self._current_chapter
        if self._current_chapter is None:
            result = StoryProgressionResult(StoryProgressionResultType.ERROR, 'Attempting to update Arc {} that has no current chapter.', self)
            log_story_progression_update(self.tracker, self, self._current_chapter, result)
            return (
             result, updated_chapter)
        current_chapter_result = self._current_chapter.update_story_chapter()
        log_story_progression_update(self.tracker, self, self._current_chapter, current_chapter_result)
        if current_chapter_result.result_type == StoryProgressionResultType.FAILED_PRECONDITIONS:
            return (current_chapter_result, updated_chapter)
        if current_chapter_result:
            if self._current_chapter.drama_nodes:
                self._chapter_with_drama_nodes_to_schedule = self._current_chapter
            new_chapter_result, next_chapter = self._current_chapter.get_next_chapter()
            if new_chapter_result.should_be_made_historical:
                if self._historical_chapters is None:
                    self._historical_chapters = []
                self._historical_chapters.append(self._current_chapter)
            if not new_chapter_result:
                self._set_current_chapter(None)
                return (
                 new_chapter_result, updated_chapter)
            self._set_current_chapter(next_chapter)
            if self._current_chapter is None:
                return (StoryProgressionResult(StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL), updated_chapter)
            return (StoryProgressionResult(StoryProgressionResultType.SUCCESS), updated_chapter)
        self._set_current_chapter(None)
        return (
         current_chapter_result, updated_chapter)

    def schedule_drama_nodes_gen(self, timeline=None):
        if self._chapter_with_drama_nodes_to_schedule is not None:
            drama_scheduler = services.drama_scheduler_service()
            if is_scoring_archive_enabled():
                gsi_data = GSIDramaScoringData()
                gsi_data.bucket = f"Story Chapter: {self._chapter_with_drama_nodes_to_schedule}"
            else:
                gsi_data = None
            yield from drama_scheduler.score_and_schedule_nodes_gen((self._chapter_with_drama_nodes_to_schedule.drama_nodes), 1,
              timeline=timeline,
              resolver_resolver=(self._get_drama_node_resolver),
              gsi_data=gsi_data)
            if gsi_data is not None:
                archive_drama_scheduler_scoring(gsi_data)
            self._chapter_with_drama_nodes_to_schedule = None
        if False:
            yield None

    def cleanup(self):
        if self._current_chapter is not None:
            self._current_chapter.cleanup()
        self._tracker = None
        self._stored_participants = None

    def _get_additional_participants_for_resolver(self):
        if self._stored_participants is None:
            return {}
        additional_participants = {}
        sim_info_manager = services.sim_info_manager()
        for participant, obj in self._stored_participants.items():
            if participant & STORY_PROGRESSION_SIM_PARTICIPANTS:
                obj = sim_info_manager.get(obj)
                if obj is None:
                    continue
            additional_participants[participant] = (
             obj,)

        return additional_participants

    def get_resolver(self):
        raise NotImplementedError

    def _get_drama_node_resolver(self, actor_sim_info):
        raise NotImplementedError

    def store_participant(self, participant, obj):
        if obj is None:
            logger.error('Arc {} is attempting to store participant {} but obj is None.', self, participant)
            return
        if not isinstance(obj, (int, str, LocalizedString)):
            logger.error('Arc {} is attempting to store participant {} object {} of unsupported type {}.', self, participant, obj, type(obj))
            return
        if self._stored_participants is None:
            self._stored_participants = {}
        if participant in self._stored_participants:
            logger.warn('Setting participant {} to {} which is already within the stored participants as {}.  This is fine if such overwriting of participants is expected.', participant, obj, self._stored_participants[participant])
        self._stored_participants[participant] = obj

    def get_gsi_data(self):
        if self._current_chapter is None:
            current_chapter = 'No Current Chapter'
            current_chapter_data = []
        else:
            current_chapter = str(self._current_chapter)
            current_chapter_data = self._current_chapter.get_gsi_data()
        historical_chapter_data = []
        if self._historical_chapters is not None:
            expiration_timespan = StoryProgTunables.HISTORY.chapter_history_lifetime()
            for chapter in self._historical_chapters:
                completion_time = chapter.get_completion_time()
                time_until_expiration = completion_time + expiration_timespan - services.time_service().sim_now
                historical_chapter_data.append({'chapter':str(chapter), 
                 'time_completed':str(completion_time), 
                 'time_until_expiration':str(time_until_expiration)})

        entry = {'arc_type':str(self), 
         'chapter_type':current_chapter, 
         'current_chapter_data':current_chapter_data, 
         'historical_chapter_data':historical_chapter_data}
        return entry

    def try_remove_historical_chapter(self, chapter):
        if self._historical_chapters is not None:
            if chapter in self._historical_chapters:
                self._historical_chapters.remove(chapter)
                return True
        return False

    def get_random_historical_chapter(self):
        if not self._historical_chapters:
            return (None, None)
        index = random.randint(0, len(self._historical_chapters) - 1)
        chapter = self._historical_chapters[index]
        tokens = [
         self.get_resolver().get_participant(self._actor_participant)]
        tokens += self._get_discovery_tokens(chapter)
        return (
         chapter, tokens)

    def _get_discovery_tokens(self, chapter):
        tokens = []
        if self._stored_participants is None or chapter.discovery is None:
            return tokens
        sim_info_manager = services.sim_info_manager()
        zone_manager = services.get_zone_manager()
        for participant_type in chapter.discovery.token_participants:
            obj = None
            value = self._stored_participants.get(participant_type)
            if value is not None:
                if participant_type & STORY_PROGRESSION_SIM_PARTICIPANTS:
                    obj = sim_info_manager.get(value)
                else:
                    if participant_type & STORY_PROGRESSION_ZONE_PARTICIPANTS:
                        obj = zone_manager.get(value)
                    else:
                        if participant_type & STORY_PROGRESSION_STRING_PARTICIPANTS:
                            obj = value
            if obj is None:
                logger.error('Stored participant type {0} not found for story progression arc {1}', participant_type, self)
            else:
                tokens.append(obj)

        return tokens

    def save(self, arc_msg):
        arc_msg.type = self.guid64
        if self._current_chapter is not None:
            self._current_chapter.save(arc_msg.current_chapter)
        if self._historical_chapters is not None:
            for historical_chapter in self._historical_chapters:
                with ProtocolBufferRollback(arc_msg.historical_chapters) as historical_chapter_msg:
                    historical_chapter.save(historical_chapter_msg)

        if self._stored_participants is not None:
            for participant_type, participant in self._stored_participants.items():
                with ProtocolBufferRollback(arc_msg.saved_participants) as participant_msg:
                    participant_msg.participant_type = get_number_of_bit_shifts_by_participant_type(participant_type)
                    if type(participant) is str:
                        participant_msg.participant_str = participant
                    else:
                        if type(participant) is int:
                            participant_msg.participant_id = int(participant)
                        else:
                            if isinstance(participant, LocalizedString):
                                participant_msg.participant_loc_str = participant
                            else:
                                raise RuntimeError('Arc {} is attempting to save unknown type for stored participant {}.'.format(self, participant))

    def load--- This code section failed: ---

 L. 371         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              get_instance_manager
                4  LOAD_GLOBAL              Types
                6  LOAD_ATTR                STORY_CHAPTER
                8  CALL_METHOD_1         1  '1 positional argument'
               10  STORE_FAST               'chapter_instance_manager'

 L. 372        12  LOAD_FAST                'arc_msg'
               14  LOAD_METHOD              HasField
               16  LOAD_STR                 'current_chapter'
               18  CALL_METHOD_1         1  '1 positional argument'
               20  POP_JUMP_IF_FALSE    80  'to 80'

 L. 373        22  LOAD_FAST                'chapter_instance_manager'
               24  LOAD_METHOD              get
               26  LOAD_FAST                'arc_msg'
               28  LOAD_ATTR                current_chapter
               30  LOAD_ATTR                type
               32  CALL_METHOD_1         1  '1 positional argument'
               34  STORE_FAST               'chapter_type'

 L. 374        36  LOAD_FAST                'chapter_type'
               38  LOAD_CONST               None
               40  COMPARE_OP               is-not
               42  POP_JUMP_IF_FALSE    80  'to 80'

 L. 375        44  LOAD_FAST                'chapter_type'
               46  LOAD_FAST                'self'
               48  CALL_FUNCTION_1       1  '1 positional argument'
               50  STORE_FAST               'chapter'

 L. 376        52  LOAD_FAST                'chapter'
               54  LOAD_METHOD              load
               56  LOAD_FAST                'arc_msg'
               58  LOAD_ATTR                current_chapter
               60  CALL_METHOD_1         1  '1 positional argument'
               62  POP_TOP          

 L. 377        64  LOAD_FAST                'chapter'
               66  LOAD_FAST                'self'
               68  STORE_ATTR               _current_chapter

 L. 378        70  LOAD_FAST                'self'
               72  LOAD_ATTR                _current_chapter
               74  LOAD_METHOD              on_set_current
               76  CALL_METHOD_0         0  '0 positional arguments'
               78  POP_TOP          
             80_0  COME_FROM            42  '42'
             80_1  COME_FROM            20  '20'

 L. 380        80  LOAD_GLOBAL              services
               82  LOAD_METHOD              time_service
               84  CALL_METHOD_0         0  '0 positional arguments'
               86  LOAD_ATTR                sim_now
               88  STORE_FAST               'now'

 L. 381        90  LOAD_GLOBAL              StoryProgTunables
               92  LOAD_ATTR                HISTORY
               94  LOAD_METHOD              chapter_history_lifetime
               96  CALL_METHOD_0         0  '0 positional arguments'
               98  STORE_FAST               'expiration_timespan'

 L. 383       100  SETUP_LOOP          204  'to 204'
              102  LOAD_FAST                'arc_msg'
              104  LOAD_ATTR                historical_chapters
              106  GET_ITER         
            108_0  COME_FROM           200  '200'
            108_1  COME_FROM           152  '152'
            108_2  COME_FROM           132  '132'
              108  FOR_ITER            202  'to 202'
              110  STORE_FAST               'historical_chapter_msg'

 L. 384       112  LOAD_FAST                'chapter_instance_manager'
              114  LOAD_METHOD              get
              116  LOAD_FAST                'historical_chapter_msg'
              118  LOAD_ATTR                type
              120  CALL_METHOD_1         1  '1 positional argument'
              122  STORE_FAST               'chapter_type'

 L. 385       124  LOAD_FAST                'chapter_type'
              126  LOAD_CONST               None
              128  COMPARE_OP               is
              130  POP_JUMP_IF_FALSE   134  'to 134'

 L. 386       132  CONTINUE            108  'to 108'
            134_0  COME_FROM           130  '130'

 L. 388       134  LOAD_FAST                'now'
              136  LOAD_GLOBAL              DateAndTime
              138  LOAD_FAST                'historical_chapter_msg'
              140  LOAD_ATTR                completion_time
              142  CALL_FUNCTION_1       1  '1 positional argument'
              144  BINARY_SUBTRACT  
              146  LOAD_FAST                'expiration_timespan'
              148  COMPARE_OP               >
              150  POP_JUMP_IF_FALSE   154  'to 154'

 L. 389       152  CONTINUE            108  'to 108'
            154_0  COME_FROM           150  '150'

 L. 390       154  LOAD_FAST                'self'
              156  LOAD_ATTR                _historical_chapters
              158  LOAD_CONST               None
              160  COMPARE_OP               is
              162  POP_JUMP_IF_FALSE   170  'to 170'

 L. 391       164  BUILD_LIST_0          0 
              166  LOAD_FAST                'self'
              168  STORE_ATTR               _historical_chapters
            170_0  COME_FROM           162  '162'

 L. 392       170  LOAD_FAST                'chapter_type'
              172  LOAD_FAST                'self'
              174  CALL_FUNCTION_1       1  '1 positional argument'
              176  STORE_FAST               'chapter'

 L. 393       178  LOAD_FAST                'chapter'
              180  LOAD_METHOD              load
              182  LOAD_FAST                'historical_chapter_msg'
              184  CALL_METHOD_1         1  '1 positional argument'
              186  POP_TOP          

 L. 394       188  LOAD_FAST                'self'
              190  LOAD_ATTR                _historical_chapters
              192  LOAD_METHOD              append
              194  LOAD_FAST                'chapter'
              196  CALL_METHOD_1         1  '1 positional argument'
              198  POP_TOP          
              200  JUMP_LOOP           108  'to 108'
              202  POP_BLOCK        
            204_0  COME_FROM_LOOP      100  '100'

 L. 396       204  SETUP_LOOP          364  'to 364'
              206  LOAD_FAST                'arc_msg'
              208  LOAD_ATTR                saved_participants
              210  GET_ITER         
            212_0  COME_FROM           360  '360'
            212_1  COME_FROM           348  '348'
            212_2  COME_FROM           310  '310'
            212_3  COME_FROM           288  '288'
              212  FOR_ITER            362  'to 362'
              214  STORE_FAST               'participant_msg'

 L. 397       216  LOAD_FAST                'self'
              218  LOAD_ATTR                _stored_participants
              220  LOAD_CONST               None
              222  COMPARE_OP               is
              224  POP_JUMP_IF_FALSE   232  'to 232'

 L. 398       226  BUILD_MAP_0           0 
              228  LOAD_FAST                'self'
              230  STORE_ATTR               _stored_participants
            232_0  COME_FROM           224  '224'

 L. 399       232  LOAD_GLOBAL              ParticipantType
              234  LOAD_CONST               1
              236  LOAD_FAST                'participant_msg'
              238  LOAD_ATTR                participant_type
              240  BINARY_LSHIFT    
              242  CALL_FUNCTION_1       1  '1 positional argument'
              244  STORE_FAST               'participant_type'

 L. 400       246  LOAD_FAST                'participant_msg'
              248  LOAD_METHOD              HasField
              250  LOAD_STR                 'participant_str'
              252  CALL_METHOD_1         1  '1 positional argument'
          254_256  POP_JUMP_IF_FALSE   266  'to 266'

 L. 401       258  LOAD_FAST                'participant_msg'
              260  LOAD_ATTR                participant_str
              262  STORE_FAST               'participant'
              264  JUMP_FORWARD        350  'to 350'
            266_0  COME_FROM           254  '254'

 L. 402       266  LOAD_FAST                'participant_msg'
              268  LOAD_METHOD              HasField
              270  LOAD_STR                 'participant_loc_str'
              272  CALL_METHOD_1         1  '1 positional argument'
          274_276  POP_JUMP_IF_FALSE   314  'to 314'

 L. 403       278  LOAD_FAST                'participant_msg'
              280  LOAD_ATTR                participant_loc_str
              282  LOAD_ATTR                hash
              284  LOAD_CONST               0
              286  COMPARE_OP               !=
              288  POP_JUMP_IF_FALSE_LOOP   212  'to 212'

 L. 404       290  LOAD_GLOBAL              LocalizedString
              292  CALL_FUNCTION_0       0  '0 positional arguments'
              294  STORE_FAST               'participant'

 L. 405       296  LOAD_FAST                'participant'
              298  LOAD_METHOD              MergeFrom
              300  LOAD_FAST                'participant_msg'
              302  LOAD_ATTR                participant_loc_str
              304  CALL_METHOD_1         1  '1 positional argument'
              306  POP_TOP          
              308  JUMP_FORWARD        312  'to 312'

 L. 407       310  CONTINUE            212  'to 212'
            312_0  COME_FROM           308  '308'
              312  JUMP_FORWARD        350  'to 350'
            314_0  COME_FROM           274  '274'

 L. 408       314  LOAD_FAST                'participant_msg'
              316  LOAD_METHOD              HasField
              318  LOAD_STR                 'participant_id'
              320  CALL_METHOD_1         1  '1 positional argument'
          322_324  POP_JUMP_IF_FALSE   334  'to 334'

 L. 409       326  LOAD_FAST                'participant_msg'
              328  LOAD_ATTR                participant_id
              330  STORE_FAST               'participant'
              332  JUMP_FORWARD        350  'to 350'
            334_0  COME_FROM           322  '322'

 L. 411       334  LOAD_GLOBAL              logger
              336  LOAD_METHOD              error
              338  LOAD_STR                 'Arc {} is attempting to load unknown type for stored participant {}.'
              340  LOAD_FAST                'self'
              342  LOAD_FAST                'participant_msg'
              344  CALL_METHOD_3         3  '3 positional arguments'
              346  POP_TOP          

 L. 412       348  CONTINUE            212  'to 212'
            350_0  COME_FROM           332  '332'
            350_1  COME_FROM           312  '312'
            350_2  COME_FROM           264  '264'

 L. 413       350  LOAD_FAST                'participant'
              352  LOAD_FAST                'self'
              354  LOAD_ATTR                _stored_participants
              356  LOAD_FAST                'participant_type'
              358  STORE_SUBSCR     
              360  JUMP_LOOP           212  'to 212'
              362  POP_BLOCK        
            364_0  COME_FROM_LOOP      204  '204'

Parse error at or near `JUMP_FORWARD' instruction at offset 312

    def on_zone_load(self):
        raise NotImplementedError

    def remove_expired_historical_chapters(self):
        if not self._historical_chapters:
            return
        now = services.time_service().sim_now
        expiration_timespan = StoryProgTunables.HISTORY.chapter_history_lifetime()
        for historical_chapter in tuple(self._historical_chapters):
            completion_time = historical_chapter.get_completion_time()
            time_since_completion = now - completion_time
            if time_since_completion > expiration_timespan:
                historical_chapter.cleanup()
                self._historical_chapters.remove(historical_chapter)


class SimStoryArc(BaseStoryArc):
    INSTANCE_TUNABLES = {'starting_chapter':TunableReference(description='\n            The first chapter of this Story Arc.\n            ',
       manager=services.get_instance_manager(Types.STORY_CHAPTER),
       class_restrictions='SimStoryChapter'), 
     'candidate_selection_function':TunableVariant(description='\n            The function used to figure out the actual candidates to run the arcs on.\n            ',
       sim_from_demographic_list=SelectSimCandidateFromDemographicListFunction.TunableFactory(),
       sim_from_filter=SelectSimCandidateFromFilterFunction.TunableFactory(),
       default='sim_from_demographic_list')}

    @classproperty
    def _initial_story_chapter(cls):
        return cls.starting_chapter

    @constproperty
    def _actor_participant():
        return ParticipantType.Actor

    @constproperty
    def arc_type():
        return StoryType.SIM_BASED

    @property
    def sim_info(self):
        return self._tracker.sim_info

    @property
    def reserved_household_slots(self):
        if self._current_chapter is None:
            return 0
        return self._current_chapter.reserved_household_slots

    def get_resolver(self):
        return SingleSimResolver((self._tracker.sim_info), additional_participants=(self._get_additional_participants_for_resolver()))

    def _get_drama_node_resolver(self, actor_sim_info):
        return DoubleSimResolver(actor_sim_info, (self._tracker.sim_info), additional_participants=(self._get_additional_participants_for_resolver()))

    def load(self, arc_msg):
        super().load(arc_msg)
        if self._historical_chapters:
            services.get_story_progression_service().cache_historical_arcs_sim_id(self.sim_info.id)

    def on_zone_load(self):
        if self._historical_chapters:
            services.get_story_progression_service().cache_historical_arcs_sim_id(self.sim_info.id)


class HouseholdStoryArc(BaseStoryArc):
    INSTANCE_TUNABLES = {'starting_chapter':TunableReference(description='\n            The first chapter of this Story Arc.\n            ',
       manager=services.get_instance_manager(Types.STORY_CHAPTER),
       class_restrictions='HouseholdStoryChapter'), 
     'candidate_selection_function':TunableVariant(description='\n            The function used to figure out the actual candidates to run the arcs on.\n            ',
       household_and_livable_lot_from_demographic_list=SelectHouseholdCandidateMatchingLotFromDemographicListFunction.TunableFactory(),
       household_based_on_culling=SelectHouseholdWithHomeCandidateFromDemographicListBasedOnCullingScoreFunction.TunableFactory(),
       default='household_based_on_culling')}

    @classproperty
    def _initial_story_chapter(cls):
        return cls.starting_chapter

    @constproperty
    def _actor_participant():
        return ParticipantType.ActorHousehold

    @constproperty
    def arc_type():
        return StoryType.HOUSEHOLD_BASED

    @property
    def household(self):
        return self._tracker.household

    def get_resolver(self):
        return HouseholdResolver((self._tracker.household), additional_participants=(self._get_additional_participants_for_resolver()))

    def _get_drama_node_resolver(self, actor_sim_info):
        return SingleSimAndHouseholdResolver(actor_sim_info, (self._tracker.household), additional_participants=(self._get_additional_participants_for_resolver()))

    def load(self, arc_msg):
        super().load(arc_msg)
        if self._historical_chapters:
            services.get_story_progression_service().cache_historical_arcs_household_id(self.household.id)

    def on_zone_load(self):
        if self._historical_chapters:
            services.get_story_progression_service().cache_historical_arcs_household_id(self.household.id)