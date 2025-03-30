#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\eventManager.py
import carbonui.const as uiconst
import evetypes
from carbonui.uicore import uicore
from eve.client.script.ui.shared.planet import planetCommon
from eve.client.script.ui.shared.planet.depletionPinManager import DepletionManager
from eve.client.script.ui.shared.planet.planetConst import STATE_NORMAL, STATE_BUILDPIN, STATE_CREATELINKSTART, STATE_CREATELINKEND, STATE_CREATEROUTE, STATE_SURVEY, SUBSTATE_NORMAL, SUBSTATE_MOVEEXTRACTIONHEAD, STATE_DECOMMISSION
from eve.client.script.ui.shared.planet.surveyUI import SurveyWindow

class EventManager:
    __notifyevents__ = ['OnPlanetChangesSubmitted']

    def __init__(self):
        sm.RegisterNotify(self)
        self.state = STATE_NORMAL
        self.subState = SUBSTATE_NORMAL
        self.selectedPin = None
        self.selectedLink = None
        self.showRoutePin = None
        self.selectedPinIDs = set()

    def Close(self):
        sm.UnregisterNotify(self)

    def OnPlanetChangesSubmitted(self, planetID):
        self.SetStateNormal()

    def OnPlanetViewOpened(self):
        self.planetUISvc = sm.GetService('planetUI')
        self.myPinManager = self.planetUISvc.myPinManager
        self.myPinManager = self.planetUISvc.myPinManager
        self.otherPinManager = self.planetUISvc.otherPinManager

    def OnPlanetViewClosed(self):
        self.SetStateNormal()

    def SetStateNormal(self):
        self._SetState(STATE_NORMAL)
        self._SetSubState(SUBSTATE_NORMAL)

    def SetStateBuildPin(self):
        self._SetState(STATE_BUILDPIN)

    def SetStateCreateLinkStart(self):
        self._SetState(STATE_CREATELINKSTART)

    def SetStateCreateLinkEnd(self):
        self._SetState(STATE_CREATELINKEND)

    def SetStateCreateRoute(self):
        self._SetState(STATE_CREATEROUTE)

    def SetStateSurvey(self):
        self._SetState(STATE_SURVEY)

    def SetStateDecommission(self):
        self._SetState(STATE_DECOMMISSION)

    def _SetState(self, state):
        oldState = self.state
        self.state = state
        if state != oldState:
            if oldState == STATE_BUILDPIN:
                self.myPinManager.EndPlacingPin()
            elif oldState == STATE_CREATELINKSTART and state != STATE_CREATELINKEND:
                self.myPinManager.EndLinkCreation()
            elif oldState == STATE_CREATELINKEND:
                self.myPinManager.EndLinkCreation()
            elif oldState == STATE_CREATEROUTE:
                self.myPinManager.LeaveRouteMode()
            elif oldState == STATE_SURVEY:
                self.myPinManager.LeaveSurveyMode()
        sm.ScatterEvent('OnPlanetUIStateChanged', state, oldState)

    def SetSubStateNormal(self):
        self._SetSubState(SUBSTATE_NORMAL)

    def SetSubStateMoveExtractionHead(self):
        self._SetSubState(SUBSTATE_MOVEEXTRACTIONHEAD)

    def _SetSubState(self, subState):
        if subState == self.subState:
            return
        oldSubState = self.subState
        self.subState = subState

    def OnPlanetPinClicked(self, pinID):
        if pinID not in self.myPinManager.pinsByID:
            return
        if uicore.uilib.rightbtn:
            return
        shouldClearMultiSelect = True
        if self.state == STATE_CREATEROUTE:
            self._CreateRouteSelectPin(pinID)
        elif self.state == STATE_CREATELINKEND:
            self.DeselectCurrentlySelected()
            self.myPinManager.SetLinkChild(self.myPinManager.linkParentID, pinID)
        elif self.state == STATE_DECOMMISSION:
            self.myPinManager.RemovePin(pinID)
        elif uicore.uilib.Key(uiconst.VK_CONTROL) or self.state == STATE_CREATELINKSTART:
            self.DeselectCurrentlySelected()
            self.myPinManager.SetLinkParent(pinID)
        else:
            shouldClearMultiSelect = False
            self.SelectPin(pinID)
        if shouldClearMultiSelect:
            self.selectedPinIDs.clear()
            self.UpdateMultiPinSelection()

    def SelectPin(self, pinID):
        shiftDown = uicore.uilib.Key(uiconst.VK_SHIFT)
        pin = self.GetPinByID(pinID)
        if not shiftDown and self.selectedPin and pin == self.selectedPin:
            return
        if shiftDown:
            if pinID in self.selectedPinIDs:
                self.selectedPinIDs.discard(pinID)
            else:
                self.selectedPinIDs.add(pinID)
        else:
            self.ResetMultiSelect()
            self.selectedPinIDs.add(pinID)
        panelID = self._DeselectCurrentlySelected()
        self.UpdateMultiPinSelection()
        if len(self.selectedPinIDs) < 2:
            self.planetUISvc.OpenContainer(pin.pin, panelID=panelID)
            self.selectedPin = pin
            pin.SetSelected()
            self.ShowRoutesToFromPin(pin)

    def ResetMultiSelect(self):
        self.selectedPinIDs.clear()
        self.UpdateMultiPinSelection()

    def UpdateMultiPinSelection(self):
        for pinID, pin in self.myPinManager.pinsByID.iteritems():
            doDisplay = len(self.selectedPinIDs) > 1 and pinID in self.selectedPinIDs
            pin.SetMultiSelectedDisplay(doDisplay)

    def GetPinByID(self, pinID):
        pin = self.myPinManager.pinsByID[pinID]
        return pin

    def DeselectCurrentlySelected(self):
        self.selectedPinIDs.clear()
        return self._DeselectCurrentlySelected()

    def _DeselectCurrentlySelected(self):
        sm.GetService('audio').SendUIEvent('msg_pi_pininteraction_close_play')
        if self.selectedPin:
            self._DeselectCurrentlySelectedPin()
        elif self.selectedLink:
            self._DeselectCurrentlySelectedLink()
        panelID = self.planetUISvc.CloseCurrentlyOpenPinContainer()
        return panelID

    def _DeselectCurrentlySelectedPin(self):
        self.selectedPin.SetDeselected()
        self.StopShowingRouteToFromPin()
        self.selectedPin = None

    def _DeselectCurrentlySelectedLink(self):
        self.selectedLink.SetDeselected()
        self.selectedLink = None

    def _CreateRouteSelectPin(self, pinID):
        if self.myPinManager.currentRoute:
            self.myPinManager.SetRouteWaypoint(pinID)
            if self.myPinManager.oneoffRoute:
                self.myPinManager.CreateRoute()
            elif self.planetUISvc.currentContainer:
                self.planetUISvc.currentContainer.OnPlanetRouteWaypointAdded(self.myPinManager.currentRoute)
        else:
            self.myPinManager.EnterRouteMode(pinID)

    def OnPlanetPinDblClicked(self, pinID):
        if self.state == STATE_CREATEROUTE:
            if self.myPinManager.oneoffRoute:
                return
            self.myPinManager.SetRouteWaypoint(pinID)
            self.planetUISvc.currentContainer.SubmitRoute()
        elif self.planetUISvc.currentContainer:
            self.planetUISvc.currentContainer.ShowDefaultPanel()

    def OnDepletionPinClicked(self, index):
        self.DeselectCurrentlySelected()
        DepletionManager.Open(pinManager=self.myPinManager)

    def OnPlanetPinMouseEnter(self, pinID):
        if self.state == STATE_BUILDPIN:
            return
        if self.state == STATE_SURVEY and self.myPinManager.IsDraggingExtractionHead():
            return
        pin = self.myPinManager.pinsByID.get(pinID, None)
        if not pin:
            return
        pin.OnMouseEnter()
        if self.state == STATE_CREATEROUTE:
            self._HighlightRoute(pin)
        elif self.state == STATE_CREATELINKEND:
            parentPin = self.myPinManager.pinsByID.get(self.myPinManager.linkParentID)
            if not parentPin:
                return
            self.planetUISvc.curveLineDrawer.ChangeLinePosition('rubberLink', self.myPinManager.rubberLink, pin.surfacePoint, parentPin.surfacePoint)
            self.myPinManager.UpdateRubberLinkLabels(pin.surfacePoint, parentPin.surfacePoint)
        else:
            self.ShowRoutesToFromPin(pin)

    def GetColony(self):
        planet = sm.GetService('planetUI').planet
        if planet:
            return planet.GetColony(session.charid)

    def ShowRoutesToFromPin(self, pin):
        self.StopShowingRouteToFromPin()
        self.showRoutePin = pin
        colony = self.GetColony()
        if not colony or colony.colonyData is None:
            return
        routesFrom = colony.colonyData.GetSourceRoutesForPin(pin.pin.id)
        routesTo = colony.colonyData.GetDestinationRoutesForPin(pin.pin.id)
        numRoutes = len(routesFrom)
        for i, route in enumerate(routesFrom):
            path = route.path
            links = self.myPinManager.GetLinksFromPath(path)
            for l, id in links:
                l.ShowAsRoute(id, i, numRoutes)

            pin = self.GetPinByID(path[-1])
            pin.SetAsRoute()

        numRoutes = len(routesTo)
        for i, routeID in enumerate(routesTo):
            r = colony.GetRoute(routeID)
            path = r.path
            links = self.myPinManager.GetLinksFromPath(path)
            for l, id in links:
                l.ShowAsRoute(id, i, numRoutes)

            pin = self.GetPinByID(path[0])
            pin.SetAsRoute()

    def _HighlightRoute(self, pin):
        colony = self.GetColony()
        currentRoute = self.myPinManager.currentRoute
        if currentRoute and pin.pin.id not in currentRoute:
            path = colony.FindShortestPathIDs(currentRoute[-1], pin.pin.id)
            self.myPinManager.routeHoverPath = path
            links = self.myPinManager.GetLinksFromPath(path)
            for l, id in links:
                l.ShowAsRoute(id, 1, 1, self.myPinManager.currRouteVolume)

    def OnPlanetPinMouseExit(self, pinID):
        if not self:
            return
        pin = self.myPinManager.pinsByID.get(pinID, None)
        if not pin:
            return
        pin.OnMouseExit()
        if self.state == STATE_CREATEROUTE:
            path = getattr(self.myPinManager, 'routeHoverPath', [])
            links = self.myPinManager.GetLinksFromPath(path)
            for l, id in links:
                l.RemoveAsRoute(id)

        else:
            self.StopShowingRouteToFromPin()
            if self.selectedPin:
                self.ShowRoutesToFromPin(self.selectedPin)

    def StopShowingRouteToFromPin(self):
        if not self.showRoutePin:
            return
        colony = self.GetColony()
        if colony is None or colony.colonyData is None:
            return
        routesFrom = colony.colonyData.GetSourceRoutesForPin(self.showRoutePin.pin.id)
        routesTo = colony.colonyData.GetDestinationRoutesForPin(self.showRoutePin.pin.id)
        for route in routesFrom:
            path = route.path
            links = self.myPinManager.GetLinksFromPath(path)
            for l, id in links:
                l.RemoveAsRoute(id)

            pin = self.GetPinByID(path[-1])
            pin.ResetAsRoute()

        for routeID in routesTo:
            r = colony.GetRoute(routeID)
            path = r.path
            links = self.myPinManager.GetLinksFromPath(path)
            for l, id in links:
                l.RemoveAsRoute(id)

            pin = self.GetPinByID(path[0])
            pin.ResetAsRoute()

        self.showRoutePin = None

    def OnExtractionHeadMouseEnter(self, ecuID, headNum):
        if self.state == STATE_SURVEY:
            self.myPinManager.OnExtractionHeadMouseEnter(ecuID, headNum)

    def OnExtractionHeadMouseExit(self, ecuID, headNum):
        if self.state == STATE_SURVEY:
            self.myPinManager.OnExtractionHeadMouseExit(ecuID, headNum)

    def OnExtractionHeadMouseDown(self, ecuID, headNum):
        if self.state == STATE_SURVEY and not uicore.uilib.Key(uiconst.VK_CONTROL):
            self.myPinManager.BeginDragExtractionHead(ecuID, headNum)

    def OnExtractionHeadClicked(self, ecuID, headNum):
        if self.state == STATE_SURVEY:
            if uicore.uilib.Key(uiconst.VK_CONTROL):
                self.myPinManager.RemoveExtractionHead(ecuID, headNum)

    def OnOtherCharactersCommandPinClicked(self, pinID):
        pin = self.otherPinManager.otherPlayerPinsByPinID.get(pinID)
        if not pin:
            return
        if evetypes.GetGroupID(pin.typeID) != const.groupCommandPins:
            return
        self.otherPinManager.RenderOtherCharactersNetwork(pin.ownerID)

    def OnPlanetOtherPinMouseEnter(self, pinID):
        if pinID not in self.otherPinManager.otherPlayerPinsByPinID:
            return
        pin = self.otherPinManager.otherPlayerPinsByPinID[pinID]
        pin.OnMouseEnter()

    def OnPlanetOtherPinMouseExit(self, pinID):
        if pinID not in self.otherPinManager.otherPlayerPinsByPinID:
            return
        pin = self.otherPinManager.otherPlayerPinsByPinID[pinID]
        pin.OnMouseExit()

    def OnPlanetNavClicked(self, wasDragged):
        surfacePoint = planetCommon.GetPickIntersectionPoint()
        if not wasDragged and self.state != STATE_SURVEY:
            self.DeselectCurrentlySelected()
            self.ResetMultiSelect()
            self.otherPinManager.HideOtherCharactersNetwork()
        if surfacePoint:
            if self.state == STATE_BUILDPIN:
                if not wasDragged:
                    self.myPinManager.PlacePin(surfacePoint)
            elif self.state == STATE_SURVEY and uicore.uilib.Key(uiconst.VK_CONTROL):
                wnd = SurveyWindow.GetIfOpen()
                if wnd:
                    self.myPinManager.PlaceExtractionHead(wnd.pin.id, surfacePoint)

    def OnPlanetNavMouseUp(self):
        if self.state == STATE_SURVEY:
            if self.subState == SUBSTATE_MOVEEXTRACTIONHEAD:
                self.myPinManager.EndDragExtractionHead()

    def OnPlanetNavRightClicked(self):
        if self.state != STATE_NORMAL:
            self.SetStateNormal()
            return True
        else:
            return False

    def OnPlanetSurfaceMouseMoved(self, surfacePoint):
        if self.state == STATE_CREATELINKEND:
            self.myPinManager.UpdateRubberLink(surfacePoint)
        elif self.state == STATE_BUILDPIN:
            if self.myPinManager.buildIndicatorPin:
                self.myPinManager.buildIndicatorPin.SetLocation(surfacePoint)
                canBuild = self.myPinManager.DistanceToOtherPinsOK(surfacePoint)
                self.myPinManager.buildIndicatorPin.SetCanBuildIndication(canBuild)
        elif self.state == STATE_SURVEY:
            if self.subState == SUBSTATE_MOVEEXTRACTIONHEAD:
                self.myPinManager.DragExtractionHeadTo(surfacePoint)

    def OnPlanetNavFocusLost(self):
        if self.state in (STATE_CREATELINKEND, STATE_BUILDPIN):
            self.SetStateNormal()

    def MoveTemplate(self):
        from eve.client.script.ui.shared.planet.templatePreviewWindow import StartDraggingTemplate
        x = uicore.uilib.x
        y = uicore.uilib.y
        StartDraggingTemplate(x, y)

    def OnPlanetLinkClicked(self, linkID):
        if linkID not in self.myPinManager.linksByGraphicID:
            return
        if self.state in (STATE_CREATEROUTE, STATE_CREATELINKSTART, STATE_CREATELINKEND):
            return
        if self.state == STATE_DECOMMISSION:
            link = self.myPinManager.linksByGraphicID[linkID]
            self.myPinManager.RemoveLink(link.GetIDTuple())
        else:
            self.SelectLink(linkID)

    def SelectLink(self, linkID):
        link = self.myPinManager.linksByGraphicID[linkID]
        if self.planetUISvc.currentContainer and self.planetUISvc.currentContainer.pin == link:
            return
        panelID = self.DeselectCurrentlySelected()
        link.SetSelected()
        self.selectedLink = link
        self.planetUISvc.OpenContainerLink(link, panelID)

    def OnPlanetLinkDblClicked(self, linkID):
        if self.planetUISvc.currentContainer:
            self.planetUISvc.currentContainer.ShowDefaultPanel()

    def OnPlanetLinkMouseEnter(self, lineID):
        if self.state == STATE_CREATEROUTE:
            return
        if lineID in self.myPinManager.linksByGraphicID:
            link = self.myPinManager.linksByGraphicID[lineID]
            link.OnMouseEnter()

    def OnPlanetLinkMouseExit(self, areaID):
        if self.state == STATE_CREATEROUTE:
            return
        if areaID in self.myPinManager.linksByGraphicID:
            link = self.myPinManager.linksByGraphicID[areaID]
            link.OnMouseExit()

    def BeginCreateLink(self, sourcePinID):
        self._SetState(STATE_CREATELINKSTART)
        self.DeselectCurrentlySelected()
        self.myPinManager.SetLinkParent(sourcePinID)
