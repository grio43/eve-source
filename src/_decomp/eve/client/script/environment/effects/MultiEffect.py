#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\MultiEffect.py
import blue
from carbon.common.lib.const import MSEC
from eve.client.script.environment.effects.GenericEffect import GenericEffect
from eve.client.script.environment.effects.GenericEffect import STOP_REASON_DEFAULT
import logging
from fsdBuiltData.client.effectSequences import GetSequence, GetStops
from evegraphics.graphicEffects.effectPhasePlayer import PhasePlayer, GetStepsToPlayForPhase
log = logging.getLogger(__name__)

def GetStepNames(sequenceName, phaseName):
    return [ s.name for s in GetStepsToPlayForPhase(sequenceName, phaseName) ]


def ShouldPhaseBeStoppedOnNewPhase(sequenceName, oldPhaseName, newPhaseName):
    phases = GetSequence(sequenceName)
    oldPhaseIndex = -1
    newPhaseIndex = -1
    index = 0
    for phase in phases:
        if phase.name == oldPhaseName:
            oldPhaseIndex = index
        if phase.name == newPhaseName:
            newPhaseIndex = index
        if oldPhaseIndex >= 0 and newPhaseIndex >= 0:
            break
        index += 1

    if oldPhaseIndex > newPhaseIndex:
        return True
    steps = GetStepNames(sequenceName, oldPhaseName)
    for phase in phases:
        phaseStops = GetStops(phase, [])
        if any([ s in phaseStops for s in steps ]):
            return True
        if phase.name == newPhaseName:
            return False

    return False


class EvePhasePlayer(PhasePlayer):

    def GetPosition(self, objectID):
        p = sm.GetService('michelle').GetBall(objectID).GetVectorAt(blue.os.GetSimTime())
        return (p.x, p.y, p.z)

    def MoonMiningCreateCrater(self, step, timeElapsed, objectID):
        targetID = self.GetStepTargetID(step)
        target = sm.GetService('michelle').GetBall(targetID)
        sourceID = self.GetStepSourceID(step)
        target.SpawnImpactCrater(self.GetDirection(sourceID, targetID), self.GetScaling(step), timeElapsed / 1000.0)

    def GetTurretSet(self, sourceID, turretSetID):
        ball = sm.GetService('michelle').GetBall(sourceID)
        if turretSetID not in ball.modules:
            ball.UnfitHardpoints()
            ball.FitHardpoints(blocking=True)
        ts = ball.modules.get(turretSetID, None)
        if ts is not None:
            if len(ts.turretSets) > 0:
                return ts.turretSets[0]
        log.warning("Could not find turretset '%s' for source '%s'" % (turretSetID, sourceID))

    def GetTrinityObject(self, identifier):
        ball = sm.GetService('michelle').GetBall(identifier)
        if ball is not None:
            return ball.GetModel()
        log.warning("Could not find ball '%s'" % identifier)

    def GetTranslationCurve(self, identifier):
        ball = sm.GetService('michelle').GetBall(identifier)
        if ball is None:
            log.warning("Could not find ball '%s'" % identifier)
            return
        return ball

    def GetRotationCurve(self, identifier):
        ball = sm.GetService('michelle').GetBall(identifier)
        if ball is None:
            log.warning("Could not find ball '%s'" % identifier)
            return
        model = ball.GetModel()
        if model is None:
            log.warning("Could not find model '%s'" % identifier)
            return
        return model.rotationCurve


class MultiEffect(GenericEffect):
    __guid__ = 'effects.MultiEffect'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(MultiEffect, self).__init__(trigger, effect, graphicFile)
        graphicInfo = trigger.get('graphicInfo', {})
        self.sequence = graphicInfo.get('sequence')
        phase = graphicInfo.get('phase', None)
        currentTime = blue.os.GetSimTime()
        self.timeFromStart = currentTime - graphicInfo.get('effectStarted', currentTime)
        self.timeFromStart /= MSEC
        if self.sequence is None:
            raise RuntimeError('No sequence was given... not sure what I should do')
        if phase is None:
            raise RuntimeError('No phase was given... not sure what I should do')
        self.triggerIds = {}
        graphicInfo = trigger.get('graphicInfo')
        if graphicInfo is not None:
            for ID in graphicInfo['triggers']:
                self.triggerIds[ID] = trigger.get(ID, graphicInfo.get(ID))

        self.phasePlayers = [EvePhasePlayer(self.sequence, phase, self.triggerIds)]

    def Start(self, duration):
        self.phasePlayers[0].Start(self.fxSequencer.GetScene(), timeOffset=self.timeFromStart)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        for phasePlayer in self.phasePlayers:
            phasePlayer.Stop()

        self.phasePlayers = []

    def UpdateGraphicInfo(self, newGraphicInfo):
        newPhase = newGraphicInfo.get('phase', None)
        if newPhase is not None:
            currentTime = blue.os.GetSimTime()
            self.timeFromStart = currentTime - newGraphicInfo.get('effectStarted', currentTime)
            self.timeFromStart /= MSEC
            phasePlayersToStop = []
            for phasePlayer in self.phasePlayers:
                if ShouldPhaseBeStoppedOnNewPhase(self.sequence, phasePlayer.phaseName, newPhase):
                    phasePlayersToStop.append(phasePlayer)

            for phasePlayer in phasePlayersToStop:
                p = self.phasePlayers.pop(self.phasePlayers.index(phasePlayer))
                p.Stop()

            if newPhase not in [ p.phaseName for p in self.phasePlayers ]:
                newPhasePlayer = EvePhasePlayer(self.sequence, newPhase, self.triggerIds)
                self.phasePlayers.append(newPhasePlayer)
                newPhasePlayer.Start(self.fxSequencer.GetScene(), self.timeFromStart)
