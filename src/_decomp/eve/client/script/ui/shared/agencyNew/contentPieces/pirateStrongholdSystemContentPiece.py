#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\pirateStrongholdSystemContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.pirateStrongholdContentPiece import PirateStrongholdContentPiece
from eve.common.lib import appConst

class PirateStrongholdSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_PIRATE_STRONGHOLD

    def __init__(self, contentDataList, *args, **kwargs):
        super(PirateStrongholdSystemContentPiece, self).__init__(typeID=appConst.typeSolarSystem, *args, **kwargs)
        self.contentPieces = [ PirateStrongholdContentPiece(contentData) for contentData in contentDataList ]

    def GetIconTexturePath(self):
        faction_id = self.GetEnemyFactionID()
        if faction_id == appConst.factionTheBloodRaiderCovenant:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/bloodRaiderSite.png'
        elif faction_id == appConst.factionGuristasPirates:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/guristasSite.png'
        else:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/CombatSite.png'

    def GetBracketIconTexturePath(self):
        return sm.GetService('bracket').GetBracketIconByGroupID(appConst.groupForwardOperatingBase)

    def GetEnemyOwnerID(self):
        return self.contentPieces[0].GetEnemyOwnerID()

    def GetName(self):
        return self.contentPieces[0].GetName()

    def GetContentPieces(self):
        return self.contentPieces

    def GetNumDungeons(self):
        return len(self.contentPieces)
