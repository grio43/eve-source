#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\resourceHarvesting\resourceHarvestingContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.resourceHarvesting.asteroidBelts import AsteroidBeltsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.resourceHarvesting.iceBelts import IceBeltsContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.resourceHarvesting.oreAnomalies import OreAnomaliesContentGroup
from eve.client.script.ui.shared.agencyNew.contentGroups.resourceHarvesting.planetHarvesting import PlanetHarvestingContentGroup

class ResourceHarvestingContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupResourceHarvesting
    childrenGroups = [(contentGroupConst.contentGroupAsteroidBelts, AsteroidBeltsContentGroup),
     (contentGroupConst.contentGroupOreAnomalies, OreAnomaliesContentGroup),
     (contentGroupConst.contentGroupIceBelts, IceBeltsContentGroup),
     (contentGroupConst.contentGroupPlanetaryProduction, PlanetHarvestingContentGroup)]

    @staticmethod
    def IsTabGroup():
        return True
