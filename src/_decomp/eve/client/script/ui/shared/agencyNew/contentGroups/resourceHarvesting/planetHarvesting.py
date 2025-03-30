#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\resourceHarvesting\planetHarvesting.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.resourceHarvesting.colonyResourcesAgency import ColonyResourcesAgencyContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.resourceHarvesting.mercDen import MercDenContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.resourceHarvesting.planetaryProduction import PlanetaryProductionContentGroup

class PlanetHarvestingContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupPlanetHarvesting
    childrenGroups = [(contentGroupConst.contentGroupPlanetaryProduction, PlanetaryProductionContentGroup), (contentGroupConst.contentGroupColonyResourcesAgency, ColonyResourcesAgencyContentGroup), (contentGroupConst.contentGroupMercDens, MercDenContentGroup)]

    @staticmethod
    def IsTabGroup():
        return True
