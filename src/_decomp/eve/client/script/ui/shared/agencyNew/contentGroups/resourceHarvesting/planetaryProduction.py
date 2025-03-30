#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\resourceHarvesting\planetaryProduction.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPagePlanetaryProduction import ContentPagePlanetaryProduction

class PlanetaryProductionContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupPlanetaryProduction

    @staticmethod
    def GetContentPageClass():
        return ContentPagePlanetaryProduction
