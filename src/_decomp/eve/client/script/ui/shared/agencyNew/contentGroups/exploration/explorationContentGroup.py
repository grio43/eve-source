#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\exploration\explorationContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.escalationsContentGroup import EscalationsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.combatAnomalies import CombatAnomaliesContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.cosmicSignatures import CosmicSignaturesContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.essContentGroup import ESSContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.projectDiscovery import ProjectDiscoveryContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.triglavianSpaceContentGroup import TriglavianSpaceContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.exploration.zarzakhContentGroup import ZarzakhContentGroup

class ExplorationContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupExploration
    childrenGroups = [(contentGroupConst.contentGroupCombatAnomalies, CombatAnomaliesContentGroup),
     (contentGroupConst.contentGroupSignatures, CosmicSignaturesContentGroup),
     (contentGroupConst.contentGroupEscalations, EscalationsContentGroup),
     (contentGroupConst.contentGroupProjectDiscovery, ProjectDiscoveryContentGroup),
     (contentGroupConst.contentGroupTriglavianSpace, TriglavianSpaceContentGroup),
     (contentGroupConst.contentGroupESSSystems, ESSContentGroup),
     (contentGroupConst.contentGroupZarzakh, ZarzakhContentGroup)]

    @staticmethod
    def IsTabGroup():
        return True
