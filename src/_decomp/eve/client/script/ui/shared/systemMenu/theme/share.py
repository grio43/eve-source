#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\theme\share.py
import carbonui
import eveui.clipboard
import localization
from carbonui.uicore import uicore
from chroma import Color
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.systemMenu.theme import theme_const, theme_util

def parse_theme_slug(slug):
    try:
        focus, accent, tint, alert = slug.split(',')
        focus = theme_util.get_with_capped_brightness(Color.from_hex(focus.strip()), min=theme_const.FOREGROUND_MIN_BRIGHTNESS)
        accent = theme_util.get_with_capped_brightness(Color.from_hex(accent.strip()), min=theme_const.FOREGROUND_MIN_BRIGHTNESS)
        tint = theme_util.get_with_capped_brightness(Color.from_hex(tint.strip()), max=theme_const.BACKGROUND_MAX_BRIGHTNESS)
        alert = theme_util.get_with_capped_brightness(Color.from_hex(alert.strip()), min=theme_const.FOREGROUND_MIN_BRIGHTNESS)
    except Exception:
        raise InvalidThemeSlug()
    else:
        return (focus,
         accent,
         tint,
         alert)


def format_theme_slug(focus, accent, tint, alert):
    return u','.join([focus.hex_rgb,
     accent.hex_rgb,
     tint.hex_rgb,
     alert.hex_rgb]).upper()


class InvalidThemeSlug(ValueError):
    pass


def copy_theme_slug_to_clipboard(theme_slug):
    eveui.clipboard.set(theme_slug)
    ShowQuickMessage(localization.GetByLabel('UI/SystemMenu/GeneralSettings/ColorTheme/ThemeCopiedToClipboard'), layer=uicore.layer.modal)
