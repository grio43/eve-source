#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\corpContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.externalContentGroup import ExternalContentGroup
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.common.script.sys import idCheckers
from localization import GetByLabel

class CorpContentGroup(ExternalContentGroup):
    contentGroupID = contentGroupConst.contentGroupCorp

    @staticmethod
    def CallExternalFunc():
        if idCheckers.IsNPC(session.corpid):
            return sm.GetService('corpui').Show(CorpPanel.RECRUITMENT_SEARCH)
        else:
            return sm.GetService('corpui').Show()

    def GetNameKey(self):
        return self._GeNameAndDescKey()

    def GetDescriptionKey(self):
        return self._GeNameAndDescKey()

    def _GeNameAndDescKey(self):
        if not idCheckers.IsNPC(session.corpid):
            return (self.contentGroupID, 1)
        return self.contentGroupID
