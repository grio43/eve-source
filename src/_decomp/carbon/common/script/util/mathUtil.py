#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\mathUtil.py
import math
try:
    import geo2
except ImportError:
    geo2 = None

MATH_PI_2 = math.pi / 2
MATH_PI_4 = math.pi / 4
MATH_PI_8 = math.pi / 8
MATH_2_PI = math.pi * 2

def LtoI(v):
    if v < 2147483648L:
        return int(v)
    return ~int(~v & 4294967295L)


def LerpList(color1, color2, lerpValue):
    invLerpValue = 1.0 - lerpValue
    return [invLerpValue * color1[0] + lerpValue * color2[0],
     invLerpValue * color1[1] + lerpValue * color2[1],
     invLerpValue * color1[2] + lerpValue * color2[2],
     invLerpValue * color1[3] + lerpValue * color2[3]]


def LerpVector(v1, v2, s):
    v = v1.CopyTo()
    v.Lerp(v2, s)
    return v


def Lerp(start, end, s):
    return start + min(max(s, 0.0), 1.0) * (end - start)


def LerpTupleThree(tuple1, tuple2, scaling):
    return (Lerp(tuple1[0], tuple2[0], scaling), Lerp(tuple1[1], tuple2[1], scaling), Lerp(tuple1[2], tuple2[2], scaling))


def LerpTupleFour(tuple1, tuple2, scaling):
    return (Lerp(tuple1[0], tuple2[0], scaling),
     Lerp(tuple1[1], tuple2[1], scaling),
     Lerp(tuple1[2], tuple2[2], scaling),
     Lerp(tuple1[3], tuple2[3], scaling))


def LerpByTime(startVal, endVal, startTime, endTime, curTime):
    lerpRatio = float(curTime - startTime) / float(endTime - startTime)
    return Lerp(startVal, endVal, lerpRatio)


def RayToPlaneIntersection(P, d, Q, n, returnSign = False):
    position = P
    sign = 1
    denom = geo2.Vec3Dot(n, d)
    if abs(denom) >= 1e-05:
        distance = -geo2.Vec3Dot(Q, n)
        t = -(geo2.Vec3Dot(n, P) + distance) / denom
        if t < 0:
            sign = -1
        S = geo2.Add(geo2.Scale(d, t), P)
        position = S
    if returnSign:
        return (position, sign)
    return position


def ClampRotation(rotation):
    if rotation > math.pi * 2:
        rotation -= math.pi * 2
    elif rotation < 0:
        rotation += math.pi * 2
    return rotation
