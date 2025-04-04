#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\mathCommon.py
from carbon.common.lib.const import FLOAT_TOLERANCE
from carbon.common.script.util.mathErrors import InvalidInput
import logging
import math
import random
try:
    import geo2
except ImportError:
    geo2 = None

log = logging.getLogger(__name__)

def ConvertGeoToTriMatrix(geoMatrix):
    return ConvertTupleToTriMatrix(geoMatrix)


def ConvertTriToGeoMatrix(triMatrix):
    return ConvertTriToTupleMatrix(triMatrix)


def ConvertTupleToTriMatrix(tupleMatrix):
    import trinity
    return trinity.TriMatrix(tupleMatrix[0][0], tupleMatrix[0][1], tupleMatrix[0][2], tupleMatrix[0][3], tupleMatrix[1][0], tupleMatrix[1][1], tupleMatrix[1][2], tupleMatrix[1][3], tupleMatrix[2][0], tupleMatrix[2][1], tupleMatrix[2][2], tupleMatrix[2][3], tupleMatrix[3][0], tupleMatrix[3][1], tupleMatrix[3][2], tupleMatrix[3][3])


def ConvertTriToTupleMatrix(triMatrix):
    return ((triMatrix._11,
      triMatrix._12,
      triMatrix._13,
      triMatrix._14),
     (triMatrix._21,
      triMatrix._22,
      triMatrix._23,
      triMatrix._24),
     (triMatrix._31,
      triMatrix._32,
      triMatrix._33,
      triMatrix._34),
     (triMatrix._41,
      triMatrix._42,
      triMatrix._43,
      triMatrix._44))


def FloatCloseEnough(a, b, epsilon = None):
    if not epsilon:
        epsilon = FLOAT_TOLERANCE
    return abs(a - b) < epsilon


def VectorCloseEnough(a, b):
    for i in range(len(a)):
        if not FloatCloseEnough(a[i], b[i]):
            return False

    return True


def RandomFloatBetween(a, b):
    return a + (b - a) * random.random()


def CreateOrthogonalVector(v):
    minIdx = v.index(min(v))
    maxIdx = v.index(max(v))
    ortho = list(v)
    ortho[minIdx], ortho[maxIdx] = -ortho[maxIdx], ortho[minIdx]
    return tuple(ortho)


def GetRandomHemisphereVector(axis):
    radius = geo2.Vec3Length(axis)
    randVec = RandomVector(radius)
    dotProduct = geo2.Vec3Dot(randVec, axis)
    if dotProduct <= 0:
        randVec = list(randVec)
        for i in xrange(len(randVec)):
            if abs(axis[i] - randVec[i]) > radius:
                randVec[i] *= -1

        randVec = tuple(randVec)
    return randVec


def RandomVector(radius = 1.0, width = 0.0):
    t = random.random() * 2.0 * math.pi
    u = (random.random() - 0.5) * 2.0
    sq = math.sqrt(1.0 - u * u)
    if width > 0.0:
        if width > radius:
            width = radius
        radius = radius - random.random() * width
    x = radius * sq * math.cos(t)
    y = radius * sq * math.sin(t)
    z = radius * u
    return [x, y, z]


def TrinityMatrixCloseEnough(a, b):
    return FloatCloseEnough(a._11, b._11) and FloatCloseEnough(a._21, b._21) and FloatCloseEnough(a._31, b._31) and FloatCloseEnough(a._41, b._41) and FloatCloseEnough(a._12, b._12) and FloatCloseEnough(a._22, b._22) and FloatCloseEnough(a._32, b._32) and FloatCloseEnough(a._42, b._42) and FloatCloseEnough(a._13, b._13) and FloatCloseEnough(a._23, b._23) and FloatCloseEnough(a._33, b._33) and FloatCloseEnough(a._43, b._43) and FloatCloseEnough(a._14, b._14) and FloatCloseEnough(a._24, b._24) and FloatCloseEnough(a._34, b._34) and FloatCloseEnough(a._44, b._44)


def MatrixCloseEnough(a, b):
    for i in xrange(0, 4):
        for j in xrange(0, 4):
            if not FloatCloseEnough(a[i][j], b[i][j]):
                return False

    return True


def RotateQuatByYaw(oldRot, yawAngle):
    newRot = (0,
     math.sin(yawAngle / 2.0),
     0,
     math.cos(yawAngle / 2.0))
    return geo2.QuaternionMultiply(oldRot, newRot)


def CalculateShortestRotation(angle):
    angle = math.fmod(angle, 2 * math.pi)
    if angle <= -math.pi:
        angle += math.pi * 2
    elif angle > math.pi:
        angle -= math.pi * 2
    return angle


def BoundedRotateQuatByYaw(entityRotation, facingAngle, maxRotate):
    if abs(facingAngle) < 0.01:
        return entityRotation
    maxRotate = abs(maxRotate)
    facingAngle = CalculateShortestRotation(facingAngle)
    if maxRotate < abs(facingAngle):
        if facingAngle < 0:
            facingAngle = -maxRotate
        else:
            facingAngle = maxRotate
    return RotateQuatByYaw(entityRotation, facingAngle)


def GetLesserAngleBetweenYaws(first, second):
    return CalculateShortestRotation(second - first)


def GetDeltaAngleToFaceTarget(sourcePos, sourceRot, targetPos):
    targetVec = geo2.Vec3Subtract(targetPos, sourcePos)
    theta = GetYawAngleFromDirectionVector(targetVec)
    yaw, trash, trash = geo2.QuaternionRotationGetYawPitchRoll(sourceRot)
    return GetLesserAngleBetweenYaws(yaw, theta)


def CreateDirectionVectorFromYawAngle(yaw):
    return (math.sin(yaw), 0.0, math.cos(yaw))


def CreateDirectionVectorFromYawAndPitchAngle(yaw, pitch):
    direction = (-math.sin(pitch) * math.cos(yaw), math.cos(pitch), -math.sin(pitch) * math.sin(yaw))
    return direction


def GetYawAngleFromDirectionVector(vec3):
    testVec = list(vec3)
    testVec[1] = 0.0
    testVec = list(geo2.Vec3Normalize(testVec))
    if testVec[2] >= 1.0:
        testVec[2] = 1.0
    elif testVec[2] <= -1.0:
        testVec[2] = -1.0
    yaw = math.acos(testVec[2])
    if testVec[0] < 0.0:
        yaw = math.pi * 2 - yaw
    return yaw


def GetPitchAngleFromDirectionVector(vec3):
    testVec = list(geo2.Vec3Normalize(vec3))
    if testVec[1] >= 1.0:
        testVec[1] = 1.0
    elif testVec[1] <= -1.0:
        testVec[1] = -1.0
    pitch = math.asin(testVec[1])
    return pitch


def GetNewQuatToFacePos(sourcePos, sourceRot, targetPos):
    deltaAngle = GetDeltaAngleToFaceTarget(sourcePos, sourceRot, targetPos)
    yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(sourceRot)
    yaw += deltaAngle
    return geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)


def CalcLinearIntpValue(startVal, targetVal, startTime, curTime, howLong):
    endTime = startTime + howLong
    if curTime > endTime:
        return targetVal
    elif startTime > curTime:
        return startVal
    else:
        timeFactor = max(1.0 * (curTime - startTime) / howLong, 0)
        return startVal + timeFactor * (targetVal - startVal)


def CalcScaledValueOverInterval(startVal, targetVal, intervalLength, intervalRemaining, minFactor = None, maxFactor = None):
    if intervalLength == 0:
        return targetVal
    factor = 1.0 - 1.0 * intervalRemaining / intervalLength
    if minFactor:
        factor = max(factor, minFactor)
    if maxFactor:
        factor = min(factor, maxFactor)
    return startVal + (targetVal - startVal) * factor


def LineIntersectVerticalPlaneWithTwoPoints(lineV1, lineV2, planeV1, planeV2):
    v1 = planeV1
    v2 = planeV2
    v3 = geo2.Vector(*planeV1)
    v3.y += 1
    plane = geo2.PlaneFromPoints(v1, v2, v3)
    intersectionPoint = geo2.PlaneIntersectLine(plane, lineV1, lineV2)
    return intersectionPoint


def DecomposeMatrix(matrix):
    if hasattr(matrix, '__bluetype__') and matrix.__bluetype__ == 'trinity.TriMatrix':
        matrix = util.ConvertTriToTupleMatrix(matrix)
    scale, rot, pos = geo2.MatrixDecompose(matrix)
    rot = geo2.QuaternionRotationGetYawPitchRoll(rot)
    return (pos, rot, scale)


def ComposeMatrix(pos, rot, scale):
    return geo2.MatrixTransformation(None, None, scale, None, rot, pos)


def GetViewFrustumPlanes(viewMatrix, projectionMatrix):
    viewProjectionMatrix = geo2.MatrixMultiply(viewMatrix, projectionMatrix)
    left = tuple((viewProjectionMatrix[i][0] + viewProjectionMatrix[i][3] for i in xrange(0, 4)))
    right = tuple((-viewProjectionMatrix[i][0] + viewProjectionMatrix[i][3] for i in xrange(0, 4)))
    bottom = tuple((viewProjectionMatrix[i][1] + viewProjectionMatrix[i][3] for i in xrange(0, 4)))
    top = tuple((-viewProjectionMatrix[i][1] + viewProjectionMatrix[i][3] for i in xrange(0, 4)))
    near = tuple((viewProjectionMatrix[i][2] + viewProjectionMatrix[i][3] for i in xrange(0, 4)))
    far = tuple((-viewProjectionMatrix[i][2] + viewProjectionMatrix[i][3] for i in xrange(0, 4)))
    return [left,
     right,
     bottom,
     top,
     near,
     far]


def GetSignedDistanceFromPointToPlane(point, plane):
    x0, y0, z0 = point
    A, B, C, D = plane
    numerator = A * x0 + B * y0 + C * z0 + D
    denominator = math.sqrt(A * A + B * B + C * C)
    if FloatCloseEnough(denominator, 0.0):
        raise InvalidInput('Cannot calculate distance as the provided plane equation is not valid (all 0s)')
    return numerator / denominator


def IsWithinFrustum(point, viewMatrix, projectionMatrix):
    planes = GetViewFrustumPlanes(viewMatrix, projectionMatrix)
    for plane in planes:
        try:
            if GetSignedDistanceFromPointToPlane(point, plane) < 0:
                return False
        except InvalidInput:
            continue

    return True


def GetYawAndPitchAnglesRad(position0, position1):
    quat = GetYawAndPitchQuaternion(position0, position1)
    rot = geo2.QuaternionRotationGetYawPitchRoll(quat)
    return (rot[0], rot[1])


def GetYawAndPitchQuaternion(position0, position1):
    direction = geo2.Vec3Subtract(position1, position0)
    direction = geo2.Vec3Normalize(direction)
    quat = geo2.QuaternionRotationArc(direction, (0.0, 0.0, 1.0))
    return quat


def GetYawAndPitchAnglesDeg(position0, position1):
    yaw, pitch = GetYawAndPitchAnglesRad(position0, position1)
    yaw = yaw * 180 / math.pi
    pitch = pitch * 180 / math.pi
    return (yaw, pitch)


def GetAngleBetweenTwoVectors(v1, v2):
    try:
        side1 = geo2.Vec3Length(v1)
        side2 = geo2.Vec3Length(v2)
        if side1 >= side2:
            a = side1
            b = side2
            c = geo2.Vec3Length(geo2.Vec3Subtract(v1, v2))
        else:
            a = side2
            b = side1
            c = geo2.Vec3Length(geo2.Vec3Subtract(v2, v1))
        mu = c - (a - b) if b >= c else b - (a - c)
        numerator = (a - b + c) * mu
        denominator = (a + (b + c)) * (a - c + b)
        if FloatCloseEnough(denominator, 0.0):
            if FloatCloseEnough(numerator, 0.0):
                raise InvalidInput('Cannot calculate angle for degenerate triangle (encountering atan(0/0) = NaN)')
            if numerator > 0.0:
                return math.pi
            raise RuntimeError('Cannot calculate angle as these side lengths do not belong to a real triangle')
        angle = 2.0 * math.atan(math.sqrt(numerator / denominator))
        return angle
    except Exception as exc:
        log.exception('Failed to calculate angle between 2 vectors: %s and %s. Exception: %s', v1, v2, exc)
        raise exc


def ProjectPointToLineSegment(A, B, p):
    AB = geo2.Vec3SubtractD(B, A)
    AB_squared = geo2.Vec3DotD(AB, AB)
    if AB_squared == 0:
        return A
    Ap = geo2.Vec3SubtractD(p, A)
    t = geo2.Vec3DotD(Ap, AB) / AB_squared
    if t < 0.0:
        return A
    elif t > 1.0:
        return B
    else:
        return geo2.Vec3AddD(A, geo2.Vec3ScaleD(AB, t))
