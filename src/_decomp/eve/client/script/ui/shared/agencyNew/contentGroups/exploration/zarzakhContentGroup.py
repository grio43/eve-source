#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\exploration\zarzakhContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageZarzakh import ContentPageZarzakh

class ZarzakhContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupZarzakh
    childrenGroups = []

    @staticmethod
    def GetContentPageClass():
        return ContentPageZarzakh
