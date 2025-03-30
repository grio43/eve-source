#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ballparkCommon\intersection.py
import geo2
import math

def GetClosestIntersection(origin, direction, spheres):
    direction = geo2.Vec3NormalizeD(direction)
    closest = -1.0
    intersection = None
    theID = None
    for sphereID, center, radius in spheres:
        delta = geo2.Vec3SubtractD(origin, center)
        b = geo2.Vec3DotD(geo2.Vec3ScaleD(direction, 2.0), delta)
        if b > 0:
            continue
        c = geo2.Vec3LengthSqD(delta) - radius ** 2
        det = b * b - 4.0 * c
        if det < 0.0:
            continue
        det = math.sqrt(det)
        t0 = (-b - det) * 0.5
        t1 = (-b + det) * 0.5
        if t0 < t1:
            t = t0
        else:
            t = t1
        p = geo2.Vec3AddD(origin, geo2.Vec3ScaleD(direction, t))
        d2 = geo2.Vec3DistanceSqD(origin, p)
        if closest < 0.0:
            closest = d2
            theID = sphereID
            intersection = p
        elif d2 < closest:
            closest = d2
            intersection = p
            theID = sphereID

    return (theID, intersection)


def GetClosestIntersectionForRay(ballpark, origin, direction, maxDistance = None):
    spheres = [ (eachBall.id, (eachBall.x, eachBall.y, eachBall.z), eachBall.radius) for eachBall in ballpark.balls.values() if eachBall.isGlobal ]
    if maxDistance:
        spheres = FilterOutVectorsOutsideRange(spheres, origin, maxDistance)
    return GetClosestIntersection(origin, direction, spheres)


def FilterOutVectorsOutsideRange(spheres, origin, maxDistance):
    maxDistanceSquared = maxDistance ** 2
    return [ (sphereID, sphereCenterVector, sphereRadius) for sphereID, sphereCenterVector, sphereRadius in spheres if geo2.Vec3DistanceSqD(sphereCenterVector, origin) <= maxDistanceSquared ]
