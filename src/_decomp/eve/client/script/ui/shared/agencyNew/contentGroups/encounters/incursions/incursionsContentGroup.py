#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\incursions\incursionsContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.incursions.incursionContentGroup import IncursionContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageIncursions import ContentPageIncursions

class IncursionsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupIncursions

    def _ConstructChildrenGroups(self):
        contentPieces = self.GetContentPieces()
        if contentPieces:
            for contentPiece in contentPieces:
                childGroup = IncursionContentGroup(parent=self, itemID=contentPiece.GetConstellationID())
                self.children.append(childGroup)

    @staticmethod
    def GetContentPageClass():
        return ContentPageIncursions
