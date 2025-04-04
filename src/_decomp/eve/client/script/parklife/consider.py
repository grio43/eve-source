#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\consider.py
import dogma.data
import uthread
import carbonui.const as uiconst
import telemetry
import inventorycommon.typeHelpers
from carbon.common.script.sys.service import Service
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from npcs.client.entitystandings import is_npc_hostile, is_npc_hostile_towards_player

class ConsiderSvc(Service):
    __guid__ = 'svc.consider'
    __exportedcalls__ = {'ConfirmTakeIllicitGoods': []}
    __notifyevents__ = ['ProcessSessionChange',
     'DoBallRemove',
     'DoBallClear',
     'DoBallsRemove']
    __dependencies__ = ['michelle', 'crimewatchSvc']

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.confirmationCache = {}
        self.pendingConfirmations = {}
        self.containerTakeRights = {}

    def ProcessSessionChange(self, isRemote, session, change):
        if change.has_key('solarsystemid'):
            self.confirmationCache.clear()
            self.pendingConfirmations.clear()
            self.containerTakeRights.clear()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball:
            itemID = ball.id
        elif slimItem:
            itemID = slimItem.itemID
        else:
            return
        if itemID in self.confirmationCache:
            self.LogInfo('DoBallRemove::consider removing item', itemID)
            del self.confirmationCache[itemID]

    def DoBallClear(self, solitem):
        self.confirmationCache.clear()

    def ShowNPCAtttackConfirmationWindowIfAppropriate(self, requiredSafetyLevel, targetID):
        item = self.michelle.GetItem(targetID)
        if item and idCheckers.IsNPC(item.ownerID) and item.ownerID not in const.legalOffensiveTargetOwnerIDs:
            if not is_npc_hostile(item.hostile_response_threshold) and not is_npc_hostile_towards_player(item, session.charid):
                if not self.TypeHasAttribute(item.typeID, const.attributeEntitySecurityStatusKillBonus):
                    if item.groupID not in [const.groupLargeCollidableObject,
                     const.groupControlBunker,
                     const.groupWormhole,
                     const.groupStructurePirateForwardOperatingBase]:
                        if not self.ConfirmationRequest(targetID, 'AttackGoodNPCAbort1', targetID):
                            return False
        return True

    def SafetyCheckPasses(self, requiredSafetyLevel):
        if self.crimewatchSvc.CheckUnsafe(requiredSafetyLevel):
            self.crimewatchSvc.SafetyActivated(requiredSafetyLevel)
            return False
        return True

    def DoAttackConfirmations(self, targetID, effect = None):
        requiredSafetyLevel = self.crimewatchSvc.GetSafetyLevelRestrictionForAttackingTarget(targetID, effect=effect)
        if not self.SafetyCheckPasses(requiredSafetyLevel):
            return False
        return self.ShowNPCAtttackConfirmationWindowIfAppropriate(requiredSafetyLevel, targetID)

    def ConfirmationRequest(self, targetID, msgName, actualTargetID):
        if self.HasConfirmation(targetID, msgName):
            return 1
        item = self.michelle.GetItem(actualTargetID)
        targetName = 'your target'
        if item is not None:
            targetName = uix.GetSlimItemName(item)
        k = (targetID, msgName)
        if self.pendingConfirmations.has_key(k):
            return self.pendingConfirmations[k].receive()
        result = 0
        self.pendingConfirmations[k] = uthread.Channel(('consider::ConfirmationRequest', k))
        try:
            ret = eve.Message(msgName, {'target': targetName}, uiconst.YESNO, suppress=uiconst.ID_YES, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                result = 0
                return 0
            self.RememberConfirmation(targetID, msgName)
            result = 1
        finally:
            if self.pendingConfirmations.has_key(k):
                while self.pendingConfirmations[k].queue:
                    self.pendingConfirmations[k].send(result)

                del self.pendingConfirmations[k]

        return result

    def RememberConfirmation(self, targetID, msgName):
        if not self.confirmationCache.has_key(targetID):
            self.confirmationCache[targetID] = []
        self.confirmationCache[targetID].append(msgName)

    def HasConfirmation(self, targetID, msgName):
        return self.confirmationCache.has_key(targetID) and msgName in self.confirmationCache[targetID]

    def TypeHasAttribute(self, typeID, attributeID):
        for typeAttribute in dogma.data.get_type_attributes(typeID):
            if typeAttribute.attributeID == attributeID:
                return 1

        return 0

    def ConfirmTakeIllicitGoods(self, items):
        if not session.solarsystemid:
            return True
        if sm.GetService('map').GetSecurityClass(eve.session.solarsystemid2) == const.securityClassZeroSec:
            return True
        toFactionID = sm.GetService('faction').GetFactionOfSolarSystem(session.solarsystemid)
        for item in items:
            illegality = inventorycommon.typeHelpers.GetIllegalityInFaction(item.typeID, toFactionID)
            if illegality:
                return eve.Message('ConfirmTakeIllicitGoods', {'faction': cfg.eveowners.Get(toFactionID).name}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES

        return True
