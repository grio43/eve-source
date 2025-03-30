#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\externalContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import NEW_FEATURE_CONTENT_GROUP_OFFSET

class ExternalContentGroup(BaseContentGroup):

    @staticmethod
    def IsExternalGroup():
        return True

    @staticmethod
    def CallExternalFunc():
        pass

    def OpensWithinAgency(self):
        return False

    def IsEnabled(self):
        if self.contentGroupID >= NEW_FEATURE_CONTENT_GROUP_OFFSET:
            return True
        return super(ExternalContentGroup, self).IsEnabled()
