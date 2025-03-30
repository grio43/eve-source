#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\common\dotRegistry.py
import log
import gametime
import uthread2
from dotWeapons.common.dotApplication import DotApplication
from dotWeapons.common.dotApplicationStore import DotApplicationStore
from eveexceptions import ExceptionEater
import logging
logger = logging.getLogger(__name__)
DOT_TICK_RATE_SEC = 1
SLIM_ITEM_DOT_ATTR_NAME = 'dotHpPercentageApplied'

class DotRegistry(object):

    def __init__(self, dogmaLM, dotClientNotifier):
        self.dogmaLM = dogmaLM
        self.clientNotifier = dotClientNotifier
        self._dotProcessingTasklet = None
        self._dynamicDotStore = DotApplicationStore(self.dogmaLM)

    def ApplyHitToTarget(self, targetID, missileInfo):
        dotApplication = DotApplication(gametime.GetSimTime(), missileInfo, targetID)
        self._ApplyDotToTargets(targetID, dotApplication)

    def _ApplyDotToTargets(self, targetID, dotApplication):
        log.LogInfo('DotWeapons: ApplyDotToTargets', dotApplication)
        self._dynamicDotStore.Insert(targetID, dotApplication)
        self.clientNotifier.ScheduleTargetUpdate(targetID)
        self.clientNotifier.ScheduleAttackerUpdate(dotApplication.charID, targetID)

    def GetDotWeaponsByTargetID(self):
        return self._dynamicDotStore.GetDotApplicationsForAllTargets()

    def ProcessDotAppssInQueue(self):
        log.LogInfo('DotWeapons: ProcessDotAppssInQueue')
        ballpark = self.dogmaLM.ballpark
        targetsToRemove = []
        damageInfoByTargetID = {}
        for targetID, dotWeapons in self._dynamicDotStore.IterateApplicationByTargetID():
            dotWeapons.ExpireDotApplications()
            if not dotWeapons.HasValidApplications():
                targetsToRemove.append(targetID)
                continue
            highestDamageInfo = dotWeapons.GetHighestDamageDotApplication(self.dogmaLM)
            if highestDamageInfo is None:
                continue
            damageInfoByTargetID[targetID] = (dotWeapons, highestDamageInfo)

        self.RemoveTargetsWithoutEffets(targetsToRemove)
        self.ApplyDamageToTargets(ballpark, damageInfoByTargetID)

    def ApplyDamageToTargets(self, ballpark, damageInfoByTargetID):
        for targetID, damageInfo in damageInfoByTargetID.iteritems():
            try:
                dotWeaponsForTarget, highestDamageInfo = damageInfo
                dmgApp = highestDamageInfo.dmgApplication
                self.dogmaLM.broker.dogma.ApplyFlatDamage(dmgApp.sourceShipItem.itemID, dmgApp.sourceShipItem, dmgApp.weaponItem, targetID, highestDamageInfo.damage, dmgApp.charID, self.dogmaLM)
                damageHpFraction = highestDamageInfo.damageHpFraction
                if dotWeaponsForTarget.IsDifferentHpFraction(damageHpFraction):
                    ballpark.UpdateSlimItemField(targetID, SLIM_ITEM_DOT_ATTR_NAME, 100 * damageHpFraction)
                    dotWeaponsForTarget.UpdateLastUpdatedHpFraction(damageHpFraction)
                attackerChanged, attackersToNotify = dotWeaponsForTarget.UpdateLastDamageApp(dmgApp)
                if attackerChanged:
                    self.clientNotifier.ScheduleTargetUpdate(targetID)
                for attackerID in attackersToNotify:
                    self.clientNotifier.ScheduleAttackerUpdate(attackerID, targetID)

            except StandardError as e:
                logger.exception('DotWeapons: Failed to apply damage')

    def RemoveTargetsWithoutEffets(self, targetsToRemove):
        ballpark = self.dogmaLM.ballpark
        for targetID in targetsToRemove:
            if not self._dynamicDotStore.IsTargetRecored(targetID):
                continue
            if self._dynamicDotStore.DoesTargetHaveValidApplication(targetID):
                continue
            self._dynamicDotStore.DeleteAllForTarget(targetID)
            ballpark.DeleteSlimItemField(targetID, SLIM_ITEM_DOT_ATTR_NAME)
            self.clientNotifier.ScheduleTargetUpdate(targetID)

    def ClearApplicationsForTarget(self, targetID):
        removed = self._dynamicDotStore.DeleteAllForTarget(targetID)
        if removed:
            self.dogmaLM.ballpark.DeleteSlimItemField(targetID, SLIM_ITEM_DOT_ATTR_NAME)
            self.clientNotifier.ScheduleTargetUpdate(targetID)

    def GetDotAppsOnTarget(self, targetID):
        return self._dynamicDotStore.GetDotAppsOnTarget(targetID)

    def ScheduleTargetUpdate(self, targetID):
        self.clientNotifier.ScheduleTargetUpdate(targetID)

    def KillDotProcessingTasklet(self):
        if self._dotProcessingTasklet:
            self._dotProcessingTasklet.Kill()
            self._dotProcessingTasklet = None

    def StartDotProcessingTasklet(self):
        self.KillDotProcessingTasklet()
        self._dotProcessingTasklet = self._StartDotProcessingTasklet()

    def _StartDotProcessingTasklet(self):

        def ProcessingFunc():
            while True:
                with ExceptionEater('Error in ProcessDotAppssInQueue'):
                    self.ProcessDotAppssInQueue()
                uthread2.SleepSim(DOT_TICK_RATE_SEC)

        tasklet = uthread2.StartTasklet(ProcessingFunc)
        tasklet.context = 'dotWeapon::StartDotProcessingTasklet'
        return tasklet

    def IsDotPorcessingTaskletRunning(self):
        return bool(self._dotProcessingTasklet)
