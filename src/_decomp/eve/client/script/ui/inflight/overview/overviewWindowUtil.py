#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewWindowUtil.py
import localization
from eve.client.script.ui.inflight.overview.overviewWindow import OverviewWindow

def GetOverviewWndIfOpen():
    return OverviewWindow.GetIfOpen()


def IsOverviewWndOpen():
    return OverviewWindow.IsOpen()


def OpenOverview():
    presetSvc = sm.GetService('overviewPresetSvc')
    for windowInstanceID in presetSvc.GetWindowInstanceIDs():
        windowID = presetSvc.GetWindowID(windowInstanceID)
        if not OverviewWindow.GetIfOpen(windowID=windowID):
            OverviewWindow.OpenBehindFullscreenViews(showActions=False, panelName=localization.GetByLabel('UI/Overview/Overview'), windowID=windowID, windowInstanceID=windowInstanceID)


def CloseAllOverviewWindows():
    for windowID in sm.GetService('overviewPresetSvc').GetWindowIDs():
        OverviewWindow.CloseIfOpen(windowID=windowID)
