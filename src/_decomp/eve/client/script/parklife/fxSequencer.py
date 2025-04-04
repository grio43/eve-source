#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\fxSequencer.py
import sys
import blue
import blue.heapq as heapq
import log
import telemetry
import evegraphics.settings as gfxsettings
import locks
import uthread
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.util.commonutils import IsFullLogging
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_BALL_REMOVED, STOP_REASON_DEFAULT
from eve.client.script.environment.effects.Repository import GetClassification
from eve.client.script.environment.effects.effectConsts import FX_MERGE_GUID, FX_MERGE_MODULE, FX_MERGE_SHIP, FX_MERGE_TARGET
from eve.client.script.environment.effects.shipRenderEffect import ShipRenderEffect
from eve.client.script.environment.spaceObject.playerOwnedStructure import PlayerOwnedStructure
from eveexceptions import ExceptionEater
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
from fsdBuiltData.client.effects import GetEffectGuids
from destructionEffect import destructionType as destructionEffectType
from fsdBuiltData.client.travelEffects import IsTravelEffect
SECOND = 10000000L
FX_TURRET_EFFECT_GUIDS = ['effects.Laser',
 'effects.ProjectileFiredForEntities',
 'effects.ProjectileFired',
 'effects.HybridFired',
 'effects.TractorBeam',
 'effects.Salvaging',
 'effects.TriglavianBeam']
FX_PROTECTED_EFFECT_GUIDS = ['effects.GateActivity',
 'effects.WormholeActivity',
 'effects.JumpIn',
 'effects.JumpOut',
 'effects.JumpOutWormhole',
 'effects.JumpOutAbyssal',
 'effects.JumpOutAbyssalBetween',
 'effects.JumpBridgeIn',
 'effects.JumpBridgeOut',
 'effects.Warping',
 'effects.Cloaking',
 'effects.Uncloak',
 'effects.Cloak',
 'effects.CloakNoAmim',
 'effects.CloakRegardless',
 'effects.StructureOffline',
 'effects.StructureOnlined',
 'effects.AnchorDrop',
 'effects.AnchorLift',
 'effects.SiegeMode',
 'effects.TriageMode',
 'effects.WarpDisruptFieldGenerating',
 'effects.WarpScramble',
 'effects.Tethering',
 'effects.StellarHarvester']
FX_LONG_ONESHOT_GUIDS = ['effects.SuperWeaponAmarr',
 'effects.SuperWeaponCaldari',
 'effects.SuperWeaponGallente',
 'effects.SuperWeaponMinmatar']

class Trigger(utillib.KeyVal):

    def __le__(self, other):
        return self.stamp <= other.stamp

    def __eq__(self, other):
        return self.shipID == other.shipID and self.moduleID == other.moduleID and self.targetID == other.targetID and self.guid == other.guid


class Activation():

    def __init__(self, broker):
        self.triggers = []
        self.effect = None
        self.guid = None
        self.stamp = -1
        self.duration = -1
        self.broker = broker
        self.key = None
        self.isOn = False
        self.balls = set()
        self.isZombie = False

    def __le__(self, other):
        return self.stamp <= other.stamp

    def Zombify(self):
        self.isZombie = True
        self.triggers = []
        self.balls = set()
        self.broker = None

    def TriggerAlreadyExists(self, trigger):
        for t in self.triggers:
            if trigger.moduleID == t.moduleID:
                return True

        return False

    @telemetry.ZONE_METHOD
    def AddTrigger(self, trigger):
        if self.TriggerAlreadyExists(trigger):
            return
        heapq.heappush(self.triggers, trigger)
        stampUpdated = self.UpdateRepeatTime()
        if self.effect is None:
            try:
                self.effect = self.GetEffectFromGuid(trigger)
            except:
                self.effect = GenericEffect(trigger)
                log.LogException()
                sys.exc_clear()

            self.guid = trigger.guid
            self.balls = set(self.effect.GetBalls())
            self.PrepareAndStart()
            self.isOn = True
        else:
            self.balls.add(trigger.shipID)
            self.balls.add(trigger.targetID)
        return stampUpdated

    @telemetry.ZONE_METHOD
    def PrepareAndStart(self):
        try:
            self.effect.Prepare()
            self.effect.Start(self.duration)
        except:
            log.LogException()
            sys.exc_clear()

    @telemetry.ZONE_METHOD
    def RemoveTrigger(self, trigger):
        try:
            ix = self.triggers.index(trigger)
        except ValueError:
            ix = -1

        if ix >= 0:
            del self.triggers[ix]
            heapq.heapify(self.triggers)
            self.PurgeTriggers()
            return self.UpdateRepeatTime()

    @telemetry.ZONE_METHOD
    def UpdateRepeatTime(self):
        lastTime = -1
        candidate = None
        for trigger in self.triggers:
            if trigger.stamp > lastTime:
                lastTime = trigger.stamp
                candidate = trigger

        if candidate is None:
            return -1
        now = blue.os.GetSimTime()
        duration = int(candidate.duration)
        durationInBluetime = SECOND * duration / 1000
        wholeRepeatsLeft = long((candidate.stamp - now) / durationInBluetime)
        if wholeRepeatsLeft == candidate.repeat:
            wholeRepeatsLeft -= 1
        newStamp = candidate.stamp - wholeRepeatsLeft * durationInBluetime
        if newStamp == self.stamp:
            return 0
        self.stamp = newStamp
        self.duration = candidate.duration
        return 1

    @telemetry.ZONE_METHOD
    def Repeat(self):
        if self.effect is None:
            raise RuntimeError('Activation::Repeat: No effect defined')
        stampUpdated = self.PurgeTriggers()
        if not self.triggers:
            self.Stop()
            return -1
        if not self.isOn:
            return stampUpdated
        try:
            self.effect.Repeat(self.duration)
        except:
            log.LogException()
            sys.exc_clear()

        return stampUpdated

    @telemetry.ZONE_METHOD
    def Stop(self, reason = STOP_REASON_DEFAULT):
        if not self.isOn:
            return
        if self.effect is None:
            raise RuntimeError('Activation::Stop: No effect defined')
        try:
            self.effect.Stop(reason)
        except:
            log.LogException()
            sys.exc_clear()

        self.isOn = False

    @telemetry.ZONE_METHOD
    def PurgeTriggers(self):
        now = blue.os.GetSimTime()
        while self.triggers and self.triggers[0].stamp <= now:
            heapq.heappop(self.triggers)

        return self.UpdateRepeatTime()

    def GetBalls(self):
        return self.balls

    def GetName(self):
        if self.triggers:
            return self.triggers[0].guid
        else:
            return 'unknown'

    def GetEffectFromGuid(self, trigger):
        classification = GetClassification(trigger.guid)
        if classification is None:
            raise RuntimeError('Activation::Unable to load effect for guid:', trigger.guid)
        classType = classification[0]
        args = classification[1:]
        return classType(trigger, *args)


def GetFxSequencer():
    return sm.GetService('FxSequencer')


class FxSequencer(Service):
    __guid__ = 'svc.FxSequencer'
    __exportedcalls__ = {'ClearAll': [],
     'NotifyModelLoaded': [],
     'EnableGuids': [],
     'DisableGuids': [],
     'GetDisabledGuids': []}
    __notifyevents__ = ['OnSpecialFX',
     'DoBallRemove',
     'DoSimClockRebase',
     'DoBallsRemove',
     'OnGraphicSettingsChanged']
    __dependencies__ = ['michelle']
    __startupdependencies__ = ['settings']

    def __init__(self):
        Service.__init__(self)
        self.activations = {}
        self.stopCandidates = []
        self.ballRegister = {}
        self.delayedtriggers = {}
        self.killLoop = True
        self.sequencerTasklet = None
        self.disabledGuids = {}

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.lock = locks.RLock()
        self.disabledGuids = settings.user.ui.Get('disabledGuids', {})
        self.sequencerTasklet = uthread.new(self.SequencerLoop)
        self.sequencerTasklet.context = 'FxSequencer::SequencerLoop'
        if gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            self.EnableGuids(FX_TURRET_EFFECT_GUIDS)
        else:
            self.DisableGuids(FX_TURRET_EFFECT_GUIDS)
        candidateEffects = []
        for guid in GetEffectGuids():
            if guid not in FX_TURRET_EFFECT_GUIDS and guid not in FX_PROTECTED_EFFECT_GUIDS:
                candidateEffects.append(guid)

        if gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED):
            self.EnableGuids(candidateEffects)
        else:
            self.DisableGuids(candidateEffects)

    def Stop(self, ms):
        Service.Stop(self)
        self.killLoop = True
        blue.pyos.synchro.WakeupAtSim(self.sequencerTasklet, 0, -1)
        self.sequencerTasklet = None

    def DoSimClockRebase(self, times):
        oldSimTime, newSimTime = times
        offset = newSimTime - oldSimTime
        for activation in self.activations.itervalues():
            activation.stamp += offset
            for trigger in activation.triggers:
                with ExceptionEater('Adjusting time on an FX trigger'):
                    trigger.stamp += offset
                    if trigger.startTime:
                        trigger.startTime += offset

        for triggerList in self.delayedtriggers.itervalues():
            for trigger in triggerList:
                with ExceptionEater('Adjusting time on a delayed FX trigger'):
                    if trigger.startTime:
                        trigger.startTime += offset

    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.UI_TURRETS_ENABLED in changes:
            if gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
                self.EnableGuids(fxTurretGuids)
            else:
                self.DisableGuids(fxTurretGuids)
        if gfxsettings.UI_EFFECTS_ENABLED in changes:
            candidateEffects = []
            for guid in GetEffectGuids():
                if guid not in fxTurretGuids and guid not in fxProtectedGuids:
                    candidateEffects.append(guid)

            if len(candidateEffects) > 0:
                if gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED):
                    self.EnableGuids(candidateEffects)
                else:
                    self.DisableGuids(candidateEffects)

    @telemetry.ZONE_METHOD
    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        if start == 1 and guid in self.disabledGuids:
            return
        if IsTravelEffect(guid) and sm.GetService('subway').Enabled():
            return
        if startTime is not None and guid in FX_LONG_ONESHOT_GUIDS:
            now = blue.os.GetSimTime()
            if now - startTime > 150000000:
                return
        classification = GetClassification(guid)
        if classification is not None:
            effect = classification[1]
            mergeFlags = getattr(effect, 'mergeFlags')
        else:
            effect = None
            mergeFlags = [0]
        trigger = Trigger(shipID=shipID, moduleID=moduleID, moduleTypeID=moduleTypeID, targetID=targetID, otherTypeID=otherTypeID, guid=guid, isOffensive=isOffensive, duration=duration, repeat=repeat, startTime=startTime, timeFromStart=timeFromStart, graphicInfo=graphicInfo, mergeFlags=mergeFlags, controllerVariableTriggers=getattr(effect, 'controllerVariableTriggers', {}))
        if trigger.repeat is None or trigger.repeat <= 0:
            trigger.repeat = 1
        else:
            trigger.repeat += 1
        if guid is None:
            self.LogWarn('FxSequencer::OnSpecialFx: No guid in trigger for moduleTypeID', moduleTypeID, 'and graphicInfo', graphicInfo)
            return
        splitGuid = guid.split('.')
        if len(splitGuid) != 2:
            self.LogInfo('FxSequencer::OnSpecialFx: No guid in trigger')
            return
        niceName = guid.split('.')[1]
        if shipID == session.shipid:
            ship = 'for myself'
        elif IsFullLogging():
            ship = 'for ship: %s' % shipID
        else:
            ship = 'for another ship'
        if start == 1:
            if active == 0:
                self.LogInfo('FxSequencer::OnSpecialFX: Got ONE-SHOT event:', niceName, ship, '[', moduleID, '] with duration:', duration)
            if trigger.repeat is not None and trigger.repeat > 0:
                self.LogInfo('Starting REPEAT event:', niceName, ship, '[', moduleID, '] with duration:', duration / 1000.0, 'and repeat:', trigger.repeat)
                self.AddTrigger(trigger)
            else:
                self.LogInfo('FxSequencer::OnSpecialFX: Starting TOGGLE event:', niceName, ship, '[', moduleID, ']')
            if targetID is not None:
                if targetID == session.shipid:
                    target = 'myself'
                else:
                    target = targetID
                self.LogInfo('targeted at:', target, 'and is', ['not', ''][isOffensive], 'offensive')
        else:
            self.RemoveTrigger(trigger)
            self.LogInfo('FxSequencer::OnSpecialFX: Stopping', niceName, 'for ship:', ship, 'and module:', moduleID)

    def EnableGuids(self, guids):
        for guid in guids:
            if guid in self.disabledGuids:
                del self.disabledGuids[guid]

        settings.user.ui.Set('disabledGuids', self.disabledGuids)
        self.LogInfo('FxSequencer::EnableGuids', guids, ' Current disabled guids:', self.disabledGuids)

    def DisableGuids(self, guids):
        for guid in guids:
            if guid not in self.disabledGuids and guid not in FX_PROTECTED_EFFECT_GUIDS:
                self.disabledGuids[guid] = None

        settings.user.ui.Set('disabledGuids', self.disabledGuids)
        self.LogInfo('FxSequencer::DisableGuids', guids, ' Current disabled guids:', self.disabledGuids)

    def GetDisabledGuids(self):
        return self.disabledGuids

    @telemetry.ZONE_METHOD
    def AddTrigger(self, trigger):
        with self.lock:
            telemetry.APPEND_TO_ZONE(trigger.guid)
            self.LogInfo('FxSequencer::AddTrigger: Entering')
            shipBall = None
            targetBall = None
            if trigger.shipID is not None:
                shipBall = self.GetBall(trigger.shipID)
            if trigger.targetID is not None:
                targetBall = self.GetBall(trigger.targetID)
            classification = GetClassification(trigger.guid)
            if trigger.shipID is not None and shipBall is None:
                self.LogWarn('FxSequencer::AddTrigger: ship not in ballpark. Trigger ignored')
                return
            if classification and classification[0] is ShipRenderEffect:
                if hasattr(shipBall, 'model') and not hasattr(shipBall.model, 'overlayEffects'):
                    self.LogInfo('This ball', shipBall.id, 'of type', self.GetItem(trigger.shipID).typeID, 'does not support the ship effect', trigger.guid)
                    return
            if isinstance(shipBall, PlayerOwnedStructure) and getattr(trigger, 'moduleID', None):
                trigger.shipID = trigger.moduleID
            if trigger.targetID is not None and targetBall is None:
                self.LogWarn('FxSequencer::AddTrigger: target not in ballpark. Trigger ignored')
                return
            delayed = False
            if trigger.shipID is not None and getattr(shipBall, 'model', None) is None:
                if trigger.shipID in self.delayedtriggers:
                    self.delayedtriggers[trigger.shipID].append(trigger)
                else:
                    self.delayedtriggers[trigger.shipID] = [trigger]
                delayed = True
            if trigger.targetID is not None and getattr(targetBall, 'model', None) is None:
                if trigger.targetID in self.delayedtriggers:
                    self.delayedtriggers[trigger.targetID].append(trigger)
                else:
                    self.delayedtriggers[trigger.targetID] = [trigger]
                delayed = True
            if delayed:
                return
            key = self.GetKey(trigger)
            if trigger.duration is None or trigger.duration <= 0.0:
                if classification is not None:
                    trigger.duration = getattr(classification[1], 'duration', None)
            if trigger.repeat is None or trigger.repeat == 0:
                trigger.repeat = 1
            trigger.__dict__['stamp'] = blue.os.GetSimTime() + long(trigger.duration * trigger.repeat / 1000.0 * SECOND)
            if key in self.activations and trigger.guid not in ('effects.Cloak', 'effects.Uncloak'):
                activation = self.activations[key]
                activation.AddTrigger(trigger)
                self.AddActivationToBallRegister(activation)
                effect = activation.effect
                if effect and trigger.graphicInfo:
                    effect.UpdateGraphicInfo(trigger.graphicInfo)
            else:
                self.AddActivation(trigger, key)
        self.LogInfo('FxSequencer::AddTrigger: Done')

    @telemetry.ZONE_METHOD
    def RemoveTrigger(self, trigger):
        self.LogInfo('FxSequencer::RemoveTrigger: Entering')
        shipBall = None
        if trigger.shipID is not None:
            shipBall = self.GetBall(trigger.shipID)
        if getattr(shipBall, '__guid__', '') == 'spaceObject.PlayerOwnedStructure' and getattr(trigger, 'moduleID', None) is not None:
            trigger.shipID = trigger.moduleID
        key = self.GetKey(trigger)
        if key not in self.activations:
            self.LogInfo('FxSequencer::RemoveTrigger: Trigger not found')
            return
        activation = self.activations[key]
        updateTime = activation.RemoveTrigger(trigger)
        if updateTime == -1:
            self.LogInfo('FxSequencer::RemoveTrigger: Activation empty. Deleting it.')
            self.RemoveActivation(activation, fromSequencer=True)
        self.LogInfo('FxSequencer::RemoveTrigger:', trigger.guid, 'Done')

    @telemetry.ZONE_METHOD
    def SequencerLoop(self):
        self.killLoop = False
        reason = None
        self.LogInfo('FxSequencer: Sequencer loop starting')
        while not getattr(self, 'killLoop', True):
            self.CheckForStopCandidates()
            if self.stopCandidates:
                wakeupTime = self.stopCandidates[0].stamp
            else:
                wakeupTime = blue.os.GetSimTime() + 60 * SECOND
            reason = blue.pyos.synchro.SleepUntilSim(wakeupTime)

        self.LogInfo('FxSequencer: Sequencer loop terminated with reason', reason)

    @telemetry.ZONE_METHOD
    def CheckForStopCandidates(self):
        now = blue.os.GetSimTime()
        while self.stopCandidates and self.stopCandidates[0].isZombie:
            heapq.heappop(self.stopCandidates)

        while self.stopCandidates and self.stopCandidates[0].stamp < now:
            activation = heapq.heappop(self.stopCandidates)
            state = activation.Repeat()
            if state == -1:
                self.LogInfo('FxSequencer::CheckForStopCandidates: activation expired')
                self.RemoveActivation(activation)
            else:
                heapq.heappush(self.stopCandidates, activation)
            while self.stopCandidates and self.stopCandidates[0].isZombie:
                heapq.heappop(self.stopCandidates)

            now = blue.os.GetSimTime()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.RemoveAllBallActivations(ball.id)

    @telemetry.ZONE_METHOD
    def DoBallRemove(self, ball, slimItem, terminal):
        self.RemoveAllBallActivations(ball.id)

    @telemetry.ZONE_METHOD
    def GetKey(self, trigger):
        key = []
        if FX_MERGE_GUID in trigger.mergeFlags:
            key.append(trigger.guid)
        if FX_MERGE_SHIP in trigger.mergeFlags:
            key.append(trigger.shipID)
        if FX_MERGE_MODULE in trigger.mergeFlags:
            key.append(trigger.moduleID)
        if FX_MERGE_TARGET in trigger.mergeFlags:
            key.append(trigger.targetID)
        if len(key) == 0:
            log.LogWarn('Key is empty for trigger:', trigger)
            return
        return tuple(key)

    @telemetry.ZONE_METHOD
    def AddActivation(self, trigger, key = None):
        if key is None:
            key = self.GetKey(trigger)
        activation = Activation(self)
        activation.key = key
        self.activations[key] = activation
        activation.AddTrigger(trigger)
        self.AddActivationToBallRegister(activation)
        self.AddActivationToSequencer(activation)

    @telemetry.ZONE_METHOD
    def AddActivationToSequencer(self, activation):
        currentStopTime = activation.stamp
        reschedule = True
        if self.stopCandidates:
            if self.stopCandidates[0].stamp <= currentStopTime:
                reschedule = False
        heapq.heappush(self.stopCandidates, activation)
        if reschedule:
            try:
                self.LogInfo('AddActivationToSequencer: just going for some rescheduling here')
                blue.pyos.synchro.WakeupAtSim(self.sequencerTasklet, currentStopTime)
            except:
                self.LogInfo('AddActivationToSequencer: Activation rescedule failed, sequencer will wake up by itself')
                sys.exc_clear()

        self.LogInfo('AddActivationToSequencer: Activation added')

    @telemetry.ZONE_METHOD
    def RemoveActivation(self, activation, fromSequencer = False, reason = STOP_REASON_DEFAULT):
        niceName = activation.GetName()
        activation.Stop(reason)
        if activation.key in self.activations:
            del self.activations[activation.key]
        self.RemoveActivationFromBallRegister(activation)
        if fromSequencer:
            self.RemoveActivationFromSequencer(activation)
        self.LogInfo('FxSequencer::RemoveActivation:', niceName, 'activation removed.', len(self.activations), 'remaining')

    @telemetry.ZONE_METHOD
    def RemoveActivationFromSequencer(self, activation):
        activation.Zombify()
        try:
            if self.stopCandidates:
                blue.pyos.synchro.WakeupAtSim(self.sequencerTasklet, self.stopCandidates[0].stamp)
            else:
                blue.pyos.synchro.WakeupAtSim(self.sequencerTasklet, blue.os.GetSimTime() + 60 * SECOND)
        except:
            pass

        self.LogInfo('RemoveActivationFromSequencer:', activation)

    def ClearAll(self):
        self.LogInfo('FxSequencer::ClearAll')
        for activation in self.activations.values():
            self.RemoveActivation(activation, fromSequencer=True)

        self.stopCandidates = []
        if len(self.delayedtriggers):
            self.LogWarn('FxSequencer::ClearAll: Model Loaded notifications never came through?')
            self.delayedtriggers = {}
        if len(self.stopCandidates) or len(self.activations) or len(self.ballRegister):
            self.LogWarn('FxSequencer::ClearAll: Incomplete reset')

    def AreModelsLoadedForTrigger(self, trigger):
        if trigger.targetID is not None and trigger.targetID in self.delayedtriggers:
            return False
        if trigger.shipID is not None and trigger.shipID in self.delayedtriggers:
            return False
        return True

    @telemetry.ZONE_METHOD
    def NotifyModelLoaded(self, ballID):
        if ballID in self.delayedtriggers:
            initiateTriggers = self.delayedtriggers.pop(ballID)
            self.LogInfo('FxSequencer::NotifyModelLoaded', ballID, 'initiating', len(initiateTriggers), 'triggers')
            for trigger in initiateTriggers:
                if self.AreModelsLoadedForTrigger(trigger):
                    self.AddTrigger(trigger)

    def GetAllBallActivations(self, ballID):
        if ballID in self.ballRegister:
            return self.ballRegister[ballID]
        return set()

    def GetAllBallActivationNames(self, ballID):
        return set([ a.GetName() for a in self.GetAllBallActivations(ballID) ])

    def RemoveAllBallActivations(self, ballID):
        if ballID in self.ballRegister:
            self.LogInfo('FxSequencer::RemoveAllBallActivations for ball', ballID)
            self.RemoveActivationsForBallID(ballID)

    def RemoveActivationAtTime(self, activation, g):
        uthread.new(self._RemoveActivationAtTime, activation, g)

    def _RemoveActivationAtTime(self, activation, g):
        blue.synchro.SleepUntilSim(g)
        self.RemoveActivation(activation, fromSequencer=True, reason=STOP_REASON_BALL_REMOVED)

    def RemoveActivationsForBallID(self, ballID):

        def explosionTimeCallback(sequencer, activationObject):
            return lambda g, w: sequencer.RemoveActivationAtTime(activationObject, g)

        for activation in tuple(self.ballRegister.get(ballID, [])):
            removeImmediately = True
            if ballID == activation.effect.GetEffectTargetID():
                ball = self.GetBall(ballID)
                if destructionEffectType.isExplosionOrOverride(ball.destructionEffectId):
                    removeImmediately = False
                    SpaceObjectExplosionManager.GetExplosionTimesWhenAvailable(ballID, explosionTimeCallback(self, activation))
            if removeImmediately:
                self.RemoveActivation(activation, fromSequencer=True, reason=STOP_REASON_BALL_REMOVED)

    def AddActivationToBallRegister(self, activation):
        for ballID in activation.GetBalls():
            if ballID is not None:
                if ballID in self.ballRegister:
                    self.ballRegister[ballID].add(activation)
                else:
                    self.ballRegister[ballID] = set([activation])
                sm.ScatterEvent('OnAddFX', activation.guid, ballID)

    def RemoveActivationFromBallRegister(self, activation):
        for ballID in activation.GetBalls():
            if ballID in self.ballRegister:
                try:
                    self.ballRegister[ballID].remove(activation)
                except KeyError:
                    pass

                if len(self.ballRegister[ballID]) == 0:
                    del self.ballRegister[ballID]
                sm.ScatterEvent('OnRemoveFX', activation.guid, ballID)

    def GetBall(self, ballID):
        return self.michelle.GetBall(ballID)

    def GetBallpark(self):
        return self.michelle.GetBallpark()

    def GetItem(self, itemID):
        return self.michelle.GetItem(itemID)

    def GetScene(self):
        return sm.GetService('sceneManager').GetRegisteredScene('default')

    def GetTypeAttribute(self, moduleTypeID, attributeEmpFieldRange):
        return sm.GetService('godma').GetTypeAttribute(moduleTypeID, attributeEmpFieldRange)


fxTurretGuids = FX_TURRET_EFFECT_GUIDS
fxProtectedGuids = FX_PROTECTED_EFFECT_GUIDS
exports = {'FxSequencer.fxTurretGuids': fxTurretGuids,
 'FxSequencer.fxProtectedGuids': fxProtectedGuids}
