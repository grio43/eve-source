#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\graphicEffects\effectPhasePlayer.py
import blue
import geo2
import trinity
import uthread
from carbon.common.lib.const import MSEC
from fsdBuiltData.client.effectSequences import GetStepGraphicFile, GetStepStepsToStop, GetStepScaling, GetStepSource, GetStops, GetSequence, GetStepTarget, GetStepFunctions, GetStepFunctionTarget
import logging
import evegraphics.settings as gfxSettings
log = logging.getLogger(__name__)
EFFECT_START_TIME_DELTA_MS = 3000

def GetStepsToPlayForPhase(sequenceName, phaseName):

    def SortStepsByStartTime(steps):
        return sorted(steps, key=lambda x: x.startTime)

    previousPhaseSteps = []
    steps = []
    stops = []
    for phase in GetSequence(sequenceName):
        stops.extend(GetStops(phase, []))
        if phase.name != phaseName:
            previousPhaseSteps.extend(phase.steps)
        else:
            steps = phase.steps
            break

    stepsToPlay = SortStepsByStartTime(steps)
    for step in reversed(SortStepsByStartTime(previousPhaseSteps)):
        if step.name not in stops and step.looped:
            stepsToPlay.insert(0, step)

    return stepsToPlay


class PhasePlayer(object):

    def __init__(self, sequenceName, phaseName, objectIDs):
        log.info("Setting up phase '%s' in sequence '%s'" % (phaseName, sequenceName))
        self.sequenceName = sequenceName
        self.phaseName = phaseName
        self.processedSteps = []
        self.cleanupFunctions = {}
        self.objectIDs = objectIDs
        self.unprocessedSteps = GetStepsToPlayForPhase(self.sequenceName, self.phaseName)
        self.stepProcessingThread = None
        self.startTimeInMs = 0
        self.active = True
        self.effects = {}
        for step in self.unprocessedSteps:
            graphicFile = GetStepGraphicFile(step)
            if graphicFile:
                log.info("Preloading '%s'" % graphicFile)
                self.effects[step.name] = self._LoadGraphicFile(graphicFile)

    def Start(self, scene, timeOffset = 0):
        log.info("Starting phase '%s' with timeoffset %s" % (self.phaseName, timeOffset))
        self.active = True
        if timeOffset < EFFECT_START_TIME_DELTA_MS:
            timeOffset = 0
        stepsToThrowAway = []
        for step in self.unprocessedSteps:
            stops = GetStepStepsToStop(step)
            if stops and step.startTime < timeOffset:
                stepsToThrowAway.extend(stops)

        if len(stepsToThrowAway) > 0:
            log.info('Trowing away these steps due to them being obsolete because of time %s' % stepsToThrowAway)
        self.unprocessedSteps = [ step for step in self.unprocessedSteps if step.name not in stepsToThrowAway ]
        self.effects = {stepName:effect for stepName, effect in self.effects.iteritems() if stepName not in stepsToThrowAway}
        self.startTimeInMs = blue.os.GetSimTime() / MSEC - timeOffset
        self.stepProcessingThread = uthread.new(self._ProcessSteps, scene)

    def Stop(self):
        log.info("Stopping phase '%s'" % self.phaseName)
        self.active = False
        if self.stepProcessingThread is not None:
            self.stepProcessingThread.kill()
        for cleanUpFunction, arguments in self.cleanupFunctions.values():
            cleanUpFunction(*arguments)

        self.cleanupFunctions = {}

    def Reset(self):
        log.info("Resetting phase '%s'" % self.phaseName)
        self.Stop()
        self.unprocessedSteps = GetStepsToPlayForPhase(self.sequenceName, self.phaseName)
        self.processedSteps = []

    def _GetElapsedTimeInMilliseconds(self):
        return blue.os.GetSimTime() / MSEC - self.startTimeInMs

    def _GetNextWakeTimeInMilliseconds(self):
        if len(self.unprocessedSteps) == 0:
            return 0
        nextStartTime = self.unprocessedSteps[0].startTime - self._GetElapsedTimeInMilliseconds()
        return nextStartTime

    def wait(self, ms):
        log.info('Waiting for %s ms' % ms)
        blue.synchro.SleepSim(ms)

    def _ProcessSteps(self, scene):
        while len(self.unprocessedSteps) > 0 and self.active:
            try:
                self.wait(self._GetNextWakeTimeInMilliseconds())
                if not self.active:
                    return
                currentStep = self.unprocessedSteps[0]
                self.unprocessedSteps.remove(currentStep)
                self.RemoveStepsForCurrentStep(currentStep)
                self._ProcessSingleStep(currentStep, self._GetElapsedTimeInMilliseconds(), scene)
                self.processedSteps.append(currentStep)
            except Exception:
                log.exception('Could not process step')

        self.active = False

    def RemoveStepsForCurrentStep(self, currentStep):
        for stepToRemove in GetStepStepsToStop(currentStep):
            if stepToRemove in self.cleanupFunctions:
                cleanUpFunction, cleanUpArgs = self.cleanupFunctions[stepToRemove]
                cleanUpFunction(*cleanUpArgs)
                del self.cleanupFunctions[stepToRemove]

    def _LoadGraphicFile(self, filePath):
        return blue.resMan.LoadObject(filePath)

    def GetScaling(self, step):
        scaling = GetStepScaling(step)
        if not scaling:
            return
        parent = self.GetTrinityObject(self.objectIDs[scaling.parent])
        if parent is None:
            log.error('Could not find a %s object' % scaling.parent)
            return 1
        sourceValue = getattr(parent, scaling.sourceValue, None)
        if sourceValue is None:
            log.error('Parent has no attribte %s' % scaling.sourceValue)
            return 1
        return sourceValue * scaling.amount

    def GetStepTargetID(self, step):
        return self.objectIDs.get(GetStepTarget(step))

    def GetStepSourceID(self, step):
        return self.objectIDs.get(GetStepSource(step))

    def _ProcessSingleStep(self, step, elapsedTime, scene):
        elapsedTime -= step.startTime
        log.info("Processing phase '%s' step '%s' with %s ms elapsed" % (self.phaseName, step.name, elapsedTime))
        effect = self.effects.get(step.name)
        if effect:
            if isinstance(effect, trinity.EveTurretFiringFX):
                self._StartFiringEffect(step.name, effect, GetStepSource(step), GetStepTarget(step), elapsedTime, step.looped)
            elif isinstance(effect, trinity.EveTransform):
                self._StartEveTransformEffect(step.name, effect, GetStepSource(step), elapsedTime, self.GetScaling(step))
            elif isinstance(effect, trinity.EveRootTransform):
                self._StartEveRootTransformEffect(step.name, effect, GetStepSource(step), elapsedTime, self.GetScaling(step), scene)
            else:
                log.warn("Could not handle effect of type '%s'", type(effect))
        for function in GetStepFunctions(step):
            functionAttr = getattr(self, function.name)
            if functionAttr:
                obj = GetStepFunctionTarget(function)
                if obj is not None:
                    obj = self.objectIDs[obj]
                functionAttr(step, elapsedTime, obj)
            else:
                log.warn("Could not find function '%s'", function)

    def _StartFiringEffect(self, stepName, effect, sourceTurretSetID, targetID, elapsedTime, looped = False):
        if abs(elapsedTime) > EFFECT_START_TIME_DELTA_MS and not looped:
            log.info('Single playing firing effect not played, elapsed time is %s ms' % elapsedTime)
            return
        if not gfxSettings.Get(gfxSettings.UI_TURRETS_ENABLED):
            log.info('TurretFx not played due to turrets not being enabled')
            return
        sourceID = 'shipID'
        if sourceID not in self.objectIDs:
            log.info('TurretFx not played due to missing ship sourceID')
            return
        sourceID = self.objectIDs[sourceID]
        turretSetID = self.objectIDs[sourceTurretSetID]
        targetObjectID = self.objectIDs[targetID]
        sourceTurretSet = self.GetTurretSet(sourceID, turretSetID)
        sourceTurretSet.firingEffect = effect
        sourceTurretSet.targetObject = self.GetTrinityObject(targetObjectID)
        sourceTurretSet.EnterStateFiring()
        self.cleanupFunctions[stepName] = (self._StopFiringEffect, [sourceID, turretSetID])

    def _StartEveTransformEffect(self, stepName, effect, targetID, elapsedTime, scale):
        curveSets = effect.Find('trinity.TriCurveSet')
        maxCurveDuration = 0
        elapsedTime = float(elapsedTime) / 1000.0
        for curveSet in curveSets:
            maxCurveDuration = max(curveSet.GetMaxCurveDuration(), maxCurveDuration)

        if maxCurveDuration <= elapsedTime:
            return
        if scale is not None:
            effect.scaling = (scale,) * 3
        targetID = self.objectIDs[targetID]
        target = self.GetTrinityObject(targetID)
        target.children.append(effect)
        self.cleanupFunctions[stepName] = (self._StopEveTransformEffect, [effect, targetID])

    def _StartEveRootTransformEffect(self, stepName, effect, targetID, elapsedTime, scale, scene):
        curveSets = effect.Find('trinity.TriCurveSet')
        maxCurveDuration = 0
        elapsedTime = float(elapsedTime) / 1000.0
        for curveSet in curveSets:
            maxCurveDuration = max(curveSet.GetMaxCurveDuration(), maxCurveDuration)

        if maxCurveDuration <= elapsedTime:
            return
        if scale is not None:
            effect.scaling = (scale,) * 3
        targetID = self.objectIDs[targetID]
        effect.translationCurve = self.GetTranslationCurve(targetID)
        effect.rotationCurve = self.GetRotationCurve(targetID)
        for curveSet in curveSets:
            curveSet.PlayFrom(elapsedTime)

        scene.objects.append(effect)
        self.cleanupFunctions[stepName] = (self._StopEveRootTransformEffect, [effect, scene])

    def _StopFiringEffect(self, sourceID, sourceTurretSetID):
        sourceTurretSet = self.GetTurretSet(sourceID, sourceTurretSetID)
        if sourceTurretSet is None:
            return
        sourceTurretSet.EnterStateTargeting()
        sourceTurretSet.firingEffect = None

    def _StopEveTransformEffect(self, effect, targetID):
        target = self.GetTrinityObject(targetID)
        if target and effect:
            index = target.children.index(effect)
            if index > -1:
                target.children.remove(effect)

    def _StopEveRootTransformEffect(self, effect, scene):
        scene.objects.fremove(effect)

    def _StopEvePinEffect(self, effect, targetID):
        target = self.GetTrinityObject(targetID)
        if target and effect:
            index = target.highDetail.children.index(effect)
            if index > -1:
                target.highDetail.children.remove(effect)

    def GetTrinityObject(self, identifier):
        raise NotImplementedError()

    def GetTranslationCurve(self, identifier):
        raise NotImplementedError()

    def GetRotationCurve(self, identifier):
        raise NotImplementedError()

    def CallFunction(self, functionToCall, step, timeElapsed):
        raise NotImplementedError()

    def GetTurretSet(self, sourceID, turretSetID):
        raise NotImplementedError()

    def GetPosition(self, objectID):
        raise NotImplementedError()

    def GetDirection(self, objectID1, objectID2):
        direction = geo2.Vec3Direction(self.GetPosition(objectID1), self.GetPosition(objectID2))
        return direction[0:3]

    def MakeVisible(self, step, elapsedTime, objectID):
        self.GetTrinityObject(objectID).display = True

    def MakeInvisible(self, step, elapsedTime, objectID):
        self.GetTrinityObject(objectID).display = False
