#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\combat.py
import logging
import random
import uthread2
from ballpark.const import DESTINY_MODE_MISSILE
from ballpark.messenger.const import MESSAGE_ENTITY_SUPER_WEAPON_STOPPED
from behaviors import status
from behaviors.const.behaviorroles import COMBAT_EFFECTS_BY_ROLES
from behaviors.tasks import Task
from behaviors.utility.dogmatic import can_activate_effect_on_target, is_my_effect_active_on_target, try_activate_effect
from ccpProfile import TimedFunction
from dogma.const import attributeExplosiveDamage, attributeKineticDamage, attributeThermalDamage
from dogma.const import attributeFighterAbilityKamikazeDamageEM, attributeFighterAbilityKamikazeDamageExp
from dogma.const import attributeFighterAbilityKamikazeDamageKin
from dogma.const import attributeFighterAbilityKamikazeRange, attributeFighterSquadronSize
from dogma.const import attributeFighterAbilityKamikazeSignatureRadius, attributeEmDamage
from dogma.const import effectEntitySuperWeapon
from dogma.const import effectEntitySuperWeaponLanceAllRaces
from eve.server.script.mgt.fighters import GetControlledFighterRegistryForSolarsystem
from eveexceptions import UserError
logger = logging.getLogger(__name__)
MIN_THREAT_VALUE = float('-inf')

class ActivateSuperWeaponOnTarget(Task):

    @TimedFunction('behaviors::actions::combat::ActivateSuperWeaponOnTarget::OnEnter')
    def OnEnter(self):
        selectedTarget = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        self.SetStatusToFailed()
        item = self.context.ballpark.inventory2.GetItem(self.context.myItemId)
        if selectedTarget:
            if self.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(item.typeID, effectEntitySuperWeapon):
                self.SetStatusToSuspended()
                self.TryActivateEffect(effectEntitySuperWeapon, item.ownerID, selectedTarget)
            if self.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(item.typeID, effectEntitySuperWeaponLanceAllRaces):
                self.SetStatusToSuspended()
                self.TryActivateEffect(effectEntitySuperWeaponLanceAllRaces, item.ownerID, selectedTarget)

    @TimedFunction('behaviors::actions::combat::ActivateSuperWeaponOnTarget::TryActivateEffect')
    def TryActivateEffect(self, effectID, ownerID, targetID):
        try:
            self.SubscribeItem(self.context.myItemId, MESSAGE_ENTITY_SUPER_WEAPON_STOPPED, self.OnSuperWeaponStopped)
            self.context.dogmaLM.ActivateWithContext(ownerID, self.context.myItemId, effectID, targetid=targetID)
            logger.debug('SuperWeapon: %s: started super weapon on target %s with effect %s', self.context.myItemId, targetID, effectID)
        except UserError:
            logger.warn('SuperWeapon: %s: failed to activate on %s with effect %s', self.context.myItemId, targetID, effectID)
        except RuntimeError:
            logger.exception('Entity: %s - unexpected exception when starting effect %s on target %s', self.context.myItemId, effectID, targetID)

    def OnSuperWeaponStopped(self):
        if not self.IsInvalid():
            self.status = status.TaskSuccessStatus
            self.status.OnUpdated(self)
            logger.debug('SuperWeapon: %s: super weapon cycle stopped', self.context.myItemId)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ENTITY_SUPER_WEAPON_STOPPED, self.OnSuperWeaponStopped)
            Task.CleanUp(self)


class AddCharacterForPodding(Task):

    @TimedFunction('behaviors::actions::combat::AddCharacterForPodding::OnEnter')
    def OnEnter(self):
        characterIdForPodding = self.GetLastBlackboardValue(self.attributes.characterAddress)
        if characterIdForPodding:
            self.UpdatePoddingList(characterIdForPodding)
        self.status = status.TaskSuccessStatus

    def UpdatePoddingList(self, characterIdForPodding):
        poddingList = self.GetLastBlackboardValue(self.attributes.poddingTargetListAddress)
        if poddingList is None:
            poddingList = set()
        if characterIdForPodding not in poddingList:
            poddingList.add(characterIdForPodding)
            self.SendBlackboardValue(self.attributes.poddingTargetListAddress, poddingList)


class KamikazeAttack(Task):
    explosionDelaySeconds = 1.0
    explosionScheduled = False

    def _ScheduleExplosion(self, targetId):
        if not self.explosionScheduled:
            self.explosionScheduled = True
            uthread2.call_after_simtime_delay(self._ExplodeSquadron, self.explosionDelaySeconds, targetId)

    def EngageTarget(self, targetId):
        myBall = self.context.myBall
        notifyRange = self.context.ballpark.dogmaLM.GetAttributeValue(self.context.myItemId, attributeFighterAbilityKamikazeRange)
        distBetweenBalls = self.context.ballpark.GetSurfaceDist(myBall.id, targetId)
        if distBetweenBalls <= 0.0:
            self._ScheduleExplosion(targetId)
        if self.context.myBall.mode == DESTINY_MODE_MISSILE:
            self.SetStatusToRunning()
            return
        if distBetweenBalls <= notifyRange:
            self.DoTargetTracking()
            self.SetStatusToRunning()
            return
        myBall.ApproachObject(targetId, approachRange=-999999.0, cruise=False)
        self.context.myBall.DoTargetTracking = self.DoTargetTracking
        self.context.myBall.DoCollision = self.DoCollision
        self.context.ballpark.SetTargetTracking(self.context.myItemId, targetId, notifyRange)
        self.SetStatusToRunning()

    @TimedFunction('behaviors::actions::combat::KamikazeAttack::OnEnter')
    def OnEnter(self):
        selfItem = self.GetSelfAsItem()
        if not selfItem:
            self.SetStatusToFailed()
            return
        self.Update()

    def _GetTargetBall(self):
        targetId = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        return self.context.ballpark.GetBallOrNone(targetId)

    def Abort(self):

        def noop(*args, **kwargs):
            pass

        if self.context.myBall.mode == DESTINY_MODE_MISSILE:
            self.SendBlackboardValue(self.attributes.shouldAbortAddress, False)
            targetBall = self._GetTargetBall()
            if targetBall is None:
                self.context.ballpark.ExplodeEx(self.context.myBall.id)
            return
        self.context.myBall.DoCollision = noop
        self.context.myBall.DoTargetTracking = noop
        self.context.ballpark.StopEx(self.context.myItemId)
        self.SendBlackboardValue(self.attributes.shouldAbortAddress, False)
        self.SetStatusToSuccess()

    def Update(self):
        shouldAbort = self.GetLastBlackboardValue(self.attributes.shouldAbortAddress)
        targetBall = self._GetTargetBall()
        if targetBall is None or shouldAbort:
            self.Abort()
            return
        self.EngageTarget(targetBall.id)

    def GetSelfAsItem(self):
        return self.context.ballpark.inventory2.GetItem(self.context.myItemId)

    def GetTargetAsItem(self, targetId):
        return self.context.ballpark.inventory2.GetItem(targetId)

    def _ApplyDamageToTarget(self, fighterID):
        targetBall = self._GetTargetBall()
        if targetBall is None:
            return
        GAV = self.context.ballpark.dogmaLM.GetAttributeValue
        squadronSizeMultiplier = GAV(self.context.myItemId, attributeFighterSquadronSize)
        cloudSize = GAV(fighterID, attributeFighterAbilityKamikazeSignatureRadius)
        cloudFactor = self.context.ballpark.dogmaLM.GetCloudFactor(targetBall.id, cloudSize)
        damageAmount = squadronSizeMultiplier * cloudFactor
        damageByType = {attributeEmDamage: GAV(fighterID, attributeFighterAbilityKamikazeDamageEM),
         attributeExplosiveDamage: GAV(fighterID, attributeFighterAbilityKamikazeDamageExp),
         attributeKineticDamage: GAV(fighterID, attributeFighterAbilityKamikazeDamageKin),
         attributeThermalDamage: GAV(fighterID, attributeThermalDamage)}
        dogma = sm.GetService('dogma')
        dogma.ApplyDamage(None, self.context.myItemId, targetBall.id, damageAmount, indirectDogmaLM=self.context.ballpark.dogmaLM, splash=False, damageShieldOnly=False, sourceID=fighterID, weaponDamages=damageByType)

    def _ExplodeSquadron(self, targetID):
        fighterID = self.context.myItemId
        self._ApplyDamageToTarget(fighterID)
        self.context.ballpark.ExplodeEx(fighterID)
        self.SetStatusToSuccess()

    def DoCollision(self, otherID, otherX, otherY, otherZ):
        targetID = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        if otherID == targetID:
            self._ScheduleExplosion(targetID)

    def DoTargetTracking(self, *args):
        uthread2.start_tasklet(self._DoTargetTracking_Threaded, args)

    def _DoTargetTracking_Threaded(self, *args):
        targetID = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        if targetID is None:
            return
        fighterID = self.context.myItemId
        controllerRegistry = GetControlledFighterRegistryForSolarsystem(self.context.ballpark.solarsystemID)
        controllerID = controllerRegistry.GetControllerForFighter(self.context.myItemId)
        if controllerID is None:
            controllerID = 0
        self.context.ballpark.MissileFollow(fighterID, targetID, controllerID)
        self.context.ballpark.SetBallMassive(fighterID, False)


class ActivateCombatEffectsOnTarget(Task):

    @TimedFunction('behaviors::actions::combat::ActivateCombatEffectsOnTarget::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        selfItem = self.GetSelfAsItem()
        targetId = self.GetLastBlackboardValue(self.attributes.selectedTargetAddress)
        if targetId is None:
            return
        targetItem = self.GetTargetAsItem(targetId)
        if not selfItem or not targetItem:
            return
        self._ActivateCombatEffectsOnTarget(targetId, selfItem)

    def _ActivateCombatEffectsOnTarget(self, targetId, selfItem):
        reactionDelay = self._GetReactionDelay()
        for effectId in self.attributes.effectIds:
            if self._is_my_effect_active_on_target(effectId, targetId):
                self.SetStatusToSuccess()
                continue
            if self.CanActivateEffectOnTarget(effectId, selfItem.typeID, targetId):
                self._TryActiveEffect(effectId, targetId, reactionDelay)
                self.SetStatusToSuccess()

    def _TryActiveEffect(self, effectId, targetId, reactionDelay):
        uthread2.start_tasklet(try_activate_effect, self, effectId, self.attributes.repeat, target_id=targetId, delay=reactionDelay)

    def GetSelfAsItem(self):
        return self.context.ballpark.inventory2.GetItem(self.context.myItemId)

    def GetTargetAsItem(self, targetId):
        return self.context.ballpark.inventory2.GetItem(targetId)

    @TimedFunction('behaviors::actions::combat::ActivateCombatEffectsOnTarget::CanActivateEffectOnTarget')
    def CanActivateEffectOnTarget(self, effectId, typeId, targetId):
        return can_activate_effect_on_target(self, typeId, effectId, targetId)

    def _GetReactionDelay(self):
        if self.HasAttribute('reactionDelayMilliseconds'):
            return random.uniform(0.0, float(self.attributes.reactionDelayMilliseconds) / 1000.0)
        return random.random()

    def _is_my_effect_active_on_target(self, effectId, targetId):
        return is_my_effect_active_on_target(self, effectId, targetId)


class StopCombatEffectsOnTarget(Task):

    @TimedFunction('behaviors::actions::combat::StopCombatEffectsOnTarget::OnEnter')
    def OnEnter(self):
        self.status = status.TaskSuccessStatus
        item = self.context.ballpark.inventory2.GetItem(self.context.myItemId)
        for effectId in self.attributes.effectIds:
            if self.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(item.typeID, effectId):
                self.TryStopEffect(effectId)

    @TimedFunction('behaviors::actions::combat::StopCombatEffectsOnTarget::TryStopEffect')
    def TryStopEffect(self, effectId):
        try:
            self.context.dogmaLM.StopEffect(effectId, self.context.myItemId, forced=True)
            logger.debug('CeaseFireOnTarget: %s: stopped attacking with effect %s', self.context.myItemId, effectId)
        except UserError:
            pass


class OwnerListFilterAction(Task):

    @TimedFunction('behaviors::actions::combat::OwnerListFilterAction::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        itemIdSet = self.GetLastBlackboardValue(self.attributes.itemIdSetAddress)
        if not itemIdSet:
            return
        filteredItemIdSet = self.FilterSet(itemIdSet)
        if filteredItemIdSet != itemIdSet:
            self.SendBlackboardValue(self.attributes.itemIdSetAddress, filteredItemIdSet)

    def FilterSet(self, itemIdSet):
        filteredSet = itemIdSet.copy()
        for itemId in list(itemIdSet):
            slimItem = self.context.ballpark.slims.get(itemId)
            if slimItem and slimItem.ownerID in self.attributes.ownerIdSet:
                filteredSet.discard(itemId)

        return filteredSet


class GetCombatEffectsForRole(Task):

    @TimedFunction('behaviors::actions::combat::GetCombatEffectsForRole::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        if self._has_already_registered_combat_effects():
            return
        role = self.GetLastBlackboardValue(self.attributes.roleAddress)
        combatEffects = self._GetCombatEffectsOnTypeForRole(role)
        self.SendBlackboardValue(self.attributes.combatEffectsAddress, combatEffects)

    def _has_already_registered_combat_effects(self):
        return self.GetLastBlackboardValue(self.attributes.combatEffectsAddress) is not None

    def _GetCombatEffectsOnTypeForRole(self, role):
        combatEffectsByRole = COMBAT_EFFECTS_BY_ROLES.get(role, [])
        actualCombatEffectsByRoleOnType = []
        for effectId in combatEffectsByRole:
            if self.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(self.context.mySlimItem.typeID, effectId):
                actualCombatEffectsByRoleOnType.append(effectId)

        return actualCombatEffectsByRoleOnType
