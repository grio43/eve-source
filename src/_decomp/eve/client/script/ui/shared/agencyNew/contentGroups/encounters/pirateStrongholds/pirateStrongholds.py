#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\pirateStrongholds\pirateStrongholds.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPagePirateStrongholds import ContentPagePirateStrongholds
from localization import GetByLabel

class PirateStrongholdsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupPirateStrongholds

    def IsEnabled(self):
        contentProvider = self.GetContentProvider()
        if not contentProvider:
            return False
        return bool(contentProvider.GetPirateStrongholds())

    def GetDisabledHint(self):
        return GetByLabel('UI/Agency/PirateStrongholdsDisabledHint')

    @staticmethod
    def GetContentPageClass():
        return ContentPagePirateStrongholds
