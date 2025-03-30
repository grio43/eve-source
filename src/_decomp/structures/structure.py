#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\structures\structure.py
import datetime
from random import randint
import signals
import structures
from structures import reinforce
import logging
logger = logging.getLogger(__name__)

class Structure(object):

    def __init__(self):
        self.state = structures.STATE_UNKNOWN
        self.damage = (None, None, None)
        self.vulnerable = None
        self.firstAggressed = None
        self.lastAggressed = None
        self.notificationSent = False
        self.repairing = None
        self.unanchoring = None
        self.reinforceTiming = reinforce.ReinforceTiming()
        self.upkeepState = None
        self.abandonAt = None
        self.countdownTimer = CountdownTimer(self)
        self.deployStartTime = None
        self.deployEndTime = None
        self.structureSize = structures.STRUCTURE_SIZE_UNDEFINED
        self.deedState = None
        self.hangarView = None
        self.OnStateChanged = signals.Signal(signalName='OnStateChanged')
        self.OnDamageChanged = signals.Signal(signalName='OnDamageChanged')
        self.OnVulnerabilityChanged = signals.Signal(signalName='OnVulnerabilityChanged')
        self.OnRepairingChanged = signals.Signal(signalName='OnRepairingChanged')
        self.OnDeployTimeChanged = signals.Signal(signalName='OnDeployTimeChanged')
        self.OnAggressionChanged = signals.Signal(signalName='OnAggressionChanged')
        self.OnUnanchoringChanged = signals.Signal(signalName='OnUnanchoringChanged')
        self.OnFirstAggressed = signals.Signal(signalName='OnFirstAggressed')
        self.OnRepairCompleted = signals.Signal(signalName='OnRepairCompleted')
        self.OnReinforceTimeChanged = signals.Signal(signalName='OnReinforceTimeChanged')

    def IsFlexStructure(self):
        return self.structureSize == structures.STRUCTURE_SIZE_FLEX

    def IsMediumStructure(self):
        return self.structureSize == structures.STRUCTURE_SIZE_MEDIUM

    def Update(self):
        self.UpdateVulnerability()
        self.UpdateState()
        self.UpdateTimers()
        self.UpdateRepair()
        self.UpdateUnanchoring()
        self.UpdateReinforceTimer()
        self.UpdateUpkeep()
        self.UpdateDeed()

    def SaveState(self, state):
        pass

    def SaveDamage(self, damage):
        pass

    def SaveVulnerable(self, vulnerable):
        pass

    def SaveReinforceTimes(self):
        pass

    def SaveTimer(self, start, end, paused):
        pass

    def SaveRepairing(self, repairing):
        pass

    def SaveUnanchoring(self, unanchoring):
        pass

    def _SaveDeployTimer(self, start, end):
        pass

    def SaveAbandoned(self):
        pass

    def SaveUpkeepState(self):
        pass

    def GetRepairTime(self):
        return structures.STATE_REPAIR_TIME.get(self.state, structures.DEFAULT_REPAIR_TIMER)

    def GetReinforceDurationArmor(self):
        return structures.REINFORCE_DURATION_ARMOR_DEFAULT

    def GetReinforceDurationHull(self):
        return structures.REINFORCE_DURATION_HULL_DEFAULT

    def ApplyJitterToReinforceExitTime(self, exitTime):
        if self.IsFlexStructure():
            jitterRange = structures.REINFORCE_EXIT_JITTER_FLEX_SECONDS
        elif self.IsMediumStructure():
            jitterRange = structures.REINFORCE_EXIT_JITTER_MEDIUM_SECONDS
        else:
            jitterRange = structures.REINFORCE_EXIT_JITTER_DEFAULT_SECONDS
        return exitTime + reinforce.GenerateJitterTimeDelta(jitterRange)

    def GenerateArmorReinforceExitDateTime(self, startDateTime):
        duration = self.GetReinforceDurationArmor()
        exitTime = startDateTime + datetime.timedelta(seconds=duration)
        exitTime = self.reinforceTiming.GetEarliestTimeAfterDatetime(exitTime)
        exitTime = self.ApplyJitterToReinforceExitTime(exitTime)
        return exitTime

    def GenerateHullReinforceExitDateTime(self, startDateTime):
        if self.IsFlexStructure():
            duration = structures.FLEX_REINFORCE_DURATION_HULL
        else:
            duration = self.GetReinforceDurationHull()
        exitTime = startDateTime + datetime.timedelta(seconds=duration)
        exitTime = self.reinforceTiming.GetEarliestTimeAfterDatetime(exitTime)
        exitTime = self.ApplyJitterToReinforceExitTime(exitTime)
        return exitTime

    def GetAnchoringTime(self):
        return structures.ANCHORING_TIME

    def GetFlexDeployingTime(self):
        return structures.FLEX_DEPLOYING_TIME

    def GetUnanchoringTime(self):
        if self.IsFlexStructure():
            return structures.FLEX_UNANCHORING_TIME
        elif self.IsInsurgencyFOB():
            return structures.INSURGENCY_FOB_UNANCHORING_TIME
        else:
            return structures.UNANCHORING_TIME

    def HandleStateChanged(self):
        self.countdownTimer.ClearTimer()
        self.SetDeployingTimer(None, None)
        self.SetRepairing(None)
        self.UpdateVulnerability()
        self.UpdateTimers()
        self.SetAggression(None)
        self.UpdateShieldArmorHull()
        self.UpdateRepair()
        self.UpdateUnanchoring()
        self.UpdateReinforceTimer()

    def HandleDamageChanged(self):
        self.UpdateAggression()
        self.Update()

    def UpdateShieldArmorHull(self, *args):
        if self.state in structures.STATE_SHIELD_ARMOR_HULL:
            self.SetDamage(*structures.STATE_SHIELD_ARMOR_HULL[self.state])

    def UpdateVulnerability(self, *args):
        if self.state in structures.STATE_VULNERABILITY:
            self.SetVulnerable(structures.STATE_VULNERABILITY[self.state])

    def UpdateState(self, *args):
        if self.state == structures.STATE_SHIELD_VULNERABLE:
            if self.IsArmorDamaged() and self.CanHaveArmorPhases():
                self.PlaySpecialFX('effects.StructureRepairStateFailed')
                if self._CanHaveArmorReinforce():
                    self.SetState(structures.STATE_ARMOR_REINFORCE)
                else:
                    self.SetState(structures.STATE_ARMOR_VULNERABLE)
            elif self.IsHullDamaged():
                self.PlaySpecialFX('effects.StructureRepairStateFailed')
                if self._CanHaveHullReinforce():
                    self.SetState(structures.STATE_HULL_REINFORCE)
                else:
                    self.SetState(structures.STATE_HULL_VULNERABLE)
        elif self.state == structures.STATE_ARMOR_REINFORCE:
            if self.countdownTimer.IsExpired():
                self.SetState(structures.STATE_ARMOR_VULNERABLE)
        elif self.state == structures.STATE_ARMOR_VULNERABLE:
            if not self.IsDamaged():
                self.SetState(structures.STATE_SHIELD_VULNERABLE)
            elif self.IsHullDamaged():
                self.PlaySpecialFX('effects.StructureRepairStateFailed')
                if self._CanHaveHullReinforce():
                    self.SetState(structures.STATE_HULL_REINFORCE)
                else:
                    self.SetState(structures.STATE_HULL_VULNERABLE)
        elif self.state == structures.STATE_HULL_REINFORCE:
            if self.countdownTimer.IsExpired():
                self.SetState(structures.STATE_HULL_VULNERABLE)
        elif self.state == structures.STATE_HULL_VULNERABLE:
            if self.IsShieldOrArmorFullyHealed():
                self.SetState(structures.STATE_SHIELD_VULNERABLE)
        elif self.state == structures.STATE_ANCHOR_VULNERABLE:
            if not self.IsDamaged():
                self.SetState(structures.STATE_ANCHORING)
        elif self.state == structures.STATE_ANCHORING:
            if self.countdownTimer.IsExpired():
                self.SetState(structures.STATE_ONLINING_VULNERABLE)
        elif self.state == structures.STATE_FITTING_INVULNERABLE:
            if self.countdownTimer.IsExpired():
                self.PlaySpecialFX('effects.StructureRepairStateComplete')
                self.SetState(structures.STATE_SHIELD_VULNERABLE)
        elif self.state == structures.STATE_ONLINING_VULNERABLE:
            if not self.IsDamaged() and self.HasDeedInSlot():
                self.SetState(structures.STATE_SHIELD_VULNERABLE)
        elif self.state == structures.STATE_DEPLOY_VULNERABLE:
            if self.IsDeployTimeCompleted() and not self.IsHullDamaged():
                self.SetState(structures.STATE_SHIELD_VULNERABLE)
        elif self.state == structures.STATE_ONLINE_DEPRECATED:
            self.SetState(structures.STATE_SHIELD_VULNERABLE)

    def _CanHaveArmorReinforce(self):
        if self.IsUpkeepState_Abandoned():
            return False
        if self.IsFlexStructure():
            return False
        if not self.IsMediumStructure() and self.IsUpkeepState_Low():
            return False
        return True

    def _CanHaveHullReinforce(self):
        if self.IsUpkeepState_Abandoned():
            return False
        if self.IsFlexStructure() and self.IsUpkeepState_Low():
            return False
        if self.IsMediumStructure():
            return False
        if self.IsInsurgencyFOB():
            return False
        return True

    def CanHaveArmorPhases(self):
        return True

    def IsDeployTimeCompleted(self):
        return self.deployEndTime and self.deployEndTime < self.GetTimeNow()

    def UpdateAggression(self, *args):
        if self.IsAggressed():
            aggressed = self.GetFirstAggressed()
            if not aggressed:
                self.SetAggression(self.GetTimeNow(), self.GetTimeNow())
            else:
                self.SetAggression(aggressed, self.GetTimeNow())
        else:
            self.SetAggression(None)

    def UpdateRepair(self, *args):
        if self.ShouldRepair():
            if self.GetRepairing() is None:
                self.countdownTimer.SetTimer(self.GetTimeNow() + datetime.timedelta(seconds=self.GetRepairTime()), self.GetTimeNow())
                self.SetRepairing(True)
            elif self.ShouldRepairPause():
                self.countdownTimer.Pause()
                self.SetRepairing(False)
            else:
                self.countdownTimer.Unpause()
                self.SetRepairing(True)
            if self.IsRepairing() and self.countdownTimer.IsExpired():
                self.PlaySpecialFX('effects.StructureRepairStateComplete')
                self.countdownTimer.ClearTimer()
                if self.state == structures.STATE_DEPLOY_VULNERABLE:
                    self.RepairHullOnly()
                else:
                    self.FullyRepairSelf()
                self.OnRepairCompleted()
        else:
            self.SetRepairing(None)

    def UpdateTimers(self, *args):
        if self.ShouldRepair():
            return
        if self.state == structures.STATE_SHIELD_VULNERABLE:
            self.countdownTimer.ClearTimer()
        elif self.state == structures.STATE_ARMOR_REINFORCE:
            if not self.countdownTimer.IsRunning():
                start = self.GetTimeNow()
                self.countdownTimer.SetTimer(self.GenerateArmorReinforceExitDateTime(start))
        elif self.state == structures.STATE_ARMOR_VULNERABLE:
            self.countdownTimer.ClearTimer()
        elif self.state == structures.STATE_HULL_REINFORCE:
            if not self.countdownTimer.IsRunning():
                start = self.GetTimeNow()
                self.countdownTimer.SetTimer(self.GenerateHullReinforceExitDateTime(start))
        elif self.state == structures.STATE_HULL_VULNERABLE:
            self.countdownTimer.ClearTimer()
        elif self.state == structures.STATE_ANCHOR_VULNERABLE:
            self.countdownTimer.ClearTimer()
        elif self.state == structures.STATE_ANCHORING:
            if not self.countdownTimer.IsRunning():
                self.countdownTimer.SetTimer(self.GetTimeNow() + datetime.timedelta(seconds=self.GetAnchoringTime()))
        elif self.state == structures.STATE_FITTING_INVULNERABLE:
            if not self.countdownTimer.IsRunning():
                self.countdownTimer.SetTimer(self.GetTimeNow() + datetime.timedelta(seconds=structures.FITTING_INVULNERABLE_TIME))
        elif self.state == structures.STATE_ONLINING_VULNERABLE:
            self.countdownTimer.ClearTimer()
        elif self.state == structures.STATE_DEPLOY_VULNERABLE:
            if self.deployStartTime is None or self.deployEndTime is None:
                self.SetDeployingTimer(self.GetTimeNow(), self.GetTimeNow() + datetime.timedelta(seconds=self.GetFlexDeployingTime()))
        elif self.state == structures.STATE_ONLINE_DEPRECATED:
            self.countdownTimer.ClearTimer()
        elif self.state == structures.STATE_FOB_INVULNERABLE:
            self.countdownTimer.ClearTimer()

    def SetDeployingTimer(self, startTime, endTime):
        if startTime == self.deployStartTime and endTime == self.deployEndTime:
            return
        self.deployStartTime = startTime
        self.deployEndTime = endTime
        self._SaveDeployTimer(self.deployStartTime, self.deployEndTime)
        self.OnDeployTimeChanged()

    def UpdateUnanchoring(self):
        if structures.STATE_CANCELS_UNANCHOR.get(self.state) is True:
            if self.GetUnanchoring() is not None and hasattr(self, 'LogUnanchoringForceCancelled'):
                self.LogUnanchoringForceCancelled(self.state)
            self.SetUnanchoring(None)
        if self.HasUnanchoringExpired():
            self.SetState(structures.STATE_UNANCHORED)

    def UpdateReinforceTimer(self):
        if self.CanApplyNextReinforceTime():
            currentTime = self.GetTimeNow()
            if self.reinforceTiming.IsNextChangeReady(currentTime):
                self.reinforceTiming.ApplyNextTiming()
                self.SaveReinforceTimes()
                self.OnReinforceTimeChanged(None, None)

    def GetState(self):
        return self.state

    def SetState(self, state):
        if state not in structures.STATES:
            raise structures.InvalidStructureState(state)
        current = self.GetState()
        if state != current:
            self.state = state
            self.SaveState(state)
            self.HandleStateChanged()
            self.OnStateChanged(self, current, state)

    def IsOnline(self):
        return self.GetState() not in structures.OFFLINE_STATES

    def IsOffline(self):
        return self.GetState() in structures.OFFLINE_STATES

    def IsDisabled(self):
        return self.GetState() in structures.DISABLED_STATES

    def GetUnanchoring(self):
        return self.unanchoring

    def SetUnanchoring(self, unanchoring):
        if unanchoring is not None and not isinstance(unanchoring, datetime.datetime):
            raise TypeError('Unanchoring time must be a datetime object or None')
        if unanchoring != self.GetUnanchoring():
            self.unanchoring = unanchoring
            self.SaveUnanchoring(unanchoring)
            self.OnUnanchoringChanged(self, unanchoring)

    def SetUnanchoringRemaining(self, seconds):
        self.SetUnanchoring(self.GetTimeNow() + datetime.timedelta(seconds=int(seconds)))

    def GetUnanchoringRemaining(self):
        unanchoring = self.GetUnanchoring()
        if unanchoring is not None:
            return int((unanchoring - self.GetTimeNow()).total_seconds())

    def StartUnanchoring(self):
        if self.GetUnanchoring() is None:
            self.SetUnanchoring(self.GetTimeNow() + datetime.timedelta(seconds=self.GetUnanchoringTime()))

    def StopUnanchoring(self):
        if self.GetUnanchoring():
            self.SetUnanchoring(None)

    def IsUnanchoring(self):
        return self.unanchoring is not None

    def GetUnanchorTime(self):
        return self.unanchoring

    def HasUnanchoringExpired(self):
        unanchoring = self.GetUnanchoring()
        return unanchoring is not None and unanchoring <= self.GetTimeNow()

    def IsShieldDamaged(self):
        ALMOST_MAX_SHIELD_LEVEL = 0.995
        return self.GetShield() < ALMOST_MAX_SHIELD_LEVEL

    def IsArmorDamaged(self):
        return self.GetArmor() < 1

    def IsHullDamaged(self):
        return self.GetHull() < 1

    def IsDamaged(self):
        if self.GetDamage() == (None, None, None):
            return False
        return self.IsShieldDamaged() or self.IsArmorDamaged() or self.IsHullDamaged()

    def IsShieldOrArmorFullyHealed(self):
        if self.GetDamage() == (None, None, None):
            return True
        if not self.IsShieldDamaged():
            return True
        if not self.IsArmorDamaged():
            return True
        return False

    def IsInFittingState(self):
        return self.GetState() == structures.STATE_FITTING_INVULNERABLE

    def SetDamage(self, shield, armor, hull):
        damage = (max(min(float(shield), 1.0), 0.0), max(min(float(armor), 1.0), 0.0), max(min(float(hull), 1.0), 0.0))
        if damage != self.GetDamage():
            self.damage = damage
            self.SaveDamage(damage)
            self.HandleDamageChanged()
            self.OnDamageChanged(self, damage)

    def GetDamage(self):
        return self.damage

    def CanHaveAutoRepair(self):
        return True

    def ShouldRepair(self):
        if self.state in structures.STATES_THAT_REQUIRE_AUTO_REPAIR_TO_REPAIR and not self.CanHaveAutoRepair():
            return False
        elif not self.IsVulnerable():
            return False
        elif self.state == structures.STATE_DEPLOY_VULNERABLE:
            return self.IsHullDamaged()
        elif self.state == structures.STATE_ONLINING_VULNERABLE:
            return self.IsDamaged() and self.HasDeedInSlot()
        else:
            return self.IsDamaged()

    def ShouldRepairPause(self):
        return self.GetLastAggressed()

    def IsRepairing(self):
        return bool(self.repairing)

    def GetRepairing(self):
        return self.repairing

    def SetRepairing(self, repairing):
        if repairing is not None and not isinstance(repairing, bool):
            raise TypeError('Repairing must be a bool or None')
        if repairing != self.repairing:
            self.repairing = repairing
            self.SaveRepairing(repairing)
            self.OnRepairingChanged(self, repairing)

    def IsAggressed(self):
        if self.state == structures.STATE_SHIELD_VULNERABLE:
            return self.IsShieldDamaged()
        if self.state == structures.STATE_ARMOR_VULNERABLE:
            return self.IsArmorDamaged()
        if self.state == structures.STATE_HULL_VULNERABLE:
            return self.IsHullDamaged()
        if self.state == structures.STATE_ANCHOR_VULNERABLE:
            return self.IsHullDamaged()
        if self.state == structures.STATE_DEPLOY_VULNERABLE:
            return self.IsHullDamaged()

    def IsDamageBelowNotificationThreshold(self):
        if self.state == structures.STATE_SHIELD_VULNERABLE:
            return self.GetShield() < 0.95
        return True

    def GetFirstAggressed(self):
        return self.firstAggressed

    def GetLastAggressed(self):
        return self.lastAggressed

    def SetAggression(self, aggressed, latest = None):
        if aggressed is not None and not isinstance(aggressed, datetime.datetime):
            raise TypeError('Aggression time must be a datetime object or None')
        if latest is not None and not isinstance(aggressed, datetime.datetime):
            raise TypeError('Latest aggression time must be a datetime object or None')
        firstAggressed = self.GetFirstAggressed()
        if aggressed != firstAggressed or latest != self.GetLastAggressed():
            self.firstAggressed = aggressed
            self.lastAggressed = latest
            self.OnAggressionChanged(self, self.firstAggressed, self.lastAggressed)
        if self.firstAggressed is None:
            self.notificationSent = False
        if self.firstAggressed and not self.notificationSent:
            if self.IsDamageBelowNotificationThreshold():
                self.notificationSent = True
                self.OnFirstAggressed(self, self.firstAggressed)

    def GetShield(self):
        return self.GetDamage()[0]

    def GetArmor(self):
        return self.GetDamage()[1]

    def GetHull(self):
        return self.GetDamage()[2]

    def GetVulnerable(self):
        return self.vulnerable

    def IsVulnerable(self):
        return bool(self.GetVulnerable())

    def SetVulnerable(self, vulnerable):
        vulnerable = bool(int(vulnerable))
        existing = self.GetVulnerable()
        if vulnerable != existing:
            self.vulnerable = vulnerable
            self.SaveVulnerable(vulnerable)
            self.OnVulnerabilityChanged(self, existing, vulnerable)

    def SetReinforceTimes(self, weekday, hour, userID, characterID):
        self.reinforceTiming.SetReinforceTimes(weekday, hour)
        self.SaveReinforceTimes()
        self.OnReinforceTimeChanged(userID, characterID)

    def SetNextReinforceTimes(self, weekday, hour, delaySeconds, userID, characterID):
        applyAtTime = self.GetTimeNow() + datetime.timedelta(seconds=int(delaySeconds))
        self.reinforceTiming.SetNextReinforceTimes(weekday, hour, applyAtTime)
        self.SaveReinforceTimes()
        self.OnReinforceTimeChanged(userID, characterID)

    def GetTimeNow(self):
        now = datetime.datetime.utcnow()
        return now.replace(microsecond=0)

    def IsStateHullVulnerable(self):
        return self.state in (structures.STATE_HULL_VULNERABLE, structures.STATE_ANCHOR_VULNERABLE, structures.STATE_ONLINING_VULNERABLE)

    def IsStateArmorVulnerable(self):
        return self.state == structures.STATE_ARMOR_VULNERABLE

    def IsStateShieldVulnerable(self):
        return self.state == structures.STATE_SHIELD_VULNERABLE

    def FullyRepairSelf(self):
        self.SetDamage(1.0, 1.0, 1.0)

    def RepairHullOnly(self):
        self.SetDamage(0.0, 0.0, 1.0)

    def HasOnlineServiceModule(self):
        raise NotImplementedError()

    def SetAbandonAt(self, abandonAt):
        if abandonAt is not None:
            if not isinstance(abandonAt, datetime.datetime):
                raise TypeError('abandonAt must be a datetime object or None')
            if self.upkeepState != structures.UPKEEP_STATE_LOW_POWER:
                raise RuntimeError('Structure must be in Low Power to set abandon timer - current upkeep state = %s' % self.upkeepState)
            if not self.StructureAllowsAbandonment():
                raise RuntimeError('This structure does not allow abandonment')
        self.abandonAt = abandonAt
        self.SaveAbandoned()

    def UpdateUpkeep(self):
        if self.upkeepState == structures.UPKEEP_STATE_FULL_POWER:
            if not self.HasOnlineServiceModule():
                self.SetUpkeepState(structures.UPKEEP_STATE_LOW_POWER)
            elif self.abandonAt is not None:
                self.SetAbandonAt(None)
        elif self.upkeepState == structures.UPKEEP_STATE_LOW_POWER:
            if self.HasOnlineServiceModule():
                self.SetUpkeepState(structures.UPKEEP_STATE_FULL_POWER)
            elif self.abandonAt is None:
                if self.StructureAllowsAbandonment():
                    abandonDurationSec = randint(structures.ABANDONING_TIME_MIN, structures.ABANDONING_TIME_MAX)
                    self.SetAbandonAt(self.GetTimeNow() + datetime.timedelta(seconds=abandonDurationSec))
            elif self.abandonAt < self.GetTimeNow():
                self.SetUpkeepState(structures.UPKEEP_STATE_ABANDONED)
            else:
                self.ConsiderSendingImpendingAbandonWarnings()
        elif self.upkeepState == structures.UPKEEP_STATE_ABANDONED:
            if self.HasOnlineServiceModule():
                self.SetUpkeepState(structures.UPKEEP_STATE_FULL_POWER)
        else:
            logger.warn('UpdateUpkeep called for for unrecognised upkeep state - falling back to Full Power [%s]', self)
            self.SetUpkeepState(structures.UPKEEP_STATE_FULL_POWER)

    def SetUpkeepState(self, newUpkeepState):
        if newUpkeepState not in structures.ALL_UPKEEP_STATES:
            raise ValueError('newUpkeepState must be one of ALL_UPKEEP_STATES')
        if self.upkeepState != newUpkeepState:
            oldUpkeepState = self.upkeepState
            self.upkeepState = newUpkeepState
            self.SaveUpkeepState()
            self.OnUpkeepStateChanged(oldUpkeepState, newUpkeepState)
            self.UpdateUpkeep()

    def OnUpkeepStateChanged(self, oldUpkeepState, newUpkeepState):
        pass

    def IsUpkeepState_Full(self):
        return self.upkeepState == structures.UPKEEP_STATE_FULL_POWER

    def IsUpkeepState_Low(self):
        return self.upkeepState == structures.UPKEEP_STATE_LOW_POWER

    def IsUpkeepState_Abandoned(self):
        return self.upkeepState == structures.UPKEEP_STATE_ABANDONED

    def CanApplyNextReinforceTime(self):
        return self.state == structures.STATE_SHIELD_VULNERABLE and not self.IsDamaged()

    def CanActivateEquipment(self):
        return self.state in structures.CAN_ACTIVATE_EQUIPMENT_IN_STATE

    def PlaySpecialFX(self, guid):
        pass

    def ConsiderSendingImpendingAbandonWarnings(self):
        raise NotImplementedError()

    def StructureAllowsAbandonment(self):
        return True

    def UpdateDeed(self):
        newDeedState = self.CalculateDeedState()
        if newDeedState == self.deedState:
            return
        self.deedState = newDeedState
        self.Update()
        self.OnDeedStateChanged()

    def HasDeedInSlot(self):
        return self.deedState

    def CalculateDeedState(self):
        raise NotImplementedError()

    def OnDeedStateChanged(self):
        pass

    def IsInsurgencyFOB(self):
        return False


class CountdownTimer(object):

    def __init__(self, structure):
        self._structure = structure
        self.endDateTime = None
        self.startDateTime = None
        self.pausedDateTime = None
        self.OnTimerChanged = signals.Signal(signalName='OnTimerChanged')

    def LoadFromRow(self, structureRow):
        from carbon.common.script.util.format import BlueToDate
        self.startDateTime = BlueToDate(structureRow.timerStart)
        self.endDateTime = BlueToDate(structureRow.timerEnd)

    def IsRunning(self):
        return self.startDateTime and self.endDateTime

    def GetTimerRemaining(self):
        if self.endDateTime is not None:
            return int((self.endDateTime - self._structure.GetTimeNow()).total_seconds())

    def IsExpired(self):
        return self.endDateTime is None or self.endDateTime <= self._structure.GetTimeNow()

    def ClearTimer(self):
        if self.endDateTime is not None or self.startDateTime is not None or self.pausedDateTime is not None:
            self.startDateTime = None
            self.endDateTime = None
            self.pausedDateTime = None
            self._structure.SaveTimer(self.startDateTime, self.endDateTime, self.pausedDateTime)
            self.OnTimerChanged(self, self.startDateTime, self.endDateTime, self.pausedDateTime)

    def SetTimer(self, endDateTime, startDateTime = None, pausedDateTime = None):
        if endDateTime is not None and not isinstance(endDateTime, datetime.datetime):
            raise TypeError('Timer must be a datetime object or None')
        if isinstance(pausedDateTime, bool):
            pausedDateTime = self._structure.GetTimeNow() if pausedDateTime else None
        elif pausedDateTime is not None and not isinstance(pausedDateTime, datetime.datetime):
            raise TypeError('Paused must be a datetime object, a bool or None')
        if endDateTime != self.endDateTime or startDateTime != self.startDateTime or pausedDateTime != self.pausedDateTime:
            self.startDateTime = startDateTime or self._structure.GetTimeNow()
            self.endDateTime = endDateTime
            self.pausedDateTime = pausedDateTime
            self._structure.SaveTimer(self.startDateTime, self.endDateTime, self.pausedDateTime)
            self.OnTimerChanged(self, self.startDateTime, self.endDateTime, self.pausedDateTime)

    def IsPaused(self):
        return self.pausedDateTime is not None

    def Pause(self):
        if not self.IsRunning():
            return
        if not self.pausedDateTime:
            self.SetTimer(self.endDateTime, self.startDateTime, self._structure.GetTimeNow())

    def Unpause(self):
        if not self.IsRunning():
            logger.warn('CountdownTimer.Unpause() called for structure timer that is not running. %s', self._structure)
            return
        if self.pausedDateTime:
            elapsed = self._structure.GetTimeNow() - self.pausedDateTime
            start = elapsed + self.startDateTime
            end = elapsed + self.endDateTime
            self.SetTimer(end, start)

    def GetTimesBlue(self):
        if self.startDateTime and self.endDateTime:
            from carbon.common.script.util.format import DateToBlue
            return (DateToBlue(self.startDateTime), DateToBlue(self.endDateTime), DateToBlue(self.pausedDateTime))

    def GetEndTimeBlue(self):
        from carbon.common.script.util.format import DateToBlue
        return DateToBlue(self.endDateTime)


def LookupState(state):
    if state:
        state = str(state).lower()
        for value, name in structures.STATES.iteritems():
            if str(value) == state:
                return value
            if name.startswith(state):
                return value
