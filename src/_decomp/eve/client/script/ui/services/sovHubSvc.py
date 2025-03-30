#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\sovHubSvc.py
from carbon.common.script.sys.service import Service
from sovereignty.fuel.client.external_messenger import SovFuelExternalMessenger, FakseSovFuelExternalMessenger
from sovereignty.upgrades.client.external_data import UpgradesStaticDataSource, InstalledUpgradesLocalDataSource, InstalledUpgradesDataSource
from sovereignty.upgrades.client.external_messenger import SovUpgradesExternalMessenger, FakeSovUpgradesExternalMessenger
from sovereignty.upgrades.client.notice_listener import ExternalNoticeListener as HubUpgradesExternalNoticeListener
from sovereignty.workforce.client.notice_listener import ExternalNoticeListener as HubWorkforceExternalNoticeListener
from eve.client.script.environment.spaceObject.sovereigntyHub import UpdateUpgradesOnUpgradesUpdated, UpdateWorkforceTransportState
from sovereignty.workforce.client.external_messenger import WorkforceExternalMessenger, FakeWorkforceExternalMessenger

class SovHubSvc(Service):
    __guid__ = 'svc.sovHubSvc'
    __servicename__ = 'Sov Hub'
    __displayname__ = 'Sov Hub service'
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged']
    sovUpgradesExternalMessenger = None
    upgradesStaticData = None
    installedUpgradesLocalDataSource = None
    installedUpgradesDataSource = None
    hubUpgradesExternalNoticeListener = None
    hubWorkforceExternalNoticeListener = None

    def __init__(self):
        super(SovHubSvc, self).__init__()

    def Run(self, memStream = None):
        super(SovHubSvc, self).Run(memStream=memStream)
        USE_FAKE_UPGRADE_DATA = False
        USE_FAKE_FUEL_DATA = False
        USE_FAKE_WORKFORCE_DATA = False
        if USE_FAKE_UPGRADE_DATA:
            self.sovUpgradesExternalMessenger = FakeSovUpgradesExternalMessenger()
        else:
            self.sovUpgradesExternalMessenger = SovUpgradesExternalMessenger(self.publicGatewaySvc)
        if USE_FAKE_FUEL_DATA:
            self.sovFuelExternalMessenger = FakseSovFuelExternalMessenger()
        else:
            self.sovFuelExternalMessenger = SovFuelExternalMessenger(self.publicGatewaySvc)
        if USE_FAKE_WORKFORCE_DATA:
            self.workforceExternalMessenger = FakeWorkforceExternalMessenger(self.publicGatewaySvc)
        else:
            self.workforceExternalMessenger = WorkforceExternalMessenger(self.publicGatewaySvc)
        self.upgradesStaticData = UpgradesStaticDataSource(self.sovUpgradesExternalMessenger)
        self.installedUpgradesLocalDataSource = InstalledUpgradesLocalDataSource(self.sovUpgradesExternalMessenger)
        self.installedUpgradesDataSource = InstalledUpgradesDataSource(self.sovUpgradesExternalMessenger)
        self.hubUpgradesExternalNoticeListener = HubUpgradesExternalNoticeListener(self.publicGatewaySvc)
        self.hubUpgradesExternalNoticeListener.on_hub_upgrades_state_changed_notice.connect(self._OnHubUpgradesStateChangedNotice)
        self.hubWorkforceExternalNoticeListener = HubWorkforceExternalNoticeListener(self.publicGatewaySvc)
        self.hubWorkforceExternalNoticeListener.on_hub_workforce_configured_notice.connect(self._OnHubWorkforceConfiguredNotice)
        self.hubWorkforceExternalNoticeListener.on_hub_workforce_state_changed_notice.connect(self._OnHubWorkforceStateChangedNotice)

    def OnSessionChanged(self, isRemove, sess, change):
        if 'solarsystemid2' in change:
            self.installedUpgradesLocalDataSource.flush_all_data()

    def _OnHubUpgradesStateChangedNotice(self, hubID, installedUpgrades, fuelLastUpdated):
        self.LogInfo('sovHubSvc._OnHubUpgradesStateChangedNotice', hubID, installedUpgrades)
        self.installedUpgradesLocalDataSource.update_installed_upgrades_if_already_primed(hubID, installedUpgrades, fuelLastUpdated)
        UpdateUpgradesOnUpgradesUpdated(hubID, installedUpgrades)
        sm.ScatterEvent('OnHubUpgradesStateChanged', hubID, installedUpgrades)

    def _OnHubWorkforceConfiguredNotice(self, solarSystemID, sovHubID, oldConfig, newConfig):
        sm.ScatterEvent('OnHubWorkforceConfigureChanged', solarSystemID)

    def _OnHubWorkforceStateChangedNotice(self, solarSystemID, sovHubID, oldState, newState):
        sm.ScatterEvent('OnHubWorkforceStateChanged', solarSystemID)

    def GetInstalledUpgradesLocal(self, hubID):
        return self.installedUpgradesLocalDataSource.get_installed_upgrades_in_local(hubID)

    def GetInstalledUpgradesForHub(self, hubID):
        return self.installedUpgradesDataSource.get_installed_upgrades(hubID)

    def PrimeStaticDataForUpgrades(self):
        return self.upgradesStaticData.prime_data()

    def GetStaticDataForUpgrade(self, typeID):
        return self.upgradesStaticData.get_static_data(typeID)

    def GetReagentsByTypeID(self, hubID):
        return self.sovFuelExternalMessenger.get(hubID)

    def AddFuel(self, itemID, qty, sovHubID):
        return self.sovFuelExternalMessenger.add_fuel(itemID, qty, sovHubID)

    def SaveUpgradeConfiguration(self, sovHubID, newUpgrades, upgrades_states):
        return self.sovUpgradesExternalMessenger.update_upgrade_configuration(sovHubID, newUpgrades, upgrades_states)

    def UninstallUpgrade(self, upgradeKey):
        return self.sovUpgradesExternalMessenger.uninstall_upgrade(upgradeKey[0], upgradeKey[1])

    def SaveWorkforceConfiguration(self, sovHubID, workforceConfiguration):
        result = self.workforceExternalMessenger.configure(sovHubID, workforceConfiguration)
        if result:
            UpdateWorkforceTransportState(sovHubID, workforceConfiguration)
        return result

    def GetWorkforceConfiguration(self, sovHubID):
        return self.workforceExternalMessenger.get_configuration(sovHubID)

    def GetWorkforceState(self, sovHubID):
        return self.workforceExternalMessenger.get_state(sovHubID)

    def GetNetworkableHubs(self, sovHubID):
        return self.workforceExternalMessenger.get_networkable_hubs(sovHubID)
