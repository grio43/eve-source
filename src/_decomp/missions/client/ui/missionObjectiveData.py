#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\missions\client\ui\missionObjectiveData.py
import eveformat.client
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.client.script.ui.const import buttonConst
from eve.client.script.util.clientPathfinderService import ConvertStationIDToSolarSystemIDIfNecessary
from eve.common.script.sys.eveCfg import IsControllingStructure
from eveservices.menu import GetMenuService
from evetypes import GetCategoryID, GetName, GetGroupNameByGroup
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import ApproachLocation, IsApproachingBall
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToBookmark
from eve.client.script.ui.shared.infoPanels.infoPanelMissionObjective import MissionObjective
from eve.common.lib.appConst import minWarpDistance, typeSolarSystem
from eve.common.script.sys.idCheckers import IsStation, IsSolarSystem, IsOwner
from eve.common.script.util.notificationUtil import CreateLocationInfoLink, CreateTypeInfoLink
from inventorycommon.const import categoryCelestial, typeAccelerationGate
from localization import GetByLabel, GetByMessageID
import logging
from missions.common.missionTriggerTypeNames import NAME_BY_TRIGGER_TYPE
from menucheckers import BookmarkChecker
logger = logging.getLogger('missionObjectiveData')
AGENT_LOCATION_TYPES = ['agenthomebase']
ORIGIN_LOCATION_TYPES = ['objective', 'objective.source']
DROP_OFF_LOCATION_TYPES = ['objective.destination']
DUNGEON_LOCATION_TYPES = ['dungeon']
TALK_TO_AGENT_LOCATION_TYPES = ['objective']
START_CONVERSATION_LABEL_PATH = 'UI/Commands/StartConversation'
READ_DETAILS_LABEL_PATH = 'UI/Agents/Commands/ReadDetails'
START_CONVERSATION_ICON_PATH = 'res:/UI/Texture/Shared/actions/startConversation.png'
READ_DETAILS_ICON_PATH = 'res:/UI/Texture/Icons/38_16_190.png'
DUNGEON_DISTANCE_THRESHOLD = 500000

def ReadDetails(agentID, *args):
    sm.GetService('agents').PopupMission(agentID)


def TalkToAgent(agentID, *args):
    sm.GetService('agents').OpenDialogueWindow(agentID)


class AgentMissionObjective(MissionObjective):
    SHOW_START_CONVERSATION = False
    SHOW_READ_DETAILS = False
    BOOKMARK_LOCATION_TYPES = []

    def __init__(self, iconItemID = None, iconTypeID = None, missionHint = None, agentID = None, bookmarks = None, header = None, activeIcon = None):
        super(AgentMissionObjective, self).__init__(iconItemID, iconTypeID, missionHint, activeIcon)
        self._michelle = None
        self.agentID = agentID
        self.bookmarks = bookmarks
        self.header = header
        self.isLocationSet = False
        self.locationText, self.locationCallback, self.locationIcon = (None, None, None)
        self.isBookmarkSet = False
        self._bookmark = None

    @property
    def bookmark(self):
        if not self.isBookmarkSet:
            self._bookmark = self.FindBookmark()
            self.isBookmarkSet = True
        return self._bookmark

    @bookmark.setter
    def bookmark(self, value):
        self._bookmark = value
        self.isBookmarkSet = True

    @property
    def michelle(self):
        if not self._michelle:
            self._michelle = sm.GetService('michelle')
        return self._michelle

    def FindBookmark(self):
        if self.BOOKMARK_LOCATION_TYPES:
            for location_types in self.BOOKMARK_LOCATION_TYPES:
                bookmark = self.GetBookmarkByLocationType(self.bookmarks, location_types)
                if bookmark:
                    return bookmark

    def GetBookmarkByLocationType(self, bookmarks, locationType):
        for bookmark in bookmarks:
            if bookmark['locationType'] in locationType:
                return bookmark

    def GetBookmarkPosition(self):
        if self.bookmark is not None:
            return (self.bookmark.x, self.bookmark.y, self.bookmark.z)

    def GetHeaderText(self):
        if self.header is not None:
            return self.header
        if self.bookmark is None:
            return ''
        solarSystemName = cfg.evelocations.Get(self.bookmark.solarsystemID).name
        headerText = self.bookmark.hint
        headerText = headerText.replace(solarSystemName, '')
        return headerText.strip(' ').strip('-').strip(' ')

    def GetLocationButtonNamePostfix(self):
        return self.agentID

    def HasIcon(self):
        return self.iconTypeID is not None and GetCategoryID(self.iconTypeID) != categoryCelestial

    def BuildIcon(self, name, parent, align, state, opacity, width, height):
        icon = Icon(name=name, parent=parent, align=align, state=state, opacity=opacity, width=width, height=height)
        sm.GetService('photo').GetIconByType(icon, self.iconTypeID, self.iconItemID, ignoreSize=True)

    def GetLocation(self):
        if not self.isLocationSet:
            self.FindLocation()
        return (self.locationText, self.locationCallback, self.locationIcon)

    def FindLocation(self):
        if self.SHOW_READ_DETAILS:
            self.locationText, self.locationCallback, self.locationIcon = self._GetReadDetailsButtonAction()
        elif self.bookmark:
            self.locationText = self.GetButtonLabel()
            self.locationCallback = self.GetButtonFunction()
            self.locationIcon = self.GetButtonTexturePath()

    def GetItemLink(self, typeID, itemID, text = None):
        if text is None and itemID:
            try:
                if IsOwner(itemID):
                    text = cfg.eveowners.Get(itemID).name
            except OverflowError:
                logger.warning('Failed to get item link for mission objective due to OverflowError (itemID: %s)', itemID)

        text = text or GetName(typeID)
        return GetShowInfoLink(typeID=typeID, text=text, itemID=itemID)

    def GetTypeLink(self, typeID):
        typeName = GetName(typeID)
        return GetShowInfoLink(typeID=typeID, text=typeName)

    def GetDestinationLink(self, locationID):
        locationName = cfg.evelocations.Get(locationID).locationName
        return GetShowInfoLink(typeID=typeSolarSystem, text=locationName, itemID=locationID)

    def _GetReadDetailsButtonAction(self):
        text = GetByLabel(READ_DETAILS_LABEL_PATH)
        funcAndArgs = (ReadDetails, self.agentID)
        icon = READ_DETAILS_ICON_PATH
        return (text, funcAndArgs, icon)

    def IsInActiveMissionDungeon(self):
        return sm.GetService('missionObjectivesTracker').IsInActiveMissionDungeon(self.agentID)

    def _IsAtTheRightStation(self, locationID):
        currentStationID = session.stationid
        return currentStationID and currentStationID == locationID

    def _ShouldUndock(self, locationID):
        if sm.GetService('undocking').IsExiting():
            return False
        currentStationID = session.stationid
        currentStructureID = session.structureid
        if currentStationID and currentStationID != locationID:
            return True
        if currentStructureID and currentStructureID != locationID:
            return True
        return False

    def _ShouldDock(self, locationID):
        shipBall = self.michelle.GetBall(session.shipid)
        if not shipBall:
            return False
        return IsStation(locationID) and not IsApproachingBall(locationID)

    def _GetBallparkButtonState(self, ballpark):
        if ballpark:
            missionItem = ballpark.GetInvItem(self.bookmark.itemID)
            distance = BookmarkChecker(missionItem, self.bookmark, cfg).getDistanceToActiveShip() or 0
            checkWithinDungeonDist = distance and distance < DUNGEON_DISTANCE_THRESHOLD
            if checkWithinDungeonDist and not IsStation(self.bookmark.itemID):
                return buttonConst.STATE_NONE
            checkApproachDist = distance and distance < minWarpDistance
            if checkApproachDist:
                return buttonConst.STATE_APPROACH

    def _GetButtonState(self):
        if not self.bookmark or IsControllingStructure():
            return buttonConst.STATE_NONE
        warpingState = self.GetWarpingState()
        if warpingState and self.buttonState in (buttonConst.STATE_WARPTO,
         buttonConst.STATE_PREPARING_WARP,
         buttonConst.STATE_WARPING,
         buttonConst.STATE_DOCK,
         buttonConst.STATE_NONE):
            return warpingState
        if self._ShouldUndock(self.bookmark.itemID):
            return buttonConst.STATE_UNDOCK
        if sm.GetService('undocking').IsExiting():
            return buttonConst.STATE_UNDOCKING
        if self.bookmark.solarsystemID != session.solarsystemid2:
            waypoints = sm.StartService('starmap').GetWaypoints()
            if waypoints and ConvertStationIDToSolarSystemIDIfNecessary(waypoints[-1]) == self.bookmark.solarsystemID:
                return buttonConst.STATE_DESTINATIONSET
            return buttonConst.STATE_SETDESTINATION
        if self._IsAtTheRightStation(self.bookmark.itemID):
            if self.SHOW_START_CONVERSATION:
                return buttonConst.STATE_STARTCONVERSATION
            return buttonConst.STATE_NONE
        if self._ShouldDock(self.bookmark.itemID):
            return buttonConst.STATE_DOCK
        if IsApproachingBall(self.bookmark.itemID):
            return buttonConst.STATE_APPROACHING
        ballpark = self.michelle.GetBallpark()
        buttonState = self._GetBallparkButtonState(ballpark)
        if buttonState:
            return buttonState
        if self.IsInActiveMissionDungeon():
            return buttonConst.STATE_NONE
        if sm.GetService('autoPilot').InWarpRange(self.bookmark.itemID):
            return buttonConst.STATE_WARPTO
        bookmarkPosition = self.GetBookmarkPosition()
        if ballpark and self.michelle.IsPositionWithinWarpDistance(bookmarkPosition):
            return buttonConst.STATE_WARPTO
        return super(AgentMissionObjective, self)._GetButtonState()

    def _Warp(self):
        defaultWarpDist = GetMenuService().GetDefaultActionDistance('WarpTo')
        return WarpToBookmark(self.bookmark, defaultWarpDist)

    def GetButtonFunction(self):
        buttonState = self.buttonState
        if buttonState == buttonConst.STATE_WARPTO:
            return lambda x: self._Warp()
        if buttonState == buttonConst.STATE_SETDESTINATION:
            return lambda x: sm.StartService('starmap').SetWaypoint(self.bookmark.itemID, True)
        if buttonState == buttonConst.STATE_APPROACH:
            return lambda x: ApproachLocation(self.bookmark)
        if buttonState == buttonConst.STATE_DOCK:
            return lambda x: sm.GetService('menu').Dock(self.bookmark.itemID)
        if buttonState == buttonConst.STATE_STARTCONVERSATION:
            return lambda x: sm.GetService('agents').OpenDialogueWindow(self.agentID)
        if buttonState == buttonConst.STATE_READDETAILS:
            return lambda x: ReadDetails(self.agentID)
        return super(AgentMissionObjective, self).GetButtonFunction()

    def GetSolarSystemFromObjectiveLocation(self, locationID):
        if IsStation(locationID):
            station = sm.GetService('ui').GetStationStaticInfo(locationID)
            return station.solarSystemID
        if IsSolarSystem(locationID):
            return locationID

    def GetColorCodedSecurityStringForLocation(self, locationID):
        solarSystemID = self.GetSolarSystemFromObjectiveLocation(locationID)
        if solarSystemID:
            return eveformat.solar_system_security_status(solarSystemID)
        return ''


class TravelTo(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_destination.png'
    ICON_OPACITY = 0.7
    MISSION_HINT_LABEL_PATH = None
    WARP_TO_LABEL_PATH = 'UI/Agents/MissionTracker/WarpTo'
    TRAVEL_TO_LABEL_PATH = 'UI/Agents/MissionTracker/TravelTo'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, locationID, agentID, bookmarks):
        sm.GetService('missionObjectivesTracker').SetDestinationNotificationTrigger(locationID, agentID)
        self.locationID = locationID
        self.agentID = agentID
        bookmark = self.GetBookmarkByLocationType(bookmarks, DUNGEON_LOCATION_TYPES)
        if locationID == session.solarsystemid2:
            if self.IsInActiveMissionDungeon():
                missionHint = None
            else:
                missionHint = self._GetWarpToMissionHint()
            iconItemID = bookmark['itemID'] if bookmark else None
            iconTypeID = bookmark['typeID'] if bookmark else None
        else:
            iconItemID = locationID
            iconTypeID = None
            missionHint = self._GetTravelToMissionHint(locationID)
        super(TravelTo, self).__init__(iconItemID, iconTypeID, missionHint, agentID, bookmarks)

    def _GetWarpToMissionHint(self):
        return GetByLabel(self.WARP_TO_LABEL_PATH)

    def _GetTravelToMissionHint(self, locationID):
        destinationLink = self.GetDestinationLink(locationID)
        missionHint = GetByLabel(self.TRAVEL_TO_LABEL_PATH, destination=destinationLink)
        if locationID:
            missionHint += ' ' + self.GetColorCodedSecurityStringForLocation(locationID)
        return missionHint


class TalkToAgentObjective(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_destination.png'
    ICON_OPACITY = 0.7
    MISSION_HINT_LABEL_PATH = None
    WARP_TO_LABEL_PATH = 'UI/Agents/MissionTracker/WarpTo'
    TRAVEL_TO_LABEL_PATH = 'UI/Agents/MissionTracker/TravelTo'
    REPORT_TO_AGENT_PATH = 'UI/Agents/MissionTracker/ReportToAgent'
    SHOW_START_CONVERSATION = True
    BOOKMARK_LOCATION_TYPES = [TALK_TO_AGENT_LOCATION_TYPES]

    def __init__(self, missionInfo, agentID, bookmarks):
        self.targetAgentID = missionInfo[1]
        self.agentID = agentID
        self.bookmarks = bookmarks
        bookmark = self.FindBookmark()
        self.locationID = bookmark.itemID
        sm.GetService('missionObjectivesTracker').SetDestinationNotificationTrigger(self.locationID, agentID)
        iconItemID = self.locationID
        iconTypeID = None
        if self.locationID == session.locationid:
            missionHint = GetByLabel(self.REPORT_TO_AGENT_PATH, agent=self.targetAgentID)
        else:
            missionHint = self._GetTravelToMissionHint(self.locationID)
        super(TalkToAgentObjective, self).__init__(iconItemID, iconTypeID, missionHint, agentID, bookmarks)

    def _GetWarpToMissionHint(self):
        return GetByLabel(self.WARP_TO_LABEL_PATH)

    def _GetButtonState(self):
        ballpark = self.michelle.GetBallpark()
        if ballpark:
            missionItem = ballpark.GetInvItem(self.bookmark.itemID)
            distance = BookmarkChecker(missionItem, self.bookmark, cfg).getDistanceToActiveShip() or 0
            checkWithinDungeonDist = distance and distance < DUNGEON_DISTANCE_THRESHOLD
            if checkWithinDungeonDist and not IsStation(self.bookmark.itemID):
                return buttonConst.STATE_COMPLETEREFERRAL
        elif self.bookmark.itemID == session.stationid:
            return buttonConst.STATE_COMPLETEREFERRAL
        return super(TalkToAgentObjective, self)._GetButtonState()

    def _GetTravelToMissionHint(self, locationID):
        destinationLink = self.GetDestinationLink(locationID)
        missionHint = GetByLabel(self.TRAVEL_TO_LABEL_PATH, destination=destinationLink)
        if locationID:
            missionHint += ' ' + self.GetColorCodedSecurityStringForLocation(locationID)
        return missionHint

    def GetButtonFunction(self):
        if self.buttonState == buttonConst.STATE_COMPLETEREFERRAL:
            return lambda x: sm.GetService('agents').OpenDialogueWindow(self.targetAgentID)
        return super(TalkToAgentObjective, self).GetButtonFunction()


class MissionFetch(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_pickup.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/FetchItem'
    NO_LOCATION_HEADER_PATH = 'UI/Agents/MissionTracker/FetchItemHeader'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES, ORIGIN_LOCATION_TYPES]

    def __init__(self, typeID, agentID, bookmarks, itemID = None):
        iconItemID = itemID
        iconTypeID = typeID
        missionHint = self._GetMissionHint(typeID)
        self.bookmarks = bookmarks
        header = None if self.FindBookmark() else GetByLabel(self.NO_LOCATION_HEADER_PATH)
        super(MissionFetch, self).__init__(iconItemID, iconTypeID, missionHint, agentID, bookmarks, header)

    def _GetMissionHint(self, typeID):
        typeLink = self.GetTypeLink(typeID)
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, item=typeLink)


class MissionFetchMany(MissionFetch):
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/FetchItems'
    NO_LOCATION_HEADER_PATH = 'UI/Agents/MissionTracker/FetchItemsHeader'

    def __init__(self, typeID, quantity, agentID, bookmarks):
        self.quantity = quantity
        super(MissionFetchMany, self).__init__(typeID, agentID, bookmarks)

    def _GetMissionHint(self, typeID):
        typeLink = self.GetTypeLink(typeID)
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, quantity=self.quantity, item=typeLink)


class MissionFetchContainer(MissionFetch):
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/RetrieveFromContainer'


class MissionFetchContainerContents(MissionFetch):
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/RetrieveContentsFromContainer'


class MissionFetchMine(MissionFetch):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_mining.png'
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/FetchMine'


class MissionFetchMineQuantity(MissionFetchMany):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_mining.png'
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/FetchMineQuantity'


class MissionFetchTarget(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/FetchTarget'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, typeID, targetTypeID, agentID, bookmarks):
        missionHint = self._GetMissionHint(typeID, targetTypeID)
        super(MissionFetchTarget, self).__init__(missionHint=missionHint, agentID=agentID, bookmarks=bookmarks)

    def _GetMissionHint(self, typeID, targetTypeID):
        typeLink = self.GetTypeLink(typeID)
        targetTypeLink = self.GetTypeLink(targetTypeID)
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, npc=typeLink, item=targetTypeLink)


class AllObjectivesComplete(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/InfoPanels/Missions.png'
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/MissionComplete'
    SHOW_START_CONVERSATION = True
    ICON_OPACITY = 0.6
    OBJECTIVE_HEADER_LABEL_PATH = 'UI/Agents/CompleteMission'
    TRAVEL_TO_LABEL_PATH = 'UI/Agents/MissionTracker/TravelTo'
    BOOKMARK_LOCATION_TYPES = [DROP_OFF_LOCATION_TYPES, ORIGIN_LOCATION_TYPES, AGENT_LOCATION_TYPES]

    def __init__(self, agentID, bookmarks):
        agentTypeID = cfg.eveowners.Get(agentID).typeID
        iconItemID = agentID
        iconTypeID = agentTypeID
        missionHint = None
        self.journal = sm.GetService('journal')
        super(AllObjectivesComplete, self).__init__(iconItemID, iconTypeID, missionHint, agentID, bookmarks)

    def GetHeaderText(self):
        if session.locationid in (self.bookmark.itemID, self.bookmark.solarsystemID) or self._IsMissionRemoteCompletable():
            return GetByLabel(self.OBJECTIVE_HEADER_LABEL_PATH)
        return self._GetTravelToMissionHint(self.bookmark.locationID)

    def _GetTravelToMissionHint(self, locationID):
        destinationLink = self.GetDestinationLink(locationID)
        missionHint = GetByLabel(self.TRAVEL_TO_LABEL_PATH, destination=destinationLink)
        if locationID:
            missionHint += ' ' + self.GetColorCodedSecurityStringForLocation(locationID)
        return missionHint

    def _IsMissionRemoteCompletable(self):
        missionController = self.journal.GetActiveMissionForAgent(self.agentID)
        if missionController:
            return missionController.remoteCompletable

    def _GetBallparkButtonState(self, ballpark):
        if ballpark:
            buttonState = super(AllObjectivesComplete, self)._GetBallparkButtonState(ballpark)
            if buttonState:
                if buttonState == buttonConst.STATE_NONE:
                    missionItem = ballpark.GetInvItem(self.bookmark.itemID)
                    distance = BookmarkChecker(missionItem, self.bookmark, cfg).getDistanceToActiveShip() or 0
                    isWithinDungeonDist = distance and distance < DUNGEON_DISTANCE_THRESHOLD
                    if isWithinDungeonDist and not IsStation(self.bookmark.itemID):
                        return buttonConst.STATE_STARTCONVERSATION
                return buttonState
            bookmarkPosition = self.GetBookmarkPosition()
            if bookmarkPosition and self.michelle.IsPositionWithinWarpDistance(bookmarkPosition):
                return buttonConst.STATE_WARPTO

    def _GetButtonState(self):
        if not self.bookmark or IsControllingStructure():
            return buttonConst.STATE_NONE
        if self._IsMissionRemoteCompletable():
            return buttonConst.STATE_STARTCONVERSATION
        if self.bookmark.itemID == session.stationid:
            return buttonConst.STATE_STARTCONVERSATION
        return super(AllObjectivesComplete, self)._GetButtonState()


class TransportItemsPresent(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_dropoff.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/TransportItem'
    MISSION_HINT_LABEL_PLURAL_PATH = 'UI/Agents/MissionTracker/TransportItems'
    BOOKMARK_LOCATION_TYPES = [DROP_OFF_LOCATION_TYPES]

    def __init__(self, agentID = None, typeID = None, locationID = None, quantity = None, bookmarks = None):
        self.quantity = quantity
        itemLink = 'item'
        destinationLink = 'destination'
        if typeID:
            itemLink = CreateTypeInfoLink(typeID)
        if locationID and agentID:
            sm.GetService('missionObjectivesTracker').SetDestinationNotificationTrigger(locationID, agentID)
            destinationLink = CreateLocationInfoLink(locationID)
        missionHint = self._GetMissionHint(itemLink, destinationLink)
        if locationID:
            missionHint += ' ' + self.GetColorCodedSecurityStringForLocation(locationID)
        super(TransportItemsPresent, self).__init__(iconTypeID=typeID, missionHint=missionHint, agentID=agentID, bookmarks=bookmarks)

    def _GetMissionHint(self, itemLink, destinationLink):
        if self.quantity is not None and self.quantity > 1:
            return GetByLabel(self.MISSION_HINT_LABEL_PLURAL_PATH, quantity=self.quantity, item=itemLink, destination=destinationLink)
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, item=itemLink, destination=destinationLink)


class TransportItemsMissing(MissionFetch):
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/TransportItemMissing'
    MISSION_HINT_LABEL_PLURAL_PATH = 'UI/Agents/MissionTracker/TransportItemsMissing'
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_pickup.png'
    ICON_OPACITY = 0.6
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES, ORIGIN_LOCATION_TYPES, AGENT_LOCATION_TYPES]

    def __init__(self, typeID, quantity, agentID, bookmarks, itemID = None):
        self.quantity = quantity
        missionHint = self._GetMissionHint(typeID)
        super(MissionFetch, self).__init__(itemID, typeID, missionHint, agentID, bookmarks)

    def _GetMissionHint(self, typeID):
        typeLink = self.GetTypeLink(typeID)
        if self.quantity is not None and self.quantity > 1:
            return GetByLabel(self.MISSION_HINT_LABEL_PLURAL_PATH, quantity=self.quantity, item=typeLink)
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, item=typeLink)


class DropOffItemsMissing(TransportItemsMissing):

    def _GetButtonState(self):
        return buttonConst.STATE_NONE


class MissionTransport(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_dropoff.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MoveItemToItemHangar'
    OBJECTIVE_HEADER_LABEL_PATH = 'UI/Agents/MoveItemToItemHangarTitle'
    BOOKMARK_LOCATION_TYPES = [DROP_OFF_LOCATION_TYPES]

    def __init__(self, agentID = None, typeID = None, bookmarks = None):
        iconTypeID = typeID
        itemLink = CreateTypeInfoLink(typeID) if iconTypeID else 'item'
        missionHint = GetByLabel(self.MISSION_HINT_LABEL_PATH, item=itemLink)
        super(MissionTransport, self).__init__(iconTypeID=iconTypeID, missionHint=missionHint, agentID=agentID, bookmarks=bookmarks)

    def GetHeaderText(self):
        return GetByLabel(self.OBJECTIVE_HEADER_LABEL_PATH)


class FetchObjectsAcquiredDungeonDone(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_dropoff.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/FetchItemReturn'
    MISSION_HINT_LABEL_PLURAL_PATH = 'UI/Agents/MissionTracker/FetchItemsReturn'
    BOOKMARK_LOCATION_TYPES = [AGENT_LOCATION_TYPES, DROP_OFF_LOCATION_TYPES, ORIGIN_LOCATION_TYPES]

    def __init__(self, typeID, agentID, stationID, quantity, bookmarks):
        self.quantity = quantity
        missionHint = self._GetMissionHint(typeID, agentID)
        if stationID:
            sm.GetService('missionObjectivesTracker').SetDestinationNotificationTrigger(stationID, agentID)
        super(FetchObjectsAcquiredDungeonDone, self).__init__(iconTypeID=typeID, missionHint=missionHint, agentID=agentID, bookmarks=bookmarks)

    def _GetMissionHint(self, typeID, agentID):
        typeLink = self.GetTypeLink(typeID)
        agentTypeID = cfg.eveowners.Get(agentID).typeID
        agentLink = self.GetItemLink(agentTypeID, agentID)
        if self.quantity is not None and self.quantity > 1:
            return GetByLabel(self.MISSION_HINT_LABEL_PLURAL_PATH, quantity=self.quantity, item=typeLink, agent=agentLink)
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, item=typeLink, agent=agentLink)


class GoToGate(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_destination.png'
    ICON_OPACITY = 0.7
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/GoToGate'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, itemID, agentID, bookmarks):
        iconItemID = itemID
        iconTypeID = typeAccelerationGate
        missionHint = GetByLabel(self.MISSION_HINT_LABEL_PATH)
        super(GoToGate, self).__init__(iconItemID, iconTypeID, missionHint, agentID, bookmarks)


class KillTrigger(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/KillTrigger'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, typeID, itemID, agentID, bookmarks):
        iconItemID = itemID
        iconTypeID = typeID
        missionHint = self._GetMissionHint(typeID, itemID)
        super(KillTrigger, self).__init__(iconItemID, iconTypeID, missionHint, agentID, bookmarks)

    def _GetMissionHint(self, typeID, itemID):
        targetLink = self.GetItemLink(typeID, itemID)
        missionHint = GetByLabel(self.MISSION_HINT_LABEL_PATH, target=targetLink)
        return missionHint


class KillAllTrigger(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/KillAllTrigger'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, agentID, bookmarks):
        missionHint = self._GetMissionHint()
        super(KillAllTrigger, self).__init__(missionHint=missionHint, agentID=agentID, bookmarks=bookmarks)

    def _GetMissionHint(self):
        missionHint = GetByLabel(self.MISSION_HINT_LABEL_PATH)
        return missionHint


class Destroy(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/Destroy'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, typeID, itemID, objectNameID, agentID, bookmarks):
        iconItemID = itemID
        iconTypeID = typeID
        missionHint = self._GetMissionHint(typeID, itemID, objectNameID)
        super(Destroy, self).__init__(iconItemID, iconTypeID, missionHint, agentID, bookmarks)

    def _GetMissionHint(self, typeID, itemID, objectNameID):
        objectName = GetByMessageID(objectNameID) if objectNameID else GetName(typeID)
        targetLink = self.GetItemLink(typeID, itemID, objectName)
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, lcs=targetLink)


class DestroyLCSAndAll(Destroy):
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/DestroyLCSAndAll'


class DestroyAll(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/DestroyAll'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, agentID, bookmarks):
        missionHint = self._GetMissionHint()
        super(DestroyAll, self).__init__(missionHint=missionHint, agentID=agentID, bookmarks=bookmarks)

    def _GetMissionHint(self):
        return GetByLabel(self.MISSION_HINT_LABEL_PATH)


class TargetObjective(AgentMissionObjective):
    ICON_TEXTURE_PATH = None
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = None
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, typeID, itemID, agentID, bookmarks):
        iconItemID = itemID
        iconTypeID = typeID
        missionHint = self._GetMissionHint(typeID, itemID)
        super(TargetObjective, self).__init__(iconItemID, iconTypeID, missionHint, agentID, bookmarks)

    def _GetMissionHint(self, typeID, itemID):
        targetLink = self.GetItemLink(typeID, itemID)
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, target=targetLink)


class Attack(TargetObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/Attack'


class Approach(TargetObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_approach.png'
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/Approach'


class Hack(TargetObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_hack.png'
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/Hack'


class Salvage(TargetObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/Approach'


class ActivateEffect(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    ICON_OPACITY = 0.6
    LABEL_PATH = 'UI/Agents/MissionTracker/ActivateEffect'
    LABEL_PATH_NO_TARGET = 'UI/Agents/MissionTracker/ActivateEffectNoTarget'
    LABEL_PATH_MULTI_MODULE = 'UI/Agents/MissionTracker/ActivateEffectMultiModule'
    LABEL_PATH_MULTI_MODULE_NO_TARGET = 'UI/Agents/MissionTracker/ActivateEffectMultiModuleNoTarget'
    BOOKMARK_LOCATION_TYPES = [DUNGEON_LOCATION_TYPES]

    def __init__(self, typeID, itemIDs, moduleGroupIDs, agentID, bookmarks):
        self.typeID = typeID
        self.itemID = long(itemIDs[0]) if len(itemIDs) else None
        self.moduleGroupIDs = moduleGroupIDs
        missionHint = self._GetMissionHint()
        super(ActivateEffect, self).__init__(self.itemID, self.typeID, missionHint, agentID, bookmarks)

    def _GetTargetText(self):
        if self.typeID:
            return self.GetItemLink(self.typeID, self.itemID)

    def _GetModuleGroupName(self, moduleGroupID):
        return u'%s' % GetGroupNameByGroup(moduleGroupID)

    def _GetModuleText(self, hasOnlyOneModule):
        if hasOnlyOneModule:
            return GetGroupNameByGroup(self.moduleGroupIDs[0])
        return '<br>'.join([ '- %s' % self._GetModuleGroupName(moduleGroupID) for moduleGroupID in self.moduleGroupIDs ])

    def _GetMissionHint(self):
        hasTarget = bool(self.typeID)
        hasOnlyOneModule = len(self.moduleGroupIDs) == 1
        targetText = self._GetTargetText()
        moduleText = self._GetModuleText(hasOnlyOneModule)
        if hasTarget and hasOnlyOneModule:
            return GetByLabel(self.LABEL_PATH, module=moduleText, target=targetText)
        if hasTarget and not hasOnlyOneModule:
            return GetByLabel(self.LABEL_PATH_MULTI_MODULE, module=moduleText, target=targetText)
        if not hasTarget and hasOnlyOneModule:
            return GetByLabel(self.LABEL_PATH_NO_TARGET, module=moduleText)
        if not hasTarget and not hasOnlyOneModule:
            return GetByLabel(self.LABEL_PATH_MULTI_MODULE_NO_TARGET, module=moduleText)


class DungeonTriggerObjective(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_kill.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/ReadJournal'
    SHOW_READ_DETAILS = True

    def __init__(self, agentID, bookmarks):
        missionHint = GetByLabel(self.MISSION_HINT_LABEL_PATH)
        super(DungeonTriggerObjective, self).__init__(missionHint=missionHint, agentID=agentID, bookmarks=bookmarks)

    def _GetButtonState(self):
        buttonState = super(DungeonTriggerObjective, self)._GetButtonState()
        if buttonState == buttonConst.STATE_NONE and not IsControllingStructure():
            return buttonConst.STATE_READDETAILS
        return buttonState


class ReadJournal(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/classes/MissionTracker/tracker_read.png'
    ICON_OPACITY = 0.6
    SHOW_READ_DETAILS = True

    def __init__(self, agentID, bookmarks):
        super(ReadJournal, self).__init__(missionHint=None, agentID=agentID, bookmarks=bookmarks)

    def _GetButtonState(self):
        if not IsControllingStructure():
            return buttonConst.STATE_READDETAILS
        return buttonConst.STATE_NONE


class DropItemInMissionContainerObjective(AgentMissionObjective):
    ICON_TEXTURE_PATH = 'res:/UI/Texture/Shared/Brackets/containerCargoNPC.png'
    ICON_OPACITY = 0.6
    MISSION_HINT_LABEL_PATH = 'UI/Agents/MissionTracker/DropItemInMissionContainer'

    def __init__(self, missionInfo, agentID, bookmarks):
        _, self.missionContainerType, self.dropOffItemID, self.typeToDrop, self.quantity = missionInfo
        missionHint = self._GetMissionHint()
        super(DropItemInMissionContainerObjective, self).__init__(missionHint=missionHint, agentID=agentID, bookmarks=bookmarks)

    def _GetButtonState(self):
        if not IsControllingStructure():
            return buttonConst.STATE_DROPITEMINMISSIONCONTAINER
        return buttonConst.STATE_NONE

    def _GetMissionHint(self):
        return GetByLabel(self.MISSION_HINT_LABEL_PATH, dropOffType=CreateTypeInfoLink(self.typeToDrop), dropOffQuantity=self.quantity, missionContainerType=CreateTypeInfoLink(self.missionContainerType))

    def _ButtonFunction(self, _):
        ballpark = self.michelle.GetBallpark()
        if ballpark:
            missionContainerItem = ballpark.GetInvItem(self.dropOffItemID)
            if missionContainerItem is not None:
                sm.GetService('menu').OpenCargo(self.dropOffItemID)

    def GetButtonFunction(self):
        if self.buttonState == buttonConst.STATE_DROPITEMINMISSIONCONTAINER:
            return self._ButtonFunction
        return super(DropItemInMissionContainerObjective, self).GetButtonFunction()


def CreateTravelTo(missionInfo, agentID, bookmarks):
    locationID = int(missionInfo[1])
    return TravelTo(locationID, agentID, bookmarks)


def CreateMissionFetch(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    quantity = int(missionInfo[2]) if missionInfo[2] else None
    if quantity is not None and quantity > 1:
        return MissionFetchMany(typeID, quantity, agentID, bookmarks)
    return MissionFetch(typeID, agentID, bookmarks)


def CreateMissionFetchContainer(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    containerID = long(missionInfo[2])
    return MissionFetchContainer(typeID, agentID, bookmarks, containerID)


def CreateMissionFetchMine(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    if len(missionInfo) > 2:
        quantity = int(missionInfo[2]) if missionInfo[2] else None
        if quantity is not None and quantity > 1:
            return MissionFetchMineQuantity(typeID, quantity, agentID, bookmarks)
    return MissionFetchMine(typeID, agentID, bookmarks)


def CreateMissionFetchTarget(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    targetTypeID = int(missionInfo[2])
    return MissionFetchTarget(typeID, targetTypeID, agentID, bookmarks)


def CreateAllObjectivesComplete(missionInfo, agentID, bookmarks):
    agentID = long(missionInfo[1])
    return AllObjectivesComplete(agentID, bookmarks)


def CreateTransportItemsPresent(missionInfo, agentID, bookmarks):
    try:
        typeID = int(missionInfo[1])
    except (KeyError, ValueError):
        typeID = None

    try:
        locationID = int(missionInfo[2]) if agentID else None
    except (KeyError, ValueError):
        locationID = None

    quantity = int(missionInfo[3]) if missionInfo[3] else None
    return TransportItemsPresent(agentID, typeID, locationID, quantity, bookmarks)


def CreateTransportItemsMissing(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    quantity = int(missionInfo[2]) if missionInfo[2] else None
    return TransportItemsMissing(typeID, quantity, agentID, bookmarks)


def CreateDropOffItemsMissing(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    quantity = int(missionInfo[2]) if missionInfo[2] else None
    return DropOffItemsMissing(typeID, quantity, agentID, bookmarks)


def CreateMissionTransport(missionInfo, agentID, bookmarks):
    try:
        typeID = int(missionInfo[1])
    except (KeyError, ValueError):
        typeID = None

    return MissionTransport(agentID, typeID, bookmarks)


def CreateFetchObjectAcquiredDungeonDone(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    agentID = long(missionInfo[2])
    stationID = long(missionInfo[3]) if missionInfo[3] else None
    quantity = int(missionInfo[4]) if missionInfo[4] else None
    return FetchObjectsAcquiredDungeonDone(typeID, agentID, stationID, quantity, bookmarks)


def CreateGoToGate(missionInfo, agentID, bookmarks):
    itemID = long(missionInfo[1])
    return GoToGate(itemID, agentID, bookmarks)


def CreateKillTrigger(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    itemID = long(missionInfo[2])
    return KillTrigger(typeID, itemID, agentID, bookmarks)


def CreateKillAllTrigger(missionInfo, agentID, bookmarks):
    return KillAllTrigger(agentID, bookmarks)


def CreateDestroy(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    itemID = long(missionInfo[2])
    objectNameID = int(missionInfo[3]) if missionInfo[3] else None
    return Destroy(typeID, itemID, objectNameID, agentID, bookmarks)


def CreateDestroyLCSAndAll(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    itemID = long(missionInfo[2])
    objectNameID = int(missionInfo[3]) if missionInfo[3] else None
    return DestroyLCSAndAll(typeID, itemID, objectNameID, agentID, bookmarks)


def CreateDestroyAll(missionInfo, agentID, bookmarks):
    return DestroyAll(agentID, bookmarks)


def CreateAttack(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    itemID = long(missionInfo[2])
    return Attack(typeID, itemID, agentID, bookmarks)


def CreateApproach(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    itemID = long(missionInfo[2])
    return Approach(typeID, itemID, agentID, bookmarks)


def CreateHack(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    itemID = long(missionInfo[2])
    return Hack(typeID, itemID, agentID, bookmarks)


def CreateSalvage(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    itemID = long(missionInfo[2])
    return Salvage(typeID, itemID, agentID, bookmarks)


def CreateRemoveItemFromContainer(missionInfo, agentID, bookmarks):
    typeID = int(missionInfo[1])
    containerID = long(missionInfo[2])
    return MissionFetchContainerContents(typeID, agentID, bookmarks, containerID)


def CreateActivateEffect(missionInfo, agentID, bookmarks):
    moduleGroupIDs = list(missionInfo[1])
    typeID = int(missionInfo[2]) if missionInfo[2] else None
    itemIDs = list(missionInfo[3])
    return ActivateEffect(typeID, itemIDs, moduleGroupIDs, agentID, bookmarks)


def CreateTalkToAgent(missionInfo, agentID, bookmarks):
    return TalkToAgentObjective(missionInfo, agentID, bookmarks)


def CreateDungeonTriggerObjective(agentID, bookmarks):
    return DungeonTriggerObjective(agentID, bookmarks)


def CreateDropItemInMissionContainer(missionInfo, agentID, bookmarks):
    return DropItemInMissionContainerObjective(missionInfo, agentID, bookmarks)


OBJECTIVE_ID_TO_CREATOR = {'TravelTo': CreateTravelTo,
 'MissionFetch': CreateMissionFetch,
 'MissionFetchContainer': CreateMissionFetchContainer,
 'MissionFetchMineTrigger': CreateMissionFetchMine,
 'MissionFetchMine': CreateMissionFetchMine,
 'MissionFetchTarget': CreateMissionFetchTarget,
 'AllObjectivesComplete': CreateAllObjectivesComplete,
 'TransportItemsPresent': CreateTransportItemsPresent,
 'TransportItemsMissing': CreateTransportItemsMissing,
 'MissionTransport': CreateMissionTransport,
 'FetchObjectAcquiredDungeonDone': CreateFetchObjectAcquiredDungeonDone,
 'GoToGate': CreateGoToGate,
 'KillTrigger': CreateKillTrigger,
 'KillAllTrigger': CreateKillAllTrigger,
 'Destroy': CreateDestroy,
 'DestroyLCSAndAll': CreateDestroyLCSAndAll,
 'DestroyAll': CreateDestroyAll,
 'Destroy all the enemies': CreateDestroyAll,
 'Attack': CreateAttack,
 'Approach': CreateApproach,
 'Hack': CreateHack,
 'Salvage': CreateSalvage,
 'TalkToAgent': CreateTalkToAgent,
 'Remove item from container': CreateRemoveItemFromContainer,
 'dunTriggerEffectActivated': CreateActivateEffect,
 'DropItemInMissionContainer': CreateDropItemInMissionContainer,
 'DropOffItemsMissing': CreateDropOffItemsMissing}

def CreateObjective(missionInfo, agentID, bookmarks = None, title = ''):
    bookmarks = bookmarks or []
    if missionInfo and len(missionInfo) > 0 and missionInfo[0]:
        objectiveID = None
        try:
            objectiveID = str(missionInfo[0])
            if objectiveID in OBJECTIVE_ID_TO_CREATOR.keys():
                return OBJECTIVE_ID_TO_CREATOR[objectiveID](missionInfo, agentID, bookmarks)
            if objectiveID in NAME_BY_TRIGGER_TYPE.values():
                return CreateDungeonTriggerObjective(agentID, bookmarks)
            logger.error('Failed to represent mission objective for mission %s: type for objective data is unknown: %s (data: %s)', title, objectiveID, missionInfo)
        except Exception as exc:
            logger.exception('Failed to represent mission objective for mission %s: cannot parse objective data of type: %s (data: %s, error: %s)', title, objectiveID, missionInfo, exc)

    return ReadJournal(agentID, bookmarks)
