#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelRoute.py
import random
import weakref
from collections import deque
import eveformat
import evelink.client
import localization
import log
import threadutils
import uthread
import uthread2
import utillib
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import timerstuff
from carbonui import uiconst, TextColor
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.shared.autopilotSettings import AutopilotSettings
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.util import searchUtil, uix
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst, infoPanelUIConst
from eve.common.lib import appConst as const
from eve.common.script.search.const import ResultType
from eve.common.script.sys import eveCfg, idCheckers
from evePathfinder.pathfinderconst import ROUTE_TYPE_SAFE, ROUTE_TYPE_SHORTEST, ROUTE_TYPE_UNSAFE
from eveformat.client.location import GetLawlessSystemSecStatusColor
from eveservices.menu import GetMenuService
from pirateinsurgency.client.dashboard.const import CORRUPTION_STAGES
from stackless_response_router.exceptions import TimeoutException, UnpackException
from stargate.client.localGates import FindLocalStargate
from uihider import UiHiderMixin
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
ROUTE_MARKERSIZE = 8
ROUTE_MARKERGAP = 2
ROUTE_MARKERTYPE_NORMAL = 0
ROUTE_MARKERTYPE_STATION = 1
ROUTE_MARKERTYPE_WAYPOINT = 2
ROUTE_MARKERTYPE_INVASION = 3
ROUTE_MARKERTYPE_INSURGENCY = 4
NEOCOM_PANELWIDTH = 328
FRAME_WIDTH = 20
FRAME_SEPERATION = 10
IDLE_ROUTEMARKER_ALPHA = 1.0

def _GetCurrentDestinationLabel(destination_name):
    if destination_name is None:
        return localization.GetByLabel('UI/Inflight/NoDestination')
    destination_label = localization.GetByLabel('UI/Neocom/Autopilot/CurrentDestination')
    return sm.GetService('infoPanel').GetSolarSystemTrace(destination_name, destination_label)


class InfoPanelRoute(UiHiderMixin, InfoPanelBase):
    default_name = 'InfoPanelRoute'
    panelTypeID = infoPanelConst.PANEL_ROUTE
    label = 'UI/InfoWindow/TabNames/Route'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/Route.png'
    hasSettings = True
    uniqueUiName = pConst.UNIQUE_NAME_INFO_PANEL_ROUTE
    __notifyevents__ = ['OnDestinationSet',
     'OnUIRefresh',
     'OnAutoPilotOn',
     'OnAutoPilotOff']

    def ApplyAttributes(self, attributes):
        super(InfoPanelRoute, self).ApplyAttributes(attributes)
        self.headerButton.uniqueUiName = pConst.UNIQUE_NAME_AUTOPILOT_SETTINGS
        sm.RegisterNotify(self)
        self.routeData = None
        self.sliderLabel = None
        self.toAnimate = []
        self.utilMenu = None
        self.header = self.headerCls(parent=self.headerCont, align=uiconst.CENTERLEFT)
        self.headerCompact = self.headerCls(name='headerCompact', parent=self.headerCompactCont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.headerTrigIcon = TriglavianWarningIcon(parent=self.headerCompactCont, align=uiconst.CENTERRIGHT, idx=0)
        self.UpdateHeaderTrigIconDisplay()
        self.noDestinationLabel = eveLabel.EveLabelMedium(name='noDestinationLabel', parent=self.mainCont, text=localization.GetByLabel('UI/Inflight/NoDestination'), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        self.currentParent = NextWaypointPanel(parent=self.mainCont, align=uiconst.TOTOP)
        self.markersParent = Container(name='markersParent', parent=self.mainCont, align=uiconst.TOTOP)
        self.endParent = DestinationWaypointPanel(parent=self.mainCont, align=uiconst.TOTOP)

    def GetSettingsMenu(self, parent):
        self.utilMenu = weakref.ref(parent)
        self.AddSearchBox(parent)
        parent.AddCheckBox(localization.GetByLabel('UI/Map/MapPallet/AutopilotActive'), sm.GetService('autoPilot').GetState(), callback=self.OnCheckBoxAutopilotActive, state=uiconst.UI_DISABLED if eveCfg.IsDocked() else uiconst.UI_NORMAL)
        parent.AddCheckBox(localization.GetByLabel('UI/Map/MapPallet/ShowRoutePathInSpace'), settings.user.ui.Get('routeVisualizationEnabled', True), callback=sm.GetService('gameui').routeVisualizer.ToggleRouteVisualization)
        pfRouteType = sm.GetService('clientPathfinderService').GetAutopilotRouteType()
        parent.AddRadioButton(localization.GetByLabel('UI/Map/MapPallet/cbPreferShorter'), pfRouteType == ROUTE_TYPE_SHORTEST, callback=(self.OnRadioBtnRouteType, 'shortest'), uniqueUiName=pConst.UNIQUE_NAME_ROUTE_SHORTER)
        parent.AddRadioButton(localization.GetByLabel('UI/Map/MapPallet/cbPreferSafer'), pfRouteType == ROUTE_TYPE_SAFE, callback=(self.OnRadioBtnRouteType, 'safe'), uniqueUiName=pConst.UNIQUE_NAME_ROUTE_SAFER)
        parent.AddRadioButton(localization.GetByLabel('UI/Map/MapPallet/cbPreferRisky'), pfRouteType == ROUTE_TYPE_UNSAFE, callback=(self.OnRadioBtnRouteType, 'unsafe'))
        sliderCont = Container(name='sliderCont', parent=parent, align=uiconst.TOTOP, height=18, padding=(17, 0, 0, 0))
        self.securitySlider = Slider(parent=sliderCont, align=uiconst.TOLEFT, width=100, name='pfPenalty', state=uiconst.UI_NORMAL, minValue=1, maxValue=100, labelDecimalPlaces=0, value=settings.char.ui.Get('pfPenalty', 50.0), on_dragging=self.OnSecuritySlider, callback=self.OnSecuritySliderEnd, hint=localization.GetByLabel('UI/Map/MapPallet/hintSecurityPeneltySlider'), padLeft=5)
        self.sliderLabel = eveLabel.EveLabelSmall(parent=sliderCont, align=uiconst.TOALL, padLeft=5, top=3)
        self.UpdateSliderLabel(self.securitySlider.value)
        parent.AddSpace()
        parent.AddCheckBox(localization.GetByLabel('UI/Map/MapPallet/IncludeJumpGates'), settings.char.ui.Get('pathFinder_includeJumpGates', 0), callback=self.OnCheckBoxUseJumpGates, uniqueUiName=pConst.UNIQUE_NAME_ROUTE_INCLUDE_JUMP_GATES)
        parent.AddCheckBox(localization.GetByLabel('UI/Map/MapPallet/cbAdvoidPodkill'), settings.char.ui.Get('pfAvoidPodKill', 0), callback=self.OnCheckBoxAvoidPodKill)
        parent.AddCheckBox(localization.GetByLabel('UI/Map/MapPallet/cbAvoidTriglavianTales'), settings.char.ui.Get('pfAvoidTriglavianTales', 0), callback=self.OnCheckBoxAvoidTriglavianTales)
        parent.AddCheckBox(localization.GetByLabel('UI/Map/MapPallet/cbAvoidEdencomSystems'), settings.char.ui.Get('pfAvoidEdencomSystems', 0), callback=self.OnCheckBoxAvoidEdencomSystems)
        parent.AddCheckBox(localization.GetByLabel('UI/Map/MapPallet/cbAdvoidSystemsOnList'), settings.char.ui.Get('pfAvoidSystems', 1), callback=self.OnCheckBoxAvoidSystems)
        parent.AddCheckBox(localization.GetByLabel('UI/Map/MapPallet/cbDisableAtEachWaypoint'), settings.user.ui.Get('autopilot_stop_at_each_waypoint', 0) == 0, callback=self.OnCheckBoxDisableAtEachWaypoint)
        parent.AddDivider()
        starmapSvc = sm.GetService('starmap')
        waypoints = starmapSvc.GetWaypoints()
        if len(waypoints) > 0:
            parent.AddButton(localization.GetByLabel('UI/Neocom/ClearAllAutopilotWaypoints'), starmapSvc.ClearWaypoints, toggleMode=False)
        if len(waypoints) > 1:
            parent.AddButton(localization.GetByLabel('UI/Map/MapPallet/OptimizeRoute'), sm.GetService('autoPilot').OptimizeRoute, toggleMode=False)
        parent.AddButton(localization.GetByLabel('UI/Map/MapPallet/ManageRoute'), AutopilotSettings.Open, toggleMode=False)

    def AddSearchBox(self, parent):
        container = parent.AddContainer(padding=6)
        inpt = SingleLineEditText(name='searchbox', parent=container, align=uiconst.TOPLEFT, width=220, maxLength=64, hintText=localization.GetByLabel('UI/Map/MapPallet/lblSearchForLocation'), OnReturn=lambda *args: self.SearchForLocation(inpt, container, *args))
        Button(parent=container, align=uiconst.TOPLEFT, left=inpt.width + 4, label=localization.GetByLabel('UI/Map/MapPallet/btnSearchForLocation'), func=self.SearchForLocation, args=(inpt, container))
        parent.AddDivider()

    def SearchForLocation(self, inputField, container, *args):
        searchText = inputField.GetValue().strip()
        groupIDList = [ResultType.solar_system,
         ResultType.constellation,
         ResultType.region,
         ResultType.station,
         ResultType.structure_with_inlined_data]
        searchUtil.GetResultsInNewWindow(searchText, groupIDList, searchWndName='addressBookSearch')
        container.parent.Close()

    def OnRadioBtnRouteType(self, routeType):
        sm.GetService('clientPathfinderService').SetAutopilotRouteType(routeType)

    def OnCheckBoxAutopilotActive(self):
        if eveCfg.IsDocked():
            return
        autoPilotSvc = sm.GetService('autoPilot')
        if autoPilotSvc.GetState():
            autoPilotSvc.SetOff()
        else:
            autoPilotSvc.SetOn()

    def OnCheckBoxShowRoutePath(self):
        pass

    def OnCheckBoxAvoidPodKill(self):
        val = not settings.char.ui.Get('pfAvoidPodKill', 0)
        if val:
            eve.Message('MapAutoPilotAvoidPodkillZones')
        sm.GetService('clientPathfinderService').SetPodKillAvoidance(val)

    def OnCheckBoxAvoidTriglavianTales(self):
        val = not settings.char.ui.Get('pfAvoidTriglavianTales', 0)
        if val:
            eve.Message('MapAutoPilotAvoidTriglavianTales')
        sm.GetService('clientPathfinderService').SetTriglavianTaleAvoidance(val)

    def OnCheckBoxAvoidEdencomSystems(self):
        val = not settings.char.ui.Get('pfAvoidEdencomSystems', 0)
        if val:
            eve.Message('MapAutoPilotAvoidEdencomSystems')
        sm.GetService('clientPathfinderService').SetEdencomSystemsAvoidance(val)

    def OnCheckBoxAvoidSystems(self):
        val = not settings.char.ui.Get('pfAvoidSystems', 0)
        if val:
            eve.Message('MapAutoPilotAvoidSystems')
        sm.GetService('clientPathfinderService').SetSystemAvoidance(val)

    def OnCheckBoxDisableAtEachWaypoint(self):
        val = not settings.user.ui.Get('autopilot_stop_at_each_waypoint', 0)
        settings.user.ui.Set('autopilot_stop_at_each_waypoint', val)

    def OnCheckBoxUseJumpGates(self):
        val = not settings.char.ui.Get('pathFinder_includeJumpGates', 0)
        settings.char.ui.Set('pathFinder_includeJumpGates', val)
        sm.ScatterEvent('OnMapShowsJumpGatesChanged')

    def OnSecuritySlider(self, slider):
        self.UpdateSliderLabel(slider.value)

    def OnSecuritySliderEnd(self, slider):
        sm.GetService('clientPathfinderService').SetSecurityPenaltyFactor(slider.value)
        self.UpdateSliderLabel(slider.value)

    def UpdateSliderLabel(self, value):
        if self.sliderLabel:
            self.sliderLabel.text = '%s %i' % (localization.GetByLabel('UI/Map/MapPallet/lblSecurityPenelity'), value)

    def ConstructNormal(self):
        self.UpdateRoute()

    def ConstructCompact(self):
        self.UpdateHeaderText()
        self.UpdateHeaderTrigIconDisplay()

    def UpdateHeaderTrigIconDisplay(self):
        starMapSvc = sm.GetService('starmap')
        nextDestination = None
        if self.routeData is None:
            self.routeData = starMapSvc.GetAutopilotRoute()
            if not self.routeData or self.routeData == [None]:
                self.routeData = starMapSvc.GetWaypoints()
        try:
            if len(self.routeData):
                nextDestination = self.routeData[0]
        except KeyError:
            self.headerTrigIcon.display = False
            return

        should_display_trig_warning = ShowTriglavianWarning(nextDestination)
        self.headerTrigIcon.display = should_display_trig_warning
        header_label_width = infoPanelUIConst.PANELWIDTH - infoPanelUIConst.LEFTPAD
        if should_display_trig_warning:
            header_label_width -= self.headerTrigIcon.width
        self.headerCompact.SetRightAlphaFade(header_label_width, self.HEADER_FADE_WIDTH)

    def OnDestinationSet(self, destination):
        self.UpdateRoute(animate=bool(destination))

    def UpdateRoute(self, animate = False):
        starMapSvc = sm.GetService('starmap')
        self.routeData = starMapSvc.GetAutopilotRoute()
        self.UpdateHeaderText()
        if not session.solarsystemid2:
            return
        if self.mode != infoPanelConst.MODE_NORMAL:
            return
        if not self.routeData or self.routeData == [None]:
            self.routeData = starMapSvc.GetWaypoints()
        if not self.routeData:
            if self.markersParent:
                self.currentParent.Hide()
                self.endParent.Hide()
                self.markersParent.Hide()
            self.noDestinationLabel.Show()
            return
        self.noDestinationLabel.Hide()
        planetView = sm.GetService('viewState').IsViewActive('planet')
        autoPilotActive = sm.GetService('autoPilot').GetState()
        updatingRouteData = getattr(self, 'updatingRouteData', None)
        if updatingRouteData == (autoPilotActive, planetView, self.routeData):
            return
        oldRouteIDs = [ child.solarSystemID for child in self.markersParent.children ]
        self.toAnimate = []
        self.markersParent.Flush()
        self.updatingRouteData = (autoPilotActive, planetView, self.routeData[:])
        self.currentParent.Show()
        self.currentParent.item_id = self.routeData[0]
        self.markersParent.Show()
        routeIDs = []
        lastStationSystemID = None
        for i, id in enumerate(self.routeData):
            isLast = i == len(self.routeData) - 1
            if idCheckers.IsSolarSystem(id) and not isLast and not idCheckers.IsSolarSystem(self.routeData[i + 1]):
                continue
            if idCheckers.IsSolarSystem(id) and lastStationSystemID == id:
                continue
            if idCheckers.IsStation(id):
                lastStationSystemID = cfg.stations.Get(id).solarSystemID
            else:
                lastStationSystemID = None
            routeIDs.append(id)

        maxWidth = infoPanelUIConst.PANELWIDTH - self.mainCont.padLeft
        markerX = 0
        markerY = 0
        waypoints = deque(sm.GetService('starmap').GetWaypoints())
        nextWaypoint = waypoints.popleft() if waypoints else None
        lastSystemID = session.solarsystemid2
        systemsIDsInRoute = []
        for i, destinationID in enumerate(routeIDs):
            if destinationID == nextWaypoint:
                isWaypoint = True
                nextWaypoint = waypoints.popleft() if waypoints else None
            else:
                isWaypoint = False
            if idCheckers.IsSolarSystem(destinationID):
                isStation = False
                solarSystemID = destinationID
            elif idCheckers.IsStation(destinationID):
                isStation = True
                solarSystemID = cfg.stations.Get(destinationID).solarSystemID
            else:
                structure = sm.GetService('structureDirectory').GetStructureInfo(destinationID)
                if structure is not None:
                    isStation = True
                    solarSystemID = structure.solarSystemID
                else:
                    log.LogError('ConstructRoute: Unknown item. I can only handle solar systems, stations and structures. You gave me', destinationID)
                    continue
            if solarSystemID != lastSystemID:
                systemsIDsInRoute.append(solarSystemID)
                lastSystemID = solarSystemID
            if len(self.markersParent.children) > i:
                systemIcon = self.markersParent.children[i]
                systemIcon.left = markerX
                systemIcon.top = markerY
                systemIcon.numJumps = len(systemsIDsInRoute)
            else:
                systemIcon = AutopilotDestinationIcon(parent=self.markersParent, pos=(markerX,
                 markerY,
                 ROUTE_MARKERSIZE,
                 ROUTE_MARKERSIZE), solarSystemID=solarSystemID, destinationID=destinationID, idx=i, numJumps=len(systemsIDsInRoute))
                if i >= len(oldRouteIDs) or solarSystemID != oldRouteIDs[i]:
                    self.toAnimate.append(systemIcon)
            if isStation:
                systemIcon.SetMarkerType(ROUTE_MARKERTYPE_STATION)
            elif isWaypoint:
                systemIcon.SetMarkerType(ROUTE_MARKERTYPE_WAYPOINT)
            elif ShowTriglavianWarning(destinationID):
                systemIcon.SetMarkerType(ROUTE_MARKERTYPE_INVASION)
            else:
                systemIcon.SetMarkerType(ROUTE_MARKERTYPE_NORMAL)
            systemIcon.SetSolarSystemAndDestinationID(solarSystemID, destinationID)
            self.endParent.pointer_offset = markerX
            markerParHeight = markerY + ROUTE_MARKERSIZE + ROUTE_MARKERGAP
            if animate:
                animations.MorphScalar(self.markersParent, 'height', self.markersParent.height, markerParHeight, duration=0.3)
            else:
                self.markersParent.height = markerParHeight
            markerX += ROUTE_MARKERGAP + ROUTE_MARKERSIZE
            if markerX + ROUTE_MARKERSIZE > maxWidth:
                markerX = 0
                markerY += ROUTE_MARKERGAP + ROUTE_MARKERSIZE
            if len(routeIDs) > 1:
                self.endParent.Show()
                self.endParent.item_id = routeIDs[-1]
            else:
                self.endParent.Hide()

        self.updatingRouteData = None
        if animate:
            uthread.new(self.AnimateRouteIn)
        self.UpdateHeaderTrigIconDisplay()

    def UpdateHeaderText(self):
        starMapSvc = sm.GetService('starmap')
        destination = starMapSvc.GetDestination()
        routeData = starMapSvc.GetAutopilotRoute()
        if self.mode == infoPanelConst.MODE_NORMAL:
            numJumps = self._GetNumJumps(routeData)
            if not destination:
                subHeader = ''
            elif idCheckers.IsWormholeSystem(session.solarsystemid2) or idCheckers.IsAbyssalSpaceSystem(session.solarsystemid2) or idCheckers.IsVoidSpaceSystem(session.solarsystemid2):
                if numJumps <= 1:
                    subHeader = localization.GetByLabel('UI/Market/MarketQuote/UnknownNumberOfJumps')
                else:
                    subHeader = localization.GetByLabel('UI/Market/MarketQuote/MinimumPossibleNumberOfJumps', num=numJumps)
            else:
                subHeader = localization.GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=numJumps)
            self.header.text = '%s <fontsize=12>%s' % (localization.GetByLabel('UI/InfoWindow/TabNames/Route'), subHeader)
        elif routeData:
            self.headerCompact.text = _GetCurrentDestinationLabel(routeData[0])
        else:
            destination = starMapSvc.GetDestination()
            self.headerCompact.text = _GetCurrentDestinationLabel(destination)

    def OnStartModeChanged(self, oldMode):
        uthread.new(self._OnStartModeChanged, oldMode)

    def _OnStartModeChanged(self, oldMode):
        if self.mode == infoPanelConst.MODE_NORMAL:
            if oldMode:
                animations.FadeOut(self.headerCompactCont, duration=0.3, sleep=True)
                animations.FadeIn(self.headerCont, duration=0.3)
            else:
                self.headerCont.opacity = 1.0
                self.headerCompactCont.opacity = 0.0
            self.headerCompactCont.state = uiconst.UI_DISABLED
        elif self.mode == infoPanelConst.MODE_COMPACT:
            if oldMode:
                animations.FadeOut(self.headerCont, duration=0.3, sleep=True)
                animations.FadeIn(self.headerCompactCont, duration=0.3)
            else:
                self.headerCont.opacity = 0.0
                self.headerCompactCont.opacity = 1.0
            self.headerCompactCont.state = uiconst.UI_PICKCHILDREN

    def AnimateRouteIn(self):
        if not self.toAnimate:
            return
        random.shuffle(self.toAnimate)
        kOffset = 0.6 / len(self.toAnimate)
        for i, icon in enumerate(self.toAnimate):
            animations.SpMaskIn(icon.icon, timeOffset=i * kOffset, loops=3, duration=0.05)

    def _GetNumJumps(self, routeData):
        if not routeData:
            return 0
        ids = []
        lastID = None
        for routeID in routeData:
            if idCheckers.IsStation(routeID):
                routeID = cfg.stations.Get(routeID).solarSystemID
            if routeID != lastID and idCheckers.IsSolarSystem(routeID):
                ids.append(routeID)
            lastID = routeID

        numJumps = len(ids)
        if ids and ids[0] == session.solarsystemid2:
            numJumps -= 1
        return numJumps

    def OnUIRefresh(self):
        self.UpdateRoute()

    def OnAutoPilotOn(self):
        if self.utilMenu and self.utilMenu():
            self.utilMenu().ReloadMenu()

    def OnAutoPilotOff(self):
        if self.utilMenu and self.utilMenu():
            self.utilMenu().ReloadMenu()


class AutopilotDestinationIcon(Container):
    __guid__ = 'uicls.AutopilotDestinationIcon'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    isDragObject = True
    default_pointerDirection = uiconst.POINT_BOTTOM_2

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.icon = Sprite(parent=self, pos=(0, 0, 10, 10), state=uiconst.UI_DISABLED, shadowOffset=(0, 1), shadowColor=(0, 0, 0, 0.2), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0)
        self.markerType = None
        self.solarSystemID = None
        self.destinationID = None
        self.hiliteTimer = None
        self.fadingDisabled = False
        self.lawless = False
        self.numJumps = attributes.numJumps

    def SetMarkerType(self, markerType):
        if self.markerType == markerType:
            return
        if markerType == ROUTE_MARKERTYPE_WAYPOINT:
            self.icon.LoadTexture('res:/UI/Texture/classes/LocationInfo/waypointMarker.png')
        elif markerType == ROUTE_MARKERTYPE_STATION:
            self.icon.LoadTexture('res:/UI/Texture/classes/LocationInfo/stationMarker.png')
        elif markerType == ROUTE_MARKERTYPE_INVASION:
            self.icon.LoadTexture('res:/UI/Texture/classes/LocationInfo/triglavianMarker.png')
        elif markerType == ROUTE_MARKERTYPE_INSURGENCY:
            self.icon.LoadTexture('res:/UI/Texture/classes/LocationInfo/triglavianMarker.png')
        else:
            self.icon.LoadTexture('res:/UI/Texture/classes/LocationInfo/normalMarker.png')
        self.markerType = markerType

    def SetSolarSystemAndDestinationID(self, solarSystemID, destinationID):
        if self.solarSystemID == solarSystemID and self.destinationID == destinationID:
            return
        self.icon.SetRGBA(*eveColor.GUNMETAL_GREY)
        animations.MorphScalar(self.icon, 'opacity', 1.0, 0.0, duration=1, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE, timeOffset=random.random())
        self.solarSystemID = solarSystemID
        self.destinationID = destinationID
        uthread2.StartTasklet(self.UpdateLawlessStatus, solarSystemID)

    def UpdateLawlessStatus(self, solarSystemID):
        c = sm.GetService('map').GetModifiedSystemColor(solarSystemID)
        try:
            corruptionStage = sm.GetService('corruptionSuppressionSvc').GetSystemCorruptionStage(solarSystemID)
        except (TimeoutException, UnpackException):
            corruptionStage = 0

        if corruptionStage == CORRUPTION_STAGES:
            self.lawless = True
        if self.lawless:
            secStatus = sm.GetService('map').GetSecurityStatus(solarSystemID)
            c = GetLawlessSystemSecStatusColor(secStatus)
            if self.markerType == ROUTE_MARKERTYPE_NORMAL:
                self.SetMarkerType(ROUTE_MARKERTYPE_INSURGENCY)
        animations.StopAnimation(self.icon, 'opacity')
        self.icon.SetRGBA(c[0], c[1], c[2], IDLE_ROUTEMARKER_ALPHA)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if self.fadingDisabled:
            return
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 0.5, duration=uiconst.TIME_ENTRY)
        if self.hiliteTimer is None:
            self.hiliteTimer = timerstuff.AutoTimer(111, self.CheckIfMouseOver)

    def CheckIfMouseOver(self, *args):
        if uicore.uilib.mouseOver == self or self.fadingDisabled:
            return
        animations.MorphScalar(self.icon, 'glowBrightness', self.icon.glowBrightness, 0.0, duration=uiconst.TIME_ENTRY)
        self.hiliteTimer = None

    def OnMouseExit(self, *args):
        self.CheckIfMouseOver()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        if self.lawless:
            traceText = sm.GetService('infoPanel').GetLawlessSolarSystemTrace(self.destinationID, traceFontSize=None)
        else:
            traceText = sm.GetService('infoPanel').GetSolarSystemTrace(self.destinationID, traceFontSize=None)
        tooltipPanel.AddTextBodyLabel(text=traceText)
        if not idCheckers.IsSolarSystem(self.destinationID):
            if idCheckers.IsStation(self.destinationID) or sm.GetService('structureDirectory').GetStructureInfo(self.destinationID):
                text = cfg.evelocations.Get(self.destinationID).name
                tooltipPanel.AddTextBodyLabel(text=text)
        if ShowTriglavianWarning(self.solarSystemID):
            text = localization.GetByLabel('UI/Invasion/HUD/InvasionWarning')
            tooltipPanel.AddTextBodyLabel(text=text)
        if self.numJumps:
            text = localization.GetByLabel('UI/Common/numberOfJumps', numJumps=self.numJumps)
            tooltipPanel.AddTextDetailsLabel(text=text, color=TextColor.SECONDARY)

    def GetMenu(self, *args):
        if idCheckers.IsSolarSystem(self.destinationID):
            return GetMenuService().GetMenuFromItemIDTypeID(self.destinationID, const.typeSolarSystem)
        typeID = self.GetStationOrStructureTypeID(self.destinationID)
        if typeID:
            return GetMenuService().GetMenuFromItemIDTypeID(self.destinationID, typeID)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if idCheckers.IsSolarSystem(self.destinationID):
            sm.GetService('info').ShowInfo(const.typeSolarSystem, self.destinationID)
        typeID = self.GetStationOrStructureTypeID(self.destinationID)
        if typeID:
            sm.GetService('info').ShowInfo(typeID, self.destinationID)

    def GetDragData(self, *args):
        entry = utillib.KeyVal()
        entry.__guid__ = 'xtriui.ListSurroundingsBtn'
        entry.itemID = self.destinationID
        entry.label = cfg.evelocations.Get(self.destinationID).name
        if idCheckers.IsSolarSystem(self.destinationID):
            entry.typeID = const.typeSolarSystem
        else:
            typeID = self.GetStationOrStructureTypeID(self.destinationID)
            if typeID:
                entry.typeID = typeID
        return [entry]

    def GetStationOrStructureTypeID(self, destinationID):
        if idCheckers.IsStation(self.destinationID):
            station = sm.StartService('ui').GetStationStaticInfo(self.destinationID)
            return station.stationTypeID
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(self.destinationID)
        if structureInfo:
            return structureInfo.typeID

    def OnMouseDown(self, *args):
        uthread.new(self.OnMouseDown_thread)

    def OnMouseDown_thread(self):
        destinationID = self.destinationID
        if idCheckers.IsSolarSystem(destinationID):
            typeID = const.typeSolarSystem
        elif idCheckers.IsStation(destinationID):
            station = sm.StartService('ui').GetStationStaticInfo(destinationID)
            typeID = station.stationTypeID
        else:
            structure = sm.GetService('structureDirectory').GetStructureInfo(destinationID)
            if structure is None:
                return
            typeID = structure.typeID
        GetMenuService().TryExpandActionMenu(itemID=destinationID, clickedObject=self, typeID=typeID)

    def GetRadialMenuIndicator(self, create = True, *args):
        radialMenuSprite = getattr(self, 'radialMenuSprite', None)
        if radialMenuSprite and not radialMenuSprite.destroyed:
            return radialMenuSprite
        if not create:
            return
        radialMenuSprite = Fill(name='radialMenuSprite', bgParent=self, padding=(-1, -1, -2, -2), color=(0.5, 0.5, 0.5, 0.8))
        self.radialMenuSprite = radialMenuSprite
        return radialMenuSprite

    def ShowRadialMenuIndicator(self, slimItem, *args):
        mySprite = self.GetRadialMenuIndicator(create=True)
        mySprite.display = True
        self.icon.SetAlpha(1.0)
        self.fadingDisabled = True

    def HideRadialMenuIndicator(self, slimItem, *args):
        mySprite = self.GetRadialMenuIndicator(create=False)
        if mySprite:
            mySprite.display = False
        self.fadingDisabled = False
        self.CheckIfMouseOver()

    def GetTooltipPositionFallbacks(self):
        return [uiconst.POINT_BOTTOM_1]


def ShowTriglavianWarning(solarSystemID):
    return False


class WaypointPanel(ContainerAutoSize):
    COLOR_BACKGROUND = (0.0, 0.0, 0.0, 0.3)

    def __init__(self, item_id = None, link_hint = None, **kwargs):
        self._item_id = item_id
        self._waypoint_trace_label = None
        self._link_hint = link_hint
        super(WaypointPanel, self).__init__(alignMode=uiconst.TOTOP, **kwargs)
        self.layout()
        self._update()

    def layout(self):
        main_cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        Fill(bgParent=main_cont, color=self.COLOR_BACKGROUND)
        self._waypoint_trace_label = eveLabel.EveLabelMedium(parent=main_cont, align=uiconst.TOTOP, padding=8, state=uiconst.UI_NORMAL)
        self._waypoint_trace_label.OnMouseDownWithUrl = self._on_mouse_down_with_url
        self._trig_warning = TriglavianWarningIcon(parent=main_cont, align=uiconst.CENTERRIGHT, left=8)

    @property
    def item_id(self):
        return self._item_id

    @item_id.setter
    def item_id(self, item_id):
        if self._item_id == item_id:
            return
        self._item_id = item_id
        self._update()

    @property
    def should_show_triglavian_warning(self):
        return self.item_id is not None and ShowTriglavianWarning(self.item_id)

    def _update(self):
        if self._item_id is None:
            text = localization.GetByLabel('UI/Inflight/NoDestination')
        else:
            text = eveformat.center(sm.GetService('infoPanel').GetSolarSystemTrace(self.item_id, self._link_hint))
        self._waypoint_trace_label.text = text
        if self.should_show_triglavian_warning:
            self._waypoint_trace_label.padRight = 34
            self._trig_warning.Show()
        else:
            self._waypoint_trace_label.padRight = 8
            self._trig_warning.Hide()

    @threadutils.threaded
    def _on_mouse_down_with_url(self, url, *args):
        try:
            parsed = evelink.parse_show_info_url(url)
        except Exception:
            log.LogWarning('Failed to parse URL')
            return

        if parsed.item_id is None or not idCheckers.IsSolarSystem(parsed.item_id):
            return
        local_stargate = FindLocalStargate(parsed.item_id)
        if local_stargate:
            destination_id = local_stargate.itemID
            type_id = local_stargate.typeID
        else:
            destination_id = parsed.item_id
            type_id = const.typeSolarSystem
        GetMenuService().TryExpandActionMenu(itemID=destination_id, clickedObject=self, typeID=type_id)


class NextWaypointPanel(WaypointPanel):

    def __init__(self, item_id = None, **kwargs):
        self._trig_icon_cont = None
        super(NextWaypointPanel, self).__init__(item_id=item_id, link_hint=localization.GetByLabel('UI/Neocom/Autopilot/NextSystemInRoute'), **kwargs)

    def layout(self):
        super(NextWaypointPanel, self).layout()
        Sprite(parent=Container(parent=self, align=uiconst.TOTOP, height=12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/LocationInfo/pointerDown.png', width=10, height=10, color=self.COLOR_BACKGROUND)


class DestinationWaypointPanel(WaypointPanel):

    def __init__(self, item_id = None, pointer_offset = 0, **kwargs):
        self._pointer = None
        self._pointer_offset = pointer_offset
        super(DestinationWaypointPanel, self).__init__(item_id=item_id, link_hint=localization.GetByLabel('UI/Neocom/Autopilot/CurrentDestination'), **kwargs)

    def layout(self):
        self._pointer = Sprite(parent=Container(parent=self, align=uiconst.TOTOP, height=12), align=uiconst.BOTTOMLEFT, state=uiconst.UI_DISABLED, left=self.pointer_offset, texturePath='res:/UI/Texture/classes/LocationInfo/pointerUp.png', width=10, height=10, color=self.COLOR_BACKGROUND)
        super(DestinationWaypointPanel, self).layout()

    @property
    def pointer_offset(self):
        return self._pointer_offset

    @pointer_offset.setter
    def pointer_offset(self, pointer_offset):
        self._pointer_offset = pointer_offset
        self._pointer.left = pointer_offset


class TriglavianWarningIcon(Sprite):

    def __init__(self, **kwargs):
        super(TriglavianWarningIcon, self).__init__(texturePath='res:/UI/Texture/classes/Invasions/triglavianRace_18x18.png', width=18, height=18, hint=localization.GetByLabel('UI/Invasion/HUD/InvasionSolarSystemHint'), color=(1.0, 0.2, 0.1), **kwargs)
