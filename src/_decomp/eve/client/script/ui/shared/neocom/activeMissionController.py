#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\activeMissionController.py
import evetypes
from carbonui.util.color import Color
from eve.client.script.ui.station.agents import agentUtil
from eve.common.lib import appConst
from localization import GetByLabel, GetByMessageID
import blue
MISSIONSTATE_ORDER = (appConst.agentMissionStateAccepted,
 appConst.agentMissionStateAllocated,
 appConst.agentMissionStateOffered,
 appConst.agentMissionStateFailed)

class ActiveMissionController(object):

    def __init__(self, missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID):
        self.missionState = missionState
        self.isImportantMission = importantMission
        self.missionTypeID = missionType
        self.missionName = missionName
        self.agentID = agentID
        self.expirationTime = expirationTime
        self.bookmarks = bookmarks
        self.remoteOfferable = remoteOfferable
        self.remoteCompletable = remoteCompletable
        self.contentID = contentID
        self._disallowedTypeIDs = None
        self._isSpecialShipRestriction = None
        self._dungeonData = -1

    def GetExpiryTimeText(self, short = False):
        return agentUtil.GetMissionExpirationText(self.missionState, self.expirationTime, short=short)

    def GetMissionStateText(self):
        return agentUtil.GetMissionStateText(self.missionState, self.expirationTime)

    def GetMissionStateTextColored(self):
        color = Color.RGBtoHex(*self.GetMissionStateColor())
        text = agentUtil.GetMissionStateText(self.missionState, self.expirationTime)
        return "<color='%s'>%s</color>" % (color, text)

    def GetMissionStateColor(self):
        return agentUtil.GetMissionStateColor(self.missionState, self.expirationTime)

    def GetTimeRemaining(self):
        return self.expirationTime - blue.os.GetWallclockTime()

    def IsExpired(self):
        return self.GetTimeRemaining() <= 0

    def GetMissionTypeText(self):
        return GetByLabel(self.missionTypeID)

    def GetMissionName(self):
        return GetByMessageID(self.missionName)

    def GetEnemyFactionID(self):
        missionDetails = self.GetMissionDetails()
        try:
            dungeons = missionDetails['objectives']['dungeons']
        except KeyError:
            return None

        for dungeon in dungeons:
            if 'ownerID' in dungeon:
                return dungeon['ownerID']

    def GetMissionDetails(self):
        return sm.GetService('agents').GetMissionInfo(self.agentID, contentID=self.contentID)

    def GetActiveMissionSortKey(self):
        try:
            return MISSIONSTATE_ORDER.index(self.missionState)
        except ValueError:
            return len(MISSIONSTATE_ORDER)

    def GetDungeonID(self):
        self._CheckPrimeDungeonData()
        if self._dungeonData:
            return self._dungeonData['dungeonID']

    def _CheckPrimeDungeonData(self):
        if self._dungeonData == -1:
            missionInfo = sm.GetService('agents').GetMissionInfo(self.agentID)
            dungeons = missionInfo['objectives']['dungeons']
            if dungeons:
                self._dungeonData = dungeons[0]
            else:
                self._dungeonData = None

    def GetAllowedShipTypeIDs(self):
        disallowedTypes = self.GetDisallowedShipTypeIDs()
        if disallowedTypes:
            allShipTypes = evetypes.GetTypeIDsByCategory(appConst.categoryShip)
            return [ typeID for typeID in allShipTypes if typeID not in disallowedTypes and evetypes.IsPublished(typeID) ]

    def GetDisallowedShipTypeIDs(self):
        if not self._disallowedTypeIDs:
            self._FetchDisallowedTypeIDs()
        return self._disallowedTypeIDs

    def _FetchDisallowedTypeIDs(self):
        dungeonID = self.GetDungeonID()
        if not dungeonID:
            return None
        restrictions = sm.GetService('agents').GetAgentMoniker(self.agentID).GetDungeonShipRestrictions(dungeonID)
        self._disallowedTypeIDs = restrictions['restrictedShipTypes']

    def IsShipRestrictionInteresting(self):
        self._CheckPrimeDungeonData()
        if self._dungeonData is not None:
            return self._dungeonData.get('shipRestrictions', 0) == 1

    def IsMissionAccepted(self):
        return self.missionState == appConst.agentMissionStateAccepted

    def GetDestinationAgentID(self):
        if self.missionTypeID == appConst.missionTypeEpicArcTalkToAgent and self.IsMissionAccepted():
            details = self.GetMissionDetails()
            try:
                agentID = details['objectives']['objectives'][0][1][0]
                return agentID
            except KeyError as IndexError:
                pass

        return self.agentID
