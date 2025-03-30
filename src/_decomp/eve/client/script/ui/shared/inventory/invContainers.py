#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\invContainers.py
import threadutils
import uthread2
from carbonui import ButtonStyle, uiconst
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from eve.client.script.ui.crimewatch import crimewatchConst
from eve.client.script.ui.inflight.squadrons.fighterInvCont import FighterInvCont
from eve.client.script.ui.shared.container import _InvContBase, GetBasicSortOptions, GetSortMenuForOptionsOptions
from eve.client.script.ui.shared.redeem.redeemItem import RedeemItemSortData
import eve.client.script.environment.invControllers as invCtrl
import log
from eve.client.script.ui.shared.redeem.redeemUiConst import CREATION_DATE_SORT_KEY, EXPIRY_DATE_SORT_KEY
from eve.client.script.ui.shared.itemShip import ShipItemCard, ShipItemIcon
from eve.client.script.ui.structure.structureDeedInvCont import StructureDeedInvCont
from menu import MenuLabel
from inventorycommon.const import VIEWMODE_DETAILS, VIEWMODE_ICONS, VIEWMODE_LIST, VIEWMODE_CARDS

class _BaseCelestialContainer(_InvContBase):
    __guid__ = 'invCont._BaseCelestialContainer'
    __invControllerClass__ = None

    def ApplyAttributes(self, attributes):
        _InvContBase.ApplyAttributes(self, attributes)
        if self.invController.IsLootable():
            self.CheckCanTakeItems = sm.GetService('crimewatchSvc').CheckCanTakeItems
            self.restrictedFrame = Frame(parent=self, color=crimewatchConst.Colors.Yellow.GetRGBA(), state=uiconst.UI_HIDDEN)
            self.restrictedButton = None

    def RegisterSpecialActionButton(self, button):
        if self.invController.IsLootable() and button.name == invCtrl.LOOT_ALL_BUTTON_NAME:
            self.restrictedButton = button
            self._start_loot_rights_update_loop()

    @threadutils.threaded
    def _start_loot_rights_update_loop(self):
        while not self.destroyed:
            self._update_loot_rights()
            uthread2.sleep(0.25)

    def _is_access_restricted(self):
        return not self.CheckCanTakeItems(self.invController.itemID)

    def _update_loot_rights(self):
        if self.destroyed or self.restrictedButton.destroyed:
            return
        if self._is_access_restricted():
            self.restrictedFrame.Show()
            self.restrictedButton.style = ButtonStyle.WARNING
        else:
            self.restrictedFrame.Hide()
            self.restrictedButton.style = self.restrictedButton.default_style

    def _EnforceLootableContainerRestrictions(self, *args):
        if not self or self.destroyed:
            return False
        isAccessRestricted = False
        if uicore.uilib.mouseOver in (self, self.restrictedButton) or uicore.uilib.mouseOver.IsUnder(self) or uicore.uilib.mouseOver.IsUnder(self.restrictedButton):
            if not self.CheckCanTakeItems(self.invController.itemID):
                isAccessRestricted = True
        if isAccessRestricted:
            self.restrictedFrame.Show()
            self.restrictedButtonFill.Show()
        else:
            self.restrictedFrame.Hide()
            self.restrictedButtonFill.Hide()
        return True


class InventoryContainerWithItemTracking(_InvContBase):
    __notifyevents__ = _InvContBase.__notifyevents__ + ['OnInventoryLocationSeen']

    def __init__(self, *args, **kwargs):
        super(InventoryContainerWithItemTracking, self).__init__(*args, **kwargs)

    def GetItemPanel(self, itemID):
        for node in reversed(self.scroll.GetNodes()):
            if node:
                item = getattr(node, 'item', None)
                panel = getattr(node, 'panel', None)
                if item and panel:
                    if node.item.itemID == itemID:
                        return panel

    def GetAllItemPanels(self):
        panels = {}
        for node in self.scroll.GetNodes():
            if node:
                item = getattr(node, 'item', None)
                panel = getattr(node, 'panel', None)
                if item and panel:
                    itemID = node.item.itemID
                    panels[itemID] = panel

        return panels

    def OnInventoryLocationSeen(self, locationID):
        if self.invController.GetInventoryLocationID() != locationID:
            return
        itemPanels = self.GetAllItemPanels()
        for itemPanel in itemPanels.values():
            if itemPanel and itemPanel.IsTagged():
                itemPanel.HideTag()


class ShipCargo(InventoryContainerWithItemTracking):
    __guid__ = 'invCont.ShipCargo'
    __invControllerClass__ = invCtrl.ShipCargo


class POSRefinery(_BaseCelestialContainer):
    __guid__ = 'invCont.POSRefinery'
    __invControllerClass__ = invCtrl.POSRefinery


class POSCompression(_BaseCelestialContainer):
    __guid__ = 'invCont.POSCompression'
    __invControllerClass__ = invCtrl.POSCompression


class POSStructureCharges(_BaseCelestialContainer):
    __guid__ = 'invCont.POSStructureCharges'
    __invControllerClass__ = invCtrl.POSStructureCharges


class POSStructureChargeCrystal(POSStructureCharges):
    __guid__ = 'invCont.POSStructureChargeCrystal'
    __invControllerClass__ = invCtrl.POSStructureChargeCrystal


class POSStructureChargesStorage(_BaseCelestialContainer):
    __guid__ = 'invCont.POSStructureChargesStorage'
    __invControllerClass__ = invCtrl.POSStructureChargesStorage


class POSStrontiumBay(_BaseCelestialContainer):
    __guid__ = 'invCont.POSStrontiumBay'
    __invControllerClass__ = invCtrl.POSStrontiumBay


class POSFuelBay(_BaseCelestialContainer):
    __guid__ = 'invCont.POSFuelBay'
    __invControllerClass__ = invCtrl.POSFuelBay


class POSShipMaintenanceArray(_BaseCelestialContainer):
    __guid__ = 'invCont.POSShipMaintenanceArray'
    __invControllerClass__ = invCtrl.POSShipMaintenanceArray


class POSSilo(_BaseCelestialContainer):
    __guid__ = 'invCont.POSSilo'
    __invControllerClass__ = invCtrl.POSSilo


class POSMobileReactor(_BaseCelestialContainer):
    __guid__ = 'invCont.POSMobileReactor'
    __invControllerClass__ = invCtrl.POSMobileReactor


class POSPersonalHangar(_BaseCelestialContainer):
    __guid__ = 'invCont.POSPersonalHangar'
    __invControllerClass__ = invCtrl.POSPersonalHangar


class ItemWreck(_BaseCelestialContainer):
    __guid__ = 'invCont.ItemWreck'
    __invControllerClass__ = invCtrl.ItemWreck


class ItemFloatingCargo(_BaseCelestialContainer):
    __guid__ = 'invCont.ItemFloatingCargo'
    __invControllerClass__ = invCtrl.ItemFloatingCargo


class ItemSiphonPseudoSilo(_BaseCelestialContainer):
    __guid__ = 'invCont.ItemSiphonPseudoSilo'
    __invControllerClass__ = invCtrl.ItemSiphonPseudoSilo


class StationContainer(_BaseCelestialContainer):
    __guid__ = 'invCont.StationContainer'
    __invControllerClass__ = invCtrl.StationContainer


class AssetSafetyContainer(_BaseCelestialContainer):
    __guid__ = 'invCont.AssetSafetyContainer'
    __invControllerClass__ = invCtrl.AssetSafetyContainer


class ShipMaintenanceBay(_BaseCelestialContainer):
    __guid__ = 'invCont.ShipMaintenanceBay'
    __invControllerClass__ = invCtrl.ShipMaintenanceBay


class ShipDroneBay(_InvContBase):
    __guid__ = 'invCont.ShipDroneBay'
    __invControllerClass__ = invCtrl.ShipDroneBay


class ShipFighterBay(FighterInvCont):
    __guid__ = 'invCont.ShipFighterBay'
    __invControllerClass__ = invCtrl.ShipFighterBay


class ShipFrigateEscapeBay(_InvContBase):
    __guid__ = 'invCont.ShipFrigateEscapeBay'
    __invControllerClass__ = invCtrl.ShipFrigateEscapeBay


class ShipFuelBay(_InvContBase):
    __guid__ = 'invCont.ShipFuelBay'
    __invControllerClass__ = invCtrl.ShipFuelBay


class ShipGeneralMiningHold(_InvContBase):
    __guid__ = 'invCont.ShipGeneralMiningHold'
    __invControllerClass__ = invCtrl.ShipGeneralMiningHold


class ShipAsteroidHold(_InvContBase):
    __guid__ = 'invCont.ShipAsteroidHold'
    __invControllerClass__ = invCtrl.ShipAsteroidHold


class ShipIceHold(_InvContBase):
    __guid__ = 'invCont.ShipIceHold'
    __invControllerClass__ = invCtrl.ShipIceHold


class ShipGasHold(_InvContBase):
    __guid__ = 'invCont.ShipGasHold'
    __invControllerClass__ = invCtrl.ShipGasHold


class ShipMineralHold(_InvContBase):
    __guid__ = 'invCont.ShipMineralHold'
    __invControllerClass__ = invCtrl.ShipMineralHold


class ShipSalvageHold(_InvContBase):
    __guid__ = 'invCont.ShipSalvageHold'
    __invControllerClass__ = invCtrl.ShipSalvageHold


class ShipShipHold(_InvContBase):
    __guid__ = 'invCont.ShipShipHold'
    __invControllerClass__ = invCtrl.ShipShipHold


class ShipSmallShipHold(_InvContBase):
    __guid__ = 'invCont.ShipSmallShipHold'
    __invControllerClass__ = invCtrl.ShipSmallShipHold


class ShipMediumShipHold(_InvContBase):
    __guid__ = 'invCont.ShipMediumShipHold'
    __invControllerClass__ = invCtrl.ShipMediumShipHold


class ShipLargeShipHold(_InvContBase):
    __guid__ = 'invCont.ShipLargeShipHold'
    __invControllerClass__ = invCtrl.ShipLargeShipHold


class ShipIndustrialShipHold(_InvContBase):
    __guid__ = 'invCont.ShipIndustrialShipHold'
    __invControllerClass__ = invCtrl.ShipIndustrialShipHold


class ShipAmmoHold(_InvContBase):
    __guid__ = 'invCont.ShipAmmoHold'
    __invControllerClass__ = invCtrl.ShipAmmoHold


class ShipCommandCenterHold(_InvContBase):
    __guid__ = 'invCont.ShipCommandCenterHold'
    __invControllerClass__ = invCtrl.ShipCommandCenterHold


class ShipPlanetaryCommoditiesHold(_InvContBase):
    __guid__ = 'invCont.ShipPlanetaryCommoditiesHold'
    __invControllerClass__ = invCtrl.ShipPlanetaryCommoditiesHold


class ShipFleetHangar(_BaseCelestialContainer):
    __guid__ = 'invCont.ShipFleetHangar'
    __invControllerClass__ = invCtrl.ShipFleetHangar


class ShipQuafeHold(_InvContBase):
    __guid__ = 'invCont.ShipQuafeHold'
    __invControllerClass__ = invCtrl.ShipQuafeHold


class ShipCorpseHold(_InvContBase):
    __guid__ = 'invCont.ShipCorpseHold'
    __invControllerClass__ = invCtrl.ShipCorpseHold


class ShipBoosterHold(_InvContBase):
    __guid__ = 'invCont.ShipBoosterHold'
    __invControllerClass__ = invCtrl.ShipBoosterHold


class ShipSubsystemHold(_InvContBase):
    __guid__ = 'invCont.ShipSubsystemHold'
    __invControllerClass__ = invCtrl.ShipSubsystemHold


class ShipMobileDepotHold(_InvContBase):
    __guid__ = 'invCont.ShipMobileDepotHold'
    __invControllerClass__ = invCtrl.ShipMobileDepotHold


class ShipColonyResourcesHold(_InvContBase):
    __guid__ = 'invCont.ShipColonyResourcesHold'
    __invControllerClass__ = invCtrl.ShipColonyResourcesHold


class StationCorpDeliveries(_InvContBase):
    __guid__ = 'invCont.StationCorpDeliveries'
    __invControllerClass__ = invCtrl.StationCorpDeliveries


class AssetSafetyDeliveries(_InvContBase):
    __guid__ = 'invCont.AssetSafetyDeliveries'
    __invControllerClass__ = invCtrl.AssetSafetyDeliveries


class StationItems(InventoryContainerWithItemTracking):
    __guid__ = 'invCont.StationItems'
    __invControllerClass__ = invCtrl.StationItems
    __notifyevents__ = InventoryContainerWithItemTracking.__notifyevents__ + ['OnItemNameChange']

    def OnItemNameChange(self, *args):
        self.Refresh()


class RedeemItems(_InvContBase):
    __guid__ = 'invCont.RedeemItems'
    __invControllerClass__ = invCtrl.RedeemItems
    __notifyevents__ = _InvContBase.__notifyevents__ + ['OnItemNameChange']
    default_shouldShowHint = True

    def ApplyAttributes(self, attributes):
        super(RedeemItems, self).ApplyAttributes(attributes)
        self.shouldShowHint = attributes.get('shouldShowHint', self.default_shouldShowHint)
        if attributes.onSelectionChange:
            self.scroll.OnSelectionChange = attributes.onSelectionChange

    def OnItemNameChange(self, *args):
        self.Refresh()

    def AddItem(self, rec, index = None, fromWhere = None):
        pass

    def RemoveItem(self, item):
        pass

    def UpdateItem(self, rec, *etc):
        pass

    def SetItem(self, index, rec):
        pass

    def InitializeSortBy(self):
        self.sortIconsBy, self.sortIconsDir = settings.user.ui.Get('containerSortIconsBy_%s' % self.name, (CREATION_DATE_SORT_KEY, 1))

    def GetSortData(self, sortby, direction):
        sortData = []
        for rec in self.items:
            if rec is None:
                continue
            sortKey = RedeemItemSortData(rec).GetSortKey(sortby, direction)
            if not sortKey:
                log.LogError('Unknown sortkey used in container sorting', sortby, direction)
                continue
            sortData.append((sortKey, rec))

        return sortData

    def UpdateHint(self):
        if not self.shouldShowHint:
            return
        super(RedeemItems, self).UpdateHint()

    def GetContainerMenu(self):
        return GetRedeemContainerMenu(self)


def GetRedeemContainerMenu(containerWindow):
    m = [(MenuLabel('UI/Common/SelectAll'), containerWindow.SelectAll), (MenuLabel('UI/Inventory/InvertSelection'), containerWindow.InvertSelection)]
    sortOptions = GetRedeemSortOptions()
    m += [(MenuLabel('UI/Common/SortBy'), GetSortMenuForOptionsOptions(containerWindow, sortOptions))]
    return m


def GetRedeemSortOptions():
    sortOptions = [None,
     ('UI/RedeemWindow/TokenCreationDate', (CREATION_DATE_SORT_KEY, 1)),
     ('UI/RedeemWindow/TokenCreationDateReversed', (CREATION_DATE_SORT_KEY, 0)),
     None,
     ('UI/RedeemWindow/TokenExpiryDate', (EXPIRY_DATE_SORT_KEY, 0)),
     ('UI/RedeemWindow/TokenExpiryDateReversed', (EXPIRY_DATE_SORT_KEY, 1))]
    sortOptions += GetBasicSortOptions()
    return sortOptions


class StationShips(InventoryContainerWithItemTracking):
    __guid__ = 'invCont.StationShips'
    __invControllerClass__ = invCtrl.StationShips
    __notifyevents__ = InventoryContainerWithItemTracking.__notifyevents__ + ['OnItemNameChange', 'ProcessActiveShipChanged']
    default_containerViewMode = VIEWMODE_CARDS
    default_availableViewModes = (VIEWMODE_CARDS,
     VIEWMODE_ICONS,
     VIEWMODE_DETAILS,
     VIEWMODE_LIST)

    def ApplyAttributes(self, attributes):
        super(StationShips, self).ApplyAttributes(attributes)
        self.scroll.SetNodes_ = self.scroll.SetNodes
        self.scroll.SetNodes = self._SetScrollNodes

    def GetViewModeSettingKey(self):
        return u'stationShipsViewMode_{}'.format(self.name)

    def GetItemClass(self):
        if self.viewMode == VIEWMODE_CARDS:
            return ShipItemCard
        return ShipItemIcon

    def _SetScrollNodes(self, nodes):
        self._SortActiveShip(nodes)
        self.scroll.SetNodes_(nodes)

    def SetSortedItems(self, sortedList):
        self._SortActiveShip(sortedList)
        super(StationShips, self).SetSortedItems(sortedList)

    def _SortActiveShip(self, sortedList):
        activeShip = None
        for index, ship in enumerate(sortedList):
            if ship.itemID == session.shipid:
                if index != 0:
                    activeShip = ship
                break

        if activeShip:
            sortedList.remove(activeShip)
            sortedList.insert(0, activeShip)

    def OnItemNameChange(self, *args):
        self.Refresh()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.Refresh()


class StationCorpMember(_InvContBase):
    __guid__ = 'invCont.StationCorpMember'
    __invControllerClass__ = invCtrl.StationCorpMember

    def ApplyAttributes(self, attributes):
        _InvContBase.ApplyAttributes(self, attributes)
        sm.GetService('invCache').InvalidateLocationCache((const.containerHangar, self.invController.ownerID))

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, ownerID=attributes.ownerID)

    def Refresh(self):
        sm.GetService('invCache').InvalidateLocationCache((const.containerHangar, self.invController.ownerID))
        _InvContBase.Refresh(self)


class StationCorpHangar(_InvContBase):
    __guid__ = 'invCont.StationCorpHangar'
    __invControllerClass__ = invCtrl.StationCorpHangar

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, divisionID=attributes.divisionID)


class POSCorpHangar(_InvContBase):
    __guid__ = 'invCont.POSCorpHangar'
    __invControllerClass__ = invCtrl.POSCorpHangar

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, divisionID=attributes.divisionID)


class SpaceComponentInventory(_BaseCelestialContainer):
    __guid__ = 'invCont.SpaceComponentInventory'
    __invControllerClass__ = invCtrl.SpaceComponentInventory


class Structure(_InvContBase):
    __guid__ = 'invCont.Structure'
    __invControllerClass__ = invCtrl.Structure


class StructureAmmoBay(_InvContBase):
    __guid__ = 'invCont.StructureAmmoBay'
    __invControllerClass__ = invCtrl.StructureAmmoBay


class StructureFuelBay(_InvContBase):
    __guid__ = 'invCont.StructureFuelBay'
    __invControllerClass__ = invCtrl.StructureFuelBay


class StructureFighterBay(FighterInvCont):
    __guid__ = 'invCont.StructureFighterBay'
    __invControllerClass__ = invCtrl.StructureFighterBay


class StructureItemHangar(InventoryContainerWithItemTracking):
    __guid__ = 'invCont.StructureItemHangar'
    __invControllerClass__ = invCtrl.StructureItemHangar


class StructureShipHangar(StationShips):
    __guid__ = 'invCont.StructureShipHangar'
    __invControllerClass__ = invCtrl.StructureShipHangar


class StructureDeliveriesHangar(_InvContBase):
    __guid__ = 'invCont.StructureDeliveriesHangar'
    __invControllerClass__ = invCtrl.StructureDeliveriesHangar


class StructureCorpHangar(_InvContBase):
    __guid__ = 'invCont.StructureCorpHangar'
    __invControllerClass__ = invCtrl.StructureCorpHangar

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, divisionID=attributes.divisionID)


class StructureDeedBay(StructureDeedInvCont):
    __guid__ = 'invCont.StructureDeedBay'
    __invControllerClass__ = invCtrl.StructureDeedBay


class AssetSafetyCorpContainer(StructureCorpHangar):
    __guid__ = 'invCont.AssetSafetyCorpContainer'
    __invControllerClass__ = invCtrl.AssetSafetyCorpContainer


class StructureMoonMaterialBay(_InvContBase):
    __guid__ = 'invCont.StructureMoonMaterialBay'
    __invControllerClass__ = invCtrl.StructureMoonMaterialBay
