#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\factionWarfare\factionWarfare.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.factionWarfare.factionWarfareAgents import FactionWarfareAgentsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.factionWarfare.factionWarfareSystems import FactionWarfareSystemsContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.factionWarfareContentGroupPage import FactionWarfareContentGroupPage

class FactionWarfareContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupFactionalWarfare
    childrenGroups = [(contentGroupConst.contentGroupFactionalWarfareSystems, FactionWarfareSystemsContentGroup), (contentGroupConst.contentGroupFactionalWarfareAgents, FactionWarfareAgentsContentGroup)]

    @staticmethod
    def GetContentPageClass():
        return FactionWarfareContentGroupPage
