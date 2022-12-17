# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\omega.py
# Compiled at: 2012-10-02 16:05:18
# Size of source mod 2**32: 729 bytes
try:
    import _omega
except ImportError:

    class _omega:

        @staticmethod
        def send(session_id, msg_id, data):
            return True


_send = _omega.send

def send(session_id, msg_id, data):
    if not _send(session_id, msg_id, data):
        raise KeyError('Failed to find ZoneSessionContext for [ZoneSessionId: 0x{:016x}]'.format(session_id))