# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gallery_tuning.py
# Compiled at: 2019-09-03 08:10:04
# Size of source mod 2**32: 1108 bytes
from sims4.tuning.tunable import TunableEnumEntry
import enum, tag

class GalleryGameplayTuning:
    EXPORT_SAVE_DATA_TO_GALLERY_TAG = TunableEnumEntry(description='\n        Reference to the tag used for marking objects that require their \n        save data to be stored in the gallery.\n        i.e. Craftables, books, etc.\n        ',
      tunable_type=(tag.Tag),
      default=(tag.Tag.INVALID))


class ContentSource(enum.Int, export=False):
    DEFAULT = 0
    LIBRARY = 1
    GALLERY = 2
    HOUSEHOLD_INVENTORY_PROXY = 3