#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\workforce.py
import geo2
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.mapViewBookmarkHandler import IsMarkerGroupEnabled
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERS_OPTION_SOV_HUBS, MARKERID_SOVHUBS, WORKFORCE_TRANSPORT_STATE_TYPE, WORKFORCE_TRANSPORT_CONFIG_TYPE
from eve.client.script.ui.shared.mapView.markers.mapMarkerSovHub import MarkerSovHub
from eve.common.script.sys.idCheckers import IsSolarSystem
from evemap.workforceUtil import GetStateAndConfigByHubID, GetOtherStateAndSystems, GetSystemsForConfigs
from sovereignty.workforce import workforceConst
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
import logging
logger = logging.getLogger(__name__)
IMPORT_STATE_COLOR = (191 / 255.0,
 0,
 207 / 255.0,
 1.0)
EXPORT_STATE_COLOR = (0.0, 0.0, 1.0, 1.0)
IMPORT_CONFIG_COLOR = IMPORT_STATE_COLOR
EXPORT_CONFIG_COLOR = (0.0, 0.0, 1.0, 1.0)

class MapViewSovHubHandler(object):
    __notifyevents__ = ['OnSovHubMarkersChanged']

    def __init__(self, mapView):
        self.mapView = mapView
        sm.RegisterNotify(self)

    @property
    def workforceTransportLineSet(self):
        return self.mapView.workforceTransportLineSet

    def OnSovHubMarkersChanged(self):
        self.LoadShowHubMarkers()

    def LoadShowHubMarkers(self):
        if self.mapView.destroyed:
            return
        if not CanSeeSovHubs() or not session.allianceid:
            return
        isStationManager = session.corprole & const.corpRoleStationManager
        if not isStationManager:
            return
        showSovHubMarkers = IsMarkerGroupEnabled(MARKERS_OPTION_SOV_HUBS, self.mapView.mapViewID)
        markersHandler = self.mapView.markersHandler
        if not showSovHubMarkers:
            sovHubMarkers = markersHandler.GetMarkersByType(MARKERID_SOVHUBS)
            sovHubMarkerIDs = set([ markerObject.markerID for markerObject in sovHubMarkers ])
            for removeMarkerID in sovHubMarkerIDs:
                markersHandler.RemoveMarker(removeMarkerID)

            self.workforceTransportLineSet.ClearLines()
            self.workforceTransportLineSet.SubmitChanges()
            return
        svcSvc = sm.GetService('sov')
        sovHubSvc = sm.GetService('sovHubSvc')
        networkedHubByItemID = GetStateAndConfigByHubID(svcSvc, sovHubSvc)
        for hubID, hubStateConfig in networkedHubByItemID.iteritems():
            ssID = hubStateConfig.solarSystemID
            markerID = (MARKERID_SOVHUBS, ssID)
            mapNode = self.mapView.layoutHandler.GetNodeBySolarSystemID(ssID)
            solarSystemPosition = mapNode.position
            sovHubKwds = {'hubStateConfig': hubStateConfig}
            marker = markersHandler.AddSolarSystemBasedMarker(markerID, markerClass=MarkerSovHub, solarSystemID=ssID, mapPositionSolarSystem=solarSystemPosition, mapPositionLocal=(0, 0, 0), idx=0, **sovHubKwds)
            marker.SetMarkerKwds(sovHubKwds)
            self.mapView.markersAlwaysVisible.add(markerID)

        self.LoadTransportLines(networkedHubByItemID)

    def LoadTransportLines(self, networkedHubByItemID):
        newLineData = []
        self.workforceTransportLineSet.ClearLines()
        newLineDataState, addedPairs = self._LoadStateTransportLines(networkedHubByItemID)
        newLineData.extend(newLineDataState)
        newLineDataConfig = self._LoadConfigTransportLines(networkedHubByItemID, addedPairs)
        configLineIDs = [ lineData.lineID for lineData in newLineDataConfig ]
        newLineData.extend(newLineDataConfig)
        worldUp = geo2.Vector(0.0, -1.0, 0.0)
        for eachLineData in newLineData:
            self.mapView.layoutHandler.UpdateLinePosition(eachLineData, {}, worldUp)

        if self.workforceTransportLineSet:
            for lineID in configLineIDs:
                self.workforceTransportLineSet.ChangeLineAnimation(lineID, (0, 0, 0, 1), 0.0, 100)
                self.workforceTransportLineSet.ChangeLineWidth(lineID, mapViewConst.JUMPLINE_BASE_WIDTH * 1.3)

            self.workforceTransportLineSet.SubmitChanges()

    def _LoadStateTransportLines(self, networkedHubByItemID):
        defaultPos = (0, 0, 0)
        lineWidth = 3
        newLineData = []
        addedStatePairs = {}
        for hubID, hubInfo in networkedHubByItemID.iteritems():
            solarSystemA = hubInfo.solarSystemID
            otherState, solarSystemBsState = GetOtherStateAndSystems(hubInfo)
            if otherState is None:
                continue
            hubStateMode = hubInfo.hubState.get_mode()
            for ssB in solarSystemBsState:
                if not IsSolarSystem(solarSystemA) or not IsSolarSystem(ssB):
                    logger.warn("_LoadStateTransportLines had entry that wasn't a solarsystem: %s, %s" % (solarSystemA, ssB))
                    continue
                sortedInfo = sorted([(solarSystemA, hubStateMode), (ssB, otherState)], key=lambda x: x[0])
                pairKey = tuple([ x[0] for x in sortedInfo ])
                pairStates = [ x[1] for x in sortedInfo ]
                existingPair = addedStatePairs.get(pairKey, None)
                if existingPair and existingPair != pairStates:
                    logger.exception("states don't match :(")
                    continue
                addedStatePairs[pairKey] = pairStates
                if hubStateMode == workforceConst.MODE_IMPORT:
                    colorA = IMPORT_STATE_COLOR
                    colorB = EXPORT_STATE_COLOR
                else:
                    colorA = EXPORT_STATE_COLOR
                    colorB = IMPORT_STATE_COLOR
                lineID = self.workforceTransportLineSet.AddCurvedLineCrt(defaultPos, colorA, defaultPos, colorB, (1, 1, 1), lineWidth)
                lineData = mapViewData.PrimeJumpData(solarSystemA, ssB, WORKFORCE_TRANSPORT_STATE_TYPE, colorA, colorB)
                lineData.lineID = lineID
                newLineData.append(lineData)

        return (newLineData, addedStatePairs.keys())

    def _LoadConfigTransportLines(self, networkedHubByItemID, addedPairs):
        existingLines = {}
        defaultPos = (0, 0, 0)
        lineWidth = 3
        newLineData = []
        for hubID, hubInfo in networkedHubByItemID.iteritems():
            solarSystemA = hubInfo.solarSystemID
            solarSystemBsConfig = GetSystemsForConfigs(hubInfo)
            if solarSystemBsConfig is None:
                continue
            hubConfigMode = hubInfo.hubConfig.get_mode()
            for ssB in solarSystemBsConfig:
                if not IsSolarSystem(solarSystemA) or not IsSolarSystem(ssB):
                    logger.warn("_LoadConfigTransportLines had entry that wasn't a solarsystem: %s, %s" % (solarSystemA, ssB))
                    continue
                pairKey = tuple(sorted([solarSystemA, ssB]))
                if pairKey in addedPairs:
                    continue
                existingLineData = existingLines.get(pairKey, None)
                if hubConfigMode == workforceConst.MODE_IMPORT:
                    colorA = IMPORT_CONFIG_COLOR
                else:
                    colorA = EXPORT_CONFIG_COLOR
                if existingLineData:
                    if solarSystemA == existingLineData.toSolarSystemID:
                        self.workforceTransportLineSet.ChangeLineColor(existingLineData.lineID, existingLineData.colorFrom, colorA)
                    else:
                        self.workforceTransportLineSet.ChangeLineColor(existingLineData.lineID, colorA, existingLineData.colorTo)
                else:
                    colorB = (0.0, 0.0, 0.0, 1.0)
                    lineID = self.workforceTransportLineSet.AddCurvedLineCrt(defaultPos, colorA, defaultPos, colorB, defaultPos, lineWidth)
                    lineData = mapViewData.PrimeJumpData(solarSystemA, ssB, WORKFORCE_TRANSPORT_CONFIG_TYPE, colorA, colorB)
                    lineData.lineID = lineID
                    existingLines[pairKey] = lineData
                    newLineData.append(lineData)

        return newLineData


def CanSeeSovHubs():
    if not session.allianceid:
        return False
    isStationManager = session.corprole & const.corpRoleStationManager
    if not isStationManager:
        return False
    return True
