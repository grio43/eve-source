#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\missions\agents\distributionAgents.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageAgents import ContentPageAgents

class DistributionAgentsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupMissionAgentsDistribution

    @staticmethod
    def GetContentPageClass():
        return ContentPageAgents
