#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\button\styling.py
from carbonui.button.const import ButtonStyle, ButtonVariant, HEIGHT_COMPACT, HEIGHT_EXPANDED, HEIGHT_NORMAL, InteractionState
from carbonui.fontconst import EVE_LARGE_FONTSIZE, EVE_SMALL_FONTSIZE
from carbonui.text.color import TextColor
from carbonui.uiconst import Density
from eve.client.script.ui import eveColor, eveThemeColor
_FOREGROUND_COLOR_IDLE = TextColor.NORMAL
_FOREGROUND_COLOR_HOVERED = TextColor.HIGHLIGHT
_FOREGROUND_COLOR_PRESSED = eveColor.BLACK
_FOREGROUND_COLOR_DISABLED = TextColor.DISABLED
_ICON_COLOR_IDLE = TextColor.NORMAL
_ICON_COLOR_DISABLED = TextColor.DISABLED
_ICON_COLOR_HOVERED = TextColor.HIGHLIGHT
_ICON_COLOR_PRESSED = eveColor.BLACK
_BACKGROUND_COLOR_IDLE = {ButtonVariant.NORMAL: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUSDARK.rgb + (0.2,),
                        ButtonStyle.WARNING: tuple(eveColor.DUSKY_ORANGE[:3]) + (0.2,),
                        ButtonStyle.DANGER: tuple(eveColor.CHERRY_RED[:3]) + (0.2,),
                        ButtonStyle.MONETIZATION: tuple(eveColor.BURNISHED_GOLD[:3]) + (0.2,),
                        ButtonStyle.SUCCESS: tuple(eveColor.COPPER_OXIDE_GREEN[:3]) + (0.2,)},
 ButtonVariant.PRIMARY: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUSDARK.rgb + (0.6,),
                         ButtonStyle.WARNING: tuple(eveColor.DUSKY_ORANGE[:3]) + (0.6,),
                         ButtonStyle.DANGER: tuple(eveColor.CHERRY_RED[:3]) + (0.6,),
                         ButtonStyle.MONETIZATION: tuple(eveColor.BURNISHED_GOLD[:3]) + (0.6,),
                         ButtonStyle.SUCCESS: tuple(eveColor.COPPER_OXIDE_GREEN[:3]) + (0.6,)},
 ButtonVariant.GHOST: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUSDARK.rgb + (0.0,),
                       ButtonStyle.WARNING: tuple(eveColor.DUSKY_ORANGE[:3]) + (0.0,),
                       ButtonStyle.DANGER: tuple(eveColor.CHERRY_RED[:3]) + (0.0,),
                       ButtonStyle.MONETIZATION: tuple(eveColor.BURNISHED_GOLD[:3]) + (0.0,),
                       ButtonStyle.SUCCESS: tuple(eveColor.COPPER_OXIDE_GREEN[:3]) + (0.0,)}}
_BACKGROUND_COLOR_HOVERED = {ButtonVariant.NORMAL: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUSDARK.rgb + (0.6,),
                        ButtonStyle.WARNING: tuple(eveColor.DUSKY_ORANGE[:3]) + (0.6,),
                        ButtonStyle.DANGER: tuple(eveColor.CHERRY_RED[:3]) + (0.6,),
                        ButtonStyle.MONETIZATION: tuple(eveColor.BURNISHED_GOLD[:3]) + (0.6,),
                        ButtonStyle.SUCCESS: tuple(eveColor.COPPER_OXIDE_GREEN[:3]) + (0.6,)},
 ButtonVariant.PRIMARY: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUSDARK.rgb + (0.6,),
                         ButtonStyle.WARNING: tuple(eveColor.DUSKY_ORANGE[:3]) + (0.6,),
                         ButtonStyle.DANGER: tuple(eveColor.CHERRY_RED[:3]) + (0.6,),
                         ButtonStyle.MONETIZATION: tuple(eveColor.BURNISHED_GOLD[:3]) + (0.6,),
                         ButtonStyle.SUCCESS: tuple(eveColor.COPPER_OXIDE_GREEN[:3]) + (0.6,)},
 ButtonVariant.GHOST: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUSDARK.rgb + (0.6,),
                       ButtonStyle.WARNING: tuple(eveColor.DUSKY_ORANGE[:3]) + (0.6,),
                       ButtonStyle.DANGER: tuple(eveColor.CHERRY_RED[:3]) + (0.6,),
                       ButtonStyle.MONETIZATION: tuple(eveColor.BURNISHED_GOLD[:3]) + (0.6,),
                       ButtonStyle.SUCCESS: tuple(eveColor.COPPER_OXIDE_GREEN[:3]) + (0.6,)}}
_BACKGROUND_COLOR_PRESSED = eveColor.TUNGSTEN_GREY
_BACKGROUND_COLOR_DISABLED = {ButtonVariant.NORMAL: tuple(eveColor.MATTE_BLACK[:3]) + (0.2,),
 ButtonVariant.PRIMARY: tuple(eveColor.MATTE_BLACK[:3]) + (0.6,),
 ButtonVariant.GHOST: tuple(eveColor.MATTE_BLACK[:3]) + (0.0,)}
_STROKE_COLOR_IDLE = {ButtonVariant.NORMAL: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUSDARK,
                        ButtonStyle.WARNING: eveColor.WARNING_ORANGE,
                        ButtonStyle.DANGER: eveColor.CHERRY_RED,
                        ButtonStyle.MONETIZATION: eveColor.SAND_YELLOW,
                        ButtonStyle.SUCCESS: eveColor.SUCCESS_GREEN},
 ButtonVariant.PRIMARY: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUS,
                         ButtonStyle.WARNING: eveColor.WARNING_ORANGE,
                         ButtonStyle.DANGER: eveColor.CHERRY_RED,
                         ButtonStyle.MONETIZATION: eveColor.SAND_YELLOW,
                         ButtonStyle.SUCCESS: eveColor.SUCCESS_GREEN},
 ButtonVariant.GHOST: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUSDARK.rgb + (0.6,),
                       ButtonStyle.WARNING: tuple(eveColor.DUSKY_ORANGE[:3]) + (0.6,),
                       ButtonStyle.DANGER: tuple(eveColor.CHERRY_RED[:3]) + (0.6,),
                       ButtonStyle.MONETIZATION: tuple(eveColor.BURNISHED_GOLD[:3]) + (0.6,),
                       ButtonStyle.SUCCESS: tuple(eveColor.COPPER_OXIDE_GREEN[:3]) + (0.6,)}}
_STROKE_COLOR_HOVERED = {ButtonVariant.NORMAL: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUS,
                        ButtonStyle.WARNING: eveColor.WARNING_ORANGE,
                        ButtonStyle.DANGER: eveColor.HOT_RED,
                        ButtonStyle.MONETIZATION: eveColor.SAND_YELLOW,
                        ButtonStyle.SUCCESS: eveColor.SUCCESS_GREEN},
 ButtonVariant.PRIMARY: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUS,
                         ButtonStyle.WARNING: eveColor.WARNING_ORANGE,
                         ButtonStyle.DANGER: eveColor.HOT_RED,
                         ButtonStyle.MONETIZATION: eveColor.SAND_YELLOW,
                         ButtonStyle.SUCCESS: eveColor.SUCCESS_GREEN},
 ButtonVariant.GHOST: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUS,
                       ButtonStyle.WARNING: eveColor.WARNING_ORANGE,
                       ButtonStyle.DANGER: eveColor.HOT_RED,
                       ButtonStyle.MONETIZATION: eveColor.SAND_YELLOW,
                       ButtonStyle.SUCCESS: eveColor.SUCCESS_GREEN}}
_STROKE_COLOR_PRESSED = eveColor.TUNGSTEN_GREY
_STROKE_COLOR_DISABLED = tuple(eveColor.MATTE_BLACK[:3]) + (0.6,)
_GLOW_COLOR_IDLE = {ButtonVariant.NORMAL: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUS.rgb + (0.0,),
                        ButtonStyle.WARNING: tuple(eveColor.WARNING_ORANGE[:3]) + (0.0,),
                        ButtonStyle.DANGER: tuple(eveColor.HOT_RED[:3]) + (0.0,),
                        ButtonStyle.MONETIZATION: tuple(eveColor.SAND_YELLOW[:3]) + (0.0,),
                        ButtonStyle.SUCCESS: tuple(eveColor.SUCCESS_GREEN[:3]) + (0.0,)},
 ButtonVariant.PRIMARY: {ButtonStyle.NORMAL: lambda : eveThemeColor.THEME_FOCUS.rgb + (0.0,),
                         ButtonStyle.WARNING: tuple(eveColor.WARNING_ORANGE[:3]) + (0.0,),
                         ButtonStyle.DANGER: tuple(eveColor.HOT_RED[:3]) + (0.0,),
                         ButtonStyle.MONETIZATION: tuple(eveColor.SAND_YELLOW[:3]) + (0.0,),
                         ButtonStyle.SUCCESS: tuple(eveColor.SUCCESS_GREEN[:3]) + (0.0,)},
 ButtonVariant.GHOST: {ButtonStyle.NORMAL: tuple(eveColor.BLACK[:3]) + (0.0,),
                       ButtonStyle.WARNING: tuple(eveColor.BLACK[:3]) + (0.0,),
                       ButtonStyle.DANGER: tuple(eveColor.BLACK[:3]) + (0.0,),
                       ButtonStyle.MONETIZATION: tuple(eveColor.BLACK[:3]) + (0.0,),
                       ButtonStyle.SUCCESS: tuple(eveColor.BLACK[:3]) + (0.0,)}}
_GLOW_COLOR_HOVERED = {ButtonVariant.NORMAL: {ButtonStyle.NORMAL: lambda : tuple(eveThemeColor.THEME_FOCUS[:3]) + (0.6,),
                        ButtonStyle.WARNING: tuple(eveColor.WARNING_ORANGE[:3]) + (0.6,),
                        ButtonStyle.DANGER: tuple(eveColor.HOT_RED[:3]) + (0.6,),
                        ButtonStyle.MONETIZATION: tuple(eveColor.SAND_YELLOW[:3]) + (0.6,),
                        ButtonStyle.SUCCESS: tuple(eveColor.SUCCESS_GREEN[:3]) + (0.6,)},
 ButtonVariant.PRIMARY: {ButtonStyle.NORMAL: lambda : tuple(eveThemeColor.THEME_FOCUS[:3]) + (0.6,),
                         ButtonStyle.WARNING: tuple(eveColor.WARNING_ORANGE[:3]) + (0.6,),
                         ButtonStyle.DANGER: tuple(eveColor.HOT_RED[:3]) + (0.6,),
                         ButtonStyle.MONETIZATION: tuple(eveColor.SAND_YELLOW[:3]) + (0.6,),
                         ButtonStyle.SUCCESS: tuple(eveColor.SUCCESS_GREEN[:3]) + (0.6,)},
 ButtonVariant.GHOST: {ButtonStyle.NORMAL: lambda : tuple(eveThemeColor.THEME_FOCUS[:3]) + (0.6,),
                       ButtonStyle.WARNING: tuple(eveColor.WARNING_ORANGE[:3]) + (0.6,),
                       ButtonStyle.DANGER: tuple(eveColor.HOT_RED[:3]) + (0.6,),
                       ButtonStyle.MONETIZATION: tuple(eveColor.SAND_YELLOW[:3]) + (0.6,),
                       ButtonStyle.SUCCESS: tuple(eveColor.SUCCESS_GREEN[:3]) + (0.6,)}}
_GLOW_COLOR_PRESSED = eveColor.TUNGSTEN_GREY
_GLOW_COLOR_DISABLED = tuple(eveColor.TUNGSTEN_GREY[:3]) + (0.0,)

def resolve(color):
    if callable(color):
        color = color()
    if hasattr(color, 'rgba'):
        color = color.rgba
    return color


def get_foreground_color(button_variant, button_style, interaction_states):
    if InteractionState.disabled in interaction_states:
        return resolve(_FOREGROUND_COLOR_DISABLED)
    elif InteractionState.pressed in interaction_states:
        return resolve(_FOREGROUND_COLOR_PRESSED)
    elif InteractionState.hovered in interaction_states:
        return resolve(_FOREGROUND_COLOR_HOVERED)
    else:
        return resolve(_FOREGROUND_COLOR_IDLE)


def get_icon_color(button_variant, button_style, interaction_states):
    if InteractionState.disabled in interaction_states:
        return resolve(_ICON_COLOR_DISABLED)
    elif InteractionState.pressed in interaction_states:
        return resolve(_ICON_COLOR_PRESSED)
    elif InteractionState.hovered in interaction_states:
        return resolve(_ICON_COLOR_HOVERED)
    else:
        return resolve(_ICON_COLOR_IDLE)


def get_background_color(button_variant, button_style, interaction_states):
    if InteractionState.disabled in interaction_states:
        return resolve(_BACKGROUND_COLOR_DISABLED[button_variant])
    elif InteractionState.pressed in interaction_states:
        return resolve(_BACKGROUND_COLOR_PRESSED)
    elif InteractionState.hovered in interaction_states:
        return resolve(_BACKGROUND_COLOR_HOVERED[button_variant][button_style])
    else:
        return resolve(_BACKGROUND_COLOR_IDLE[button_variant][button_style])


def get_stroke_color(button_variant, button_style, interaction_states):
    if InteractionState.disabled in interaction_states:
        return resolve(_STROKE_COLOR_DISABLED)
    elif InteractionState.pressed in interaction_states:
        return resolve(_STROKE_COLOR_PRESSED)
    elif InteractionState.hovered in interaction_states:
        return resolve(_STROKE_COLOR_HOVERED[button_variant][button_style])
    else:
        return resolve(_STROKE_COLOR_IDLE[button_variant][button_style])


def get_glow_color(button_variant, button_style, interaction_states):
    if InteractionState.disabled in interaction_states:
        return resolve(_GLOW_COLOR_DISABLED)
    elif InteractionState.pressed in interaction_states:
        return resolve(_GLOW_COLOR_PRESSED)
    elif InteractionState.hovered in interaction_states:
        return resolve(_GLOW_COLOR_HOVERED[button_variant][button_style])
    else:
        return resolve(_GLOW_COLOR_IDLE[button_variant][button_style])


def get_height(density):
    if density == Density.NORMAL:
        return HEIGHT_NORMAL
    if density == Density.COMPACT:
        return HEIGHT_COMPACT
    if density == Density.EXPANDED:
        return HEIGHT_EXPANDED


def get_min_width(density):
    return get_height(density)


def get_icon_offset(density):
    if density in [Density.NORMAL, Density.EXPANDED]:
        return 4
    if density == Density.COMPACT:
        return 2


def get_icon_gap(density):
    if density in [Density.NORMAL, Density.EXPANDED]:
        return 8
    if density == Density.COMPACT:
        return 6


def get_side_padding(density):
    if density == Density.NORMAL:
        return 16
    if density == Density.COMPACT:
        return 8
    if density == Density.EXPANDED:
        return 40


def get_fontsize(density):
    if density == Density.NORMAL:
        return EVE_SMALL_FONTSIZE
    if density == Density.COMPACT:
        return EVE_SMALL_FONTSIZE
    if density == Density.EXPANDED:
        return EVE_LARGE_FONTSIZE


def get_default_min_width(density):
    if density == Density.EXPANDED:
        return 180
    return 32
