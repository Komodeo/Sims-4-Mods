# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\video_commands.py
# Compiled at: 2013-10-10 18:01:17
# Size of source mod 2**32: 2961 bytes
from objects.components import types
import objects, services, sims4.commands

@sims4.commands.Command('video.object_info')
def get_video_object_info(obj_id: int, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('Object ID {} not present in the object manager.'.format(obj_id), _connection)
    if obj is not None:
        sims4.commands.output('Object {} ({})'.format(obj_id, obj.__class__.__name__), _connection)
        v = obj.get_component(types.VIDEO_COMPONENT)
        if v is not None:
            sims4.commands.output('  ' + repr(v), _connection)
        else:
            sims4.commands.output('  Object does not have video playback capabilities.', _connection)


@sims4.commands.Command('video.set_clips')
def set_video_clips(obj_id: int, *clip_names, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('Object ID {} not present in the object manager.'.format(obj_id), _connection)
    if obj is not None:
        sims4.commands.output('Object {} ({})'.format(obj_id, obj.__class__.__name__), _connection)
        v = obj.get_component(types.VIDEO_COMPONENT)
        if v is not None:
            v.set_video_clips(clip_names, False)
            sims4.commands.output('  Added {} clip(s).'.format(len(clip_names)), _connection)
        else:
            sims4.commands.output('  Object does not have video playback capabilities.', _connection)


@sims4.commands.Command('video.add_clips')
def add_video_clips(obj_id: int, *clip_names, _connection=None):
    manager = services.object_manager()
    obj = None
    if obj_id in manager:
        obj = manager.get(obj_id)
    else:
        sims4.commands.output('Object ID {} not present in the object manager.'.format(obj_id), _connection)
    if obj is not None:
        sims4.commands.output('Object {} ({})'.format(obj_id, obj.__class__.__name__), _connection)
        v = obj.get_component(types.VIDEO_COMPONENT)
        if v is not None:
            v.add_video_clips(clip_names, False)
            sims4.commands.output('  Added {} clip(s).'.format(len(clip_names)), _connection)
        else:
            sims4.commands.output('  Object does not have video playback capabilities.', _connection)