#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetsWindow\coloniesPanel.py
import uthread
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eve.client.script.ui.shared.planet.planetsWindow.colonyEntry import ColonyEntry, ColonyEntryCompact, ColonyEntryEmpty, ColonyEntryEmptyCompact
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib import appConst
from localization import GetByLabel
import blue
MAX_NUM_COLONIES = 6
ACTION_SETDEST = 1
ACTION_WARPTO = 2
ACTION_ACCESS = 3

class ColoniesPanel(Container):
    default_name = 'ColoniesPanel'
    __notifyevents__ = ['OnPlanetCommandCenterDeployedOrRemoved',
     'OnPlanetPinsChanged',
     'OnColonyPinCountUpdated',
     'OnSessionChanged',
     'OnClientEvent_WarpFinished',
     'OnViewStateChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.isCompact = attributes.isCompact
        self.entries = []
        self.scrollCont = ScrollContainer(name='scrollCont', parent=self)
        self.btnGroup = ButtonGroup(parent=self, align=uiconst.TOBOTTOM, idx=0, padTop=8)
        self.viewBtn = self.btnGroup.AddButton(GetByLabel('UI/Common/View'), self.ViewPlanet, hint=GetByLabel('UI/PI/Common/ViewInPlanetMode'))
        self.actionBtn = self.btnGroup.AddButton(GetByLabel('UI/Commands/WarpTo'), self.OnActionBtnClicked)
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN)
        uthread.new(self.UpdateThread)

    def UpdateThread(self):
        while not self.destroyed:
            for entry in self.entries:
                entry.Update()

            blue.pyos.synchro.SleepWallclock(1000)

    def OnTabSelect(self):
        self.LoadPlanetScroll()

    def LoadPlanetScroll(self):
        scrollPos = self.scrollCont.GetPositionVertical()
        self.scrollCont.Flush()
        self.loadingWheel.Show()
        self.entries = []
        planetSvc = sm.GetService('planetSvc')
        planetsData = planetSvc.GetMyPlanetsData()
        self.ConstructEntries(planetsData)
        self.ConstructEmptyEntries(planetsData)
        self.viewBtn.Disable()
        self.actionBtn.Disable()
        self.loadingWheel.Hide()
        if scrollPos:
            self.scrollCont.ScrollToVertical(scrollPos)

    def ConstructEmptyEntries(self, planetsData):
        numColonies = len(planetsData)
        skillLvl = sm.GetService('skills').GetMyLevel(appConst.typeInterplanetaryConsolidation) or 0
        maxColonies = skillLvl + 1
        if numColonies < MAX_NUM_COLONIES:
            for i in xrange(numColonies, MAX_NUM_COLONIES):
                cls = ColonyEntryEmptyCompact if self.isCompact else ColonyEntryEmpty
                entry = cls(parent=self.scrollCont, align=uiconst.TOTOP, padBottom=2, slotIndex=i, slotsTotal=maxColonies)
                self.entries.append(entry)

    def ConstructEntries(self, planetsData):
        for planetData in planetsData:
            cls = ColonyEntryCompact if self.isCompact else ColonyEntry
            entry = cls(parent=self.scrollCont, align=uiconst.TOTOP, planetData=planetData, padBottom=2, onClickCallback=self.OnEntryClicked)
            self.entries.append(entry)

    def OnEntryClicked(self, entryClicked):
        for entry in self.entries:
            if entry == entryClicked:
                entry.SetSelected()
                self.viewBtn.Enable()
            elif entry.isSelected:
                entry.SetDeselected()

        self.UpdateButtons()

    def ViewPlanet(self, *args):
        entry = self.GetSelectedEntry()
        if entry:
            sm.GetService('viewState').ActivateView('planet', planetID=entry.planetData.planetID)

    def UpdateViewPlanetBtn(self):
        entry = self.GetSelectedEntry()
        if not entry:
            self.viewBtn.Disable()
            return
        viewState = sm.GetService('viewState').GetView(ViewState.Planet)
        if viewState.IsActive():
            if viewState.lastPlanetID == entry.GetPlanetID():
                self.viewBtn.Disable()
                return
        self.viewBtn.Enable()

    def UpdateButtons(self):
        self.UpdateViewPlanetBtn()
        self.UpdateActionButton()

    def UpdateActionButton(self):
        entry = self.GetSelectedEntry()
        if entry:
            actionID = self._GetActionButtonActionID(entry)
            if actionID:
                self.actionBtn.Enable()
            else:
                self.actionBtn.Disable()
            self.UpdateActionBtnLabel(actionID)
        else:
            self.actionBtn.Disable()

    def _GetActionButtonActionID(self, entryClicked):
        solarSystemID = entryClicked.planetData.solarSystemID
        if self.IsWarpToPossible(solarSystemID):
            customsOfficeID = self.GetCustomsOfficeID(entryClicked.planetData.planetID)
            ball = sm.GetService('michelle').GetBall(customsOfficeID)
            if ball and ball.surfaceDist < 50000:
                return ACTION_ACCESS
            else:
                return ACTION_WARPTO
        elif solarSystemID != session.solarsystemid2:
            return ACTION_SETDEST

    def UpdateActionBtnLabel(self, actionID):
        if actionID == ACTION_ACCESS:
            self.actionBtn.SetLabel(GetByLabel('UI/PI/Common/Access'))
            self.actionBtn.SetHint(GetByLabel('UI/PI/Common/AccessCustomOffice'))
        elif actionID == ACTION_WARPTO:
            self.actionBtn.SetLabel(GetByLabel('UI/Commands/WarpTo'))
            self.actionBtn.SetHint(GetByLabel('UI/PI/Common/WarpToPlanetHint'))
        else:
            self.actionBtn.SetLabel(GetByLabel('UI/Inflight/SetDestination'))
            self.actionBtn.SetHint('')
        self.btnGroup.ResetLayout()

    def IsWarpToPossible(self, solarSystemID):
        return session.solarsystemid2 and solarSystemID == session.solarsystemid and not session.structureid

    def OnActionBtnClicked(self, *args):
        entry = self.GetSelectedEntry()
        actionID = self._GetActionButtonActionID(entry)
        if actionID == ACTION_WARPTO:
            self.WarpToPlanet(entry)
        elif actionID == ACTION_ACCESS:
            self.AccessCustomsOffice(entry)
        else:
            self.SetDestinationToSystem(entry)

    def AccessCustomsOffice(self, entry):
        customsOfficeID = self.GetCustomsOfficeID(entry.planetData.planetID)
        sm.GetService('planetUI').OpenPlanetCustomsOfficeImportWindow(customsOfficeID)

    def SetDestinationToSystem(self, entry):
        sm.StartService('starmap').SetWaypoint(entry.planetData.solarSystemID, clearOtherWaypoints=True)

    def WarpToPlanet(self, entry):
        planetID = entry.planetData.planetID
        customsOfficeID = self.GetCustomsOfficeID(planetID)
        itemID = customsOfficeID or planetID
        movementFunctions.WarpToItem(itemID)

    def GetCustomsOfficeID(self, planetID):
        customsOfficeIDs = sm.GetService('planetInfo').GetFunctionalCustomOfficeOrbitalsForPlanet(planetID)
        if customsOfficeIDs:
            return list(customsOfficeIDs)[0]

    def GetSelectedEntry(self):
        for entry in self.entries:
            if entry.isSelected:
                return entry

    def OnPlanetCommandCenterDeployedOrRemoved(self):
        self.LoadPlanetScroll()

    def OnPlanetPinsChanged(self, planetID):
        self.LoadPlanetScroll()

    def OnColonyPinCountUpdated(self, planetID):
        self.LoadPlanetScroll()

    def OnSessionChanged(self, isRemote, sess, change):
        self.UpdateButtons()

    def OnClientEvent_WarpFinished(self, *args):
        self.UpdateButtons()

    def OnViewStateChanged(self, oldView, newView):
        self.UpdateButtons()
