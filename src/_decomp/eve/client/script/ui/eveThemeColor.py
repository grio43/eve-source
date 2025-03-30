#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\eveThemeColor.py
import chroma
from eve.client.script.ui import eveColor

class ThemeColor(chroma.ColorMutable):
    pass


THEME_TINT = ThemeColor(eveColor.SMOKE_BLUE)
THEME_FOCUS = ThemeColor(eveColor.CRYO_BLUE)
THEME_FOCUSDARK = ThemeColor(eveColor.SMOKE_BLUE)
THEME_ACCENT = ThemeColor('#58A7BF')
THEME_ALERT = ThemeColor('#F39058')

def SetThemeColors(tint, focus, focus_dark, accent, alert):
    global THEME_ACCENT
    global THEME_FOCUS
    global THEME_FOCUSDARK
    global THEME_TINT
    THEME_TINT.rgba = tint
    THEME_FOCUS.rgba = focus
    THEME_FOCUSDARK.rgba = focus_dark
    THEME_ACCENT.rgba = accent
    THEME_ALERT.rgba = alert
