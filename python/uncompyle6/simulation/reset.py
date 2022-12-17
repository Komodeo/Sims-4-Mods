# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reset.py
# Compiled at: 2014-07-18 15:00:54
# Size of source mod 2**32: 3081 bytes
import elements, services, sims4.log
logger = sims4.log.Logger('Reset')

class ResettableObjectMixin:

    def register_reset_element(self, element):
        pass

    def unregister_reset_element(self, element):
        pass

    def on_reset_element_hard_stop(self):
        pass


class ResettableElement(elements.RunChildElement):
    __slots__ = ('obj', '_registered')

    @classmethod
    def shortname(cls):
        return 'Resettable'

    def __init__(self, child_element, obj):
        super().__init__(child_element)
        self.obj = obj
        self._registered = False

    def set_parent_handle(self, handle):
        logger.error('ResettableElements must be at the root of the chain {}', self)
        super().set_parent_handle(handle)

    def on_scheduled(self, timeline):
        self.register()

    def _run(self, timeline):
        return super()._run(timeline)

    def _resume(self, timeline, child_result):
        self.unregister()
        return child_result

    def _hard_stop(self):
        super()._hard_stop()
        if self._registered:
            self.obj.on_reset_element_hard_stop()
        else:
            services.get_reset_and_delete_service().start_processing()

    def _teardown(self):
        self.unregister()

    def register(self):
        if not self._registered:
            self._registered = True
            self.obj.register_reset_element(self)

    def unregister(self):
        if self._registered:
            self._registered = False
            self.obj.unregister_reset_element(self)
            self.obj = None

    def __repr__(self):
        return '<Resettable obj:{}, child:{}>'.format(self.obj, self.child_element)

    def tracing_repr(self):
        return '<Resettable obj:{}, child:{}>'.format(self.obj, self.child_element.tracing_repr())