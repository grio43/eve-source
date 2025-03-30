#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\upgradeEntryController.py
import carbonui
import eveicon
from eve.client.script.ui import eveColor
from inventorycommon.const import typeColonyReagentIce, typeColonyReagentLava
from localization import GetByLabel
from sovereignty.client.sovHub.hubUtil import GetTypeListTexturePathForType

class UpgradeEntryController(object):

    def __init__(self, installedUpgradeData, priority, hubController, functionalState):
        self._typeID = installedUpgradeData.typeID
        self.installedUpgradeData = installedUpgradeData
        self._priority = priority
        self._hubController = hubController

    @property
    def typeID(self):
        return self._typeID

    @property
    def isConfiguredOnline(self):
        return self.installedUpgradeData.isConfiguredOnline

    @property
    def isPowerStateFunctional(self):
        return self.installedUpgradeData.isPowerStateFunctional

    @property
    def itemID(self):
        return self.installedUpgradeData.itemID

    @property
    def upgradeKey(self):
        return self.installedUpgradeData.upgradeKey

    @property
    def priority(self):
        return self._priority

    @property
    def staticData(self):
        return self.installedUpgradeData.staticData

    @property
    def name(self):
        return self.installedUpgradeData.name

    @property
    def typeListTexture(self):
        return GetTypeListTexturePathForType(self.typeID)

    @property
    def priorityText(self):
        return self.priority + 1

    @property
    def powerText(self):
        if self.staticData:
            return self.staticData.power
        return '-'

    @property
    def workforceText(self):
        if self.staticData:
            return self.staticData.workforce
        return '-'

    @property
    def upkeepText(self):
        if self.staticData:
            return '%s/h' % self.staticData.consumption_per_hour
        return '-'

    @property
    def fuelTexturePath(self):
        if self.staticData:
            if self.fuelTypeID == typeColonyReagentIce:
                return eveicon.superionic_ice
            if self.fuelTypeID == typeColonyReagentLava:
                return eveicon.magmatic_gas
        return ''

    @property
    def fuelTypeID(self):
        return self.staticData.fuel_type_id

    @property
    def startupText(self):
        if self.staticData:
            return self.staticData.startup_cost
        return '-'

    @property
    def powerState(self):
        return self.installedUpgradeData.powerState

    @powerState.setter
    def powerState(self, value):
        self.installedUpgradeData.powerState = value

    @property
    def isLackingPower(self):
        return self.installedUpgradeData.isLackingPower

    @property
    def isLackingWorkforce(self):
        return self.installedUpgradeData.isLackingWorkforce

    @property
    def isLackingFuel(self):
        return self.installedUpgradeData.isLackingFuel

    @property
    def isLackingStartupFuel(self):
        return self.installedUpgradeData.isLackingStartupFuel

    def GetOnlineStateTextAndHints(self):
        isConfigOnline = self.isConfiguredOnline
        upgradeStateText = self.installedUpgradeData.upgradeStateText
        if not isConfigOnline:
            return (upgradeStateText, GetByLabel('Tooltips/StructureUI/SovHubOfflineUpgrade'))
        if self.installedUpgradeData.isPowerStateFunctional:
            return (upgradeStateText, GetByLabel('Tooltips/StructureUI/SovHubOnlineUpgrade'))
        hint = ''
        if self.installedUpgradeData.isInPendingPowerState:
            if self.installedUpgradeData.isLackingStartupFuel:
                hint = GetByLabel('Tooltips/StructureUI/SovHubRedFuelState')
        elif self.installedUpgradeData.isInLowPowerState:
            if len(self.installedUpgradeData.lackingResources) > 1:
                hint = GetByLabel('Tooltips/StructureUI/SovHubRedResourceState')
            elif self.installedUpgradeData.isLackingPower:
                hint = GetByLabel('Tooltips/StructureUI/SovHubRedPowerState')
            elif self.installedUpgradeData.isLackingWorkforce:
                hint = GetByLabel('Tooltips/StructureUI/SovHubRedWorkforceState')
        text = '<color=%s>%s</color>' % (eveColor.DANGER_RED_HEX, upgradeStateText)
        return (text, hint)

    def GetEntryTextColor(self):
        return self._GetElementColor(self.installedUpgradeData.isInRestrictedPowerState)

    def GetPowerColor(self, defaultColor = None):
        return self._GetElementColor(self.isLackingPower, defaultColor)

    def GetWorkforceColor(self, defaultColor = None):
        return self._GetElementColor(self.isLackingWorkforce, defaultColor)

    def GetReagentColor(self, defaultColor = None):
        return self._GetElementColor(self.isLackingFuel, defaultColor)

    def GetReagentStartupColor(self, defaultColor = None):
        return self._GetElementColor(self.isLackingStartupFuel, defaultColor)

    def _GetElementColor(self, isLacking, defaultColor = None):
        if isLacking:
            return eveColor.DANGER_RED
        return defaultColor or carbonui.TextBody.default_color

    def DeleteUpgrade(self, *args):
        self._hubController.DeleteUpgrade(self.typeID, self.upgradeKey, self.itemID)

    def GetRemoveTexturePath(self):
        if self.upgradeKey:
            return eveicon.trashcan
        return eveicon.close
