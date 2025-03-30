#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\superWeapon.py
import random
import geo2
import blue
from dogma.const import attributeDamageDelayDuration
from eve.common.lib import appConst
import trinity
import uthread
import uthread2
import evetypes
import log
from eve.client.script.environment.effects.stretchEffect import StretchEffect
from eve.client.script.environment.effects.GenericEffect import GetBoundingBox, STOP_REASON_DEFAULT

def GetClosestLocatorIndex(sourceModel, targetModel, locatorSetName):
    targetModelWorldPos = targetModel.modelWorldPosition
    return sourceModel.GetCloseLocatorIndex(targetModelWorldPos, locatorSetName)


def GetSecondaryIndices(model, locatorSetName, mainIndex):
    locatorCount = model.GetLocatorCount(locatorSetName)
    return [ x for x in xrange(locatorCount) if x != mainIndex ]


def AmarrTitanSetup(superWeapon, effect):
    sourceBall = superWeapon.GetEffectShipBall()
    targetBall = superWeapon.GetEffectTargetBall()
    sourceModel = getattr(sourceBall, 'model', None)
    targetModel = getattr(targetBall, 'model', None)
    if sourceModel is None or targetModel is None:
        return False
    sideLocatorIndex = GetClosestLocatorIndex(sourceModel, targetModel, superWeapon.data['locatorSetName'])
    locatorSetNames = {0: 'doomsday_left_side',
     1: 'doomsday_center',
     2: 'doomsday_right_side'}
    if sideLocatorIndex == -1:
        return False
    locatorSetName = locatorSetNames[sideLocatorIndex]
    firingDirection = sideLocatorIndex - 1
    mainStretchLocatorIndex = GetClosestLocatorIndex(sourceModel, targetModel, locatorSetName)
    secondaryIndices = GetSecondaryIndices(sourceModel, locatorSetName, mainStretchLocatorIndex)
    if mainStretchLocatorIndex == -1:
        return False
    SetControllerVariable(sourceModel, 'FiringDirection', firingDirection)
    superWeapon.sourceLocation.locatorSetName = locatorSetName
    superWeapon.sourceLocation.locatorIndex = mainStretchLocatorIndex
    if len(secondaryIndices) >= 2:
        secondStretchEffect = superWeapon.RecycleOrLoad(superWeapon.secondaryGraphicFile)
        thirdStretchEffect = superWeapon.RecycleOrLoad(superWeapon.secondaryGraphicFile)
        if secondStretchEffect is None:
            log.LogError('secondaryGraphicFile not found: ' + str(superWeapon.secondaryGraphicFile))
            return False
        if thirdStretchEffect is None:
            log.LogError('secondaryGraphicFile not found: ' + str(superWeapon.secondaryGraphicFile))
            return False
        secondStretchEffect = superWeapon.CreateSourceSequencer(secondStretchEffect)
        thirdStretchEffect = superWeapon.CreateSourceSequencer(thirdStretchEffect)
        secondSourceLocation = CreateSourceLocation(superWeapon.startLocation, sourceBall, targetBall, secondaryIndices[0], locatorSetName)
        thirdSourceLocation = CreateSourceLocation(superWeapon.startLocation, sourceBall, targetBall, secondaryIndices[1], locatorSetName)
        secondStretchEffect.source.functions.append(secondSourceLocation)
        thirdStretchEffect.source.functions.append(thirdSourceLocation)
        superWeapon.additionalEffects.append(secondStretchEffect)
        superWeapon.additionalEffects.append(thirdStretchEffect)
        effect.stretchObject.scaling = ObjectScaleXY(list(effect.stretchObject.scaling), 0.5)
        effect.sourceObject.scaling = ObjectScaleXY(list(effect.sourceObject.scaling), 0.5)
    return True


def ObjectScaleXY(object, value):
    object[0] = value
    object[1] = value
    return object


def CreateSourceLocation(startLocation, sourceBall, targetBall, index, locatorSetName):
    sourceLocation = trinity.EveLocalPositionCurve(startLocation)
    sourceLocation.parent = sourceBall.model
    sourceLocation.locatorIndex = index
    sourceLocation.locatorSetName = locatorSetName
    return sourceLocation


def SetControllerVariable(model, variable, value):
    if model is not None:
        for c in model.effectChildren:
            if c.name == 'Amarr_Doomsday_Controller':
                c.SetControllerVariable(variable, value)


effectData = {'effects.SuperWeaponCaldari': {'count': 32,
                                'maxDelay': 2600,
                                'delayUntilShipHit': 10000},
 'effects.SuperWeaponMinmatar': {'count': 32,
                                 'maxDelay': 4000,
                                 'delayUntilShipHit': 1000,
                                 'delayBeforeEffect': 3000,
                                 'doomsday': True,
                                 'doomsdayFaction': 0},
 'effects.SuperWeaponAmarr': {'count': 1,
                              'maxDelay': 0,
                              'delayUntilShipHit': 2200,
                              'delayBeforeEffect': 6000,
                              'startLocation': trinity.EveLocalPositionBehavior.nearestFiringLocator,
                              'locatorSetName': 'doomsday_firing',
                              'additionalSetup': AmarrTitanSetup,
                              'doomsday': True},
 'effects.SuperWeaponGallente': {'count': 1,
                                 'maxDelay': 0,
                                 'delayUntilShipHit': 4833,
                                 'startLocation': trinity.EveLocalPositionBehavior.nearestBounds,
                                 'doomsday': True,
                                 'doomsdayFaction': 1},
 'effects.TurboLaser': {'count': 1,
                        'maxDelay': 0,
                        'delayUntilShipHit': 2500,
                        'impactMassFraction': 0.5,
                        'startLocation': trinity.EveLocalPositionBehavior.nearestBounds,
                        'destLocation': trinity.EveLocalPositionBehavior.nearestBounds},
 'effects.SuperWeaponLanceAmarr': {'count': 1,
                                   'maxDelay': 0,
                                   'delayUntilShipHit': 2200,
                                   'delayBeforeEffect': 6000,
                                   'startLocation': trinity.EveLocalPositionBehavior.nearestBounds,
                                   'destLocation': trinity.EveLocalPositionBehavior.nearestBounds},
 'effects.SuperWeaponLanceCaldari': {'count': 1,
                                     'maxDelay': 0,
                                     'delayUntilShipHit': 2200,
                                     'delayBeforeEffect': 6000,
                                     'startLocation': trinity.EveLocalPositionBehavior.nearestBounds,
                                     'destLocation': trinity.EveLocalPositionBehavior.nearestBounds},
 'effects.SuperWeaponLanceGallente': {'count': 1,
                                      'maxDelay': 0,
                                      'delayUntilShipHit': 2200,
                                      'delayBeforeEffect': 6000,
                                      'startLocation': trinity.EveLocalPositionBehavior.nearestBounds,
                                      'destLocation': trinity.EveLocalPositionBehavior.nearestBounds},
 'effects.SuperWeaponLanceMinmatar': {'count': 1,
                                      'maxDelay': 0,
                                      'delayUntilShipHit': 2200,
                                      'delayBeforeEffect': 6000,
                                      'startLocation': trinity.EveLocalPositionBehavior.nearestBounds,
                                      'destLocation': trinity.EveLocalPositionBehavior.nearestBounds}}

class SuperWeapon(StretchEffect):

    def __init__(self, trigger, effect = None, graphicFile = None):
        StretchEffect.__init__(self, trigger, effect, graphicFile)
        self.data = effectData[trigger.guid]
        self.isDoomsday = self.data.get('doomsday', False)
        self.doomsdayFaction = self.data.get('doomsdayFaction', 1)
        self.projectileCount = self.data['count']
        self.maxDelay = self.data['maxDelay']
        self.delayUntilShipHit = self.data['delayUntilShipHit']
        self.delayBeforeEffect = self.data.get('delayBeforeEffect', 0)
        try:
            self.delayUntilDamageApplied = self.fxSequencer.GetTypeAttribute(trigger.moduleTypeID, attributeDamageDelayDuration)
        except evetypes.TypeNotFoundException:
            log.LogError("Module type not found: '%s'" % trigger.moduleTypeID)
            self.delayUntilDamageApplied = 9000

        self.impactMassFraction = self.data.get('impactMassFraction', 1.0)
        self.startLocation = self.data.get('startLocation', trinity.EveLocalPositionBehavior.damageLocator)
        self.destLocation = self.data.get('destLocation', trinity.EveLocalPositionBehavior.damageLocator)
        self.additionalSetup = self.data.get('additionalSetup', None)
        self.sourceLocation = trinity.EveLocalPositionCurve(self.startLocation)
        self.additionalEffects = []

    def CreateSourceSequencer(self, effect):
        effect.source = trinity.TriVectorSequencer()
        effect.source.operator = 1
        return effect

    def CreateDestSequencer(self, effect):
        effect.dest = trinity.TriVectorSequencer()
        effect.dest.operator = 1
        return effect

    def IsTargetStillValid(self):
        targetBall = self.GetEffectTargetBall()
        return targetBall is not None and targetBall.model is not None

    def Prepare(self):
        pass

    def StartIndividual(self, sourceBall, targetBall, rotation, direction):
        effect = self.RecycleOrLoad(self.graphicFile)
        if effect is None:
            log.LogError('effect not found: ' + str(self.graphicFile))
            return
        effect = self.CreateSourceSequencer(effect)
        self.sourceLocation.parent = sourceBall.model
        self.sourceLocation.parentPositionCurve = sourceBall
        self.sourceLocation.parentRotationCurve = sourceBall
        self.sourceLocation.alignPositionCurve = targetBall
        sourceScale = GetBoundingBox(sourceBall, scale=1.2)
        self.sourceLocation.boundingSize = sourceScale
        successfulAdditionalSetup = False
        if self.additionalSetup is not None:
            successfulAdditionalSetup = self.additionalSetup(self, effect)
        effect.source.functions.append(self.sourceLocation)
        sourceOffsetCurve = trinity.Tr2CurveVector3()
        if self.projectileCount > 1:
            offset = (random.gauss(0.0, 1000.0), random.gauss(0.0, 1000.0), random.gauss(0.0, 700.0) - 2000.0)
        else:
            offset = (0, 0, -self.sourceOffset)
        offset = geo2.QuaternionTransformVector(rotation, offset)
        sourceOffsetCurve.AddKey(0, offset)
        effect.source.functions.append(sourceOffsetCurve)
        effect = self.CreateDestSequencer(effect)
        destLocation = trinity.EveLocalPositionCurve(self.destLocation)
        destLocation.parent = targetBall.model
        destLocation.alignPositionCurve = sourceBall
        destLocation.parentPositionCurve = targetBall
        destLocation.parentRotationCurve = targetBall
        targetScale = GetBoundingBox(targetBall, scale=1.2)
        destLocation.boundingSize = targetScale
        effect.dest.functions.append(destLocation)
        for additionalEffect in self.additionalEffects or []:
            additionalEffect = self.CreateDestSequencer(additionalEffect)
            additionalEffect.dest.functions.append(destLocation)

        destOffsetCurve = trinity.Tr2CurveVector3()
        if self.projectileCount > 1:
            offset = (random.gauss(0.0, 1000.0), random.gauss(0.0, 1000.0), random.gauss(0.0, 700.0) + 500.0)
        else:
            offset = (0, 0, self.destinationOffset)
        offset = geo2.QuaternionTransformVector(rotation, offset)
        destOffsetCurve.AddKey(0, offset)
        effect.dest.functions.append(destOffsetCurve)
        if successfulAdditionalSetup or self.additionalSetup is None and self.isDoomsday:
            if sourceBall.model is not None and hasattr(sourceBall.model, 'SetControllerVariable'):
                sourceBall.model.SetControllerVariable('InDoomsdayFiringMode', 1.0)
                sourceBall.model.SetControllerVariable('doomsdayFaction', self.doomsdayFaction)
        blue.synchro.SleepSim(self.delayBeforeEffect)
        delay = random.random() * self.maxDelay
        blue.synchro.SleepSim(delay)
        self.AddToScene(effect)
        for additionalEffect in self.additionalEffects or []:
            self.AddToScene(additionalEffect)
            additionalEffect.Start()

        effect.Start()
        blue.synchro.SleepSim(self.delayUntilShipHit)
        if self.IsTargetStillValid() and self.delayUntilDamageApplied is not None:
            impactMass = targetBall.mass * targetBall.model.boundingSphereRadius * self.impactMassFraction / (250.0 * self.projectileCount)
            targetShip = self.GetEffectTargetBall()
            targetShip.ApplyTorqueAtPosition(effect.dest.value, direction, impactMass)
            impactDirection = geo2.Vec3Scale(direction, -1.0)
            if self.projectileCount == 1:
                impactScale = 16.0 * self.impactMassFraction
            else:
                impactScale = 8.0 * self.impactMassFraction
            damageDuration = self.delayUntilDamageApplied - self.delayUntilShipHit + 500
            targetBall.model.CreateImpact(destLocation.damageLocatorIndex, impactDirection, damageDuration * 0.001, impactScale)
            blue.synchro.SleepSim(damageDuration)
            if self.projectileCount == 1 and self.IsTargetStillValid() and self.delayUntilDamageApplied is not None:
                targetBall.model.CreateImpact(destLocation.damageLocatorIndex, impactDirection, 3, impactScale)
        sleepTime = effect.curveSets[0].GetMaxCurveDuration()
        blue.synchro.SleepSim(sleepTime * 1000)
        self.RemoveFromScene(effect)
        for additionalEffect in self.additionalEffects or []:
            self.RemoveFromScene(additionalEffect)

        if successfulAdditionalSetup or self.additionalSetup is None and self.isDoomsday:
            if sourceBall.model is not None and hasattr(sourceBall.model, 'SetControllerVariable'):
                sourceBall.model.SetControllerVariable('InDoomsdayFiringMode', 0.0)
        self.sourceLocation.parent = None
        self.sourceLocation.alignPositionCurve = None
        destLocation.parent = None
        destLocation.alignPositionCurve = None

    def Start(self, duration):
        sourceBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        sourcePos = sourceBall.GetVectorAt(blue.os.GetSimTime())
        sourcePos = (sourcePos.x, sourcePos.y, sourcePos.z)
        targetPos = targetBall.GetVectorAt(blue.os.GetSimTime())
        targetPos = (targetPos.x, targetPos.y, targetPos.z)
        direction = geo2.Vec3Direction(sourcePos, targetPos)
        rotation = geo2.QuaternionRotationArc((0, 0, 1), direction)
        direction = geo2.Vec3Scale(direction, -1.0)
        for x in range(self.projectileCount):
            uthread.new(self.StartIndividual, sourceBall, targetBall, rotation, direction)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        pass

    def ScaleEffectAudioEmitters(self):
        pass


class SlashWeapon(StretchEffect):

    def __init__(self, trigger, *args):
        StretchEffect.__init__(self, trigger, *args)
        self.startTargetOffset = trigger.graphicInfo.startTargetOffset
        self.endTargetOffset = trigger.graphicInfo.endTargetOffset
        self.durationSeconds = trigger.graphicInfo.duration / 1000.0

    def Prepare(self):
        shipBall = self.GetEffectShipBall()
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if self.gfx is None:
            log.LogError('effect not found: ' + str(self.graphicFile))
            return
        self.gfx.dest = trinity.EveRemotePositionCurve()
        self.gfx.dest.startPositionCurve = shipBall
        self.gfx.dest.offsetDir1 = self.startTargetOffset
        self.gfx.dest.offsetDir2 = self.endTargetOffset
        self.gfx.dest.sweepTime = self.durationSeconds
        sourceBehavior = trinity.EveLocalPositionBehavior.nearestBounds
        self.gfx.source = trinity.EveLocalPositionCurve(sourceBehavior)
        self.gfx.source.offset = self.sourceOffset
        self.gfx.source.parentPositionCurve = shipBall
        self.gfx.source.parentRotationCurve = shipBall
        self.gfx.source.alignPositionCurve = self.gfx.dest
        self.gfx.source.boundingSize = GetBoundingBox(shipBall, scale=1.2)
        self.AddToScene(self.gfx)

    def Start(self, duration):
        StretchEffect.Start(self, duration)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            return
        self.RemoveFromScene(self.gfx)
        self.gfx.source.parentPositionCurve = None
        self.gfx.source.parentRotationCurve = None
        self.gfx.source.alignPositionCurve = None
        self.gfx.dest.startPositionCurve = None
        self.gfx = None
        self.gfxModel = None


class DirectionalWeapon(SlashWeapon):

    def __init__(self, trigger, *args):
        StretchEffect.__init__(self, trigger, *args)
        self.startTargetOffset = trigger.graphicInfo.targetOffset
        self.endTargetOffset = trigger.graphicInfo.targetOffset
        self.durationSeconds = trigger.graphicInfo.duration / 1000.0
