# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\balloon\balloon_utils.py
# Compiled at: 2021-02-23 12:43:00
# Size of source mod 2**32: 1715 bytes
from balloon.balloon_enums import BALLOON_TYPE_LOOKUP
from balloon.balloon_request import BalloonRequest
from balloon.tunable_balloon import TunableBalloon

def create_weighted_random_balloon_request(balloon_choices, actor, resolver, duration=None, delay=0, delay_randomization=0):
    balloon_icon = TunableBalloon.select_balloon_icon(balloon_choices, resolver)
    return create_balloon_request(balloon_icon, actor, resolver, duration, delay, delay_randomization)


def create_balloon_request(balloon_icon, actor, resolver, duration=None, delay=0, delay_randomization=0):
    if balloon_icon is None:
        return
    icon_info = balloon_icon.icon(resolver, balloon_target_override=None)
    if icon_info[0] is None:
        if icon_info[1] is None:
            return
    category_icon = None
    if balloon_icon.category_icon is not None:
        category_icon = balloon_icon.category_icon(resolver, balloon_target_override=None)
    balloon_type, priority = BALLOON_TYPE_LOOKUP[balloon_icon.balloon_type]
    balloon_overlay = balloon_icon.overlay
    balloon_duration = TunableBalloon.BALLOON_DURATION if duration is None else duration
    return BalloonRequest(actor, icon_info[0], icon_info[1], balloon_overlay, balloon_type, priority, balloon_duration, delay, delay_randomization, category_icon)