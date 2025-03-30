#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveSpaceObject\missile.py
import blue
import geo2
import trinity
import uthread2
from eve.client.script.ui.camera.cameraUtil import GetPixelSizeAcrossEst
from eve.client.script.environment.spaceObject.ExplosionManager import ExplosionManager

class MissileControllerBase:

    def OnAllMissileWarheadsExploded(self):
        pass

    def OnMissileModelCleared(self, model):
        pass

    def PlaceMissileImpact(self, impactModel, impactPosition, targetLocatorID):
        pass

    def RemoveMissileImpact(self, impactModel, isFinalExplosion):
        pass


def EstimateTimeToTarget(mslPos, targetPos, targetRadius, velocity):
    offset = mslPos - targetPos
    return (offset.Length() - targetRadius) / velocity


def _GetTransformFromCurves(translationCurve, rotationCurve, time):
    q = rotationCurve.GetQuaternionAt(time)
    v = translationCurve.GetVectorAt(time)
    return geo2.MatrixAffineTransformation(1.0, (0.0, 0.0, 0.0), (q.x,
     q.y,
     q.z,
     q.w), (v.x, v.y, v.z))


def _GetWarheadStartTransform(warheadIdx, turretSet, missileTranslationCurve, missileRotationCurve):
    time = blue.os.GetSimTime()
    missileBallWorldTransform = _GetTransformFromCurves(missileTranslationCurve, missileRotationCurve, time)
    firingPosWorldTransform = missileBallWorldTransform
    invMissileBallWorldTransform = geo2.MatrixInverse(missileBallWorldTransform)
    if turretSet is not None:
        firingPosWorldTransform = turretSet.GetFiringBoneWorldTransform(turretSet.currentCyclingFiresPos + warheadIdx)
    return geo2.MatrixMultiply(firingPosWorldTransform, invMissileBallWorldTransform)


def _GetMissileStartSpeed(missileTranslationCurve, missileRotationCurve, sourceTranslationCurve):
    time = blue.os.GetSimTime()
    missileBallWorldTransform = _GetTransformFromCurves(missileTranslationCurve, missileRotationCurve, time)
    sourceSpeed = (0.0, 0.0, 0.0)
    if sourceTranslationCurve is not None:
        s = sourceTranslationCurve.GetVectorDotAt(time)
        sourceSpeed = (s.x, s.y, s.z)
    invMissileBallWorldTransform = geo2.MatrixInverse(missileBallWorldTransform)
    startSpeed = geo2.Vec3TransformNormal(sourceSpeed, invMissileBallWorldTransform)
    return startSpeed


class _WarheadTemplate:

    def __init__(self, resourceKey, doSpread):
        self.warhead = None
        self.resourceKey = resourceKey
        self.doSpread = doSpread

    def PopulateTemplateAndPrepareMissile(self, missile):
        self.warhead = missile.warheads[0]
        del missile.warheads[:]

    def CreateCopy(self, warheadID):
        wh = blue.recycler.RecycleOrCopy(self.resourceKey, self.warhead)
        wh.doSpread = self.doSpread
        wh.id = warheadID
        return wh


class MissileTurretWrapper:

    def __init__(self, turretSet, shootFunction = None):
        self.turretSet = turretSet
        self.warheadCount = 1
        self._shootFunction = shootFunction
        if turretSet is not None:
            self.firingDelay = turretSet.randomFiringDelay
            self.firingEffect = turretSet.firingEffect
            if turretSet.maxCyclingFirePos == 1:
                if turretSet.firingEffect is not None:
                    self.warheadCount = turretSet.firingEffect.GetPerMuzzleEffectCount()
        else:
            self.firingDelay = 0.0
            self.firingEffect = None

    def StartShooting(self):
        if self._shootFunction is not None:
            self._shootFunction()

    def GetMuzzleDelay(self, i):
        return getattr(self.firingEffect, 'firingDelay' + str(i + 1), 0.0)


class MissileGraphics:

    def __init__(self, name, missileFileName, explosionPath, missileController):
        self._name = name
        self._explosionPath = explosionPath
        self._missileFileName = missileFileName
        self._explosionManager = ExplosionManager()
        self._missileController = missileController
        self._translationCurve = None
        self._rotationCurve = None
        self._model = None
        self._sourceTranslationCurve = None
        self._targetModel = None
        self._targetRadius = 0
        self._totalWarheadCount = 0
        self._warheadsReleased = 0
        self._warheadImpactsRemoved = 0

    def LoadModel(self):
        self._model = blue.recycler.RecycleOrLoad(self._missileFileName)
        self._model.name = self._name
        return self._model

    def SetSourceTranslationCurve(self, translationCurve):
        self._sourceTranslationCurve = translationCurve

    def SetMissileCurves(self, translationCurve, rotationCurve):
        self._translationCurve = translationCurve
        self._rotationCurve = rotationCurve
        if self._model is not None:
            self._model.translationCurve = translationCurve
            self._model.rotationCurve = rotationCurve

    def SetTarget(self, targetModel, targetRadius):
        self._targetModel = targetModel
        self._targetRadius = targetRadius
        if self._model is not None:
            self._model.target = targetModel
            self._model.targetRadius = targetRadius

    def Start(self, turretSetInfos, timeToTarget, doSpread = False):
        if self._model is None:
            return
        whKey = self._missileFileName + ':warhead'
        warheadTemplate = _WarheadTemplate(whKey, doSpread)
        warheadTemplate.PopulateTemplateAndPrepareMissile(self._model)
        syncWarheadsCount = 0
        for turretInfo in turretSetInfos:
            turretInfo.StartShooting()
            for i in range(turretInfo.warheadCount):
                wh = warheadTemplate.CreateCopy(syncWarheadsCount)
                muzzleDelay = turretInfo.GetMuzzleDelay(i)
                wh.PrepareLaunch()
                uthread2.start_tasklet(self._StartWarhead, wh, turretInfo.firingDelay + muzzleDelay, i, turretInfo.turretSet)
                self._model.warheads.append(wh)
                syncWarheadsCount += 1

        startSpeed = _GetMissileStartSpeed(self._translationCurve, self._rotationCurve, self._sourceTranslationCurve)
        self._model.explosionCallback = self._ExplosionCallback
        self._totalWarheadCount = syncWarheadsCount
        self._explosionManager.Preload(self._explosionPath, self._totalWarheadCount)
        self._model.Start(startSpeed, timeToTarget)

    def ClearAll(self):
        self._ClearModel()
        warheadsLeft = self._totalWarheadCount - self._warheadsReleased
        self._warheadsReleased = self._totalWarheadCount
        if warheadsLeft != 0:
            self._explosionManager.Cancel(self._explosionPath, count=warheadsLeft)
        self._missileController = None
        self._translationCurve = None
        self._rotationCurve = None
        self._sourceTranslationCurve = None
        self._targetModel = None

    def _StartWarhead(self, warhead, delay, warheadIdx, turretSet):
        blue.synchro.SleepSim(1000.0 * delay)
        if self._model is None:
            return
        startTransform = _GetWarheadStartTransform(warheadIdx, turretSet, self._translationCurve, self._rotationCurve)
        warhead.Launch(startTransform)

    def _ExplosionCallback(self, warheadIdx):
        uthread2.start_tasklet(self._SpawnExplosion, warheadIdx)

    def _GetExplosionPosition(self, warheadIdx):
        if warheadIdx < len(self._model.warheads):
            warheadPosition = self._model.warheads[warheadIdx].explosionPosition
        else:
            warheadPosition = self._model.worldPosition
        return warheadPosition

    def _GetExplosionTargetLocator(self, warheadIdx):
        if warheadIdx < len(self._model.warheads):
            warheadTargetLocatorID = self._model.warheads[warheadIdx].targetLocatorID
        else:
            warheadTargetLocatorID = -1
        return warheadTargetLocatorID

    def _ClearWarheads(self, model):
        if len(model.warheads) > 0:
            del model.warheads[1:]
            whPrime = model.warheads[0]
            del whPrime.observers[:]

    def _ClearModel(self):
        if self._model is not None:
            self._ClearWarheads(self._model)
            self._model.target = None
            self._model.explosionCallback = None
            self._missileController.OnMissileModelCleared(self._model)
            self._model.translationCurve = None
            self._model.rotationCurve = None
            for ob in self._model.observers:
                ob.observer = None

            self._model = None

    def DetonateWarhead(self, warheadID):
        self._SpawnExplosion(warheadID)

    def _SpawnExplosion(self, warheadIdx):
        if not self._model:
            return
        explosionPosition = self._GetExplosionPosition(warheadIdx)
        explosionTargetLocatorID = self._GetExplosionTargetLocator(warheadIdx)
        if self._warheadsReleased >= self._totalWarheadCount:
            return
        self._warheadsReleased += 1
        if self._warheadsReleased == self._totalWarheadCount:
            self._ClearModel()
            self._missileController.OnAllMissileWarheadsExploded()
        controller = self._missileController

        def _cleanupCallback(impactModel):
            self._CleanupExplosion(impactModel, controller)

        spawnExplosion = True
        sceneManager = sm.GetServiceIfRunning('sceneManager')
        camera = sceneManager.GetActivePrimaryCamera() if sceneManager else None
        if camera is not None:
            radius = self._explosionManager.GetBoundingSphereRadius(self._explosionPath)
            pixelSize = GetPixelSizeAcrossEst(explosionPosition, radius, camera.GetEyePosition(), camera.projectionMatrix.transform)
            pixelThreshold = 4
            spawnExplosion = pixelSize > pixelThreshold
        if spawnExplosion:
            impactModel = self._explosionManager.GetExplosion(self._explosionPath, preloaded=True, callback=_cleanupCallback)
            if impactModel:
                for modelController in getattr(impactModel, 'controllers', []):
                    modelController.Start()

            controller.PlaceMissileImpact(impactModel, explosionPosition, explosionTargetLocatorID)
        if self._warheadsReleased == self._totalWarheadCount:
            controller.OnAllMissileWarheadsExploded()
        if not spawnExplosion:
            self._warheadImpactsRemoved += 1
            if self._warheadsReleased == self._totalWarheadCount and self._warheadImpactsRemoved == self._warheadsReleased:
                self.ClearAll()

    def _CleanupExplosion(self, impactModel, missileController):
        self._warheadImpactsRemoved += 1
        final = self._warheadsReleased == self._totalWarheadCount and self._warheadImpactsRemoved == self._warheadsReleased
        if missileController:
            if impactModel:
                for modelController in getattr(impactModel, 'controllers', []):
                    modelController.Stop()

            missileController.RemoveMissileImpact(impactModel, final)
        if final:
            self.ClearAll()
