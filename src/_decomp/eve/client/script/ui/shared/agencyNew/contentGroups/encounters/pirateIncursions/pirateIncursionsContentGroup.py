#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\pirateIncursions\pirateIncursionsContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.pirateIncursions.pirateIncursionContentGroup import PirateIncursionContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPagePirateIncursions import ContentPagePirateIncursions

class PirateIncursionsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupPirateIncursions

    def _ConstructChildrenGroups(self):
        contentPieces = self.GetContentPieces()
        if contentPieces:
            for contentPiece in contentPieces:
                childGroup = PirateIncursionContentGroup(parent=self, itemID=contentPiece.GetDestinationSolarSystemID())
                self.children.append(childGroup)

    @staticmethod
    def GetContentPageClass():
        return ContentPagePirateIncursions
