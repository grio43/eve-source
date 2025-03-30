#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\exploration\cosmicSignatures.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageSignatures import ContentPageSignatures

class CosmicSignaturesContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupSignatures

    @staticmethod
    def GetContentPageClass():
        return ContentPageSignatures
