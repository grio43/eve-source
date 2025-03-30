#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\ProximityEffect.py
import logging
from eve.client.script.environment.effects.GenericEffect import GenericEffect
import eve.client.script.environment.spaceObject.ship as ship
import trinity
import os.path as path

class ProximityEffect(GenericEffect):
    __guid__ = 'effects.ProximityEffect'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(ProximityEffect, self).__init__(trigger, effect, graphicFile)
        self.log = logging.getLogger(__name__)
        self.log.info('ProximityEffect: Initialize')
        self.shipBall = None
        self.targetMap = dict()
        fileName = path.basename(self.graphicFile)
        self.fxName = path.splitext(fileName)[0].lower()

    def Prepare(self):
        self.log.info('ProximityEffect::Prepare')
        self.DoPrepare()

    def DoPrepare(self):
        self.shipBall = self.GetEffectShipBall()
        newTargets = set(self._GetTargetBalls(self.shipBall))
        for ball in newTargets:
            if ball.model is not None:
                self._AddEffectToTarget(ball)

        self.log.info('ProximityEffect::DoPrepare() added effect to targets')

    def _GetTargetBalls(self, sourceBall):
        ballpark = sm.GetService('michelle').GetBallpark()
        targetBalls = ballpark.GetBallsInRange(sourceBall.id, self.graphicInfo['radius'])
        targetIDs = set([ x for x in targetBalls if x > 0 ])
        targetBalls = []
        for targetID in targetIDs:
            targetBall = sm.GetService('michelle').GetBall(targetID)
            targetBalls.append(targetBall)

        return targetBalls

    def _AddEffectToTarget(self, targetBall):
        if not hasattr(targetBall, 'model') or targetBall.model is None:
            return False
        if not isinstance(targetBall, ship.Ship):
            return False
        if len(targetBall.model.effectChildren) > 0:
            for child in targetBall.model.effectChildren:
                if child.name.lower() == self.fxName:
                    return False

        try:
            effect = trinity.Load(self.graphicFile)
            self.targetMap[targetBall] = effect
            targetBall.AddChildEffect(effect)
            return True
        except AttributeError:
            return False

    def Stop(self, reason = None):
        self.log.info('ProximityEffect: Stop')
        try:
            self.shipBall.model.SetControllerVariable('DisplayMe', 0.0)
        except AttributeError:
            pass

        for each in self.targetMap.iteritems():
            targetBall = each[0]
            effect = each[1]
            targetBall.RemoveChildEffect(effect)

        self.shipBall = None
        self.targetMap = None

    def Repeat(self, duration):
        self.log.info('ProximityEffect: Repeat')
        targetsInRange = set(self._GetTargetBalls(self.shipBall))
        for targetBall in targetsInRange:
            self._AddEffectToTarget(targetBall)

        targetsOutsideRange = [ x for x in self.targetMap.keys() if x not in targetsInRange ]
        self.CleanupShipEffects(targetsOutsideRange)
        self.UpdateControllers()

    def UpdateControllers(self):
        self.shipBall.model.SetControllerVariable('visual_active', float(bool(self.targetMap)))

    def CleanupShipEffects(self, targets):
        for target in targets:
            effect = self.targetMap[target]
            target.RemoveChildEffect(effect)

        for target in targets:
            self.targetMap.pop(target)
