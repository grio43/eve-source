#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\exploration\combatAnomalies.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageCombatAnomalies import ContentPageCombatAnomalies

class CombatAnomaliesContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupCombatAnomalies

    @staticmethod
    def GetContentPageClass():
        return ContentPageCombatAnomalies
