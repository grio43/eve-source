#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\EveStretch3.py
import blue
import trinity
import uthread
from eve.client.script.environment.effects.GenericEffect import GenericEffect, GetBoundingBox, STOP_REASON_DEFAULT, STOP_REASON_BALL_REMOVED
from fsdBuiltData.common.graphicIDs import GetGraphicFile

class EveStretch3(GenericEffect):
    __guid__ = 'effects.EveStretch3'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(EveStretch3, self).__init__(trigger, effect, graphicFile)
        self.locatorSetName = trigger.graphicInfo.get('locatorSetName', 'damage')
        self.controllerTriggers = trigger.graphicInfo.get('controllerTrigger', None)
        gIDOverride = trigger.graphicInfo.get('graphicIDOverride', None)
        self.lingerOnDeathTime = trigger.graphicInfo.get('deathTimer', None)
        if gIDOverride is not None:
            graphicFilePath = GetGraphicFile(gIDOverride)
            if graphicFilePath is not None:
                self.graphicFile = graphicFilePath

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('EveStretch3: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        self.gfx.StopFiring()
        self.gfx.SetControllerVariable('LinkWithShip_Active', 0)
        self.RemoveFromScene(self.gfxModel)
        if isinstance(self.gfx.source, trinity.EveLocalPositionCurve):
            self.gfx.source.parentPositionCurve = None
            self.gfx.source.parentRotationCurve = None
            self.gfx.source.alignPositionCurve = None
        if isinstance(self.gfx.dest, trinity.EveLocalPositionCurve):
            self.gfx.dest.parentPositionCurve = None
            self.gfx.dest.parentRotationCurve = None
            self.gfx.dest.alignPositionCurve = None
        scene = self.fxSequencer.GetScene()
        if reason == STOP_REASON_BALL_REMOVED:
            if self.lingerOnDeathTime is not None:
                uthread.new(EveStretch3._DelayedCleanUp, self.lingerOnDeathTime, self.gfx, scene)
        else:
            self._CleanUp(self.gfx, scene)

    @staticmethod
    def _DelayedCleanUp(timeInSec, model, scene):
        blue.synchro.SleepSim(timeInSec * 1000)
        EveStretch3._CleanUp(model, scene)

    @staticmethod
    def _CleanUp(model, scene):
        if scene is not None and model is not None:
            scene.objects.fremove(model)

    def Prepare(self):
        self.DoPrepare()

    def DoPrepare(self):
        shipBall = self.GetEffectShipBall()
        positionCurve = self.GetBallPositionCurve(shipBall)
        targetBall = self.GetEffectTargetBall()
        if shipBall is None:
            raise RuntimeError('StretchEffect: no ball found')
        if not getattr(shipBall, 'model', None):
            raise RuntimeError('StretchEffect: no model found')
        if targetBall is None:
            raise RuntimeError('StretchEffect: no target ball found')
        if targetBall.model is None or shipBall.model is None:
            raise RuntimeError('StretchEffect: Both Source and Target need to have models')
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect found: ' + str(getattr(self, 'graphicFile', 'None')))
        if self.controllerTriggers is not None:
            for key, value in self.controllerTriggers.items():
                self.gfx.SetControllerVariable(key, value)

        self.gfx.destSpaceObject = targetBall.model
        self.gfx.sourceSpaceObject = shipBall.model
        sourceCurve = trinity.EveLocalPositionCurve(trinity.EveLocalPositionBehavior.nearestBounds)
        sourceCurve.parent = shipBall.model
        destCurve = trinity.EveLocalPositionCurve(trinity.EveLocalPositionBehavior.nearestFiringLocator)
        destCurve.locatorSetName = self.locatorSetName
        destCurve.parent = targetBall.model
        self.gfx.source = sourceCurve
        self.gfx.dest = destCurve
        self.SetDestCurve(targetBall)
        self.gfx.source.parentPositionCurve = shipBall
        self.gfx.source.parentRotationCurve = shipBall
        self.gfx.source.alignPositionCurve = targetBall
        sourceScale = GetBoundingBox(shipBall, scale=1.0)
        self.gfx.source.boundingSize = sourceScale
        self.AddToScene(self.gfx)

    def SetDestCurve(self, targetBall):
        if targetBall is None:
            self.Stop(STOP_REASON_BALL_REMOVED)
            return
        targetModelWorldPos = self.gfx.sourceSpaceObject.modelWorldPosition
        goodIndex = self.gfx.destSpaceObject.GetGoodLocatorIndex(targetModelWorldPos, self.locatorSetName)
        self.gfx.dest.locatorIndex = goodIndex
        self.gfx.dest.parentPositionCurve = targetBall
        self.gfx.dest.parentRotationCurve = targetBall
        targetScale = GetBoundingBox(targetBall, scale=1.0)
        self.gfx.dest.boundingSize = targetScale

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('EveStretch3: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        self.gfx.StartFiring(0.0)

    def Repeat(self, duration):
        if self.gfx is None:
            return
        shipBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        if targetBall is None:
            self.Stop(STOP_REASON_BALL_REMOVED)
        if shipBall is None:
            self.Stop(STOP_REASON_BALL_REMOVED)
        if self.gfx.destSpaceObject is None or self.gfx.sourceSpaceObject is None:
            self.Stop(STOP_REASON_BALL_REMOVED)
        self.SetDestCurve(targetBall)

    def UpdateGraphicInfo(self, newGraphicInfo):
        if self.gfx is None:
            return
        self.locatorSetName = newGraphicInfo.get('locatorSetName', 'damage')
        if self.locatorSetName is not None:
            positionOffset = self.FindGoodLocator()
            if positionOffset is not None:
                self.gfx.dest.positionOffset = positionOffset
        self.controllerTriggers = newGraphicInfo.get('controllerTrigger', None)
        if self.controllerTriggers is not None:
            for key, value in self.controllerTriggers.items():
                self.gfx.SetControllerVariable(key, value)
                if self.gfx.destSpaceObject is not None:
                    self.gfx.destSpaceObject.SetControllerVariable(key, value)
                if self.gfx.sourceSpaceObject is not None:
                    self.gfx.sourceSpaceObject.SetControllerVariable(key, value)

    def FindGoodLocator(self):
        locatorSets = getattr(self.gfx.destSpaceObject, 'locatorSets', None)
        if locatorSets:
            locator = locatorSets.FindByName(self.locatorSetName)
            if locator is None:
                self.locatorSetName = 'damage'
        targetModelWorldPos = self.gfx.sourceSpaceObject.modelWorldPosition
        goodIndex = self.gfx.destSpaceObject.GetGoodLocatorIndex(targetModelWorldPos, self.locatorSetName)
        if goodIndex != -1:
            return self.gfx.destSpaceObject.GetLocatorPositionFromSet(goodIndex, True, self.locatorSetName)
