#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\charactercreator\client\scalingUtils.py
from carbonui.uicore import uicore
SMALL_SCREEN_HEIGHT = 768
BIG_SCREEN_HEIGHT = 1080
NUMBER_OF_BANNERS = 4
BANNER_SEPARATION = 0
BANNER_WIDTH = 213
BANNER_HEIGHT = 346
SMALL_PANEL_WIDTH = 900
SMALL_PANEL_HEIGHT = 600
HORIZONTAL_PANEL_WIDTH = 700
HORIZONTAL_PANEL_HEIGHT = 250
EMPIRE_LOGO_SIZE_SMALL = 128
PANEL_HEADER_HEIGHT = 36
ENLIST_BUTTON_WIDTH = 166
ENLIST_BUTTON_HEIGHT = 46
CUSTOMIZE_CHARACTER_BUTTON_WIDTH = 166
CUSTOMIZE_CHARACTER_BUTTON_HEIGHT = 46

def GetScaleFactor():
    return float(uicore.desktop.height) / float(SMALL_SCREEN_HEIGHT)


def GetBannerWidth():
    bannerWidth = BANNER_WIDTH * GetScaleFactor()
    desktopWidth = uicore.desktop.width
    if NUMBER_OF_BANNERS * bannerWidth > desktopWidth:
        return desktopWidth / NUMBER_OF_BANNERS
    return bannerWidth


def GetBannerHeight():
    bannerWidth = BANNER_WIDTH * GetScaleFactor()
    bannerHeight = BANNER_HEIGHT * GetScaleFactor()
    adaptedBannerWidth = GetBannerWidth()
    desktopWidth = uicore.desktop.width
    if bannerWidth > 0 and adaptedBannerWidth == desktopWidth / NUMBER_OF_BANNERS:
        adaptedBannerHeight = bannerHeight * adaptedBannerWidth / bannerWidth
        return adaptedBannerHeight
    return bannerHeight


def GetBannersWidth():
    return GetBannerWidth() * NUMBER_OF_BANNERS + BANNER_SEPARATION * (NUMBER_OF_BANNERS - 1)


def GetMainPanelWidth():
    return min(SMALL_PANEL_WIDTH * GetScaleFactor(), uicore.desktop.width)


def GetMainPanelHeight():
    return uicore.desktop.height - GetTopNavHeight() - GetBottomNavHeight()


def GetMainPanelEmpireLogoSize():
    return EMPIRE_LOGO_SIZE_SMALL * GetScaleFactor()


def GetTopNavHeight():
    return (uicore.desktop.height - SMALL_PANEL_HEIGHT * GetScaleFactor()) / 2


def GetBottomNavHeight():
    return GetTopNavHeight()


def GetHorizontalPanelWidth():
    return min(HORIZONTAL_PANEL_WIDTH * GetScaleFactor(), uicore.desktop.width)


def GetHorizontalPanelHeight():
    return HORIZONTAL_PANEL_HEIGHT * GetScaleFactor()


def GetBannerHeaderHeight():
    return PANEL_HEADER_HEIGHT * GetScaleFactor()


def GetEnlistButtonWidth():
    return ENLIST_BUTTON_WIDTH * GetScaleFactor()


def GetEnlistButtonHeight():
    return ENLIST_BUTTON_HEIGHT * GetScaleFactor()


def GetCustomizeCharacterButtonWidth():
    return CUSTOMIZE_CHARACTER_BUTTON_WIDTH * GetScaleFactor()


def GetCustomizeCharacterButtonHeight():
    return CUSTOMIZE_CHARACTER_BUTTON_HEIGHT * GetScaleFactor()
