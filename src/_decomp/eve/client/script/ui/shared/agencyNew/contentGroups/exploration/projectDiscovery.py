#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\exploration\projectDiscovery.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageProjectDiscovery import ContentPageProjectDiscovery

class ProjectDiscoveryContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupProjectDiscovery

    @staticmethod
    def GetContentPageClass():
        return ContentPageProjectDiscovery
