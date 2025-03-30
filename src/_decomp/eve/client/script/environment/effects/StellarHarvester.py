#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\StellarHarvester.py
import trinity
import geo2
import blue
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT

class StellarHarvester(GenericEffect):
    __guid__ = 'effects.StellarHarvester'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(StellarHarvester, self).__init__(trigger, effect, graphicFile)
        self.sunRotComponent = None
        self.sunSuckerZScaleComponent = None
        self.graphicFile = 'res:/fisfx/module/tg_starharvestinglaser_st_01a.red'
        self.secondaryGraphicFile = 'res:/fisfx/environment/celestial/multieffect/small_blue_star_stages_multieffect.red'

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('StellarHarvester: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        if hasattr(self, 'gfx'):
            self.RemoveFromScene(self.gfx)
        if hasattr(self, 'flickerEffect'):
            self.RemoveFromScene(self.flickerEffect)
        self.flickerEffect = None
        self.gfx.source = None
        self.gfx.dest = None
        self.gfx.sourceObject = None
        self.gfx = None
        self.gfxModel = None
        tmp = self.sunSuckerZScaleComponent.scaling
        self.sunSuckerZScaleComponent.scaling = (tmp[0], tmp[1], 0.0)
        self.sunRotComponent = None
        self.sunSuckerZScaleComponent = None

    def IsExplodingSystem(self, solarsystemID):
        explodingSystems = [30002086]
        return solarsystemID in explodingSystems

    def Prepare(self):
        self.DoPrepare()

    def DoPrepare(self):
        harvesterBall = self.GetEffectShipBall()
        scm = sm.GetService('sceneManager')
        scene = scm.GetRegisteredScene('default')
        targetBall = scene.sunBall if scene else None
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if harvesterBall is None:
            raise RuntimeError('StellarHarvester: no ball found')
        if not getattr(harvesterBall, 'model', None):
            raise RuntimeError('StellarHarvester: no model found')
        if targetBall is None:
            raise RuntimeError('StellarHarvester: no target ball found')
        if self.gfx is None:
            raise RuntimeError('StellarHarvester: no effect defined: %s' % getattr(self, 'graphicFile', 'None'))
        bp = sm.GetService('michelle').GetBallpark()
        solarsystemid = bp.solarsystemID
        if self.IsExplodingSystem(solarsystemid):
            self.secondaryGraphicFile = 'res:/fisfx/environment/celestial/multieffect/small_blue_star_flickering_multieffect.red'
        self.flickerEffect = self.RecycleOrLoad(self.secondaryGraphicFile)
        for each in self.flickerEffect.parameters:
            if each.name == 'Sun':
                each.object = scene.sunBall.GetModel()
            elif each.name == 'LensFlare':
                each.object = scene.lensflares[0]

        self.AddToScene(self.flickerEffect)
        self.flickerEffect.StartControllers()
        self.AddToScene(self.gfx)
        self._SetupLaserEndpoints(harvesterBall, targetBall)
        self.gfx.SetControllerVariable('star_state', 2)
        for controller in self.gfx.controllers:
            controller.Start()

        harvesterBall.model.StartControllers()
        targetBall.model.StartControllers()

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('StellarHarvester: no effect defined: %s' % getattr(self, 'graphicFile', 'None'))
        self.UpdateGraphicInfo(self.graphicInfo)

    def UpdateGraphicInfo(self, newGraphicInfo):
        self.graphicInfo = newGraphicInfo
        poseID = self._GetPoseID()
        self.gfx.StartFiring(0.0)
        self.gfx.SetControllerVariable('star_state', poseID)
        sun = self.GetEffectTargetBall()
        sun.SetControllerVariable('star_state', poseID)
        sun.model.StartControllers()

    def _SetupLaserEndpoints(self, sourceBall, targetBall):
        positionCurve = trinity.EveLocalPositionCurve()
        positionCurve.parent = sourceBall.GetModel()
        positionCurve.locatorSetName = 'triglavian_starharvest_source'
        positionCurve.behavior = trinity.EveLocalPositionBehavior.nearestFiringLocator
        positionCurve.locatorIndex = 0
        self.gfx.source = positionCurve
        self.gfx.dest = targetBall
        sun = targetBall.GetModel()
        sunLaser = sun.effectChildren.FindByName('Lazer')
        self.sunRotComponent = sunLaser
        sunSuckerXYScaleComponent = self.sunRotComponent.objects.FindByName('Scale_X_Y')
        self.sunSuckerZScaleComponent = sunSuckerXYScaleComponent.objects.FindByName('Scale_Z')
        self.RotateSunSucker(sourceBall, targetBall)
        self.ScaleSunSuckerZ(sourceBall, targetBall)

    def _GetPoseID(self):
        defaultPoseID = 0
        if not isinstance(self.graphicInfo, dict):
            return defaultPoseID
        return self.graphicInfo.get('poseID', defaultPoseID)

    def _GetStationPosInSunSpace(self, stationBall):
        station = stationBall
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

    def RotateSunSucker(self, sourceBall, targetBall):
        sunBall = targetBall
        sunPos = (sunBall.x, sunBall.y, sunBall.z)
        stationPos = self._GetStationPosInSunSpace(sourceBall)
        z = geo2.VectorD(0.0, 0.0, 1.0)
        direction = geo2.Vec3NormalizeD(geo2.Vec3SubtractD(sunPos, stationPos))
        self.sunRotComponent.rotation = geo2.QuaternionRotationArc(z, direction)

    def ScaleSunSuckerZ(self, sourceBall, targetBall):
        sunBall = targetBall
        sunPos = (sunBall.x, sunBall.y, sunBall.z)
        stationPos = self._GetStationPosInSunSpace(sourceBall)
        tmpScale = self.sunSuckerZScaleComponent.scaling
        zScale = geo2.Vec3DistanceD(sunPos, stationPos) - 0.5
        self.sunSuckerZScaleComponent.scaling = (tmpScale[0], tmpScale[1], zScale)
