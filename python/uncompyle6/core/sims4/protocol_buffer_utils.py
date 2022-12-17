# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\protocol_buffer_utils.py
# Compiled at: 2014-10-02 20:10:36
# Size of source mod 2**32: 2550 bytes
from _net_proto2___python import TYPE_MESSAGE, LABEL_REPEATED

def has_field(proto, field_name):
    result = False
    try:
        result = proto.HasField(field_name)
    except ValueError:
        pass

    return result


def persist_fields_for_custom_option(message, custom_option):
    all_clear = True
    if message is None:
        return all_clear
    for name, value in message.DESCRIPTOR.fields_by_name.items():
        options = value.GetOptions()
        if options.Extensions[custom_option]:
            all_clear = False
        elif value.type == TYPE_MESSAGE:
            msg_recur = getattr(message, name)
            recur = (m for m in msg_recur) if value.label == LABEL_REPEATED else (msg_recur,)
            for _msg in recur:
                result = persist_fields_for_custom_option(_msg, custom_option)
                if result:
                    _msg.Clear()
                else:
                    all_clear = False

        else:
            message.ClearField(name)

    return all_clear