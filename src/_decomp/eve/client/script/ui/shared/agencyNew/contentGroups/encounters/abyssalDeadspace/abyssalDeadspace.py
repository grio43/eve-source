#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\abyssalDeadspace\abyssalDeadspace.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.abyssalDeadspace.filaments import AbyssalDeadspaceFilamentsContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.abyssalDeadspaceContentGroupPage import AbyssalDeadspaceContentGroupPage

class AbyssalDeadspaceContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupAbyssalDeadspace
    childrenGroups = [(contentGroupConst.contentGroupAbyssalFilaments, AbyssalDeadspaceFilamentsContentGroup)]

    @staticmethod
    def GetContentPageClass():
        return AbyssalDeadspaceContentGroupPage
