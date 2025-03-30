#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\crimewatchSvc.py
import clonegrade
import dogma.data
import blue
import uthread
import utillib
from carbon.common.script.sys.service import Service
from corruptionsuppression.systemEffects import DoesConcordReact
from crimewatch.const import containerGroupsWithLootRights
from crimewatch.util import IsItemFreeForAggression
from eve.client.script.ui.crimewatch.duelInviteWindow import DuelInviteWindow
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.eveCfg import IsControllingStructure
from eve.common.script.util import facwarCommon
from inventorycommon.const import categoryStructure
from inventorycommon.util import IsNPC
from spacecomponents.common.components.enforcecriminalflag import has_enforce_suspect_flag, has_enforce_criminal_flag
from spacecomponents.common.helper import HasEnforceCriminalFlagComponent
from evewar import warConst
from eve.common.script.sys.idCheckers import IsWormholeSystem
from eve.common.script.util.facwarCommon import IsSameFwFaction, IsCombatEnemyFaction

class CrimewatchService(Service):
    __guid__ = 'svc.crimewatchSvc'
    __dependencies__ = ['michelle',
     'godma',
     'war',
     'facwar',
     'corp',
     'securitySvc']
    __startupdependencies__ = []
    __notifyevents__ = ['ProcessSessionChange',
     'OnWeaponsTimerUpdate',
     'OnPvpTimerUpdate',
     'OnNpcTimerUpdate',
     'OnCriminalTimerUpdate',
     'OnDisapprovalTimerUpdate',
     'OnSystemCriminalFlagUpdates',
     'OnSystemDisapprovalFlagUpdates',
     'OnCrimewatchEngagementCreated',
     'OnCrimewatchEngagementEnded',
     'OnCrimewatchEngagementStartTimeout',
     'OnCrimewatchEngagementStopTimeout',
     'OnDuelChallenge',
     'OnSecurityStatusUpdate',
     'OnJumpTimersUpdated',
     'OnCorpAggressionSettingsChange',
     'OnSessionReset',
     'OnSubscriptionChanged']

    def Run(self, *args):
        Service.Run(self, *args)
        self.Initialize()

    def Initialize(self):
        self.weaponsTimerState = None
        self.weaponsTimerExpiry = None
        self.pvpTimerState = None
        self.pvpTimerExpiry = None
        self.npcTimerState = None
        self.npcTimerExpiry = None
        self.criminalTimerState = None
        self.criminalTimerExpiry = None
        self.disapprovalTimerState = None
        self.disapprovalTimerExpiry = None
        self.criminalFlagsByCharID = {}
        self.disapprovalFlagsByCharID = {}
        self.myEngagements = {}
        self.safetyLevel = const.shipSafetyLevelFull
        self.duelWindow = None
        self.mySecurityStatus = None
        self.jumpTimers = None
        self.corpAggressionSettings = None

    def OnSubscriptionChanged(self):
        if session.charid and session.solarsystemid:
            _, _, _, safetyLevel = eveMoniker.CharGetCrimewatchLocation().GetClientStates()
            self._UpdateSafetyLevel(safetyLevel)
            sm.ScatterEvent('OnReCheckAlphaLock')

    def ProcessSessionChange(self, isRemote, session, change):
        if 'locationid' in change or 'charid' in change:
            myCombatTimers, myEngagements, flaggedCharacters, safetyLevel = eveMoniker.CharGetCrimewatchLocation().GetClientStates()
            self.LogInfo('ProcessSessionChange', myCombatTimers, myEngagements, flaggedCharacters, safetyLevel)
            self._UpdateSafetyLevel(safetyLevel)
            weaponTimerState, pvpTimerState, npcTimerState, criminalTimerState, disapprovalTimerState = myCombatTimers
            self.weaponsTimerState, self.weaponsTimerExpiry = weaponTimerState
            self.pvpTimerState, self.pvpTimerExpiry = pvpTimerState
            self.npcTimerState, self.npcTimerExpiry = npcTimerState
            self.criminalTimerState, self.criminalTimerExpiry = criminalTimerState
            self.disapprovalTimerState, self.disapprovalTimerExpiry = disapprovalTimerState
            self.myEngagements = myEngagements
            sm.ScatterEvent('OnCombatTimersUpdated')
            criminals, suspects = flaggedCharacters
            self.criminalFlagsByCharID.clear()
            self.UpdateSuspectsAndCriminals(criminals, suspects)
            if self.duelWindow is not None:
                self.duelWindow.Close()
                self.duelWindow = None
        elif 'shipid' in change and session.structureid:
            _, _, _, safetyLevel = eveMoniker.CharGetCrimewatchLocation().GetClientStates()
            self.LogInfo('ProcessSessionChange', safetyLevel)
            self._UpdateSafetyLevel(safetyLevel)
        if 'corpid' in change:
            self.RefreshCorpAggressionSettings()

    def _ReCheckAlphaLock(self):
        if self._IsAlphaClone():
            sm.ScatterEvent('OnReCheckAlphaLock')

    def _IsAlphaClone(self):
        clone_grade = sm.GetService('cloneGradeSvc').GetCloneGrade()
        return clone_grade == clonegrade.CLONE_STATE_ALPHA

    def OnSessionReset(self):
        self.Initialize()

    def _UpdateSafetyLevel(self, safetyLevel):
        if self.IsSafetyLockedToFullLevel():
            safetyLevel = const.shipSafetyLevelFull
        old = self.safetyLevel
        self.safetyLevel = safetyLevel
        if self.safetyLevel != old:
            sm.ScatterEvent('OnSafetyLevelChanged', self.safetyLevel)
        elif self._IsAlphaClone():
            sm.ScatterEvent('OnReCheckAlphaLock')

    def IsSafetyLockedToFullLevel(self):
        if IsControllingStructure():
            securityClass = self.securitySvc.get_modified_security_class(session.solarsystemid)
            if securityClass >= const.securityClassHighSec:
                return True
        return False

    def IsSafetyAlphaLocked(self):
        if self._IsAlphaClone():
            if session.solarsystemid2:
                securityClass = self.securitySvc.get_modified_security_class(session.solarsystemid2)
                return securityClass >= const.securityClassHighSec
        return False

    def GetSlimItemDataForCharID(self, charID):
        slimItem = None
        if eveCfg.InShipInSpace():
            ballpark = self.michelle.GetBallpark()
            if ballpark:
                for _slimItem in ballpark.slimItems.itervalues():
                    if _slimItem.charID == charID:
                        slimItem = _slimItem
                        break

        if slimItem is None:
            pubInfo = sm.RemoteSvc('charMgr').GetPublicInfo(charID)
            info = cfg.eveowners.Get(charID)
            slimItem = utillib.KeyVal()
            slimItem.charID = charID
            slimItem.typeID = info.typeID
            slimItem.corpID = pubInfo.corporationID
            slimItem.warFactionID = pubInfo.warFactionID
            slimItem.allianceID = pubInfo.allianceID
            slimItem.securityStatus = self.GetCharacterSecurityStatus(charID)
            slimItem.groupID = const.groupCharacter
            slimItem.categoryID = const.categoryOwner
            slimItem.itemID = None
            slimItem.ownerID = charID
        return slimItem

    def UpdateSuspectsAndCriminals(self, criminals, suspects, decriminalizedCharIDs = ()):
        for charID in decriminalizedCharIDs:
            try:
                del self.criminalFlagsByCharID[charID]
            except KeyError:
                pass

        for charID in criminals:
            self.criminalFlagsByCharID[charID] = const.criminalTimerStateActiveCriminal

        for charID in suspects:
            self.criminalFlagsByCharID[charID] = const.criminalTimerStateActiveSuspect

        criminalizedCharIDs = set(self.criminalFlagsByCharID.iterkeys())
        sm.ScatterEvent('OnSuspectsAndCriminalsUpdate', criminalizedCharIDs, set(decriminalizedCharIDs))

    def UpdateDisapprovals(self, newNaughtyChars, noLongerNaughty):
        for charID in noLongerNaughty:
            self.disapprovalFlagsByCharID.pop(charID, None)

        for charID in newNaughtyChars:
            self.disapprovalFlagsByCharID[charID] = const.disapprovalTimerStateActive

        sm.ScatterEvent('OnDisapprovalUpdate', newNaughtyChars, noLongerNaughty)

    def OnWeaponsTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnWeaponsTimerUpdate', state, expiryTime)
        self.weaponsTimerState = state
        self.weaponsTimerExpiry = expiryTime

    def OnPvpTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnPvpTimerUpdate', state, expiryTime)
        self.pvpTimerState = state
        self.pvpTimerExpiry = expiryTime

    def OnNpcTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnNpcTimerUpdate', state, expiryTime)
        self.npcTimerState = state
        self.npcTimerExpiry = expiryTime

    def OnCriminalTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnCriminalTimerUpdate', state, expiryTime)
        self.criminalTimerState = state
        self.criminalTimerExpiry = expiryTime

    def OnDisapprovalTimerUpdate(self, state, expiryTime):
        self.LogInfo('OnDisapprovalTimerUpdate', state, expiryTime)
        self.disapprovalTimerState = state
        self.disapprovalTimerExpiry = expiryTime

    def OnSystemCriminalFlagUpdates(self, newIdles, newSuspects, newCriminals):
        self.LogInfo('OnSystemCriminalFlagUpdates', newIdles, newSuspects, newCriminals)
        self.UpdateSuspectsAndCriminals(newCriminals, newSuspects, newIdles)

    def OnSystemDisapprovalFlagUpdates(self, newIdles, newNaughyBoysAndGirls):
        self.LogInfo('OnSystemDisapprovalFlagUpdates', newIdles, newNaughyBoysAndGirls)
        self.UpdateDisapprovals(newNaughyBoysAndGirls, newIdles)

    def OnCrimewatchEngagementCreated(self, otherCharId, timeout):
        self.LogInfo('OnCrimewatchEngagementCreated', otherCharId, timeout)
        self.myEngagements[otherCharId] = timeout
        sm.ScatterEvent('OnCrimewatchEngagementUpdated', otherCharId, timeout)
        if self.duelWindow is not None and self.duelWindow.charID == otherCharId:
            self.duelWindow.Close()
            self.duelWindow = None

    def OnCrimewatchEngagementEnded(self, otherCharId):
        self.LogInfo('OnCrimewatchEngagementEnded', otherCharId)
        if otherCharId in self.myEngagements:
            del self.myEngagements[otherCharId]
        sm.ScatterEvent('OnCrimewatchEngagementUpdated', otherCharId, None)

    def OnCrimewatchEngagementStartTimeout(self, otherCharId, timeout):
        self.LogInfo('OnCrimewatchEngagementStartTimeout', otherCharId, timeout)
        self.myEngagements[otherCharId] = timeout
        sm.ScatterEvent('OnCrimewatchEngagementUpdated', otherCharId, timeout)

    def OnCrimewatchEngagementStopTimeout(self, otherCharId):
        self.LogInfo('OnCrimewatchEngagementStopTimeout', otherCharId)
        self.myEngagements[otherCharId] = const.crimewatchEngagementTimeoutOngoing
        sm.ScatterEvent('OnCrimewatchEngagementUpdated', otherCharId, const.crimewatchEngagementTimeoutOngoing)

    def GetMyEngagements(self):
        return self.myEngagements.copy()

    def GetMyBoosters(self):
        if not session.charid:
            return []
        myGodmaItem = sm.GetService('godma').GetItem(session.charid)
        if hasattr(myGodmaItem, 'boosters'):
            return myGodmaItem.boosters
        return []

    def GetBoosterEffects(self, booster):
        godma = sm.GetService('godma')
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        staticMgr = dogmaLocation.dogmaStaticMgr
        boosterEffectsNegative = []
        boosterEffectsPositive = []
        if booster:
            boosterEffects = staticMgr.GetPassiveFilteredEffectsByType(booster.boosterTypeID)
            for effectID in boosterEffects:
                eff = dogma.data.get_effect(effectID)
                chanceAttributeID = staticMgr.effects[effectID].fittingUsageChanceAttributeID
                if chanceAttributeID and effectID in booster.sideEffectIDs:
                    boosterEffectsNegative.append(eff)
                if not chanceAttributeID:
                    boosterEffectsPositive.append(eff)

        return {'negative': boosterEffectsNegative,
         'positive': boosterEffectsPositive}

    def GetWeaponsTimer(self):
        return (self.weaponsTimerState, self.weaponsTimerExpiry)

    def GetNpcTimer(self):
        return (self.npcTimerState, self.npcTimerExpiry)

    def GetPvpTimer(self):
        return (self.pvpTimerState, self.pvpTimerExpiry)

    def GetCriminalTimer(self):
        return (self.criminalTimerState, self.criminalTimerExpiry)

    def GetDisapprovalTimer(self):
        return (self.disapprovalTimerState, self.disapprovalTimerExpiry)

    def GetSafetyLevel(self):
        return self.safetyLevel

    def SetSafetyLevel(self, safetyLevel):
        eveMoniker.CharGetCrimewatchLocation().SetSafetyLevel(safetyLevel)
        self.safetyLevel = safetyLevel
        sm.ScatterEvent('OnSafetyLevelChanged', self.safetyLevel)

    def IsCriminal(self, charID):
        return self.criminalFlagsByCharID.get(charID) == const.criminalTimerStateActiveCriminal

    def IsSuspect(self, charID):
        return self.criminalFlagsByCharID.get(charID) == const.criminalTimerStateActiveSuspect

    def IsDisapproved(self, charID):
        return self.disapprovalFlagsByCharID.get(charID) == const.disapprovalTimerStateActive

    def IsCriminallyFlagged(self, charID):
        return charID in self.criminalFlagsByCharID

    def IsDisapprovalFlagged(self, charID):
        return charID in self.disapprovalFlagsByCharID

    def HasLimitedEngagmentWith(self, charID):
        return charID in self.myEngagements

    def HaveWeaponsTimer(self):
        return self.weaponsTimerState != const.weaponsTimerStateIdle

    def GetRequiredSafetyLevelForActivatingAccelerationGate(self, gateID):
        bp = self.michelle.GetBallpark()
        item = bp.GetInvItem(gateID)
        if item is None:
            return (const.shipSafetyLevelFull, None, None)
        if item.isFactionWarfareGate or item.isInsurgencyGate:
            if session.warfactionid is None:
                return (const.shipSafetyLevelPartial, 'DunGateNonFactionWarfareSafetyPreventsSuspect', None)
            sameFactionOrEnemy = IsCombatEnemyFaction(session.warfactionid, item.ownerID) or IsSameFwFaction(session.warfactionid, item.ownerID)
            if not sameFactionOrEnemy:
                return (const.shipSafetyLevelPartial, 'DunGateNonFactionWarfareSafetyPreventsSuspect', None)
        if item.dunKeyLock == const.dungeonKeySoftLockOwnerSuspect:
            gateOwnerID = item.dunOwnerLock
            if not gateOwnerID or item.dunOwnerLock == session.charid or sm.GetService('fleet').IsMember(item.dunOwnerLock):
                return (const.shipSafetyLevelFull, None, None)
            else:
                return (const.shipSafetyLevelPartial, 'DunGateFactionCampaignSuspectSiteSafetyPreventsSuspect', 'ConfirmActivateGateSuspect')
        return (const.shipSafetyLevelFull, None, None)

    def GetRequiredSafetyLevelForAssistanc(self, targetID):
        if self.IsCriminal(targetID):
            return const.shipSafetyLevelNone
        elif self.IsSuspect(targetID):
            return const.shipSafetyLevelPartial
        else:
            return const.shipSafetyLevelFull

    def GetSafetyLevelRestrictionForAttackingTarget(self, targetID, effect = None):
        securityClass = self.securitySvc.get_modified_security_class(session.solarsystemid)
        minSafetyLevel = const.shipSafetyLevelFull
        if securityClass > const.securityClassZeroSec:
            item = self.michelle.GetItem(targetID)
            if not item:
                if effect.rangeAttributeID is not None:
                    minSafetyLevel = const.shipSafetyLevelNone
            elif idCheckers.IsSystemOrNPC(item.ownerID):
                minSafetyLevel = self._GetMinimumSafetyLevelForNpc(item, securityClass)
            elif not self.CanAttackFreely(item):
                if securityClass == const.securityClassHighSec:
                    if not DoesConcordReact(sm.GetService('clientDogmaIM').GetDogmaLocation(), item.groupID, True):
                        minSafetyLevel = const.shipSafetyLevelPartial
                    else:
                        minSafetyLevel = const.shipSafetyLevelNone
                elif item.groupID == const.groupCapsule:
                    minSafetyLevel = const.shipSafetyLevelNone
                else:
                    minSafetyLevel = const.shipSafetyLevelPartial
        return minSafetyLevel

    def GetSafetyLevelRestrictionForAidingTarget(self, targetID):
        secClass = self.securitySvc.get_modified_security_class(session.solarsystemid)
        minSafetyLevel = const.shipSafetyLevelFull
        if secClass > const.securityClassZeroSec:
            item = self.michelle.GetItem(targetID)
            if item and item.ownerID != session.charid:
                if self.IsCriminallyFlagged(item.ownerID):
                    if self.IsCriminal(item.ownerID):
                        minSafetyLevel = const.shipSafetyLevelNone
                    elif self.IsSuspect(item.ownerID):
                        minSafetyLevel = const.shipSafetyLevelPartial
                else:
                    minSafetyLevel = const.shipSafetyLevelFull
        return minSafetyLevel

    def CanAttackFreely(self, item):
        if idCheckers.IsSystem(item.ownerID) or item.ownerID == session.charid:
            return True
        securityClass = self.securitySvc.get_modified_security_class(session.solarsystemid)
        if securityClass == const.securityClassZeroSec:
            return True
        if self.IsCriminallyFlagged(item.ownerID):
            return True
        if self.HasLimitedEngagmentWith(item.ownerID):
            return True
        if idCheckers.IsCharacter(item.ownerID) and eveCfg.IsOutlawStatus(item.securityStatus):
            return True
        if session.warfactionid:
            if hasattr(item, 'warFactionID') and facwarCommon.IsCombatEnemyFaction(item.warFactionID, session.warfactionid):
                return True
        belongToPlayerCorp = not IsNPC(session.corpid)
        if belongToPlayerCorp:
            if item.ownerID == session.corpid:
                if self.GetCorpAggressionSettings().IsFriendlyFireLegalAtTime(blue.os.GetWallclockTime()):
                    return True
            otherCorpID = getattr(item, 'corpID', None)
            if otherCorpID is not None:
                if otherCorpID == session.corpid:
                    if self.GetCorpAggressionSettings().IsFriendlyFireLegalAtTime(blue.os.GetWallclockTime()):
                        return True
                if self.war.GetRelationship(otherCorpID) == warConst.warRelationshipAtWarCanFight:
                    return True
            otherAllianceID = getattr(item, 'allianceID', None)
            if otherAllianceID is not None:
                if self.war.GetRelationship(otherAllianceID) == warConst.warRelationshipAtWarCanFight:
                    return True
        if IsItemFreeForAggression(item.groupID):
            return True
        return False

    def _GetActiveEffectsByItem(self, itemID):
        effectIDs = set()
        item = self.michelle.GetItem(itemID)
        if item is not None:
            for row in dogma.data.get_type_effects(item.typeID):
                effectID, isDefault = row.effectID, row.isDefault
                if isDefault:
                    effectIDs.add(effectID)

        return [ dogma.data.get_effect(effectID) for effectID in effectIDs ]

    def IsAnyEffectOffensive(self, itemIDs):
        for itemID in itemIDs:
            for effect in self._GetActiveEffectsByItem(itemID):
                if effect.isOffensive:
                    return True

        return False

    def GetRequiredSafetyLevelForEffect(self, effect, targetID = None):
        requiredSafetyLevel = const.shipSafetyLevelFull
        if effect is not None:
            if targetID is None and effect.effectCategory == const.dgmEffTarget:
                targetID = sm.GetService('target').GetActiveTargetID()
                if targetID is None:
                    return requiredSafetyLevel
            requiredSafetyLevel = const.shipSafetyLevelFull
            if effect.isOffensive:
                requiredSafetyLevel = self.GetSafetyLevelRestrictionForAttackingTarget(targetID, effect)
            elif effect.isAssistance:
                requiredSafetyLevel = self.GetSafetyLevelRestrictionForAidingTarget(targetID)
        return requiredSafetyLevel

    def CheckUnsafe(self, requiredSafetyLevel):
        if requiredSafetyLevel < self.safetyLevel:
            return True
        else:
            return False

    def SafetyActivated(self, requiredSafetyLevel):
        self.LogInfo('Safeties activated', self.safetyLevel, requiredSafetyLevel)
        sm.ScatterEvent('OnCrimewatchSafetyCheckFailed')

    def CheckCanTakeItems(self, containerID):
        if session.solarsystemid is None:
            return True
        bp = self.michelle.GetBallpark()
        if bp and not IsWormholeSystem(bp.solarsystemID) and self.GetSafetyLevel() == const.shipSafetyLevelFull:
            item = bp.GetInvItem(containerID)
            if item is not None:
                if item.groupID in containerGroupsWithLootRights:
                    bp = self.michelle.GetBallpark()
                    if bp and not bp.HaveLootRight(containerID):
                        return False
        return True

    def IsOkToScoopItem(self, itemID):
        securityClass = self.securitySvc.get_modified_security_class(session.solarsystemid)
        if securityClass == const.securityClassZeroSec:
            return True
        if self.GetSafetyLevel() != const.shipSafetyLevelFull:
            return True
        bp = self.michelle.GetBallpark()
        if not bp:
            return True
        item = bp.GetInvItem(itemID)
        if item is not None:
            if item.categoryID == categoryStructure and item.ownerID not in (session.charid, session.corpid):
                return False
        return True

    def GetRequiredSafetyLevelForEngagingDrones(self, droneIDs, targetID):
        safetyLevel = const.shipSafetyLevelFull
        if targetID is not None:
            effects = []
            for droneID in droneIDs:
                effects += self._GetActiveEffectsByItem(droneID)

            if effects:
                safetyLevels = [ self.GetRequiredSafetyLevelForEffect(effect, targetID) for effect in effects ]
                safetyLevel = min(safetyLevels)
        return safetyLevel

    def OnDuelChallenge(self, fromCharID, fromCorpID, fromAllianceID, expiryTime):
        self.LogInfo('OnDuelChallenge', fromCharID, fromCorpID, fromAllianceID, expiryTime)
        wnd = DuelInviteWindow(charID=fromCharID, corpID=fromCorpID, allianceID=fromAllianceID)
        try:
            self.duelWindow = wnd
            wnd.StartTimeout(expiryTime)
            result = wnd.ShowDialog(modal=False)
            accept = None
            if 'accept' in wnd.result:
                accept = True
            elif 'decline' in wnd.result:
                accept = False
            if 'block' in wnd.result:
                uthread.new(sm.GetService('addressbook').BlockOwner, fromCharID)
            if accept is not None:
                eveMoniker.CharGetCrimewatchLocation().RespondToDuelChallenge(fromCharID, expiryTime, accept)
        finally:
            self.duelWindow = None

    def StartDuel(self, charID):
        if charID in self.myEngagements:
            self.LogInfo('The char', charID, 'is already in limited engagement with us. No duel request sent.')
        else:
            eveMoniker.CharGetCrimewatchLocation().StartDuelChallenge(charID)

    def GetMySecurityStatus(self):
        if self.mySecurityStatus is None:
            self.mySecurityStatus = eveMoniker.CharGetCrimewatchLocation().GetMySecurityStatus()
        return self.mySecurityStatus

    def GetCharacterSecurityStatus(self, charID):
        return eveMoniker.CharGetCrimewatchLocation().GetCharacterSecurityStatus(charID)

    def OnSecurityStatusUpdate(self, newSecurityStatus):
        self.mySecurityStatus = newSecurityStatus

    def GetSecurityStatusTransactions(self):
        return eveMoniker.CharGetCrimewatchLocation().GetSecurityStatusTransactions()

    def GetJumpTimers(self):
        if self.jumpTimers is None:
            self.jumpTimers = sm.RemoteSvc('jumpTimers').GetTimers(session.charid)
        return self.jumpTimers

    def OnJumpTimersUpdated(self, *args):
        self.jumpTimers = args

    def RefreshCorpAggressionSettings(self):
        self.corpAggressionSettings = self.corp.GetCorpRegistry().GetAggressionSettings()

    def GetCorpAggressionSettings(self):
        if self.corpAggressionSettings is None:
            self.RefreshCorpAggressionSettings()
        return self.corpAggressionSettings

    def OnCorpAggressionSettingsChange(self, aggressionSettings):
        self.corpAggressionSettings = aggressionSettings

    def _GetMinimumSafetyLevelForNpc(self, item, securityClass):
        if item.ownerID == const.ownerCONCORD:
            return const.shipSafetyLevelNone
        if item.groupID in const.illegalTargetNpcOwnedGroups:
            if securityClass == const.securityClassHighSec:
                return const.shipSafetyLevelNone
            else:
                return const.shipSafetyLevelPartial
        elif HasEnforceCriminalFlagComponent(item.typeID):
            if has_enforce_criminal_flag(item.typeID):
                return const.shipSafetyLevelNone
            if has_enforce_suspect_flag(item.typeID):
                return const.shipSafetyLevelPartial
        return const.shipSafetyLevelFull

    def GetSecurityWhereAttacked(self):
        characterSecurity = sm.GetService('crimewatchSvc').GetMySecurityStatus()
        if characterSecurity <= -4.5:
            return 0.5
        if characterSecurity <= -4.0:
            return 0.6
        if characterSecurity <= -3.5:
            return 0.7
        if characterSecurity <= -3.0:
            return 0.8
        if characterSecurity <= -2.5:
            return 0.9
        if characterSecurity <= -2.0:
            return 1.0
