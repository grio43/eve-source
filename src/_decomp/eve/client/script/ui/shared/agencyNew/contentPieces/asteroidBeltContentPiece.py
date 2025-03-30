#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\asteroidBeltContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.common.lib import appConst
from eve.common.script.sys.eveCfg import IsDocked
from evedungeons.client.oreTypesInDungeons.util import get_consolidated_ore_types_in_system

class AsteroidBeltContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_ASTEROIDBELTS

    def __init__(self, orbitIndex, celestialIndex, *args, **kwargs):
        super(AsteroidBeltContentPiece, self).__init__(*args, **kwargs)
        self.orbitIndex = orbitIndex
        self.celestialIndex = celestialIndex

    def GetName(self):
        return cfg.evelocations.Get(self.itemID).name

    def GetMenu(self):
        if IsDocked():
            return
        else:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(self.itemID, appConst.typeAsteroidBelt)

    def _ExecutePrimaryFunction(self, actionID):
        super(AsteroidBeltContentPiece, self)._ExecutePrimaryFunction(actionID)

    def GetBracketIconTexturePath(self):
        return sm.GetService('bracket').GetBracketIcon(appConst.typeAsteroidBelt)

    def GetResourceTypeIDs(self):
        return get_consolidated_ore_types_in_system(self.solarSystemID)
