#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\directionalScanUtil.py
import math
from carbonui.uicore import uicore
SCANMODE_TARGET = 1
SCANMODE_CAMERA = 2
RANGEMODE_AU = 1
RANGEMODE_KM = 2

def SetActiveScanMode(scanMode):
    if GetActiveScanMode() != scanMode:
        settings.char.ui.Set('directionalScannerMode', scanMode)
        sm.ScatterEvent('OnDirectionalScannerScanModeChanged', scanMode)


def GetActiveScanMode():
    return settings.char.ui.Get('directionalScannerMode', SCANMODE_TARGET)


def ToggleScanMode():
    scanMode = GetActiveScanMode()
    if scanMode == SCANMODE_TARGET:
        SetScanModeCamera()
    else:
        SetScanModeTarget()


def SetScanModeTarget():
    SetActiveScanMode(SCANMODE_TARGET)


def SetScanModeCamera():
    SetActiveScanMode(SCANMODE_CAMERA)


def SetScanConeDisplayState(displayState):
    if IsDscanConeShown() != displayState:
        settings.char.ui.Set('directionalScannerShowCone', displayState)
        sm.ScatterEvent('OnDirectionalScannerShowCone', displayState)


def IsDscanConeShown():
    return settings.char.ui.Get('directionalScannerShowCone', True)


def ConvertKmToAu(kmValue):
    auValue = kmValue * 1000 / const.AU
    return auValue


def ConvertAuToKm(auValue):
    kmValue = int(auValue * const.AU / 1000)
    return kmValue


def GetScanRange():
    return settings.user.ui.Get('dir_scanrange', const.AU * MAX_RANGE_AU)


def GetScanRangeInMeters():
    return GetScanRange() * 1000


def SetScanRange(scanRangeKM):
    scanRangeKM = min(MAX_RANGE_KM, max(MIN_RANGE_KM, scanRangeKM))
    settings.user.ui.Set('dir_scanrange', scanRangeKM)
    sm.ScatterEvent('OnDirectionalScannerRangeChanged', GetScanRangeInMeters())


MIN_RANGE_KM = 10
MAX_RANGE_AU = 14.3
MIN_RANGE_AU = ConvertKmToAu(MIN_RANGE_KM)
MAX_RANGE_KM = ConvertAuToKm(MAX_RANGE_AU)

def GetScanAngle():
    return settings.user.ui.Get('scan_angleSlider', math.pi / 2)


def SetScanAngle(angle):
    angle = max(0, min(angle, 2 * math.pi))
    settings.user.ui.Set('scan_angleSlider', angle)
    sm.ScatterEvent('OnDirectionalScannerAngleChanged', angle)


def IsDscanShortcutPressed():
    return uicore.cmd.IsCombatCommandLoaded('CmdRefreshDirectionalScan')
