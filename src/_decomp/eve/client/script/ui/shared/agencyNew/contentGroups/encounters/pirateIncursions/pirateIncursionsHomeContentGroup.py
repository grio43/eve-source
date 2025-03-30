#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\pirateIncursions\pirateIncursionsHomeContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.pirateIncursions.pirateIncursionsContentGroup import PirateIncursionsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.pirateIncursions.pirateIncursionsGuideContentGroup import PirateIncursionsGuideContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPagePirateIncursionsHome import ContentPagePirateIncursionsHome

class PirateIncursionsHomeContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupPirateIncursionsHome
    childrenGroups = [(contentGroupConst.contentGroupPirateIncursionsGuide, PirateIncursionsGuideContentGroup), (contentGroupConst.contentGroupPirateIncursions, PirateIncursionsContentGroup)]

    @staticmethod
    def GetContentPageClass():
        return ContentPagePirateIncursionsHome
