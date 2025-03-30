#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\SunHarvestingBeam.py
import trinity
import geo2
import blue
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT

class SunHarvestingBeam(GenericEffect):
    __guid__ = 'effects.SunHarvestingBeam'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(SunHarvestingBeam, self).__init__(trigger, effect, graphicFile)
        self.sunRotComponent = None
        self.sunSuckerZScaleComponent = None

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('SunHarvestingBeam: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        self.RemoveFromScene(self.gfx)
        self.gfx.source = None
        self.gfx.dest = None
        self.gfx.sourceObject = None
        self.gfx = None
        self.gfxModel = None
        tmp = self.sunSuckerZScaleComponent.scaling
        self.sunSuckerZScaleComponent.scaling = (tmp[0], tmp[1], 0.0)
        self.sunRotComponent = None
        self.sunSuckerZScaleComponent = None

    def Prepare(self):
        self.DoPrepare()

    def DoPrepare(self):
        harvesterBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if harvesterBall is None:
            raise RuntimeError('SunHarvestingBeam: no ball found')
        if not getattr(harvesterBall, 'model', None):
            raise RuntimeError('SunHarvestingBeam: no model found')
        if targetBall is None:
            raise RuntimeError('SunHarvestingBeam: no target ball found')
        if self.gfx is None:
            raise RuntimeError('SunHarvestingBeam: no effect defined: %s' % getattr(self, 'graphicFile', 'None'))
        sceneManager = sm.GetService('sceneManager')
        scene = sceneManager.registeredScenes['default']
        self._SetupLaserEndpoints(harvesterBall, scene.sunBall)
        self.AddToScene(self.gfx)

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('SunHarvestingBeam: no effect defined: %s' % getattr(self, 'graphicFile', 'None'))
        self.UpdateGraphicInfo(self.graphicInfo)

    def UpdateGraphicInfo(self, newGraphicInfo):
        self.graphicInfo = newGraphicInfo
        poseID = self._GetPoseID()
        self.gfx.StartFiring(0.0)
        self.gfx.SetControllerVariable('star_state', poseID)
        sun = self.GetEffectTargetBall()
        sun.SetControllerVariable('star_state', poseID)

    def _SetupLaserEndpoints(self, sourceBall, targetBall):
        positionCurve = trinity.EveLocalPositionCurve()
        positionCurve.parent = sourceBall.GetModel()
        positionCurve.locatorSetName = 'triglavian_starharvest_source'
        positionCurve.behavior = trinity.EveLocalPositionBehavior.nearestFiringLocator
        positionCurve.locatorIndex = 0
        self.gfx.source = positionCurve
        self.gfx.dest = targetBall
        sun = targetBall.GetModel()
        sunLaser = sun.effectChildren.FindByName('Laser')
        if sunLaser is not None:
            self.sunRotComponent = sunLaser.objects.FindByName('HarvestLaserEnd_RotMe')
            sunSuckerXYScaleComponent = self.sunRotComponent.objects.FindByName('Scale_X_Y')
            self.sunSuckerZScaleComponent = sunSuckerXYScaleComponent.objects.FindByName('Scale_Z')
            self.RotateSunSucker()
            self.ScaleSunSuckerZ()

    def _GetPoseID(self):
        defaultPosID = 0
        if not isinstance(self.graphicInfo, dict):
            return defaultPosID
        return self.graphicInfo.get('poseID', defaultPosID)

    def _GetStationPosInSunSpace(self):
        station = self.GetEffectShipBall()
        stationModel = station.GetModel()
        offset = (0.0, 0.0, 0.0)
        locatorSet = stationModel.locatorSets.FindByName('triglavian_starharvest_source')
        if locatorSet:
            offset = locatorSet.locators[0][0]
        rotationCurve = stationModel.modelRotationCurve
        if rotationCurve:
            r = rotationCurve.GetQuaternionAt(blue.os.GetSimTime())
            offset = geo2.QuaternionTransformVector((r.x,
             r.y,
             r.z,
             r.w), offset)
        translation = (station.x, station.y, station.z)
        offset = geo2.Vec3AddD(offset, translation)
        sunBall = self.GetEffectTargetBall()
        sunScale = sunBall.GetModel().scaling[0]
        return geo2.Vec3ScaleD(offset, 1.0 / sunScale)

    def RotateSunSucker(self):
        sunBall = self.GetEffectTargetBall()
        sunPos = (sunBall.x, sunBall.y, sunBall.z)
        stationPos = self._GetStationPosInSunSpace()
        z = geo2.VectorD(0.0, 0.0, 1.0)
        direction = geo2.Vec3NormalizeD(geo2.Vec3SubtractD(sunPos, stationPos))
        self.sunRotComponent.rotation = geo2.QuaternionRotationArc(z, direction)

    def ScaleSunSuckerZ(self):
        sunBall = self.GetEffectTargetBall()
        sunPos = (sunBall.x, sunBall.y, sunBall.z)
        stationPos = self._GetStationPosInSunSpace()
        tmpScale = self.sunSuckerZScaleComponent.scaling
        zScale = geo2.Vec3DistanceD(sunPos, stationPos) - 0.5
        self.sunSuckerZScaleComponent.scaling = (tmpScale[0], tmpScale[1], zScale)
