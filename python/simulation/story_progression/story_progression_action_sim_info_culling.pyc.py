# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_action_sim_info_culling.py
# Compiled at: 2019-10-25 17:02:21
# Size of source mod 2**32: 37518 bytes
from collections import Counter, namedtuple
import itertools
from gsi_handlers.sim_info_culling_handler import CullingArchive, CullingCensus
from objects import ALL_HIDDEN_REASONS
from performance.performance_commands import get_sim_info_creation_sources
from sims.genealogy_tracker import genealogy_caching
from sims.household import Household
from sims.sim_info_lod import SimInfoLODLevel
from sims4.math import MAX_INT32
from sims4.tuning.tunable import TunableRange, TunableTuple, TunablePercent, TunableMapping, TunableEnumEntry, OptionalTunable
from story_progression import StoryProgressionFlags
from story_progression.story_progression_action import _StoryProgressionAction
from story_progression.story_progression_enums import CullingReasons
from tunable_time import TunableTimeOfDay
from uid import UniqueIdGenerator
import gsi_handlers, services, sims4.log, telemetry_helper
logger = sims4.log.Logger('SimInfoCulling', default_owner='manus')
TELEMETRY_GROUP_STORY_PROGRESSION = 'STRY'
TELEMETRY_HOOK_CULL_SIMINFO_BEFORE = 'CSBE'
TELEMETRY_HOOK_CULL_SIMINFO_BEFORE2 = 'CSBT'
TELEMETRY_HOOK_CULL_SIMINFO_AFTER = 'CSAF'
TELEMETRY_CREATION_SOURCE_HOOK_COUNT = 10
TELEMETRY_CREATION_SOURCE_BUFFER_LENGTH = 100
with sims4.reload.protected(globals()):
    telemetry_id_generator = UniqueIdGenerator()
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_STORY_PROGRESSION)
SimInfoCullingScoreInfo = namedtuple('SimInfoCullingScoreInfo', ('score', 'rel_score',
                                                                 'inst_score', 'importance_score'))
DEFAULT_CULLING_INFO = SimInfoCullingScoreInfo(0, 0, 0, 1.0)

class StoryProgressionActionMaxPopulation(_StoryProgressionAction):
    FACTORY_TUNABLES = {'sim_info_cap_per_lod':TunableMapping(description="\n            The mapping of SimInfoLODLevel value to an interval of sim info cap\n            integer values.\n            \n            NOTE: The ACTIVE lod can't be tuned here because it's being tracked\n            via the Maximum Size tuning in Household module tuning.\n            ",
       key_type=TunableEnumEntry(description='\n                The SimInfoLODLevel value.\n                ',
       tunable_type=SimInfoLODLevel,
       default=(SimInfoLODLevel.FULL),
       invalid_enums=(
      SimInfoLODLevel.ACTIVE,)),
       value_type=TunableRange(description='\n                The number of sim infos allowed to be present before culling\n                is triggered for this SimInfoLODLevel.\n                ',
       tunable_type=int,
       default=210,
       minimum=0)), 
     'time_of_day':TunableTuple(description='\n            Only run this action when it is between a certain time of day.\n            ',
       start_time=TunableTimeOfDay(default_hour=2),
       end_time=TunableTimeOfDay(default_hour=6)), 
     'culling_buffer_percentage':TunablePercent(description='\n            When sim infos are culled due to the number of sim infos exceeding\n            the cap, this is how much below the cap the number of sim infos\n            will be (as a percentage of the cap) after the culling, roughly.\n            The margin of error is due to the fact that we cull at the household\n            level, so the number of sims culled can be a bit more than this value\n            if the last household culled contains more sims than needed to reach\n            the goal. (i.e. we never cull partial households)\n            ',
       default=20), 
     'homeless_played_demotion_time':OptionalTunable(description='\n            If enabled, played Sims that have been homeless for at least this\n            many days will be drops from FULL to BASE_SIMULATABLE lod.\n            ',
       tunable=TunableRange(tunable_type=int,
       default=10,
       minimum=0))}

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)
        self._played_family_tree_distances = {}
        self._precull_telemetry_data = Counter()
        self._precull_telemetry_lod_counts_str = ''
        self._telemetry_id = 0
        self._total_sim_cap = Household.MAXIMUM_SIZE
        self._total_sim_cap += sum(self.sim_info_cap_per_lod.values())
        import sims.sim_info_manager
        sims.sim_info_manager.SimInfoManager.SIM_INFO_CAP = self._total_sim_cap
        sims.sim_info_manager.SIM_INFO_CAP_PER_LOD = self.sim_info_cap_per_lod

    def should_process(self, options):
        current_time = services.time_service().sim_now
        if not current_time.time_between_day_times(self.time_of_day.start_time, self.time_of_day.end_time):
            return False
        return True

    def process_action(self, story_progression_flags):
        try:
            self._pre_cull()
            self._process_full()
            self._process_interacted()
            self._process_base()
            self._process_background()
            self._process_minimum()
            self._post_cull(story_progression_flags)
        finally:
            self._cleanup()

    def _get_cap_level(self, sim_info_lod):
        cap_override = services.sim_info_manager().get_sim_info_cap_override_per_lod(sim_info_lod)
        if cap_override is not None:
            return cap_override
        if sim_info_lod in self.sim_info_cap_per_lod:
            return self.sim_info_cap_per_lod[sim_info_lod]
        return 0

    def _pre_cull(self):
        self._played_family_tree_distances = self._get_played_family_tree_distances()
        self._telemetry_id = telemetry_id_generator()
        self._precull_telemetry_data['scap'] = self._total_sim_cap
        player_households, player_sims, households, sims, lod_counts = self._get_census()
        self._precull_telemetry_data['thob'] = households
        self._precull_telemetry_data['tsib'] = sims
        self._precull_telemetry_data['phob'] = player_households
        self._precull_telemetry_data['psib'] = player_sims
        self._precull_telemetry_lod_counts_str = self._get_lod_counts_str_for_telemetry(lod_counts)
        for sim_info in services.sim_info_manager().get_all():
            sim_info.report_telemetry('pre-culling')

        self._trigger_creation_source_telemetry()

    def _trigger_creation_source_telemetry(self):
        payload = ''
        counter = 0

        def dump_hook():
            hook_name = 'CS{:0>2}'.format(counter)
            with telemetry_helper.begin_hook(writer, hook_name) as hook:
                hook.write_int('clid', self._telemetry_id)
                hook.write_string('crsr', payload)

        sources = get_sim_info_creation_sources()
        for source, count in sources.most_common():
            if counter >= TELEMETRY_CREATION_SOURCE_HOOK_COUNT:
                break
            else:
                delta = '{}${}'.format(source, count)
            if len(payload) + len(delta) <= TELEMETRY_CREATION_SOURCE_BUFFER_LENGTH:
                payload = '{}+{}'.format(payload, delta)
            else:
                dump_hook()
                payload = delta
                counter += 1

        dump_hook()

    def _process_full--- This code section failed: ---

 L. 252         0  LOAD_GLOBAL              gsi_handlers
                2  LOAD_ATTR                sim_info_culling_handler
                4  LOAD_METHOD              is_archive_enabled
                6  CALL_METHOD_0         0  '0 positional arguments'
                8  POP_JUMP_IF_FALSE    30  'to 30'

 L. 253        10  LOAD_GLOBAL              CullingArchive
               12  LOAD_STR                 'Full Pass'
               14  CALL_FUNCTION_1       1  '1 positional argument'
               16  STORE_FAST               'gsi_archive'

 L. 254        18  LOAD_FAST                'self'
               20  LOAD_METHOD              _get_gsi_culling_census
               22  CALL_METHOD_0         0  '0 positional arguments'
               24  LOAD_FAST                'gsi_archive'
               26  STORE_ATTR               census_before
               28  JUMP_FORWARD         34  'to 34'
             30_0  COME_FROM             8  '8'

 L. 256        30  LOAD_CONST               None
               32  STORE_FAST               'gsi_archive'
             34_0  COME_FROM            28  '28'

 L. 258        34  LOAD_FAST                'self'
               36  LOAD_METHOD              _get_cap_level
               38  LOAD_GLOBAL              SimInfoLODLevel
               40  LOAD_ATTR                FULL
               42  CALL_METHOD_1         1  '1 positional argument'
               44  STORE_FAST               'cap'

 L. 259        46  LOAD_GLOBAL              services
               48  LOAD_METHOD              sim_info_manager
               50  CALL_METHOD_0         0  '0 positional arguments'
               52  LOAD_METHOD              get_sim_infos_with_lod
               54  LOAD_GLOBAL              SimInfoLODLevel
               56  LOAD_ATTR                FULL
               58  CALL_METHOD_1         1  '1 positional argument'
               60  STORE_FAST               'sim_infos'

 L. 260        62  LOAD_GLOBAL              services
               64  LOAD_METHOD              time_service
               66  CALL_METHOD_0         0  '0 positional arguments'
               68  LOAD_ATTR                sim_now
               70  STORE_FAST               'now'

 L. 261        72  LOAD_GLOBAL              set
               74  CALL_FUNCTION_0       0  '0 positional arguments'
               76  STORE_FAST               'mandatory_drops'

 L. 262        78  BUILD_MAP_0           0 
               80  STORE_DEREF              'scores'

 L. 263        82  SETUP_LOOP          334  'to 334'
               84  LOAD_FAST                'sim_infos'
               86  GET_ITER         
             88_0  COME_FROM           330  '330'
             88_1  COME_FROM           314  '314'
             88_2  COME_FROM           306  '306'
             88_3  COME_FROM           270  '270'
             88_4  COME_FROM           204  '204'
             88_5  COME_FROM           188  '188'
             88_6  COME_FROM           168  '168'
             88_7  COME_FROM           126  '126'
             88_8  COME_FROM           110  '110'
               88  FOR_ITER            332  'to 332'
               90  STORE_FAST               'sim_info'

 L. 264        92  LOAD_FAST                'sim_info'
               94  LOAD_ATTR                is_instanced
               96  LOAD_GLOBAL              ALL_HIDDEN_REASONS
               98  LOAD_CONST               ('allow_hidden_flags',)
              100  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              102  POP_JUMP_IF_FALSE   128  'to 128'

 L. 265       104  LOAD_FAST                'gsi_archive'
              106  LOAD_CONST               None
              108  COMPARE_OP               is-not
              110  POP_JUMP_IF_FALSE_LOOP    88  'to 88'

 L. 266       112  LOAD_FAST                'gsi_archive'
              114  LOAD_ATTR                add_sim_info_cullability
              116  LOAD_FAST                'sim_info'
              118  LOAD_STR                 'immune -- instanced'
              120  LOAD_CONST               ('info',)
              122  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              124  POP_TOP          

 L. 267       126  CONTINUE             88  'to 88'
            128_0  COME_FROM           102  '102'

 L. 269       128  LOAD_FAST                'sim_info'
              130  LOAD_ATTR                is_player_sim
              132  POP_JUMP_IF_TRUE    170  'to 170'

 L. 270       134  LOAD_FAST                'gsi_archive'
              136  LOAD_CONST               None
              138  COMPARE_OP               is-not
              140  POP_JUMP_IF_FALSE   158  'to 158'

 L. 271       142  LOAD_FAST                'gsi_archive'
              144  LOAD_ATTR                add_sim_info_cullability
              146  LOAD_FAST                'sim_info'
              148  LOAD_CONST               0
              150  LOAD_STR                 'mandatory drop -- non-player'
              152  LOAD_CONST               ('score', 'info')
              154  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              156  POP_TOP          
            158_0  COME_FROM           140  '140'

 L. 272       158  LOAD_FAST                'mandatory_drops'
              160  LOAD_METHOD              add
              162  LOAD_FAST                'sim_info'
              164  CALL_METHOD_1         1  '1 positional argument'
              166  POP_TOP          

 L. 273       168  CONTINUE             88  'to 88'
            170_0  COME_FROM           132  '132'

 L. 275       170  LOAD_FAST                'sim_info'
              172  LOAD_ATTR                household
              174  LOAD_ATTR                home_zone_id
              176  LOAD_CONST               0
              178  COMPARE_OP               !=
              180  POP_JUMP_IF_FALSE   206  'to 206'

 L. 276       182  LOAD_FAST                'gsi_archive'
              184  LOAD_CONST               None
              186  COMPARE_OP               is-not
              188  POP_JUMP_IF_FALSE_LOOP    88  'to 88'

 L. 277       190  LOAD_FAST                'gsi_archive'
              192  LOAD_ATTR                add_sim_info_cullability
              194  LOAD_FAST                'sim_info'
              196  LOAD_STR                 'immune -- player and not homeless'
              198  LOAD_CONST               ('info',)
              200  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              202  POP_TOP          

 L. 278       204  CONTINUE             88  'to 88'
            206_0  COME_FROM           180  '180'

 L. 280       206  LOAD_FAST                'self'
              208  LOAD_ATTR                homeless_played_demotion_time
              210  LOAD_CONST               None
              212  COMPARE_OP               is-not
          214_216  POP_JUMP_IF_FALSE   308  'to 308'

 L. 281       218  LOAD_FAST                'now'
              220  LOAD_FAST                'sim_info'
              222  LOAD_ATTR                household
              224  LOAD_ATTR                home_zone_move_in_time
              226  BINARY_SUBTRACT  
              228  LOAD_METHOD              in_days
              230  CALL_METHOD_0         0  '0 positional arguments'
              232  STORE_FAST               'days_homeless'

 L. 282       234  LOAD_FAST                'days_homeless'
              236  LOAD_FAST                'self'
              238  LOAD_ATTR                homeless_played_demotion_time
              240  COMPARE_OP               <
          242_244  POP_JUMP_IF_FALSE   272  'to 272'

 L. 283       246  LOAD_FAST                'gsi_archive'
              248  LOAD_CONST               None
              250  COMPARE_OP               is-not
          252_254  POP_JUMP_IF_FALSE   306  'to 306'

 L. 284       256  LOAD_FAST                'gsi_archive'
              258  LOAD_ATTR                add_sim_info_cullability
              260  LOAD_FAST                'sim_info'
              262  LOAD_STR                 'immune -- not homeless long enough'
              264  LOAD_CONST               ('info',)
              266  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              268  POP_TOP          
              270  JUMP_LOOP            88  'to 88'
            272_0  COME_FROM           242  '242'

 L. 286       272  LOAD_FAST                'gsi_archive'
              274  LOAD_CONST               None
              276  COMPARE_OP               is-not
          278_280  POP_JUMP_IF_FALSE   298  'to 298'

 L. 287       282  LOAD_FAST                'gsi_archive'
              284  LOAD_ATTR                add_sim_info_cullability
              286  LOAD_FAST                'sim_info'
              288  LOAD_FAST                'days_homeless'
              290  LOAD_STR                 'homeless for too long'
              292  LOAD_CONST               ('score', 'info')
              294  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              296  POP_TOP          
            298_0  COME_FROM           278  '278'

 L. 288       298  LOAD_FAST                'days_homeless'
              300  LOAD_DEREF               'scores'
              302  LOAD_FAST                'sim_info'
              304  STORE_SUBSCR     
            306_0  COME_FROM           252  '252'

 L. 289       306  CONTINUE             88  'to 88'
            308_0  COME_FROM           214  '214'

 L. 291       308  LOAD_FAST                'gsi_archive'
              310  LOAD_CONST               None
              312  COMPARE_OP               is-not
              314  POP_JUMP_IF_FALSE_LOOP    88  'to 88'

 L. 292       316  LOAD_FAST                'gsi_archive'
              318  LOAD_ATTR                add_sim_info_cullability
              320  LOAD_FAST                'sim_info'
              322  LOAD_STR                 'immune -- no pressure to drop'
              324  LOAD_CONST               ('info',)
              326  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              328  POP_TOP          
              330  JUMP_LOOP            88  'to 88'
              332  POP_BLOCK        
            334_0  COME_FROM_LOOP       82  '82'

 L. 296       334  LOAD_FAST                'self'
              336  LOAD_METHOD              _get_num_to_cull
              338  LOAD_GLOBAL              len
              340  LOAD_FAST                'sim_infos'
              342  CALL_FUNCTION_1       1  '1 positional argument'
              344  LOAD_GLOBAL              len
              346  LOAD_FAST                'mandatory_drops'
              348  CALL_FUNCTION_1       1  '1 positional argument'
              350  BINARY_SUBTRACT  
              352  LOAD_FAST                'cap'
              354  CALL_METHOD_2         2  '2 positional arguments'
              356  STORE_FAST               'num_to_cull'

 L. 297       358  LOAD_GLOBAL              sorted
              360  LOAD_DEREF               'scores'
              362  LOAD_METHOD              keys
              364  CALL_METHOD_0         0  '0 positional arguments'
              366  LOAD_CLOSURE             'scores'
              368  BUILD_TUPLE_1         1 
              370  LOAD_LAMBDA              '<code_object <lambda>>'
              372  LOAD_STR                 'StoryProgressionActionMaxPopulation._process_full.<locals>.<lambda>'
              374  MAKE_FUNCTION_CLOSURE        'closure'
              376  LOAD_CONST               True
              378  LOAD_CONST               ('key', 'reverse')
              380  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              382  STORE_FAST               'sorted_sims'

 L. 299       384  LOAD_GLOBAL              services
              386  LOAD_METHOD              get_culling_service
              388  CALL_METHOD_0         0  '0 positional arguments'
              390  STORE_FAST               'culling_service'

 L. 301       392  SETUP_LOOP          526  'to 526'
              394  LOAD_GLOBAL              itertools
              396  LOAD_METHOD              chain
              398  LOAD_FAST                'mandatory_drops'
              400  LOAD_FAST                'sorted_sims'
              402  LOAD_CONST               None
              404  LOAD_FAST                'num_to_cull'
              406  BUILD_SLICE_2         2 
              408  BINARY_SUBSCR    
              410  CALL_METHOD_2         2  '2 positional arguments'
              412  GET_ITER         
            414_0  COME_FROM           520  '520'
            414_1  COME_FROM           496  '496'
            414_2  COME_FROM           488  '488'
              414  FOR_ITER            524  'to 524'
              416  STORE_FAST               'sim_info'

 L. 302       418  LOAD_FAST                'culling_service'
              420  LOAD_METHOD              has_sim_interacted_with_active_sim
              422  LOAD_FAST                'sim_info'
              424  LOAD_ATTR                sim_id
              426  CALL_METHOD_1         1  '1 positional argument'
          428_430  POP_JUMP_IF_FALSE   440  'to 440'

 L. 303       432  LOAD_GLOBAL              SimInfoLODLevel
              434  LOAD_ATTR                INTERACTED
              436  STORE_FAST               'new_lod'
              438  JUMP_FORWARD        446  'to 446'
            440_0  COME_FROM           428  '428'

 L. 305       440  LOAD_GLOBAL              SimInfoLODLevel
              442  LOAD_ATTR                BASE
              444  STORE_FAST               'new_lod'
            446_0  COME_FROM           438  '438'

 L. 306       446  LOAD_FAST                'sim_info'
              448  LOAD_METHOD              request_lod
              450  LOAD_FAST                'new_lod'
              452  CALL_METHOD_1         1  '1 positional argument'
          454_456  POP_JUMP_IF_FALSE   490  'to 490'

 L. 307       458  LOAD_FAST                'gsi_archive'
              460  LOAD_CONST               None
              462  COMPARE_OP               is-not
          464_466  POP_JUMP_IF_FALSE   520  'to 520'

 L. 308       468  LOAD_FAST                'gsi_archive'
              470  LOAD_ATTR                add_sim_info_action
              472  LOAD_FAST                'sim_info'
              474  LOAD_STR                 'drop to {}'
              476  LOAD_METHOD              format
              478  LOAD_FAST                'new_lod'
              480  CALL_METHOD_1         1  '1 positional argument'
              482  LOAD_CONST               ('action',)
              484  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              486  POP_TOP          
              488  JUMP_LOOP           414  'to 414'
            490_0  COME_FROM           454  '454'

 L. 310       490  LOAD_FAST                'gsi_archive'
              492  LOAD_CONST               None
              494  COMPARE_OP               is-not
          496_498  POP_JUMP_IF_FALSE_LOOP   414  'to 414'

 L. 311       500  LOAD_FAST                'gsi_archive'
              502  LOAD_ATTR                add_sim_info_action
              504  LOAD_FAST                'sim_info'
              506  LOAD_STR                 'failed to drop to {}'
              508  LOAD_METHOD              format
              510  LOAD_FAST                'new_lod'
              512  CALL_METHOD_1         1  '1 positional argument'
              514  LOAD_CONST               ('action',)
              516  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              518  POP_TOP          
            520_0  COME_FROM           464  '464'
          520_522  JUMP_LOOP           414  'to 414'
              524  POP_BLOCK        
            526_0  COME_FROM_LOOP      392  '392'

 L. 314       526  LOAD_FAST                'gsi_archive'
              528  LOAD_CONST               None
              530  COMPARE_OP               is-not
          532_534  POP_JUMP_IF_FALSE   554  'to 554'

 L. 315       536  LOAD_FAST                'self'
              538  LOAD_METHOD              _get_gsi_culling_census
              540  CALL_METHOD_0         0  '0 positional arguments'
              542  LOAD_FAST                'gsi_archive'
              544  STORE_ATTR               census_after

 L. 316       546  LOAD_FAST                'gsi_archive'
              548  LOAD_METHOD              apply
              550  CALL_METHOD_0         0  '0 positional arguments'
              552  POP_TOP          
            554_0  COME_FROM           532  '532'

Parse error at or near `CONTINUE' instruction at offset 306

    def _process_interacted(self):
        if gsi_handlers.sim_info_culling_handler.is_archive_enabled():
            gsi_archive = CullingArchive('Interacted Pass')
            gsi_archive.census_before = self._get_gsi_culling_census()
        else:
            gsi_archive = None
        culling_service = services.get_culling_service()
        cap = self._get_cap_level(SimInfoLODLevel.INTERACTED)
        sim_info_manager = services.sim_info_manager()
        interacted_sim_ids_in_priority_order = culling_service.get_interacted_sim_ids_in_priority_order()
        interacted_count = 0
        for sim_id in interacted_sim_ids_in_priority_order:
            sim_info = sim_info_manager.get(sim_id)
            if sim_info is None or sim_info.lod != SimInfoLODLevel.INTERACTED:
                culling_service.remove_sim_from_interacted_sims(sim_id)
                continue
            else:
                interacted_count += 1
            if cap < interacted_count:
                if gsi_archive is not None:
                    gsi_archive.add_sim_info_cullability(sim_info, score=(interacted_sim_ids_in_priority_order.index(sim_id)),
                      info='last interaction too old')
                elif sim_info.request_lod(SimInfoLODLevel.BASE):
                    culling_service.remove_sim_from_interacted_sims(sim_id)
                    interacted_count -= 1
                    if gsi_archive is not None:
                        gsi_archive.add_sim_info_action(sim_info, action='drop to BASE')
                else:
                    if gsi_archive is not None:
                        gsi_archive.add_sim_info_action(sim_info, action='failed to drop to INTERACTED')
            if gsi_archive is not None:
                gsi_archive.add_sim_info_cullability(sim_info, score=(interacted_sim_ids_in_priority_order.index(sim_id)),
                  info='no pressure to drop')

        if gsi_archive is not None:
            gsi_archive.census_after = self._get_gsi_culling_census()
            gsi_archive.apply()

    def _process_base(self):

        def demote_from_base(sim_info, gsi_archive):
            if sim_info.request_lod(SimInfoLODLevel.BACKGROUND):
                if gsi_archive is not None:
                    gsi_archive.add_sim_info_action(sim_info, action='drop to BACKGROUND')
            else:
                if gsi_archive is not None:
                    gsi_archive.add_sim_info_action(sim_info, action='failed to drop to BACKGROUND')

        self._process_low(SimInfoLODLevel.BASE, 'Base Pass', demote_from_base)

    def _process_background(self):
        culling_service = services.get_culling_service()
        if gsi_handlers.sim_info_culling_handler.is_archive_enabled():
            gsi_archive = CullingArchive('Background Pass')
            gsi_archive.census_before = self._get_gsi_culling_census()
        else:
            gsi_archive = None
        background_cap = self._get_cap_level(SimInfoLODLevel.BACKGROUND)
        sim_info_manager = services.sim_info_manager()
        sim_infos = sim_info_manager.get_sim_infos_with_lod(SimInfoLODLevel.BACKGROUND)
        households = frozenset((sim_info.household for sim_info in sim_infos))
        num_infos_above_background_lod = sim_info_manager.get_num_sim_infos_with_criteria(lambda sim_info: sim_info.lod > SimInfoLODLevel.BACKGROUND
)
        full_and_active_cap = self._get_cap_level(SimInfoLODLevel.FULL) + Household.MAXIMUM_SIZE
        cap_overage = num_infos_above_background_lod - full_and_active_cap
        cap = max(background_cap - cap_overage, 0) if cap_overage > 0 else background_cap
        sim_info_immunity_reasons = {}
        sim_info_scores = {}
        for sim_info in sim_infos:
            immunity_reasons = sim_info.get_culling_immunity_reasons()
            if immunity_reasons:
                sim_info_immunity_reasons[sim_info] = immunity_reasons
                continue
            else:
                sim_info_scores[sim_info] = culling_service.get_culling_score_for_sim_info(sim_info)

        household_scores = {}
        immune_households = set()
        for household in households:
            if any((sim_info.lod != SimInfoLODLevel.BACKGROUND or sim_info in sim_info_immunity_reasons for sim_info in household)):
                immune_households.add(household)
                continue
            else:
                score = max((sim_info_scores[sim_info].score for sim_info in household))
                household_scores[household] = score

        if gsi_archive is not None:
            for sim_info, immunity_reasons in sim_info_immunity_reasons.items():
                gsi_archive.add_sim_info_cullability(sim_info, info=('immune: {}'.format(', '.join((reason.gsi_reason for reason in immunity_reasons)))))

            for sim_info, score in sim_info_scores.items():
                gsi_archive.add_sim_info_cullability(sim_info, score=(score.score), rel_score=(score.rel_score),
                  inst_score=(score.inst_score),
                  importance_score=(score.importance_score))

            def get_sim_cullability(sim_info):
                if sim_info.lod > SimInfoLODLevel.BACKGROUND:
                    return 'LOD is not BACKGROUND'
                if sim_info in sim_info_immunity_reasons:
                    return ', '.join((reason.gsi_reason for reason in sim_info_immunity_reasons[sim_info]))
                if sim_info in sim_info_scores:
                    return str(sim_info_scores[sim_info].score)
                return ''

            for household in immune_households:
                member_cullabilities = ', '.join(('{} ({})'.format(sim_info.full_name, get_sim_cullability(sim_info)) for sim_info in household))
                gsi_archive.add_household_cullability(household, info=('immune: {}'.format(member_cullabilities)))

            for household, score in household_scores.items():
                member_cullabilities = ', '.join(('{} ({})'.format(sim_info.full_name, get_sim_cullability(sim_info)) for sim_info in household))
                gsi_archive.add_household_cullability(household, score=score, info=member_cullabilities)

        self._precull_telemetry_data['imho'] = len(immune_households)
        self._precull_telemetry_data['imsi'] = len(sim_info_immunity_reasons)
        self._precull_telemetry_data['imsc'] = sum((len(h) for h in immune_households))
        self._precull_telemetry_data.update((reason.telemetry_hook for reason in itertools.chain.from_iterable(sim_info_immunity_reasons.values())))
        for reason in CullingReasons.ALL_CULLING_REASONS:
            if reason not in self._precull_telemetry_data:
                self._precull_telemetry_data[reason.telemetry_hook] = 0

        culling_service = services.get_culling_service()
        sorted_households = sorted(household_scores, key=(household_scores.get))
        num_to_cull = self._get_num_to_cull(len(sim_infos), cap)
        while sorted_households:
            if num_to_cull > 0:
                household = sorted_households.pop(0)
                num_to_cull -= len(household)
                culling_service.cull_household(household, is_important_fn=(self._has_player_sim_in_family_tree), gsi_archive=gsi_archive)

        for sim_info in sim_info_manager.get_all():
            if sim_info.household is None:
                logger.error('Found sim info {} without household during sim culling.', sim_info)

        if gsi_archive is not None:
            gsi_archive.census_after = self._get_gsi_culling_census()
            gsi_archive.apply()

    def _process_minimum(self):

        def demote_from_minimum(sim_info, gsi_archive):
            if gsi_archive is not None:
                gsi_archive.add_sim_info_action(sim_info, action='cull')
            sim_info.remove_permanently()

        self._process_low(SimInfoLODLevel.MINIMUM, 'Minimum Pass', demote_from_minimum)

    def _process_low(self, current_lod, debug_pass_name, demote_fn):
        if gsi_handlers.sim_info_culling_handler.is_archive_enabled():
            gsi_archive = CullingArchive(debug_pass_name)
            gsi_archive.census_before = self._get_gsi_culling_census()
        else:
            gsi_archive = None
        cap = self._get_cap_level(current_lod)
        sim_info_manager = services.sim_info_manager()
        min_lod_sim_infos = sim_info_manager.get_sim_infos_with_lod(current_lod)
        num_min_lod_sim_infos = len(min_lod_sim_infos)
        sorted_sim_infos = sorted(min_lod_sim_infos, key=(lambda x: self._played_family_tree_distances[x.id]
), reverse=True)
        if gsi_archive is not None:
            for sim_info in min_lod_sim_infos:
                gsi_archive.add_sim_info_cullability(sim_info, score=(self._played_family_tree_distances[sim_info.id]))

        num_to_cull = self._get_num_to_cull(num_min_lod_sim_infos, cap)
        for sim_info in sorted_sim_infos[:num_to_cull]:
            demote_fn(sim_info, gsi_archive)

        if gsi_archive is not None:
            gsi_archive.census_after = self._get_gsi_culling_census()
            gsi_archive.apply()

    def _post_cull(self, story_progression_flags):
        with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_CULL_SIMINFO_BEFORE) as hook:
            hook.write_int('clid', self._telemetry_id)
            hook.write_string('rson', self._get_trigger_reason(story_progression_flags))
            for key, value in self._precull_telemetry_data.items():
                hook.write_int(key, value)

        with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_CULL_SIMINFO_BEFORE2) as hook:
            hook.write_int('clid', self._telemetry_id)
            hook.write_string('lodb', self._precull_telemetry_lod_counts_str)
        player_households, player_sims, households, sims, lod_counts = self._get_census()
        with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_CULL_SIMINFO_AFTER) as hook:
            hook.write_int('clid', self._telemetry_id)
            hook.write_string('rson', self._get_trigger_reason(story_progression_flags))
            hook.write_int('scap', self._total_sim_cap)
            hook.write_int('thoa', households)
            hook.write_int('tsia', sims)
            hook.write_string('loda', self._get_lod_counts_str_for_telemetry(lod_counts))
            hook.write_int('phoa', player_households)
            hook.write_int('psia', player_sims)

    def _cleanup(self):
        self._played_family_tree_distances.clear()
        self._precull_telemetry_data.clear()

    def _get_played_family_tree_distances(self):
        with genealogy_caching():
            sim_info_manager = services.sim_info_manager()
            played_sim_infos = frozenset((sim_info for sim_info in sim_info_manager.get_all() if sim_info.is_player_sim))

            def get_sim_ids_with_played_spouses():
                return set((sim_info.spouse_sim_id for sim_info in played_sim_infos if sim_info.spouse_sim_id is not None if sim_info.spouse_sim_id in sim_info_manager))

            def get_sim_ids_with_played_siblings():
                sim_ids_with_played_siblings = set()
                visited_ids = set()
                for sim_info in played_sim_infos:
                    if sim_info.id in visited_ids:
                        continue
                    else:
                        siblings = set(sim_info.genealogy.get_siblings_sim_infos_gen())
                        siblings.add(sim_info)
                        visited_ids.update((sibling.id for sibling in siblings))
                        played_siblings = set((sibling for sibling in siblings if sibling.is_player_sim))
                    if len(played_siblings) == 1:
                        sim_ids_with_played_siblings.update((sibling.id for sibling in siblings if sibling not in played_siblings))
                    if len(played_siblings) > 1:
                        sim_ids_with_played_siblings.update((sibling.id for sibling in siblings))

                return sim_ids_with_played_siblings

            def get_played_relative_distances(up=False):
                distances = {}
                step = 0
                next_crawl_set = set(played_sim_infos)
                while next_crawl_set:
                    step += 1
                    crawl_set = next_crawl_set
                    next_crawl_set = set()

                    def relatives_gen(sim_info):
                        if up:
                            yield from sim_info.genealogy.get_child_sim_infos_gen()
                        else:
                            yield from sim_info.genealogy.get_parent_sim_infos_gen()
                        if False:
                            yield None

                    for relative in itertools.chain.from_iterable((relatives_gen(sim_info) for sim_info in crawl_set)):
                        if relative.id in distances:
                            continue
                        else:
                            distances[relative.id] = step
                        if relative not in played_sim_infos:
                            next_crawl_set.add(relative)

                return distances

            zero_distance_sim_ids = get_sim_ids_with_played_spouses() | get_sim_ids_with_played_siblings()
            ancestor_map = get_played_relative_distances(up=True)
            descendant_map = get_played_relative_distances(up=False)

            def get_score(sim_info):
                sim_id = sim_info.id
                if sim_id in zero_distance_sim_ids:
                    return 0
                return min(ancestor_map.get(sim_id, MAX_INT32), descendant_map.get(sim_id, MAX_INT32))

            distances = {sim_info.id: get_score(sim_info) for sim_info in }
            return distances

    def _has_player_sim_in_family_tree(self, sim_info):
        if sim_info.id not in self._played_family_tree_distances:
            logger.error('Getting played family tree distance for an unknown Sim Info {}', sim_info)
            return False
        return self._played_family_tree_distances[sim_info.id] < MAX_INT32

    def _get_distance_to_nearest_player_sim_in_family_tree(self, sim_info):
        if sim_info.id not in self._played_family_tree_distances:
            logger.error('Getting played family tree distance for an unknown Sim Info {}', sim_info)
            return MAX_INT32
        return self._played_family_tree_distances[sim_info.id]

    def _get_num_to_cull(self, pop_count, pop_cap):
        if pop_cap < 0:
            logger.error('Invalid pop_cap provided to _get_num_to_cull: {}', pop_cap)
        if pop_count > pop_cap:
            target_pop = pop_cap * (1 - self.culling_buffer_percentage)
            return int(pop_count - target_pop)
        return 0

    def _get_census(self):
        player_households = sum((1 for household in services.household_manager().get_all() if household.is_player_household))
        player_sims = sum((1 for sim_info in services.sim_info_manager().get_all() if sim_info.is_player_sim))
        households = len(services.household_manager())
        sims = len(services.sim_info_manager())
        lod_counts = {lod: services.sim_info_manager().get_num_sim_infos_with_lod(lod) for lod in SimInfoLODLevel}
        return (
         player_households, player_sims, households, sims, lod_counts)

    def _get_lod_counts_str_for_telemetry(self, lod_counts):
        return '+'.join(('{}~{}'.format(lod.name, num) for lod, num in lod_counts.items()))

    def _get_gsi_culling_census(self):
        player_households, player_sims, households, sims, lod_counts = self._get_census()
        return CullingCensus(player_households, player_sims, households, sims, lod_counts)

    @classmethod
    def _get_trigger_reason(cls, flags):
        reason = 'REGULAR_PROGRESSION'
        if flags & StoryProgressionFlags.SIM_INFO_FIREMETER != 0:
            reason = 'FIREMETER'
        return reason