#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\map.py
from eve.client.script.ui.services.insurgenceDashboardSvc import WrapCallbackWithErrorHandling
from functools import partial
import evecamera
from carbonui import uiconst
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.mapView import MapView
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_CSBLOB
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
from eve.common.script.util.facwarCommon import GetInsurgencyEnemyFactions, IsPirateFWFaction, IsOccupierFWFaction
from pirateinsurgency.client.dashboard.const import WARZONE_ID_TO_PIRATE_FACTION_ID
from pirateinsurgency.client.dashboard.mapMarker import InsurgencyBlobMarker

class MapPanel(MapView):
    cameraID = evecamera.CAM_INSURGENCY_MAP
    default_allowedSystems = [30002799,
     30002794,
     30002795,
     30002796]

    def ApplyAttributes(self, attributes):
        self.loadedSystems = False
        self.insurgencySystems = attributes.get('insurgencySystems', MapPanel.default_allowedSystems)
        self.dashboardSvc = attributes.get('dashboardSvc')
        self.campaignIDs = attributes.get('campaignIDs')
        self.systemIDToCampaignID = {}
        allowedSystemsSet = set(self.insurgencySystems)
        mapCacheData = mapViewData.GetStarMapCache()
        for snapshot in self.dashboardSvc.GetCurrentCampaignSnapshots():
            neighbouringSystemIDs = []
            for systemID in snapshot.coveredSolarsystemIDs:
                self.systemIDToCampaignID[systemID] = snapshot.campaignID
                neighbours = mapCacheData['solarSystems'][systemID]['neighbours']
                neighbouringSystemIDs.extend(neighbours)

            allowedSystemsSet.update(neighbouringSystemIDs)
            for systemID in neighbouringSystemIDs:
                self.systemIDToCampaignID[systemID] = snapshot.campaignID

        self.allowedSystems = list(allowedSystemsSet)
        self.initialInterestID = None
        focusSystem = self.GetBestFocusSystem()
        if focusSystem:
            self.initialInterestID = focusSystem
        else:
            self.initialInterestID = self.allowedSystems[0]
        super(MapPanel, self).ApplyAttributes(attributes)
        self.systems = {}

    def _ConstructScene(self, _interestID, zoomToItem, mapFilterID):
        self.sceneContainer.Hide()
        loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER)
        self.sceneContainer.Startup()
        self.camera.SetUpdateCallback(self.OnCameraUpdate)
        self.ConstructStarDataTexture()
        self.ConstructMapScene()
        self.ConstructMapRoot()
        self.ConstructMarkersHandler()
        self.ConstructBookmarkHandler()
        self.CreateStarParticles()
        self.CreateJumpLineSet()
        self.LoadJumpLines()
        self.UpdateMapLayout()
        self.ReconstructMyLocationMarker()
        self.ShowMyHomeStation()
        self._SetActiveItemID(self.initialInterestID)
        self.CheckLoadAllMarkers()
        self.InitCameraFocus(zoomToItem, mapFilterID)
        self.constructSceneThread = None
        loadingWheel.Hide()
        self.sceneContainer.Show()
        for campaignID in self.campaignIDs:
            fun = partial(self.ShowBlobs, snapshot=self.dashboardSvc.GetCurrentCampaignSnapshotByID(campaignID))
            wrappedCallback = WrapCallbackWithErrorHandling(fun, parentContainer=None)
            self.dashboardSvc.RequestAllCorruptionAndSuppressionValuesForCampaignID(campaignID, wrappedCallback)

    def PrintResult(self, data):
        print data

    def ShowBlobs(self, data, snapshot = None):
        if self.destroyed:
            return
        corruptionData = data['corruption']
        suppressionData = data['suppression']
        for solarSystemID, data in corruptionData.iteritems():
            corruptionStage = data.stage
            mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
            solarSystemPosition = mapNode.position
            localPosition = self.SolarSystemPosToMapPos(solarSystemPosition)
            markerID = (MARKERID_CSBLOB, solarSystemID)
            suppressionStage = suppressionData[solarSystemID].stage
            iceHeist = None
            iceHeistDungeons = self.dashboardSvc.GetIceHeistInstances_Memoized()
            if solarSystemID in iceHeistDungeons and iceHeistDungeons[solarSystemID]:
                iceHeist = iceHeistDungeons[solarSystemID]
            self.markersHandler.AddSolarSystemBasedMarker(markerID, InsurgencyBlobMarker, snapshot=snapshot, solarSystemID=solarSystemID, mapPositionLocal=localPosition, mapPositionSolarSystem=solarSystemPosition, texturePath='res:/UI/Texture/classes/pirateinsurgencies/map/CorruptionCircle05.png', corruptionStage=corruptionStage, suppressionStage=suppressionStage, dashboardSvc=self.dashboardSvc, iceHeist=iceHeist)
            self.markersAlwaysVisible.add(markerID)

    def LoadJumpLines(self):
        self.allianceJumpLines = []
        self.jumpLineInfoByLineID = {}
        self.allJumpBridges = []
        self.myJumpBridges = []
        lineSet = self.solarSystemJumpLineSet
        defaultColor = (0, 0, 0, 0)
        defaultPos = (0, 0, 0)
        for lineData in mapViewData.IterateJumps():
            lineID = lineSet.AddStraightLine(defaultPos, defaultColor, defaultPos, defaultColor, mapViewConst.JUMPLINE_BASE_WIDTH)
            lineData.lineID = lineID
            fromNode = self.layoutHandler.GetNodeBySolarSystemID(lineData.fromSolarSystemID)
            toNode = self.layoutHandler.GetNodeBySolarSystemID(lineData.toSolarSystemID)
            if fromNode is not None and toNode is not None and lineData.fromSolarSystemID in self.allowedSystems and lineData.toSolarSystemID in self.allowedSystems:
                fromNode.AddLineData(lineData)
                toNode.AddLineData(lineData)
                self.jumpLineInfoByLineID[lineID] = lineData

    def SetSelectedMarker(self, markerObject, **kwds):
        super(MapPanel, self).SetSelectedMarker(markerObject, **kwds)
        if markerObject.solarSystemID is not None:
            self.dashboardSvc.OnSolarSystemSelectedFromMap(markerObject.solarSystemID)

    def ReconstructMyLocationMarker(self):
        pass

    def ShowMyHomeStation(self):
        pass

    def _GetKnownUniverseSolarSystems(self):
        if self.loadedSystems:
            return self.systems
        for systemID, system in mapViewData.GetKnownUniverseSolarSystems().iteritems():
            if systemID in self.allowedSystems:
                self.systems[systemID] = system

        return self.systems

    def _GetKnownUniverseConstellations(self):
        constellations = set()
        for systemID, system in self._GetKnownUniverseSolarSystems().iteritems():
            constellations.add(system.constellationID)

        constellationData = {}
        for constellationID in constellations:
            constellationData[constellationID] = mapViewData.GetKnownUniverseConstellations()[constellationID]

        return constellationData

    def _GetKnownUniverseRegions(self):
        regions = set()
        for systemID, system in self._GetKnownUniverseSolarSystems().iteritems():
            regions.add(system.regionID)

        regionData = {}
        for regionID in regions:
            regionData[regionID] = mapViewData.GetKnownUniverseRegions()[regionID]

        return regionData

    def GetBestFocusSystem(self):
        campaignSnapshots = self.dashboardSvc.GetCurrentCampaignSnapshots()
        if len(campaignSnapshots) == 0:
            return
        if session.solarsystemid2 in self.allowedSystems:
            return session.solarsystemid2
        if session.warfactionid is not None:
            if IsOccupierFWFaction(session.warfactionid):
                enemyPirateFactions = GetInsurgencyEnemyFactions(session.warfactionid)
                FOBSystem = None
                for id in enemyPirateFactions:
                    FOBSystem = self.GetPirateFactionFOBSystem(id, campaignSnapshots)
                    if FOBSystem is not None:
                        break

                if FOBSystem is not None:
                    return FOBSystem
            elif IsPirateFWFaction(session.warfactionid):
                FOBSystemID = self.GetPirateFactionFOBSystem(session.warfactionid, campaignSnapshots)
                if FOBSystemID is not None:
                    return FOBSystemID
        return campaignSnapshots[0].originSolarsystemID

    def GetPirateFactionFOBSystem(self, pirateFactionID, campaignSnapshots):
        FOBSystemID = None
        for snapshot in campaignSnapshots:
            if WARZONE_ID_TO_PIRATE_FACTION_ID[snapshot.warzoneID] == pirateFactionID:
                FOBSystemID = snapshot.originSolarsystemID

        return FOBSystemID

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid' in change:
            lastSystem, newSystem = change['solarsystemid']
            if self.activeItemID == lastSystem and newSystem in self.allowedSystems:
                self.dashboardSvc.OnSolarSystemSelectedFromMap(newSystem)
                self.SetActiveItemID(newSystem, zoomToItem=True)

    def LoadVulnerableSkyhooks(self):
        pass
