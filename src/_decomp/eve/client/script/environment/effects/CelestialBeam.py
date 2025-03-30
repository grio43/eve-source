#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\CelestialBeam.py
import trinity
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT

class CelestialBeam(GenericEffect):
    __guid__ = 'effects.CelestialBeam'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(CelestialBeam, self).__init__(trigger, effect, graphicFile)
        self.celestialID = trigger.targetID
        self.graphicFile = graphicFile

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('CelestialBeam: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        if hasattr(self, 'gfx'):
            self.RemoveFromScene(self.gfx)
        self.gfx.source = None
        self.gfx.dest = None
        self.gfx.sourceObject = None
        self.gfx = None
        self.gfxModel = None

    def UpdateGraphicInfo(self, newGraphicInfo):
        if self.gfx:
            self.gfx.SetControllerVariable('isFiring', newGraphicInfo['isFiring'])
            if newGraphicInfo['isFiring'] > 0.0:
                self.gfx.StartFiring(0.0)

    def Prepare(self, addToScene = True):
        self.DoPrepare()

    def CheckEndPoints(self):
        hasParentChanged = self.GetEffectShipBall().GetModel() != self.gfx.source.parent
        if hasParentChanged:
            sourceBall = self.GetEffectShipBall()
            targetBall = self.GetEffectTargetBall()
            if sourceBall is not None and targetBall is not None:
                self._SetUpBeamEndpoints(sourceBall, targetBall)

    def _SetUpBeamEndpoints(self, sourceBall, targetBall):
        sourcePositionCurve = trinity.EveLocalPositionCurve()
        sourcePositionCurve.parent = sourceBall.GetModel()
        sourcePositionCurve.locatorSetName = 'beam_source'
        sourcePositionCurve.behavior = trinity.EveLocalPositionBehavior.nearestFiringLocator
        sourcePositionCurve.locatorIndex = 0
        self.gfx.source = sourcePositionCurve
        targetPositionCurve = trinity.EveLocalPositionCurve()
        self.gfx.dest = targetPositionCurve
        targetPositionCurve.parent = targetBall.GetModel()
        targetPositionCurve.behavior = trinity.EveLocalPositionBehavior.nearestBounds
        self.gfx.dest.parentPositionCurve = targetBall
        self.gfx.dest.parentRotationCurve = targetBall
        self.gfx.dest.alignPositionCurve = self.GetBallPositionCurve(sourceBall)
        self.gfx.dest.offset = targetBall.radius

    def DoPrepare(self):
        sourceBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        if sourceBall is not None and targetBall is not None:
            try:
                self.gfx = self.RecycleOrLoad(self.graphicFile)
            except Exception as e:
                raise RuntimeError('CelestialBeam: no effect found:' + self.__guid__)

            self.AddToScene(self.gfx)
            self._SetUpBeamEndpoints(sourceBall, targetBall)

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('CelestialBeam: no effect defined:' + self.__guid__)
        elif 'isFiring' in self.graphicInfo:
            self.gfx.SetControllerVariable('isFiring', self.graphicInfo['isFiring'])
            if self.graphicInfo['isFiring'] > 0.0:
                self.gfx.StartFiring(0.0)
