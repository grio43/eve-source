#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\client\sovHub\dataTypes.py
import evetypes
from localization import GetByLabel
from sovereignty.upgrades.client.data_types import InstalledUpgradeData, UpgradeStaticData
import sovereignty.upgrades.const as upgrades_const
import sovereignty.client.sovHub.hubConst as hubConst

class UpgradeData(object):
    _typeID = None
    _onlineState = None

    def __init__(self, upgrade_type_id, powerState, staticData, upgradeKey = None, itemID = None, installedUpgradeData = None):
        self._typeID = upgrade_type_id
        self._powerState = powerState
        self._upgradeKey = upgradeKey
        self._itemID = itemID
        self.staticData = staticData
        self._originalInstalledUpgradeData = installedUpgradeData
        self._lackingResources = []

    @property
    def typeID(self):
        return self._typeID

    @property
    def upgradeKey(self):
        return self._upgradeKey

    @property
    def itemID(self):
        return self._itemID

    @property
    def powerState(self):
        return self._powerState

    @powerState.setter
    def powerState(self, value):
        self._powerState = value

    @property
    def lackingResources(self):
        return self._lackingResources

    @lackingResources.setter
    def lackingResources(self, value):
        self._lackingResources = value

    @property
    def isLackingPower(self):
        return hubConst.LACKING_POWER in self.lackingResources

    @property
    def isLackingWorkforce(self):
        return hubConst.LACKING_WORKFORCE in self.lackingResources

    @property
    def isLackingFuel(self):
        return hubConst.LACKING_REAGENTS in self.lackingResources

    @property
    def isLackingStartupFuel(self):
        return hubConst.LACKING_REAGENT_STARTUP in self.lackingResources

    @property
    def isConfiguredOnline(self):
        return self._powerState != upgrades_const.POWER_STATE_OFFLINE

    @property
    def isInLowPowerState(self):
        return self._powerState == upgrades_const.POWER_STATE_LOW

    @property
    def isInPendingPowerState(self):
        return self._powerState == upgrades_const.POWER_STATE_PENDING

    @property
    def isPowerStateFunctional(self):
        return self._powerState == upgrades_const.POWER_STATE_ONLINE

    @property
    def isInRestrictedPowerState(self):
        return self._powerState in (upgrades_const.POWER_STATE_PENDING, upgrades_const.POWER_STATE_LOW)

    @property
    def isNewUpgrade(self):
        return bool(self.itemID)

    @property
    def wasPending(self):
        if self._originalInstalledUpgradeData is None:
            return False
        return self._originalInstalledUpgradeData.is_power_pending

    @property
    def wasOffline(self):
        if self._originalInstalledUpgradeData is None:
            return False
        return self._originalInstalledUpgradeData.is_power_offline

    @property
    def name(self):
        return evetypes.GetName(self.typeID)

    @property
    def upgradeStateText(self):
        if not self.isConfiguredOnline:
            return GetByLabel('UI/Common/Offline')
        if self.isPowerStateFunctional:
            return GetByLabel('UI/Common/Online')
        if self.isInPendingPowerState:
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/PendingPowerState')
        if self.isInLowPowerState:
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/LowPowerState')
        return GetByLabel('UI/Sovereignty/SovHub/Upgrades/UnknownPowerState')

    def UpdateOriginalUpgrade(self, installedUpgradeData):
        self._itemID = None
        self._upgradeKey = installedUpgradeData.upgrade_id_key
        self._originalInstalledUpgradeData = installedUpgradeData

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.typeID == other.typeID and self.isConfiguredOnline == other.isConfiguredOnline

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<UpgradeData %s>, %s' % (self.__dict__, id(self))

    def take_copy(self):
        return UpgradeData(self.typeID, self.powerState, self.staticData, self.upgradeKey, self.itemID, self._originalInstalledUpgradeData)

    @staticmethod
    def create_from_installed_upgrade_data(installed_upgrade_data, sovHubSvc):
        return UpgradeData(installed_upgrade_data.upgrade_type_id, installed_upgrade_data.power_state, sovHubSvc.GetStaticDataForUpgrade(installed_upgrade_data.upgrade_type_id), installed_upgrade_data.upgrade_id_key, installedUpgradeData=installed_upgrade_data)
