# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\ui_tuning.py
# Compiled at: 2022-10-05 11:14:58
# Size of source mod 2**32: 50524 bytes
from sims4.common import Pack
from sims4.localization import TunableLocalizedString
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, Tunable, TunableList, TunableTuple, TunableReference, TunableResourceKey, TunableRange, TunableVariant, TunableMTXBundle, OptionalTunable, TunableRegionDescription, TunableLotDescription
from sims4.tuning.tunable_base import ExportModes
from tag import TunableTag
from world.region import RegionType
import enum, sims4.resources
from interactions.utils.tunable_icon import TunableIcon
from objects.collection_manager import CollectionIdentifier
import services

class PackTypes(enum.Int):
    BASE = 0
    EXPANSION_PACK = 1
    GAME_PACK = 2
    STUFF_PACK = 3
    FREE_PACK = 4


class PackSubTypes(enum.Int):
    FULL = 0
    KIT = 1


class Platform(enum.Int):
    DESKTOP = 0
    CONSOLE = 1
    PS4 = 2
    XB1 = 3


class InputMethod(enum.Int):
    ANY = 0
    KBM = 1
    CONTROLLER = 2


class BrandedLogoBackground(enum.Int):
    LIGHT = 0
    DARK = 1


class BrandedStyle(enum.Int):
    TOP_WIDE = 0
    TOP_LEFT_ICON = 1


class MultiPickerStyle(enum.Int):
    DEFAULT = 0
    PHOTOPAIR_ORGANIZE_DELETE = 1
    PHOTO_PAIR_SELECT = 2


class MultiPickerFilterType(enum.Int):
    NO_FILTER = 0
    RELBIT_FILTER = 1
    TOPIC_FILTER = 2


class MapOverlayEnum(DynamicEnum, export_modes=(ExportModes.ClientBinary, ExportModes.ServerXML)):
    NONE = 0


class PromoCycleImagesTuning(TunableTuple):

    def __init__(self, description='', **kwargs):
        (super().__init__)(image_large=TunableResourceKey(description='\n                The large version of the screenshot displayed in the Pack\n                Preview Panel.\n                ',
  resource_types=(sims4.resources.CompoundTypes.IMAGE)), 
         image_small=TunableResourceKey(description='\n                The small version of the screenshot displayed in the Pack \n                Detail Panel.\n                ',
  resource_types=(sims4.resources.CompoundTypes.IMAGE)), 
         title=TunableLocalizedString(description='\n                The title displayed over the screenshot in both the Pack\n                Detail Panel and Pack Preview Panel.\n                '), 
         description=description, **kwargs)


class TunableUiValue(TunableVariant):

    def __init__(self, description='Represents a value that can be provided to the UI.', **kwargs):
        (super().__init__)(raw_int=Tunable(description='\n                Provide an integer value.\n                ',
  tunable_type=int,
  default=0), 
         raw_float=Tunable(description='\n                Provide a floating-point value.\n                ',
  tunable_type=float,
  default=0), 
         raw_string=Tunable(description='\n                Provide a non-localized string.\n                ',
  tunable_type=str,
  default=''), 
         raw_bool=Tunable(description='\n                Provide a boolean value.\n                ',
  tunable_type=bool,
  default=False), 
         resource_key=TunableResourceKey(description='\n                Provide a resource key.\n                This is provided to the UI in the same format as\n                the ResourceKey AS3 class.\n                '), 
         locked_args={'null': None}, 
         default='null', 
         description=description, **kwargs)


class TunableUiMessage(TunableTuple):

    def __init__(self, description='Represents a message to be sent to the UI.', **kwargs):
        (super().__init__)(message_name=Tunable(description="\n                Name of the UI message.\n                e.g. 'ShowEscapeMenu'\n                ",
  tunable_type=str,
  default=''), 
         parameters=TunableMapping(description='\n                Any parameters to send with the message.\n                Consult your UI engineering partner to determine what\n                parameters, if any, should be specified.\n                ',
  key_type=str,
  value_type=TunableUiValue(description='\n                    Value to associate with this parameter.\n                    '),
  tuple_name='TunableUiMessageParameter'), 
         description=description, **kwargs)


class UiTuning:
    DLC_TRIALS_EXPIRATION_DIALOG_DURATION_IN_DAYS = TunableRange(description="\n        Duration in number of days after trial expiration in which it's still\n        valid to show the Trial Expired dialog to the player.\n\n        This value also doubles as the number of days after conversion in which\n        it's still valid to show the Welcome to Pack dialog.\n\n        After this period of time, these dialogs will not be able to show when\n        the player returns to the game.\n        ",
      tunable_type=int,
      default=14,
      minimum=1,
      export_modes=(
     ExportModes.ClientBinary,))
    LOADING_SCREEN_STRINGS = TunableMapping(description='\n        Mapping from the Pack to its associated loading strings.\n        ',
      key_type=TunableEnumEntry(description='\n            The pack containing the strings.\n            ',
      tunable_type=Pack,
      default=(Pack.BASE_GAME)),
      value_type=TunableList(description='\n            The list of loading screen strings which belongs to the pack.\n            We always display the strings from base game AND from the latest\n            pack which the player is entitled to and has installed. \n            ',
      tunable=(TunableLocalizedString())),
      export_modes=(
     ExportModes.ClientBinary,),
      tuple_name='LoadingScreenStringsTuple')
    GO_HOME_INTERACTION = TunableReference(description='\n        The interaction to push a Sim to go home.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      export_modes=(
     ExportModes.ClientBinary,))
    COME_NEAR_ACTIVE_SIM = TunableReference(description='\n        An affordance to push on a Sim so they come near the active Sim.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))
    BRING_HERE_INTERACTION = TunableReference(description='\n        An affordance to push on household members to summon them to the\n        current lot if they are not instanced.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))
    NEW_CONTENT_ALERT_TUNING = TunableMapping(description='\n        Mapping from Pack to its associated new content alert tuning\n        ',
      key_type=TunableEnumEntry(description='\n            The pack containing the new content tuning. NOTE: this should never\n            be tuned to BASE_GAME. That would trigger for all users.\n            ',
      tunable_type=Pack,
      default=(Pack.BASE_GAME)),
      value_type=TunableTuple(description='\n            Each pack will have a set of tuning of images and text to display\n            to inform the user what new features have been introduced in the \n            pack.\n            ',
      export_class_name='TunablePackContentTuple',
      title=TunableLocalizedString(description='\n                The title to be displayed at the top of the New Content Alert\n                UI for this pack.\n                '),
      cycle_images=TunableList(description='\n                A list of images (screenshots) that the UI cycles through to\n                show off some of the new features.\n                ',
      tunable=TunableResourceKey(resource_types=(sims4.resources.CompoundTypes.IMAGE))),
      feature_list=TunableList(description='\n                A list of tuples that describe each new feature in the New\n                Content Alert UI. NOTE: This should NEVER have more than 4\n                elements in it.\n                ',
      maxlength=4,
      tunable=TunableTuple(description='\n                    A tuple that contains title text, description, an icon,\n                    and a reference to the matching lesson for this new \n                    feature.\n                    ',
      export_class_name='TunableFeatureTuple',
      title_text=TunableLocalizedString(description='\n                        A title to be displayed in bold for the feature.\n                        '),
      description_text=TunableLocalizedString(description='\n                        A short description of the new feature.\n                        '),
      icon=TunableResourceKey(description='\n                        An icon that represents the feature.\n                        ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE)),
      lesson=TunableReference(description='\n                        A reference to the lesson that the user can go look at\n                        for this new feature.\n                        ',
      manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL)),
      allow_none=True,
      pack_safe=True)))),
      export_modes=(
     ExportModes.ClientBinary,),
      tuple_name='NewContentAlertTuple')
    REGION_TYPE_HEADING_TUNING = TunableMapping(description='\n        Mapping from region type to Heading information for world select\n        screen\n        ',
      key_type=TunableEnumEntry(description='\n            The regiontype that should get this heading data\n            ',
      tunable_type=RegionType,
      default=(RegionType.REGIONTYPE_RESIDENTIAL)),
      value_type=TunableTuple(description='\n            Each region will have a set of tuning of icons and text to display\n            in the heading.\n            ',
      export_class_name='TunableRegionHeadingTuple',
      heading=TunableLocalizedString(description='\n                The text to be displayed at the top.\n                '),
      vacation_subheading=OptionalTunable(description='\n                The sub heading to be displayed below the heading when\n                selecting a lot for a vacation.\n                ',
      tunable=(TunableLocalizedString())),
      icon=TunableIcon(description='\n                Icon to be displayed next to the heading.\n                ')),
      export_modes=(
     ExportModes.ClientBinary,),
      tuple_name='RegionTypeHeadingTuple')
    PACK_SPECIFIC_DATA = TunableMapping(description='\n        Mapping from a Pack to its associated data.  This includes pack icons,\n        filter strings, and the credits file.\n        ',
      key_name='packId',
      key_type=TunableEnumEntry(description='\n            The pack id for the associated data.\n            ',
      tunable_type=Pack,
      default=(Pack.BASE_GAME)),
      value_name='packData',
      value_type=TunableTuple(description='\n            Each pack will have a set icons and can have an optional filter \n            string for use in Build/CAS and an optional Credits Title\n            ',
      export_class_name='TunablePackDataTuple',
      credits_title=TunableLocalizedString(description='\n                The title used in the credits dropdown to select this packs credits.\n                If set, there must be a creditsxml file for this pack\n                in Assets/InGame/UI/Flash/data/\n                ',
      allow_none=True),
      filter_name=TunableLocalizedString(description='\n                The name to used to describe the pack in CAS and BuildBuy filters.\n                If set, this pack will appear in the filter list.\n                ',
      allow_none=True),
      pack_type=TunableEnumEntry(description='\n                Which type of pack is this.\n                ',
      tunable_type=PackTypes,
      default=(PackTypes.BASE)),
      pack_sub_type=TunableEnumEntry(description='\n                Which sub type of pack is this.\n                ',
      tunable_type=PackSubTypes,
      default=(PackSubTypes.FULL)),
      icon_32=TunableResourceKey(description='\n                Pack icon. 32x32.\n                ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE)),
      icon_64=TunableResourceKey(description='\n                Pack icon. 64x64.\n                ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE)),
      icon_128=TunableResourceKey(description='\n                Pack icon. 128x128.\n                ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE)),
      icon_owned=TunableIcon(description='\n                Pack icon that is displayed in the main menu\n                pack display when the player owns that pack.\n                ',
      allow_none=True),
      icon_unowned=TunableIcon(description='\n                Pack icon that is displayed in the main menu\n                pack display when the player does not own that pack.\n                ',
      allow_none=True),
      webstore_id=Tunable(description='\n                web store pack specific url identifier\n                ',
      tunable_type=str,
      default=None),
      region_list=TunableList(description='\n                A list of tuples that describe each new region in the pack.\n                ',
      tunable=TunableTuple(description='\n                    A tuple that contains metadata for a world select region.\n                    ',
      export_class_name='TunablePackRegionTuple',
      region_resource=TunableRegionDescription(description='\n                            Reference to the region description catalog resource associated with this region\n                        ',
      pack_safe=True),
      is_player_facing=Tunable(description='\n                            Whether to display this region in world select when the user does not own the associated pack\n                        ',
      tunable_type=bool,
      default=False),
      region_name=TunableLocalizedString(description='\n                        Localized name of region.\n                        ',
      allow_none=True),
      region_description=TunableLocalizedString(description='\n                        Localized description of region.\n                        ',
      allow_none=True),
      region_tooltip_override=TunableLocalizedString(description='\n                        Tooltip on the world select. If none is set, will use region_description.\n                        ',
      allow_none=True),
      overlay_layer=TunableResourceKey(description='\n                        Hero image displayed on mouse over of region in\n                        world selection UI.\n                        ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      allow_none=True),
      parallax_layers=TunableList(description='\n                        Images used for scrolling parallax layers for region\n                        in world selection UI. Max number of images = 5.\n                        ',
      maxlength=5,
      tunable=TunableResourceKey(resource_types=(sims4.resources.CompoundTypes.IMAGE))),
      tourist_highlights=TunableList(description='\n                        Icon, heading, and description used to list points of\n                        interest when selecting world for vacations.\n                        ',
      tunable=TunableTuple(description='\n                            Each highlight will have a set of tuning of icons,\n                            heading, and description.\n                            ',
      export_class_name='TunableTouristHighlightTuple',
      heading=TunableLocalizedString(description='\n                                The heading text.\n                                '),
      description_text=TunableLocalizedString(description='\n                                The description.\n                                '),
      icon=TunableIcon(description='\n                                Icon to be displayed .\n                                '))),
      is_destination_region=Tunable(description='\n                        Whether this region is a destination world.\n                        ',
      tunable_type=bool,
      default=False),
      disable_view_lot_types=Tunable(description='\n                        When tuned, this disables the view lot types button in the World Info Description panel.    \n                        ',
      tunable_type=bool,
      default=False),
      travel_only_lots=TunableMapping(description='\n                        Any lots tuned here are unselectable outside of gameplay travel/vacation flows,\n                        with text describing why this is the case.\n                        ',
      key_name='lot',
      key_type=TunableLotDescription(description='\n                            The lot that is unselectable in manage worlds.\n                            ',
      pack_safe=True),
      value_name='unselectable_text',
      value_type=TunableLocalizedString(description='\n                            Localized text describing why the lot is unselectable.\n                            '),
      tuple_name='ManageWorldsUnselectableLotsTuple'),
      region_type=TunableEnumEntry(description='\n                        The region type for this region.  Keep in sync \n                        with gameplay tuning at region->region type\n                        ',
      tunable_type=RegionType,
      default=(RegionType.REGIONTYPE_RESIDENTIAL)),
      is_summit_weather_enabled=Tunable(description='\n                        Whether this region has summit (EP10) weather enabled.\n                        ',
      tunable_type=bool,
      default=False))),
      promo_cycle_images=TunableList(description='\n                A list of promo screenshots and titles to display in the \n                Pack Detail panel.\n                ',
      tunable=PromoCycleImagesTuning(description='\n                    Screenshots and label displayed in the Pack Detail Panel\n                    and Pack Preview Panel.\n                    ')),
      short_description=TunableLocalizedString(description='\n                Short description of the pack meant to be displayed in \n                a tooltip.\n                ',
      allow_none=True),
      community_creator_name=TunableLocalizedString(description='\n               The name of the community creator who helped create this pack,\n               to be displayed in the Pack Detail Panel\n                ',
      allow_none=True),
      dlc_trial_title=TunableLocalizedString(description='\n                The title to display in the "Trial Goals" dialog in manage worlds\n                when the player runs a trial of this pack.\n                ',
      allow_none=True),
      dlc_trial_pack_goals_description=TunableLocalizedString(description='\n                A description of the goals associated with this pack. This\n                is displayed in the "Trial Goals" dialog in manage worlds when\n                the player runs a trial of this pack.\n                ',
      allow_none=True),
      dlc_trial_image=TunableIcon(description='\n                Image displayed in the "Trial Goals" dialog in manage worlds\n                when the player runs a trial of this pack.\n                ',
      allow_none=True),
      dlc_trial_region=OptionalTunable(description='\n                Reference to the region description catalog resource that will\n                be shown in the "Trial Goals" dialog in manage worlds when the\n                player runs a trial of this pack.\n                ',
      tunable=TunableRegionDescription(pack_safe=True))),
      export_modes=(
     ExportModes.ClientBinary,),
      tuple_name='PackSpecificDataTuple')
    BUNDLE_SPECIFIC_DATA = TunableMapping(description='\n        Mapping from an MTX Bundle to its associated data. This is for bundles that\n        should appear in the ui, but are not packs. This includes main menu icons,\n        description, and the action associated with that bundle.\n        ',
      key_type=TunableMTXBundle(description='\n            The MTX bundle id for the associated data.\n            ',
      pack_safe=True),
      value_type=TunableTuple(description='\n            Each bundle has icons and a description, as well as an\n            data for the action performed when the bundle is interacted \n            with either the PromotionDialog or the PackDisplayPanel.\n            ',
      bundle_name=TunableLocalizedString(description='\n                Name used in pack detail panel and main menu. If empty,\n                we fall back to using the MTX product name.\n                ',
      allow_none=True),
      icon_owned=TunableIcon(description='\n                Bundle icon that is displayed in the main menu\n                pack display when the player is entitled to that bundle.\n                '),
      icon_unowned=TunableIcon(description='\n                Bundle icon that is displayed in the main menu\n                pack display when the player is not entitled to that bundle.\n                '),
      short_description=TunableLocalizedString(description='\n                Short description of the bundle meant to be displayed in \n                a tooltip.\n                '),
      action=TunableVariant(description='\n                The action that should be performed when this bundle is interacted with\n                in either the PromotionDialog or the PackDisplayPanel.\n                ',
      url=Tunable(description='\n                    External url to open from PackDisplayPanel.\n                    ',
      tunable_type=str,
      default=None),
      promo_data=TunableTuple(description='\n                    Data that populates PromotionDialog.\n                    ',
      title=TunableLocalizedString(description='\n                        Title of the promotion.\n                        '),
      text=TunableLocalizedString(description='\n                        Text describing the promotion.\n                        '),
      image=TunableIcon(description='\n                        Image displayed in the promotion dialog.\n                        '),
      legal_text=TunableLocalizedString(description='\n                        Legal text required for this promotion.\n                        ',
      allow_none=True),
      export_class_name='TunablePromoDataTuple'),
      default='url'),
      export_class_name='TunableBundleDataTuple'),
      export_modes=(
     ExportModes.ClientBinary,),
      tuple_name='BundleSpecificDataTuple')
    PACK_RELEASE_ORDER = TunableList(description='\n        List of Pack Ids in release order.\n        ',
      tunable=TunableEnumEntry(description='\n            A pack Id.\n            ',
      tunable_type=Pack,
      default=(Pack.BASE_GAME)),
      export_modes=(
     ExportModes.ClientBinary,))
    CHALLENGE_DATA = TunableList(description='\n        List of challenge event data for engagement challenge notification UI.\n        ',
      tunable=TunableTuple(description='\n            Data for each engagement challenge event.\n            ',
      export_class_name='TunableChallengeNotificationTuple',
      challenge_list=TunableList(description='\n                A list of tuples that describe each challenge.\n                ',
      tunable=TunableTuple(description='\n                    A tuple that contains data for a challenge.\n                    ',
      export_class_name='TunableChallengeDataTuple',
      challenge_description=TunableLocalizedString(description='\n                        The description of the challenge.\n                        ',
      allow_none=True),
      challenge_name=TunableLocalizedString(description='\n                        The name of the challenge.\n                        ',
      allow_none=True),
      image=TunableResourceKey(description='\n                        The main image displayed for challenge info.\n                        ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE)),
      info_link=Tunable(description='\n                        The url link to page for more info on a challenge.\n                        ',
      tunable_type=str,
      default='',
      allow_empty=True),
      event_display=TunableTuple(description='\n                        Display data for a challenge event.\n                        ',
      export_class_name='TunableChallengeEventDisplayTuple',
      event_icon=TunableIcon(description='\n                            An icon to use for the challenge event.\n                            ',
      allow_none=True),
      event_title=TunableLocalizedString(description='\n                            Title to display.  If not provided, challenge name will be used.\n                            ',
      allow_none=True),
      end_time=TunableTuple(description='\n                            Date and time (UTC) for when the challenge event is expected to end.\n                            This is currently used to compute the time remaining in the UI.\n                            ',
      display_name='End Time (UTC)',
      export_class_name='TunableChallengeDateTuple',
      year=TunableRange(description='\n                                Year\n                                ',
      tunable_type=int,
      default=2016,
      minimum=2014),
      month=TunableRange(description='\n                                Month\n                                ',
      tunable_type=int,
      default=1,
      minimum=1,
      maximum=12),
      day=TunableRange(description='\n                                Day\n                                ',
      tunable_type=int,
      default=1,
      minimum=1,
      maximum=31),
      hour=TunableRange(description='\n                                Hour (24-hour)\n                                ',
      tunable_type=int,
      default=0,
      minimum=0,
      maximum=23),
      minute=TunableRange(description='\n                                Minute\n                                ',
      tunable_type=int,
      default=0,
      minimum=0,
      maximum=59)),
      activity_icon=TunableIcon(description='\n                            Icon to display beside the activity progress bar.\n                            ',
      allow_none=True),
      activity_progress_text=TunableLocalizedString(description="\n                            Status text for when the player is still making progress towards\n                            the challenge goal.  This is currently displayed on a tooltip.\n                            A CSS class of 'timeremaining' will have its color changed\n                            when the event is close to ending.\n                            The following tokens are available:\n                            0 - Number: Current collection progress, if available.\n                            1 - Number: Collection goal, if available.\n                            2 - Number: Hours remaining.\n                            3 - Number: Days remaining.\n                            ",
      allow_none=True),
      activity_progress_icon=TunableIcon(description='\n                            Icon to be paired with the progress text.\n                            ',
      allow_none=True),
      activity_complete_text=TunableLocalizedString(description="\n                            Status text for when the player has met the challenge goal.\n                            This is currently displayed on a tooltip.\n                            If not specified, the in-progress text will be used.\n                            A CSS class of 'timeremaining' will have its color changed\n                            when the event is close to ending.\n                            The following tokens are available (same as the in-progress text):\n                            0 - Number: Current collection progress, if available.\n                            1 - Number: Collection goal, if available.\n                            2 - Number: Hours remaining.\n                            3 - Number: Days remaining.\n                            ",
      allow_none=True),
      activity_complete_icon=TunableIcon(description='\n                            Icon to be paired with the challenge complete text.\n                            If not specified, the in-progress icon will be used.\n                            ',
      allow_none=True),
      community_progress_text=TunableLocalizedString(description="\n                            Status text describing the community's progress.\n                            This is currently displayed on a tooltip.\n                            This text is displayed even when challenges do not have\n                            community goals.\n                            Two Number tokens are available:\n                            0 - Current community collection progress.\n                            1 - Community collection goal, if any.\n                            ",
      allow_none=True),
      community_progress_icon=TunableIcon(description='\n                            Icon to be paired with the community status text.\n                            ',
      allow_none=True),
      community_complete_text=TunableLocalizedString(description='\n                            Status text for when the community has met the challenge goal.\n                            This text is only used when a goal is defined.\n                            If not specified, the in-progress status text will be used.\n                            Two Number tokens are available:\n                            0 - Current community collection progress.\n                            1 - Community collection goal, if any.\n                            ',
      allow_none=True),
      community_complete_icon=TunableIcon(description='\n                            Icon to be paired with the community challenge complete text.\n                            ',
      allow_none=True),
      community_goal_amount=Tunable(description='\n                            Optional collection goal for the community to reach.\n                            ',
      tunable_type=int,
      default=0)),
      collection_id=TunableEnumEntry(description="\n                        A CollectionIdentifier that is associated with this\n                        challenge. This is used by the UI to tie a collectible \n                        with this challenge.\n                        \n                        Use the default of Unindentified for challenges that\n                        aren't associated with a particular collection.\n                        ",
      tunable_type=CollectionIdentifier,
      default=(CollectionIdentifier.Unindentified),
      export_modes=(ExportModes.All)),
      reward_items=TunableList(description='\n                        A list of tuples that describe rewards for challenge.\n                        ',
      tunable=TunableTuple(description='\n                            A tuple that contains data for a challenge reward item.\n                            ',
      export_class_name='TunableChallengeRewardTuple',
      reward_icon=TunableResourceKey(description='\n                                The icon of reward item.\n                                ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE)),
      reward_name=TunableLocalizedString(description='\n                                The name of reward item.\n                                ',
      allow_none=True))))),
      challenge_subtitle=TunableLocalizedString(description='\n                The subtitle text to be displayed in notification UI.\n                ',
      allow_none=True),
      challenge_title=TunableLocalizedString(description='\n                The title text to be displayed in notification UI.\n                ',
      allow_none=True),
      switch_name=Tunable(description='\n                Server switch name to check whether challenge is active.\n                ',
      tunable_type=str,
      default='',
      allow_empty=True)),
      export_modes=(
     ExportModes.ClientBinary,))
    PLATFORM_STRING_REPLACEMENTS = TunableList(description='\n        A list of strings that will be swapped out when in use on different \n        platforms. Each entry contains the original and replacement LocKey, the platforms\n        to perform the swap on, and the input method that is in use when the\n        LocKey is used.\n        ',
      tunable=TunableTuple(original_string=TunableLocalizedString(description='\n                The string that will be replaced or ignored.\n                '),
      replacement_string=OptionalTunable(description='\n                The string that will be used in place of original_string. If\n                omitted, original_string will simply be ignored entirely.\n                ',
      tunable=(TunableLocalizedString())),
      platform=TunableEnumEntry(description='\n                The platforms on which the string will be replaced.\n                ',
      tunable_type=Platform,
      default=(Platform.CONSOLE)),
      input_method=TunableEnumEntry(description='\n                The input method that should be in use when attempting to replace\n                the original_string.\n                ',
      tunable_type=InputMethod,
      default=(InputMethod.ANY)),
      export_modes=(ExportModes.ClientBinary),
      export_class_name='PlatformStringReplacementTuple'))
    SCALING = TunableList(description='\n        Defines a min/max ui scaling value for a screen resolution.\n        ',
      tunable=TunableTuple(screen_width=Tunable(description='\n                Provide an integer value.\n                ',
      tunable_type=int,
      default=0),
      screen_height=Tunable(description='\n                Provide an integer value.\n                ',
      tunable_type=int,
      default=0),
      scale_max=Tunable(description='\n                Provide a float value.\n                ',
      tunable_type=float,
      default=1),
      scale_min=Tunable(description='\n                Provide a float value.\n                ',
      tunable_type=float,
      default=1),
      export_modes=(ExportModes.ClientBinary),
      export_class_name='UIScaleTuple'))
    MAIN_MENU_PLAY_TEXT = TunableMapping(description='\n        Defines text strings which can be shown under the play/new game button on the main menu.\n        A message will be randomly selected from a named group.\n        ',
      key_type=Tunable(description='\n            Name of the group these messages are assigned to.\n            ',
      tunable_type=str,
      default=''),
      value_type=TunableList(description='\n            List of main menu play texts.\n            ',
      tunable=TunableTuple(description='\n                Defines a main menu play button message.\n                ',
      text=TunableLocalizedString(description='\n                    String to display.\n                    ',
      allow_none=False),
      export_modes=(ExportModes.ClientBinary),
      export_class_name='MainMenuPlayText')),
      export_modes=(ExportModes.ClientBinary),
      tuple_name='MainMenuPlayTextMap')
    ENGAGEMENT_MESSAGES = TunableMapping(description='\n        Defines offline engagement messages on the main menu, keyed by destination name.\n        Maps as a subset of values for the UMMainMenuTemplateData class in as3.un\n        ',
      key_type=Tunable(description='\n            Name of the destination these messages are assigned to.\n            ',
      tunable_type=str,
      default=''),
      value_type=TunableList(description='\n            List of engagement messages for a destination.\n            ',
      tunable=TunableTuple(description='\n                Defines an engagement message.\n                ',
      layout=Tunable(description='\n                    Layout id, integer value.\n                    ',
      tunable_type=int,
      default=1),
      layout_position=TunableRange(description='\n                    0 = single large, 1 = left, 2 = right, 3 = middle\n                    ',
      tunable_type=int,
      default=0,
      minimum=0,
      maximum=3),
      message_type=Tunable(description='\n                    Message type.\n                    ',
      tunable_type=str,
      default='Message',
      allow_empty=True),
      image=TunableResourceKey(description='\n                    The main image displayed on the message\n                    ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      allow_none=True),
      title_text=TunableLocalizedString(description='\n                    String to display for the title of the message\n                    ',
      allow_none=True),
      description_text=TunableLocalizedString(description='\n                    String to display for the description of the message\n                    ',
      allow_none=True),
      button_text=TunableLocalizedString(description='\n                    Optional string to display on the cta button\n                    ',
      allow_none=True),
      button_cta_url=Tunable(description='\n                    Url for when cta button is pressed. If button_text is defined\n                    this should also be defined.\n                    ',
      tunable_type=str,
      default='',
      allow_empty=True),
      link_cta_url=Tunable(description='\n                    Optional url for when a link in the description is pressed\n                    ',
      tunable_type=str,
      default='',
      allow_empty=True),
      video_url=Tunable(description='\n                    Optional url for when video button is pressed\n                    ',
      tunable_type=str,
      default='',
      allow_empty=True),
      child_friendly=Tunable(description='\n                    When true this message can be shown to children\n                    ',
      tunable_type=bool,
      default=False),
      export_modes=(ExportModes.ClientBinary),
      export_class_name='UIEngagementMessage')),
      export_modes=(ExportModes.ClientBinary),
      tuple_name='UIEngagementMessageMap')
    CG_CHALLENGE_DATAS = TunableList(description="\n        A list of a challenge's data.\n        ",
      tunable=TunableTuple(cg_challenge_hashtag=TunableLocalizedString(description='\n                Hashtag of this challenge\n                '),
      cg_challenge_name=TunableLocalizedString(description='\n                Name of this challenge\n                '),
      export_modes=(ExportModes.ClientBinary),
      export_class_name='CGChallengeTuning'))
    DEFAULT_OVERLAY_MAP = TunableMapping(description='\n        This is a mapping of MapOverlayEnum -> List of MapOverlayEnums. The key\n        is used as the layer to be shown when no other overlays are present.\n        The value is a list of overlay types that would result in the default\n        layer being turned off if both are active.\n        ',
      key_type=TunableEnumEntry(description='\n            This is the OverlayType that acts as the default for the grouping\n            of OverlayTypes.\n            ',
      tunable_type=MapOverlayEnum,
      default=(MapOverlayEnum.NONE)),
      value_type=TunableList(description='\n            A list of OverlayTypes, that if turned on would result in the\n            default OverlayType being shut off.\n            ',
      tunable=TunableEnumEntry(description='\n                The OverlayType that causes the default value to turn off.\n                ',
      tunable_type=MapOverlayEnum,
      default=(MapOverlayEnum.NONE))),
      export_modes=(ExportModes.All),
      tuple_name='OverlayDefaultData')
    BRANDED_TAG_DATA = TunableList(description='\n        A list of tag to data used to show a branded logo on the item\n        ',
      tunable=TunableTuple(description='\n            Tuning for branded logo to use.\n            ',
      tag=TunableTag(description='\n                Tag to use for the brand to be displayed\n                '),
      icon=TunableIcon(description='\n                Icon to be displayed on the item\n                '),
      background_type=TunableEnumEntry(description='\n                Background to be used for it\n                ',
      tunable_type=BrandedLogoBackground,
      default=(BrandedLogoBackground.LIGHT)),
      style=TunableEnumEntry(description='\n                The style that defines where in the thumbnail we place this branding.\n                ',
      tunable_type=BrandedStyle,
      default=(BrandedStyle.TOP_WIDE)),
      tooltip_title=(OptionalTunable(TunableLocalizedString(description='\n                Title for the tooltip shown when hovering the brand icon.\n                '))),
      tooltip_text=(OptionalTunable(TunableLocalizedString(description='\n                Text for the tooltip shown when hovering the brand icon.\n                '))),
      export_class_name='BrandedTagEntry'),
      export_modes=(ExportModes.ClientBinary))