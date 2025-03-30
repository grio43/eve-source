#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\oreAnomalyContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.siteContentPiece import SiteContentPiece
from evedungeons.client.oreTypesInDungeons.util import get_consolidated_ore_types_in_dungeon

class OreAnomalyContentPiece(SiteContentPiece):
    contentType = agencyConst.CONTENTTYPE_OREANOMALY

    def GetBracketIconTexturePath(self):
        return 'res:/UI/Texture/Shared/Brackets/ore_site_16.png'

    def GetResourceTypeIDs(self):
        return get_consolidated_ore_types_in_dungeon(self.site.dungeonID)
