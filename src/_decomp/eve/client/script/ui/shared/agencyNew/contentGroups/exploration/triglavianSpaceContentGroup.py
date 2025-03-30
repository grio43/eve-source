#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\exploration\triglavianSpaceContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.triglavianFilaments import TriglavianFilamentsContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.triglavianSpaceContentGroupPage import TriglavianSpaceContentGroupPage

class TriglavianSpaceContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupTriglavianSpace
    childrenGroups = [(contentGroupConst.contentGroupTriglavianFilaments, TriglavianFilamentsContentGroup)]

    @staticmethod
    def GetContentPageClass():
        return TriglavianSpaceContentGroupPage
