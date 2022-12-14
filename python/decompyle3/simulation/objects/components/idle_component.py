# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\idle_component.py
# Compiled at: 2020-07-22 13:11:31
# Size of source mod 2**32: 13977 bytes
import animation.asm, caches, distributor.ops, element_utils, services, sims4
from animation import AnimationContext
from animation.animation_utils import flush_all_animations
from collections import defaultdict
from distributor.system import Distributor
from element_utils import build_critical_section_with_finally, build_element
from objects.components import Component, types, componentmethod_with_fallback, componentmethod
from sims4.tuning.tunable import HasTunableFactory, TunableMapping, TunableReference, OptionalTunable, Tunable, AutoFactoryInit
from sims4.callback_utils import CallableList
from singletons import DEFAULT
from weakref import WeakKeyDictionary
logger = sims4.log.Logger('IdleComponent', default_owner='rmccord')

class IdleComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.IDLE_COMPONENT):
    FACTORY_TUNABLES = {'idle_animation_map':TunableMapping(description='\n            The animations that the attached object can play.\n            ',
       key_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
       class_restrictions='ObjectStateValue'),
       value_type=TunableReference(description='\n                The animation to play when the object is in the specified state.\n                If you want the object to stop playing idles, you must tune an\n                animation element corresponding to an ASM state that requests a\n                stop on the object.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ANIMATION)),
       class_restrictions='ObjectAnimationElement')), 
     'client_suppressed_state':OptionalTunable(description='\n            If enabled, set this object state whenever a client suppression is \n            triggered.\n            For example, when the retail system replaces an object when sold\n            all of its distributables are suppressed so we should stop all\n            animation, vfx, etc. \n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
       class_restrictions='ObjectStateValue')), 
     'parent_name':OptionalTunable(description='\n            If enabled, when the object is parented, its parent will be set as\n            this actor in whatever ASM is playing.\n            ',
       tunable=Tunable(tunable_type=str,
       default=None))}

    def __init__(self, owner, *args, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self._asm_registry = WeakKeyDictionary()
        self._animation_context = AnimationContext()
        self._animation_context.add_ref(self)
        self._idle_animation_element = None
        self._current_idle_state_value = None
        self._component_suppressed = False
        self._wakeable_element = None
        self._scheduled_after_callbacks = defaultdict(CallableList)

    def get_asm(self, asm_key, actor_name, setup_asm_func=None, use_cache=True, animation_context=DEFAULT, cache_key=DEFAULT, **kwargs):
        if animation_context is DEFAULT:
            animation_context = self._animation_context
        if use_cache:
            asm_dict = self._asm_registry.setdefault(animation_context, {})
            asm = None
            if asm_key in asm_dict:
                asm = asm_dict[asm_key]
                if asm.current_state == 'exit':
                    asm = None
            if asm is None:
                asm = animation.asm.create_asm(asm_key, context=animation_context)
            asm_dict[asm_key] = asm
        else:
            asm = animation.asm.create_asm(asm_key, context=animation_context)
        asm.set_actor(actor_name, self.owner)
        if self.parent_name is not None:
            parent = self.owner.parent
            if parent is not None:
                asm.add_potentially_virtual_actor(actor_name, self.owner, self.parent_name, parent)
        if setup_asm_func is not None:
            result = setup_asm_func(asm)
            if not result:
                logger.warn("Couldn't setup idle asm {} for {}. {}", asm, self.owner, result)
                return
            return asm

    @componentmethod
    def get_idle_animation_context(self):
        return self._animation_context

    def add_scheduled_after_callback(self, state, func):
        self._scheduled_after_callbacks[state].register(func)

    def remove_scheduled_after_callback(self, state, func):
        self._scheduled_after_callbacks[state].unregister(func)

    def _refresh_active_idle(self):
        if self._current_idle_state_value is not None:
            if self._idle_animation_element is not None:
                self._trigger_idle_animation(self._current_idle_state_value.state, self._current_idle_state_value, False)

    def _stop_wakeable(self):
        if self._wakeable_element is not None:
            self._wakeable_element.trigger_soft_stop()
            self._wakeable_element = None

    def on_removed_from_inventory(self):
        self._refresh_active_idle()

    def on_state_changed(self, state, old_value, new_value, from_init):
        if not self._trigger_idle_animation(state, new_value, from_init):
            if new_value.anim_overrides is not None:
                if old_value != new_value:
                    self._refresh_active_idle()

    def _trigger_idle_animation(self, state, new_value, from_init):
        if self._component_suppressed:
            return
        if new_value in self.idle_animation_map:
            current_zone = services.current_zone()
            if current_zone is None or from_init and current_zone.is_zone_loading:
                return False
            new_animation = self.idle_animation_map[new_value]
            self._stop_animation_element()
            self._current_idle_state_value = new_value
            if new_animation is not None:
                sequence = ()
                if new_animation.repeat:
                    self._wakeable_element = element_utils.soft_sleep_forever()
                    sequence = self._wakeable_element
                animation_element = new_animation((self.owner), sequence=sequence)
                core_idle_animation_element = build_element((animation_element,
                 flush_all_animations))
                self._idle_animation_element = build_critical_section_with_finally(core_idle_animation_element, lambda _: self._scheduled_after_callbacks[new_value]()
)
                services.time_service().sim_timeline.schedule(self._idle_animation_element)
                return True
        return False

    @componentmethod_with_fallback(lambda *_, **__: None
)
    def on_client_suppressor_added(self):
        if self.client_suppressed_state is not None:
            self.owner.set_state(self.client_suppressed_state.state, self.client_suppressed_state)
        self._component_suppressed = True

    @componentmethod_with_fallback(lambda *_, **__: None
)
    def on_client_suppressor_removed(self, supressors_active):
        if supressors_active:
            return
        self._component_suppressed = False
        if self.client_suppressed_state is not None:
            if self._current_idle_state_value is not None:
                self.owner.set_state(self._current_idle_state_value.state, self._current_idle_state_value)

    def component_reset(self, _):
        self._stop_animation_element(hard_stop=True)

    def post_component_reset(self):
        self.reapply_idle_state()

    def reapply_idle_state(self):
        for current_value in self.idle_animation_map:
            if self.owner.state_value_active(current_value):
                self._trigger_idle_animation(current_value.state, current_value, False)
                return

    def _stop_animation_element(self, hard_stop=False):
        self._stop_wakeable()
        if self._idle_animation_element is not None:
            if hard_stop:
                self._idle_animation_element.trigger_hard_stop()
            else:
                self._idle_animation_element.trigger_soft_stop()
            self._idle_animation_element = None
        self._current_idle_state_value = None

    def on_remove_from_client(self, *_, **__):
        zone = services.current_zone()
        if not zone is not None or zone.is_in_build_buy:
            try:
                reset_op = distributor.ops.ResetObject(self.owner.id)
                dist = Distributor.instance()
                dist.add_op(self.owner, reset_op)
            except:
                logger.exception('Exception thrown sending reset op for {}', self)

    def on_remove(self, *_, **__):
        if self._animation_context is not None:
            self._animation_context.release_ref(self)
            self._animation_context = None
        self._stop_animation_element(hard_stop=True)