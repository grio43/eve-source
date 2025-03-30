#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\client\quasarCallWrapper.py
import sovereignty.fuel.client.errors as fuelErrors
import sovereignty.resource.client.errors as resourceErrors
import sovereignty.upgrades.client.errors as upgradeErrors
import logging
from sovereignty.workforce.client.errors import SovWorkforceGetConfigError, SovWorkforceGetStateError, SovWorkforceGetNetworkableHubsError
DATA_NOT_AVAILABLE = 'notAvailable'
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)

class QuasarCallWrapper(object):

    def __init__(self, sovHubSvc, sovereigntyResourceSvc = None):
        self.sovHubSvc = sovHubSvc
        self.sovereigntyResourceSvc = sovereigntyResourceSvc

    def GetInstalledUpgradesForHub(self, sovHubID):
        try:
            return self.sovHubSvc.GetInstalledUpgradesForHub(sovHubID)
        except upgradeErrors.SovUpgradeDataUnavailableError as e:
            logger.exception('Failed to get installed upgrades')
        except TimeoutException as e:
            logger.exception('Timed out when getting installed upgrades')

        return DATA_NOT_AVAILABLE

    def GetAvailableHubResources(self, sovHubID):
        try:
            return self.sovereigntyResourceSvc.GetAvailableHubResources(sovHubID)
        except resourceErrors.SovGetResourcesResponseError as e:
            logger.exception('Failed to get available resources')
        except TimeoutException as e:
            logger.exception('Timed out when getting available resources')

        return DATA_NOT_AVAILABLE

    def GetReagentsByTypeID(self, sovHubID):
        try:
            return self.sovHubSvc.GetReagentsByTypeID(sovHubID)
        except fuelErrors.SovFuelGetLevelsError as e:
            logger.exception('Failed to get fuel levels')
        except TimeoutException as e:
            logger.exception('Timed out when getting fuel levels')

        return DATA_NOT_AVAILABLE

    def PrimeStaticDataForUpgrades(self):
        try:
            self.sovHubSvc.PrimeStaticDataForUpgrades()
        except TimeoutException as e:
            logger.exception('Timed out when getting static data for upgrades')

        return DATA_NOT_AVAILABLE

    def GetWorkforceConfiguration(self, sovHubID):
        try:
            return self.sovHubSvc.GetWorkforceConfiguration(sovHubID)
        except SovWorkforceGetConfigError as e:
            logger.exception('Failed to workforce config')
        except TimeoutException as e:
            logger.exception('Timed out when getting workforce config')

        return DATA_NOT_AVAILABLE

    def SaveWorkforceConfiguration(self, sovHubID, workforceConfiguration):
        try:
            return self.sovHubSvc.SaveWorkforceConfiguration(sovHubID, workforceConfiguration)
        except SovWorkforceGetConfigError as e:
            logger.exception('Failed to set workforce config')
        except TimeoutException as e:
            logger.exception('Timed out when setting workforce config')

        return DATA_NOT_AVAILABLE

    def GetWorkforceState(self, sovHubID):
        try:
            return self.sovHubSvc.GetWorkforceState(sovHubID)
        except SovWorkforceGetStateError as e:
            logger.exception('Failed to get workforce state')
        except TimeoutException as e:
            logger.exception('Timed out when getting workforce state')

        return DATA_NOT_AVAILABLE

    def GetNetworkableHubs(self, sovHubID):
        try:
            return self.sovHubSvc.GetNetworkableHubs(sovHubID)
        except SovWorkforceGetNetworkableHubsError as e:
            logger.exception('Failed to networkable hubs')
        except TimeoutException as e:
            logger.exception('Timed out when getting networkable hubs')

        return DATA_NOT_AVAILABLE
