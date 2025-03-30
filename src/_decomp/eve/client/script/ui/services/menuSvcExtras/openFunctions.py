#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuSvcExtras\openFunctions.py
import eveicon
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.uicore import uicore
from eve.client.script.environment import invControllers as invCtrl
from eve.client.script.ui.shared.AuditLogSecureContainerLogViewer import AuditLogSecureContainerLogViewer
from eve.client.script.ui.shared.bountyWindow import BountyWindow
from eve.client.script.ui.shared.factionalWarfare.infrastructureHub import FWInfrastructureHub
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.client.script.ui.shared.sov.reagentBay.reagentBayWnd import OpenReagnetBay
from eve.client.script.ui.station.repairshop.base_repairshop import RepairShopWindow
from eve.client.script.ui.structure.dropbox.dropboxWnd import DropboxWnd
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg
from globalConfig.getFunctions import IsPlayerBountyHidden
from inventorycommon.const import INVENTORY_ID_SHIP_CARGO
from menu import MenuLabel, MenuList
from localization import GetByLabel

def GetOpenShipHoldMenus(checker):
    entries = MenuList()
    itemID = checker.item.itemID
    if checker.OfferOpenCargoHold():
        entries.append(MenuEntryData(MenuLabel('UI/Commands/OpenCargoHold'), lambda : OpenShipHangarCargo([itemID]), texturePath=eveicon.inventory))
    if checker.OfferOpenDroneBay():
        entries += [[MenuLabel('UI/Commands/OpenDroneBay'), OpenDroneBay, [itemID]]]
    if checker.OfferOpenFighterBay():
        entries += [[MenuLabel('UI/Commands/OpenFighterBay'), OpenFighterBay, [itemID]]]
    if checker.OfferOpenFrigateEscapeBay():
        entries += [[MenuLabel('UI/Commands/OpenFrigateEscapeBay'), OpenFrigateEscapeBay, [itemID]]]
    if checker.OfferOpenShipMaintenanceBay():
        entries += [[MenuLabel('UI/Commands/OpenShipMaintenanceBay'), OpenShipMaintenanceBayShip, (itemID, GetByLabel('UI/Commands/OpenShipMaintenanceBayError'))]]
    if checker.OfferOpenFleetHangar():
        entries += [[MenuLabel('UI/Commands/OpenFleetHangar'), OpenFleetHangar, (itemID,)]]
    if checker.OfferOpenFuelBay():
        entries += [[MenuLabel('UI/Commands/OpenFuelBay'), OpenShipBay, [('ShipFuelBay', itemID)]]]
    if checker.OfferOpenGeneralMiningHold():
        entries += [[MenuLabel('UI/Commands/OpenGeneralMiningHold'), OpenShipBay, [('ShipGeneralMiningHold', itemID)]]]
    if checker.OfferOpenGasHold():
        entries += [[MenuLabel('UI/Commands/OpenGasHold'), OpenShipBay, [('ShipGasHold', itemID)]]]
    if checker.OfferOpenMineralHold():
        entries += [[MenuLabel('UI/Commands/OpenMineralHold'), OpenShipBay, [('ShipMineralHold', itemID)]]]
    if checker.OfferOpenSalvageHold():
        entries += [[MenuLabel('UI/Commands/OpenSalvageHold'), OpenShipBay, [('ShipSalvageHold', itemID)]]]
    if checker.OfferOpenShipHold():
        entries += [[MenuLabel('UI/Commands/OpenShipHold'), OpenShipBay, [('ShipShipHold', itemID)]]]
    if checker.OfferOpenSmallShipHold():
        entries += [[MenuLabel('UI/Commands/OpenSmallShipHold'), OpenShipBay, [('ShipSmallShipHold', itemID)]]]
    if checker.OfferOpenMediumShipHold():
        entries += [[MenuLabel('UI/Commands/OpenMediumShipHold'), OpenShipBay, [('ShipMediumShipHold', itemID)]]]
    if checker.OfferOpenLargeShipHold():
        entries += [[MenuLabel('UI/Commands/OpenLargeShipHold'), OpenShipBay, [('ShipLargeShipHold', itemID)]]]
    if checker.OfferOpenIndustrialShipHold():
        entries += [[MenuLabel('UI/Commands/OpenIndustrialShipHold'), OpenShipBay, [('ShipIndustrialShipHold', itemID)]]]
    if checker.OfferOpenAmmoHold():
        entries += [[MenuLabel('UI/Commands/OpenAmmoHold'), OpenShipBay, [('ShipAmmoHold', itemID)]]]
    if checker.OfferOpenCommandCenterHold():
        entries += [[MenuLabel('UI/Commands/OpenCommandCenterHold'), OpenShipBay, [('ShipCommandCenterHold', itemID)]]]
    if checker.OfferOpenPlanetaryCommoditiesHold():
        entries += [[MenuLabel('UI/PI/Common/OpenPlanetaryCommoditiesHold'), OpenShipBay, [('ShipPlanetaryCommoditiesHold', itemID)]]]
    if checker.OfferOpenQuafeBay():
        entries += [[MenuLabel('UI/Commands/OpenQuafeBay'), OpenShipBay, [('ShipQuafeHold', itemID)]]]
    if checker.OfferOpenCorpseBay():
        entries += [[MenuLabel('UI/Commands/OpenCorpseBay'), OpenShipBay, [('ShipCorpseHold', itemID)]]]
    if checker.OfferOpenBoosterBay():
        entries += [[MenuLabel('UI/Commands/OpenBoosterBay'), OpenShipBay, [('ShipBoosterHold', itemID)]]]
    if checker.OfferOpenSubsystemBay():
        entries += [[MenuLabel('UI/Commands/OpenSubsystemBay'), OpenShipBay, [('ShipSubsystemHold', itemID)]]]
    if checker.OfferOpenMobileDepotHold():
        entries += [[MenuLabel('UI/Commands/OpenMobileDepotHold'), OpenShipBay, [('ShipMobileDepotHold', itemID)]]]
    if checker.OfferOpenColonyResourcesHold():
        entries += [[MenuLabel('UI/Commands/OpenInfrastructureHold'), OpenShipBay, [('ShipColonyResourcesHold', itemID)]]]
    return entries


def OpenShipBay(invID):
    Inventory.OpenOrShow(invID=invID, openFromWnd=uicore.registry.GetActive())


def OpenShipHangarCargo(itemIDs):
    usePrimary = len(itemIDs) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for itemID in itemIDs:
        invID = (INVENTORY_ID_SHIP_CARGO, itemID)
        Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenDroneBay(itemIDs):
    usePrimary = len(itemIDs) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for itemID in itemIDs:
        invID = ('ShipDroneBay', itemID)
        invCtrl.ShipDroneBay(itemID).GetItems()
        Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenFighterBay(itemIDs):
    usePrimary = len(itemIDs) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for itemID in itemIDs:
        invID = ('ShipFighterBay', itemID)
        invCtrl.ShipFighterBay(itemID).GetItems()
        Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenFrigateEscapeBay(itemIDs):
    itemIDs = [itemIDs]
    usePrimary = len(itemIDs) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for itemID in itemIDs:
        invID = ('ShipFrigateEscapeBay', itemID)
        invCtrl.ShipFrigateEscapeBay(itemID).GetItems()
        Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenShipMaintenanceBayShip(itemID, name):
    invID = ('ShipMaintenanceBay', itemID)
    if itemID != eveCfg.GetActiveShip() and not session.stationid:
        invCtrl.ShipMaintenanceBay(itemID).GetItems()
        sm.GetService('inv').AddTemporaryInvLocation(invID)
    Inventory.OpenOrShow(invID=invID)


def OpenFleetHangar(itemID):
    invID = ('ShipFleetHangar', itemID)
    if itemID != eveCfg.GetActiveShip() and not session.stationid:
        invCtrl.ShipFleetHangar(itemID).GetItems()
        sm.GetService('inv').AddTemporaryInvLocation(invID)
    Inventory.OpenOrShow(invID=invID)


def OpenInfrastructureHubPanel(itemID):
    occupierID = sm.GetService('facwar').GetSystemOccupier(session.solarsystemid)
    if occupierID == session.warfactionid:
        bp = sm.GetService('michelle').GetBallpark()
        distance = bp.GetSurfaceDist(session.shipid, itemID)
        if distance < const.facwarIHubInteractDist:
            FWInfrastructureHub.Open(itemID=itemID)
        else:
            uicore.Message('InfrastructureHubCannotOpenDistance')
    else:
        uicore.Message('InfrastructureHubCannotOpenFaction', {'factionName': cfg.eveowners.Get(occupierID).name})


def OpenSovFuelDepositWindow(itemID, slimItem):
    ownerID = slimItem and slimItem.ownerID
    isOwner = ownerID == session.corpid
    isStationMgr = isOwner and bool(session.corprole & const.corpRoleStationManager)
    if not isStationMgr and not sm.GetService('sov').IsOnLocalSovHubFuelAccessGroup():
        raise UserError('NotOnLocalSovHubFuelAccessGroup')
    OpenReagnetBay(itemID, session.solarsystemid, isStationMgr)


def OpenSovHubWindow(itemID):
    from eve.client.script.ui.shared.sov.sovHub.sovHubWnd import OpenSovHubWnd
    OpenSovHubWnd(itemID, session.solarsystemid)


def OpenMercenaryDenWindow(itemID, typeID):
    from sovereignty.mercenaryden.client.ui.configuration_window import open_mercenary_den_window
    open_mercenary_den_window(itemID, typeID)


def OpenCargoContainer(invItems):
    usePrimary = len(invItems) == 1
    openFromWnd = uicore.registry.GetActive() if usePrimary else None
    for item in invItems:
        if item.ownerID not in (session.charid, session.corpid):
            eve.Message('CantDoThatWithSomeoneElsesStuff')
            return
        invID = ('StationContainer', item.itemID)
        Inventory.OpenOrShow(invID=invID, usePrimary=usePrimary, openFromWnd=openFromWnd)


def OpenBountyOffice(charID):
    if IsPlayerBountyHidden(sm.GetService('machoNet')):
        return
    wnd = BountyWindow.GetIfOpen()
    if not wnd:
        wnd = BountyWindow.Open()
    wnd.ownerID = charID
    wnd.ShowResult(charID)


def ViewAuditLogForALSC(itemID):
    AuditLogSecureContainerLogViewer.CloseIfOpen()
    AuditLogSecureContainerLogViewer.Open(itemID=itemID)


def RepairItems(items):
    if items is None or len(items) < 1:
        return
    wnd = RepairShopWindow.Open()
    if wnd and not wnd.destroyed:
        wnd.DisplayRepairQuote(items)


def OpenProfileSettingsForStructure(itemID):
    corpStructures = sm.GetService('structureDirectory').GetCorporationStructures()
    structureInfo = corpStructures.get(itemID, None)
    if not structureInfo:
        return
    profileID = structureInfo['profileID']
    browserController = sm.GetService('structureControllers').GetStructureBrowserController()
    from eve.client.script.ui.structure.structureBrowser.structureBrowserWnd import StructureBrowserWnd
    settingID = 'TabNavigationWindowHeader%s' % StructureBrowserWnd.default_windowID
    browserController.SetProfileSettingsSelected(settingID)
    browserController.SelectProfile(profileID)
    wnd = StructureBrowserWnd.GetIfOpen()
    if wnd:
        wnd.ForceProfileSettingsSelected()
    else:
        StructureBrowserWnd.Open()


def SimulateFitting(fitting, chargesToLoad = None):
    from eve.client.script.ui.shared.fittingScreen.fittingWnd import FittingWindow
    wnd = FittingWindow.GetIfOpen()
    if wnd:
        wnd.Maximize()
    else:
        uicore.cmd.GetCommandAndExecute('OpenFitting')
    sm.GetService('ghostFittingSvc').SimulateFitting(fitting, chargesToLoad=chargesToLoad)


def OpenDropbox(structureID, structureTypeID, items = None):
    wnd = DropboxWnd.GetIfOpen()
    if wnd and not wnd.destroyed:
        if wnd.dropBoxController.structureID == structureID and wnd.dropBoxController.forShipID == session.shipid:
            wnd.Maximize()
            if items:
                wnd.dropBoxController.AddManyItems(items)
            return
        wnd.Close()
    DropboxWnd.Open(structureID=structureID, structureTypeID=structureTypeID, itemsToTransfer=items)
