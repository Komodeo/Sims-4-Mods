# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\spells\spells.py
# Compiled at: 2019-06-04 10:47:18
# Size of source mod 2**32: 2581 bytes
import services
from interactions.item_consume import ItemCost
from interactions.utils.display_mixin import get_display_mixin
from objects.mixins import SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin
from sims4.localization import TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import OptionalTunable, TunableSet, TunableEnumWithFilter
from sims4.tuning.tunable_base import GroupNames, EnumBinaryExportType, ExportModes
from sims4.utils import classproperty
from tag import Tag
_SpellDisplayMixin = get_display_mixin(has_description=True, has_icon=True, has_tooltip=True, enabled_by_default=True)

class Spell(_SpellDisplayMixin, SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SPELL)):
    INSTANCE_TUNABLES = {'locked_description':OptionalTunable(description='\n            Description used in the spellbook if spell is not yet unlocked.\n            If unset, uses display data description.\n            ',
       tunable=TunableLocalizedString(),
       tuning_group=GroupNames.UI), 
     'ingredients':ItemCost.TunableFactory(description='\n            Ingredients needed to cast the spell.  Interactions which specify this spell as the item cost will consume \n            the ingredients specified here.\n            '), 
     'tags':TunableSet(description='\n            Tags for the spell.\n            ',
       tunable=TunableEnumWithFilter(tunable_type=Tag,
       filter_prefixes=[
      'spell'],
       default=(Tag.INVALID),
       invalid_enums=(
      Tag.INVALID,),
       pack_safe=True,
       binary_type=(EnumBinaryExportType.EnumUint32)),
       export_modes=ExportModes.All,
       tuning_group=GroupNames.TAG)}

    @classmethod
    def get_display_name(cls, *_):
        return cls.display_name

    @classproperty
    def unlock_as_new(cls):
        return True

    @classproperty
    def tuning_tags(cls):
        return cls.tags