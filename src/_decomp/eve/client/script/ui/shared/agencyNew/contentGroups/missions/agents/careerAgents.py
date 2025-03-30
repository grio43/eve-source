#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\missions\agents\careerAgents.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageCareerAgents import ContentPageCareerAgents

class CareerAgentsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupCareerAgents

    @staticmethod
    def GetContentPageClass():
        return ContentPageCareerAgents
