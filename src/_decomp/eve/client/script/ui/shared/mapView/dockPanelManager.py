#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\dockPanelManager.py
from eve.client.script.ui.shared.mapView.dockPanelUtil import RegisterPanelSettings
import carbonui.const as uiconst
from carbonui.uicore import uicore

class DockablePanelManager(object):
    __notifyevents__ = ['OnSetDevice', 'OnShowUI', 'OnHideUI']

    def __init__(self):
        self.panels = {}
        settings.char.CreateGroup('dockPanels')
        sm.RegisterNotify(self)

    def GetIfOpen(self, panelID):
        panel = self.panels.get(panelID, None)
        if panel and not panel.destroyed:
            return panel

    def GetAllOpen(self):
        return self.panels.values()

    def GetCurrentFullscreenPanel(self):
        for panel in self.GetAllOpen():
            if panel.IsFullscreen():
                return panel

    def RegisterPanel(self, dockPanel):
        if dockPanel.panelID in self.panels:
            prevPanel = self.panels[dockPanel.panelID]
            if not prevPanel.destroyed:
                prevPanel.Close()
        self.panels[dockPanel.panelID] = dockPanel

    def UnregisterPanel(self, dockPanel):
        if dockPanel.panelID in self.panels:
            del self.panels[dockPanel.panelID]
        self.CheckViewState()

    def CheckViewState(self):
        self.UpdateCameraCenter()

    def GetFullScreenView(self):
        for panel in self.panels.values():
            if panel.IsFullscreen() and not panel.IsMinimized():
                return panel

    def UpdateCameraCenter(self):
        if self.IsAnyPanelDockedToSide() and sm.GetService('ui').IsUiVisible():
            pLeft, pRight = uicore.layer.sidePanels.GetSideOffset()
            viewCenter = pLeft + (uicore.desktop.width - pLeft - pRight) / 2
            viewCenterProportion = viewCenter / float(uicore.desktop.width)
            sm.GetService('sceneManager').SetCameraOffsetOverride(-100 + int(200 * viewCenterProportion))
        else:
            sm.GetService('sceneManager').SetCameraOffsetOverride(None)

    def IsAnyPanelDockedToSide(self):
        for panel in self.panels.values():
            if panel.IsDockedLeft() or panel.IsDockedRight():
                return True

        return False

    def OnSetDevice(self, *args, **kwds):
        for panel in self.panels.values():
            if not panel.IsFullscreen() and not panel.IsMinimized():
                panel.InitDockPanelPosition()

    def OnHideUI(self, *args):
        self.UpdateCameraCenter()

    def OnShowUI(self, *args):
        self.UpdateCameraCenter()

    def UpdatePanelsPushedBySettings(self):
        for panel in self.panels.values():
            if panel.align not in (uiconst.TOLEFT, uiconst.TORIGHT):
                continue
            pushedBy = []
            for each in uicore.layer.sidePanels.children:
                if each is panel:
                    break
                if each.align == panel.align:
                    pushedBy.append(each.name)

            currentSettings = panel.GetPanelSettings()
            currentSettings['pushedBy'] = pushedBy
            RegisterPanelSettings(panel.panelID, currentSettings)

    def ResetAllPanelSettings(self):
        settings.char.Remove('dockPanels')
        for panel in self.GetAllOpen():
            panel.Close()
            panel.Open()
