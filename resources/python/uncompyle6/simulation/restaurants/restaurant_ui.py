# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\restaurants\restaurant_ui.py
# Compiled at: 2018-04-18 14:08:22
# Size of source mod 2**32: 384 bytes
from distributor.ops import Op, protocol_constants

class ShowMenu(Op):

    def __init__(self, show_menu_message):
        super().__init__()
        self.op = show_menu_message

    def write(self, msg):
        self.serialize_op(msg, self.op, protocol_constants.RESTAURANT_SHOW_MENU)