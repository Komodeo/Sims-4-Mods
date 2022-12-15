# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\tuning\module_tuning.py
# Compiled at: 2014-02-21 11:55:42
# Size of source mod 2**32: 2233 bytes
import sys, xml.sax.handler, sims4.resources, sims4.tuning.instance_manager, sims4.tuning.serialization

class _EarlyExit(Exception):
    pass


class _ParseHandler(xml.sax.handler.ContentHandler):

    def __init__(self):
        self.module_name = None

    def startElement(self, name, attrs):
        if name == 'TuningRoot':
            return
        if name == sims4.tuning.tunable.LoadingTags.Instance:
            raise RuntimeError('Instance tuning can not be reloaded as module tuning')
        else:
            if name == sims4.tuning.tunable.LoadingTags.Module:
                self.module_name = attrs[sims4.tuning.tunable.LoadingAttributes.Name]
                raise _EarlyExit
        raise RuntimeError('All tuning must start with either instance or module tuning')


def get_module_name_from_tuning(key):
    loader = sims4.resources.ResourceLoader(key)
    tuning_file = loader.load()
    parse_handler = _ParseHandler()
    try:
        xml.sax.parse(tuning_file, parse_handler)
    except _EarlyExit:
        return parse_handler.module_name


class ModuleTuningManager(sims4.tuning.instance_manager.InstanceManager):

    def reload_by_key(self, key):
        raise RuntimeError('[manus] Reloading tuning is not supported for optimized python builds.')
        module_name = get_module_name_from_tuning(key)
        module = sys.modules[module_name]
        sims4.tuning.serialization.load_module_tuning(module, key)