#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\hubController.py
import eveformat
import evetypes
import locks
import uthread
import uthread2
from brennivin.itertoolsext import Bundle
from carbon.common.script.util.format import FmtAmt
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.sov.sovHub.upgradeEntry import UpgradeTypeDragData
from eve.client.script.ui.shared.sov.sovHub.upgradeEntryController import UpgradeEntryController
from eve.common.script.sys import devIndexUtil
from eve.common.script.sys.idCheckers import IsNPCCorporation
from localization import GetByLabel
from signals import Signal
from sovereignty.client.quasarCallWrapper import QuasarCallWrapper, DATA_NOT_AVAILABLE
from sovereignty.client.sovHub.dataTypes import UpgradeData
from sovereignty.upgrades.client.errors import SovUpgradeDataUnavailableError, SovUpgradeUninstallError, SovUpgradeInstallError
from sovereignty.client.sovHub.hubUtil import GetPowerForUpgrades, GetWorkforceForUpgrades, GetConsumptionPerHour, GetStartupCost, GetHoursLeft, GetTimeLeftTextForTypeID, UpdateEffectiveStatesForUpgrades, GetHoursLeftProgress
from sovereignty.workforce.client.workforceController import WorkforceController
from stackless_response_router.exceptions import TimeoutException
import inventorycommon.const as invConst
import carbonui.const as uiconst
import blue
import sovereignty.upgrades.const as upgrades_const
import logging
logger = logging.getLogger(__name__)
NO_ACL_SET = -99
NOT_AVAILABLE = -999
NOT_DEFINED = 'notDefined'

class HubController(object):
    __notifyevents__ = ['OnHubUpgradesStateChanged', 'OnHubWorkforceConfigureChanged', 'OnHubWorkforceStateChanged']

    def __init__(self, itemID, solarSystemID):
        self._itemID = itemID
        self._solarSystemID = solarSystemID
        self._systemClaimTime = NOT_DEFINED
        self.sovHubSvc = sm.GetService('sovHubSvc')
        self.sovereigntyResourceSvc = sm.GetService('sovereigntyResourceSvc')
        self.quasarCallWrapper = QuasarCallWrapper(self.sovHubSvc, self.sovereigntyResourceSvc)
        self.workforceController = WorkforceController(self.itemID, self.quasarCallWrapper, self.solarSystemID)
        self.sovSvc = sm.GetService('sov')
        self.upgradeItemIDsPendingInstall = []
        fuelACL = self.sovSvc.GetSovHubFuelAccessGroup(self._solarSystemID)
        self.maxPower, self.maxWorkforce = self.sovereigntyResourceSvc.GetMaxPowerAndWorkforce(solarSystemID)
        self._allowedTypeIDs = evetypes.GetTypeIDsByGroups(upgrades_const.UPGRADE_GROUP_IDS)
        self._accessGroupOptions = None
        self._availableHubResources = None
        self._simulatedInstalledUpgrades = None
        self._originalInstalledUpgradeData = None
        self._newUpgrades = {}
        self._currentFuelACL = fuelACL
        self._tempWorkforceMode = 1
        self._hubReagentsByTypeID = {}
        self.on_order_changed = Signal(signalName='order_changed')
        self.on_online_state_changed = Signal(signalName='on_online_state_changed')
        self.on_acl_changed = Signal(signalName='on_acl_changed')
        self.on_acl_setting_failed = Signal(signalName='on_acl_setting_failed')
        self.on_upgrades_changed = Signal(signalName='on_upgrades_changed')
        self.on_legend_moused_over = Signal(signalName='on_legend_moused_over')
        sm.RegisterNotify(self)
        uthread2.StartTasklet(self.PrimeSovHubInfo)

    def IsSameItemID(self, itemID):
        return self.itemID == itemID

    @property
    def itemID(self):
        return self._itemID

    @property
    def solarSystemID(self):
        return self._solarSystemID

    @property
    def fuelACL(self):
        return self._currentFuelACL

    @property
    def availablePower(self):
        self._PrimeAvailableResources()
        return self._availableHubResources.power_available

    @property
    def availableWorkforce(self):
        self._PrimeAvailableResources()
        return self._availableHubResources.workforce_available

    @property
    def localHarvestWorkforce(self):
        self._PrimeAvailableResources()
        return self._availableHubResources.workforce_local_harvest

    def PrimeData(self):
        parallelCalls = [(self._PrimeInstalledUpgrades, ()),
         (self._PrimeAvailableResources, ()),
         (self._PrimeStaticDataForUpgrades, ()),
         (self._PrimeGetReagentsByTypeID, ())]
        installedError, _, failureStatus, _ = uthread.parallel(parallelCalls)
        if NOT_AVAILABLE in (installedError, failureStatus):
            raise SovUpgradeDataUnavailableError()

    def _PrimeInstalledUpgrades(self):
        if self.installedUpgradesSimulated is not None:
            return
        with locks.TempLock('HubController_Prime_upgrades%s' % self._itemID):
            if self.installedUpgradesSimulated is None:
                installedUpgrades = self._GetInstalledUpgrades()
                if installedUpgrades == NOT_AVAILABLE:
                    return NOT_AVAILABLE
                self._simulatedInstalledUpgrades = [ UpgradeData.create_from_installed_upgrade_data(x, self.sovHubSvc) for x in installedUpgrades ]
                self._originalInstalledUpgradeData = [ x.take_copy() for x in installedUpgrades ]

    def _GetInstalledUpgrades(self):
        installedUpgradesOriginal = self.quasarCallWrapper.GetInstalledUpgradesForHub(self._itemID)
        if installedUpgradesOriginal == DATA_NOT_AVAILABLE:
            return NOT_AVAILABLE
        return installedUpgradesOriginal

    def _PrimeAvailableResources(self):
        if self.AreResourcesSet():
            return
        with locks.TempLock('GetAvailableHubResources_%s' % self.itemID):
            if self.AreResourcesSet():
                return
            availableSovHubResources = self.sovereigntyResourceSvc.GetAvailableHubResources(self.itemID)
            self._availableHubResources = availableSovHubResources

    def _PrimeStaticDataForUpgrades(self):
        failureStatus = self.quasarCallWrapper.PrimeStaticDataForUpgrades()
        return failureStatus

    def AreResourcesSet(self):
        return self._availableHubResources is not None

    def _PrimeGetReagentsByTypeID(self):
        reagentsByTypeID = self.sovHubSvc.GetReagentsByTypeID(self._itemID)
        self._hubReagentsByTypeID = {x:y.take_copy() for x, y in reagentsByTypeID.iteritems()}

    def GetInstalledUpgradesEntryControllers(self):
        dataList = []
        self.UpdateEffectiveStatesForSimulatedUpgrades()
        for i, installedUpgrade in enumerate(self.installedUpgradesSimulated):
            upgradeData = UpgradeEntryController(installedUpgrade, i, self, installedUpgrade.powerState)
            dataList.append(upgradeData)

        return dataList

    def GetNoInstalledUpgradesHint(self):
        if self.solarSystemID == session.solarsystemid:
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/DropUpgradesToAdd')
        else:
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/NoUpgradesInstalled')

    def VerifyStateIsCorrectOnFirstLoad(self):
        simulated = {x.typeID:x.powerState for x in self.installedUpgradesSimulated}
        original = {x.upgrade_type_id:x.power_state for x in self.originalInstalledUpgradeData}
        if simulated != original:
            eve.Message('CustomInfo', {'info': 'There seems to be a mismatch'})

    def GetDropError(self, data):
        isEntryInWnd = isinstance(data, UpgradeTypeDragData)
        if isEntryInWnd:
            return
        if data.__guid__ not in ('xtriui.InvItem', 'listentry.InvItem'):
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/SovHubUpgradeCannotBeAddedNotItem')
        dataTypeID = data.invtype
        if not self._IsTypeAllowed(dataTypeID):
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/SovHubUpgradeCannotBeAddedTypeNotValid')
        if not self._IsUpgradeAllowed(dataTypeID):
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/SovHubUpgradeCannotBeAddedAlreadyInstalled')
        if self._IsInMutuallyExclusiveGroup(dataTypeID):
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/UpgradeSlotFilled')
        if not self._IsEnoughPowerLeftInSystem(dataTypeID):
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/NotEnoughPower')
        if not isEntryInWnd and not self._IsInTransferRange():
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/SovHubUpgradeCannotBeAddedNotInRange')
        if not self._IsSovReqMet(dataTypeID):
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/SovHubUpgradeCannotBeAddedSovLevelTooLow')
        if data.rec.locationID != session.shipid:
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/SovHubUpgradeCannotBeAddedNotInShip')

    def _IsTypeAllowed(self, typeID):
        return typeID in self._allowedTypeIDs

    def _IsUpgradeAllowed(self, typeID):
        currentTypeIDs = [ x.typeID for x in self.installedUpgradesSimulated ]
        if typeID in currentTypeIDs:
            return False
        return True

    def _IsInTransferRange(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return False
        if session.shipid not in bp.balls:
            return False
        if self.itemID not in bp.balls:
            return False
        dist = bp.DistanceBetween(session.shipid, self.itemID)
        if dist is None:
            return False
        if dist > const.maxCargoContainerTransferDistance:
            return False
        return True

    def _IsEnoughPowerLeftInSystem(self, typeID):
        upgradeStaticData = self.sovHubSvc.GetStaticDataForUpgrade(typeID)
        installedPower = self.GetSimulatedPowerOfAllInstalled()
        if upgradeStaticData.power + installedPower > self.maxPower:
            return False
        return True

    def _IsInMutuallyExclusiveGroup(self, typeID):
        upgradeStaticData = self.sovHubSvc.GetStaticDataForUpgrade(typeID)
        mutually_exclusive_group = upgradeStaticData.mutually_exclusive_group
        for upgrade in self.installedUpgradesSimulated:
            if upgrade.staticData.mutually_exclusive_group == mutually_exclusive_group:
                return True

        return False

    def _IsSovReqMet(self, typeID):
        requiredSovereigntyLevel = int(sm.GetService('godma').GetTypeAttribute(typeID, const.attributeDevIndexSovereignty, 0))
        if requiredSovereigntyLevel:
            if self.systemClaimTime is None:
                return False
            sovHeldFor = (blue.os.GetWallclockTime() - self.systemClaimTime) / const.DAY
            if devIndexUtil.GetTimeIndexLevelForDays(sovHeldFor) < requiredSovereigntyLevel:
                return False
        return True

    @property
    def systemClaimTime(self):
        if self._systemClaimTime == NOT_DEFINED:
            iHubInfo = self.sovSvc.GetInfrastructureHubInfo(self.solarSystemID)
            if iHubInfo:
                self._systemClaimTime = iHubInfo.claimTime
            else:
                self._systemClaimTime = None
        return self._systemClaimTime

    def PrimeSovHubInfo(self):
        self.systemClaimTime

    def DoDropData(self, dragObj, entries, idx = -1):
        if not entries:
            return
        data = entries[0]
        if isinstance(data, UpgradeTypeDragData):
            self.DoMove(data, idx)
        elif data.__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            dropError = self.GetDropError(data)
            if dropError:
                eve.Message('CustomNotify', {'notify': dropError})
                return
            dataTypeID = data.invtype
            rec = data.rec
            itemID = rec.itemID
            self._newUpgrades[rec.itemID] = rec
            upgradeData = self._GetUpgradeDataForUpgradeItem(dataTypeID, itemID)
            if idx < 0:
                self.installedUpgradesSimulated.append(upgradeData)
            else:
                self.installedUpgradesSimulated.insert(idx, upgradeData)
            self.on_order_changed()
            self.on_online_state_changed(dataTypeID)
        else:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Sovereignty/SovHub/Upgrades/SovHubUpgradeCannotBeAddedNotItem')})

    def _GetUpgradeDataForUpgradeItem(self, typeID, itemID):
        staticData = self.sovHubSvc.GetStaticDataForUpgrade(typeID)
        return UpgradeData(typeID, True, staticData, itemID=itemID)

    def DoMove(self, data, newIdx):
        fromIdx = data.idx
        upgradeInfo = self.installedUpgradesSimulated.pop(fromIdx)
        if newIdx < 0:
            self.installedUpgradesSimulated.append(upgradeInfo)
        else:
            if fromIdx < newIdx:
                newIdx -= 1
            self.installedUpgradesSimulated.insert(newIdx, upgradeInfo)
        self.on_order_changed()
        self.on_online_state_changed(upgradeInfo.typeID)

    def DeleteUpgrade(self, typeID, upgradeKey, itemID):
        if itemID:
            self._newUpgrades.pop(itemID, None)
        else:
            buttons = [Bundle(id=uiconst.ID_YES, label=GetByLabel('UI/Sovereignty/SovHub/HubWnd/ProceedBtn')), Bundle(id=uiconst.ID_CANCEL, label=GetByLabel('UI/Common/Buttons/Cancel'))]
            if eve.Message('ConfirmDestroyUpgrade', {}, buttons=buttons, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return
            try:
                self.sovHubSvc.UninstallUpgrade(upgradeKey)
            except (SovUpgradeUninstallError, TimeoutException):
                logger.exception('Failed to delete upgrade')
                eve.Message('CustomInfo', {'info': GetByLabel('UI/Sovereignty/SovHub/Upgrades/FailedToRemoveUpgrade')})
                return
            except Exception as e:
                eve.Message('CustomInfo', {'info': GetByLabel('UI/Sovereignty/SovHub/Upgrades/FailedToRemoveUpgrade')})
                raise

        for upgrade in self.installedUpgradesSimulated:
            if upgrade.typeID == typeID:
                self.installedUpgradesSimulated.remove(upgrade)
                break

        self.on_order_changed()
        self.on_online_state_changed(typeID)

    def SetOnlineState(self, typeID, onlineState):
        if onlineState:
            newState = upgrades_const.POWER_STATE_ONLINE
        else:
            newState = upgrades_const.POWER_STATE_OFFLINE
        for upgrade in self.installedUpgradesSimulated:
            if upgrade.typeID == typeID:
                upgrade.powerState = newState
                break

        self.on_online_state_changed(typeID)

    def AreThereUnsavedChanges(self):
        if self.installedUpgradesSimulated is None or self.originalInstalledUpgradeData is None:
            return False
        simulatedConfig = [ (x.typeID, x.isConfiguredOnline) for x in self.installedUpgradesSimulated ]
        originalConfig = [ (x.upgrade_type_id, not x.is_power_offline) for x in self.originalInstalledUpgradeData ]
        if simulatedConfig != originalConfig:
            return True
        return False

    def SaveChanges(self, *args):
        data = {'currentUpgrades': self.installedUpgradesSimulated,
         'originalUpgrades': self.originalInstalledUpgradeData}
        buttons = [Bundle(id=uiconst.ID_YES, label=GetByLabel('UI/Sovereignty/SovHub/HubWnd/ProceedBtn')), Bundle(id=uiconst.ID_CANCEL, label=GetByLabel('UI/Common/Buttons/Cancel'))]
        if eve.Message('ConfirmSovHubUpgradeChanges', data, buttons=buttons, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        newUpgrades = self._newUpgrades.keys()
        installed = [ (upgrade.typeID, upgrade.isConfiguredOnline) for upgrade in self.installedUpgradesSimulated ]
        powerStatesBeforeSaving = [ (upgrade.typeID, upgrade.powerState) for upgrade in self.installedUpgradesSimulated ]
        try:
            result = self.sovHubSvc.SaveUpgradeConfiguration(self.itemID, newUpgrades, installed)
        except SovUpgradeInstallError as e:
            eve.Message('SovHubChangeNotSaved')
            raise
        except TimeoutException as e:
            eve.Message('SovHubChangeNotSavedTimeout')
            raise

        self._newUpgrades.clear()
        powerStatesAfterSaving = [ (x.upgrade_type_id, x.power_state) for x in result ]
        success = powerStatesBeforeSaving == powerStatesAfterSaving
        if success:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Sovereignty/SovHub/HubWnd/ConfigurationSuccessfullySaved')})
        else:
            eve.Message('CustomInfo', {'info': GetByLabel('UI/Sovereignty/SovHub/HubWnd/ConfigurationSavedNotSame')})
            logger.exception('SovHubWnd: Unexpected state after save')
        self.on_order_changed()

    def SetFuelACL(self, fuelACL):
        try:
            self.sovSvc.SetSovHubFuelAccessGroup(self.solarSystemID, fuelACL)
        except UserError:
            self.on_acl_setting_failed()
            raise

        self._currentFuelACL = fuelACL
        self.on_acl_changed()

    @property
    def accessGroupOptions(self):
        if self._accessGroupOptions is None:
            from eve.client.script.ui.inflight.orbitalConfiguration import GetAccessGroupOptions
            self._accessGroupOptions = GetAccessGroupOptions()
            if self._currentFuelACL not in [ x[1] for x in self._accessGroupOptions ]:
                self.AddGroup(self._currentFuelACL, False)
        return self._accessGroupOptions

    def AddGroup(self, newGroupID, raiseGroupNotFound = True):
        if newGroupID:
            try:
                newGroup = sm.GetService('structureControllers').GetAccessGroupController().GetGroupInfoFromID(newGroupID, fetchToServer=True)
            except UserError as e:
                if e.msg == 'GroupNotFound' and not raiseGroupNotFound:
                    return
                raise

            groupDisplayName = cfg.eveowners.Get(newGroup.creatorID).name if IsNPCCorporation(newGroup.creatorID) else newGroup.name
            self._accessGroupOptions.append((groupDisplayName, newGroupID))

    def GetNumSimulatedUpgradesOnlineAndInstalled(self):
        self.UpdateEffectiveStatesForSimulatedUpgrades()
        return (len([ x for x in self.installedUpgradesSimulated if x.isPowerStateFunctional ]), len(self.installedUpgradesSimulated))

    def GetSimulatedPowerAllocated(self):
        fuelAmounts = self.GetRagentAmountByTypeID()
        return GetPowerForUpgrades(self.installedUpgradesSimulated, self.availablePower, self.availableWorkforce, fuelAmounts)

    def GetSimulatedPowerAllocatedText(self):
        return FmtAmt(self.GetSimulatedPowerAllocated())

    GetPowerAllocated = GetSimulatedPowerAllocated
    GetPowerAllocatedText = GetSimulatedPowerAllocatedText

    def GetSimulatedWorkforce(self):
        fuelAmounts = self.GetRagentAmountByTypeID()
        return GetWorkforceForUpgrades(self.installedUpgradesSimulated, self.availablePower, self.availableWorkforce, fuelAmounts)

    def GetSimulatedWorkforceText(self):
        return FmtAmt(self.GetSimulatedWorkforce())

    GetWorkforce = GetSimulatedWorkforce
    GetWorkforceText = GetSimulatedWorkforceText

    def GetReagentForTypeID(self, typeID):
        return self._hubReagentsByTypeID.get(typeID, None)

    def GetRagentAmountByTypeID(self):
        return {typeID:x.amount_now for typeID, x in self._hubReagentsByTypeID.iteritems()}

    def GetSimulatedReagentConsumptionForTypeID(self, reagentTypeID):
        fuelAmounts = self.GetRagentAmountByTypeID()
        return GetConsumptionPerHour(self.installedUpgradesSimulated, reagentTypeID, availablePower=self.availablePower, availableWorkforce=self.availableWorkforce, fuelAmounts=fuelAmounts)

    GetReagentConsumptionForTypeID = GetSimulatedReagentConsumptionForTypeID

    def GetSimulatedStartupCostForTypeID(self, reagentTypeID):
        fuelAmounts = self.GetRagentAmountByTypeID()
        return GetStartupCost(self.installedUpgradesSimulated, self.originalInstalledUpgradeData, reagentTypeID, availablePower=self.availablePower, availableWorkforce=self.availableWorkforce, fuelAmounts=fuelAmounts)

    GetStartupCostForTypeID = GetSimulatedStartupCostForTypeID

    def GetSimulatedTimeLeftForTypeID(self, reagentTypeID):
        fuelAmounts = self.GetRagentAmountByTypeID()
        if reagentTypeID not in fuelAmounts:
            return None
        return GetHoursLeft(self.installedUpgradesSimulated, self.originalInstalledUpgradeData, reagentTypeID, availablePower=self.availablePower, availableWorkforce=self.availableWorkforce, fuelAmounts=fuelAmounts)

    GetTimeLeftForTypeID = GetSimulatedTimeLeftForTypeID

    def GetSimulatedTimeLeftProgressForTypeID(self, reagentTypeID):
        hoursLeft = self.GetSimulatedTimeLeftForTypeID(reagentTypeID)
        return GetHoursLeftProgress(hoursLeft)

    GetTimeLeftProgressForTypeID = GetSimulatedTimeLeftProgressForTypeID

    def GetTimeLeftTextForTypeID(self, reagentTypeID):
        hoursLeft = self.GetSimulatedTimeLeftForTypeID(reagentTypeID)
        return GetTimeLeftTextForTypeID(hoursLeft)

    def GetSimulatedPowerOfAllInstalled(self):
        power = 0
        for upgrade in self.installedUpgradesSimulated:
            power += upgrade.staticData.power

        return power

    def GetOriginalPower(self):
        pass

    def GetOriginalWorkforce(self):
        pass

    def GetAvailablePower(self):
        return self.availablePower

    def GetAvailablePowerText(self):
        return FmtAmt(self.GetAvailablePower())

    def GetAvailableWorkforce(self):
        return self.availableWorkforce

    def GetAvailableBaseWorkforceText(self):
        localWorkforce = self.localHarvestWorkforce
        return FmtAmt(localWorkforce)

    def GetImportedValue(self):
        return self.workforceController.GetImportedWorkforceFromState()

    def GetImportedValueTextAndHint(self):
        imported = self.GetImportedValue()
        if not imported:
            return ('', '')
        hint = GetByLabel('UI/Sovereignty/SovHub/HubWnd/ImportedWorkforce')
        return (eveformat.color('+%s' % FmtAmt(imported), eveColor.SUCCESS_GREEN_HEX), hint)

    def GetExportedValue(self):
        return self.workforceController.GetExportedWorkforceFromState()

    def GetWorkforceAddition(self):
        return -self.GetImportedValue() or self.GetExportedValue()

    def GetPowerLowStateUpgrades(self):
        power = 0
        self.UpdateEffectiveStatesForSimulatedUpgrades()
        for upgrade in self.installedUpgradesSimulated:
            if upgrade.isInRestrictedPowerState:
                power += upgrade.staticData.power

        return power

    def GetWorkforceLowStateUpgrades(self):
        workforce = 0
        self.UpdateEffectiveStatesForSimulatedUpgrades()
        for upgrade in self.installedUpgradesSimulated:
            if upgrade.isInRestrictedPowerState:
                workforce += upgrade.staticData.workforce

        return workforce

    def UpdateEffectiveStatesForSimulatedUpgrades(self):
        fuelAmounts = self.GetRagentAmountByTypeID()
        return UpdateEffectiveStatesForUpgrades(self.installedUpgradesSimulated, self.availablePower, self.availableWorkforce, fuelAmounts)

    @property
    def originalInstalledUpgradeData(self):
        return self._originalInstalledUpgradeData

    @property
    def installedUpgradesSimulated(self):
        return self._simulatedInstalledUpgrades

    def GetAclName(self):
        if self._currentFuelACL is None:
            return GetByLabel('UI/Sovereignty/SovHub/HubWnd/SectionACLNotSet')
        for displayName, groupID in self.accessGroupOptions:
            if groupID == self._currentFuelACL:
                return displayName

        try:
            newGroup = sm.GetService('structureControllers').GetAccessGroupController().GetGroupInfoFromID(self._currentFuelACL, fetchToServer=True)
        except UserError as e:
            if e.msg == 'GroupNotFound':
                return GetByLabel('UI/Sovereignty/UnknownACL')
            raise

        if newGroup:
            if IsNPCCorporation(newGroup.creatorID):
                return cfg.eveowners.Get(newGroup.creatorID).name
            return newGroup.name

    def GetHubName(self):
        systemName = cfg.evelocations.Get(self.solarSystemID).name
        caption = GetByLabel('UI/Sovereignty/SovHub/HubWnd/SovHubName', solarSystemName=systemName)
        return caption

    def CanEditACL(self):
        return session.corprole & const.corpRoleDirector

    def OnHubUpgradesStateChanged(self, hubID, installedUpgrades):
        if hubID != self.itemID:
            return
        eve.Message('CustomNotify', {'notify': GetByLabel('UI/Sovereignty/SovHub/Upgrades/UpgradesUpdated')})
        self._originalInstalledUpgradeData = [ x.take_copy() for x in installedUpgrades ]
        simulatedByTypeID = {x.typeID:x for x in self.installedUpgradesSimulated}
        for originalUpgrade in self._originalInstalledUpgradeData:
            simulatedUpgrade = simulatedByTypeID.pop(originalUpgrade.upgrade_type_id, None)
            if simulatedUpgrade:
                simulatedUpgrade.UpdateOriginalUpgrade(originalUpgrade)
            else:
                newSimulated = UpgradeData.create_from_installed_upgrade_data(originalUpgrade, self.sovHubSvc)
                self._simulatedInstalledUpgrades.append(newSimulated)

        for simulatedUpgrade in simulatedByTypeID.itervalues():
            if simulatedUpgrade in self._simulatedInstalledUpgrades:
                self._simulatedInstalledUpgrades.remove(simulatedUpgrade)

        self._availableHubResources = None
        self.workforceController.workforceState = None
        self._PrimeGetReagentsByTypeID()
        self.on_upgrades_changed()

    def OnHubWorkforceConfigureChanged(self, solarSystemID, sovHubID, oldConfig, newConfig):
        if solarSystemID != self.solarSystemID:
            return
        self._availableHubResources = None
        self.workforceController.UpdateWorkforceConfiguration(newConfig)

    def OnHubWorkforceStateChanged(self, solarSystemID, sovHubID, oldState, newState):
        if solarSystemID != self.solarSystemID:
            return
        self._availableHubResources = None
        self.workforceController.UpdateWorkforceState(newState)

    def Disconnect(self):
        self.on_order_changed.clear()
        self.on_online_state_changed.clear()
        self.on_acl_changed.clear()
        self.on_acl_setting_failed.clear()
        self.on_upgrades_changed.clear()
        sm.UnregisterNotify(self)
