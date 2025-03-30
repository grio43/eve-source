#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\actionPanelDefaults.py
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.control.window import Window
default_width = 566
activeItem_default_height_large = 174
activeItem_default_height_medium = 174
activeItem_default_height_small = 138
overview_default_height_large = 690
overview_default_height_medium = 640
overview_default_height_small = 380
droneView_default_height_large = 216
droneView_default_height_medium = 156
droneView_default_height_small = 156

def _GetWidth():
    return default_width


def GetActiveItemLeft():
    return uicore.desktop.width - GetActiveItemWidth() - 16


def GetActiveItemTop():
    return 16


def GetActiveItemWidth():
    return _GetWidth()


def GetActiveItemHeight():
    height = uicore.desktop.height
    if height >= uiconst.UI_DEFAULT_HEIGHT_THRESHOLD_LARGE:
        return activeItem_default_height_large
    if height >= uiconst.UI_DEFAULT_HEIGHT_THRESHOLD_MEDIUM:
        return activeItem_default_height_medium
    return activeItem_default_height_small


def GetOverviewLeft():
    return uicore.desktop.width - GetOverviewWidth() - 16


def GetOverviewTop():
    return GetActiveItemTop() + GetActiveItemHeight()


def GetOverviewWidth():
    return _GetWidth()


def GetOverviewHeight():
    deviceHeight = uicore.desktop.height
    if deviceHeight >= uiconst.UI_DEFAULT_HEIGHT_THRESHOLD_LARGE:
        return overview_default_height_large
    if deviceHeight >= uiconst.UI_DEFAULT_HEIGHT_THRESHOLD_MEDIUM:
        return overview_default_height_medium
    return overview_default_height_small


def GetDroneViewLeft():
    return uicore.desktop.width - GetDroneViewWidth() - 16


def GetDroneViewTop():
    topRight_TopOffset = Window.GetTopRight_TopOffset()
    if topRight_TopOffset is not None:
        return topRight_TopOffset
    return GetOverviewTop() + GetOverviewHeight()


def GetDroneViewWidth():
    return _GetWidth()


def GetDroneViewHeight():
    deviceHeight = uicore.desktop.height
    if deviceHeight >= uiconst.UI_DEFAULT_HEIGHT_THRESHOLD_LARGE:
        return droneView_default_height_large
    if deviceHeight >= uiconst.UI_DEFAULT_HEIGHT_THRESHOLD_MEDIUM:
        return droneView_default_height_medium
    return droneView_default_height_small
