#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\homeContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.corpContentGroup import CorpContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.encounters.encountersContentGroup import EncountersContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.explorationContentGroup import ExplorationContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.fleetupContentGroup import FleetupContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.helpContentGroup import HelpContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.missions.missionsContentGroup import MissionsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.resourceHarvesting.resourceHarvestingContentGroup import ResourceHarvestingContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.homeContentGroupPage import HomeContentGroupPage

class HomeContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupHome
    childrenGroups = [(contentGroupConst.contentGroupMissions, MissionsContentGroup),
     (contentGroupConst.contentGroupEncounters, EncountersContentGroup),
     (contentGroupConst.contentGroupExploration, ExplorationContentGroup),
     (contentGroupConst.contentGroupResourceHarvesting, ResourceHarvestingContentGroup),
     (contentGroupConst.contentGroupFleetUp, FleetupContentGroup),
     (contentGroupConst.contentGroupHelp, HelpContentGroup),
     (contentGroupConst.contentGroupCorp, CorpContentGroup)]

    @staticmethod
    def GetContentPageClass():
        return HomeContentGroupPage
