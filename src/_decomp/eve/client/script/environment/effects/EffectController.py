#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\EffectController.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT, STOP_REASON_BALL_REMOVED
from tacticalNavigation.ballparkFunctions import AddClientBallLocal, RemoveClientBall
import blue
import trinity
import uthread
import logging
log = logging.getLogger(__name__)

class ControllerEffect(GenericEffect):
    targetControllerState = 'notSet'

    def Stop(self, reason = STOP_REASON_DEFAULT):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipBall.SetControllerVariable(self.targetControllerState, False)

    def Start(self, duration):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipBall.SetControllerVariable(self.targetControllerState, True)

    def Repeat(self, duration):
        pass


class SiegeMode(ControllerEffect):
    __guid__ = 'effects.SiegeMode'
    targetControllerState = 'InSiegeMode'


class AttackMode(ControllerEffect):
    __guid__ = 'effects.AttackMode'
    targetControllerState = 'InAttackingMode'


class ControllerTrigger(GenericEffect):
    __guid__ = 'effects.ControllerTrigger'
    controllerVariables = []

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(ControllerTrigger, self).__init__(trigger, effect, graphicFile)
        shipID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(shipID)
        self.triggers = None
        self.isLoaded = False
        self.model = self.ExtractModel(graphicFile, ball)
        if ball is not None:
            self.targetBallModel = ball.model
        self.ball = None
        self.lingerOnDeathTime = trigger.graphicInfo.get('deathTimer') or 0.0
        self.SetUpControllerVariableTriggers(trigger)

    def SetUpControllerVariableTriggers(self, trigger):
        if hasattr(trigger, 'controllerVariableTriggers') and trigger.controllerVariableTriggers is not None:
            self.triggers = trigger.controllerVariableTriggers.items()
        if trigger.graphicInfo is not None:
            for i, (name, value) in enumerate(self.triggers):
                if trigger.graphicInfo.get(name) is not None:
                    attributeOverride = trigger.graphicInfo.get(name)
                    self.triggers[i] = tuple([name, attributeOverride])

    def ExtractModel(self, graphicFile, targetBall):
        model = None
        if targetBall is not None and hasattr(targetBall, 'model'):
            if graphicFile is None:
                model = targetBall.model
                self.isLoaded = True
            else:
                model = self.RecycleOrLoad(self.graphicFile)
                if targetBall is None or targetBall.model is None or not hasattr(targetBall.model, 'worldPosition'):
                    return model
                self.ball = AddClientBallLocal(targetBall.model.worldPosition)
                model.translationCurve = targetBall
        return model

    def Start(self, duration):
        if self.model is None:
            return
        if not self.isLoaded:
            self.AddToScene(self.model)
        if hasattr(self.model, 'controllers'):
            secondsFromStart = self.timeFromStart / float(const.SEC)
            self.model.SetControllerVariable('elapsedTime', secondsFromStart)
            self.TriggerAttributes()
            self.model.StartControllers()

    def Stop(self, reason = STOP_REASON_DEFAULT):
        scene = self.fxSequencer.GetScene()
        if reason == STOP_REASON_BALL_REMOVED:
            if self.lingerOnDeathTime is not None:
                uthread.new(ControllerTrigger._DelayedCleanUp, self.lingerOnDeathTime, self.model, self.ball, scene)
        else:
            self._CleanUp(self.model, self.ball, scene)

    @staticmethod
    def _DelayedCleanUp(timeInSec, model, ball, scene):
        blue.synchro.SleepSim(timeInSec * 1000)
        ControllerTrigger._CleanUp(model, ball, scene)

    @staticmethod
    def _CleanUp(model, ball, scene):
        if scene is not None and model is not None:
            scene.objects.fremove(model)
        if ball is not None:
            RemoveClientBall(ball)

    def Repeat(self, duration):
        if hasattr(self.model, 'controllers'):
            self.TriggerAttributes()

    def TriggerAttributes(self):
        if not self.triggers or self.model is None:
            return
        for name, value in self.triggers:
            self.model.SetControllerVariable(name, float(value))
            if hasattr(self, 'targetBallModel'):
                if not self.isLoaded and self.targetBallModel is not None:
                    self.targetBallModel.SetControllerVariable(name, float(value))

    def UpdateGraphicInfo(self, newGraphicInfo):
        super(ControllerTrigger, self).UpdateGraphicInfo(newGraphicInfo)
        if newGraphicInfo is not None:
            for i, (name, value) in enumerate(self.triggers):
                if newGraphicInfo.get(name) is not None:
                    attributeOverride = newGraphicInfo.get(name)
                    self.triggers[i] = tuple([name, attributeOverride])

        self.TriggerAttributes()


class MultiEffectControllerTrigger(ControllerTrigger):
    __guid__ = 'effects.MultiEffectControllerTrigger'
    controllerVariables = []

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(MultiEffectControllerTrigger, self).__init__(trigger, effect, graphicFile)
        if trigger.shipID is not None:
            if hasattr(self.model, 'name'):
                shipID = str(trigger.shipID)
                if self.model.name is not None:
                    self.model.name = self.model.name + '_' + shipID
                elif graphicFile is not None:
                    self.model.name = graphicFile.split('.')[0].split('/')[-1] + '_' + shipID
        self.AssignMultiEffectParameters(trigger.graphicInfo)
        self.ConfigureModelRotationAndTranslationCurves()

    def ExtractModel(self, graphicFile, targetBall):
        if graphicFile is not None:
            model = self.RecycleOrLoad(self.graphicFile)
            if isinstance(model, trinity.EveMultiEffect):
                return model
            log.warning("file loaded is not a multiEffect: '%s'" % graphicFile)

    def AssignMultiEffectParameters(self, graphicInfo):
        MultiEffectParams = []
        if self.model is not None:
            for param in self.model.parameters:
                MultiEffectParams.append(param.name)

        for paramName in MultiEffectParams:
            targetId = graphicInfo.get(paramName)
            model = None
            if targetId is None:
                log.warning("Could not find GraphicInfo parameter for MultiEffect param '%s'" % paramName)
                continue
            ball = self.fxSequencer.GetBall(int(targetId))
            if ball is not None and hasattr(ball, 'model'):
                model = ball.model
            if model is None:
                log.warning("Could not find a model on ball to assign to MultiEffect param.  ballId: '%s'" % targetId)
                continue
            MEP = self.model.parameters.FindByName(paramName)
            if MEP is not None:
                MEP.object = model

    def ConfigureModelRotationAndTranslationCurves(self):
        if self.model is not None:
            for param in self.model.parameters:
                if param.object is not None:
                    if hasattr(param.object, 'modelRotationCurve') and param.object.modelRotationCurve is None:
                        rotationAdapter = trinity.Tr2RotationAdapter()
                        if rotationAdapter is not None:
                            param.object.modelRotationCurve = rotationAdapter
                    if hasattr(param.object, 'modelTranslationCurve') and param.object.modelTranslationCurve is None:
                        translationAdapter = trinity.Tr2CurveVector3()
                        if translationAdapter is not None:
                            param.object.modelTranslationCurve = translationAdapter
