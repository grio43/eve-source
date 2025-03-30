#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\turrets.py
import sys
import logging
import telemetry
import geo2
logger = logging.getLogger(__name__)

@telemetry.ZONE_METHOD
def setupTurretMovementAudio(turretSets, locators, parentBoundingBox):
    turretSetsByName = {}
    for turretSet in turretSets:
        turretSetsByName.setdefault(turretSet.name, []).append(turretSet)

    for name, turretSets in turretSetsByName.items():
        if len(turretSets) > 2:
            closestTurretSetToMinPoint = {'turretSet': None,
             'distance': sys.float_info.max}
            closestTurretSetToMaxPoint = {'turretSet': None,
             'distance': sys.float_info.max}
            for turretSet in turretSets:
                turretSet.playMovementSound = False
                turretLocatorName = '{}{}'.format(turretSet.locatorName, turretSet.slotNumber)
                closestLocatorDistanceToMinPoint = sys.float_info.max
                closestLocatorDistanceToMaxPoint = sys.float_info.max
                for locator in locators:
                    if not locator.name.startswith(turretLocatorName):
                        continue
                    positionVec4 = locator.transform[-1]
                    positionVec3 = positionVec4[:-1]
                    closestLocatorDistanceToMinPoint = min(closestLocatorDistanceToMinPoint, geo2.Vec3DistanceSq(positionVec3, parentBoundingBox[0]))
                    closestLocatorDistanceToMaxPoint = min(closestLocatorDistanceToMaxPoint, geo2.Vec3DistanceSq(positionVec3, parentBoundingBox[1]))

                if closestLocatorDistanceToMinPoint < closestTurretSetToMinPoint['distance']:
                    closestTurretSetToMinPoint['turretSet'] = turretSet
                    closestTurretSetToMinPoint['distance'] = closestLocatorDistanceToMinPoint
                if closestLocatorDistanceToMaxPoint < closestTurretSetToMaxPoint['distance']:
                    closestTurretSetToMaxPoint['turretSet'] = turretSet
                    closestTurretSetToMaxPoint['distance'] = closestLocatorDistanceToMaxPoint

            if closestTurretSetToMinPoint['turretSet'] and closestTurretSetToMaxPoint['turretSet']:
                closestTurretSetToMinPoint['turretSet'].playMovementSound = True
                closestTurretSetToMaxPoint['turretSet'].playMovementSound = True
