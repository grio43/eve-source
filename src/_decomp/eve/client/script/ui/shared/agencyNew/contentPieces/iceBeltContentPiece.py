#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\iceBeltContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.common.lib import appConst
from eve.common.script.sys.eveCfg import IsDocked
from evedungeons.client.iceTypesInDungeon.util import get_consolidated_ice_types_in_dungeon
from localization import GetByMessageID

class IceBeltContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_ICEBELTS

    def __init__(self, site = None, **kwargs):
        BaseContentPiece.__init__(self, **kwargs)
        self.site = site

    def GetName(self):
        return GetByMessageID(self.site.dungeonNameID)

    def GetMenu(self):
        if IsDocked():
            return
        elif self.GetTargetID():
            scanSvc = sm.GetService('scanSvc')
            return scanSvc.GetScannedDownMenu(self.site)
        else:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(self.solarSystemID, appConst.typeSolarSystem)

    def GetTargetID(self):
        return getattr(self.site, 'targetID', None)

    def _ExecutePrimaryFunction(self, actionID):
        if actionID == agencyUIConst.ACTION_WARPTO:
            targetID = self.GetTargetID()
            sm.GetService('menu').WarpToScanResult(targetID)
        else:
            super(IceBeltContentPiece, self)._ExecutePrimaryFunction(actionID)

    def GetBracketIconTexturePath(self):
        return 'res:/UI/Texture/Shared/Brackets/ore_site_16.png'

    def GetResourceTypeIDs(self):
        return get_consolidated_ice_types_in_dungeon(self.site.dungeonID)
