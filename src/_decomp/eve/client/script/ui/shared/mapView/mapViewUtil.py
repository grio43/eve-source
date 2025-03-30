#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewUtil.py
import math
import sys
from math import sin, cos
import geo2
import trinity
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsSolarSystemMapFullscreen, IsDirectionalScanPanelEmbedded, SetDirectionalScanEmbeddedPanelClosed, SetProbeScanEmbeddedPanelClosed, SetDirectionalScanEmbeddedPanelOpen, SetProbeScanEmbeddedPanelOpen
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.mapViewConst import MARKER_TYPES, UNIVERSE_SCALE, SOLARSYSTEM_SCALE
from eve.client.script.ui.shared.mapView.settings import classic_map_enabled_setting
from carbonui.uicore import uicore

def GetBoundingSphereRadiusCenter(vectors, yScaleFactor = None):
    minX = sys.maxint
    minY = sys.maxint
    minZ = sys.maxint
    maxX = -sys.maxint
    maxY = -sys.maxint
    maxZ = -sys.maxint
    for x, y, z in vectors:
        if yScaleFactor:
            y *= yScaleFactor
        minX = min(minX, x)
        minY = min(minY, y)
        minZ = min(minZ, z)
        maxX = max(maxX, x)
        maxY = max(maxY, y)
        maxZ = max(maxZ, z)

    maxBound = (maxX, maxY, maxZ)
    minBound = (minX, minY, minZ)
    center = geo2.Vec3Scale(geo2.Vec3Add(minBound, maxBound), 0.5)
    offset = geo2.Vec3Scale(geo2.Vec3Subtract(minBound, maxBound), 0.5)
    return (center, geo2.Vec3Length(offset))


def GetTranslationFromParentWithRadius(radius, camera):
    camangle = camera.fov * 0.5
    translationFromParent = max(mapViewConst.MIN_CAMERA_DISTANCE, min(mapViewConst.MAX_CAMERA_DISTANCE, radius / sin(camangle) * cos(camangle)))
    return translationFromParent


def SolarSystemPosToMapPos(position):
    if not position:
        return
    x, y, z = position
    return (ScaleSolarSystemValue(x), ScaleSolarSystemValue(y), ScaleSolarSystemValue(z))


def MapPosToSolarSystemPos(position):
    if not position:
        return
    x, y, z = position
    return (x / SOLARSYSTEM_SCALE, y / SOLARSYSTEM_SCALE, z / SOLARSYSTEM_SCALE)


def WorldPosToMapPos(position):
    x, y, z = position
    return (x * -UNIVERSE_SCALE, y * -UNIVERSE_SCALE, z * UNIVERSE_SCALE)


def ScaledPosToMapPos(pos):
    x, y, z = pos
    return (-x, -y, z)


def ScaleSolarSystemValue(value):
    return value * SOLARSYSTEM_SCALE


def IsDynamicMarkerType(itemID):
    try:
        if itemID[0] in MARKER_TYPES:
            return True
    except:
        return False


def IsLandmark(itemID):
    return itemID and itemID < 0


def IsDirectionalScannerOpen():
    if IsDirectionalScanPanelEmbedded():
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        w = SolarSystemViewPanel.GetIfOpen()
        return w and w.IsDirectionalScannerOpen()
    else:
        from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
        return DirectionalScanner.IsOpen()


def ToggleSolarSystemMap(openProbeScanPanel = False, openDirectionalScanPanel = False):
    if IsSolarSystemMapFullscreen():
        _ToggleSolarSystemMapFullscreen(openDirectionalScanPanel, openProbeScanPanel)
    else:
        _ToggleSolarSystemMapWindowed(openDirectionalScanPanel, openProbeScanPanel)


def _ToggleSolarSystemMapFullscreen(openDirectionalScanPanel, openProbeScanPanel):
    from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
    w = SolarSystemViewPanel.GetIfOpen()
    if not w:
        if openDirectionalScanPanel:
            SetDirectionalScanEmbeddedPanelOpen()
        if openProbeScanPanel:
            SetProbeScanEmbeddedPanelOpen()
        SolarSystemViewPanel.Open()
    elif not openDirectionalScanPanel and not openProbeScanPanel:
        w.Close()
    else:
        if openDirectionalScanPanel:
            w.ToggleDirectionalScanner()
        if openProbeScanPanel:
            w.ToggleProbeScanner()


def _ToggleSolarSystemMapWindowed(openDirectionalScanPanel, openProbeScanPanel):
    from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
    w = SolarSystemViewPanel.GetIfOpen()
    if w:
        if w.mapView and session.solarsystemid2 and (openProbeScanPanel or openDirectionalScanPanel):
            if openDirectionalScanPanel:
                w.ToggleDirectionalScanner()
            if openProbeScanPanel:
                w.ToggleProbeScanner()
        elif w.IsMinimized():
            w.Maximize()
        else:
            SolarSystemViewPanel.CloseIfOpen()
    else:
        if openDirectionalScanPanel:
            SetDirectionalScanEmbeddedPanelOpen()
        if openProbeScanPanel:
            SetProbeScanEmbeddedPanelOpen()
        if openDirectionalScanPanel and not openProbeScanPanel:
            SetProbeScanEmbeddedPanelClosed()
        elif openProbeScanPanel and not openDirectionalScanPanel:
            SetDirectionalScanEmbeddedPanelClosed()
        elif not openProbeScanPanel and not openDirectionalScanPanel:
            SetProbeScanEmbeddedPanelClosed()
            SetDirectionalScanEmbeddedPanelClosed()
        SolarSystemViewPanel.Open()


def OpenSolarSystemMap(openProbeScanPanel = False, openDirectionalScanPanel = False):
    if session.solarsystemid2:
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        panel = SolarSystemViewPanel.GetIfOpen()
        if panel:
            if openProbeScanPanel:
                panel.OpenProbeScanner()
            if openDirectionalScanPanel:
                panel.ToggleDirectionalScanner()
        else:
            SolarSystemViewPanel.Open(isDirectionalScanPanelOpen=openDirectionalScanPanel, isProbeScanPanelOpen=openProbeScanPanel)


def ToggleMap(*args, **kwds):
    if not classic_map_enabled_setting.is_enabled():
        from eve.client.script.ui.shared.mapView.mapViewPanel import MapViewPanel
        if not MapViewPanel.CloseIfOpen():
            return OpenMap(*args, **kwds)
    else:
        viewSvc = sm.GetService('viewState')
        if viewSvc.IsViewActive('starmap', 'systemmap'):
            viewSvc.CloseSecondaryView()
        else:
            viewSvc.ActivateView('starmap', **kwds)


def OpenMap(interestID = None, hightlightedSolarSystems = None, starColorMode = None, zoomToItem = True, **kwds):
    if not classic_map_enabled_setting.is_enabled():
        from eve.client.script.ui.shared.mapView.mapViewPanel import MapViewPanel
        mapPanel = MapViewPanel.GetIfOpen()
        if mapPanel:
            if interestID:
                mapPanel.SetActiveItemID(interestID, zoomToItem=zoomToItem)
            if starColorMode:
                mapPanel.SetMapFilter(starColorMode)
            if mapPanel.IsMinimized():
                mapPanel.Maximize()
        else:
            if hightlightedSolarSystems:
                interestID = hightlightedSolarSystems.keys()
            MapViewPanel.Open(parent=uicore.layer.main, interestID=interestID, starColorMode=starColorMode, zoomToItem=zoomToItem)
    else:
        sm.GetService('viewState').ActivateView('starmap', interestID=interestID, hightlightedSolarSystems=hightlightedSolarSystems, starColorMode=starColorMode)


def UpdateDebugOutput(debugOutput, camera = None, mapView = None, **kwds):
    debugText = ''
    if mapView:
        debugText += '<br>MapViewID %s' % mapView.mapViewID
    if camera:
        debugText += '<br>field of view %s' % camera.fov
        debugText += '<br>min/max distance %s/%s' % (camera.maxZoom, camera.minZoom)
        debugText += '<br>front/back clip %s/%s' % (camera.nearClip, camera.farClip)
        debugText += '<br>translationFromParent %s' % camera.GetZoomDistance()
        debugText += '<br>viewAngle %.3f, %.3f, %.3f' % camera.GetViewVector()
    debugOutput.text = debugText


def CreateLineSet(pickEnabled = False, texturePath = None, overlayTexturePath = None):
    lineSet = trinity.EveCurveLineSet()
    tex2D = trinity.TriTextureParameter()
    tex2D.name = 'TexMap'
    tex2D.resourcePath = texturePath or 'res:/UI/Texture/classes/LineSet/lineSegment.dds'
    lineSet.lineEffect.resources.append(tex2D)
    overlayTex2D = trinity.TriTextureParameter()
    overlayTex2D.name = 'OverlayTexMap'
    overlayTex2D.resourcePath = overlayTexturePath or 'res:/UI/Texture/classes/MapView/lineSegmentConstellation.dds'
    lineSet.lineEffect.resources.append(overlayTex2D)
    if not pickEnabled:
        lineSet.pickEffect = None
    return lineSet


def CreatePlanarLineSet(pickEnabled = False, texturePath = None):
    lineSet = trinity.EveCurveLineSet()
    lineSet.lineEffect = trinity.Tr2Effect()
    lineSet.lineEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Lines/Lines3DPlanar.fx'
    tex2D = trinity.TriTextureParameter()
    tex2D.name = 'TexMap'
    tex2D.resourcePath = texturePath or 'res:/dx9/texture/ui/linePlanarBase.dds'
    lineSet.lineEffect.resources.append(tex2D)
    if pickEnabled:
        lineSet.pickEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Lines/Lines3DPlanarPicking.fx'
    else:
        lineSet.pickEffect = None
    return lineSet


PARTICLE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Particles/StarmapNew.fx'
PARTICLE_SPRITE_TEXTURE = 'res:/Texture/Particle/mapStarNew5.dds'
PARTICLE_SPRITE_HEAT_TEXTURE = 'res:/Texture/Particle/mapStarNewHeat.dds'
PARTICLE_SPRITE_DATA_TEXTURE = 'res:/Texture/Particle/mapStatData_Circle.dds'
DISTANCE_RANGE = 'distanceRange'

def CreateParticles():
    particleTransform = trinity.EveTransform()
    particleTransform.name = 'particleTransform'
    tex = trinity.TriTextureParameter()
    tex.name = 'TexMap'
    tex.resourcePath = PARTICLE_SPRITE_TEXTURE
    heattex = trinity.TriTextureParameter()
    heattex.name = 'HeatTexture'
    heattex.resourcePath = PARTICLE_SPRITE_HEAT_TEXTURE
    distanceFadeControl = trinity.Tr2Vector4Parameter()
    distanceFadeControl.name = DISTANCE_RANGE
    distanceFadeControl.value = (0, 1, 0, 0)
    particles = trinity.Tr2RuntimeInstanceData()
    particles.SetElementLayout([(trinity.PARTICLE_ELEMENT_TYPE.POSITION, 0, 3),
     (trinity.PARTICLE_ELEMENT_TYPE.POSITION, 1, 3),
     (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 0, 1),
     (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 1, 4)])
    mesh = trinity.Tr2InstancedMesh()
    mesh.geometryResPath = 'res:/Graphics/Generic/UnitPlane/UnitPlane.gr2'
    mesh.instanceGeometryResource = particles
    particleTransform.mesh = mesh
    area = trinity.Tr2MeshArea()
    area.effect = trinity.Tr2Effect()
    area.effect.effectFilePath = PARTICLE_EFFECT
    area.effect.resources.append(tex)
    area.effect.resources.append(heattex)
    area.effect.parameters.append(distanceFadeControl)
    mesh.additiveAreas.append(area)
    return (particleTransform, particles, distanceFadeControl)


def DrawLineSetCircle(lineSet, centerPosition, outerPosition, segmentSize, lineColor = (0.3, 0.3, 0.3, 0.5), lineWeight = 2.0, animationSpeed = 0.0, dashSegments = 0, dashColor = None):
    orbitPos = geo2.Vector(*outerPosition)
    parentPos = geo2.Vector(*centerPosition)
    dirVec = orbitPos - parentPos
    radius = geo2.Vec3Length(dirVec)
    fwdVec = (1.0, 0.0, 0.0)
    dirVec = geo2.Vec3Normalize(dirVec)
    rotation = geo2.QuaternionRotationArc(fwdVec, dirVec)
    matrix = geo2.MatrixAffineTransformation(1.0, (0.0, 0.0, 0.0), rotation, centerPosition)
    circum = math.pi * 2 * radius
    steps = min(256, max(16, int(circum / segmentSize)))
    coordinates = []
    stepSize = math.pi * 2 / steps
    for step in range(steps):
        angle = step * stepSize
        x = math.cos(angle) * radius
        z = math.sin(angle) * radius
        pos = geo2.Vector(x, 0.0, z)
        pos = geo2.Vec3TransformCoord(pos, matrix)
        coordinates.append(pos)

    lineIDs = set()
    dashColor = dashColor or lineColor
    for start in xrange(steps):
        end = (start + 1) % steps
        lineID = lineSet.AddStraightLine(coordinates[start], lineColor, coordinates[end], lineColor, lineWeight)
        lineIDs.add(lineID)
        if dashSegments:
            lineSet.ChangeLineAnimation(lineID, dashColor, animationSpeed, dashSegments)

    return lineIDs


def DrawCircle(lineSet, centerPosition, radius, arcSegments = 4, startColor = (0.3, 0.3, 0.3, 0.5), endColor = (0.3, 0.3, 0.3, 0.5), **kwds):
    lineIDs = set()
    arcAngle = math.pi * 2 / float(arcSegments)
    stepSize = 1.0 / float(arcSegments)
    for i in xrange(arcSegments):
        step = i / float(arcSegments)
        startAngle = math.pi * 2 * step
        color1 = geo2.Vec4Lerp(startColor, endColor, step)
        color2 = geo2.Vec4Lerp(startColor, endColor, step + stepSize)
        lineID = DrawCircularArc(lineSet, centerPosition, radius, angle=arcAngle, startAngle=startAngle, startColor=color1, endColor=color2, **kwds)
        lineIDs.add(lineID)

    return lineIDs


def DrawCircularArc(lineSet, centerPosition, radius, angle, startAngle = 0.0, lineWidth = 1.0, startColor = (0.3, 0.3, 0.3, 0.5), endColor = (0.3, 0.3, 0.3, 0.5)):
    cos = math.cos(startAngle)
    sin = math.sin(startAngle)
    p1 = geo2.Vec3Add(centerPosition, (-radius * cos, 0.0, -radius * sin))
    cos = math.cos(startAngle + angle)
    sin = math.sin(startAngle + angle)
    p2 = geo2.Vec3Add(centerPosition, (-radius * cos, 0.0, -radius * sin))
    lineID = lineSet.AddSpheredLineCrt(p1, startColor, p2, endColor, centerPosition, lineWidth)
    lineSet.ChangeLineSegmentation(lineID, int(math.degrees(angle)))
    return lineID


def TryGetPosFromItemID(locationID, solarsystemID):
    locationInfo = cfg.evelocations.GetIfExists(locationID)
    if locationInfo and locationInfo.solarSystemID == solarsystemID and (locationInfo.x, locationInfo.y, locationInfo.z) != (0, 0, 0):
        return (locationInfo.x, locationInfo.y, locationInfo.z)
    return (0, 0, 0)
