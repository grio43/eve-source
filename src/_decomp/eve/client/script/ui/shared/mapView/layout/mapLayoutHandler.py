#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\layout\mapLayoutHandler.py
import weakref
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.layout.mapLayoutConstellations import MapLayoutConstellations
from eve.client.script.ui.shared.mapView.layout.mapLayoutRegions import MapLayoutRegions
from eve.client.script.ui.shared.mapView.layout.mapLayoutSolarSystems import MapLayoutSolarSystems
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_LAYOUT_REGIONS, VIEWMODE_LAYOUT_CONSTELLATIONS, VIEWMODE_LAYOUT_SOLARSYSTEM, JUMPBRIDGE_CURVE_SCALE, JUMPBRIDGE_TYPE, WORKFORCE_TRANSPORT_CONFIG_TYPE, WORKFORCE_TRANSPORT_STATE_TYPE
from eve.client.script.ui.shared.mapView.mapViewUtil import ScaleSolarSystemValue
import uthread
import blue
import geo2
layoutClassMapping = {VIEWMODE_LAYOUT_SOLARSYSTEM: MapLayoutSolarSystems,
 VIEWMODE_LAYOUT_REGIONS: MapLayoutRegions,
 VIEWMODE_LAYOUT_CONSTELLATIONS: MapLayoutConstellations}

class MapViewLayoutNode(object):
    dirty = False

    def __init__(self, particleID, solarSystemID, position, system):
        self.particleID = particleID
        self.solarSystemID = solarSystemID
        self.system = system
        self.lineData = set()
        self.position = position
        self.oldPosition = None
        self.animPosition = None

    def AddLineData(self, lineData):
        self.lineData.add(lineData)

    def SetPosition(self, position):
        self.position = position

    def UpdateAnimPosition(self, ndt):
        self.animPosition = geo2.Vec3Lerp(self.oldPosition, self.position, ndt)


class MapViewLayoutHandler(object):
    starParticles = None
    jumpLineSet = None
    workforceTransportLineSet = None
    layoutDirty = False
    starGateAdjusted = None
    expandedSolarSystemID = None
    lineAdjustmentOffset = {}
    morph_to_index = 0
    transformTime = 500.0
    currentLayout = None

    def StopHandler(self):
        try:
            self.updateThread.kill()
        except:
            pass

    def __init__(self, mapView):
        self.mapView = weakref.proxy(mapView)
        self.nodesByParticleID = {}
        self.nodesBySolarSystemID = {}
        self.dirtyNodesBySolarSystemID = {}
        self.layouts = {}

    def __del__(self):
        self.nodesByParticleID = None
        self.nodesBySolarSystemID = None
        self.dirtyNodesBySolarSystemID = None
        self.layouts = None

    def __len__(self):
        return len(self.nodesByParticleID)

    def ClearCache(self):
        for layoutType, mapLayout in self.layouts.iteritems():
            mapLayout.ClearCache()

        self.currentLayout = None

    def LoadLayout(self, layoutType, *args, **kwds):
        if self.currentLayout == (layoutType, args, kwds):
            return
        self.currentLayout = (layoutType, args, kwds)
        if layoutType not in self.layouts:
            self.layouts[layoutType] = layoutClassMapping[layoutType](self)
        mapLayout = self.layouts[layoutType]
        mapLayout.PrimeLayout(*args, **kwds)
        self.mapLayout = mapLayout
        for solarSystemID, position in mapLayout.positionsBySolarSystemID.iteritems():
            if solarSystemID in self.nodesBySolarSystemID:
                mapNode = self.nodesBySolarSystemID[solarSystemID]
                if not mapNode.position or not geo2.Vec3Equal(mapNode.position, position):
                    mapNode.oldPosition = mapNode.position or position
                    mapNode.SetPosition(position)
                    self.dirtyNodesBySolarSystemID[solarSystemID] = mapNode

        if self.dirtyNodesBySolarSystemID:
            self.Update()

    def Update(self):
        uthread.new(self._Update)

    def _Update(self):
        if not self.mapView or self.mapView.destroyed:
            return
        if not (self.jumpLineSet and self.starParticles):
            return
        self.mapView.LayoutChangeStarting(self.dirtyNodesBySolarSystemID)
        self.mapView.SetMarkersFilter(self.mapLayout.visibleMarkers)
        adjustLines, dirtyNodes = self.AdjustStarGateLines()
        for mapNode in dirtyNodes:
            if mapNode.solarSystemID not in self.dirtyNodesBySolarSystemID:
                mapNode.oldPosition = mapNode.position
                self.dirtyNodesBySolarSystemID[mapNode.solarSystemID] = mapNode

        self.AnimateNodes(self.dirtyNodesBySolarSystemID, adjustLines, self.mapView)
        self.mapView.LayoutChangeCompleted(self.dirtyNodesBySolarSystemID)
        self.dirtyNodesBySolarSystemID = {}

    def AnimateNodes(self, nodesBySolarSystemID, adjustLines, mapView):
        start = blue.os.GetWallclockTime()
        ndt = 0.0
        dirtyLines = set()
        worldUp = geo2.Vector(0.0, -1.0, 0.0)
        while ndt != 1.0:
            try:
                ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / self.transformTime, 1.0)
                for mapNode in nodesBySolarSystemID.itervalues():
                    mapNode.UpdateAnimPosition(ndt)
                    dirtyLines.update(mapNode.lineData)
                    self.starParticles.SetItemElement(mapNode.particleID, 0, mapNode.animPosition)

                for lineData in dirtyLines:
                    self.UpdateLinePosition(lineData, adjustLines, worldUp)

                self.starParticles.UpdateData()
                self.jumpLineSet.SubmitChanges()
                if self.workforceTransportLineSet:
                    self.workforceTransportLineSet.SubmitChanges()
                mapView.LayoutChanging(ndt, nodesBySolarSystemID)
                blue.pyos.synchro.Yield()
            except ReferenceError:
                return

    def UpdateLinePosition(self, lineData, adjustLines, worldUp):
        fromMapNode = self.GetNodeBySolarSystemID(lineData.fromSolarSystemID)
        fromPosition = fromMapNode.animPosition or fromMapNode.position
        toMapNode = self.GetNodeBySolarSystemID(lineData.toSolarSystemID)
        toPosition = toMapNode.animPosition or toMapNode.position
        if lineData.lineID in adjustLines:
            fromPosition = geo2.Vec3Add(fromPosition, adjustLines[lineData.lineID][0])
            toPosition = geo2.Vec3Add(toPosition, adjustLines[lineData.lineID][2])
        if lineData.jumpType in (WORKFORCE_TRANSPORT_STATE_TYPE, WORKFORCE_TRANSPORT_CONFIG_TYPE):
            if lineData.jumpType == WORKFORCE_TRANSPORT_CONFIG_TYPE:
                curveScale = 0.5
            else:
                curveScale = 1.25
            self.workforceTransportLineSet.ChangeLinePositionCrt(lineData.lineID, fromPosition, toPosition)
            self.UpdateCurvedLinePosition(fromPosition, lineData, toPosition, worldUp, self.workforceTransportLineSet, curveScale)
        else:
            self.jumpLineSet.ChangeLinePositionCrt(lineData.lineID, fromPosition, toPosition)
            if lineData.jumpType == JUMPBRIDGE_TYPE:
                self.UpdateCurvedLinePosition(fromPosition, lineData, toPosition, worldUp, self.jumpLineSet)

    def UpdateCurvedLinePosition(self, fromPosition, lineData, toPosition, worldUp, lineSet, curveScale = 1.0):
        linkVec = geo2.Vec3Subtract(toPosition, fromPosition)
        normLinkVec = geo2.Vec3Normalize(linkVec)
        rightVec = geo2.Vec3Cross(worldUp, normLinkVec)
        upVec = geo2.Vec3Cross(rightVec, normLinkVec)
        offsetVec = geo2.Vec3Scale(geo2.Vec3Normalize(upVec), geo2.Vec3Length(linkVec) * curveScale)
        midPos = geo2.Vec3Scale(geo2.Vec3Add(toPosition, fromPosition), 0.5)
        splinePos = geo2.Vec3Add(midPos, offsetVec)
        lineSet.ChangeLineIntermediateCrt(lineData.lineID, splinePos)

    def SetExpandedSolarSystemID(self, solarSystemID = None):
        self.expandedSolarSystemID = solarSystemID
        self.Update()

    def RegisterStarParticles(self, starParticles):
        self.starParticles = weakref.proxy(starParticles)

    def RegisterJumpLineSet(self, jumpLineSet):
        self.jumpLineSet = weakref.proxy(jumpLineSet)

    def RegisterTransitLineSet(self, workforceTransportLineSet):
        self.workforceTransportLineSet = weakref.proxy(workforceTransportLineSet)

    def CreateSolarSystemNode(self, particleID, solarSystemID, position, system):
        node = MapViewLayoutNode(particleID, solarSystemID, position, system)
        self.nodesByParticleID[particleID] = node
        self.nodesBySolarSystemID[solarSystemID] = node
        return node

    def GetNodesIter(self):
        return self.nodesByParticleID.itervalues()

    def GetNodesByParticleID(self):
        return self.nodesByParticleID

    def GetNodeByParticleID(self, particleID):
        return self.nodesByParticleID.get(particleID, None)

    def GetNodeBySolarSystemID(self, solarSystemID):
        return self.nodesBySolarSystemID.get(solarSystemID, None)

    def GetNodesBySolarSystemIDs(self, solarSystemIDs):
        return [ self.nodesBySolarSystemID[solarSystemID] for solarSystemID in solarSystemIDs if solarSystemID in self.nodesBySolarSystemID ]

    def GetLineData(self):
        lineIDs = set()
        for solarSystemID, mapNode in self.nodesBySolarSystemID.iteritems():
            for lineData in mapNode.lineData:
                if lineData.lineID in lineIDs:
                    continue
                lineIDs.add(lineData.lineID)
                yield lineData

    def AdjustStarGateLines(self):
        adjustLines = {}
        dirtyNodes = set()
        if self.starGateAdjusted != self.expandedSolarSystemID and self.lineAdjustmentOffset:
            self.starGateAdjusted = None
            for lineID, (fromSolarSystemID, toSolarSystemID, offsetFromPosition, offsetToPosition, jumpType) in self.lineAdjustmentOffset.iteritems():
                fromMapNode = self.GetNodeBySolarSystemID(fromSolarSystemID)
                toMapNode = self.GetNodeBySolarSystemID(toSolarSystemID)
                adjustLines[lineID] = ((0, 0, 0),
                 offsetFromPosition,
                 (0, 0, 0),
                 offsetToPosition)
                dirtyNodes.add(fromMapNode)
                dirtyNodes.add(toMapNode)

        if self.expandedSolarSystemID:
            applyOffset = self.GetStarGateLineOffsets(self.expandedSolarSystemID)
            self.starGateAdjusted = self.expandedSolarSystemID
            for lineID, (fromSolarSystemID, toSolarSystemID, offsetFromPosition, offsetToPosition, jumpType) in applyOffset.iteritems():
                if lineID in self.lineAdjustmentOffset:
                    oldOffsetFromPosition = self.lineAdjustmentOffset[lineID][2]
                    oldOffsetToPosition = self.lineAdjustmentOffset[lineID][3]
                else:
                    oldOffsetFromPosition = oldOffsetToPosition = (0, 0, 0)
                fromMapNode = self.GetNodeBySolarSystemID(fromSolarSystemID)
                toMapNode = self.GetNodeBySolarSystemID(toSolarSystemID)
                adjustLines[lineID] = (offsetFromPosition,
                 oldOffsetFromPosition,
                 offsetToPosition,
                 oldOffsetToPosition)
                dirtyNodes.add(fromMapNode)
                dirtyNodes.add(toMapNode)

            self.lineAdjustmentOffset = applyOffset
        return (adjustLines, dirtyNodes)

    def GetStarGateLineOffsets(self, solarSystemID):
        fromSystemInfo = cfg.mapSolarSystemContentCache[solarSystemID]
        adjustLines = {}
        mapNode = self.GetNodeBySolarSystemID(solarSystemID)
        if not mapNode:
            return adjustLines
        for lineData in mapNode.lineData:
            if solarSystemID == lineData.fromSolarSystemID:
                otherSystemInfo = cfg.mapSolarSystemContentCache[lineData.toSolarSystemID]
            else:
                otherSystemInfo = cfg.mapSolarSystemContentCache[lineData.fromSolarSystemID]
            fromStargateVector = None
            for each in fromSystemInfo.stargates:
                if fromSystemInfo.stargates[each].destination in otherSystemInfo.stargates:
                    fromStargate = fromSystemInfo.stargates[each]
                    fromStargateVector = (fromStargate.position.x, fromStargate.position.y, fromStargate.position.z)
                    break

            if fromStargateVector:
                stargateOffset = geo2.Vec3Scale(fromStargateVector, ScaleSolarSystemValue(mapViewConst.SCALING_SOLARSYSTEMINWORLDMAP))
                if solarSystemID == lineData.fromSolarSystemID:
                    adjustLines[lineData.lineID] = (lineData.fromSolarSystemID,
                     lineData.toSolarSystemID,
                     stargateOffset,
                     (0, 0, 0),
                     lineData.jumpType)
                else:
                    adjustLines[lineData.lineID] = (lineData.fromSolarSystemID,
                     lineData.toSolarSystemID,
                     (0, 0, 0),
                     stargateOffset,
                     lineData.jumpType)

        return adjustLines

    def GetDistanceBetweenSolarSystems(self, fromSolarSystemID, toSolarSystemID):
        fromMapNode = self.GetNodeBySolarSystemID(fromSolarSystemID)
        toMapNode = self.GetNodeBySolarSystemID(toSolarSystemID)
        if fromMapNode and toMapNode:
            return geo2.Vec3Length(geo2.Vec3Subtract(fromMapNode.position, toMapNode.position))
