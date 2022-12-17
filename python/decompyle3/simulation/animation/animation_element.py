# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\animation_element.py
# Compiled at: 2021-09-01 10:58:18
# Size of source mod 2**32: 49286 bytes
import animation, animation.arb, animation.asm, animation.posture_manifest, element_utils, elements, gsi_handlers.interaction_archive_handlers, random, services, sims4.log
from animation import get_throwaway_animation_context
from animation.animation_constants import AUTO_EXIT_REF_TAG, MAX_ZERO_LENGTH_ASM_CALLS_FOR_RESET
from animation.animation_overrides_tuning import TunableParameterMapping
from animation.animation_utils import get_actors_for_arb_sequence, create_run_animation, get_auto_exit, mark_auto_exit, flush_all_animations
from animation.awareness.awareness_elements import with_audio_awareness
from animation.posture_manifest import PostureManifest, MATCH_ANY, MATCH_NONE, AnimationParticipant
from animation.tunable_animation_overrides import TunableAnimationOverrides
from balloon.tunable_balloon import TunableBalloon
from element_utils import build_critical_section, build_critical_section_with_finally, build_element, do_all
from event_testing.results import TestResult
from interactions import ParticipantType
from sims.favorites import favorites_utils
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import Tunable, TunableList, TunableTuple, OptionalTunable, HasTunableReference, TunableInteractionAsmResourceKey
from sims4.tuning.tunable_base import SourceQueries, FilterTag
from sims4.utils import classproperty, flexmethod
from singletons import DEFAULT, UNSET
logger = sims4.log.Logger('Animation')
dump_logger = sims4.log.LoggerClass('Animation')
logged_missing_interaction_callstack = False

def _create_balloon_request_callback(balloon_request=None):

    def balloon_handler_callback(_):
        balloon_request.distribute()

    return balloon_handler_callback


def register_balloon_requests(asm, balloon_requests, repeat=False, interaction=None, overrides=None):
    if not balloon_requests:
        return
    remaining_balloons = list(balloon_requests)
    for balloon_request in balloon_requests:
        balloon_delay = balloon_request.delay or 0
        if balloon_request.delay_randomization > 0:
            balloon_delay += random.random() * balloon_request.delay_randomization
        if asm.context.register_custom_event_handler(_create_balloon_request_callback(balloon_request=balloon_request), None, balloon_delay, allow_stub_creation=True):
            remaining_balloons.remove(balloon_request)
        if repeat:
            break

    if remaining_balloons and not repeat:
        logger.error('Failed to schedule all requested balloons for {}', asm)
    else:
        if repeat:
            if interaction is not None:
                if overrides is not None:
                    balloon_requests = TunableBalloon.get_balloon_requests(interaction, overrides)
    return balloon_requests


def get_asm_supported_posture(asm_key, actor_name, overrides):
    context = get_throwaway_animation_context()
    posture_manifest_overrides = None
    if overrides is not None:
        posture_manifest_overrides = overrides.manifests
    asm = animation.asm.create_asm(asm_key, context, posture_manifest_overrides=posture_manifest_overrides)
    return asm.get_supported_postures_for_actor(actor_name)


def animate_states(asm, begin_states, end_states=None, sequence=(), require_end=True, overrides=None, balloon_requests=None, setup_asm=None, cleanup_asm=None, enable_auto_exit=True, repeat_begin_states=False, interaction=None, additional_blockers=(), **kwargs):
    if asm is not None:
        requires_begin_flush = bool(sequence)
        all_actors = set()
        do_gsi_logging = interaction is not None and gsi_handlers.interaction_archive_handlers.is_archive_enabled(interaction)
        if interaction is not None:
            interaction.register_additional_event_handlers(asm.context)

        def do_begin(timeline):
            nonlocal all_actors
            nonlocal balloon_requests
            if overrides:
                overrides.override_asm(asm)
            if setup_asm is not None:
                result = setup_asm(asm)
                if not result:
                    logger.error('Animate States failed to setup ASM {}. {}', asm, result, owner='rmccord')
                if do_gsi_logging:
                    for actor_name, (actor, _, _) in asm._actors.items():
                        actor = actor()
                        gsi_handlers.interaction_archive_handlers.add_asm_actor_data(interaction, asm, actor_name, actor)

                if begin_states:
                    balloon_requests = register_balloon_requests(asm, balloon_requests, repeat=repeat_begin_states, interaction=interaction, overrides=overrides)
                    arb_begin = animation.arb.Arb(additional_blockers=additional_blockers)
                    if do_gsi_logging:
                        gsi_archive_logs = []
                    if asm.current_state == 'exit':
                        asm.set_current_state('entry')
                    for state in begin_states:
                        if do_gsi_logging:
                            prev_state = asm.current_state
                            arb_buffer = arb_begin.get_contents_as_string()
                        else:
                            asm.request(state, arb_begin, debug_context=interaction)
                        if do_gsi_logging:
                            arb_begin_str = arb_begin.get_contents_as_string()
                            current_arb_str = arb_begin_str[arb_begin_str.find(arb_buffer) + len(arb_buffer):]
                            gsi_archive_logs.append((prev_state, state, current_arb_str))

                    actors_begin = get_actors_for_arb_sequence(arb_begin)
                    all_actors = all_actors | actors_begin
                    sequence = create_run_animation(arb_begin)
                    if asm.current_state == 'exit':
                        auto_exit_releases = mark_auto_exit(actors_begin, asm)
                        if auto_exit_releases is not None:
                            sequence = build_critical_section_with_finally(sequence, auto_exit_releases)
                    try:
                        auto_exit_element = get_auto_exit(actors_begin, asm=asm, interaction=interaction)
                    except RuntimeError:
                        if do_gsi_logging:
                            for prev_state, state, current_arb_str in gsi_archive_logs:
                                gsi_handlers.interaction_archive_handlers.add_animation_data(interaction, asm, prev_state, state, current_arb_str)

                            for actor_to_log in actors_begin:
                                gsi_handlers.interaction_archive_handlers.archive_interaction(actor_to_log, interaction, 'RUNTIME ERROR')

                        raise

                    if auto_exit_element is not None:
                        sequence = (
                         auto_exit_element, sequence)
                    if enable_auto_exit:
                        if asm.current_state != 'exit':
                            auto_exit_actors = {actor for actor in all_actors if actor.is_sim if not actor.asm_auto_exit.locked}
                            for actor in auto_exit_actors:
                                if actor.asm_auto_exit.asm is None:
                                    actor.asm_auto_exit.asm = (
                                     asm, auto_exit_actors, asm.context)
                                    asm.context.add_ref(AUTO_EXIT_REF_TAG)
                                if actor.asm_auto_exit.asm[0] != asm:
                                    raise RuntimeError('Multiple ASMs in need of auto-exit simultaneously: {} and {}'.format(actor.asm_auto_exit.asm[0], asm))

                    if do_gsi_logging:
                        for prev_state, state, current_arb_str in gsi_archive_logs:
                            gsi_handlers.interaction_archive_handlers.add_animation_data(interaction, asm, prev_state, state, current_arb_str)

                    if requires_begin_flush:
                        sequence = build_critical_section(sequence, flush_all_animations)
                    sequence = build_element(sequence)
                    if sequence is not None:
                        result = yield from element_utils.run_child(timeline, sequence)
                    else:
                        result = True
                    cur_ticks = services.time_service().sim_now.absolute_ticks()
                    for actor_name, (actor, _, _) in asm._actors.items():
                        actor = actor()
                        if actor is None:
                            continue
                        if actor.is_sim:
                            if actor.asm_last_call_time == cur_ticks:
                                actor.zero_length_asm_calls += 1
                            else:
                                actor.zero_length_asm_calls = 0
                            actor.asm_last_call_time = cur_ticks
                            if actor.zero_length_asm_calls >= MAX_ZERO_LENGTH_ASM_CALLS_FOR_RESET:
                                raise RuntimeError('ASM {} is being called repeatedly with a zero-length duration.\nInteraction: {}\nPosture: {}\nStates: {} -> {}\n'.format(asm.name, interaction.get_interaction_type(), actor.posture.posture_type, begin_states, end_states))

                    return result
                return True
            if False:
                yield None

        def do_end(timeline):
            nonlocal all_actors
            arb_end = animation.arb.Arb()
            if do_gsi_logging:
                gsi_archive_logs = []
            if end_states:
                for state in end_states:
                    if do_gsi_logging:
                        prev_state = asm.current_state
                        arb_buffer = arb_end.get_contents_as_string()
                    else:
                        asm.request(state, arb_end, debug_context=interaction)
                    if do_gsi_logging:
                        arb_end_str = arb_end.get_contents_as_string()
                        current_arb_str = arb_end_str[arb_end_str.find(arb_buffer) + len(arb_buffer):]
                        gsi_archive_logs.append((prev_state, state, current_arb_str))

            actors_end = get_actors_for_arb_sequence(arb_end)
            all_actors = all_actors | actors_end
            if requires_begin_flush or not arb_end.empty:
                sequence = create_run_animation(arb_end)
            else:
                sequence = None
            if asm.current_state == 'exit':
                auto_exit_releases = mark_auto_exit(all_actors, asm)
                if auto_exit_releases is not None:
                    sequence = build_critical_section_with_finally(sequence, auto_exit_releases)
            if sequence:
                auto_exit_element = get_auto_exit(actors_end, asm=asm, interaction=interaction)
                if do_gsi_logging:
                    for prev_state, state, current_arb_str in gsi_archive_logs:
                        gsi_handlers.interaction_archive_handlers.add_animation_data(interaction, asm, prev_state, state, current_arb_str)

                if auto_exit_element is not None:
                    sequence = (
                     auto_exit_element, sequence)
                result = yield from element_utils.run_child(timeline, sequence)
                return result
            return True
            if False:
                yield None

        if repeat_begin_states:

            def do_soft_stop(timeline):
                loop.trigger_soft_stop()

            loop = elements.RepeatElement(build_element(do_begin))
            sequence = do_all(loop, build_element([sequence, do_soft_stop]))
        sequence = build_element([do_begin, sequence])
        if require_end:
            sequence = build_critical_section(sequence, do_end)
        else:
            sequence = build_element([sequence, do_end])
        sequence = with_audio_awareness(*list(asm.actors_gen()), **{'sequence': sequence})
    if cleanup_asm is not None:
        sequence = build_critical_section_with_finally(sequence, lambda _: cleanup_asm(asm)
)
    return sequence


class AnimationElement(HasTunableReference, elements.ParentElement, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ANIMATION)):
    ASM_SOURCE = 'asm_key'
    INSTANCE_TUNABLES = {ASM_SOURCE: TunableInteractionAsmResourceKey(description='\n            ASM Key is the Animation State Machine to use for this animation. \n            You are selecting from the ASMs that are in your \n            Assets/InGame/Statemachines folder, and several of the subsequent \n            fields are populated by information from this selection. \n            ',
                   default=None,
                   category='asm'), 
     
     'actor_name': Tunable(description="\n            Actor Name is the name of the main actor for this animation. In \n            almost every case this will just be 'x', so please be absolutely \n            sure you know what you're doing when changing this value.\n            ",
                     tunable_type=str,
                     default='x',
                     source_location=ASM_SOURCE,
                     source_query=(SourceQueries.ASMActorSim)), 
     
     'target_name': Tunable(description='\n            This determines which actor the target of the interaction will be. \n            In general, this should be the object that will be clicked on to \n            create interactions that use this content.\n            This helps the posture system understand what objects you already \n            know about and which to search for. Sit says its target name is \n            sitTemplate, which means you have to sit in the chair that was \n            clicked on, whereas Eat says its target name is consumable, which \n            means you can sit in any chair in the world to eat. This ends up \n            in the var_map in the runtime. \n            ',
                      tunable_type=str,
                      default=None,
                      source_location=ASM_SOURCE,
                      source_query=(SourceQueries.ASMActorAll)), 
     
     'carry_target_name': Tunable(description='\n            Carry Target Name is the actor name of the carried object in this \n            ASM. This is only relevant if the Target and Carry Target are \n            different. \n            ',
                            tunable_type=str,
                            default=None,
                            source_location=ASM_SOURCE,
                            source_query=(SourceQueries.ASMActorAll)), 
     
     'create_target_name': Tunable(description="\n            Create Target Name is the actor name of an object that will be \n            created by this interaction. This is used frequently in the \n            crafting system but rarely elsewhere. If your interaction creates \n            an object in the Sim's hand, use this. \n            ",
                             tunable_type=str,
                             default=None,
                             source_location=ASM_SOURCE,
                             source_query=(SourceQueries.ASMActorAll)), 
     
     'initial_state': OptionalTunable(description="\n             The name of the initial state in the ASM to use when begin_states \n             are requested. \n             If this is untuned, which should be the case almost all the time, \n             it will use the default initial state of 'entry'. Ask your \n             animation partner if you think you want to tune this because you \n             should not have to and it is probably best to just change the \n             structure of the ASM. Remember that ASMs are re-used within a \n             single interaction, so if you are defining an outcome animation, \n             you can rely on the state to persist from the basic content.\n             ",
                        tunable=Tunable(tunable_type=str, default=None,
                        source_location=('../' + ASM_SOURCE),
                        source_query=(SourceQueries.ASMState)),
                        disabled_value=DEFAULT,
                        disabled_name='use_default',
                        enabled_name='custom_state_name'), 
     
     'begin_states': TunableList(description='\n             A list of states in the ASM to run through at the beginning of \n             this element. Generally-speaking, you should always use \n             begin_states for all your state requests. The only time you would \n             need end_states is when you are making a staging-SuperInteraction. \n             In that case, the content in begin_states happens when the SI \n             first runs, before it stages, and the content in end_states will \n             happen as the SI is exiting. When in doubt, put all of your state \n             requests here.\n             ',
                       tunable=str,
                       source_location=ASM_SOURCE,
                       source_query=(SourceQueries.ASMState)), 
     
     '_overrides': TunableAnimationOverrides(description='\n            Overrides are for expert-level configuration of Animation Elements. \n            In 95% of cases, the animation element will work perfectly with no \n            overrides.\n            Overrides allow us to customize animations further using things \n            like vfx changes and also to account for some edge cases. \n            ',
                     asm_source=ASM_SOURCE,
                     state_source='begin_states'), 
     
     'end_states': TunableList(description="\n             A list of states to run through at the end of this element. This \n             should generally be one of two values:\n             * empty (default), which means to do no requests. This is best if \n             you don't know what to use here, as auto-exit behavior, which \n             automatically requests the 'exit' state on any ASM that is still \n             active, should handle most cases for you. Note: this is not safe \n             for elements that are used as the staging content for SIs! \n             See below!\n             * 'exit', which requests the content on the way out of the \n             statemachine. This is important to set for SuperInteractions that \n             are set to use staging basic content, as auto-exit behavior is \n             disabled in that case. This means the content on the way to exit \n             will be requested as the SI is finishing. You can put additional \n             state requests here if the ASM is more complex, but that is very \n             rare.\n             ",
                     tunable=str,
                     source_location=ASM_SOURCE,
                     source_query=(SourceQueries.ASMState)), 
     
     'repeat': Tunable(description='\n            If this is checked, then the begin_states will loop until the\n            controlling sequence (e.g. the interaction) ends. At that point,\n            end_states will play.\n            \n            This tunable allows you to create looping one-shot states. The\n            effects of this tunable on already looping states is undefined.\n            \n            This changes the interpretation of thought balloons. We will\n            trigger one balloon per loop of the animation. The delay on the\n            balloon is relative to the start of each loop rather than the start\n            of the entire sequence.\n            ',
                 tunable_type=bool,
                 default=False,
                 tuning_filter=(FilterTag.EXPERT_MODE)), 
     
     'base_object_name': OptionalTunable(description='\n            ',
                           tunable=Tunable(description='\n                If enabled this allows you to tune which actor is the base object\n                by  name. This is important if the posture target is not the\n                same as the target of the interaction.\n                \n                For example: The massage table has massage interactions that\n                target the other Sim but the massage therapist must route\n                and stand at the massage table. In this case you would need\n                to enable base_object_name and tune it to the name of the \n                actor you want to target with the posture, or in this case\n                massageTable. This is tuned in massageTable_SocialInteractions.\n                ',
                           tunable_type=str,
                           default=None,
                           source_location=('../' + ASM_SOURCE),
                           source_query=(SourceQueries.ASMActorAll)))}
    _child_animations = None
    _child_constraints = None

    def __init__(self, interaction=UNSET, setup_asm_additional=None, setup_asm_override=DEFAULT, overrides=None, use_asm_cache=True, **animate_kwargs):
        global logged_missing_interaction_callstack
        super().__init__()
        self.interaction = None if interaction is UNSET else interaction
        self.setup_asm_override = setup_asm_override
        self.setup_asm_additional = setup_asm_additional
        if overrides is not None:
            overrides = overrides()
        if not interaction is not UNSET or interaction is not None:
            if interaction.anim_overrides is not None:
                overrides = interaction.anim_overrides(overrides=overrides)
            if not interaction.is_super:
                super_interaction = self.interaction.super_interaction
                if super_interaction is not None:
                    if super_interaction.basic_content is not None:
                        if super_interaction.basic_content.content_set is not None:
                            if super_interaction.basic_content.content_set.balloon_overrides is not None:
                                balloons = super_interaction.basic_content.content_set.balloon_overrides
                                overrides = overrides(balloons=balloons)
            self.overrides = self._overrides(overrides=overrides)
            self.animate_kwargs = animate_kwargs
            self._use_asm_cache = use_asm_cache
            if interaction is None:
                if not logged_missing_interaction_callstack:
                    logger.callstack('Attempting to set up animation {} with interaction=None.', self,
                      level=(sims4.log.LEVEL_ERROR), owner='jpollak')
                    logged_missing_interaction_callstack = True

    @classmethod
    def _verify_tuning_callback(cls):
        if not cls.begin_states:
            if not cls.end_states:
                logger.error('Animation {} specifies neither begin_states nor end_states. This is not supported.', cls)
        if cls.carry_target_name is not None:
            if cls.create_target_name is not None:
                logger.error('Animation {} has specified both a carry target ({}) and a create target ({}).  This is not supported.', cls, (cls.carry_target_name), (cls.create_target_name), owner='tastle')

    @flexmethod
    def get_supported_postures(cls, inst):
        if inst is not None and inst.interaction is not None:
            asm = inst.get_asm()
            if asm is not None:
                return asm.get_supported_postures_for_actor(cls.actor_name)
        else:
            overrides = cls._overrides()
            return get_asm_supported_posture(cls.asm_key, cls.actor_name, overrides)
        return PostureManifest()

    @classproperty
    def name(cls):
        return get_asm_name(cls.asm_key)

    @classmethod
    def register_tuned_animation(cls, *args):
        if cls._child_animations is None:
            cls._child_animations = []
        cls._child_animations.append(args)

    @classmethod
    def add_auto_constraint(cls, *args, **kwargs):
        if cls._child_constraints is None:
            cls._child_constraints = []
        cls._child_constraints.append(args)

    def get_asm(self, use_cache=True, **kwargs):
        if not self._use_asm_cache:
            use_cache = False
        if self.overrides.animation_context:
            use_cache = False
        asm = (self.interaction.get_asm)(self.asm_key, self.actor_name, self.target_name, self.carry_target_name, setup_asm_override=self.setup_asm_override, 
         posture_manifest_overrides=self.overrides.manifests, 
         use_cache=use_cache, 
         create_target_name=self.create_target_name, base_object_name=self.base_object_name, **kwargs)
        if asm is None:
            return
        if self.setup_asm_additional is not None:
            result = self.setup_asm_additional(asm)
            if not result:
                logger.warn('Failed to perform additional asm setup on asm {}. {}', asm, result, owner='rmccord')
            return asm

    @flexmethod
    def append_to_arb(cls, inst, asm, arb):
        if inst is not None:
            if inst.overrides:
                inst.overrides.override_asm(asm)
                balloon_requests = TunableBalloon.get_balloon_requests(inst.interaction, inst.overrides)
                register_balloon_requests(asm, balloon_requests)
        for state_name in cls.begin_states:
            asm.request(state_name, arb)

    @classmethod
    def append_exit_to_arb(cls, asm, arb):
        for state_name in cls.end_states:
            asm.request(state_name, arb)

    def get_constraint(self, participant_type=ParticipantType.Actor):
        from interactions.constraints import Anywhere, create_animation_constraint
        if participant_type == ParticipantType.Actor:
            actor_name = self.actor_name
            target_name = self.target_name
        else:
            if participant_type == ParticipantType.TargetSim:
                actor_name = self.target_name
                target_name = self.actor_name
            else:
                return Anywhere()
        return create_animation_constraint(self.asm_key, actor_name, target_name, self.carry_target_name, self.create_target_name, self.initial_state, self.begin_states, self.end_states, self.overrides)

    @property
    def reactionlet(self):
        if self.overrides is not None:
            return self.overrides.reactionlet

    @classproperty
    def run_in_sequence(cls):
        return True

    @classmethod
    def animation_element_gen(cls):
        yield cls

    def _set_alternative_prop_overrides--- This code section failed: ---

 L. 709         0  LOAD_FAST                'self'
                2  LOAD_ATTR                interaction
                4  LOAD_CONST               None
                6  COMPARE_OP               is
                8  POP_JUMP_IF_TRUE     20  'to 20'
               10  LOAD_FAST                'self'
               12  LOAD_ATTR                interaction
               14  LOAD_GLOBAL              UNSET
               16  COMPARE_OP               is
               18  POP_JUMP_IF_FALSE    24  'to 24'
             20_0  COME_FROM             8  '8'

 L. 710        20  LOAD_CONST               None
               22  RETURN_VALUE     
             24_0  COME_FROM            18  '18'

 L. 712        24  LOAD_FAST                'self'
               26  LOAD_ATTR                interaction
               28  LOAD_ATTR                sim
               30  STORE_FAST               'sim'

 L. 713        32  LOAD_FAST                'sim'
               34  LOAD_CONST               None
               36  COMPARE_OP               is
               38  POP_JUMP_IF_FALSE    44  'to 44'

 L. 714        40  LOAD_CONST               None
               42  RETURN_VALUE     
             44_0  COME_FROM            38  '38'

 L. 716        44  SETUP_LOOP          278  'to 278'
               46  LOAD_FAST                'self'
               48  LOAD_ATTR                overrides
               50  LOAD_ATTR                props
               52  LOAD_METHOD              items
               54  CALL_METHOD_0         0  '0 positional arguments'
               56  GET_ITER         
             58_0  COME_FROM           274  '274'
             58_1  COME_FROM           258  '258'
             58_2  COME_FROM           188  '188'
             58_3  COME_FROM           140  '140'
             58_4  COME_FROM           114  '114'
             58_5  COME_FROM           100  '100'
             58_6  COME_FROM            76  '76'
               58  FOR_ITER            276  'to 276'
               60  UNPACK_SEQUENCE_2     2 
               62  STORE_FAST               'prop'
               64  STORE_FAST               'prop_override'

 L. 717        66  LOAD_FAST                'prop_override'
               68  LOAD_ATTR                alternative_prop_definitions
               70  STORE_FAST               'alt_prop_definitions'

 L. 718        72  LOAD_FAST                'alt_prop_definitions'
               74  POP_JUMP_IF_TRUE     78  'to 78'

 L. 719        76  CONTINUE             58  'to 58'
             78_0  COME_FROM            74  '74'

 L. 720        78  LOAD_FAST                'alt_prop_definitions'
               80  LOAD_ATTR                favorite_object_in_inventory
               82  POP_JUMP_IF_FALSE    96  'to 96'

 L. 721        84  LOAD_FAST                'alt_prop_definitions'
               86  LOAD_ATTR                favorite_object_in_inventory
               88  STORE_FAST               'favorite_data'

 L. 722        90  LOAD_CONST               True
               92  STORE_FAST               'inventory'
               94  JUMP_FORWARD        116  'to 116'
             96_0  COME_FROM            82  '82'

 L. 723        96  LOAD_FAST                'alt_prop_definitions'
               98  LOAD_ATTR                favorite_object_by_definition
              100  POP_JUMP_IF_FALSE_LOOP    58  'to 58'

 L. 724       102  LOAD_FAST                'alt_prop_definitions'
              104  LOAD_ATTR                favorite_object_by_definition
              106  STORE_FAST               'favorite_data'

 L. 725       108  LOAD_CONST               False
              110  STORE_FAST               'inventory'
              112  JUMP_FORWARD        116  'to 116'

 L. 727       114  CONTINUE             58  'to 58'
            116_0  COME_FROM           112  '112'
            116_1  COME_FROM            94  '94'

 L. 728       116  LOAD_FAST                'asm'
              118  LOAD_METHOD              get_actor_and_suffix
              120  LOAD_FAST                'favorite_data'
              122  LOAD_ATTR                actor_asm_name
              124  CALL_METHOD_1         1  '1 positional argument'
              126  UNPACK_SEQUENCE_2     2 
              128  STORE_FAST               'sim'
              130  STORE_FAST               '_'

 L. 729       132  LOAD_FAST                'sim'
              134  LOAD_CONST               None
              136  COMPARE_OP               is
              138  POP_JUMP_IF_FALSE   142  'to 142'

 L. 730       140  CONTINUE             58  'to 58'
            142_0  COME_FROM           138  '138'

 L. 731       142  LOAD_FAST                'inventory'
              144  POP_JUMP_IF_FALSE   164  'to 164'

 L. 732       146  LOAD_GLOBAL              favorites_utils
              148  LOAD_METHOD              get_favorite_in_sim_inventory
              150  LOAD_FAST                'sim'
              152  LOAD_FAST                'favorite_data'
              154  CALL_METHOD_2         2  '2 positional arguments'
              156  UNPACK_SEQUENCE_2     2 
              158  STORE_FAST               'favorite_def'
              160  STORE_FAST               'favorite_obj'
              162  JUMP_FORWARD        180  'to 180'
            164_0  COME_FROM           144  '144'

 L. 734       164  LOAD_GLOBAL              favorites_utils
              166  LOAD_METHOD              get_favorite_by_definition
              168  LOAD_FAST                'sim'
              170  LOAD_FAST                'favorite_data'
              172  CALL_METHOD_2         2  '2 positional arguments'
              174  STORE_FAST               'favorite_def'

 L. 735       176  LOAD_CONST               None
              178  STORE_FAST               'favorite_obj'
            180_0  COME_FROM           162  '162'

 L. 736       180  LOAD_FAST                'favorite_def'
              182  LOAD_CONST               None
              184  COMPARE_OP               is
              186  POP_JUMP_IF_FALSE   190  'to 190'

 L. 737       188  CONTINUE             58  'to 58'
            190_0  COME_FROM           186  '186'

 L. 739       190  LOAD_FAST                'favorite_def'
              192  LOAD_FAST                'self'
              194  LOAD_ATTR                overrides
              196  LOAD_ATTR                alternative_props
              198  LOAD_FAST                'prop'
              200  STORE_SUBSCR     

 L. 741       202  LOAD_FAST                'favorite_obj'
              204  POP_JUMP_IF_FALSE   246  'to 246'
              206  LOAD_FAST                'favorite_obj'
              208  LOAD_ATTR                favorite_prop_animation_overrides
              210  POP_JUMP_IF_FALSE   246  'to 246'

 L. 742       212  LOAD_FAST                'favorite_obj'
              214  LOAD_ATTR                favorite_prop_animation_overrides
              216  LOAD_METHOD              get_overrides_for_favorite_object
              218  LOAD_FAST                'prop'
              220  LOAD_FAST                'favorite_obj'
              222  CALL_METHOD_2         2  '2 positional arguments'
              224  STORE_FAST               'fav_prop_anim_overrides'

 L. 743       226  LOAD_FAST                'fav_prop_anim_overrides'
              228  LOAD_CONST               None
              230  COMPARE_OP               is-not
              232  POP_JUMP_IF_FALSE   246  'to 246'

 L. 744       234  LOAD_FAST                'fav_prop_anim_overrides'
              236  LOAD_FAST                'self'
              238  LOAD_ATTR                overrides
              240  CALL_FUNCTION_1       1  '1 positional argument'
              242  LOAD_FAST                'self'
              244  STORE_ATTR               overrides
            246_0  COME_FROM           232  '232'
            246_1  COME_FROM           210  '210'
            246_2  COME_FROM           204  '204'

 L. 753       246  LOAD_GLOBAL              favorites_utils
              248  LOAD_METHOD              get_animation_override_for_prop_def
              250  LOAD_FAST                'favorite_def'
              252  CALL_METHOD_1         1  '1 positional argument'
              254  STORE_FAST               'anim_overrides'

 L. 754       256  LOAD_FAST                'anim_overrides'
              258  POP_JUMP_IF_FALSE_LOOP    58  'to 58'

 L. 755       260  LOAD_FAST                'anim_overrides'
              262  LOAD_FAST                'self'
              264  LOAD_ATTR                overrides
              266  LOAD_CONST               ('overrides',)
              268  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              270  LOAD_FAST                'self'
              272  STORE_ATTR               overrides
              274  JUMP_LOOP            58  'to 58'
              276  POP_BLOCK        
            278_0  COME_FROM_LOOP       44  '44'

Parse error at or near `CONTINUE' instruction at offset 114

    def _run(self, timeline):
        global logged_missing_interaction_callstack
        if self.interaction is None:
            if not logged_missing_interaction_callstack:
                logger.callstack('Attempting to run an animation {} without a corresponding interaction.', self,
                  level=(sims4.log.LEVEL_ERROR))
                logged_missing_interaction_callstack = True
            return False
        if self.asm_key is None:
            return True
        asm = self.get_asm()
        if asm is None:
            return False
        self._set_alternative_prop_overrides(asm)
        if self.overrides.balloons:
            balloon_requests = TunableBalloon.get_balloon_requests(self.interaction, self.overrides)
        else:
            balloon_requests = None
        success = timeline.run_child(animate_states(asm,
 self.begin_states, self.end_states, overrides=self.overrides, 
         balloon_requests=balloon_requests, 
         repeat_begin_states=self.repeat, 
         interaction=self.interaction, **self.animate_kwargs))
        return success


def get_asm_name(asm_key):
    return asm_key


class AnimationElementSet(metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.ANIMATION)):
    INSTANCE_TUNABLES = {'_animation_and_overrides': TunableList(description='\n            The list of the animations which get played in sequence\n            ',
                                   tunable=TunableTuple(anim_element=AnimationElement.TunableReference(pack_safe=True),
                                   overrides=(TunableAnimationOverrides()),
                                   carry_requirements=TunableTuple(description='\n                    Specify whether the Sim must be carrying objects with\n                    specific animation properties in order to animate this\n                    particular element.\n                    ',
                                   params=TunableParameterMapping(description='\n                        A carried object must override and match these animation\n                        parameters in order for it to be valid.\n                        '),
                                   actor=Tunable(description='\n                        The carried object that fulfills the param requirements\n                        will be set as this actor on the selected element.\n                        ',
                                   tunable_type=str,
                                   default=None))))}

    def __new__(cls, interaction=None, setup_asm_additional=None, setup_asm_override=DEFAULT, overrides=None, sim=DEFAULT, **animate_kwargs):
        best_supported_posture = None
        best_anim_element_type = None
        best_carry_actor_and_object = None
        for animation_and_overrides in cls._animation_and_overrides:
            if overrides is not None:
                if callable(overrides):
                    overrides = overrides()
                overrides = animation_and_overrides.overrides(overrides=overrides)
            else:
                overrides = animation_and_overrides.overrides()
            anim_element_type = animation_and_overrides.anim_element
            if best_anim_element_type is None:
                best_anim_element_type = anim_element_type
            if interaction is None:
                logger.warn('Attempting to initiate AnimationElementSet {} without interaction, it will just construct the first AnimationElement {}.', cls.name, anim_element_type.name)
                break
            else:
                sim = sim if sim is not DEFAULT else interaction.sim
                carry_actor_name = animation_and_overrides.carry_requirements.actor
            if carry_actor_name:
                from carry.carry_utils import get_carried_objects_gen
                for _, _, carry_object in get_carried_objects_gen(sim):
                    carry_object_params = carry_object.get_anim_overrides(carry_actor_name).params
                    if all((carry_object_params[k] == v for k, v in animation_and_overrides.carry_requirements.params.items())):
                        break
                else:
                    continue
                postures = anim_element_type.get_supported_postures()
                sim_posture_state = sim.posture_state
                from postures import get_best_supported_posture
                surface_target = MATCH_ANY if sim_posture_state.surface_target is not None else MATCH_NONE
                provided_postures = sim_posture_state.body.get_provided_postures(surface_target=surface_target)
                best_element_supported_posture = get_best_supported_posture(provided_postures,
                  postures, (sim_posture_state.get_carry_state()), ignore_carry=False)
                if best_element_supported_posture is not None:
                    if not best_supported_posture is None:
                        if best_element_supported_posture < best_supported_posture:
                            pass
                    best_supported_posture = best_element_supported_posture
                    best_anim_element_type = anim_element_type
                    if carry_actor_name:
                        best_carry_actor_and_object = (
                         carry_actor_name, carry_object)
                    else:
                        best_carry_actor_and_object = None

        if best_carry_actor_and_object is not None:
            setup_asm_additional_override = setup_asm_additional

            def setup_asm_additional(asm):
                if not asm.set_actor((best_carry_actor_and_object[0]), (best_carry_actor_and_object[1]), actor_participant=(AnimationParticipant.CREATE_TARGET)):
                    return TestResult(False, 'Failed to set actor {} for actor name {} on asm {}'.format(best_carry_actor_and_object[0], best_carry_actor_and_object[1], asm))
                from carry.carry_utils import set_carry_track_param_if_needed
                set_carry_track_param_if_needed(asm, sim, best_carry_actor_and_object[0], best_carry_actor_and_object[1])
                if setup_asm_additional_override is not None:
                    return setup_asm_additional_override(asm)
                return True

        best_anim_element = best_anim_element_type(**, **animate_kwargs)
        return best_anim_element

    @classproperty
    def run_in_sequence(cls):
        return False

    @classmethod
    def animation_element_gen(cls):
        for animation_and_overrides in cls._animation_and_overrides:
            yield animation_and_overrides.anim_element

    @flexmethod
    def get_supported_postures(cls, inst):
        if inst is not None:
            if inst.interaction is not None:
                asm = inst.get_asm()
                if asm is not None:
                    return asm.get_supported_postures_for_actor(cls.actor_name)
        supported_postures = PostureManifest()
        for animation_and_overrides in cls._animation_and_overrides:
            supported_postures.update(animation_and_overrides.anim_element.get_supported_postures())

        return supported_postures

    @classproperty
    def name(cls):
        return cls.__name__