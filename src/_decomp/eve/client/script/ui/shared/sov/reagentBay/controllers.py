#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\reagentBay\controllers.py
from collections import defaultdict
import eveformat
import mathext
from caching import Memoize
from const import DAY
from dogma.const import attributeSpecialColonyResourcesHoldCapacity
from eve.client.script.environment.invControllers import ShipCargo, ShipColonyResourcesHold
from eve.client.script.ui.eveColor import SUCCESS_GREEN_HEX
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalWritten
from sovereignty.client.quasarCallWrapper import QuasarCallWrapper, DATA_NOT_AVAILABLE
from sovereignty.fuel.client.errors import SovFuelGetLevelsError, SovFuelAddRequestError
from sovereignty.fuel.client.data_types import Fuel
from stackless_response_router.exceptions import TimeoutException
import inventorycommon.const as invConst
import logging
logger = logging.getLogger(__name__)
REAGENT_TYPES = [invConst.typeColonyReagentIce, invConst.typeColonyReagentLava]

class ReagentBayWndController(object):

    def __init__(self, sovHubID, solarSystemID, isStationMgr):
        self.sovHubSvc = sm.GetService('sovHubSvc')
        self.quasarCallWrapper = QuasarCallWrapper(self.sovHubSvc)
        self._sovHubID = sovHubID
        self._solarSystemID = solarSystemID
        self._isStationMgr = isStationMgr
        self.busyDepositingItems = False
        self.depositBtnDelay = False
        self.useResourceHold = False

    @property
    def sovHubID(self):
        return self._sovHubID

    @property
    def solarSystemID(self):
        return self._solarSystemID

    @property
    def isStationMgr(self):
        return self._isStationMgr

    def IsSameItemID(self, sovHubID):
        return self.sovHubID == sovHubID

    def PrimeFuelByTypeID(self):
        if self.GetFuelByTypeID() == DATA_NOT_AVAILABLE:
            self.GetFuelByTypeID.clear_memoized(self)
            raise SovFuelGetLevelsError()

    @Memoize(1)
    def GetFuelByTypeID(self):
        fuelByTypeID = self.quasarCallWrapper.GetReagentsByTypeID(self.sovHubID)
        if fuelByTypeID == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        ret = {x:Fuel(x, 0, 0, None) for x in REAGENT_TYPES}
        ret.update(fuelByTypeID)
        return ret

    @Memoize
    def GetInstalledUpgrades(self):
        return self.quasarCallWrapper.GetInstalledUpgradesForHub(self.sovHubID)

    def GetNumOnlineAndInstalledUpgradesText(self):
        installedUpgrades = self.GetInstalledUpgrades()
        if installedUpgrades == DATA_NOT_AVAILABLE:
            return DATA_NOT_AVAILABLE
        numTotal = len(installedUpgrades)
        numOnline = len([ x for x in installedUpgrades if x.is_power_online ])
        return GetByLabel('UI/Sovereignty/SovHub/ReagentBay/NumUpgradesOnline', numOnline=numOnline, numTotal=numTotal)

    def CanSeeUpgrades(self):
        return self._isStationMgr

    def DoDepositItems(self, qtyByTypeID):
        self._MergeItemsBeforeDeposit(qtyByTypeID)
        cargoInvController = self.GetSelectedSourceHold()
        cargoItemsByTypeID = self.GetSortedItemsByTypeID(qtyByTypeID.keys(), cargoInvController)
        failedToMove = qtyByTypeID.copy()
        for typeID, qty in qtyByTypeID.iteritems():
            if qty <= 0:
                failedToMove.pop(typeID, None)
                continue
            qtyLeftToMove = qty
            typeItemsInCargo = cargoItemsByTypeID.get(typeID, [])
            if not typeItemsInCargo:
                failedToMove[typeID] = qty
                continue
            for rec in typeItemsInCargo:
                if qtyLeftToMove <= 0:
                    failedToMove.pop(typeID, None)
                    break
                qtyToMove = min(rec.stacksize, qtyLeftToMove)
                try:
                    self.sovHubSvc.AddFuel(rec.itemID, qtyToMove, self.sovHubID)
                    qtyLeftToMove -= qtyToMove
                except SovFuelAddRequestError as e:
                    logger.exception('Failed to add fuel')
                    break
                except TimeoutException as e:
                    logger.exception('Failed to add fuel due to timeout')
                    break

                if qtyLeftToMove <= 0:
                    failedToMove.pop(typeID, None)
                else:
                    failedToMove[typeID] = qtyLeftToMove

        self.GetFuelByTypeID.clear_memoized(self)
        return failedToMove

    def _MergeItemsBeforeDeposit(self, qtyByTypeID):
        cargoInvController = self.GetSelectedSourceHold()
        cargoItemsByTypeID = self.GetSortedItemsByTypeID(qtyByTypeID.keys(), cargoInvController)
        for typeID, qty in qtyByTypeID.iteritems():
            mergeData = []
            sourceContainerID = None
            destID = None
            typeItemsInCargo = cargoItemsByTypeID.get(typeID, [])
            if not typeItemsInCargo:
                continue
            qtyLeftToFind = qty
            for rec in typeItemsInCargo:
                if qtyLeftToFind <= 0:
                    break
                if sourceContainerID is None:
                    sourceContainerID = rec.locationID
                    destID = rec.itemID
                else:
                    mergeData.append((rec.itemID,
                     destID,
                     rec.stacksize,
                     rec))
                qtyLeftToFind -= rec.stacksize

            if sourceContainerID and len(mergeData):
                cargoInvController.MultiMerge(mergeData, sourceContainerID)

    def GetSortedItemsByTypeID(self, wantedTypeIDs, invController):
        unsortedItemsByTypeID = defaultdict(list)
        for rec in invController.GetItems():
            if rec.typeID in wantedTypeIDs:
                unsortedItemsByTypeID[rec.typeID].append(rec)

        sortedItemsByTypeID = {}
        for typeID, itemList in unsortedItemsByTypeID.items():
            sortedItemsByTypeID[typeID] = sorted(itemList, key=lambda x: x.stacksize, reverse=True)

        return sortedItemsByTypeID

    def GetQtyByTypeID_InHold(self):
        cargoInvController = self.GetSelectedSourceHold()
        cargoQtyByTypeID = defaultdict(int)
        for item in cargoInvController.GetItems():
            cargoQtyByTypeID[item.typeID] += item.stacksize

        return cargoQtyByTypeID

    def GetSelectedSourceHold(self):
        if self.useResourceHold:
            return ShipColonyResourcesHold()
        return ShipCargo()

    def GetQtyInCargoHintPath(self):
        if self.useResourceHold:
            return 'UI/Sovereignty/SovHub/ReagentBay/NumUnitsInReagentBay'
        return 'UI/Inflight/SpaceComponents/UnderConstruction/NumUnitsInCargo'

    def GetNoQtyInCargoHintPath(self):
        if self.useResourceHold:
            return 'UI/Sovereignty/SovHub/ReagentBay/NoSuchItemInInfrastructureHold'
        return 'UI/Inflight/SpaceComponents/UnderConstruction/NoSuchItemInCargo'

    def GetSourceOptions(self):
        if not self.HasResourceBay():
            return []
        cargoInvController = ShipCargo()
        resourceBayController = ShipColonyResourcesHold()
        options = []
        for invController in [resourceBayController, cargoInvController]:
            options.append((invController.GetName(),
             invController.GetInvID(),
             None,
             invController.GetIconName()))

        return options

    def GetComboPrefsKey(self):
        return ('char', 'ui', 'fittingInvCombo')

    def HasResourceBay(self):
        return bool(sm.GetService('godma').GetAttributeValueByID(session.shipid, attributeSpecialColonyResourcesHoldCapacity))


HOURS_IN_4_WEEKS = 672

class InputItemController(object):

    def __init__(self, typeID, qtyInCargo, burnedPerHour):
        self.typeID = typeID
        self.qtyInCargo = 0
        self._unitsInSovHub = qtyInCargo
        self._burnedPerHour = burnedPerHour

    @property
    def maxToAdd(self):
        maxToAdd = max(0, self.qtyInCargo)
        return maxToAdd

    @property
    def unitsInSovHub(self):
        return self._unitsInSovHub

    @unitsInSovHub.setter
    def unitsInSovHub(self, units):
        self._unitsInSovHub = units

    @property
    def burnedPerHour(self):
        return self._burnedPerHour

    @burnedPerHour.setter
    def burnedPerHour(self, value):
        self._burnedPerHour = value

    @property
    def amountBurnedIn4weeks(self):
        return self._burnedPerHour * HOURS_IN_4_WEEKS

    def GetWindowProgress(self, unitsInWnd):
        return self._GetProgressFromValue(unitsInWnd)

    def GetProgress(self, unitsInWnd):
        inSovHubProgress = self._GetProgressFromValue(self.unitsInSovHub)
        inWndProgress = self._GetProgressFromValue(unitsInWnd)
        return (inSovHubProgress, inWndProgress)

    def _GetProgressFromValue(self, value):
        if self.amountBurnedIn4weeks:
            progress = mathext.clamp(float(value) / self.amountBurnedIn4weeks, 0, 1)
        else:
            progress = 0
        return progress

    def GetTimesLeft(self, unitsInWnd):
        timeLeftInHub = self._GetTimeForFuel(self.unitsInSovHub)
        if not unitsInWnd:
            return timeLeftInHub
        timeAdded = self._GetTimeForFuel(unitsInWnd)
        if not timeAdded:
            return timeLeftInHub
        timeAdded = '+' + timeAdded
        return '%s %s' % (timeLeftInHub, eveformat.color(timeAdded, SUCCESS_GREEN_HEX))

    def _GetTimeForFuel(self, units):
        if self.burnedPerHour:
            hoursLeft = units / self.burnedPerHour
            daysLeft = hoursLeft / 24
            if daysLeft <= 0:
                return GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', days=0)
            timeLeftInBlue = int(daysLeft * DAY)
            text = FormatTimeIntervalWritten(timeLeftInBlue, showFrom='day', showTo='day')
            return text
        else:
            return ''
