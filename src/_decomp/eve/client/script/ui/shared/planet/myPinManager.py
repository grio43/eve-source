#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\myPinManager.py
from collections import defaultdict
import evetypes
import threadutils
import utillib
from carbon.common.script.util.format import FmtDist
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.shared.planet.planetConst import GetPinNameShort
from eve.client.script.ui.util import uix
import carbonui.const as uiconst
import log
import geo2
import trinity
import localization
import eve.common.script.util.planetCommon as planetCommon
from eve.client.script.ui.shared.planet import planetConst
from eve.client.script.ui.shared.planet.planetCommon import GetPickIntersectionPoint, GetSchematicDataForID
from eve.client.script.ui.shared.planet.planetUILinks import Link
from eve.common.script.planet.surfacePoint import SurfacePoint
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
from eve.client.script.ui.shared.planet.planetUIPins import CommandCenterPin, ExtractorPin, ProcessorPin, LaunchpadPin, StorageFacilityPin, EcuPin, DepletionPin, BuildIndicatorPin
from carbonui.uicore import uicore
from eve.client.script.ui.shared.planet.surveyUI import SurveyWindow
from eve.common.lib import appConst as const
from eveexceptions import UserError
from evelink.client import type_link
from eveplanet.client.installSchematicMenu import MultiPinMenuProvider
from eveplanet.client.routeReplace import GetRouteToDeleteAndNewRouteData

class MyPinManager:
    __notifyevents__ = ['OnPlanetPinsChanged',
     'OnRefreshPins',
     'OnEditModeBuiltOrDestroyed',
     'OnPlanetPinPlaced']

    def __init__(self):
        sm.RegisterNotify(self)
        self.planetUISvc = None
        self.linkParentID = None
        self.routeParentID = None
        self.currentRoute = []
        self.routeHoverPath = []
        self.oneoffRoute = False
        self.isEdit = False
        self.currRouteVolume = None
        self.newPinType = None
        self.canMoveHeads = None
        self.depletionPoints = []
        self.extractionHeadDragged = None
        self.pinsByID = {}
        self.linksByPinIDs = {}
        self.linksByGraphicID = {}
        self.links = []
        self.buildIndicatorPin = None
        self.currentEcuPinID = None
        self.bracketCurveSet = trinity.TriCurveSet()
        self.bracketCurveSet.name = 'PlanetBrackets'
        uicore.desktop.GetRenderObject().curveSets.append(self.bracketCurveSet)

    def Close(self):
        sm.UnregisterNotify(self)
        self.planetUISvc = None
        self.linkParentID = None
        self.routeParentID = None
        self.currentRoute = None
        self.routeHoverPath = None
        self.currRouteVolume = None
        self.newPinType = None
        self.canMoveHeads = None
        self.depletionPoints = None
        self.pinsByID = None
        self.linksByPinIDs = None
        self.linksByGraphicID = None
        self.links = None
        self.buildIndicatorPin = None
        self.currentEcuPinID = None
        self.bracketCurveSet = None

    def OnPlanetViewOpened(self):
        self.planetUISvc = sm.GetService('planetUI')
        self.eventManager = self.planetUISvc.eventManager
        sp = SurfacePoint()
        rubberColor = (1.0, 1.0, 1.0, 1.0)
        self.rubberLink = self.planetUISvc.curveLineDrawer.DrawArc('rubberLink', sp, sp, 2.0, rubberColor, rubberColor)
        self.InitRubberLinkLabels()
        self.ReRender()
        self.depletionPoints = []
        self.bracketCurveSet.Play()

    def OnPlanetViewClosed(self):
        self.ClearPinsFromScene()
        self.ClearLinksFromScene()
        self.bracketCurveSet.Stop()
        self.isEdit = False

    def ReRender(self):
        if not sm.GetService('viewState').IsViewActive('planet'):
            return
        self.RenderPins()
        self.RenderLinks()
        self.ResetPinData()

    def ReRenderPin(self, pin):
        if not sm.GetService('viewState').IsViewActive('planet'):
            return
        uiPin = self.pinsByID.get(pin.id, None)
        if uiPin is None:
            return
        uiPin.Remove()
        self.RenderPin(pin)

    def InitRubberLinkLabels(self):
        self.rubberLinkLabelContainer = Container(name='rubberLinkLabels', parent=self.planetUISvc.planetUIContainer, pos=(400, 400, 110, 55), padding=(4, 4, 4, 4), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        self.rubberLinkLabels = utillib.KeyVal()
        self.rubberLinkLabels.padding = 3
        self.rubberLinkLabels.columnPadding = 9
        white = (1.0, 1.0, 1.0, 1.0)
        gray = (1.0, 1.0, 1.0, 0.6)
        self.rubberLinkLabels.distanceLbl = eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Common/Distance'), parent=self.rubberLinkLabelContainer, left=self.rubberLinkLabels.padding, height=16, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=gray)
        maxLabelWidth = uix.GetTextWidth(localization.GetByLabel('UI/Common/Distance'))
        self.rubberLinkLabels.powerLbl = eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Common/Power'), parent=self.rubberLinkLabelContainer, top=16, left=self.rubberLinkLabels.padding, height=16, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=gray)
        maxLabelWidth = max(maxLabelWidth, uix.GetTextWidth(localization.GetByLabel('UI/Common/Power')))
        self.rubberLinkLabels.cpuLbl = eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Common/Cpu'), parent=self.rubberLinkLabelContainer, top=32, left=self.rubberLinkLabels.padding, height=16, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, color=gray)
        maxLabelWidth = max(maxLabelWidth, uix.GetTextWidth(localization.GetByLabel('UI/Common/Cpu')))
        maxLabelWidth += self.rubberLinkLabels.columnPadding
        self.rubberLinkLabels.distance = eveLabel.EveLabelMedium(text='', parent=self.rubberLinkLabelContainer, left=2, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, color=white)
        self.rubberLinkLabels.power = eveLabel.EveLabelMedium(text='', parent=self.rubberLinkLabelContainer, left=2, top=16, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, color=white)
        self.rubberLinkLabels.cpu = eveLabel.EveLabelMedium(text='', parent=self.rubberLinkLabelContainer, left=2, top=32, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, color=white)
        Fill(parent=self.rubberLinkLabelContainer, color=(0.0, 0.0, 0.0, 0.5))

    def OnPlanetPinsChanged(self, planetID):
        if sm.GetService('viewState').IsViewActive('planet') and self.planetUISvc and self.planetUISvc.GetCurrentPlanet().planetID == planetID:
            self.planetUISvc.SetPlanet(planetID)
            self.ReRender()
            self.linkParentID = None
            self.routeParentID = None
        self.currentRoute = []

    def ResetPinData(self):
        if self.planetUISvc.planet.colony is None:
            return
        pinData = self.planetUISvc.planet.colony.colonyData.pins
        for pinID, pinUI in self.pinsByID.iteritems():
            pinUI.ResetPinData(pinData[pinID])

    def OnRefreshPins(self, pinIDs = None):
        for p in self.pinsByID.values():
            p.OnRefreshPins()

        for l in self.linksByPinIDs.values():
            l.OnRefreshPins()

    def OnEditModeBuiltOrDestroyed(self, planetID):
        currentPlanet = self.planetUISvc.GetCurrentPlanet()
        if currentPlanet and currentPlanet.planetID == planetID:
            self._OnEditModeBuiltOrDestroyed()

    @threadutils.throttled(0.1)
    def _OnEditModeBuiltOrDestroyed(self):
        self.OnRefreshPins()

    def OnPlanetPinPlaced(self, pinID):
        planet = sm.GetService('planetUI').GetCurrentPlanet()
        if planet is None:
            return
        colony = planet.GetColony(session.charid)
        if colony is None:
            return
        pin = colony.GetPin(pinID)
        if pin is None:
            return
        UIpin = self.RenderPin(pin)
        UIpin.PlacementAnimation()

    def OnPlanetEnteredEditMode(self):
        sm.ScatterEvent('OnEditModeChanged', True)

    def OnPlanetExitedEditMode(self):
        self.ReRender()
        sm.ScatterEvent('OnEditModeChanged', False)
        if self.planetUISvc.currentContainer is not None:
            self.planetUISvc.eventManager.DeselectCurrentlySelected()

    def SetLinkParent(self, parentID):
        self.eventManager.SetStateCreateLinkEnd()
        self.linkParams = planetCommon.GetUsageParametersForLinkType(const.typeTestPlanetaryLink)
        pin = self.pinsByID[parentID]
        self.planetUISvc.curveLineDrawer.ChangeLinePosition('rubberLink', self.rubberLink, pin.surfacePoint, pin.surfacePoint)
        self.planetUISvc.curveLineDrawer.ChangeLineSetWidth('rubberLink', 2.0)
        self.rubberLinkLabelContainer.state = uiconst.UI_DISABLED
        surfacePoint = planetCommonUI.GetPickIntersectionPoint()
        self.linkParentID = parentID
        self.UpdateRubberLink(surfacePoint)

    def EndLinkCreation(self):
        self.linkParentID = None
        self.planetUISvc.curveLineDrawer.ChangeLineSetWidth('rubberLink', 0.0)
        self.rubberLinkLabelContainer.state = uiconst.UI_HIDDEN

    def LaunchCommodities(self, pinID, commoditiesToLaunch):
        self.planetUISvc.planet.LaunchCommodities(pinID, commoditiesToLaunch)

    def EnterRouteMode(self, pinID, typeID = None, oneoff = False):
        if typeID or oneoff:
            self.typeToRoute = typeID
        else:
            pin = self.pinsByID[pinID]
            products = pin.pin.GetProductMaxOutput()
            if not products:
                return
            self.typeToRoute = products.keys()[0]
        self.eventManager.SetStateCreateRoute()
        self.routeHoverPath = []
        self.currentRoute = [pinID]
        self.oneoffRoute = oneoff
        selectedPin = self.eventManager.selectedPin
        if selectedPin:
            selectedPin.HideHologramModel()

    def LeaveRouteMode(self):
        links = self.GetLinksFromPath(self.currentRoute)
        for l, id in links:
            l.RemoveAsRoute(id)

        if len(self.routeHoverPath) > 0:
            links = self.GetLinksFromPath(self.routeHoverPath)
            for l, id in links:
                l.RemoveAsRoute(id)

        self.routeHoverPath = []
        self.currentRoute = []
        self.typeToRoute = None
        self.currRouteVolume = None
        selectedPin = self.eventManager.selectedPin
        if selectedPin:
            selectedPin.ShowHologramModel()

    def SetRouteWaypoint(self, childID):
        if childID in self.currentRoute:
            i = self.currentRoute.index(childID)
            path = self.currentRoute[i:]
            links = self.GetLinksFromPath(path)
            for l, id in links:
                l.RemoveAsRoute(id)

            self.currentRoute = self.currentRoute[:i + 1]
        else:
            lastWaypoint = self.currentRoute[-1]
            colony = self.planetUISvc.planet.GetColonyByPinID(lastWaypoint)
            shortestPath = colony.FindShortestPathIDs(lastWaypoint, childID)
            if not shortestPath:
                raise UserError('CreateRoutePathNotFound')
            self.currentRoute.extend(shortestPath[1:])
        self.routeHoverPath = []
        sm.GetService('audio').SendUIEvent('msg_pi_routes_waypoint_play')

    def _CleanRoute(self, route):
        pinIDSet = set(route)
        for pinID in pinIDSet:
            if pinID not in route:
                continue
            if route.count(pinID) > 1:
                firstPos = route.index(pinID)
                pos = lastPos = firstPos
                while True:
                    try:
                        pos = route.index(pinID, pos + 1)
                        lastPos = pos
                    except ValueError:
                        break

                deletedPath = route[firstPos:lastPos + 1]
                links = self.GetLinksFromPath(deletedPath)
                for l, id in links:
                    l.RemoveAsRoute(id)

                route = route[0:firstPos + 1] + route[lastPos + 1:]

    def GetPinGraphicsClassForType(self, typeID):
        if not evetypes.Exists(typeID):
            raise RuntimeError('Unable to find inventory type for typeID', typeID)
        groupID = evetypes.GetGroupID(typeID)
        if groupID == const.groupCommandPins:
            return CommandCenterPin
        if groupID == const.groupExtractorPins:
            return ExtractorPin
        if groupID == const.groupProcessPins:
            return ProcessorPin
        if groupID == const.groupSpaceportPins:
            return LaunchpadPin
        if groupID == const.groupStoragePins:
            return StorageFacilityPin
        if groupID == const.groupExtractionControlUnitPins:
            return EcuPin
        raise RuntimeError('Unable to resolve UI container class for pin of type', typeID)

    def RenderPins(self):
        if self.planetUISvc.planet.colony is None:
            return
        newPinData = self.planetUISvc.planet.colony.colonyData.pins
        newPinIDs = newPinData.keys()
        oldPinIDs = self.pinsByID.keys()
        pinsToDelete = [ pinID for pinID in oldPinIDs if pinID not in newPinIDs ]
        for pinID in pinsToDelete:
            pin = self.pinsByID.pop(pinID)
            pin.Remove()

        pinsToAdd = [ pinID for pinID in newPinIDs if pinID not in oldPinIDs ]
        for pinID in pinsToAdd:
            pin = newPinData[pinID]
            self.RenderPin(pin)

    def RenderPin(self, pin):
        if pin.id in self.pinsByID:
            self.pinsByID[pin.id].Remove()
        surfacePoint = SurfacePoint(phi=pin.latitude, theta=pin.longitude)
        pinClass = self.GetPinGraphicsClassForType(pin.typeID)
        UIpin = pinClass(surfacePoint, pin, self.planetUISvc.pinTransform)
        self.pinsByID[pin.id] = UIpin
        return UIpin

    def RenderLinks(self):
        self.ClearLinksFromScene()
        if session.charid not in self.planetUISvc.planet.colonies:
            return
        if self.planetUISvc.planet.colony is not None:
            for linkID, linkObj in self.planetUISvc.planet.colony.colonyData.links.iteritems():
                ep1ID, ep2ID = linkID
                self.AddLink(ep1ID, ep2ID, linkObj.typeID)

    def AddLink(self, parentID, childID, linkTypeID):
        colony = self.planetUISvc.planet.GetColony(session.charid)
        if colony is None:
            log.LogError('Unable to render link for planet without a colony')
            return
        par = colony.GetPin(parentID)
        child = colony.GetPin(childID)
        if par is None or child is None:
            log.LogWarn('Trying to render link for non-existing pin', parentID, childID)
            return
        p1 = SurfacePoint(theta=par.longitude, phi=par.latitude)
        p2 = SurfacePoint(theta=child.longitude, phi=child.latitude)
        planetLink = colony.colonyData.GetLink(parentID, childID)
        link = Link(p1, p2, parentID, childID, linkTypeID, planetLink)
        self.linksByPinIDs[parentID, childID] = link
        self.linksByPinIDs[childID, parentID] = link
        self.links.append(link)
        linkGraphicID1, linkGraphicID2 = link.GetGraphicIDs()
        self.linksByGraphicID[linkGraphicID1] = link
        self.linksByGraphicID[linkGraphicID2] = link

    def AddDepletionPoint(self, point):
        index = len(self.depletionPoints)
        self.depletionPoints.append(DepletionPin(point, index, self.planetUISvc.pinOthersTransform))

    def ClearPinsFromScene(self):
        for pin in self.pinsByID.values():
            pin.Remove()

        self.pinsByID = {}

    def ClearLinksFromScene(self):
        for link in self.links:
            link.Remove()

        self.planetUISvc.curveLineDrawer.ClearLines('links')
        self.planetUISvc.curveLineDrawer.ChangeLineSetWidth('rubberLink', 0.0)
        self.linksByPinIDs = {}
        self.links = []
        self.linksByGraphicID = {}

    def GetPinMenu(self, pinID):
        pin = self.pinsByID.get(pinID)
        if pin:
            return pin.GetMenu()

    def GetLinkMenu(self, linkGraphicID):
        if linkGraphicID in self.linksByGraphicID:
            link = self.linksByGraphicID[linkGraphicID]
            return link.GetMenu()

    def EndPlacingPin(self):
        self._RemoveBuildIndicatorPin()

    def _RemoveBuildIndicatorPin(self):
        if self.buildIndicatorPin is not None:
            self.buildIndicatorPin.Remove()
            self.buildIndicatorPin = None
        self.DisplayECUExtractionAreas(show=False)

    def DisplayECUExtractionAreas(self, show = True):
        for pin in self.pinsByID.values():
            if evetypes.GetGroupID(pin.pin.typeID) == const.groupExtractionControlUnitPins:
                if show:
                    pin.ShowMaxDistanceCircle()
                else:
                    pin.HideMaxDistanceCircle()

    def ShowECUExtractionAreas(self):
        for pin in self.pinsByID.values():
            if evetypes.GetGroupID(pin.typeID) == const.groupExtractionControlUnitPins:
                pin.ShowMaxDistanceCircle(1.0)

    def GetLinksFromPath(self, path):
        links = []
        last = None
        for pinID in path:
            if last is None:
                last = pinID
                continue
            id = (last, pinID)
            if id in self.linksByPinIDs:
                links.append((self.linksByPinIDs[id], id))
            else:
                log.LogWarn('Trying to fetch a non-existing link:', id)
            last = pinID

        return links

    def CreateRoute(self, amount = None):
        if self.oneoffRoute:
            self.planetUISvc.planet.OpenTransferWindow(self.currentRoute)
            self.planetUISvc.eventManager.DeselectCurrentlySelected()
        else:
            route = self.currentRoute
            links = self.GetLinksFromPath(self.currentRoute)
            typeToRoute = self.typeToRoute
            try:
                self.planetUISvc.planet.CreateRoute(self.currentRoute, self.typeToRoute, amount)
            except UserError:
                if self.currentRoute:
                    self.currentRoute = [self.currentRoute[0]]
                raise
            finally:
                for link, id in links:
                    link.RemoveAsRoute(id)

        sm.GetService('audio').SendUIEvent('msg_pi_routes_destination_play')
        self.currentRoute = []

    def UpdateRubberLink(self, surfacePoint):
        surfacePoint = GetPickIntersectionPoint(scale=planetConst.SCALE_RUBBERLINK)
        pin = self.pinsByID.get(self.linkParentID)
        if not pin:
            return
        if not surfacePoint:
            surfacePoint = pin.surfacePoint
        self.planetUISvc.curveLineDrawer.ChangeLinePosition('rubberLink', self.rubberLink, pin.surfacePoint, surfacePoint)
        self.UpdateRubberLinkLabels(pin.surfacePoint, surfacePoint)

    def GetCommandCenterPin(self):
        for p in self.pinsByID.values():
            if evetypes.GetGroupID(p.pin.typeID) == const.groupCommandPins:
                return p

    def GetPinsByGroupTypeIDs(self):
        pinsByGroupTypeID = defaultdict(list)
        for p in self.pinsByID.values():
            pinsByGroupTypeID[evetypes.GetGroupID(p.pin.typeID)].append(p)

        return pinsByGroupTypeID

    def UpdateRubberLinkLabels(self, surfacePointA, surfacePointB):
        self.rubberLinkLabelContainer.left = uicore.uilib.x + 3
        self.rubberLinkLabelContainer.top = uicore.uilib.y + 3
        if surfacePointA == surfacePointB:
            length = 0.0
        else:
            length = surfacePointA.GetDistanceToOther(surfacePointB) * self.planetUISvc.planet.radius
        self.rubberLinkLabels.distance.text = FmtDist(length)
        powerUsage = planetCommon.GetPowerUsageForLink(const.typeTestPlanetaryLink, length, 0, self.linkParams)
        cpuUsage = planetCommon.GetCpuUsageForLink(const.typeTestPlanetaryLink, length, 0, self.linkParams)
        self.rubberLinkLabels.power.text = localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=powerUsage)
        self.rubberLinkLabels.cpu.text = localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=cpuUsage)

    def OnRouteVolumeChanged(self, volume):
        self.currRouteVolume = volume
        for link, linkID in self.GetLinksFromPath(self.currentRoute):
            link.SetCurrentRouteVolume(volume)

    def DistanceToOtherPinsOK(self, surfacePoint):
        minDistance = 0.012
        for pin in self.pinsByID.values():
            if surfacePoint.GetDistanceToOther(pin.surfacePoint) < minDistance:
                return False

        return True

    def PlacePinOnNextClick(self, pinTypeID):
        self.eventManager.SetStateBuildPin()
        self._RemoveBuildIndicatorPin()
        self.newPinType = pinTypeID
        groupID = evetypes.GetGroupID(pinTypeID)
        self.buildIndicatorPin = BuildIndicatorPin(SurfacePoint(), pinTypeID, groupID, self.planetUISvc.pinOthersTransform)
        if groupID == const.groupExtractionControlUnitPins:
            self.DisplayECUExtractionAreas(show=True)

    def VerifySimulation(self):
        self.planetUISvc.planet.GMVerifySimulation()

    def HighlightLink(self, pinID, linkID, removeOld = True):
        link = self.linksByPinIDs[linkID]
        link.HighlightLink()

    def RemoveHighlightLink(self, linkID):
        self.linksByPinIDs[linkID].RemoveHighlightLink()

    def ShowRoute(self, routeID):
        route = self.planetUISvc.planet.colony.colonyData.GetRoute(routeID)
        path = route.path
        for link, linkID in self.GetLinksFromPath(path):
            link.ShowAsRoute(linkID, 1, 1)

    def StopShowingRoute(self, routeID):
        route = self.planetUISvc.planet.colony.colonyData.GetRoute(routeID)
        path = route.path
        for link, linkID in self.GetLinksFromPath(path):
            link.RemoveAsRoute(linkID)

    def GetCommandCenter(self):
        if not self.planetUISvc.planet:
            return None
        if not self.planetUISvc.planet.colony:
            return None
        if not self.planetUISvc.planet.colony.colonyData:
            return None
        return self.planetUISvc.planet.colony.colonyData.commandPin

    def RemovePin(self, pinID):
        self.planetUISvc.GetCurrentPlanet().RemovePin(pinID)
        pin = self.pinsByID.get(pinID, None)
        if pin:
            if pin.pin.IsCommandCenter():
                for p in self.pinsByID.values():
                    p.Remove()

                self.pinsByID = {}
                self.eventManager.SetStateNormal()
            else:
                pin.Remove()
                self.pinsByID.pop(pinID)
        self.RenderLinks()
        self.linkParentID = None
        self.eventManager.DeselectCurrentlySelected()

    def RemoveLink(self, linkID):
        link = self.linksByPinIDs[linkID]
        link.Remove()
        self.links.remove(link)
        self.planetUISvc.planet.RemoveLink(*linkID)
        self.RenderLinks()
        self.eventManager.DeselectCurrentlySelected()

    def UpgradeLink(self, *args):
        self.planetUISvc.planet.SetLinkLevel(*args)

    def InstallSchematic(self, pinID, schematicID):
        self.planetUISvc.planet.InstallSchematic(pinID, schematicID)
        pin = self.pinsByID[pinID]
        pin.OnRefreshPins()

    def RemoveRoute(self, routeID):
        route = self.planetUISvc.planet.colony.colonyData.GetRoute(routeID)
        if not route:
            return
        path = route.path
        self.planetUISvc.planet.RemoveRoute(routeID)
        for link, pinIDs in self.GetLinksFromPath(path):
            link.RenderAccordingToState()

    def PlacePin(self, surfacePoint):
        newPinType = self.newPinType
        return self.PlacePinType(surfacePoint, newPinType)

    def PlacePinType(self, surfacePoint, newPinType):
        if not self.DistanceToOtherPinsOK(surfacePoint):
            raise UserError('CannotBuildPinCloseToOthers')
        if not self or self.planetUISvc.planet is None:
            return
        self.planetUISvc.planet.CreatePin(newPinType, surfacePoint.phi, surfacePoint.theta)
        if evetypes.GetGroupID(newPinType) == const.groupCommandPins:
            sm.GetService('audio').SendUIEvent('msg_pi_build_command_play')
            self.eventManager.SetStateNormal()
        else:
            sm.GetService('audio').SendUIEvent('msg_pi_build_pin_play')

    def SetLinkChild(self, parentID, childID, setState = True):
        try:
            self.planetUISvc.planet.CreateLink(parentID, childID, const.typeTestPlanetaryLink)
            self.AddLink(childID, parentID, const.typeTestPlanetaryLink)
            sm.GetService('audio').SendUIEvent('msg_pi_build_link_play')
        finally:
            if setState:
                self.eventManager.SetStateCreateLinkStart()

    def EnterSurveyMode(self, ecuPinID):
        self.eventManager.SetStateSurvey()
        self.planetUISvc.GetSurveyWindow(ecuPinID)
        self.currentEcuPinID = ecuPinID
        ecuPin = self.pinsByID[ecuPinID]
        ecuPin.EnterSurveyMode()

    def LeaveSurveyMode(self):
        if self.currentEcuPinID is not None:
            ecuPin = self.pinsByID.get(self.currentEcuPinID, None)
            if ecuPin:
                ecuPin.ExitSurveyMode()
        self.currentEcuPinID = None
        self.planetUISvc.CloseSurveyWindow()

    def PlaceExtractionHead(self, ecuPinID, surfacePoint, headID = None):
        ecuPin = self.pinsByID[self.currentEcuPinID]
        if ecuPin.pin.IsActive():
            return
        headID = self.planetUISvc.planet.AddExtractorHead(ecuPinID, headID, surfacePoint.phi, surfacePoint.theta)
        ecuPin.AddHead(headID, surfacePoint)
        newHead = ecuPin.GetExtractionHead(headID)
        newHead.ShowUnlocked()
        wnd = SurveyWindow.GetIfOpen()
        if wnd:
            wnd.OnExtractionHeadAdded(headID, surfacePoint)

    def SetExtractionHeadRadius(self, ecuPinID, radius):
        ecuPin = self.pinsByID[ecuPinID]
        ecuPin.pin.headRadius = radius
        ecuPin.SetExtractionHeadRadius(radius)

    def RemoveExtractionHead(self, ecuPinID, headID):
        ecuPin = self.pinsByID[ecuPinID]
        if ecuPin.pin.IsActive():
            return
        self.planetUISvc.planet.RemoveExtractorHead(ecuPinID, headID)
        ecuPin.RemoveHead(headID)
        wnd = SurveyWindow.GetIfOpen()
        if wnd:
            wnd.OnExtractionHeadRemoved(headID)

    def BeginDragExtractionHead(self, ecuPinID, headID):
        if ecuPinID != self.currentEcuPinID:
            return
        ecuPin = self.pinsByID[ecuPinID]
        if ecuPinID != self.canMoveHeads:
            return
        self.extractionHeadDragged = (ecuPin, headID)
        self.eventManager.SetSubStateMoveExtractionHead()
        surfacePoint = ecuPin.GetExtractionHead(headID).surfacePoint
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnBeginDragExtractionHead(headID, surfacePoint)

    def DragExtractionHeadTo(self, surfacePoint):
        ecuPin, headID = self.extractionHeadDragged
        distanceFactor = self._EnforceMaximumDinstance(surfacePoint, ecuPin)
        ecuPin.SetDistanceFactor(distanceFactor)
        ecuPin.MoveExtractionHeadTo(headID, surfacePoint)
        wnd = SurveyWindow.GetIfOpen()
        if wnd:
            wnd.OnExtractionHeadMoved(headID, surfacePoint)

    def IsDraggingExtractionHead(self):
        return bool(self.extractionHeadDragged)

    def _EnforceMaximumDinstance(self, headSurfacePoint, uiPin):
        SAFETYFACTOR = 0.99
        ecuSurfacePoint = uiPin.surfacePoint
        distance = headSurfacePoint.GetDistanceToOther(ecuSurfacePoint)
        areaOfInfluence = uiPin.pin.GetAreaOfInfluence()
        if distance < areaOfInfluence * SAFETYFACTOR:
            return distance / areaOfInfluence
        ecuVector = ecuSurfacePoint.GetAsXYZTuple()
        v = headSurfacePoint.GetAsXYZTuple()
        normal = geo2.Vec3Cross(ecuVector, v)
        rotMat = geo2.MatrixRotationAxis(normal, areaOfInfluence * SAFETYFACTOR)
        newV = geo2.Multiply(rotMat, ecuVector)
        headSurfacePoint.SetXYZ(*newV[:3])
        return 1.0

    def EndDragExtractionHead(self):
        uiPin, headID = self.extractionHeadDragged
        headPin = uiPin.extractionHeadsByNum[headID]
        self._EnforceMaximumDinstance(headPin.surfacePoint, uiPin)
        sm.GetService('planetUI').GetCurrentPlanet().MoveExtractorHead(uiPin.pin.id, headID, headPin.surfacePoint.phi, headPin.surfacePoint.theta)
        self.extractionHeadDragged = None
        self.eventManager.SetSubStateNormal()
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnEndDragExtractionHead()

    def OnExtractionHeadMouseEnter(self, ecuPinID, headID):
        if ecuPinID != self.currentEcuPinID:
            return
        ecuPin = self.pinsByID[ecuPinID]
        if ecuPinID != self.canMoveHeads:
            return
        head = ecuPin.GetExtractionHead(headID)
        if head:
            head.OnMouseEnter()
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnHeadEntryMouseEnter(headID)

    def OnExtractionHeadMouseExit(self, ecuPinID, headID):
        if ecuPinID != self.currentEcuPinID:
            return
        ecuPin = self.pinsByID[ecuPinID]
        head = ecuPin.GetExtractionHead(headID)
        if head:
            head.OnMouseExit()
        wnd = self.planetUISvc.GetSurveyWindow(self.currentEcuPinID)
        wnd.OnHeadEntryMouseExit(headID)

    def SetEcuOverlapValues(self, ecuPinID, overlapVals):
        ecuPin = self.pinsByID.get(ecuPinID, None)
        if ecuPin:
            ecuPin.SetOverlapValues(overlapVals)

    def UnlockHeads(self, pinID):
        self.canMoveHeads = pinID
        ecuPin = self.pinsByID.get(pinID, None)
        if ecuPin:
            ecuPin.OnHeadsUnlocked()

    def LockHeads(self):
        ecuPin = self.pinsByID.get(self.canMoveHeads, None)
        self.canMoveHeads = None
        if ecuPin:
            ecuPin.OnHeadsLocked()

    def GMRunDepletionSim(self, totalDuration):
        points = []
        for point in self.depletionPoints:
            points.append(utillib.KeyVal(longitude=point.surfacePoint.theta, latitude=point.surfacePoint.phi, amount=point.GetAmount(), duration=point.GetDuration(), headRadius=point.GetHeadRadius()))

        info = utillib.KeyVal(totalDuration=totalDuration, points=points)
        sm.GetService('planetUI').GetCurrentPlanet().GMRunDepletionSim(self.planetUISvc.selectedResourceTypeID, info)

    def GetMultiPinMenu(self, currentPin):
        selectedPinIDs = self.eventManager.selectedPinIDs
        if currentPin.pin.id not in selectedPinIDs:
            selectedPinIDs.add(currentPin.pin.id)
            currentPin.SetMultiSelectedDisplay(True)
        pins = [ self.planetUISvc.planet.GetPin(x) for x in selectedPinIDs ]
        mp = MultiPinMenuProvider(self.InstallSchematicForMultiplePins)
        return mp.GetMenu(pins)

    def InstallSchematicForMultiplePins(self, schematicID, pins):
        resultsByPinID = self._GetRouteToDeleteAndNewRouteData(schematicID, pins)
        outputRouteFailures = defaultdict(list)
        inputRouteFailures = defaultdict(list)
        for pID, results in resultsByPinID.iteritems():
            self.InstallSchematic(pID, schematicID)
            for routeID in results.outputRouteIDsToDelete.union(results.inputRouteIDsToDelete):
                self.RemoveRoute(routeID)

            for routeInfo, errorDict in ((results.newOutputRouteData, outputRouteFailures), (results.newInputRouteData, inputRouteFailures)):
                for typeID, qty, path in routeInfo:
                    try:
                        self.planetUISvc.planet.CreateRoute(path, typeID, qty)
                    except UserError:
                        errorDict[typeID].append(path)

        if outputRouteFailures or inputRouteFailures:
            self._DisplayRouteFailureMessage(outputRouteFailures, inputRouteFailures)

    def _DisplayRouteFailureMessage(self, outputRouteFailures, inputRouteFailures):
        colony = self.eventManager.GetColony()
        infoTextList = []
        for routeFailures, headerText in ((outputRouteFailures, localization.GetByLabel('UI/PI/FailedToCreateOutgoingRoutes')), (inputRouteFailures, localization.GetByLabel('UI/PI/FailedToCreateIncomingRoutes'))):
            if not routeFailures:
                continue
            infoTextList.append(headerText)
            for typeID, failedRoutePaths in routeFailures.iteritems():
                infoTextList.append(u'\u2022 %s' % type_link(typeID))
                for path in failedRoutePaths:
                    sourcePinID, destPinID = path
                    sourcePin = colony.GetPin(sourcePinID)
                    if sourcePin is None:
                        continue
                    destPin = colony.GetPin(destPinID)
                    if destPin is None:
                        continue
                    sourcePinName = GetPinNameShort(sourcePin.typeID, sourcePinID)
                    destPinName = GetPinNameShort(destPin.typeID, destPinID)
                    text = '<t>%s => %s' % (sourcePinName, destPinName)
                    infoTextList.append(text)

        infoText = '<br>'.join(infoTextList)
        eve.Message('CustomInfo', {'info': infoText}, modal=False)

    def _GetRouteToDeleteAndNewRouteData(self, schematicID, pins):
        colony = self.eventManager.GetColony()
        return GetRouteToDeleteAndNewRouteData(schematicID, pins, GetSchematicDataForID, colony.colonyData.GetSourceRoutesForPin, self.GetDestRoutesForPin)

    def GetDestRoutesForPin(self, pinID):
        colony = self.eventManager.GetColony()
        routesIDsTo = colony.colonyData.GetDestinationRoutesForPin(pinID)
        return [ colony.GetRoute(routeID) for routeID in routesIDsTo ]
