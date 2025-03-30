#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\highlightState.py
from eve.client.script.ui import eveThemeColor, eveColor

class HighlightState(object):
    normal = 1
    open = 2
    active = 3
    important = 4


def GetIndicatorColor(highlightState):
    if highlightState == HighlightState.important:
        return eveThemeColor.THEME_ALERT
    elif highlightState == HighlightState.active:
        return eveThemeColor.THEME_ACCENT
    elif highlightState == HighlightState.open:
        return eveThemeColor.eveColor.SILVER_GREY
    else:
        return (0, 0, 0, 0)


def GetIndicatorBackgroundColor(highlightState):
    if highlightState == HighlightState.important:
        return eveThemeColor.THEME_ALERT
    elif highlightState == HighlightState.active:
        return eveColor.SMOKE_BLUE
    elif highlightState == HighlightState.open:
        return eveThemeColor.THEME_FOCUSDARK
    else:
        return eveColor.LED_GREY


def GetIndicatorGlowBrightness(highlightState):
    if highlightState in (HighlightState.important, HighlightState.active):
        return 0.5
    else:
        return 0.1


def GetPrimaryColor(highlightState):
    if highlightState == HighlightState.open:
        return eveThemeColor.THEME_ACCENT
    elif highlightState == HighlightState.important:
        return eveThemeColor.THEME_ALERT
    else:
        return eveColor.WHITE
