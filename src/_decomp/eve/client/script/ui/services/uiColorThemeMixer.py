#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\uiColorThemeMixer.py
from carbonui import uiconst
from carbonui.util.color import Color

def GetUIColor(baseColor, colorType):
    if colorType == uiconst.COLORTYPE_UIBASE:
        return GetBaseColor(baseColor)
    if colorType == uiconst.COLORTYPE_UIHILIGHT:
        return GetHilightColor(baseColor)
    if colorType == uiconst.COLORTYPE_UIBASECONTRAST:
        return GetBaseContrastColor(baseColor)
    if colorType == uiconst.COLORTYPE_UIHILIGHTGLOW:
        return GetHilightGlowColor(baseColor)
    if colorType == uiconst.COLORTYPE_FLASH:
        return GetFlashColor(baseColor)
    if colorType == uiconst.COLORTYPE_ACCENT:
        return baseColor


def GetBaseColor(color):
    return color


def GetBaseContrastColor(color):
    return Color(*color).SetBrightness(0.075).GetRGBA()


def GetHilightColor(color):
    return Color(*color).SetBrightness(0.75).GetRGBA()


def GetHilightGlowColor(color):
    color = Color(*color).SetBrightness(1.0)
    if color.GetSaturation() > 0.2:
        color.SetSaturation(0.2)
    return color.GetRGBA()


def GetFlashColor(color):
    color = Color(*color).SetBrightness(1.0).SetSaturation(0.25)
    return color.GetRGBA()
