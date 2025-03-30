#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\shipTreeUISvc.py
import evetypes
import threadutils
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.shipTree.infoBubble import InfoBubbleShip, InfoBubbleShipGroup
import blue
import uthread
from eve.client.script.ui.shared.shipTree import shipTreeConst
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
from carbonui.uicore import uicore
from eve.client.script.ui.shared.shipTree.shipTreeDockablePanel import ShipTreeDockablePanel
from eve.client.script.ui.shared.shipTree.shipTreeShipGroup import ShipTreeShipGroup

class ShipTreeUI(Service):
    __guid__ = 'svc.shipTreeUI'
    __servicename__ = 'Ship tree UI service'
    __displayname__ = 'Ship tree UI service'
    __notifyevents__ = ('OnSkillsChanged', 'OnSkillQueueRefreshed')
    __dependencies__ = []

    def Run(self, *args):
        self.forceCloseFanfareBubble = False
        self.selectedFaction = None
        self.infoBubble = None
        self.infoBubbleUIObj = None
        self.infoBubbleCloseThread = None
        self.fanfareBubble = None
        self.fanfareBubbleObj = None
        self.fanfareBubbleCloseThread = None
        self.fanfareBlinker = None
        self._isSelectingFaction = False
        self._isFanfareActive = False
        self.showInfoBubbleThread = None

    def Open(self, factionID = None):
        settings.char.ui.Set('shipTreeSelectedFaction', factionID)
        wnd = ShipTreeDockablePanel.GetIfOpen()
        if wnd and not wnd.destroyed and wnd.IsMinimized():
            wnd.Maximize()
        else:
            ShipTreeDockablePanel.Open()
        if factionID:
            self.SelectFaction(factionID)

    def OpenAndShowShip(self, typeID):
        factionID = evetypes.GetFactionID(typeID)
        shipGroupID = evetypes.GetShipGroupID(typeID)
        self._OpenAndPanToGroup(factionID, shipGroupID)
        sm.ScatterEvent('OnShipTreeShipFocused', typeID)

    def _OpenAndPanToGroup(self, factionID, shipGroupID = None):
        self.Open(factionID)
        animate = self._ShouldAnimatePanTo(factionID)
        if shipGroupID:
            self.PantoShipGroup(shipGroupID, animate)

    def _ShouldAnimatePanTo(self, factionID):
        if not ShipTreeDockablePanel.IsOpen():
            return False
        elif factionID != self.selectedFaction:
            return False
        else:
            return True

    def PantoShipGroup(self, shipGroupID, animate, duration = None):
        wnd = ShipTreeDockablePanel.GetIfOpen()
        if wnd:
            wnd.PanToShipGroup(shipGroupID, animate=animate, duration=duration)

    def OpenAndShowShipGroup(self, factionID, shipGroupID):
        self._OpenAndPanToGroup(factionID, shipGroupID)
        sm.ScatterEvent('OnShipTreeShipGroupFocused', factionID, shipGroupID)

    def OnShipTreeOpened(self):
        self.history = HistoryBuffer()
        sm.GetService('skills').GetSkills()
        self.SelectFaction(self.GetDefaultFactionID())
        sm.GetService('audio').SendUIEvent('isis_start')

    def GetDefaultFactionID(self):
        default = sm.GetService('facwar').GetFactionIDByRaceID(session.raceID)
        return settings.char.ui.Get('shipTreeSelectedFaction', default)

    def OnShipTreeClosed(self):
        self.factionTreesByFactionID = {}
        self.selectedFaction = None
        self._isFanfareActive = False
        self.CloseFanfareBubble()
        self.CloseInfoBubble()
        sm.GetService('audio').SendUIEvent('isis_end')

    def OnShipTreeMinimized(self):
        self._isFanfareActive = False
        self.CloseFanfareBubble()
        self.CloseInfoBubble()

    def GetEntityByID(self, factionID = None, shipGroupID = None, typeID = None):
        if typeID:
            return self.GetFactionTree(factionID).GetShipGroup(shipGroupID).GetShip(typeID)
        elif shipGroupID:
            return self.GetFactionTree(factionID).GetShipGroup(shipGroupID)
        else:
            return self.GetFactionTree(factionID)

    def GetFactionTree(self, factionID):
        return self.factionTreesByFactionID[factionID]

    def GetSelectedFaction(self):
        return self.selectedFaction or self.GetDefaultFactionID()

    def SelectFaction(self, factionID, appendHistory = True):
        if self.selectedFaction == factionID:
            return
        if self._isSelectingFaction:
            return
        self._isSelectingFaction = True
        self.CloseFanfareBubble()
        try:
            oldFactionID = self.selectedFaction
            self.selectedFaction = factionID
            sm.ScatterEvent('OnBeforeShipTreeFactionSelected', factionID)
            ShipTreeDockablePanel.GetIfOpen().SelectFaction(factionID, oldFactionID)
            settings.char.ui.Set('shipTreeSelectedFaction', factionID)
            sm.ScatterEvent('OnShipTreeFactionSelected', factionID)
            eventID = shipTreeConst.GetAudioEventIDForFaction(factionID)
            sm.GetService('audio').SendUIEvent(eventID)
            if appendHistory:
                self.history.Append(factionID)
        finally:
            self._isSelectingFaction = False

    def IsGroupLocked(self, factionID, shipGroupID):
        group = self.GetEntityByID(factionID, shipGroupID)
        return group.data.IsLocked()

    def ShowInfoBubble(self, uiObj, factionID = None, node = None, typeID = None, expertSystems = []):
        isZooming = self.IsZooming()
        if isZooming:
            return
        if uiObj == self.infoBubbleUIObj:
            return
        if self.showInfoBubbleThread:
            self.showInfoBubbleThread.kill()
        if hasattr(node, 'factionID'):
            factionID = node.factionID
        self.showInfoBubbleThread = uthread.new(self._ShowInfoBubble, uiObj, factionID, node, typeID, expertSystems=expertSystems)

    def IsZooming(self):
        wnd = ShipTreeDockablePanel.GetIfOpen()
        return wnd and wnd.isZooming

    def _ShowInfoBubble(self, uiObj, factionID = None, node = None, typeID = None, expertSystems = []):
        self.CloseFanfareBubble()
        blue.synchro.SleepWallclock(150)
        mo = uicore.uilib.mouseOver
        if mo == self.infoBubble or mo.IsUnder(self.infoBubble):
            return
        if uicore.layer.menu.children:
            return
        if self.infoBubble:
            self.CloseInfoBubble()
        self.infoBubbleUIObj = uiObj
        if self.ShouldInfoBubbleClose():
            self.CloseInfoBubble()
            return
        if node:
            self.infoBubble = InfoBubbleShipGroup(factionID=factionID, node=node, parent=uicore.layer.infoBubble, parentObj=uiObj)
        else:
            self.infoBubble = InfoBubbleShip(factionID=factionID, typeID=typeID, parent=uicore.layer.infoBubble, parentObj=uiObj, expertSystems=expertSystems)
        self.infoBubbleCloseThread = uthread.new(self.InfoBubbleCloseThread)
        self.showInfoBubbleThread = None

    def InfoBubbleCloseThread(self, *args):
        while not self.ShouldInfoBubbleClose():
            blue.synchro.Sleep(500)

        self.CloseInfoBubble()

    def ShouldInfoBubbleClose(self):
        if self.IsZooming():
            return True
        mo = uicore.uilib.mouseOver
        if mo == self.infoBubbleUIObj or mo.IsUnder(self.infoBubbleUIObj):
            return False
        if mo == self.infoBubble or mo.IsUnder(self.infoBubble):
            return False
        if uicore.layer.menu.children:
            return False
        return True

    def CloseInfoBubble(self):
        if self.infoBubble:
            self.infoBubble.Close()
        self.infoBubble = None
        self.infoBubbleUIObj = None
        if self.infoBubbleCloseThread:
            self.infoBubbleCloseThread.kill()
            self.infoBubbleCloseThread = None

    @threadutils.threaded
    def ShowUnlockFanfare(self, factionID, shipGroupID):
        if self.fanfareBubble:
            self.CloseFanfareBubble()
        wnd = ShipTreeDockablePanel.GetIfOpen()
        if not wnd:
            return
        self.SelectFaction(factionID=factionID)
        self.PantoShipGroup(shipGroupID=shipGroupID, animate=True, duration=0.5)
        self.forceCloseFanfareBubble = False
        self._isFanfareActive = True
        uthread2.sleep(0.5)
        uiObj = wnd.GetShipGroup(shipGroupID)
        node = uiObj.node
        uiObj.FlashGroupIcon(0.9)
        uthread2.sleep(0.9)
        fanfareDelay = uiObj.PlayFanfare()
        uthread2.sleep(fanfareDelay)
        if self._isFanfareActive:
            self.OpenFanfareInfoBubble(uiObj, node, factionID)
        uthread2.sleep(1)
        self._isFanfareActive = False

    def OpenFanfareInfoBubble(self, uiObj, node, factionID):
        if self.fanfareBubble:
            self.CloseFanfareBubble()
        PlaySound('ship_goals_reveal_button_end_play')
        self.fanfareBubble = InfoBubbleShipGroup(factionID=factionID, node=node, parent=uicore.layer.infoBubble, parentObj=uiObj)
        self.fanfareBubbleCloseThread = uthread.new(self._FanfareBubbleCloseThread)

    def _FanfareBubbleCloseThread(self):
        while not self.ShouldFanfareInfoBubbleClose():
            blue.synchro.Sleep(500)

        self.CloseFanfareBubble()

    def ShouldFanfareInfoBubbleClose(self):
        if self._isFanfareActive:
            return False
        if self.IsZooming():
            return True
        return self.forceCloseFanfareBubble

    def CloseFanfareBubble(self):
        self.forceCloseFanfareBubble = False
        if self.fanfareBubble:
            self.fanfareBubble.Close()
        if self.fanfareBlinker:
            self.fanfareBlinker.dispose()
        self.fanfareBubble = None
        self.fanfareBlinker = None
        self.fanfareBubbleUIObj = None
        if self.fanfareBubbleCloseThread:
            self.fanfareBubbleCloseThread.kill()
            self.fanfareBubbleCloseThread = None

    def GetZoomLevel(self):
        wnd = ShipTreeDockablePanel.GetIfOpen()
        if wnd:
            return wnd.zoomLevel

    def PanTo(self, x, y, animate = True):
        wnd = ShipTreeDockablePanel.GetIfOpen()
        if wnd:
            wnd.PanToPropCoords(x, y, animate)

    def GoBack(self):
        factionID = self.history.GoBack()
        if factionID:
            self.SelectFaction(factionID, appendHistory=False)

    def GoForward(self):
        factionID = self.history.GoForward()
        if factionID:
            self.SelectFaction(factionID, appendHistory=False)

    def OnDrag(self):
        self.CloseInfoBubble()
        self.CloseFanfareBubble()

    def OnSkillsChanged(self, *args):
        sm.GetService('shipTree').FlushRecentlyChangedSkillsCache()
        self._UpdateActiveTreeSkills()

    def OnSkillQueueRefreshed(self):
        self._UpdateActiveTreeSkills()

    def _UpdateActiveTreeSkills(self):
        if sm.GetService('viewState').IsViewActive('shiptree'):
            wnd = ShipTreeDockablePanel.GetIfOpen()
            if wnd:
                wnd.shipTreeCont.UpdateTreeSkills()
            sm.ScatterEvent('OnShipTreeSkillTrained')
