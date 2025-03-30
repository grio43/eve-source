#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\directionalScanIntersectUtil.py
import math
import geo2

def IsWithinSphere(pos, range):
    rad = geo2.Vec3Length(pos)
    return rad <= range


def IsWithinHalfSphere(pos, range, direction):
    if geo2.Vec3Dot(direction, pos) < 0:
        return False
    return IsWithinSphere(pos, range)


def IsWithinCone(pos, angle, range, direction):
    dird0 = geo2.Vec3Dot(direction, pos)
    c2 = math.cos(angle / 2) ** 2
    d0d0 = geo2.Vec3Dot(pos, pos)
    return dird0 >= 0.0 and dird0 ** 2 >= c2 * d0d0 and d0d0 <= range ** 2


def IsWithinScanShape(pos, egoPos, angle, range, direction):
    if not egoPos:
        return
    pos = geo2.Vec3Subtract(egoPos, pos)
    if angle <= math.pi:
        return IsWithinCone(pos, angle, range, direction)
    elif angle < 2 * math.pi:
        return IsWithinHalfSphere(pos, range, direction)
    else:
        return IsWithinSphere(pos, range)
