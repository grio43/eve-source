#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\utils_scene.py
import geo2
import trinity
import blue
from math import sin, tan
from iconrendering2.utils import Pump
GETPHOTO_ANGLE = (0.3, -0.3, 0.0)
GETPHOTO_VIEW_UP = (0.0, 1.0, 0.0)
GETPHOTO_FOV = 1.0
GETPHOTO_BACKCLIP = 500000.0
GETPHOTO_PROJECTION = (GETPHOTO_FOV,
 1.0,
 1.0,
 GETPHOTO_BACKCLIP)

def FreezeTime():
    blue.os.advanceTimeInPump = False
    blue.os.SetTime(1L)
    trinity.device.animationTimeScale = 0.0
    trinity.device.animationTime = 1
    Pump()
    trinity.app.ProcessMessages()


def WaitForGeometryLoad(object, geometryPath = 'mesh.geometry', context = ''):

    def _IsGeometryLoaded():
        o = object
        for attr in geometryPath.split('.'):
            o = getattr(o, attr, None)

        return o is not None and o.isGood

    blue.resMan.Wait()
    Pump()
    maxWaits = 100
    currentWait = 0
    while not _IsGeometryLoaded() and currentWait != maxWaits:
        currentWait += 1
        blue.resMan.Wait()
        Pump()

    geometry = object
    for attr in geometryPath.split('.'):
        geometry = getattr(geometry, attr, None)

    if currentWait == maxWaits:
        print 'Waiting for geometry failed for %s' % context


def GetViewProjectionForObject(object, scene, cameraAngle = None):
    if object is None:
        return (None, None)
    boundingSphereRadius = object.GetBoundingSphereRadius()
    if getattr(object, 'mesh', None) is not None:
        geometry = object.mesh.geometry
        boundingSphereCenter = object.GetBoundingSphereCenter()
        view, projection = GetViewAndProjectionUsingMeshGeometry(geometry, scene=scene, boundingSphereRadius=boundingSphereRadius, boundingSphereCenter=boundingSphereCenter, cameraAngle=cameraAngle)
    else:
        view, projection = GetViewAndProjectionUsingBoundingSphere(boundingSphereRadius)
    return (view, projection)


def _GetViewMatrixFromAngle(cameraAngle, lookAt, cameraDistance):
    view_at = geo2.Vector(lookAt[0], lookAt[1], lookAt[2])
    view_eye = geo2.Vector(0.0, 0.0, 1.0)
    angleTransform = geo2.MatrixRotationYawPitchRoll(cameraAngle[0], cameraAngle[1], cameraAngle[2])
    view_eye = geo2.Vec3TransformCoord(view_eye, angleTransform)
    view_eye = geo2.Vector(*view_eye)
    view_eye = view_eye * cameraDistance + view_at
    return (view_eye, view_at, geo2.Vector(*GETPHOTO_VIEW_UP))


def _SphericalFit(radius, fov = GETPHOTO_FOV, fudge = 1.15):
    alpha = fov / 2.0
    return radius / sin(alpha) * fudge


def _GetViewAndProjectionUsingProjectedBoundingBox(calculateProjectedBoundingBox, scene = None, boundingSphereRadius = None, boundingSphereCenter = None, boundingBoxMin = None, boundingBoxMax = None, cameraAngle = None, aspectRatio = 1.0):
    cameraAngle = cameraAngle or GETPHOTO_ANGLE
    zn = 1.0
    if boundingSphereRadius:
        radius = boundingSphereRadius
        center = boundingSphereCenter if boundingSphereCenter else (0.0, 0.0, 0.0)
    else:
        center = geo2.Vec3Add(boundingBoxMin, boundingBoxMax)
        center = geo2.Vec3Scale(center, 0.5)
        radius = geo2.Vec3Length(geo2.Vec3Subtract(boundingBoxMax, boundingBoxMin))
    dist = zn + _SphericalFit(radius)
    viewEyeAtUp = _GetViewMatrixFromAngle(cameraAngle, center, dist)
    projTransform = geo2.MatrixPerspectiveFovRH(*GETPHOTO_PROJECTION)
    viewTransform = geo2.MatrixLookAtRH(*viewEyeAtUp)
    combinedTransform = viewTransform
    combinedTransform = geo2.MatrixMultiply(combinedTransform, projTransform)
    safeMin, safeMax = calculateProjectedBoundingBox(combinedTransform)
    deltaX = safeMax[0] - safeMin[0]
    deltaY = safeMax[1] - safeMin[1]
    scalingFactor = 0.9 * (2.0 / max(deltaX, deltaY))
    try:
        if scene.backgroundEffect is not None:
            params = scene.backgroundEffect.Find(['trinity.Tr2FloatParameter'])
            for param in params:
                if param.name == 'ProjectionScaling':
                    param.value = scalingFactor

    except AttributeError:
        pass

    offsetX = -1 * scalingFactor * (safeMin[0] + safeMax[0]) / 2.0
    offsetY = -1 * scalingFactor * (safeMin[1] + safeMax[1]) / 2.0
    scale = 1.0 / tan(GETPHOTO_FOV / 2.0) * scalingFactor
    zf = dist + radius * 2
    t = zn * (1 - offsetY) / scale / aspectRatio
    b = -zn * (1 + offsetY) / scale / aspectRatio
    r = zn * (1 - offsetX) / scale
    l = -zn * (1 + offsetX) / scale
    projection = trinity.TriProjection()
    projection.PerspectiveOffCenter(l, r, b, t, zn, zf)
    view = trinity.TriView()
    view.SetLookAtPosition(*viewEyeAtUp)
    return (view, projection)


def GetViewAndProjectionUsingMeshGeometry(geometry, geometryMeshIdx = 0, scene = None, boundingSphereRadius = None, boundingSphereCenter = None, boundingBoxMin = None, boundingBoxMax = None, cameraAngle = None, aspectRatio = 1.0):

    def calculateProjectedBoundingBox(combinedTransform):
        return geometry.CalculateBoundingBoxFromTransform(geometryMeshIdx, combinedTransform)

    return _GetViewAndProjectionUsingProjectedBoundingBox(calculateProjectedBoundingBox, scene, boundingSphereRadius=boundingSphereRadius, boundingSphereCenter=boundingSphereCenter, boundingBoxMin=boundingBoxMin, boundingBoxMax=boundingBoxMax, cameraAngle=cameraAngle, aspectRatio=aspectRatio)


def GetViewAndProjectionForSkinnedModel(model, scene = None, boundingSphereRadius = None, boundingSphereCenter = None, boundingBoxMin = None, boundingBoxMax = None, cameraAngle = None):

    def calculateProjectedBoundingBox(combinedTransform):
        bb = model.CalculateSkinnedBoundingBoxFromTransform(combinedTransform)
        print bb
        return bb

    return _GetViewAndProjectionUsingProjectedBoundingBox(calculateProjectedBoundingBox, scene, boundingSphereRadius=boundingSphereRadius, boundingSphereCenter=boundingSphereCenter, boundingBoxMin=boundingBoxMin, boundingBoxMax=boundingBoxMax, cameraAngle=cameraAngle)


def GetViewAndProjectionUsingBoundingBox(boundingBoxMin = None, boundingBoxMax = None, scene = None, cameraAngle = None):

    def calculateProjectedBoundingBox(combinedTransform):
        edges = []
        edges.append(geo2.Vector(boundingBoxMin[0], boundingBoxMin[1], boundingBoxMin[2]))
        edges.append(geo2.Vector(boundingBoxMin[0], boundingBoxMin[1], boundingBoxMax[2]))
        edges.append(geo2.Vector(boundingBoxMin[0], boundingBoxMax[1], boundingBoxMin[2]))
        edges.append(geo2.Vector(boundingBoxMin[0], boundingBoxMax[1], boundingBoxMax[2]))
        edges.append(geo2.Vector(boundingBoxMax[0], boundingBoxMin[1], boundingBoxMin[2]))
        edges.append(geo2.Vector(boundingBoxMax[0], boundingBoxMin[1], boundingBoxMax[2]))
        edges.append(geo2.Vector(boundingBoxMax[0], boundingBoxMax[1], boundingBoxMin[2]))
        edges.append(geo2.Vector(boundingBoxMax[0], boundingBoxMax[1], boundingBoxMax[2]))
        for i, edge in enumerate(edges):
            edge = geo2.Vector(*geo2.Vec3TransformCoord(edge, combinedTransform))
            if i == 0:
                safeMin = geo2.Vector(*edge)
                safeMax = geo2.Vector(*edge)
            else:
                safeMin.x = min(safeMin.x, edge[0])
                safeMin.y = min(safeMin.y, edge[1])
                safeMin.z = min(safeMin.z, edge[2])
                safeMax.x = max(safeMax.x, edge[0])
                safeMax.y = max(safeMax.y, edge[1])
                safeMax.z = max(safeMax.z, edge[2])

        return (safeMin, safeMax)

    return _GetViewAndProjectionUsingProjectedBoundingBox(calculateProjectedBoundingBox, scene, boundingBoxMin=boundingBoxMin, boundingBoxMax=boundingBoxMax, cameraAngle=cameraAngle, boundingSphereRadius=None, boundingSphereCenter=None)


def GetViewAndProjectionUsingBoundingSphere(boundingSphereRadius, boundingSphereCenter = None, cameraAngle = None, distanceOverride = None, fov = GETPHOTO_FOV, near = 1.0, aspectRatio = 1.0):
    cameraAngle = cameraAngle or GETPHOTO_ANGLE
    boundingSphereCenter = boundingSphereCenter or (0.0, 0.0, 0.0)
    dist = distanceOverride if distanceOverride else _SphericalFit(boundingSphereRadius, fov)
    dist = max(dist, 1.5)
    projection = trinity.TriProjection()
    projection.PerspectiveFov(fov, aspectRatio, near, GETPHOTO_BACKCLIP)
    view = trinity.TriView()
    view.SetLookAtPosition(*_GetViewMatrixFromAngle(cameraAngle, boundingSphereCenter, dist))
    return (view, projection)
