#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\agencyContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.comtool.constants import CHANNEL_EVENTS
from localization import GetByLabel

class AgencyContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_AGENCY

    def __init__(self, **kwargs):
        BaseContentPiece.__init__(self, **kwargs)
        self.seasonSvc = sm.GetService('seasonService')

    def GetTitle(self):
        return self.seasonSvc.get_navigation_season_title()

    def GetExpiryTimeText(self):
        return self.seasonSvc.get_season_remaining_time_text()

    def GetBlurbText(self):
        return GetByLabel('UI/Agency/Blurbs/Agency')

    def GetChatChannelID(self):
        return CHANNEL_EVENTS
