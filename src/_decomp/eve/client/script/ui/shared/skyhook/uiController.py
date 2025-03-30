#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skyhook\uiController.py
import numbers
import evetypes
import gametime
from brennivin.itertoolsext import Bundle
from carbon.common.script.util.format import FmtDate, FmtAmt
from const import SEC
from dogma.const import attributeSpecialColonyResourcesHoldCapacity
from eve.client.script.environment.invControllers import ShipColonyResourcesHold, ShipCargo
from eve.client.script.ui.eveColor import CHERRY_RED_HEX, CRYO_BLUE_HEX, LED_GREY_HEX
from eve.client.script.ui.shared.skyhook import NOT_AVAILABLE, UNDEFINED
from evelink import Link, format_show_info_url
from evelink.client import corporation_link, type_link
from inventorycommon import const as invConst
from inventorycommon.const import typeInfrastructureHub
from localization import GetByLabel
import orbitalSkyhook.resourceRichness as resourceRichness
from publicGateway.grpc.exceptions import GenericException
from signals import Signal
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError
from sovereignty.skyhook.client.errors import SkyhookNotFoundError, SkyhookDeactivateForbiddenError, SkyhookActivateForbiddenError, SkyhookDeactivateInternalError
from sovereignty.skyhook.shared.skyhook_type_inference import get_skyhook_type_and_amount, POWER, WORKFORCE
from spacecomponents.client.components.orbitalSkyhook import ExtractReagentsToShip
from stackless_response_router.exceptions import TimeoutException
from spacecomponents.common.componentConst import LINK_WITH_SHIP
import logging
logger = logging.getLogger(__name__)
TEXT_NOTIFY_FORBIDDEN_ONLINE = 'Forbidden to set skyhook online'
TEXT_NOTIFY_COULDNT_ONLINE = "couldn't set online, Timed out"
TEXT_FORBIDDEN_OFFLINE = 'Forbidden to set skyhook online'
TEXT_FAILED_OFFLINE = 'Failed to set skyhook offline'
TEXT_TIMEOUT_OFFLINE = "couldn't set offline, Timed out"

class CurrentSkyhookUiController(object):
    __notifyevents__ = ['OnLinkedShipChanged']

    def __init__(self, itemID, isAuthorisedToTake):
        self._itemID = itemID
        self._reagentTypeID = UNDEFINED
        self._slimItem = UNDEFINED
        self._planetID = UNDEFINED
        self._linkedShipID = UNDEFINED
        self._isAuthorisedToTake = isAuthorisedToTake
        self.selectedQty = None
        self.product = None
        self.productAmount = 0
        self.sovereigntyResourceSvc = sm.GetService('sovereigntyResourceSvc')
        self.on_linked_ship_updated = Signal()
        sm.RegisterNotify(self)

    def __del__(self):
        sm.UnregisterNotify(self)

    def OnLinkedShipChanged(self, linkItemID, linkedShipID):
        if linkItemID != self.reagentSiloItemID:
            return
        self._linkedShipID = linkedShipID
        self.on_linked_ship_updated(linkItemID, linkedShipID)

    def IsSameItemID(self, itemID):
        return self._itemID == itemID

    @property
    def itemID(self):
        return self._itemID

    @property
    def isAuthorisedToTake(self):
        return self._isAuthorisedToTake

    @property
    def slimItem(self):
        if self._slimItem == UNDEFINED:
            self._slimItem = sm.GetService('michelle').GetItem(self.itemID)
        return self._slimItem

    @property
    def reagentTypeID(self):
        if self._reagentTypeID == UNDEFINED:
            self._reagentTypeID = self.GetPlanetReagentType()
        return self._reagentTypeID

    @property
    def planetID(self):
        if self._planetID == UNDEFINED:
            self._planetID = self.slimItem.planetID
        return self._planetID

    @property
    def reagentSiloItemID(self):
        return self.slimItem.reagentSiloItemID

    @property
    def linkedShipID(self):
        if self._linkedShipID == UNDEFINED:
            if self.reagentSiloItemID is None:
                self._linkedShipID = None
            else:
                ballpark = sm.GetService('michelle').GetBallpark()
                linkComponent = ballpark.componentRegistry.GetComponentForItem(self.reagentSiloItemID, LINK_WITH_SHIP)
                self._linkedShipID = linkComponent.linkedShipID
        return self._linkedShipID

    def GetSkyhookName(self):
        return GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/SlimSkyhookName', typeID=self.slimItem.typeID, planetID=self.planetID)

    def GetOwnerID(self):
        slimItem = sm.GetService('michelle').GetItem(self._itemID)
        return slimItem.ownerID

    def GetOwnerName(self):
        ownerID = self.GetOwnerID()
        if ownerID:
            return corporation_link(ownerID)
        return '-'

    def GetResourceDestInfo(self):
        solarsystemStructureInfo = sm.GetService('sov').GetSovStructuresInfoForSolarSystem(session.solarsystemid2)
        for s in solarsystemStructureInfo:
            if s.typeID == typeInfrastructureHub:
                return s

    def GetResourceDestName(self):
        destInfo = self.GetResourceDestInfo()
        if not destInfo:
            return '-'
        solarSystemName = cfg.evelocations.Get(destInfo.solarSystemID).name
        itemName = '%s %s' % (solarSystemName, evetypes.GetName(destInfo.typeID))
        itemLink = Link(url=format_show_info_url(destInfo.typeID, destInfo.itemID), text=itemName)
        ownerName = corporation_link(destInfo.ownerID)
        text = '%s (%s)' % (itemLink, ownerName)
        return text

    def HasConfigRoles(self):
        if self.slimItem.ownerID != session.corpid:
            return False
        if session.corprole & const.corpRoleStationManager:
            return True
        return False

    def GetProductNameAndRichnessTexture(self):
        product = self.GetProduct()
        if not product:
            return (GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NoDataAvailable'), None, None)
        onlineState = self.GetOnlineState()
        amount = self.productAmount or 0
        text = ''
        texturePath = None
        hintPath = None
        textHint = None
        if isinstance(product, numbers.Number):
            amountPerMin = amount / 60.0
            text = '%s - %s' % (type_link(product), GetByLabel('UI/Sovereignty/AmountPerMinute', value=float(amountPerMin)))
            texturePath, hintPath = resourceRichness.GetPlanetReagentRichnessTexturePathAndHint(amount, product)
        elif product == POWER:
            if onlineState:
                text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/PowerAmount', amount=FmtAmt(self.productAmount))
            else:
                text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/PowerProductionOffline', amount=FmtAmt(self.productAmount))
            texturePath, hintPath = resourceRichness.GetPlanetPowerRichnessTexturePath(amount)
        elif product == WORKFORCE:
            text, texturePath, hintPath, textHint = self._GetWorkforceTextAndTexture(onlineState, amount)
        if text:
            return (text,
             texturePath,
             hintPath,
             textHint)
        return (GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NoDataAvailable'),
         None,
         None,
         None)

    def _GetWorkforceTextAndTexture(self, onlineState, amount):
        texturePath, hintPath = resourceRichness.GetPlanetWorkforceRichnessTexturePath(amount)
        textHint = None
        productAmount = self.productAmount
        currentWorkforceAmount = self.sovereigntyResourceSvc.GetCurrentWorkforceForSkyhook(self.itemID)
        if currentWorkforceAmount is not None and productAmount != currentWorkforceAmount:
            percentage_different = round((currentWorkforceAmount - self.productAmount) / float(self.productAmount) * 100)
            color = CHERRY_RED_HEX if percentage_different < 0 else CRYO_BLUE_HEX
            if onlineState:
                text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/WorkforceAmountModified', amount=FmtAmt(currentWorkforceAmount), perc=percentage_different, perc_color=color)
            else:
                text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/WorkforceOfflineModified', amount=FmtAmt(currentWorkforceAmount), perc=percentage_different, perc_color=color)
            textHint = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/WorkforceModifiedHint', amount=FmtAmt(currentWorkforceAmount), total_amount=FmtAmt(productAmount), perc=percentage_different, previous_color=LED_GREY_HEX)
            return (text,
             texturePath,
             hintPath,
             textHint)
        if onlineState:
            text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/WorkforceAmount', amount=FmtAmt(self.productAmount))
        else:
            text = GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/WorkforceOffline', amount=FmtAmt(self.productAmount))
        return (text,
         texturePath,
         hintPath,
         textHint)

    def _GetSkyhookData(self):
        try:
            skyhookData = self.sovereigntyResourceSvc.GetSkyhook(self.itemID)
        except Exception:
            return None

        return skyhookData

    def GetProduct(self):
        if self.product is None:
            skyhookData = self._GetSkyhookData()
            if skyhookData is None:
                return
            reagentDefinition = skyhookData.get_first_reagent_data()
            reagentTypeID = None
            reagentAmountsInfo = None
            if reagentDefinition is not None:
                reagentTypeID = reagentDefinition.type_id
                reagentAmountsInfo = (reagentDefinition.configuration.amount_per_period, reagentDefinition.configuration.period)
            power = self._GetProductDataForPlanet(self.sovereigntyResourceSvc.GetPlanetPowerProduction, skyhookData.resource_version)
            workforce = self._GetProductDataForPlanet(self.sovereigntyResourceSvc.GetPlanetWorkforceProduction, skyhookData.resource_version)
            self.product, self.productAmount = get_skyhook_type_and_amount(reagentTypeID, reagentAmountsInfo, power, workforce)
        return self.product

    def GetPlanetReagentType(self):
        skyhookData = self._GetSkyhookData()
        if skyhookData is None:
            return self._GetProductDataForPlanet(self.sovereigntyResourceSvc.GetPlanetReagentType)
        reagentData = skyhookData.get_first_reagent_data()
        if reagentData is not None:
            return reagentData.type_id

    def _GetProductDataForPlanet(self, func, version = None):
        try:
            return func(self._planetID, version)
        except DataUnavailableError as e:
            logger.exception('Failed to get colony data')
            return NOT_AVAILABLE

    def GetOnlineState(self):
        try:
            return self.sovereigntyResourceSvc.IsProductionActiveAtSkyhook(self.itemID)
        except SkyhookNotFoundError as e:
            logger.exception('Failed to find skyhook')
        except TimeoutException as e:
            logger.exception('Skyhook: Timed out while getting online state')
        except GenericException as e:
            logger.exception('Failed to find skyhook active state')

        return NOT_AVAILABLE

    def SetOnline(self):
        try:
            return self.sovereigntyResourceSvc.ActivateSkyhook(self.itemID)
        except SkyhookNotFoundError as e:
            logger.exception('Failed to find skyhook')
        except SkyhookDeactivateInternalError as e:
            logger.exception('Failed to deactivate skyhook')
        except SkyhookActivateForbiddenError as e:
            logger.exception('Forbidden to online skyhook')
            eve.Message('CustomNotify', {'notify': TEXT_NOTIFY_FORBIDDEN_ONLINE})
        except TimeoutException as e:
            logger.exception('Skyhook: Timed out while onlining')
            eve.Message('CustomNotify', {'notify': TEXT_NOTIFY_COULDNT_ONLINE})

    def SetOffline(self):
        try:
            return self.sovereigntyResourceSvc.DeactivateSkyhook(self.itemID)
        except SkyhookNotFoundError as e:
            logger.exception('Failed to find skyhook')
        except SkyhookDeactivateForbiddenError as e:
            logger.exception('Forbidden to offline skyhook')
            eve.Message('CustomNotify', {'notify': TEXT_FORBIDDEN_OFFLINE})
        except SkyhookDeactivateInternalError as e:
            logger.exception('Failed to deactivate skyhook')
            eve.Message('CustomNotify', {'notify': TEXT_FAILED_OFFLINE})
        except TimeoutException as e:
            logger.exception('Skyhook: Timed out while offlining')
            eve.Message('CustomNotify', {'notify': TEXT_TIMEOUT_OFFLINE})

    def GetStorageQtyAndCapacity(self):
        try:
            skyhook_data = self._GetSkyhookData()
            if skyhook_data is None:
                secure_amount, insecure_amount = self.sovereigntyResourceSvc.GetPlanetReagentMaxAmounts(self.planetID)
            else:
                reagent_data = skyhook_data.get_first_reagent_data()
                secure_amount, insecure_amount = reagent_data.configuration.secure_capacity, reagent_data.configuration.insecure_capacity
            return (secure_amount, insecure_amount)
        except SkyhookNotFoundError as e:
            logger.exception('Failed to find skyhook')
        except TimeoutException as e:
            logger.exception('Skyhook: Timed out while getting reagents in skyhook')
        except GenericException as e:
            logger.exception('Failed to find skyhook reagents')

        return NOT_AVAILABLE

    def GetAmountInStorageText(self):
        maxAmounts = self.GetStorageQtyAndCapacity()
        if maxAmounts == NOT_AVAILABLE:
            return (GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NoDataAvailable'), None)
        maxSecure, maxInsecure = maxAmounts
        totalMaxQty = maxSecure + maxInsecure
        reagentTypeID, secure_amount, insecure_amount = self.GetReagentsInSkyhook()
        if NOT_AVAILABLE in (reagentTypeID, secure_amount, insecure_amount):
            return (GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NoDataAvailable'), None)
        unitVolume = evetypes.GetVolume(reagentTypeID)
        secureVolume = secure_amount * unitVolume
        insecureVolume = insecure_amount * unitVolume
        totalVolume = round(secureVolume + insecureVolume)
        maxVolume = round(totalMaxQty * unitVolume)
        hintInfo = Bundle(secureVolume=round(secureVolume), maxSecureVolume=round(maxSecure * unitVolume), insecureVolume=round(insecureVolume), maxInsecureVolume=round(maxInsecure * unitVolume))
        return ('%s / %s ' % (FmtAmt(totalVolume), GetByLabel('UI/Contracts/ContractsWindow/NumericVolume', volume=FmtAmt(maxVolume))), hintInfo)

    def GetReagentsInSkyhook(self):
        try:
            skyhookData = self._GetSkyhookData()
            if skyhookData is None:
                return (NOT_AVAILABLE, NOT_AVAILABLE, NOT_AVAILABLE)
            reagentTypeID = skyhookData.get_first_reagent_data().type_id
            secure_amount, insecure_amount = self.sovereigntyResourceSvc.GetReagentsInSkyhookNow(self.itemID)
            return (reagentTypeID, secure_amount or 0, insecure_amount or 0)
        except DataUnavailableError as e:
            logger.exception('Failed to get colony data')
        except TimeoutException as e:
            logger.exception('Skyhook: Timed out while getting reagents in skyhook')
        except GenericException as e:
            logger.exception('Failed to find skyhook reagents')

        return (NOT_AVAILABLE, NOT_AVAILABLE, NOT_AVAILABLE)

    def GetNextReagentHarvestTimeAndAmount(self):
        try:
            nextTimestamp, amount, isFull = self.sovereigntyResourceSvc.GetNextReagentHarvestTimeAndAmount(self.itemID)
            if (nextTimestamp, amount, isFull) == (None, None, False):
                return (NOT_AVAILABLE,
                 NOT_AVAILABLE,
                 NOT_AVAILABLE,
                 False)
            period = self.sovereigntyResourceSvc.GetNextHarvestPeriod(self.itemID)
            previousTimestamp = nextTimestamp - period * SEC
            progressSec = (gametime.GetWallclockTime() - previousTimestamp) / SEC
            progress = progressSec / float(period)
            return (nextTimestamp,
             amount,
             progress,
             isFull)
        except DataUnavailableError as e:
            logger.exception('Failed to get colony data')
        except TimeoutException as e:
            logger.exception('Skyhook: Timed out while getting reagents in skyhook')
        except GenericException as e:
            logger.exception('Failed to find skyhook reagents')

        return (NOT_AVAILABLE,
         NOT_AVAILABLE,
         NOT_AVAILABLE,
         False)

    def GetNextReagentHarvestAmounts(self):
        try:
            secured, unsecured = self.sovereigntyResourceSvc.GetNextReagentHarvestAmounts(self.itemID)
            return (secured, unsecured)
        except DataUnavailableError as e:
            logger.exception('Failed to get colony data')
        except TimeoutException as e:
            logger.exception('Skyhook: Timed out while getting reagents in skyhook')
        except GenericException as e:
            logger.exception('Failed to find skyhook reagents')

        return (NOT_AVAILABLE, NOT_AVAILABLE)

    def ExtractReagentsToShip(self):
        if self.HasResourceBay():
            flagID = invConst.flagColonyResourcesHold
            holdController = ShipColonyResourcesHold()
        else:
            flagID = invConst.flagCargo
            holdController = ShipCargo()
        cap = holdController.GetCapacity()
        availableVolume = cap.capacity - cap.used
        selectedVolume = self.GetSelectedVolume()
        selectedQty = self.selectedQty
        if selectedVolume > availableVolume:
            qtyToExtract = int(availableVolume / evetypes.GetVolume(self.reagentTypeID))
        else:
            qtyToExtract = selectedQty
        if not qtyToExtract:
            if self.HasResourceBay():
                raise UserError('SkyhookNoUnitsFitInShipHold', {'holdName': holdController.GetName()})
            raise UserError('SkyhookNoUnitsFitInShipCargo')
        try:
            quantityExtracted = ExtractReagentsToShip(self.itemID, flagID, qtyToExtract)
            eve.Message('SkyhookExtractionSuccess', {'numUnits': quantityExtracted})
        except Exception:
            raise UserError('SkyhookExtractionFailed')

    def GetSelectedVolume(self):
        if self.reagentTypeID == NOT_AVAILABLE:
            return 0
        return self.selectedQty * evetypes.GetVolume(self.reagentTypeID)

    def HasResourceBay(self):
        return bool(sm.GetService('godma').GetAttributeValueByID(session.shipid, attributeSpecialColonyResourcesHoldCapacity))

    def GetTheftVulnerabilityForSkyhook(self):
        return self.sovereigntyResourceSvc.GetTheftVulnerabilityForSkyhook(self.itemID)
