#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\pirateStrongholdContentPiece.py
from eve.client.script.ui.shared.agencyNew.contentPieces.customContentPiece import CustomContentPiece
from eve.common.lib import appConst

class PirateStrongholdContentPiece(CustomContentPiece):

    def __init__(self, content_data, is_new = False):
        super(PirateStrongholdContentPiece, self).__init__(content_data, is_new=is_new)

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
