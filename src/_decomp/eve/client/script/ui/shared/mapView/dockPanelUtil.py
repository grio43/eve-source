#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\dockPanelUtil.py
from carbonui import const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.mapView import dockPanelConst

def GetDockPanelManager():
    if getattr(uicore, 'dockablePanelManager', None) is None:
        from eve.client.script.ui.shared.mapView.dockPanelManager import DockablePanelManager
        uicore.dockablePanelManager = DockablePanelManager()
    return uicore.dockablePanelManager


def GetPanelSettings(panelID):
    defaultSettings = {'align': dockPanelConst.DEFAULT_ALIGN.get(panelID, uiconst.TOALL),
     'dblToggleFullScreenAlign': uiconst.TOPLEFT,
     'positionX': 0.5,
     'positionY': 0.5,
     'widthProportion': dockPanelConst.DEFAULT_WIDTH_PROPORTION.get(panelID, 0.8),
     'heightProportion': 0.8,
     'widthProportion_docked': dockPanelConst.DEFAULT_WIDTH_PROPORTION_DOCKED.get(panelID, 0.5),
     'heightProportion_docked': 1.0,
     'pushedBy': []}
    if panelID:
        charSetting = settings.char
        try:
            registered = charSetting.dockPanels.Get(panelID, {})
        except AttributeError:
            charSetting.CreateGroup('dockPanels')
            registered = charSetting.dockPanels.Get(panelID, {})

        defaultSettings.update(registered)
    return defaultSettings


def HasPanelSettings(panelID):
    if panelID:
        try:
            return bool(settings.char.dockPanels.Get(panelID, {}))
        except AttributeError:
            return False

    return False


def RegisterPanelSettings(panelID, panelSettings):
    settings.char.dockPanels.Set(panelID, panelSettings)


def SetPanelDefaultAlignMode(panelID, defaultAlignMode):
    if HasPanelSettings(panelID):
        return
    panelSettings = GetPanelSettings(panelID)
    panelSettings['align'] = defaultAlignMode
    RegisterPanelSettings(panelID, panelSettings)


def GetPanelAlignMode(panelID):
    return GetPanelSettings(panelID)['align']
