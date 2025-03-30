#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkersHandler.py
import evetypes
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.util.color import Color
from eve.client.script.ui.inflight.scannerFiles.directionalScanIntersectUtil import IsWithinScanShape
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import GetScanAngle, GetScanRangeInMeters
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerContellation import MarkerLabelConstellation
from eve.client.script.ui.shared.mapView.markers.mapMarkerLandmark import MarkerLabelLandmark
from eve.client.script.ui.shared.mapView.markers.mapMarkerRegion import MarkerLabelRegion
from eve.client.script.ui.shared.mapView.markers.mapMarkerSolarSystem import MarkerLabelSolarSystem
from eve.client.script.ui.shared.mapView.mapViewUtil import IsDynamicMarkerType, MapPosToSolarSystemPos
import geo2
import telemetry
from eve.common.lib.appConst import OVERVIEW_AUTO_PILOT_DESTINATION_COLOR
from eve.common.script.sys import idCheckers

@telemetry.ZONE_METHOD
def DoMarkersIntersect(marker1Bound, marker2Bound):
    l1, t1, r1, b1 = marker1Bound
    l2, t2, r2, b2 = marker2Bound
    overlapX = not (r1 <= l2 or l1 >= r2)
    if overlapX:
        overlapY = not (b1 <= t2 or t1 >= b2)
        if overlapY:
            return True
    return False


@telemetry.ZONE_METHOD
def FindOverlaps(markers):
    isOverlapped = set()
    isOverlapping = {}
    for _sortVal, (bound1, marker1) in markers:
        if marker1.markerID in isOverlapped:
            continue
        for _sortVal, (bound2, marker2) in markers:
            if marker1 is marker2:
                continue
            if marker2.markerID in isOverlapped:
                continue
            intersect = DoMarkersIntersect(bound1, bound2)
            if intersect:
                isOverlapping.setdefault(marker1.markerID, []).append(marker2)
                isOverlapped.add(marker2.markerID)

    return (isOverlapping, isOverlapped)


class MapViewMarkersHandler(object):
    __notifyevents__ = ['OnDirectionalScannerShowCone',
     'OnDirectionalScanStarted',
     'OnDestinationSet',
     'OnNewState',
     'OnSecurityModified']
    __metaclass__ = telemetry.ZONE_PER_METHOD
    projectBrackets = None
    markerCurveSet = None
    markerLayer = None
    mapView = None
    disabledMarkers = None
    eventHandler = None
    clickTimer = None
    cameraTranslationFromParent = 1.0

    def __init__(self, mapView, markerCurveSet, markerLayer, eventHandler = None, stackMarkers = True, updateInterval = 500):
        sm.RegisterNotify(self)
        self.mapView = mapView
        self.projectBrackets = {}
        self.hilightMarkers = set()
        self.activeMarkers = set()
        self.selectedMarkerIDs = set()
        self.overlapMarkers = set()
        self.distanceSortedMarkers = set()
        self.markerCurveSet = markerCurveSet
        self.markerLayer = markerLayer
        self.eventHandler = eventHandler
        self.stackMarkers = stackMarkers
        self.updateTimer = AutoTimer(updateInterval, self.UpdateMarkers)
        self.isRegionSelected = False

    def __del__(self):
        sm.UnregisterNotify(self)
        self.StopHandler()

    def IsMarkerPickOverridden(self):
        if self.eventHandler:
            return self.eventHandler.MapMarkerPickingOverride()
        return False

    def GetIntersectingMarkersForMarker(self, checkMarkerObject):
        intersectingMarkers = []
        for markerID, markerObject in self.projectBrackets.iteritems():
            if markerObject and markerObject.markerContainer and not markerObject.markerContainer.destroyed:
                intersect = DoMarkersIntersect(checkMarkerObject.GetBoundaries(), markerObject.GetBoundaries())
                if intersect:
                    intersectingMarkers.append(markerObject)

        return intersectingMarkers

    def UpdateMarkers(self):
        distance_markers = []
        stack_markers = []
        activeAndHighlighted = self.hilightMarkers.union(self.activeMarkers)
        for markerID in activeAndHighlighted.union(self.distanceSortedMarkers):
            markerObject = self.projectBrackets.get(markerID, None)
            if markerObject and markerObject.markerContainer and not markerObject.markerContainer.destroyed:
                markerDistance = markerObject.GetCameraDistance()
                distance_markers.append((markerDistance, markerObject))
                if hasattr(markerObject, 'GetOverlapSortValue'):
                    markerBoundaries = markerObject.GetBoundaries()
                    stack_markers.append(((markerObject.GetOverlapSortValue(), markerDistance), (markerBoundaries, markerObject)))

        distanceSortedMarkers = sorted(distance_markers, reverse=True)
        for markerDistance, markerObject in distanceSortedMarkers:
            markerObject.MoveToFront()

        if self.stackMarkers:
            markersSorted = sorted(stack_markers)
            isOverlapping, isOverlapped = FindOverlaps(markersSorted)
            for sortOrderValue, (bound, markerObject) in reversed(markersSorted):
                markerID = markerObject.markerID
                if markerID in isOverlapping:
                    markerObject.RegisterOverlapMarkers(isOverlapping[markerID])
                elif markerID in isOverlapped:
                    markerObject.SetOverlappedState(True)
                else:
                    markerObject.SetOverlappedState(False)

    def OnNewState(self, state):
        self.UpdateGateMarkerYellowIfNextJump()

    def OnDestinationSet(self, *args):
        self.UpdateGateMarkerYellowIfNextJump()

    def UpdateGateMarkerYellowIfNextJump(self):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp or not self.projectBrackets:
            return
        for marker in self.projectBrackets.values():
            if not marker.typeID:
                continue
            if self.IsStargate(marker.typeID):
                destinationPath = sm.GetService('starmap').GetDestinationPath()
                slimItem = bp.slimItems.get(marker.itemID, None)
                if slimItem:
                    jumpToLocationID = slimItem.jumps[0].locationID
                    if destinationPath and jumpToLocationID == destinationPath[0]:
                        iconColor = OVERVIEW_AUTO_PILOT_DESTINATION_COLOR
                    else:
                        iconColor = Color.WHITE
                    marker.SetIconColor(iconColor)

    def OnSecurityModified(self, solar_system_id, modifier_amount, new_security):
        marker = self.GetMarkerByID(solar_system_id)
        if marker is not None:
            marker.UpdateLabelText()

    def IsStargate(self, typeID):
        return evetypes.GetGroupID(typeID) == const.groupStargate

    def UpdateDscanHilite(self, direction, egoPos):
        egoPos = MapPosToSolarSystemPos(egoPos)
        range = GetScanRangeInMeters()
        angle = GetScanAngle()
        for marker in self.projectBrackets.values():
            pos = marker.GetDisplayPosition()
            if pos == egoPos:
                continue
            pos = MapPosToSolarSystemPos(pos)
            if not marker.IsPartialResult() and IsWithinScanShape(pos, egoPos, angle, range, direction):
                marker.ShowDscanHilite()
            else:
                marker.HideDscanHilite()

    def HideAllDscanHilite(self):
        for marker in self.projectBrackets.values():
            marker.HideDscanHilite()

    def OnDirectionalScanStarted(self):
        if not self.projectBrackets:
            return
        for marker in self.projectBrackets.values():
            if marker.IsDscanHiliteShown():
                marker.AnimBlinkDscanHilite()

    def OnDirectionalScannerShowCone(self, isShown):
        if not isShown:
            self.HideAllDscanHilite()

    def GetExtraMouseOverInfoForMarker(self, markerID):
        if self.mapView:
            return self.mapView.GetExtraMouseOverInfoForItemID(markerID)

    def ReloadAll(self):
        for markerID, markerObject in self.projectBrackets.iteritems():
            if markerObject:
                markerObject.Reload()

    def SetDisplayStateOverrideFilter(self, markersToShow):
        filtering = bool(markersToShow)
        for markerID, markerObject in self.projectBrackets.iteritems():
            if IsDynamicMarkerType(markerObject.markerID):
                continue
            if not filtering or markerID in markersToShow:
                markerObject.displayStateOverride = None
            else:
                markerObject.displayStateOverride = False

    def UpdateMarkerPositions(self, changedSolarSystemPositions, yScaleFactor):
        for markerID, markerObject in self.projectBrackets.iteritems():
            if hasattr(markerObject, 'UpdateSolarSystemPosition') and markerObject.solarSystemID in changedSolarSystemPositions:
                mapNode = changedSolarSystemPositions[markerObject.solarSystemID]
                markerObject.UpdateSolarSystemPosition(mapNode.position)
            elif hasattr(markerObject, 'SetYScaleFactor'):
                markerObject.SetYScaleFactor(yScaleFactor)

    def StopHandler(self):
        self.updateTimer = None
        if self.projectBrackets:
            for markerID, markerObject in self.projectBrackets.iteritems():
                markerObject.Close()

        self.projectBrackets = None
        self.mapView = None
        self.markerLayer = None
        self.markerCurveSet = None
        self.eventHandler = None

    def OnMarkerMouseEnter(self, marker):
        self.mapView.OnMarkerHovered(marker.markerID)

    def OnMarkerMouseExit(self, marker):
        self.mapView.OnMarkerHovered(None)

    def OnMarkerSelected(self, marker):
        self.isRegionSelected = marker and idCheckers.IsRegion(marker.markerID)
        self.mapView.SetSelectedMarker(marker)

    def HilightMarkers(self, markerIDs, add = False):
        hilightMarkers = markerIDs
        if not add:
            for oldMarkerID in self.hilightMarkers:
                if oldMarkerID not in hilightMarkers:
                    oldMarker = self.GetMarkerByID(oldMarkerID)
                    if oldMarker:
                        oldMarker.SetHilightState(False)

        for newMarkerID in hilightMarkers:
            newMarker = self.GetMarkerByID(newMarkerID)
            if newMarker:
                newMarker.SetHilightState(True)

        if add:
            self.hilightMarkers = self.hilightMarkers.union(set(hilightMarkers))
        else:
            self.hilightMarkers = set(hilightMarkers)

    def UpdateMarkerState(self, markerIDs, selectedMarkerIDs = None):
        for oldMarkerID in self.activeMarkers:
            if oldMarkerID not in markerIDs:
                oldMarker = self.GetMarkerByID(oldMarkerID)
                if oldMarker:
                    oldMarker.SetActiveState(mapViewConst.MARKER_INACTIVE)

        for newMarkerID in markerIDs:
            newMarker = self.GetMarkerByID(newMarkerID)
            if newMarker:
                if newMarkerID in selectedMarkerIDs:
                    newMarker.SetActiveState(mapViewConst.MARKER_SELECTED)
                else:
                    newMarker.SetActiveState(mapViewConst.MARKER_ACTIVE)

        self.selectedMarkerIDs = set(selectedMarkerIDs)
        self.activeMarkers = set(markerIDs)

    def RefreshActiveAndHilightedMarkers(self):
        for marker in self.GetActiveAndHilightedMarkers():
            marker.UpdateActiveAndHilightState()

    def GetActiveAndHilightedMarkers(self):
        ret = set()
        for markerID in self.hilightMarkers.union(self.activeMarkers):
            marker = self.GetMarkerByID(markerID)
            if marker:
                ret.add(marker)

        return ret

    def GetMarkerState(self, markerID):
        if markerID in self.selectedMarkerIDs:
            return mapViewConst.MARKER_SELECTED
        elif markerID in self.activeMarkers:
            return mapViewConst.MARKER_ACTIVE
        else:
            return mapViewConst.MARKER_INACTIVE

    def IsActiveOrHilighted(self, markerID):
        return markerID in self.activeMarkers or markerID in self.hilightMarkers

    def IsHilighted(self, markerID):
        return markerID in self.hilightMarkers

    def IsSelected(self, markerID):
        return markerID in self.selectedMarkerIDs

    def IsRegionSelected(self):
        return self.isRegionSelected

    def RemoveMarker(self, markerID, fadeOut = False):
        try:
            self.overlapMarkers.remove(markerID)
        except:
            pass

        try:
            self.distanceSortedMarkers.remove(markerID)
        except:
            pass

        markerObject = self.projectBrackets.pop(markerID, None)
        if markerObject:
            if fadeOut:
                markerObject.FadeOutAndClose()
            else:
                markerObject.Close()

    def RemoveMarkersByType(self, markerType):
        markers = self.GetMarkersByType(markerType)
        markerIDs = set([ markerObject.markerID for markerObject in markers ])
        for markerID in markerIDs:
            self.RemoveMarker(markerID)

    def GetMarkerByID(self, markerID):
        return self.projectBrackets.get(markerID, None)

    def GetMarkersByType(self, markerType):
        return [ markerObject for markerID, markerObject in self.projectBrackets.iteritems() if isinstance(markerID, tuple) and markerID[0] == markerType ]

    def _AddPositionMarker(self, **kwds):
        markerID = kwds.get('markerID', None)
        if self.projectBrackets is not None and markerID in self.projectBrackets:
            return self.projectBrackets[markerID]
        if 'parentContainer' not in kwds:
            kwds['parentContainer'] = self.markerLayer
        kwds['curveSet'] = self.markerCurveSet
        kwds['markerHandler'] = self
        kwds['eventHandler'] = self.eventHandler
        markerClass = kwds.get('markerClass', None)
        markerObject = markerClass(**kwds)
        if self.projectBrackets is not None:
            self.projectBrackets[markerID] = markerObject
        markerObject.SetActiveState(self.GetMarkerState(markerID))
        return markerObject

    def RegisterMarker(self, markerObject):
        self.projectBrackets[markerObject.markerID] = markerObject

    def AddSolarSystemMarker(self, markerID, position, **kwds):
        return self.AddSolarSystemBasedMarker(markerID=markerID, solarSystemID=markerID, mapPositionSolarSystem=position, mapPositionLocal=(0, 0, 0), markerClass=MarkerLabelSolarSystem, **kwds)

    def AddConstellationMarker(self, markerID, position, **kwds):
        return self._AddPositionMarker(markerID=markerID, position=position, markerClass=MarkerLabelConstellation, **kwds)

    def AddRegionMarker(self, markerID, position, **kwds):
        return self._AddPositionMarker(markerID=markerID, position=position, markerClass=MarkerLabelRegion, **kwds)

    def AddLandmarkMarker(self, markerID, position, **kwds):
        return self._AddPositionMarker(markerID=markerID, position=position, markerClass=MarkerLabelLandmark, **kwds)

    def AddSolarSystemBasedMarker(self, markerID, markerClass, **kwds):
        if getattr(markerClass, 'distanceSortEnabled', False):
            self.distanceSortedMarkers.add(markerID)
            if getattr(markerClass, 'overlapEnabled', False):
                self.overlapMarkers.add(markerID)
        position = geo2.Vec3Add(kwds['mapPositionSolarSystem'], kwds['mapPositionLocal'])
        return self._AddPositionMarker(markerID=markerID, position=position, markerClass=markerClass, **kwds)

    def RegisterCameraTranslationFromParent(self, cameraTranslationFromParent):
        self.cameraTranslationFromParent = cameraTranslationFromParent
