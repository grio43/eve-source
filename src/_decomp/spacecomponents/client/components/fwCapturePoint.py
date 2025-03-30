#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\fwCapturePoint.py
import evetypes
import uthread2
from battleground_capture_point_ui.client.capture_Point_ui import CapturePointUI
from eve.common.script.sys.idCheckers import IsNPC
from eve.common.script.util.facwarCommon import IsSameFwFaction, IsOccupierFWFaction, IsOccupierEnemyFaction
from spacecomponents import Component
from spacecomponents.client import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE

class FWCapturePoint(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self._on_added_to_space)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self._on_removed_from_space)
        self._ui_bracket = None
        self.attackerID = None
        self.occupierID = None
        self.fwSvc = sm.GetService('facwar')
        self.slimItem = None

    def _on_added_to_space(self, slimItem):
        self._ui_bracket = CapturePointUI(self.itemID)
        self.OnSlimItemUpdated(slimItem)
        self.run_proximity_loop = True
        uthread2.start_tasklet(self.proximity_loop)

    def _on_removed_from_space(self):
        self.run_proximity_loop = False
        if self._ui_bracket is not None:
            self._ui_bracket.remove_from_space()

    def OnSlimItemUpdated(self, slimItem):
        self.slimItem = slimItem
        self._UpdateSlimItemComponentState()

    def _UpdateSlimItemComponentState(self):
        if self.slimItem.component_fwCapturePoint_factionInfo is not None:
            self.attackerID, self.occupierID = self.slimItem.component_fwCapturePoint_factionInfo
            self._ui_bracket.attackerId = self.attackerID
            self._ui_bracket.defenderId = self.occupierID
        if self.slimItem.component_fwCapturePoint_nextPointTime is not None:
            self._ui_bracket.set_next_tick_time(self.slimItem.component_fwCapturePoint_nextPointTime, self.attributes.numberOfSeconds)

    def proximity_loop(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        currentState = CapturePointUI.EMPTY
        self._ui_bracket.set_state(60, 60, 500003, currentState)
        while self.run_proximity_loop:
            if not self.occupierID or not self.attackerID:
                uthread2.sleep_sim(1)
                continue
            newState, ownership = self.GetState(ballpark, session.charid)
            if newState != currentState:
                self._ui_bracket.set_state(60, 60, ownership, newState)
                currentState = newState
            uthread2.sleep_sim(1)

    def _IsShipPiloted(self, slimItem):
        if slimItem.charID:
            return True
        else:
            return False

    def GetState(self, ballpark, charID):
        blockingForces = set()
        capturingForces = set()
        items = ballpark.GetBallsInRange(self.itemID, self.attributes.range)
        for itemId in items:
            if itemId in ballpark.slimItems:
                slimItem = ballpark.slimItems[itemId]
                typeID = slimItem.typeID
                capturingTypeList = evetypes.GetTypeIDsByListID(self.attributes.capturingTypeListID)
                blockingTypeList = evetypes.GetTypeIDsByListID(self.attributes.blockingTypeListID)
                if typeID in capturingTypeList:
                    militiaFaction = slimItem.warFactionID
                    piloted = self._IsShipPiloted(slimItem)
                    if IsOccupierFWFaction(militiaFaction) and piloted:
                        capturingForces.add(militiaFaction)
                elif typeID in blockingTypeList:
                    npcFactionID = self._GetBlockingItemFactionID(slimItem)
                    blockingForces.add(npcFactionID)

        capturePointFactionID = self.occupierID
        currentHolders = None
        for factionID in capturingForces:
            if currentHolders is None:
                if IsSameFwFaction(capturePointFactionID, factionID):
                    currentHolders = capturePointFactionID
                elif IsOccupierEnemyFaction(capturePointFactionID, factionID):
                    currentHolders = self.attackerID
            elif IsOccupierEnemyFaction(currentHolders, factionID):
                return (CapturePointUI.CONTESTED, currentHolders)

        if currentHolders is None:
            return (CapturePointUI.EMPTY, None)
        for factionID in blockingForces:
            if IsOccupierEnemyFaction(currentHolders, factionID):
                return (CapturePointUI.CONTESTED, currentHolders)

        return (CapturePointUI.UNCONTESTED, currentHolders)

    def _GetBlockingItemFactionID(self, slimItem):
        ownerID = slimItem.ownerID
        if IsNPC(ownerID):
            return ownerID
        else:
            return slimItem.warFactionID
