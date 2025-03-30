#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\homefront\homefrontSitesContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageHomefrontSites import ContentPageHomefrontSites

class HomefrontSitesContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupHomefrontSites

    @staticmethod
    def GetContentPageClass():
        return ContentPageHomefrontSites

    def IsVisible(self):
        return bool(self.GetContentProvider().GetAllDungeonInstances())
