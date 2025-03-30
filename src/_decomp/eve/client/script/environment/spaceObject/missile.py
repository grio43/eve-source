#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\missile.py
import math
import random
import blue
import carbon.common.script.util.logUtil as log
import eveSpaceObject.missile as gfxmissile
import evegraphics.settings as gfxsettings
import geo2
import inventorycommon.typeHelpers
import pytelemetry.zoning as telemetry
import uthread
from carbon.client.script.environment.audioService import GetAudioService
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.parklife.sceneManager import GetSceneManager
from eve.client.script.remote.michelle import GetMichelle
from fsdBuiltData.client.groupGraphics import GetGraphicIdsFromTypeID
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from destructionEffect import destructionType as destructionEffectType
SECOND = 10000000

def _DestroyClientBall(ball):
    bp = GetMichelle().GetBallpark()
    if bp is not None and ball.ballpark is not None:
        bp.RemoveBall(ball.id)


def _SpawnClientBall(position):
    bp = GetMichelle().GetBallpark()
    if bp is None:
        return
    egopos = bp.GetCurrentEgoPos()
    explosionPosition = (position[0] + egopos[0], position[1] + egopos[1], position[2] + egopos[2])
    return bp.AddClientSideBall(explosionPosition)


def _ShakeCamera(shakeMagnitude, explosionPosition):
    camera = GetSceneManager().GetActiveSpaceCamera()
    if camera:
        camera.ShakeCamera(shakeMagnitude, explosionPosition, 'Missile')


def _GetScene():
    return GetSceneManager().GetRegisteredScene('default')


def _GetMissilesEnabled():
    missilesDesired = gfxsettings.Get(gfxsettings.UI_MISSILES_ENABLED)
    if missilesDesired:
        scene = GetSceneManager().GetRegisteredScene('default', allowBlocking=False)
        if scene is None:
            return False
        updateTime = scene.updateTime
        now = blue.os.GetSimTime()
        if now < updateTime:
            return False
        delta = blue.os.TimeDiffInMs(updateTime, now)
        return delta < 2000
    return missilesDesired


class Missile(SpaceObject):
    __guid__ = 'spaceObject.Missile'

    def __init__(self):
        SpaceObject.__init__(self)
        self.exploded = False
        self.collided = False
        self.targetId = None
        self.sourceShipID = None
        self.sourceModuleIDList = []
        self._delayedBall = None
        self._randomizeImpactRotation = True
        self.enabled = _GetMissilesEnabled()
        self.missileRadius = 100
        self._missileModel = None

    @telemetry.ZONE_METHOD
    def LoadModel(self, fileName = None, loadedModel = None):
        if not self.enabled:
            return
        slimItem = self.typeData['slimItem']
        self.sourceShipID = slimItem.sourceShipID
        self.sourceModuleIDList = slimItem.launchModules
        impactFileName = inventorycommon.typeHelpers.GetGraphicFile(slimItem.typeID)
        if impactFileName == '':
            log.LogError('missile::LoadModel failed to get impact red filename for missile typeID ' + str(slimItem.typeID) + ' missileID : ' + str(self.id) + ' sourceShipID: ' + str(self.sourceShipID))
            return
        missileGraphicID = GetGraphicIdsFromTypeID(slimItem.typeID, [None])[0]
        if missileGraphicID is None:
            log.LogError('missile::LoadModel failed to get missile graphicID for typeID %s from groupGraphics', slimItem.typeID)
            return
        missileFileName = GetGraphicFile(missileGraphicID)
        if missileFileName is None:
            log.LogError('missile::LoadModel failed to get missile red filename for missile typeID ' + str(slimItem.typeID) + ' missileID : ' + str(self.id) + ' sourceShipID: ' + str(self.sourceShipID))
            return
        self.targetId = self.followId
        self._missileModel = gfxmissile.MissileGraphics('Missile in %s' % self.id, missileFileName, impactFileName, self)
        self.model = self._missileModel.LoadModel()
        if self.model is None:
            self.LogError('missile::LoadModel failed to load a model ' + str(missileFileName))
            return
        self._missileModel.SetMissileCurves(self._GetMissileTranslationCurve(), self._GetMissileRotationCurve())
        scene = GetSceneManager().GetRegisteredScene('default')
        scene.objects.append(self.model)

    def _GetMissileTranslationCurve(self):
        return self

    def _GetMissileRotationCurve(self):
        return self

    def _GetModelTurret(self, moduleIdx):
        if len(self.sourceModuleIDList) <= moduleIdx:
            self.logger.warning('moduleIdx: + %s is too high to index into list!', str(moduleIdx))
            return
        slimItemID = self.sourceModuleIDList[moduleIdx]
        sourceShipBall = GetMichelle().GetBall(self.sourceShipID)
        if sourceShipBall is not None:
            if not hasattr(sourceShipBall, 'modules'):
                return
            if sourceShipBall.modules is None:
                return
            if slimItemID in sourceShipBall.modules:
                return sourceShipBall.modules[slimItemID]

    def _EstimateTimeToTarget(self, toCenter = False):
        targetBall = GetMichelle().GetBall(self.targetId)
        if targetBall is None:
            return 5.0
        now = blue.os.GetSimTime()
        myPos = self.GetVectorAt(now)
        targetPos = targetBall.GetVectorAt(now)
        if toCenter:
            targetRadius = 0
        else:
            targetRadius = targetBall.radius
        return gfxmissile.EstimateTimeToTarget(myPos, targetPos, targetRadius, self.maxVelocity)

    def _GetTimeToTarget(self):
        timeToTarget = self._EstimateTimeToTarget()
        doSpread = True
        if timeToTarget < 1.6:
            doSpread = False
        timeToTargetCenter = max(0.5, self._EstimateTimeToTarget(toCenter=True))
        if timeToTarget > 0:
            timeToTarget = (timeToTarget + timeToTargetCenter) * 0.5
        else:
            timeToTarget = timeToTargetCenter * 0.5
        return (doSpread, timeToTarget)

    def _GetAllTurretSets(self, moduleCount):
        turretWrappers = []
        for moduleIdx in range(0, moduleCount):
            turrets = self._GetModelTurret(moduleIdx)
            if not isinstance(turrets, list):
                turrets = [turrets]
            for turretIndex, turret in enumerate(turrets):
                if turret is not None and len(turret.turretSets) > 0:
                    turretWrappers.append(gfxmissile.MissileTurretWrapper(turret.turretSets[0], turret.StartShooting))
                    if hasattr(turret.turretSets[0], 'randomizeExplosionRotation'):
                        self._randomizeImpactRotation = turret.turretSets[0].randomizeExplosionRotation
                else:
                    turretWrappers.append(gfxmissile.MissileTurretWrapper(None))

        return turretWrappers

    @telemetry.ZONE_METHOD
    def Prepare(self):
        if not self.enabled:
            return
        if self.collided:
            return
        SpaceObject.Prepare(self)
        if self.model is None:
            return
        if getattr(self, 'sourceModuleIDList', None) is None:
            self.sourceModuleIDList = [0]
        moduleCount = max(len(self.sourceModuleIDList), 1)
        doSpread, timeToTarget = self._GetTimeToTarget()
        if not doSpread:
            self.DoCollision(self.targetId, 0, 0, 0)
        if len(self.model.warheads) != 1:
            log.LogError('There must be one and only one warhead per missile in: ' + str(self.model.name))
            return
        if self.targetId:
            targetBall = GetMichelle().GetBall(self.targetId)
            if targetBall is not None:
                self._missileModel.SetTarget(targetBall.model, targetBall.radius)
        self._missileModel.SetSourceTranslationCurve(GetMichelle().GetBall(self.sourceShipID))
        turretSetInfos = self._GetAllTurretSets(moduleCount)
        self._missileModel.Start(turretSetInfos, timeToTarget, doSpread)

    @telemetry.ZONE_METHOD
    def RemoveAndClearModel(self, model, scene = None):
        if model is not None:
            SpaceObject.RemoveAndClearModel(self, model, scene=scene)

    def DoCollision(self, targetId, fx, fy, fz, fake = False):
        if self.collided:
            return
        self.collided = True
        if self.model is None:
            return
        uthread.new(self._DoCollision)

    def _DoCollision(self):
        if self.model is None:
            return
        pos = self.GetVectorAt(blue.os.GetSimTime())
        self._delayedBall = _SpawnClientBall((pos.x, pos.y, pos.z))
        self._missileModel.SetMissileCurves(self._delayedBall, self)

    def Expire(self):
        self.exploded = True

    def ApplyImpactTorqueToTarget(self, targetLocatorID, blastSize):
        targetBall = GetMichelle().GetBall(self.targetId)
        if hasattr(targetBall, 'ApplyTorqueAtDamageLocator') and targetLocatorID != -1 and not math.isnan(blastSize):
            velocity = self.GetVectorDotAt(blue.os.GetSimTime())
            targetBall.ApplyTorqueAtDamageLocator(targetLocatorID, (velocity.x, velocity.y, velocity.z), blastSize)

    def Explode(self):
        return self.collided

    @telemetry.ZONE_METHOD
    def Release(self, origin = None):
        if not self.collided and self.enabled and destructionEffectType.isExplosionOrOverride(self.destructionEffectId):
            self.Expire()
            self.ReleaseAll()

    def DoFinalCleanup(self):
        SpaceObject.DoFinalCleanup(self)
        self.ReleaseAll()

    def ReleaseAll(self):
        if self._missileModel is not None:
            self._missileModel.ClearAll()
            self._missileModel = None
        self.model = None
        self._ClearDelayedBall()

    def Display(self, display = 1, canYield = True):
        if self.enabled:
            SpaceObject.Display(self, display, canYield)

    def _ClearDelayedBall(self):
        if self._delayedBall:
            _DestroyClientBall(self._delayedBall)
            self._delayedBall = None

    def OnAllMissileWarheadsExploded(self):
        self._ClearDelayedBall()
        self.exploded = True

    def OnMissileModelCleared(self, model):
        self.RemoveAndClearModel(model, _GetScene())

    def PlaceMissileImpact(self, impactModel, impactPosition, targetLocatorID):
        explosionBall = _SpawnClientBall(impactPosition)
        impactModel.translationCurve = explosionBall
        useRandomRotation = True
        if not self._randomizeImpactRotation:
            targetBall = GetMichelle().GetBall(self.targetId)
            if targetBall is not None and targetLocatorID != -1:
                if hasattr(targetBall.model, 'GetLocatorRotationFromSet'):
                    impactDirection = targetBall.model.GetLocatorRotationFromSet(targetLocatorID, True, 'damage')
                    impactRotation = geo2.QuaternionRotationArc((0, 1, 0), impactDirection)
                    useRandomRotation = False
        if useRandomRotation:
            impactRotation = geo2.QuaternionRotationSetYawPitchRoll(random.random() * 2.0 * math.pi, random.random() * 2.0 * math.pi, random.random() * 2.0 * math.pi)
        impactModel.rotation = impactRotation
        scene = _GetScene()
        if scene is not None:
            scene.objects.append(impactModel)
        shakeMagnitude = min(impactModel.boundingSphereRadius, 250)
        shakeMagnitude = max(shakeMagnitude, 50)
        _ShakeCamera(shakeMagnitude, impactPosition)
        self.ApplyImpactTorqueToTarget(targetLocatorID, self.missileRadius)

    def RemoveMissileImpact(self, impactModel, isFinalExplosion):
        if impactModel.translationCurve is not None:
            _DestroyClientBall(impactModel.translationCurve)
        self.RemoveAndClearModel(impactModel, _GetScene())
        if isFinalExplosion:
            self.ReleaseAll()


class Bomb(Missile):

    def __init__(self):
        Missile.__init__(self)
        self.impactPosition = None

    def Release(self):
        if self.model is not None:
            self.impactPosition = self.model.worldPosition
        if self._missileModel is not None:
            self._missileModel.DetonateWarhead(0)
        SpaceObject.Release(self, 'Bomb')

    def _EstimateTimeToTarget(self, toCenter = False):
        return 20.0

    def PlaceMissileImpact(self, impactModel, impactPosition, targetLocatorID):
        if self.impactPosition is not None:
            impactPosition = self.impactPosition
        Missile.PlaceMissileImpact(self, impactModel, impactPosition, targetLocatorID)

    def _GetMissileTranslationCurve(self):
        return self

    def _GetMissileRotationCurve(self):
        sourceShipBall = GetMichelle().GetBall(self.sourceShipID)
        return sourceShipBall
