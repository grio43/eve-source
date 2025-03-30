#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\encountersContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.abyssalDeadspace.abyssalDeadspace import AbyssalDeadspaceContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.factionWarfare.factionWarfare import FactionWarfareContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.incursions.incursionsContentGroup import IncursionsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.pirateIncursions.pirateIncursionsHomeContentGroup import PirateIncursionsHomeContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.pirateStrongholds.pirateStrongholds import PirateStrongholdsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.seasonsContentGroup import SeasonsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.homefront.homefrontSitesContentGroup import HomefrontSitesContentGroup

class EncountersContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupEncounters
    childrenGroups = [(contentGroupConst.contentGroupSeasons, SeasonsContentGroup),
     (contentGroupConst.contentGroupHomefrontSites, HomefrontSitesContentGroup),
     (contentGroupConst.contentGroupIncursions, IncursionsContentGroup),
     (contentGroupConst.contentGroupPirateIncursionsHome, PirateIncursionsHomeContentGroup),
     (contentGroupConst.contentGroupFactionalWarfare, FactionWarfareContentGroup),
     (contentGroupConst.contentGroupPirateStrongholds, PirateStrongholdsContentGroup),
     (contentGroupConst.contentGroupAbyssalDeadspace, AbyssalDeadspaceContentGroup)]

    def _ConstructChildrenGroups(self):
        if not self.childrenGroups:
            return
        for contentGroupID, contentGroupCls in self.childrenGroups:
            newGroup = contentGroupCls(contentGroupID=contentGroupID, parent=self)
            self._children.append(newGroup)

    @staticmethod
    def IsTabGroup():
        return True
