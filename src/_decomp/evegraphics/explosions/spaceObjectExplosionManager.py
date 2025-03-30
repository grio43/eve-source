#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\explosions\spaceObjectExplosionManager.py
import blue
import trinity
import geo2
import uthread
import random
import logging
from carbon.common.lib.const import MSEC, SEC
from eveexceptions.exceptionEater import ExceptionEater
from fsdBuiltData.client.explosionBuckets import GetRandomExplosion, GetExplosionBucket, HasSpecialExplosion, GetSpecialExplosion
from fsdBuiltData.client.explosionIDs import GetExplosion
from tacticalNavigation.ballparkFunctions import AddClientBall, RemoveClientBall
log = logging.getLogger(__name__)
RANDOM_LOCATOR_SORTING = 'random'
FROM_CENTER_SORTING = 'fromCenter'
FROM_LOCATOR_SORTING = 'fromLocator'

class ExplosionInfo(object):

    def __init__(self):
        self.resPath = 'NO RES PATH SET'
        self.explosionSorting = 'random'
        self.initialLocatorIdx = -1
        self.localScaling = 1.0
        self.globalScaling = 1.0
        self.modelWreckSwitchTime = 0
        self.localExplosionCount = -1


def CreateExplosionInfoFromFsdObject(explosionObject):
    explosionInfo = ExplosionInfo()
    explosion = GetExplosion(explosionObject.explosionID)
    explosionInfo.resPath = explosion.filePath
    explosionInfo.explosionSorting = explosion.childExplosionType
    explosionInfo.initialLocatorIdx = -1
    explosionInfo.localScaling = explosionObject.localScale
    explosionInfo.globalScaling = explosionObject.globalScale
    explosionInfo.modelWreckSwitchTime = explosion.modelSwitchDelayInMs
    explosionInfo.localExplosionCount = explosionObject.localExplosionCount
    return explosionInfo


class SpaceObjectExplosionManager(object):
    BALLPARK_MODE = True
    explosionLinkMap = {}
    explosionLinkWaiters = {}
    __preferredExplosions = {}

    @staticmethod
    def SetUpWreckFires(wreckModel):
        if wreckModel is None or not hasattr(wreckModel, 'locatorSets'):
            return
        allLocators = SpaceObjectExplosionManager.GetLocalExplosionTransforms(wreckModel)
        explosionChildren = wreckModel.Find('trinity.EveChildExplosion', 2)
        transforms = []
        for position, direction in allLocators:
            rotation = direction
            transform = geo2.MatrixTransformation((0, 0, 0), (0, 0, 0, 1), (1, 1, 1), (0, 0, 0), rotation, position)
            transforms.append(transform)

        for each in explosionChildren:
            each.SetLocalExplosionTransforms(transforms)
            each.Play()

    @staticmethod
    def GetLocalExplosionTransforms(model):
        explosionLocatorsSets = model.locatorSets.FindByName('explosions')
        if explosionLocatorsSets is None:
            explosionLocatorsSets = model.locatorSets.FindByName('damage')
        locators = []
        if explosionLocatorsSets:
            locators = explosionLocatorsSets.locators
        locators = model.TransformLocators(locators)
        return [ (l[0], l[1]) for l in locators ]

    @staticmethod
    def GetDamageLocatorTransforms(model):
        explosionLocatorsSets = model.locatorSets.FindByName('damage')
        locators = []
        if explosionLocatorsSets:
            locators = explosionLocatorsSets.locators
        locators = model.TransformLocators(locators)
        return [ (l[0], l[1]) for l in locators ]

    @staticmethod
    def SetUpChildExplosion(explosionModel, spaceObjectModel, explosionInfo):
        SpaceObjectExplosionManager.SetExplosionAudioScaling(explosionModel, explosionInfo)
        explosionChildren = explosionModel.Find('trinity.EveChildExplosion', 2)
        transforms = []
        globalExplosionOffset = (0, 0, 0)
        if spaceObjectModel is not None and hasattr(spaceObjectModel, 'locatorSets'):
            allLocators = SpaceObjectExplosionManager.GetLocalExplosionTransforms(spaceObjectModel)
            globalExplosionLocatorSet = spaceObjectModel.locatorSets.FindByName('globalExplosionOffset')
            if globalExplosionLocatorSet:
                convertedGlobalExplosionOffest = spaceObjectModel.TransformLocators(globalExplosionLocatorSet.locators)
                globalExplosionOffset = random.choice(convertedGlobalExplosionOffest)[0]
                if spaceObjectModel.rotationCurve is not None:
                    q = spaceObjectModel.rotationCurve.GetQuaternionAt(blue.os.GetSimTime())
                    rotationMatrix = geo2.MatrixRotationQuaternion((q.x,
                     q.y,
                     q.z,
                     q.w))
                    globalExplosionOffset = geo2.Vec3Transform(globalExplosionOffset, rotationMatrix)
            if spaceObjectModel.animationUpdater:
                spaceObjectModel.animationUpdater.animationEnabled = False
            if len(allLocators) > 0:
                locators = allLocators
                if explosionInfo.localExplosionCount != -1:
                    random.shuffle(locators)
                    locatorCount = min(len(locators) - 1, explosionInfo.localExplosionCount)
                    locators = locators[:locatorCount]
                if explosionInfo.explosionSorting == FROM_CENTER_SORTING:
                    point = spaceObjectModel.GetBoundingSphereCenter()
                    radius = spaceObjectModel.GetBoundingSphereRadius() * 0.2
                    locators.sort(key=lambda explosion: geo2.Vec3Distance(point, explosion[0]) + (random.random() - random.random()) * radius)
                elif explosionInfo.explosionSorting == FROM_LOCATOR_SORTING:
                    damageLocators = SpaceObjectExplosionManager.GetDamageLocatorTransforms(spaceObjectModel)
                    if explosionInfo.initialLocatorIdx < 0 or explosionInfo.initialLocatorIdx > len(damageLocators):
                        locatorTuple = random.choice(damageLocators)
                        point = locatorTuple
                    else:
                        point = damageLocators[explosionInfo.initialLocatorIdx]
                    locators.sort(key=lambda explosion: geo2.Vec3Distance(point[0], explosion[0]))
                    locators.insert(0, point)
                    locators.pop()
                else:
                    random.shuffle(locators)
                for position, direction in locators:
                    transform = geo2.MatrixTransformation((0, 0, 0), (0, 0, 0, 1), (1, 1, 1), (0, 0, 0), direction, position)
                    transforms.append(transform)

        for each in explosionChildren:
            each.scaling = (explosionInfo.localScaling, explosionInfo.localScaling, explosionInfo.localScaling)
            each.globalScaling = (explosionInfo.globalScaling, explosionInfo.globalScaling, explosionInfo.globalScaling)
            each.wreckSwitchOffsetFromGlobalStart = explosionInfo.modelWreckSwitchTime * 0.001
            each.SetLocalExplosionTransforms(transforms)
            each.SetGlobalExplosionOffset(globalExplosionOffset)

    @staticmethod
    def SetExplosionAudioScaling(explosionModel, explosionInfo):
        localExplosionList = []
        globalExplosionList = []
        for child in explosionModel.effectChildren:
            if getattr(child, 'localExplosion', None) is not None:
                localExplosionList.append(child.localExplosion)
            if getattr(child, 'localExplosions', None) is not None:
                localExplosionList.extend(child.localExplosions)
            if getattr(child, 'globalExplosion', None) is not None:
                globalExplosionList.append(child.globalExplosion)

        SpaceObjectExplosionManager.FindAndScaleAudioEmitters(localExplosionList, explosionInfo.localScaling)
        SpaceObjectExplosionManager.FindAndScaleAudioEmitters(globalExplosionList, explosionInfo.globalScaling)

    @staticmethod
    def FindAndScaleAudioEmitters(explosionList, attenuationScaling):
        for explosion in explosionList:
            for curve in explosion.Find('audio2.AudEventCurve'):
                if curve.audioEmitter:
                    curve.audioEmitter.SetAttenuationScalingFactor(attenuationScaling)

    @staticmethod
    def PlayExplosion(explosionModel):
        explosionChildren = explosionModel.Find('trinity.EveChildExplosion', 2)
        for each in explosionChildren:
            each.Play()

    @staticmethod
    def PlayExplosionAtPosition(explosionBucketID, raceName, position, scene):
        bucket = GetExplosionBucket(explosionBucketID)
        explosion = GetRandomExplosion(bucket, raceName)
        if not explosion:
            log.warning("Could not find an explosion for bucketID '%s'" % explosionBucketID)
        explosionInfo = CreateExplosionInfoFromFsdObject(explosion)
        SpaceObjectExplosionManager.PlayClientSideExplosionBall(scene, position, None, explosionInfo)

    @staticmethod
    def PlayClientSideExplosionBall(scene, worldPos, spaceObjectModel, explosionInfo, explosionLink = None, explosionOverride = None):
        if explosionOverride:
            explosionModel = explosionOverride
        else:
            explosionModel = trinity.Load(explosionInfo.resPath, nonCached=explosionLink == 'debug')
        if explosionModel is None:
            log.warn('Could not find explosion %s, can not explode model' % explosionInfo.resPath)
            return (0, None, 0)
        clientBall = None
        if SpaceObjectExplosionManager.BALLPARK_MODE:
            clientBall = AddClientBall(worldPos)
        if (explosionInfo.localExplosionCount == 0 or spaceObjectModel is None) and clientBall:
            explosionModel.translationCurve = clientBall
        elif hasattr(spaceObjectModel, 'translationCurve'):
            explosionModel.translationCurve = spaceObjectModel.translationCurve
            if hasattr(spaceObjectModel.translationCurve, 'GetTypeID'):
                if spaceObjectModel.translationCurve.GetTypeID() == 81080:
                    effectChildren = explosionModel.Find('trinity.EveChildContainer')
                    for effectChild in effectChildren:
                        if 'globalExplosion' in effectChild.name:
                            effectChild.rotation = spaceObjectModel.rotationCurve.value

        if hasattr(spaceObjectModel, 'rotationCurve'):
            explosionModel.rotationCurve = spaceObjectModel.rotationCurve
        scaling = getattr(spaceObjectModel, 'modelScale', 1.0)
        explosionModel.scaling = (scaling, scaling, scaling)
        if not explosionOverride:
            scene.objects.append(explosionModel)
        SpaceObjectExplosionManager.SetUpChildExplosion(explosionModel, spaceObjectModel, explosionInfo)
        explosionStartTime = blue.os.GetSimTime()
        log.debug('Exploding %s' % explosionInfo.resPath)
        SpaceObjectExplosionManager.PlayExplosion(explosionModel)
        explosionDuration = -1.0
        if isinstance(explosionModel, trinity.EveEffectRoot2):
            for child in explosionModel.effectChildren:
                explosionDuration = max(explosionDuration, getattr(child, 'totalDuration', 0))

        if explosionDuration == -1.0:
            explosionDuration = 60.0
        if clientBall:
            uthread.new(SpaceObjectExplosionManager._DelayedBallRemove, clientBall, scene, explosionModel, explosionDuration, explosionLink)
        return (explosionDuration, explosionModel, explosionStartTime)

    @staticmethod
    def _DelayedBallRemove(clientBall, scene, explosionModel, secTillBallRemove, explosionLink = None):
        blue.synchro.SleepSim(secTillBallRemove * 1000)
        if explosionModel in scene.objects:
            scene.objects.fremove(explosionModel)
        RemoveClientBall(clientBall)
        if explosionLink is not None:
            if explosionLink in SpaceObjectExplosionManager.explosionLinkMap:
                del SpaceObjectExplosionManager.explosionLinkMap[explosionLink]
            if explosionLink in SpaceObjectExplosionManager.explosionLinkWaiters:
                del SpaceObjectExplosionManager.explosionLinkWaiters[explosionLink]

    @staticmethod
    def ExplodeBucketForBall(ball, scene, initialLocatorIdx = -1, position = None, special = False):
        explosion, explosionInfo = SpaceObjectExplosionManager.GetExplosionForBall(ball, special)
        if not explosion:
            typeID = ball.typeData['typeID']
            log.warning("Could not find an explosion for '%s' (type '%s') with associated explosionBucketID = '%s'" % (ball.id, typeID, ball.explosionBucketID))
            simTime = blue.os.GetSimTime()
            SpaceObjectExplosionManager.AddExplosionTimeNotifications(ball.id, simTime, simTime)
            return (0, 0, None)
        explosionInfo.initialLocatorIdx = initialLocatorIdx
        explosionPosition = (ball.x, ball.y, ball.z)
        if position is not None:
            explosionPosition = position
        return SpaceObjectExplosionManager.Explode(scene, explosionPosition, ball.GetModel(), explosionInfo, ball.id)

    @staticmethod
    def GetExplosionForBall(ball, special = False):
        explosionBucket = GetExplosionBucket(ball.explosionBucketID)
        if ball.id in SpaceObjectExplosionManager.__preferredExplosions:
            explosion = SpaceObjectExplosionManager.__preferredExplosions[ball.id]
            del SpaceObjectExplosionManager.__preferredExplosions[ball.id]
        elif special and HasSpecialExplosion(explosionBucket):
            explosion = GetSpecialExplosion(explosionBucket)
        else:
            race = ball.typeData.get('sofRaceName', 'default')
            explosion = GetRandomExplosion(explosionBucket, race, randomnessSeed=ball.id)
        if explosion:
            return (explosion, CreateExplosionInfoFromFsdObject(explosion))
        return (None, None)

    @staticmethod
    def Explode(scene, pos, spaceObjectModel, explosionInfo, explosionLink = None, explosionOverride = None):
        if scene is None:
            log.warning("SpaceObjectExplosionManager: No scene therefore I can't create an explosion")
            return (0, 0, None)
        explosionDuration, explosionModel, startTime = SpaceObjectExplosionManager.PlayClientSideExplosionBall(scene, pos, spaceObjectModel, explosionInfo, explosionLink, explosionOverride)
        globalExplosionStart = SpaceObjectExplosionManager.GetGlobalExplosionStartTime(explosionModel)
        modelSwitchDelayInMs = globalExplosionStart * 1000 + explosionInfo.modelWreckSwitchTime
        wreckSwitchTime = int(startTime + modelSwitchDelayInMs * MSEC)
        globalStart = int(startTime + globalExplosionStart * SEC)
        SpaceObjectExplosionManager.AddExplosionTimeNotifications(explosionLink, globalStart, wreckSwitchTime)
        return (modelSwitchDelayInMs, explosionDuration, explosionModel)

    @staticmethod
    def GetGlobalExplosionStartTime(explosionModel):
        globalExplosionStart = 0.0
        if isinstance(explosionModel, trinity.EveEffectRoot2):
            for child in explosionModel.effectChildren:
                globalExplosionStart = max(globalExplosionStart, getattr(child, 'globalExplosionTime', 0))

        return globalExplosionStart

    @staticmethod
    def AddExplosionTimeNotifications(explosionLink, globalExplosionStartTime, wreckSwitchTime):
        if explosionLink is not None:
            SpaceObjectExplosionManager.explosionLinkMap[explosionLink] = (globalExplosionStartTime, wreckSwitchTime)
            if explosionLink in SpaceObjectExplosionManager.explosionLinkWaiters:
                for callback in SpaceObjectExplosionManager.explosionLinkWaiters[explosionLink]:
                    with ExceptionEater('SpaceObjectExplosionManager: AddExplosionTimeNotifications exception in callback %s' % callback):
                        callback(globalExplosionStartTime, wreckSwitchTime)

    @staticmethod
    def GetExplosionTimesWhenAvailable(ballID, callbackFunction):
        times = SpaceObjectExplosionManager.explosionLinkMap.get(ballID, None)
        if times is not None:
            globalExplosionStartTime, wreckSwitchTime = times
            callbackFunction(globalExplosionStartTime, wreckSwitchTime)
            return
        if ballID not in SpaceObjectExplosionManager.explosionLinkWaiters:
            SpaceObjectExplosionManager.explosionLinkWaiters[ballID] = []
        SpaceObjectExplosionManager.explosionLinkWaiters[ballID].append(callbackFunction)

    @staticmethod
    def SetPreferredExplosion(ballID, explosionObject):
        SpaceObjectExplosionManager.__preferredExplosions[ballID] = explosionObject

    @staticmethod
    def ClearWaiters():
        SpaceObjectExplosionManager.explosionLinkMap.clear()
        SpaceObjectExplosionManager.explosionLinkWaiters.clear()
