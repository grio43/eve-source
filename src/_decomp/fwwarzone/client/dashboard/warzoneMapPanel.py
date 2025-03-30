#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\warzoneMapPanel.py
import math
import eveicon
import uthread2
from carbonui import TextColor, uiconst
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorarc import VectorArc
from carbonui.primitives.vectorline import VectorLine
from carbonui.services.setting import CharSettingEnum, CharSettingBool
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from characterdata.factions import get_faction_name
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.panContainer import PanContainer
from fwwarzone.client.dashboard.collapsingSection import CollapsingSection
from fwwarzone.client.dashboard.const import ADJACENCY_STATE_TO_ICON_PATH, FACTION_ID_TO_COLOR, GetAdjacencyBrightness, GetAdjacencyOpacity
from fwwarzone.client.dashboard.fwMapStar import FWMapStar
from fwwarzone.client.dashboard.mapData import WarzoneMapData
from fwwarzone.client.util import CachedGetBattlefieldInstances
from localization import GetByLabel, GetByMessageID
from pirateinsurgency.client.dashboard.const import WARZONE_ID_TO_PIRATE_FACTION_ID
STAR_TEX_PATH = 'res:/UI/Texture/classes/frontlines/star.png'
ZOOM_LEVELS = [1.0, 0.6]
ZOOM_SETTING = CharSettingEnum(settings_key='warzone_map_panel_zoom_level', default_value=0, options=range(len(ZOOM_LEVELS)))

def getColorUIHighlight(alpha = 1.0):
    elementColor = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
    return color.GetColor(elementColor, alpha=alpha)


class WarzoneMapPanel(Container):
    GLOW_HIGHLIGHT_BRIGHTNESS = 1.5
    GLOW_STANDARD_BRIGHTNESS = 0.5
    LINK_GLOW_HIGHLIGHT_BRIGHTNESS = 1.5
    LINK_GLOW_STANDARD_BRIGHTNESS = 0.0
    default_minWidth = 640
    default_minHeight = 640
    default_viewSize = 1800
    default_bgColor = eveColor.BLACK
    default_warzoneId = 2
    ZOOM_LEVELS = ZOOM_LEVELS
    warzoneToFocusedSystem = {1: 30002959,
     2: 30003840}

    def ApplyAttributes(self, attributes):
        self.markerLayer = None
        Container.ApplyAttributes(self, attributes)
        self.cameraX = 0
        self.cameraY = 0
        self.isZooming = False
        self.linkLinesBySystemId = {}
        self.warzoneId = attributes.get('warzoneId', self.default_warzoneId)
        self.centerOnSystemId = self.warzoneToFocusedSystem[self.warzoneId]
        self.viewSize = attributes.get('viewSize', self.default_viewSize)
        self.starSelectedCallback = attributes.get('starSelectedCallback', lambda *args: args)
        self.displayAsFactionID = attributes.get('displayAsFactionID')
        self.currentZoomLevelIndex = ZOOM_SETTING.get()
        self.interstellarShipCasterFactionFocusSignal = attributes.get('interstellarShipCasterFactionFocusSignal')
        self.interstellarShipCasterFactionFocusSignal.connect(self.OnInterstellarShipCasterFactionFocus)
        self.battlefields = None
        self.mapData = None
        self.legend = None
        self.showLegendSetting = attributes.get('showLegendSetting')
        self.showLegendSetting.on_change.connect(self.UpdateLegendShown)
        self.showSystemNamesSetting = CharSettingBool('FWWindowShowSystemNames', True)
        self.showStatusSpritesSetting = CharSettingBool('FWWindowShowStatusSprites', True)
        self.showIAmhHereIconSetting = CharSettingBool('FWWindowShowIAmHereIcon', True)
        self.showLandingPadsSetting = CharSettingBool('FWWindowShowLandingPadsIcon', True)
        self.showShipcasterSetting = CharSettingBool('FWWindowShowShipcaster', True)
        self.showBattlefieldSetting = CharSettingBool('FWWindowShowBattlefield', True)
        self.showFOBSetting = CharSettingBool('FWWindowShowFOBIcons', True)
        self.ResetVariables()
        self.AsyncLoadMap()

    def ResetVariables(self):
        self.myLocationCont = None
        self.battlefielMarkersBySolarSystemID = {}
        self.landingPadMarkersBySolarSystemID = {}
        self.shipcasterMarkersBySolarSystemID = {}
        self.FOBMarkersBySolarSystemID = {}
        self.allLinkLines = []
        self.systemNameLabels = []
        self.systemStateIcons = []
        self.statusSprites = []
        self.navigationSystemSovIcons = []
        self.starCoordBySystemID = {}

    def AsyncLoadMap(self):
        uthread2.StartTasklet(self._LoadMap)

    def _LoadMap(self):
        self.Flush()
        loadingWheel = LoadingWheel(width=64, height=64, parent=self, align=uiconst.CENTER)
        self.battlefields = CachedGetBattlefieldInstances()
        self.mapData = WarzoneMapData()
        self.ResetVariables()
        self.Flush()
        self.ConstructMap()
        self.HideMapDetails(animate=False)
        self.ConstructBattlefieldMarkers()
        self.ConstructFOBMarkers()
        self.ConstructLandingPadMarkers(self.displayAsFactionID)
        self.ConstructShipCasterMarkers(self.displayAsFactionID)
        self.UpdateMarkedLocations()
        self.UpdateDetailsByZoomLevel(animate=False)
        self.ZoomTo(self.ZOOM_LEVELS[self.currentZoomLevelIndex], False)
        loadingWheel.Close()

    def UpdateLegendShown(self, active):
        if self.legend is None:
            return
        if active:
            animations.FadeIn(self.legend)
        else:
            animations.FadeOut(self.legend)

    def OnInterstellarShipCasterFactionFocus(self, factionID):
        self.ConstructShipCasterMarkers(factionID)
        self.ConstructLandingPadMarkers(factionID)
        self.UpdateMarkedLocations()
        self.UpdateDetailsByZoomLevel()

    def OnMouseWheel(self, *args):
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        self.OnZoom(modifier * uicore.uilib.dz)

    def OnZoom(self, dz):
        if self.isZooming:
            return
        if dz < 0:
            self.currentZoomLevelIndex = max(0, self.currentZoomLevelIndex - 1)
        else:
            self.currentZoomLevelIndex = min(len(self.ZOOM_LEVELS) - 1, self.currentZoomLevelIndex + 1)
        self.UpdateDetailsByZoomLevel()
        ZOOM_SETTING.set(self.currentZoomLevelIndex)
        self.ZoomTo(self.ZOOM_LEVELS[self.currentZoomLevelIndex])

    def UpdateDetailsByZoomLevel(self, animate = True):
        if self.currentZoomLevelIndex == 0:
            self.ShowMapDetails(animate)
        elif self.currentZoomLevelIndex == 1:
            self.HideMapDetails(animate)
        zoomValue = self.ZOOM_LEVELS[self.currentZoomLevelIndex]
        if self.myLocationCont:
            self.myLocationCont.AdjustToZoom(zoomValue, animate)
        for battlefieldMarker in self.battlefielMarkersBySolarSystemID.itervalues():
            battlefieldMarker.AdjustToZoom(zoomValue, animate)

        for landingPadMarker in self.landingPadMarkersBySolarSystemID.itervalues():
            landingPadMarker.AdjustToZoom(zoomValue, animate)

        for shipcasterMarker in self.shipcasterMarkersBySolarSystemID.itervalues():
            shipcasterMarker.AdjustToZoom(zoomValue, animate)

        for FOBMarker in self.FOBMarkersBySolarSystemID.itervalues():
            FOBMarker.AdjustToZoom(zoomValue, animate)

    def ShowMapDetails(self, animate = True):
        elementToFadeIn = self.allLinkLines[:]
        elementToFadeIn += self.navigationSystemSovIcons
        if self.showStatusSpritesSetting.is_enabled():
            elementToFadeIn += self.statusSprites
        if self.showSystemNamesSetting.is_enabled():
            elementToFadeIn += self.systemNameLabels
        for element in elementToFadeIn:
            if animate:
                animations.FadeIn(element)
            else:
                element.opacity = 1.0

        if self.showStatusSpritesSetting.is_enabled():
            for starIcon in self.systemStateIcons:
                if animate:
                    animations.FadeOut(starIcon)
                else:
                    starIcon.opacity = 0.0

    def HideMapDetails(self, animate = True):
        elementToFadeOut = self.allLinkLines[:]
        elementToFadeOut += self.systemNameLabels
        elementToFadeOut += self.statusSprites
        elementToFadeOut += self.navigationSystemSovIcons
        for element in elementToFadeOut:
            if animate:
                animations.FadeOut(element)
            else:
                element.opacity = 0.0

        for starIcon in self.systemStateIcons:
            if animate:
                animations.FadeIn(starIcon)
            else:
                starIcon.opacity = 1.0

    def ToggleShowSystemNames(self):
        if self.currentZoomLevelIndex == 0:
            if self.showSystemNamesSetting.is_enabled():
                for element in self.systemNameLabels:
                    animations.FadeOut(element)

            else:
                for element in self.systemNameLabels:
                    animations.FadeIn(element)

        self.showSystemNamesSetting.toggle()

    def ToggleShowStatusSprites(self):
        if self.currentZoomLevelIndex == 0:
            if self.showStatusSpritesSetting.is_enabled():
                for element in self.statusSprites:
                    animations.FadeOut(element)

                for starIcon in self.systemStateIcons:
                    animations.FadeIn(starIcon)

            else:
                for element in self.statusSprites:
                    animations.FadeIn(element)

                for starIcon in self.systemStateIcons:
                    animations.FadeOut(starIcon)

        self.showStatusSpritesSetting.toggle()

    def ZoomTo(self, newScale, animate = True):
        self.isZooming = True
        self.topLayer.state = uiconst.UI_DISABLED

        def _end_zoom():
            self.topLayer.state = uiconst.UI_PICKCHILDREN
            self.isZooming = False

        if animate:
            uicore.animations.MorphScalar(self.cameraCont, 'scale', self.cameraCont.scale, newScale, duration=0.35, callback=_end_zoom)
        else:
            self.cameraCont.scale = newScale
            _end_zoom()

    def ConstructMap(self):
        mapData = self.mapData.GetWarzoneSystems(self.warzoneId)
        systems = mapData.systems
        self.cameraCont = PanContainer(parent=self, align=uiconst.TOALL, opacity=0.0)
        stars = {}
        self.topLayer = Container(name='topLayer', parent=self.cameraCont.mainCont, align=uiconst.TOPLEFT, width=self.viewSize, height=self.viewSize, idx=-1)
        self.markerLayer = Container(name='markerLayer', parent=self.topLayer, align=uiconst.TOALL)
        self.battleFieldMarkerLayer = Container(name='battleFieldMarkerLayer', parent=self.markerLayer, align=uiconst.TOALL)
        self.territoryZonesPanel = Container(parent=self.cameraCont.mainCont, align=uiconst.TOPLEFT, width=self.viewSize, height=self.viewSize, idx=100)
        for systemId, system in systems.iteritems():
            xpos = self.viewSize * (system.position[0] / float(mapData.mapWidth))
            ypos = self.viewSize * (system.position[1] / float(mapData.mapHeight))
            texPath = STAR_TEX_PATH
            tileColor = eveColor.WHITE
            opacity = 0.2
            brightness = 0
            iconSize = 0
            icon_path = ''
            if not system.isNavigationSystem:
                occupationState = system.occupationState
                tileColor = FACTION_ID_TO_COLOR[occupationState.occupierID]
                opacity = GetAdjacencyOpacity(occupationState.adjacencyState)
                brightness = GetAdjacencyBrightness(occupationState.adjacencyState)
                icon_path = ADJACENCY_STATE_TO_ICON_PATH[occupationState.adjacencyState]
                iconSize = 64
            labelTransform = Transform(parent=self.topLayer, align=uiconst.TOPLEFT, top=ypos, left=xpos + 15, idx=100)
            labelTransform.scalingCenter = (0.0, 0.5)
            label = EveLabelLarge(parent=labelTransform, align=uiconst.TOPLEFT, text=cfg.evelocations.Get(systemId).name, color=TextColor.HIGHLIGHT)
            labelTransform.top = ypos - label.actualTextHeight / 2
            self.systemNameLabels.append(labelTransform)
            xScalingFactor = float(self.viewSize + 17) / float(mapData.mapWidth)
            yScalingFactor = float(self.viewSize + 17) / float(mapData.mapHeight)
            spriteWidth = system.textureWidth * xScalingFactor
            spriteHeight = system.textureHeight * yScalingFactor
            xOffset = system.xOffset / float(mapData.mapWidth) * self.viewSize
            yOffset = system.yOffset / float(mapData.mapHeight) * self.viewSize
            if not system.isNavigationSystem:
                Sprite(name='territorySprite', parent=self.territoryZonesPanel, width=spriteWidth, height=spriteHeight, align=uiconst.TOPLEFT, top=yOffset, left=xOffset, texturePath=system.territoryTexturePath, color=tileColor, state=uiconst.UI_DISABLED, idx=-1, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=brightness, opacity=opacity)
                icon = FWMapStar(name='starIconSprite', parent=self.topLayer, warzoneId=self.warzoneId, align=uiconst.TOPLEFT, top=ypos - 33 / 2, left=xpos - 33 / 2, iconSize=66, texturePath=texPath, func=self._GetSelectStarFunction(systemId), iconColor=tileColor, glowColor=tileColor, system=system, opacity=0.0)
                self.systemStateIcons.append(icon)
            else:
                starColor = eveColor.WHITE
                solarSystem = cfg.mapSystemCache.get(systemId, None)
                if solarSystem:
                    factionId = getattr(solarSystem, 'factionID', None)
                    if factionId in FACTION_ID_TO_COLOR:
                        starColor = FACTION_ID_TO_COLOR[factionId]
                FWMapStar(name='starIconSprite', parent=self.topLayer, warzoneId=self.warzoneId, align=uiconst.TOPLEFT, top=ypos - 33 / 2, left=xpos - 33 / 2, iconSize=66, texturePath=texPath, func=self._GetSelectStarFunction(systemId), iconColor=starColor, glowColor=starColor, system=system, opacity=1)
            statusSpriteTransform = Transform(parent=self.topLayer, name='statusSpriteTransform', width=256, height=256, top=ypos - 128, left=xpos - 128, align=uiconst.TOPLEFT, scalingCenter=(0.5, 0.5), state=uiconst.UI_DISABLED)
            Sprite(name='statusSprite', parent=statusSpriteTransform, align=uiconst.CENTER, width=iconSize, height=iconSize, texturePath=icon_path, color=eveColor.WHITE)
            statusSpriteTransform.scale = (0.5, 0.5)
            self.statusSprites.append(statusSpriteTransform)
            stars[systemId] = (xpos, ypos)

        doneSystems = set()
        for systemId, system in systems.iteritems():
            neighbours = system.neighbours
            doneSystems.add(systemId)
            for neighbourId in neighbours:
                if neighbourId in stars and neighbourId not in doneSystems:
                    aXPos = stars[systemId][0]
                    aYPos = stars[systemId][1]
                    bXPos = stars[neighbourId][0]
                    bYPos = stars[neighbourId][1]
                    aColor = eveColor.WHITE
                    bColor = eveColor.WHITE
                    linkLine = VectorLine(parent=self.topLayer, translationFrom=(aXPos, aYPos), translationTo=(bXPos, bYPos), colorFrom=aColor, colorTo=bColor, widthFrom=0.5, widthTo=0.5, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self.LINK_GLOW_STANDARD_BRIGHTNESS - 1.0)
                    self.allLinkLines.append(linkLine)
                    linkLineId = len(self.allLinkLines) - 1
                    if systemId in self.linkLinesBySystemId:
                        self.linkLinesBySystemId[systemId].append(linkLineId)
                    else:
                        self.linkLinesBySystemId[systemId] = [linkLineId]
                    if neighbourId in self.linkLinesBySystemId:
                        self.linkLinesBySystemId[neighbourId].append(linkLineId)
                    else:
                        self.linkLinesBySystemId[neighbourId] = [linkLineId]

        self.starCoordBySystemID = stars
        self._MoveCamera(systems[self.centerOnSystemId].position[0] / float(mapData.mapWidth) * self.viewSize, systems[self.centerOnSystemId].position[1] / float(mapData.mapHeight) * self.viewSize, animate=False)
        animations.FadeIn(self.cameraCont, duration=2.0)
        self.ConstructLegend()

    def FadeMarkerIcons(self, iconsMap, fadeOut = True):
        if fadeOut:
            for markerCont in iconsMap.itervalues():
                animations.FadeOut(markerCont)

        else:
            for markerCont in iconsMap.itervalues():
                animations.FadeIn(markerCont)

    def ConstructLegend(self, *args):
        if self.legend:
            self.legend.Flush()
            self.legend.Close()
        legendCont = Container(name='legendCont', align=uiconst.TOTOP, height=208, clipChildren=True, state=uiconst.UI_PICKCHILDREN)
        Fill(bgParent=legendCont, color=eveColor.BLACK, opacity=0.5)
        toggleSystemNames = lambda _: self.ToggleShowSystemNames()
        LegendRow(parent=legendCont, align=uiconst.TOTOP, label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/systemNames'), texturePath='res:/UI/Texture/Shared/Brackets/solarSystem.png', func=toggleSystemNames, active=self.showSystemNamesSetting.is_enabled())
        toggleStatusSprites = lambda _: self.ToggleShowStatusSprites()
        LegendRow(parent=legendCont, align=uiconst.TOTOP, label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/warzoneIconsLegendText'), texturePath='res:/UI/Texture/classes/frontlines/factionalwarfare_icon.png', func=toggleStatusSprites, active=self.showStatusSpritesSetting.is_enabled())

        def _showIAmHereIconAndChangeSetting(active):
            if active:
                animations.FadeIn(self.myLocationCont)
            else:
                animations.FadeOut(self.myLocationCont)
            self.showIAmhHereIconSetting.set(active)

        LegendRow(parent=legendCont, align=uiconst.TOTOP, label=GetByLabel('UI/Map/StarMap/lblYouAreHere'), texturePath=eveicon.user, func=_showIAmHereIconAndChangeSetting, active=self.showIAmhHereIconSetting.is_enabled())

        def showMarkersAndChangeSetting(active, markersMap, setting):
            if active:
                self.FadeMarkerIcons(markersMap, fadeOut=False)
            else:
                self.FadeMarkerIcons(markersMap)
            setting.set(active)

        LegendRow(parent=legendCont, align=uiconst.TOTOP, label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/landingPadLegendText'), texturePath='res:/UI/Texture/classes/frontlines/shipcaster/landingpad_32.png', func=lambda active: showMarkersAndChangeSetting(active, self.landingPadMarkersBySolarSystemID, self.showLandingPadsSetting), active=self.showLandingPadsSetting.is_enabled())
        LegendRow(parent=legendCont, align=uiconst.TOTOP, label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/shipcasterLegendText'), texturePath='res:/UI/Texture/classes/frontlines/shipcaster/shipcaster_icon_32.png', func=lambda active: showMarkersAndChangeSetting(active, self.shipcasterMarkersBySolarSystemID, self.showShipcasterSetting), active=self.showShipcasterSetting.is_enabled())
        LegendRow(parent=legendCont, align=uiconst.TOTOP, label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/battlefieldLegendText'), texturePath='res:/UI/Texture/classes/frontlines/battlefield_icon_16.png', func=lambda active: showMarkersAndChangeSetting(active, self.battlefielMarkersBySolarSystemID, self.showBattlefieldSetting), active=self.showBattlefieldSetting.is_enabled())
        LegendRow(parent=legendCont, align=uiconst.TOTOP, label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/pirateFOBLegendText'), texturePath='res:/UI/Texture/classes/frontlines/fob_32.png', func=lambda active: showMarkersAndChangeSetting(active, self.FOBMarkersBySolarSystemID, self.showFOBSetting), active=self.showFOBSetting.is_enabled())
        self.legend = CollapsingSection(parent=self, align=uiconst.TOPLEFT, width=200, headerText='Legend', section=legendCont, idx=0)
        Fill(bgParent=self.legend.headerCont, color=eveColor.BLACK, opacity=0.75)
        if not self.showLegendSetting.is_enabled():
            self.legend.opacity = 0.0

    def _GetSelectStarFunction(self, systemId):

        def fun():
            self.starSelectedCallback(systemId)

        return fun

    def highlightSingleLink(self, lineId):
        highlighted = False
        for eachSystemId, lines in self.linkLinesBySystemId.iteritems():
            for vectorLineId in lines:
                vectorLine = self.allLinkLines[vectorLineId]
                if vectorLineId == lineId and not highlighted:
                    vectorLine.glowBrightness = self.LINK_GLOW_HIGHLIGHT_BRIGHTNESS
                    highlighted = True

    def _MoveCamera(self, x, y, animate = True):
        self.cameraCont.PanTo(x / self.viewSize, y / self.viewSize, duration=0.15, animate=animate)

    def GetOccupierColor(self, occupierId):
        if occupierId == 500003:
            return eveColor.HOT_RED
        else:
            return eveColor.SMOKE_BLUE

    def DebugReloadMap(self):
        self.mapData = WarzoneMapData()
        self.mapData.occupationStates = sm.GetService('fwWarzoneSvc').GetAllOccupationStatesUncached()
        self._LoadMap()

    def ReloadMap(self):
        self._LoadMap()

    def UpdateMarkedLocations(self):
        self.UpdateCurrentLocation()
        self.UpdateBattlefieldLocation()
        self.UpdatelandingPadLocations()
        self.UpdateShipCasterLocations()
        self.UpdateFOBmarkerLocation()
        self.FadeMarkerIcons(self.battlefielMarkersBySolarSystemID, fadeOut=not self.showBattlefieldSetting.is_enabled())
        self.FadeMarkerIcons(self.landingPadMarkersBySolarSystemID, fadeOut=not self.showLandingPadsSetting.is_enabled())
        self.FadeMarkerIcons(self.shipcasterMarkersBySolarSystemID, fadeOut=not self.showShipcasterSetting.is_enabled())
        self.FadeMarkerIcons(self.FOBMarkersBySolarSystemID, fadeOut=not self.showFOBSetting.is_enabled())
        if self.showIAmhHereIconSetting.is_enabled():
            animations.FadeIn(self.myLocationCont)
        else:
            animations.FadeOut(self.myLocationCont)

    def UpdateCurrentLocation(self):
        if self.markerLayer is None or self.markerLayer.destroyed:
            return
        if not self.myLocationCont or self.myLocationCont.destroyed:
            self.ConstructMyLocationCont()
        pos = self.starCoordBySystemID.get(session.solarsystemid2, None)
        if pos is None:
            self.myLocationCont.Hide()
            return
        self.myLocationCont.Show()
        x, y = pos
        self.myLocationCont.SetOffset(x, y, False)

    def ConstructMyLocationCont(self):
        self.myLocationCont = MapMarker(parent=self.markerLayer, idx=0, currentZoomValue=self.ZOOM_LEVELS[self.currentZoomLevelIndex], text=GetByLabel('UI/Map/StarMap/lblYouAreHere'))
        if self.showIAmhHereIconSetting.is_enabled():
            self.myLocationCont.opacity = 0.0

    def ConstructShipCasterMarkers(self, factionID):
        for marker in self.shipcasterMarkersBySolarSystemID.itervalues():
            marker.Close()

        self.shipcasterMarkersBySolarSystemID = {}
        hqSystemId = sm.GetService('fwWarzoneSvc').GetAllHQSystems()
        factionsWithShipcaster = sm.GetService('shipcaster').GetFactionsWithShipcaster()
        if factionID in factionsWithShipcaster:
            solarSystemID = hqSystemId[factionID]
            marker = ShipCasterMarker(parent=self.battleFieldMarkerLayer, idx=0, currentZoomValue=self.ZOOM_LEVELS[self.currentZoomLevelIndex], text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/shipcasterSectionHeader'))
            if not self.showShipcasterSetting.is_enabled():
                marker.opacity = 0.0
            self.shipcasterMarkersBySolarSystemID[solarSystemID] = marker

    def ConstructFOBMarkers(self):
        snapshots = sm.GetService('insurgencyCampaignSvc').GetCurrentCampaignSnapshots_Memoized()
        for snapshot in snapshots:
            if snapshot.warzoneID == self.warzoneId:
                pirateFaction = WARZONE_ID_TO_PIRATE_FACTION_ID[self.warzoneId]
                factionName = get_faction_name(pirateFaction)
                marker = FOBMarker(parent=self.battleFieldMarkerLayer, idx=0, currentZoomValue=self.ZOOM_LEVELS[self.currentZoomLevelIndex], text=GetByLabel('UI/PirateInsurgencies/FOBSystem', factionName=factionName))
                if not self.showFOBSetting.is_enabled():
                    marker.opacity = 0.0
                self.FOBMarkersBySolarSystemID[snapshot.originSolarsystemID] = marker

    def ConstructLandingPadMarkers(self, factionID):
        for marker in self.landingPadMarkersBySolarSystemID.itervalues():
            marker.Close()

        self.landingPadMarkersBySolarSystemID = {}
        landingPads = sm.GetService('shipcaster').GetAllLandingPads()
        for pad in landingPads:
            if pad.factionID == factionID and pad.isLinked and pad.solarSystemID in self.starCoordBySystemID:
                marker = LandingPadMapMarker(parent=self.battleFieldMarkerLayer, idx=0, currentZoomValue=self.ZOOM_LEVELS[self.currentZoomLevelIndex], text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/landingPad'), landingPad=pad)
                if not self.showLandingPadsSetting.is_enabled():
                    marker.opacity = 0.0
                self.landingPadMarkersBySolarSystemID[pad.solarSystemID] = marker

    def ConstructBattlefieldMarkers(self):
        self.battleFieldMarkerLayer.Flush()
        self.battlefielMarkersBySolarSystemID.clear()
        for solarSystemID, battlefieldInstances in self.battlefields.iteritems():
            if solarSystemID not in self.starCoordBySystemID:
                continue
            if len(battlefieldInstances) == 0:
                continue
            dungeon = battlefieldInstances[0]
            battlefieldMarker = BattlefieldMapMarker(parent=self.battleFieldMarkerLayer, idx=0, currentZoomValue=self.ZOOM_LEVELS[self.currentZoomLevelIndex], text=GetByLabel('UI/FactionWarfare/frontlines/BattlefieldWithName', battlefieldName=GetByMessageID(dungeon.dungeonNameID)))
            self.battlefielMarkersBySolarSystemID[solarSystemID] = battlefieldMarker

    def UpdatelandingPadLocations(self):
        for solarSystemID, marker in self.landingPadMarkersBySolarSystemID.iteritems():
            pos = self.starCoordBySystemID.get(solarSystemID, None)
            if pos is None:
                continue
            marker.Show()
            x, y = pos
            marker.SetOffset(x, y, False)

    def UpdateShipCasterLocations(self):
        for solarSystemID, marker in self.shipcasterMarkersBySolarSystemID.iteritems():
            pos = self.starCoordBySystemID.get(solarSystemID, None)
            if pos is None:
                continue
            marker.Show()
            x, y = pos
            marker.SetOffset(x, y, False)

    def UpdateBattlefieldLocation(self):
        for solarSystemID, markerCont in self.battlefielMarkersBySolarSystemID.iteritems():
            pos = self.starCoordBySystemID.get(solarSystemID, None)
            if pos is None:
                continue
            markerCont.Show()
            x, y = pos
            markerCont.SetOffset(x, y, False)

    def UpdateFOBmarkerLocation(self):
        for solarSystemID, marker in self.FOBMarkersBySolarSystemID.iteritems():
            pos = self.starCoordBySystemID.get(solarSystemID, None)
            if pos is None:
                continue
            marker.Show()
            x, y = pos
            marker.SetOffset(x, y, False)


class MapMarker(Container):
    default_name = 'FW_MapMarker'
    default_align = uiconst.TOPLEFT
    default_width = 60
    default_height = 60
    default_innerSpriteWidth = 60
    default_innerSpriteHeight = 60
    markerTexture = 'res:/UI/Texture/classes/frontlines/hereYou.png'
    leftAligned = True
    default_showHereMarker = True

    def ApplyAttributes(self, attributes):
        super(MapMarker, self).ApplyAttributes(attributes)
        self.systemPos = (0, 0)
        self.currentZoomValue = attributes.get('currentZoomValue', 1.0)
        self.showHereMarker = attributes.get('showHereMarker', self.default_showHereMarker)
        self.innerSpriteWidth = attributes.get('innerSpriteWidth', self.default_innerSpriteWidth)
        self.innerSpriteHeight = attributes.get('innerSpriteHeight', self.default_innerSpriteHeight)
        text = attributes.get('text', 1.0)
        self.offsetCont = Transform(name='offsetCont', parent=self, align=uiconst.CENTER, pos=self.GetOffset(), scalingCenter=(0.5, 0.5))
        self.flipCont = Transform(name='flipCont', parent=self.offsetCont, align=uiconst.CENTER, pos=(0, 0, 32, 32), scalingCenter=(0.5, 0.5))
        innerSpriteColor = self.GetInnerSpriteColor()
        iconSprite = Sprite(name='iconSprite', parent=self.flipCont, texturePath=self.markerTexture, pos=(0,
         0,
         self.innerSpriteWidth,
         self.innerSpriteHeight), state=uiconst.UI_NORMAL, align=uiconst.CENTER, color=innerSpriteColor)
        if self.showHereMarker:
            iconSprite.state = uiconst.UI_DISABLED
        color = self.GetColor()
        if self.showHereMarker:
            backgroundSprite = Sprite(name='backgroundSprite', parent=self.flipCont, texturePath='res:/UI/Texture/classes/frontlines/here1.png', pos=(0, 0, 60, 60), align=uiconst.CENTER, state=uiconst.UI_NORMAL, color=color, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
            backgroundSprite.OnMouseEnter = self.OnMouseEnterIcon
            backgroundSprite.OnMouseExit = self.OnMouseExitIcon
        else:
            iconSprite.OnMouseEnter = self.OnMouseEnterIcon
            iconSprite.OnMouseExit = self.OnMouseExitIcon
        labelOffset = 16 if self.leftAligned else 24
        self.labelMedium = EveLabelMedium(parent=self.offsetCont, text=text, align=uiconst.CENTERLEFT, left=self.offsetCont.width / 2 + labelOffset)
        self.labelMedium.Hide()
        self.labelLarge = EveLabelMedium(parent=self.offsetCont, text=text, align=uiconst.CENTERLEFT, left=self.offsetCont.width / 2 + labelOffset)
        self.labelLarge.Hide()
        self.AdjustToZoom(self.currentZoomValue, animate=False)

    def GetOffset(self):
        return (0, 0, 32, 32)

    def OnMouseEnterIcon(self, *args):
        if self.currentZoomValue > 0.8:
            self.labelMedium.Show()
            self.labelLarge.Hide()
        else:
            self.labelMedium.Hide()
            self.labelLarge.Show()

    def OnMouseExitIcon(self, *args):
        self.labelMedium.Hide()
        self.labelLarge.Hide()

    def AdjustToZoom(self, zoomValue, animate = True):
        self.currentZoomValue = zoomValue
        self.labelMedium.Hide()
        self.labelLarge.Hide()
        scale = 1.0 / zoomValue
        self.flipCont.scale = (1, 1) if self.leftAligned else (-1, 1)
        newScale = (scale, scale)
        if animate:
            uicore.animations.MorphVector2(self.offsetCont, 'scale', self.offsetCont.scale, newScale, duration=0.5)
        else:
            self.offsetCont.scale = newScale
        self.SetOffset(*self.systemPos)

    def SetOffset(self, x, y, animate = True):
        self.systemPos = (x, y)
        newLeft = self._GetNewLeft(x)
        newTop = y - 8 * self.currentZoomValue
        if animate:
            uicore.animations.MorphScalar(self, 'left', self.left, newLeft, duration=0.5)
            uicore.animations.MorphScalar(self, 'top', self.top, newTop, duration=0.5)
        else:
            self.left = newLeft
            self.top = newTop

    def _GetNewLeft(self, x):
        if self.leftAligned:
            modifier = 1
            widthOffset = -self.width
        else:
            modifier = -1
            widthOffset = 0
        newLeft = x + widthOffset + modifier * 8 * self.currentZoomValue
        return newLeft

    def GetColor(self):
        return eveColor.CRYO_BLUE

    def GetInnerSpriteColor(self):
        return eveColor.WHITE


class LandingPadMapMarker(MapMarker):
    markerTexture = 'res:/UI/Texture/classes/frontlines/shipcaster/landingpad_32.png'
    leftAligned = False
    default_showHereMarker = False
    default_innerSpriteHeight = 40
    default_innerSpriteWidth = 40

    def ApplyAttributes(self, attributes):
        self.landingPad = attributes.get('landingPad')
        super(LandingPadMapMarker, self).ApplyAttributes(attributes)

    def GetOffset(self):
        return (-22, -50, 32, 32)


class ShipCasterMarker(MapMarker):
    markerTexture = 'res:/UI/Texture/classes/frontlines/shipcaster/shipcaster_icon_40.png'
    leftAligned = False
    default_showHereMarker = False
    default_innerSpriteHeight = 32
    default_innerSpriteWidth = 32


class FOBMarker(MapMarker):
    default_name = 'FOBMapMarker'
    markerTexture = 'res:/UI/Texture/classes/frontlines/fob_32.png'
    leftAligned = False
    default_showHereMarker = False
    default_innerSpriteHeight = 32
    default_innerSpriteWidth = 32

    def GetColor(self):
        return eveColor.WHITE


class BattlefieldMapMarker(MapMarker):
    markerTexture = 'res:/UI/Texture/classes/frontlines/battlefieldSmall.png'
    leftAligned = False
    default_showHereMarker = False
    default_innerSpriteHeight = 110
    default_innerSpriteWidth = 110

    def GetColor(self):
        return eveColor.WHITE


class LegendRow(Container):
    default_height = 30
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(LegendRow, self).ApplyAttributes(attributes)
        self.label = attributes.get('label')
        self.texturePath = attributes.get('texturePath')
        self.clickCallback = attributes.get('func', self.defaultClickCallback)
        self.active = attributes.get('active', True)
        self.ConstructLayout()

    def OnClick(self, *args):
        if self.active:
            self.active = False
            animations.FadeTo(self, startVal=TextColor.HIGHLIGHT.a, endVal=TextColor.DISABLED.a, duration=0.25)
        else:
            self.active = True
            animations.FadeTo(self, startVal=TextColor.DISABLED.a, endVal=TextColor.HIGHLIGHT.a, duration=0.25)
        self.clickCallback(self.active)

    def defaultClickCallback(self, active):
        pass

    def ConstructLayout(self):
        Container(name='spacer', parent=self, align=uiconst.TOLEFT, width=18)
        Sprite(parent=Transform(parent=self, align=uiconst.TOLEFT, width=32, height=32), texturePath=self.texturePath, align=uiconst.CENTERTOP, color=TextColor.HIGHLIGHT, top=2, width=16, height=16)
        EveLabelLarge(parent=self, align=uiconst.TOLEFT, text=self.label)
        if not self.active:
            self.opacity = TextColor.DISABLED.a
