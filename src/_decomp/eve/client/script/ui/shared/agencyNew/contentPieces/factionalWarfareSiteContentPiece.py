#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\factionalWarfareSiteContentPiece.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.siteContentPiece import SiteContentPiece
from eve.client.script.ui.shared.mapView.markers.mapMarkerUtil import GetSiteBracketIcon
from eve.common.script.util.facwarCommon import HOSTILE_COLOR_AGENCY, ALLY_COLOR_AGENCY
from evetypes import IsPublished
from localization import GetByLabel

class FactionalWarfareSiteContentPiece(SiteContentPiece):
    contentType = agencyConst.CONTENTTYPE_FACTIONALWARFARESITE

    def __init__(self, isFriendlySite, **kwargs):
        super(FactionalWarfareSiteContentPiece, self).__init__(**kwargs)

    def GetBgColor(self):
        return Color(*self.GetColor()).SetAlpha(0.075).GetRGBA()

    def GetAllowedShipTypeIDs(self):
        return filter(IsPublished, self.site.allowedTypes)

    def GetBracketIconTexturePath(self):
        return GetSiteBracketIcon(self.GetSiteArchetype())
