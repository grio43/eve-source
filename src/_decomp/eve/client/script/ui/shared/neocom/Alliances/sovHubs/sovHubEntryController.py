#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\sovHubs\sovHubEntryController.py
import eveformat
import eveicon
import locks
from carbon.common.script.util.format import FmtAmt
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.sov.sovHub.sovHubWnd import OpenSovHubWnd
from signals import Signal
from sovereignty.client.quasarCallWrapper import DATA_NOT_AVAILABLE
from localization import GetByLabel
from sovDashboard import CalculateStructureStatusCampaignStateAndVulnerability, dashboardConst, CalculateStructureStatusFromStructureInfo, GetStructureStatusString
import inventorycommon.const as invConst
from sovereignty.client.sovHub.dataTypes import UpgradeData
from sovereignty.client.sovHub.hubUtil import GetTimeLeftTextForTypeID, GetFuelStatus, GetHoursLeftProgress, GetTexturePathForWorkforceMode, GetStartupCostForPendingUpgrades
from sovereignty.workforce import workforceConst
from sovereignty.workforce.client.workforceController import WorkforceController
from sovereignty.workforce.workforceConst import LABELPATH_BY_MODE
UNDEFINED = 'undefinedValue'

class ValueStorage(object):

    def __init__(self):
        self.upgradeTextLong = UNDEFINED
        self.upgradeTextShort = UNDEFINED
        self.upgradeSortValue = UNDEFINED
        self.powerText = UNDEFINED
        self.powerSortValue = UNDEFINED
        self.workforceColumnText = UNDEFINED
        self.workforceSortValue = UNDEFINED
        self.workforceText = UNDEFINED
        self.worceforceMode = UNDEFINED
        self.iceText = UNDEFINED
        self.lavaText = UNDEFINED
        self.installedUpgrades = UNDEFINED
        self.availableResources = UNDEFINED
        self.allReagentsByTypeID = UNDEFINED
        self.workforceState = UNDEFINED


class SovHubEntryController(object):

    def __init__(self, itemID, typeID, solarSystemID, campaignState, vulnerabilityState, sovHubInfo, quasarCallWrapper):
        self.sovereigntyResourceSvc = sm.GetService('sovereigntyResourceSvc')
        self.quasarCallWrapper = quasarCallWrapper
        self._itemID = itemID
        self._typeID = typeID
        self._solarSystemID = solarSystemID
        self._constellationID = None
        self._regionID = None
        self._campaignState = campaignState
        self._sovHubInfo = sovHubInfo
        self._vulnerabilityState = vulnerabilityState
        self.workforceController = WorkforceController(self.itemID, self.quasarCallWrapper, solarSystemID)
        self.valueStorage = ValueStorage()
        self.on_legend_moused_over = Signal(signalName='on_legend_moused_over')

    @property
    def itemID(self):
        return self._itemID

    @property
    def typeID(self):
        return self._typeID

    @property
    def solarSystemID(self):
        return self._solarSystemID

    @property
    def regionID(self):
        if self._regionID is None:
            self._regionID = cfg.mapSystemCache.Get(self._solarSystemID).regionID
        return self._regionID

    @property
    def constellationID(self):
        if self._constellationID is None:
            self._constellationID = cfg.mapSystemCache.Get(self._solarSystemID).regionID
        return self._constellationID

    @property
    def sovHubInfo(self):
        return self._sovHubInfo

    @property
    def vulnerabilityState(self):
        return self._vulnerabilityState

    def GetJumpText(self):
        return self.GetNumJumps()

    def GetNumJumps(self):
        return sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(self._solarSystemID)

    def GetStructureName(self):
        return self.GetSolarSystemName()

    def GetTexturePath(self):
        return eveicon.sov_hub

    def GetSolarSystemName(self):
        return cfg.evelocations.Get(self._solarSystemID).name

    def GetRegionName(self):
        return cfg.evelocations.Get(self.regionID).name

    def GetVulnerabilityStateText(self):
        structureStatus = CalculateStructureStatusCampaignStateAndVulnerability(self._campaignState, self.vulnerabilityState)
        if structureStatus == dashboardConst.STATUS_VULNERABLE:
            return GetByLabel('UI/Sovereignty/Status/VulnerableNowType', typeName='')
        if structureStatus == dashboardConst.STATUS_VULNERABLE_OVERTIME:
            return GetByLabel('UI/Sovereignty/Status/VulnerableType', typeName='')
        if structureStatus == dashboardConst.STATUS_REINFORCED:
            return GetByLabel('UI/Sovereignty/Status/ReinforcedType', typeName='')
        if structureStatus == dashboardConst.STATUS_INVULNERABLE:
            return GetByLabel('UI/Sovereignty/Status/InvulnerableType', typeName='')
        if structureStatus == dashboardConst.STATUS_NODEFIGHT:
            return GetByLabel('UI/Sovereignty/Status/ContestedType', typeName='')
        return '-'

    def GetHubName(self):
        return GetByLabel('UI/Sovereignty/SovHub/HubWnd/SovHubName', solarSystemName=self.GetSolarSystemName())

    def GetLocation(self):
        return '%s > %s > %s' % (cfg.evelocations.Get(self.regionID).name, cfg.evelocations.Get(self.constellationID).name, self.GetSolarSystemName())

    def OpenSovHubWindow(self):
        OpenSovHubWnd(self._itemID, self._solarSystemID)

    def GetNumSkyhooks(self):
        allCorpSkyhooks = sm.GetService('sovereigntyResourceSvc').GetMyCorporationSkyhooksMemoized()
        return len([ x for x in allCorpSkyhooks if x.solarSystemID == self.solarSystemID ])

    def GetVulnerabilityTime(self):
        currentStatus = CalculateStructureStatusFromStructureInfo(self.sovHubInfo)
        textColor = dashboardConst.PRIMARYCOLOR_BY_STATUS.get(currentStatus)
        self.color = textColor
        _, timeString = GetStructureStatusString(self.sovHubInfo, getTimeString=True)
        timeString = timeString.replace('<br>', ' ')
        return timeString

    def GetLockName(self, functionName):
        return 'HubPage_%s_%s' % (self.itemID, functionName)

    def GetUpgradesTextLong(self):
        if self.valueStorage.upgradeTextLong != UNDEFINED:
            return self.valueStorage.upgradeTextLong
        text = self._GetUpgradesText(longText=True)
        self.valueStorage.upgradeTextLong = text
        return text

    def GetUpgradesTextShort(self):
        if self.valueStorage.upgradeTextShort != UNDEFINED:
            return self.valueStorage.upgradeTextShort
        text = self._GetUpgradesText(longText=False)
        self.valueStorage.upgradeTextShort = text
        return text

    def _GetUpgradesText(self, longText):
        installedUpgrades = self.GetInstalledUpgrades()
        if installedUpgrades == DATA_NOT_AVAILABLE:
            return self.GetNotAvailableText()
        numOnline = len([ x for x in installedUpgrades if x.isPowerStateFunctional ])
        self.valueStorage.upgradeSortValue = (numOnline, len(installedUpgrades))
        if longText:
            text = GetByLabel('UI/Sovereignty/HubPage/NumUpgradesOnline', online=numOnline, installed=len(installedUpgrades))
        else:
            text = GetByLabel('UI/Sovereignty/HubPage/NumUpgradesOnlineShort', online=numOnline, installed=len(installedUpgrades))
        return text

    def GetInstalledUpgrades(self):
        self.PrimeInstalledUpgrades()
        return self.valueStorage.installedUpgrades

    def GetPowerAllocated(self):
        availableResources = self._GetAvailableResources()
        if availableResources == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        return availableResources.power_allocated

    def GetPowerAllocatedText(self):
        availablePower = self.GetPowerAllocated()
        if availablePower == DATA_NOT_AVAILABLE:
            self.valueStorage.powerText = self.GetNotAvailableText()
        else:
            return FmtAmt(availablePower)

    def GetPowerColumnText(self):
        if self.valueStorage.powerText != UNDEFINED:
            return self.valueStorage.powerText
        availablePower = self.GetAvailablePower()
        maxPower = self.maxPower
        if availablePower == DATA_NOT_AVAILABLE:
            self.valueStorage.powerSortValue = DATA_NOT_AVAILABLE
            self.valueStorage.powerText = self.GetNotAvailableText()
        else:
            self.valueStorage.powerSortValue = (availablePower, maxPower)
            self.valueStorage.powerText = '%s/%s' % (availablePower, maxPower)
        return self.valueStorage.powerText

    def GetWorkforceColumnText(self):
        if self.valueStorage.workforceColumnText != UNDEFINED:
            return self.valueStorage.workforceColumnText
        localWorkforce = self.GetLocalWorkforce()
        maxWorkforce = self.maxWorkforce
        if localWorkforce == DATA_NOT_AVAILABLE:
            self.valueStorage.workforceSortValue = DATA_NOT_AVAILABLE
            self.valueStorage.workforceColumnText = self.GetNotAvailableText()
        else:
            imported = self.GetImportedValue()
            availableInSystem = localWorkforce + imported
            self.valueStorage.workforceSortValue = (availableInSystem, maxWorkforce)
            self.valueStorage.workforceColumnText = '%s/%s' % (availableInSystem, maxWorkforce)
        return self.valueStorage.workforceColumnText

    def GetWorkforce(self):
        availableResources = self._GetAvailableResources()
        if availableResources == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        return availableResources.workforce_allocated

    def GetWorkforceText(self):
        if self.valueStorage.workforceText != UNDEFINED:
            return self.valueStorage.workforceText
        workforce = self.GetWorkforce()
        if workforce == DATA_NOT_AVAILABLE:
            self.valueStorage.workforceText = self.GetNotAvailableText()
            self.valueStorage.workforceSortValue = DATA_NOT_AVAILABLE
        else:
            self.valueStorage.workforceText = FmtAmt(workforce)
            self.valueStorage.workforceSortValue = workforce
        return self.valueStorage.workforceText

    def _GetAvailableResources(self):
        self.PrimeAvailableResources()
        return self.valueStorage.availableResources

    def GetIceFuelLabel(self):
        return self.GetTimeLeftTextForAllConfiguredOnline(invConst.typeColonyReagentIce)

    def GetLavaFuelLabel(self):
        return self.GetTimeLeftTextForAllConfiguredOnline(invConst.typeColonyReagentLava)

    def GetTransitMode(self):
        if self.valueStorage.worceforceMode != UNDEFINED:
            return self.valueStorage.worceforceMode
        self.PrimeWorkforceState()
        workforceState = self.valueStorage.workforceState
        if workforceState == DATA_NOT_AVAILABLE:
            self.valueStorage.worceforceMode = DATA_NOT_AVAILABLE
            return self.valueStorage.worceforceMode
        mode = workforceState.get_mode()
        hintList = [GetByLabel(LABELPATH_BY_MODE.get(mode, ''))]
        if mode == workforceConst.MODE_IMPORT:
            importState = workforceState.import_state
            for iSystemID, iAmount in importState.amount_by_source_system_id.iteritems():
                amountText = iAmount
                if not iAmount:
                    amountText = eveformat.color(amountText, eveColor.DANGER_RED_HEX)
                systemNameAndAmount = ' - %s (%s)' % (cfg.evelocations.Get(iSystemID).name, amountText)
                hintList.append(systemNameAndAmount)

        if mode == workforceConst.MODE_EXPORT:
            exportState = workforceState.export_state
            destID = exportState.destination_system_id
            amountText = exportState.amount
            if not exportState.amount:
                amountText = eveformat.color(amountText, eveColor.DANGER_RED_HEX)
            if destID:
                systemName = cfg.evelocations.Get(destID).name
            else:
                systemName = GetByLabel('UI/Sovereignty/HubPage/NotAvailable', color=eveColor.DANGER_RED)
            systemNameAndAmount = ' - %s (%s)' % (systemName, amountText)
            hintList.append(systemNameAndAmount)
        texturePath = GetTexturePathForWorkforceMode(mode)
        hintText = '<br>'.join(hintList)
        self.valueStorage.worceforceMode = (texturePath, hintText, None)
        return self.valueStorage.worceforceMode

    def GetOriginalPower(self):
        pass

    def GetAvailablePower(self):
        availableResources = self._GetAvailableResources()
        if availableResources == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        return availableResources.power_available

    def GetAvailablePowerText(self):
        available = self.GetAvailablePower()
        if available == DATA_NOT_AVAILABLE:
            return self.GetNotAvailableText()
        return FmtAmt(available)

    def GetLocalWorkforce(self):
        availableResources = self._GetAvailableResources()
        if availableResources == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        return availableResources.workforce_local_harvest

    def GetPowerLowStateUpgrades(self):
        return None

    @property
    def maxPower(self):
        maxPower, _ = self.sovereigntyResourceSvc.GetMaxPowerAndWorkforce(self._solarSystemID)
        return maxPower

    @property
    def maxWorkforce(self):
        _, maxWorkforce = self.sovereigntyResourceSvc.GetMaxPowerAndWorkforce(self._solarSystemID)
        return maxWorkforce

    def GetOriginalWorkforce(self):
        pass

    def GetAvailableWorkforce(self):
        availableResources = self._GetAvailableResources()
        if availableResources == DATA_NOT_AVAILABLE:
            return 0
        return availableResources.workforce_available

    def GetLocalHarvestWorkforce(self):
        availableResources = self._GetAvailableResources()
        if availableResources == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        return availableResources.workforce_local_harvest

    def GetAvailableBaseWorkforceText(self):
        local_harvest = self.GetLocalHarvestWorkforce()
        if local_harvest == DATA_NOT_AVAILABLE:
            return self.GetNotAvailableText()
        return FmtAmt(local_harvest)

    def GetImportedValue(self):
        self.PrimeWorkforceState()
        return self.workforceController.GetImportedWorkforceFromState()

    def GetExportedValue(self):
        self.PrimeWorkforceState()
        return self.workforceController.GetExportedWorkforceFromState()

    def GetWorkforceAddition(self):
        return -self.GetImportedValue() or self.GetExportedValue()

    def GetImportedValueTextAndHint(self):
        imported = self.GetImportedValue()
        if not imported:
            return ('', '')
        return (eveformat.color('+%s' % FmtAmt(imported), eveColor.SUCCESS_GREEN_HEX), '')

    def GetWorkforceLowStateUpgrades(self):
        return None

    def GetLavaText(self):
        if self.valueStorage.lavaText != UNDEFINED:
            return self.valueStorage.lavaText
        self.valueStorage.lavaText = self.GetLavaFuelLabel()
        return self.valueStorage.lavaText

    def GetIceText(self):
        if self.valueStorage.iceText != UNDEFINED:
            return self.valueStorage.iceText
        self.valueStorage.iceText = self.GetIceFuelLabel()
        return self.valueStorage.iceText

    def GetTimeLeftForTypeID(self, typeID):
        fuel = self.GetReagentForTypeID(typeID)
        if not fuel or fuel == DATA_NOT_AVAILABLE or not fuel.burned_per_hour:
            return
        return float(fuel.amount_now) / fuel.burned_per_hour

    def GetTimeLeftProgressForTypeID(self, typeID):
        hoursLeft = self.GetTimeLeftForTypeID(typeID)
        return GetHoursLeftProgress(hoursLeft)

    def GetTimeLeftTextForAllConfiguredOnline(self, typeID):
        fuel = self.GetReagentForTypeID(typeID)
        if not fuel:
            return GetByLabel('UI/Sovereignty/HubPage/FuelDepleted')
        if fuel == DATA_NOT_AVAILABLE:
            return self.GetNotAvailableText()
        installedUpgrade = self.GetInstalledUpgrades()
        fuelAmount = fuel.amount_now
        startupCost = GetStartupCostForPendingUpgrades(installedUpgrade, typeID)
        if startupCost > fuelAmount:
            return GetByLabel('UI/Sovereignty/HubPage/FuelDepleted')
        return GetFuelStatus(installedUpgrade, typeID, fuelAmount)

    def GetTimeLeftTextForTypeID(self, reagentTypeID):
        hoursLeft = self.GetTimeLeftForTypeID(reagentTypeID)
        return GetTimeLeftTextForTypeID(hoursLeft)

    def GetReagentForTypeID(self, typeID):
        self.PrimeAllReagentsByTypeForItem()
        reagentsByTypeID = self.valueStorage.allReagentsByTypeID
        if reagentsByTypeID == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        return reagentsByTypeID.get(typeID, None)

    def GetReagentConsumptionForTypeID(self, typeID):
        fuel = self.GetReagentForTypeID(typeID)
        if fuel == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        elif fuel:
            return fuel.burned_per_hour
        else:
            return 0

    def GetStartupCostForTypeID(self, typeID):
        pass

    def GetNotAvailableText(self):
        return GetByLabel('UI/Sovereignty/HubPage/NotAvailable', color=eveColor.GUNMETAL_HEX)

    def PrimeInstalledUpgrades(self):
        if self.valueStorage.installedUpgrades != UNDEFINED:
            return self.valueStorage.installedUpgrades
        with locks.TempLock(self.GetLockName('PrimeInstalledUpgrades')):
            if self.valueStorage.installedUpgrades != UNDEFINED:
                return self.valueStorage.installedUpgrades
            self.valueStorage.installedUpgrades = self._PrimeInstalledUpgrades()

    def _PrimeInstalledUpgrades(self):
        installedUpgrades = self.quasarCallWrapper.GetInstalledUpgradesForHub(self._itemID)
        if installedUpgrades == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        upgradeDataList = [ UpgradeData.create_from_installed_upgrade_data(x, sm.GetService('sovHubSvc')) for x in installedUpgrades ]
        return upgradeDataList

    def PrimeAvailableResources(self):
        if self.valueStorage.availableResources != UNDEFINED:
            return self.valueStorage.availableResources
        with locks.TempLock(self.GetLockName('PrimeAvailableResources')):
            if self.valueStorage.availableResources != UNDEFINED:
                return self.valueStorage.availableResources
            self.valueStorage.availableResources = self.quasarCallWrapper.GetAvailableHubResources(self._itemID)

    def PrimeAllReagentsByTypeForItem(self):
        if self.valueStorage.allReagentsByTypeID != UNDEFINED:
            return self.valueStorage.allReagentsByTypeID
        with locks.TempLock(self.GetLockName('PrimeAllReagentsByTypeForItem')):
            if self.valueStorage.allReagentsByTypeID != UNDEFINED:
                return self.valueStorage.allReagentsByTypeID
            self.valueStorage.allReagentsByTypeID = self.quasarCallWrapper.GetReagentsByTypeID(self._itemID)

    def PrimeWorkforceState(self):
        if self.valueStorage.workforceState != UNDEFINED:
            return self.valueStorage.workforceState
        with locks.TempLock(self.GetLockName('PrimeWorkforceState')):
            if self.valueStorage.workforceState != UNDEFINED:
                return self.valueStorage.workforceState
            workforceState = self.quasarCallWrapper.GetWorkforceState(self.itemID)
            self.workforceController.workforceState = workforceState
            self.valueStorage.workforceState = workforceState
