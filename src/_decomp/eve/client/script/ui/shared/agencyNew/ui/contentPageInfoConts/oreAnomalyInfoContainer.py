#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\oreAnomalyInfoContainer.py
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.resourceHarvestingInfoCont import ResourceHarvestingInfoContainer
from jobboard.client import get_ore_anomaly_job

class OreAnomalyInfoContainer(ResourceHarvestingInfoContainer):

    def _GetJob(self, instanceID):
        return get_ore_anomaly_job(instanceID)
