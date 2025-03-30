#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\sovereigntyHub.py
import logging
import uthread
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from sovereignty.client.sovHub import hubConst
from sovereignty.upgrades.client.errors import SovUpgradeDataUnavailableError
from sovereignty.workforce.client.errors import SovWorkforceError
logger = logging.getLogger(__name__)

class SovereigntyHub(SpaceObject):

    def __init__(self):
        SpaceObject.__init__(self)
        self.upgrades = {}
        self.fitted = False
        self.miningUpgradesOnline = 0

    def _SetMuActive(self):
        if self.miningUpgradesOnline > 0:
            self.model.SetControllerVariable(hubConst.CTRL_MINING, hubConst.CTRL_ON)
        else:
            self.model.SetControllerVariable(hubConst.CTRL_MINING, hubConst.CTRL_OFF)

    def SetUpgradeControllerVariables(self, upgradeTypeId, isBuilt, isOnline):
        for upgradesMember in hubConst.UPGRADES_MAPPINGS:
            if upgradeTypeId in upgradesMember:
                if upgradeTypeId in hubConst.MINING_UPGRADES and isOnline:
                    self.miningUpgradesOnline += 1
                isBuiltVariable = upgradesMember[0] + hubConst.CTRL_IS_BUILT
                self.model.SetControllerVariable(isBuiltVariable, hubConst.CTRL_ON if isBuilt else hubConst.CTRL_OFF)
                lowPowerVariable = upgradesMember[0] + hubConst.CTRL_LOW_POWER
                self.model.SetControllerVariable(lowPowerVariable, hubConst.CTRL_ON if not isOnline else hubConst.CTRL_OFF)

    def _UpdateInstalledUpgrades(self):
        slimItem = self.typeData.get('slimItem')
        sovHubSvc = sm.GetService('sovHubSvc')
        try:
            installedUpgrades = sovHubSvc.GetInstalledUpgradesLocal(slimItem.itemID)
        except SovUpgradeDataUnavailableError as e:
            logger.warning('spaceobject.SovereigntyHub - Failed to get installed upgrades for hub %s - %s', slimItem.itemID, e)
            installedUpgrades = []

        self.miningUpgradesOnline = 0
        for upgrade in installedUpgrades:
            self.SetUpgradeControllerVariables(upgrade.upgrade_type_id, True, upgrade.is_power_online)
            self.upgrades[upgrade.upgrade_type_id] = (True, upgrade.is_power_online)

        self._SetMuActive()

    def OnUpgradesUpdated(self, installedUpgrades):
        installedUpgradesTypeIds = [ upgrade.upgrade_type_id for upgrade in installedUpgrades ]
        self.miningUpgradesOnline = 0
        for upgradeTypeID in self.upgrades.keys():
            if upgradeTypeID not in installedUpgradesTypeIds:
                self.SetUpgradeControllerVariables(upgradeTypeID, False, False)
                self.upgrades.pop(upgradeTypeID, None)

        for installedUpgrade in installedUpgrades:
            self.SetUpgradeControllerVariables(installedUpgrade.upgrade_type_id, True, installedUpgrade.is_power_online)
            if installedUpgrade.upgrade_type_id not in self.upgrades.keys():
                self.upgrades[installedUpgrade.upgrade_type_id] = (True, installedUpgrade.is_power_online)

        self._SetMuActive()

    def OnWorkforceTransportUpdated(self, transportState):
        transportStateVariable = hubConst.PopulationTransportVFX + hubConst.CTRL_TRANSPORT_STATE
        lowPowerVariable = hubConst.PopulationTransportVFX + hubConst.CTRL_LOW_POWER
        if transportState in hubConst.WORKFORCE_MAPPINGS.keys():
            self.model.SetControllerVariable(transportStateVariable, hubConst.WORKFORCE_MAPPINGS.get(transportState))
            self.model.SetControllerVariable(lowPowerVariable, hubConst.CTRL_OFF)
        else:
            self.model.SetControllerVariable(lowPowerVariable, hubConst.CTRL_ON)

    def UpdateWorkforceTransportState(self):
        slimItem = self.typeData.get('slimItem')
        sovHubSvc = sm.GetService('sovHubSvc')
        try:
            transportState = sovHubSvc.GetWorkforceConfiguration(slimItem.itemID).get_mode()
        except SovWorkforceError as e:
            logger.warning('spaceobject.SovereigntyHub - Failed to get workforce configuration for hub %s - %s', slimItem.itemID, e)
            return

        self.OnWorkforceTransportUpdated(transportState)

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True):
        self.model = self._SetupModelAndAddToScene(fileName, loadedModel, addToScene)
        if self.model is None:
            return
        self.SetStaticRotation()
        uthread.new(self._UpdateInstalledUpgrades)
        uthread.new(self.UpdateWorkforceTransportState)
        self.SetupAnimationInformation(self.model)
        if notify:
            self.NotifyModelLoaded()


def UpdateUpgradesOnUpgradesUpdated(sovHubID, installedUpgrades):
    try:
        sovHub = sm.GetService('michelle').GetBall(sovHubID)
        if sovHub:
            sovHub.OnUpgradesUpdated(installedUpgrades)
    except KeyError:
        pass


def UpdateWorkforceTransportState(sovHubID, workforceConfiguration):
    try:
        sovHub = sm.GetService('michelle').GetBall(sovHubID)
        if sovHub:
            sovHub.OnWorkforceTransportUpdated(workforceConfiguration.get_mode())
    except KeyError:
        pass
