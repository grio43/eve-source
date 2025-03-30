#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\escalationContentPiece.py
import gametime
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetTimeRemainingText
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from localization import GetByLabel, GetByMessageID
from localization.formatters import FormatTimeIntervalShortWritten

class EscalationContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_ESCALATION

    def __init__(self, escalationSite = None, **kwargs):
        BaseContentPiece.__init__(self, **kwargs)
        self.escalationSite = escalationSite

    def GetBracketIconTexturePath(self):
        return 'res:/UI/Texture/Shared/Brackets/beacon.png'

    def GetName(self):
        dungeon = self.GetDungeon()
        if dungeon:
            return GetByMessageID(getattr(dungeon, 'dungeonNameID', None))

    def GetSiteLevel(self):
        dungeon = self.GetDungeon()
        if dungeon:
            return getattr(dungeon, 'difficulty', None)

    def GetSiteLevelText(self):
        return GetByLabel('UI/Agency/LevelX', level=self.GetSiteLevel())

    def GetEnemyOwnerID(self):
        dungeon = self.GetDungeon()
        if dungeon:
            return getattr(dungeon, 'factionID', None)

    def GetDungeon(self):
        destDungeon = self.escalationSite.destDungeon
        return destDungeon

    def GetSubSolarSystemPosition(self):
        return (0, 0, 0)

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.solarSystemID)

    def GetBlurbText(self):
        return GetByLabel('UI/Agency/Blurbs/Escalation')

    def GetRewardTypes(self):
        return (agencyConst.REWARDTYPE_ISK3, agencyConst.REWARDTYPE_LOOT)

    def GetExpiryTimeShort(self):
        return FormatTimeIntervalShortWritten(self.GetTimeRemaining())

    def GetTimeRemaining(self):
        return self.escalationSite.expiryTime - gametime.GetWallclockTime()

    def IsExpired(self):
        return self.GetTimeRemaining() < 0

    def _ExecuteWarpTo(self):
        sm.GetService('michelle').CmdWarpToStuff('epinstance', self.itemID)

    def GetCardSortValue(self):
        return (0, self.GetJumpsToSelfFromCurrentLocation())

    def GetPrimaryActionDisabledHint(self):
        return GetTimeRemainingText(self.GetTimeRemaining())
