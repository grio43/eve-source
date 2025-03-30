#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\resourceHarvesting\colonyResourcesAgency.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageColonyResourcesAgency import ContentPageColonyResourcesAgency

class ColonyResourcesAgencyContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupColonyResourcesAgency
    childrenGroups = []

    @staticmethod
    def GetContentPageClass():
        return ContentPageColonyResourcesAgency
