#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\achievements\client\eventHandler.py
import collections
import weakref
import uthread2
from achievements.common.achievementConst import AchievementEventConst as eventConst
from achievements.common.eventHandlerUtil import ListContainsTypeInGivenGroups
from agency.common.content_types import CONTENTTYPE_RESOURCEWARS, CONTENTTYPE_CAREERAGENTS
from eve.client.script.environment import invControllers
from eve.common.script.sys.idCheckers import IsStation, IsFakeItem, IsNPC, IsShip
import inventorycommon.const as invConst
import operations
from npcs.client.entitystandings import get_standing_between_npc_and_player
from operations.client.operationscontroller import GetOperationsController
from spacecomponents.common.helper import HasEntityStandingsComponent

class EventHandler(object):
    __notifyevents__ = ['OnClientEvent_LockItem',
     'OnClientEvent_MoveTowardsPointExecuted',
     'OnClientEvent_OrbitCommand',
     'OnClientEvent_MoveFromCargoToHangar',
     'OnClientEvent_ActivateModule',
     'OnClientEvent_ApproachCommand',
     'OnClientEvent_SelectSpaceBracket',
     'OnClientEvent_ChatMessageSent',
     'OnClientEvent_OpenMap',
     'OnClientEvent_DestinationSet',
     'OnAutoPilotOn',
     'OnClientEvent_JumpToNextSystemInRouteCmdExecuted',
     'OnClientEvent_JumpedToNextSystemInRoute',
     'OnClientMouseZoomInSpace',
     'OnClientMouseZoomOutSpace',
     'OnClientMouseSpinInSpace',
     'OnModuleUnfitted',
     'OnCameraLookAt',
     'OnClientEvent_OpenCorpFinder',
     'OnClientEvent_BlueprintLoaded',
     'OnProbeAdded',
     'OnClientEvent_PerfectScanResultReached',
     'OnBookmarkCreated',
     'OnAutoPilotJump',
     'OnWindowOpened',
     'OnWindowClosed',
     'OnWindowMinimized',
     'OnInventoryContainerShown',
     'OnClientEvent_OrderPlaced',
     'OnClientEvent_OperationDestinationSet',
     'OnClientEvent_CrateOpen',
     'OnClientEvent_SkillPrioritized',
     'OnClientEvent_SkillAddedToQueue',
     'OnClientEvent_AgencyContentExpanded',
     'OnClientEvent_AgencyContentGroupExpanded',
     'OnClientEvent_ClaimRewardsButtonClicked',
     'OnClientEvent_ConversationContinueButtonClicked',
     'OnRWDungeonLobbyEntered',
     'OnMultipleItemChange',
     'OnWarpToAsteroidBelt',
     'OnSessionChanged',
     'OnDogmaAttributeChanged',
     'OnHighSlotFittingChanged',
     'OnClientEvent_DockCmdExecuted',
     'OnOperationSiteWarpToExecuted',
     'OnOpenCargoExecuted',
     'ProcessSessionReset',
     'OnSessionReset']

    def __init__(self, achievementSvc):
        sm.RegisterNotify(self)
        self.achievementSvc = weakref.proxy(achievementSvc)

    def ProcessSessionReset(self):
        self.UnregisterForEvents()

    def OnSessionReset(self):
        sm.RegisterNotify(self)

    def LogAchievementEvent(self, eventType, amount = 1):
        self.achievementSvc.LogClientEvent(eventType, amount)

    def OnClientEvent_LockItem(self, slimItem):
        self.NotifyOperationsServiceIfInteresting(eventConst.LOCK_TARGET_CLIENT, slimItem)
        if slimItem.categoryID == const.categoryAsteroid:
            self.LogAchievementEvent(eventConst.ASTEROIDS_LOCK_CLIENT)
        elif self.IsHostileNPC(slimItem):
            self.LogAchievementEvent(eventConst.HOSTILE_NPC_LOCK_CLIENT)

    def OnClientEvent_MoveTowardsPointExecuted(self, *args):
        self.NotifyOperationsServiceIfInteresting(eventConst.DOUBLE_CLICK_COUNT_CLIENT)
        self.LogAchievementEvent(eventConst.DOUBLE_CLICK_COUNT_CLIENT)

    def NotifyOperationsServiceIfInteresting(self, event_type, slimItem = None, extraData = None, amount = 1):
        if not operations.client.util.are_operations_active():
            return
        if GetOperationsController().is_client_event_interesting(event_type):
            if extraData is None:
                extraData = {}
            if slimItem is not None:
                extraData['typeID'] = slimItem.typeID
                extraData['objectID'] = slimItem.dunObjectID
            sm.RemoteSvc('operationsManager').process_client_event(event_type, extra_data=extraData, amount=amount)

    def NotifySeasonServiceIfInteresting(self, event_type, itemID, slimItem = None, extraData = None, amount = 1):
        if not sm.GetService('seasonService').is_season_active():
            return
        if sm.GetService('seasonService').is_client_event_interesting(event_type):
            if extraData is None:
                extraData = {}
            extraData['typeID'] = sm.GetService('michelle').GetItem(itemID).typeID
            sm.RemoteSvc('seasonManager').process_client_event(event_type, extra_data=extraData, amount=amount)

    def OnClientEvent_OrbitCommand(self, targetID, distance, slimItem):
        self.NotifyOperationsServiceIfInteresting(eventConst.ORBIT_CLIENT, slimItem)
        if slimItem.categoryID == const.categoryAsteroid:
            self.LogAchievementEvent(eventConst.ASTEROIDS_ORBIT_CLIENT)
        elif self.IsHostileNPC(slimItem):
            self.LogAchievementEvent(eventConst.HOSTILE_NPC_ORBIT_CLIENT)

    def _Operation_ClientEvent_Approach(self, event_type, slimItem = None):
        self.NotifyOperationsServiceIfInteresting(event_type, slimItem)

    def OnClientEvent_SelectSpaceBracket(self, slimItem):
        self.NotifyOperationsServiceIfInteresting(eventConst.SELECT_SPACE_BRACKET_CLIENT, slimItem=slimItem)

    def OnClientEvent_ApproachCommand(self, slimItem = None):
        event_type = eventConst.APPROACH_CLIENT
        self.NotifyOperationsServiceIfInteresting(event_type)
        self.LogAchievementEvent(event_type)
        self._Operation_ClientEvent_Approach(event_type, slimItem)

    def OnClientEvent_DockCmdExecuted(self, locationID):
        self.NotifyOperationsServiceIfInteresting(eventConst.TRAVEL_DOCK_EXECUTED_CLIENT)

    def OnOpenCargoExecuted(self, slimItem):
        self.NotifyOperationsServiceIfInteresting(eventConst.OPEN_CARGO_EXECUTED_CLIENT, slimItem=slimItem)

    def _CheckTotalItemQuantityInCargoAndHangar(self, items):
        if not items:
            return
        tasks = GetOperationsController().get_active_inventory_manipulation_tasks()
        if not tasks:
            return
        task = tasks[0]
        relevant_types = task.get_event_conditions('typeID')
        if not relevant_types:
            return
        for item in items:
            if item.typeID not in relevant_types:
                continue
            inv_controllers = task.get_event_conditions('inventoryController')
            for inv_id in inv_controllers:
                quantity_by_type_id = self._get_quantity_by_type_id(relevant_types, inv_id)
                total_quantity = sum(quantity_by_type_id.values())
                if total_quantity >= task.targetValue:
                    for type_id, amount in quantity_by_type_id.iteritems():
                        self.NotifyOperationsServiceIfInteresting(eventConst.CLIENT_ITEM_IN_MOVED_TO, extraData={'typeID': type_id,
                         'inventoryController': inv_id}, amount=amount)

    def _get_quantity_by_type_id(self, relevant_types, inv_id):
        type_count = collections.defaultdict(int)
        invCtrl = invControllers.GetInvCtrlFromInvID((inv_id,))
        for type_id in relevant_types:
            if not invCtrl or not invCtrl.IsInRange():
                continue
            type_count[type_id] += sum([ item.quantity for item in invCtrl.GetItemsByType(type_id) ])

        return type_count

    def OnMultipleItemChange(self, items, change):
        item = items[0]
        if item.ownerID != session.charid:
            return
        if item.locationID not in (session.shipid, session.stationid):
            return
        if GetOperationsController().get_active_operation_id() is None:
            return
        self._CheckTotalItemQuantityInCargoAndHangar(items)

    def OnClientEvent_MoveFromCargoToHangar(self, sourceID, destinationID, destinationFlag = None):
        if IsFakeItem(sourceID):
            self.LogAchievementEvent(eventConst.ITEMS_LOOT_CLIENT)
            return
        if session.stationid:
            sourceLocationItem = sm.GetService('invCache').FetchItem(sourceID, session.stationid)
            if not sourceLocationItem:
                return
            if sourceLocationItem.categoryID == const.categoryShip and (IsStation(destinationID) or destinationFlag == const.flagHangar):
                self.LogAchievementEvent(eventConst.ITEMS_MOVE_FROM_CARGO_TO_HANGAR_CLIENT)

    def OnClientEvent_ActivateModule(self, effectID):
        if effectID in (const.effectProjectileFired, const.effectTargetAttack):
            self.LogAchievementEvent(eventConst.ACTIVATE_GUN_CLIENT)
        elif effectID == const.effectSalvaging:
            self.LogAchievementEvent(eventConst.ACTIVATE_SALVAGER_CLIENT)

    def OnClientEvent_ChatMessageSent(self):
        self.NotifyOperationsServiceIfInteresting(eventConst.SOCIAL_CHAT_MESSAGE_SENT)
        self.LogAchievementEvent(eventConst.SOCIAL_CHAT_MESSAGE_SENT)

    def OnClientEvent_OpenMap(self):
        self.LogAchievementEvent(eventConst.UI_OPEN_MAP_CLIENT)

    def OnClientEvent_DestinationSet(self, destinationID):
        if destinationID == sm.GetService('agents').GetMySuggestetCareerAgentStation():
            self.NotifyOperationsServiceIfInteresting(eventConst.TRAVEL_SET_DESTINATION_TO_CAREER_AGENTS)
        self.NotifyOperationsServiceIfInteresting(eventConst.TRAVEL_SET_DESTINATION_CLIENT)
        self.LogAchievementEvent(eventConst.TRAVEL_SET_DESTINATION_CLIENT)
        self.NotifyOperationsServiceIfInteresting(eventConst.END_INCEPTION_NAVIGATION)

    def OnAutoPilotOn(self, *args):
        self.LogAchievementEvent(eventConst.TRAVEL_ACTIVATE_AUTOPILOT_CLIENT)

    def OnAutoPilotJump(self, *args):
        self.LogAchievementEvent(eventConst.TRAVEL_JUMP_TO_NEXT_SYSTEM_CLIENT)

    def OnClientEvent_JumpToNextSystemInRouteCmdExecuted(self, *args):
        self.LogAchievementEvent(eventConst.TRAVEL_JUMP_TO_NEXT_SYSTEM_EXECUTED_CLIENT)
        self.NotifyOperationsServiceIfInteresting(eventConst.TRAVEL_JUMP_TO_NEXT_SYSTEM_EXECUTED_CLIENT)

    def OnClientEvent_JumpedToNextSystemInRoute(self):
        self.LogAchievementEvent(eventConst.TRAVEL_JUMP_TO_NEXT_SYSTEM_CLIENT)

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid2' in change:
            fromSolarSystemID, toSolarSystemID = change['solarsystemid2']
            if fromSolarSystemID != toSolarSystemID and sm.GetService('agents').IsCareerAgentSystem(toSolarSystemID):
                self.NotifyOperationsServiceIfInteresting(eventConst.TRAVEL_CAREER_AGENT_SYSTEM_ENTERED)
        if 'shipid' in change:
            oldShipID, newShipID = change['shipid']
            if newShipID is not None:
                self.OnHighSlotFittingChanged()

    def OnWarpToAsteroidBelt(self):
        self.NotifyOperationsServiceIfInteresting(eventConst.TRAVEL_ENTER_ASTEROID_BELT)

    def OnClientMouseZoomInSpace(self, amount):
        uthread2.Sleep(1.0)
        self.NotifyOperationsServiceIfInteresting(eventConst.UI_MOUSEZOOM_IN_CLIENT)
        self.LogAchievementEvent(eventConst.UI_MOUSEZOOM_IN_CLIENT)

    def OnClientMouseZoomOutSpace(self, amount):
        uthread2.Sleep(1.0)
        self.NotifyOperationsServiceIfInteresting(eventConst.UI_MOUSEZOOM_OUT_CLIENT)
        self.LogAchievementEvent(eventConst.UI_MOUSEZOOM_OUT_CLIENT)

    def OnClientMouseSpinInSpace(self):
        uthread2.Sleep(1.0)
        self.NotifyOperationsServiceIfInteresting(eventConst.UI_MOUSE_ROTATE_CLIENT)
        self.LogAchievementEvent(eventConst.UI_MOUSE_ROTATE_CLIENT)

    def OnModuleUnfitted(self, typeID):
        self.NotifyOperationsServiceIfInteresting(eventConst.FITTING_UNFIT_MODULE_CLIENT, extraData=dict(typeID=typeID))
        self.LogAchievementEvent(eventConst.FITTING_UNFIT_MODULE_CLIENT)

    def OnClientEvent_OrderPlaced(self, typeIDs):
        for typeID in typeIDs:
            self.NotifyOperationsServiceIfInteresting(eventConst.MARKET_ORDER_PLACED_CLIENT, extraData=dict(typeID=typeID))

    def OnCameraLookAt(self, isEgo, itemID):
        if session.charid is None:
            return
        if isEgo:
            self.NotifyOperationsServiceIfInteresting(eventConst.LOOK_AT_OWN_SHIP)
            self.LogAchievementEvent(eventConst.LOOK_AT_OWN_SHIP)
        elif itemID is not None:
            self.NotifyOperationsServiceIfInteresting(eventConst.LOOK_AT_OBJECT)
            self.NotifySeasonServiceIfInteresting(eventConst.LOOK_AT_OBJECT, itemID)
            self.LogAchievementEvent(eventConst.LOOK_AT_OBJECT)

    def UnregisterForEvents(self):
        sm.UnregisterNotify(self)

    def IsHostileNPC(self, slimItem):
        if not IsNPC(slimItem.ownerID):
            return False
        if not HasEntityStandingsComponent(slimItem.typeID):
            return False
        standings = get_standing_between_npc_and_player(slimItem.ownerID, session.charid)
        return standings < slimItem.hostile_response_threshold

    def OnClientEvent_OpenCorpFinder(self):
        self.LogAchievementEvent(eventConst.OPEN_CORP_FINDER)

    def OnClientEvent_BlueprintLoaded(self, blueprintTypeID):
        self.NotifyOperationsServiceIfInteresting(eventConst.INDUSTRY_LOAD_BLUEPRINT, extraData=dict(blueprintTypeID=blueprintTypeID))
        self.LogAchievementEvent(eventConst.INDUSTRY_LOAD_BLUEPRINT)

    def OnProbeAdded(self, probe):
        self.LogAchievementEvent(eventConst.LAUNCH_PROBES)

    def OnClientEvent_PerfectScanResultReached(self, results):
        self.LogAchievementEvent(eventConst.REACH_PERFECT_SCAN_RESULTS)

    def OnClientEvent_OperationDestinationSet(self, operationSiteID):
        extraData = {'operationSiteID': operationSiteID}
        self.NotifyOperationsServiceIfInteresting(eventConst.OPERATION_DESTINATION_SET_CLIENT, extraData=extraData)

    def OnClientEvent_CrateOpen(self, crateTypeID):
        extraData = {'typeID': crateTypeID}
        self.NotifyOperationsServiceIfInteresting(eventConst.CRATE_OPENED_CLIENT, extraData=extraData)

    def OnClientEvent_SkillPrioritized(self, skillTypeID):
        extraData = {'typeID': skillTypeID}
        self.NotifyOperationsServiceIfInteresting(eventConst.SKILL_PRIORITIZED_CLIENT, extraData=extraData)

    def OnClientEvent_SkillAddedToQueue(self, skillTypeID, skillLevel):
        extraData = {'typeID': skillTypeID,
         'skillLevel': skillLevel}
        self.NotifyOperationsServiceIfInteresting(eventConst.SKILL_ADDED_TO_QUEUE_CLIENT, extraData=extraData)

    def OnBookmarkCreated(self, bookmarkID, comment, typeID = None):
        if typeID and ListContainsTypeInGivenGroups([typeID], [invConst.groupWormhole]):
            self.LogAchievementEvent(eventConst.CREATE_WORMHOLE_BOOKMARK)

    def OnWindowOpened(self, window):
        extraData = {'windowID': window.windowID}
        self.NotifyOperationsServiceIfInteresting(eventConst.WINDOW_OPENED, extraData=extraData)
        self.NotifyOperationsServiceIfInteresting(eventConst.WINDOW_OPENED_WITH_NAME_LIKE, extraData=extraData)

    def OnWindowClosed(self, windowID, *args):
        extraData = dict(windowID=windowID)
        self.NotifyOperationsServiceIfInteresting(eventConst.WINDOW_CLOSED, extraData=extraData)
        self.NotifyOperationsServiceIfInteresting(eventConst.WINDOW_CLOSED_OR_MINIMIZED, extraData=extraData)

    def OnWindowMinimized(self, window, *args):
        self.NotifyOperationsServiceIfInteresting(eventConst.WINDOW_CLOSED_OR_MINIMIZED, extraData=dict(windowID=window.windowID))

    def OnInventoryContainerShown(self, invID, _previousInvID):
        tabID, locationID = invID[0], invID[1]
        self.NotifyOperationsServiceIfInteresting(eventConst.INVENTORY_CONTAINER_SHOWN, extraData=dict(tabID=tabID, locationID=locationID))

    def OnClientEvent_AgencyContentExpanded(self, contentPiece):
        extraData = {'contentTypeID': contentPiece.GetContentTypeID() or 0,
         'contentPieceType': contentPiece.contentType or 0}
        self.NotifyOperationsServiceIfInteresting(eventConst.AGENCY_CONTENT_EXPANDED, extraData=extraData)

    def OnClientEvent_AgencyContentGroupExpanded(self, contentGroupID):
        extraData = {'contentGroupID': contentGroupID}
        self.NotifyOperationsServiceIfInteresting(eventConst.AGENCY_CONTENT_GROUP_EXPANDED, extraData=extraData)

    def OnClientEvent_ClaimRewardsButtonClicked(self):
        self.NotifyOperationsServiceIfInteresting(eventConst.CLIENT_CLAIM_REWARDS_BTN_CLICK)

    def OnRWDungeonLobbyEntered(self, siteData, secondsRemaining):
        self.NotifyOperationsServiceIfInteresting(eventConst.END_INCEPTION_NAVIGATION)

    def OnClientEvent_ConversationContinueButtonClicked(self, conversation_id):
        self.NotifyOperationsServiceIfInteresting(eventConst.TASK_CONTINUE_BUTTON_PRESSED)

    def OnOperationSiteWarpToExecuted(self, siteID):
        extraData = {'operationSiteID': siteID}
        self.NotifyOperationsServiceIfInteresting(eventConst.TRAVEL_OPERATION_SITE_WARP_TO_EXECUTED_CLIENT, extraData=extraData)

    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if shipID != session.shipid:
            return
        extraData = {'dogmaAttributeID': attributeID,
         'dogmaAttributeValue': value}
        self.NotifyOperationsServiceIfInteresting(eventConst.SHIP_DOGMA_ATTRIBUTE_CHANGED, extraData=extraData)

    def OnHighSlotFittingChanged(self):
        shipID = session.shipid
        if shipID:
            shipItem = sm.GetService('godma').GetItem(shipID)
            if shipItem:
                shipItemCategoryID = shipItem.categoryID
                if IsShip(shipItemCategoryID):
                    shipInventory = sm.GetService('invCache').GetInventoryFromId(shipID)
                    numberOfFreeSlots = shipInventory.GetAvailableTurretSlots()
                    if numberOfFreeSlots >= 2:
                        self.NotifyOperationsServiceIfInteresting(eventConst.TWO_TURRETS_FREED)
