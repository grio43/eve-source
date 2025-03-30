#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\incursionSiteContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.beaconSiteContentPiece import BeaconSiteContentPiece
from eveuniverse.security import get_solar_system_security_class
from grouprewards.data import get_group_reward_min_max_player_count_by_security_class
from localization import GetByLabel
from talecommon.const import INCURSION_INFO_BY_DUNGEONID

class IncursionSiteContentPiece(BeaconSiteContentPiece):
    contentType = agencyConst.CONTENTTYPE_INCURSIONSITE

    def __init__(self, **kwargs):
        super(IncursionSiteContentPiece, self).__init__(**kwargs)
        self.incursionInfo = INCURSION_INFO_BY_DUNGEONID[self.GetDungeonID()]
        self.incursionSvc = sm.GetService('incursion')
        self.rewardData = None
        self.minPlayerCount = 0
        self.maxPlayerCount = 0
        self.maxRewardValue = 0
        self.SetIncursionData()

    def GetSiteDescription(self):
        return GetByLabel(self.incursionInfo.text)

    def GetForcesRequiredLabel(self):
        severity = GetByLabel(INCURSION_INFO_BY_DUNGEONID[self.GetDungeonID()].severity)
        return GetByLabel('UI/Agency/IncursionSiteSubtitle', severity=severity, minPlayers=self.GetMinimumPlayerCount(), maxPlayers=self.GetMaximumPlayerCount())

    def GetRewardID(self):
        return self.incursionInfo.rewardID

    def GetMinimumPlayerCount(self):
        return self.minPlayerCount

    def GetMaximumPlayerCount(self):
        return self.maxPlayerCount

    def GetMaxRewardValue(self):
        return self.maxRewardValue

    def SetIncursionData(self):
        securityClass = get_solar_system_security_class(self.solarSystemID)
        self.minPlayerCount, self.maxPlayerCount = get_group_reward_min_max_player_count_by_security_class(self.GetRewardID(), securityClass)

    def GetBracketIconTexturePath(self):
        return 'res:/UI/Texture/Shared/Brackets/beacon.png'
