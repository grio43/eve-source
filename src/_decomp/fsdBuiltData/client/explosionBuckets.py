#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\explosionBuckets.py
import explosionBucketIDsLoader
import itertools
import random
import evetypes
from fsdBuiltData.common.base import BuiltDataLoader
from fsdBuiltData.common.graphicIDs import GetExplosionBucketID
from fsdBuiltData.client.explosionIDs import GetExplosion, GetExplosionAttribute
import logging
log = logging.getLogger(__file__)

class ExplosionBuckets(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/explosionBucketIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/explosionBucketIDs.fsdbinary'
    __loader__ = explosionBucketIDsLoader


def GetExplosionBuckets():
    return ExplosionBuckets.GetData()


def GetExplosionBucketIDByTypeID(typeID):
    if typeID is None:
        return
    return GetExplosionBucketID(evetypes.GetGraphicID(typeID))


def GetExplosionBucketByTypeID(typeID):
    return GetExplosionBucket(GetExplosionBucketIDByTypeID(typeID))


def GetExplosionBucket(explosionBucketID):
    return GetExplosionBuckets().get(explosionBucketID, None)


def GetExplosionBucketAttribute(explosionBucketID, attributeName, default = None):
    if isinstance(explosionBucketID, (int, long)):
        return getattr(GetExplosionBucket(explosionBucketID), attributeName, None) or default
    return getattr(explosionBucketID, attributeName, None) or default


def GetExplosionRaces(explosionBucketID):
    explosions = GetExplosionBucketAttribute(explosionBucketID, 'racialExplosions', None)
    if explosions is None:
        log.error("ExplosionBucket '%s' has no racialExplosions" % explosionBucketID)
        return
    return explosions


def GetExplosionsForRace(explosionBucketID, raceName):
    explosions = GetExplosionBucketAttribute(explosionBucketID, 'racialExplosions', None)
    if explosions is None:
        log.error("ExplosionBucket '%s' has no racialExplosions" % explosionBucketID)
        return
    return explosions.get(raceName, explosions.get('default', None))


def GetRandomExplosion(explosionBucket, raceName, randomnessSeed = None):
    explosionList = GetExplosionsForRace(explosionBucket, raceName)
    if explosionList is None:
        log.error("ExplosionBucket '%s' has no explosions for race '%s' or race 'default'" % (explosionBucket, raceName))
        return
    explosions = []
    for explosion in explosionList:
        for i in range(explosion.chanceMultiplier):
            explosions.append(explosion)

    if randomnessSeed is not None:
        randomness = random.Random(randomnessSeed)
    else:
        randomness = random.Random()
    chosenExplosion = randomness.choice(explosions)
    return chosenExplosion


def HasSpecialExplosion(explosionBucketID):
    return GetSpecialExplosion(explosionBucketID) is not None


def GetSpecialExplosion(explosionBucketID):
    return GetExplosionAttribute(explosionBucketID, 'specialExplosion')


def GetDescription(explosionBucketID, default = 1):
    return GetExplosionBucketAttribute(explosionBucketID, 'description', default)
