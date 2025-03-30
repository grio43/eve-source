#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\pirateIncursions\pirateIncursionContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPagePirateIncursion import ContentPagePirateIncursion
from localization import GetByLabel

class PirateIncursionContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupPirateIncursion

    def GetName(self):
        return GetByLabel('UI/Agency/IncursionIn', constellationName=cfg.evelocations.Get(self.itemID).locationName)

    def GetIncursionContentPiece(self):
        for contentPiece in self.parent.GetContentPieces():
            if contentPiece.GetConstellationID() == self.itemID:
                return contentPiece

    @staticmethod
    def GetContentPageClass():
        return ContentPagePirateIncursion
