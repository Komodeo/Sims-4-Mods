# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reservation\reservation_result.py
# Compiled at: 2016-06-16 13:40:34
# Size of source mod 2**32: 1409 bytes


class ReservationResult:
    __slots__ = ('result', '_reason', '_format_args', 'result_obj')
    TRUE = None

    def __init__(self, result, *args, result_obj=None):
        self.result = result
        if args:
            self._reason, self._format_args = args[0], args[1:]
        else:
            self._reason, self._format_args = (None, ())
        self.result_obj = result_obj

    def __str__(self):
        if self.reason:
            return self.reason
        return str(self.result)

    def __repr__(self):
        if self.reason:
            return '<ReservationResult: {0} ({1})>'.format(bool(self.result), self.reason)
        return '<ReservationResult: {0}>'.format(bool(self.result))

    def __bool__(self):
        if self.result:
            return True
        return False

    @property
    def reason(self):
        if self._format_args:
            if self._reason:
                self._reason = (self._reason.format)(*self._format_args)
                self._format_args = ()
        return self._reason


ReservationResult.TRUE = ReservationResult(True)