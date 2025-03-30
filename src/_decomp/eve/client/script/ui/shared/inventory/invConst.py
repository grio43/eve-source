#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\invConst.py
import eve.client.script.ui.shared.inventory.invContainers as invCont
import eve.client.script.environment.invControllers as invCtrl
from eve.client.script.ui.station.pvptrade.pvptradewnd import PlayerTrade
from eve.client.script.ui.shared.inventory.plexVault import PlexVault
from itertoolsext.Enum import Enum

@Enum

class ContainerType(object):
    ASSET_SAFETY_CONTAINER = 'AssetSafetyContainer'
    ASSET_SAFETY_CORP_CONTAINER = 'AssetSafetyCorpContainer'
    ASSET_SAFETY_DELIVERIES = 'AssetSafetyDeliveries'
    ITEM_FLOATING_CARGO = 'ItemFloatingCargo'
    ITEM_WRECK = 'ItemWreck'
    POS_CORP_HANGAR = 'POSCorpHangar'
    POS_FUEL_BAY = 'POSFuelBay'
    POS_MOBILE_REACTOR = 'POSMobileReactor'
    POS_PERSONAL_HANGAR = 'POSPersonalHangar'
    POS_REFINERY = 'POSRefinery'
    POS_COMPRESSION = 'POSCompression'
    POS_SHIP_MAINTENANCE_ARRAY = 'POSShipMaintenanceArray'
    POS_SILO = 'POSSilo'
    POS_STRONTIUM_BAY = 'POSStrontiumBay'
    POS_STRUCTURE_CHARGE_CRYSTAL = 'POSStructureChargeCrystal'
    POS_STRUCTURE_CHARGES = 'POSStructureCharges'
    POS_STRUCTURE_CHARGES_STORAGE = 'POSStructureChargesStorage'
    REDEEM_ITEMS = 'RedeemItems'
    SHIP_AMMO_HOLD = 'ShipAmmoHold'
    SHIP_BOOSTER_HOLD = 'ShipBoosterHold'
    SHIP_CARGO = 'ShipCargo'
    SHIP_COMMAND_CENTER_HOLD = 'ShipCommandCenterHold'
    SHIP_CORPSE_HOLD = 'ShipCorpseHold'
    SHIP_DRONE_BAY = 'ShipDroneBay'
    SHIP_FIGHTER_BAY = 'ShipFighterBay'
    SHIP_FRIGATE_ESCAPE_BAY = 'ShipFrigateEscapeBay'
    SHIP_FLEET_HANGAR = 'ShipFleetHangar'
    SHIP_FUEL_BAY = 'ShipFuelBay'
    SHIP_GAS_HOLD = 'ShipGasHold'
    SHIP_INDUSTRIAL_SHIP_HOLD = 'ShipIndustrialShipHold'
    SHIP_MAINTENANCE_BAY = 'ShipMaintenanceBay'
    SHIP_LARGE_SHIP_HOLD = 'ShipLargeShipHold'
    SHIP_MEDIUM_SHIP_HOLD = 'ShipMediumShipHold'
    SHIP_MINERAL_HOLD = 'ShipMineralHold'
    SHIP_GENERAL_MINING_HOLD = 'ShipGeneralMiningHold'
    SHIP_ASTEROID_HOLD = 'ShipAsteroidHold'
    SHIP_ICE_HOLD = 'ShipIceHold'
    SHIP_PLANETARY_COMMODITIES_HOLD = 'ShipPlanetaryCommoditiesHold'
    SHIP_QUAFE_HOLD = 'ShipQuafeHold'
    SHIP_SALVAGE_HOLD = 'ShipSalvageHold'
    SHIP_SHIP_HOLD = 'ShipShipHold'
    SHIP_SMALL_SHIP_HOLD = 'ShipSmallShipHold'
    SHIP_SUBSYSTEM_HOLD = 'ShipSubsystemHold'
    STATION_CONTAINER = 'StationContainer'
    STATION_CORP_DELIVERIES = 'StationCorpDeliveries'
    STATION_CORP_HANGAR = 'StationCorpHangar'
    STATION_CORP_MEMBER = 'StationCorpMember'
    STATION_ITEMS = 'StationItems'
    STATION_SHIPS = 'StationShips'
    PLAYER_TRADE = 'PlayerTrade'
    SPACE_COMPONENT_INVENTORY = 'SpaceComponentInventory'
    STRUCTURE = 'Structure'
    STRUCTURE_AMMO_BAY = 'StructureAmmoBay'
    STRUCTURE_FUEL_BAY = 'StructureFuelBay'
    STRUCTURE_FIGHTER_BAY = 'StructureFighterBay'
    STRUCTURE_ITEM_HANGAR = 'StructureItemHangar'
    STRUCTURE_SHIP_HANGAR = 'StructureShipHangar'
    STRUCTURE_CORP_HANGAR = 'StructureCorpHangar'
    STRUCTURE_DELIVERIES_HANGAR = 'StructureDeliveriesHangar'
    STRUCTURE_DEED_BAY = 'StructureDeedBay'
    STRUCTURE_MOON_MATERIAL_BAY = 'StructureMoonMaterialBay'
    ITEM_SIPHON_PSEUDO_SILO = 'ItemSiphonPseudoSilo'
    PLEX_VAULT = 'PlexVault'
    SHIP_MOBILE_DEPOT_HOLD = 'ShipMobileDepotHold'
    SHIP_COLONY_RESOURCES_HOLD = 'ShipColonyResourcesHold'
    BASE_CELESTIAL_CONTAINER = 'BaseCelestialContainer'


_CONTAINERS_CLASS_BY_TYPE = {ContainerType.ASSET_SAFETY_CONTAINER: invCont.AssetSafetyContainer,
 ContainerType.ASSET_SAFETY_CORP_CONTAINER: invCont.AssetSafetyCorpContainer,
 ContainerType.ASSET_SAFETY_DELIVERIES: invCont.AssetSafetyDeliveries,
 ContainerType.ITEM_FLOATING_CARGO: invCont.ItemFloatingCargo,
 ContainerType.ITEM_WRECK: invCont.ItemWreck,
 ContainerType.POS_CORP_HANGAR: invCont.POSCorpHangar,
 ContainerType.POS_FUEL_BAY: invCont.POSFuelBay,
 ContainerType.POS_MOBILE_REACTOR: invCont.POSMobileReactor,
 ContainerType.POS_PERSONAL_HANGAR: invCont.POSPersonalHangar,
 ContainerType.POS_REFINERY: invCont.POSRefinery,
 ContainerType.POS_COMPRESSION: invCont.POSCompression,
 ContainerType.POS_SHIP_MAINTENANCE_ARRAY: invCont.POSShipMaintenanceArray,
 ContainerType.POS_SILO: invCont.POSSilo,
 ContainerType.POS_STRONTIUM_BAY: invCont.POSStrontiumBay,
 ContainerType.POS_STRUCTURE_CHARGE_CRYSTAL: invCont.POSStructureChargeCrystal,
 ContainerType.POS_STRUCTURE_CHARGES: invCont.POSStructureCharges,
 ContainerType.POS_STRUCTURE_CHARGES_STORAGE: invCont.POSStructureChargesStorage,
 ContainerType.REDEEM_ITEMS: invCont.RedeemItems,
 ContainerType.SHIP_AMMO_HOLD: invCont.ShipAmmoHold,
 ContainerType.SHIP_BOOSTER_HOLD: invCont.ShipBoosterHold,
 ContainerType.SHIP_CARGO: invCont.ShipCargo,
 ContainerType.SHIP_COMMAND_CENTER_HOLD: invCont.ShipCommandCenterHold,
 ContainerType.SHIP_CORPSE_HOLD: invCont.ShipCorpseHold,
 ContainerType.SHIP_DRONE_BAY: invCont.ShipDroneBay,
 ContainerType.SHIP_FIGHTER_BAY: invCont.ShipFighterBay,
 ContainerType.SHIP_FRIGATE_ESCAPE_BAY: invCont.ShipFrigateEscapeBay,
 ContainerType.SHIP_FLEET_HANGAR: invCont.ShipFleetHangar,
 ContainerType.SHIP_FUEL_BAY: invCont.ShipFuelBay,
 ContainerType.SHIP_GAS_HOLD: invCont.ShipGasHold,
 ContainerType.SHIP_INDUSTRIAL_SHIP_HOLD: invCont.ShipIndustrialShipHold,
 ContainerType.SHIP_MAINTENANCE_BAY: invCont.ShipMaintenanceBay,
 ContainerType.SHIP_LARGE_SHIP_HOLD: invCont.ShipLargeShipHold,
 ContainerType.SHIP_MEDIUM_SHIP_HOLD: invCont.ShipMediumShipHold,
 ContainerType.SHIP_MINERAL_HOLD: invCont.ShipMineralHold,
 ContainerType.SHIP_GENERAL_MINING_HOLD: invCont.ShipGeneralMiningHold,
 ContainerType.SHIP_ASTEROID_HOLD: invCont.ShipAsteroidHold,
 ContainerType.SHIP_ICE_HOLD: invCont.ShipIceHold,
 ContainerType.SHIP_PLANETARY_COMMODITIES_HOLD: invCont.ShipPlanetaryCommoditiesHold,
 ContainerType.SHIP_QUAFE_HOLD: invCont.ShipQuafeHold,
 ContainerType.SHIP_SALVAGE_HOLD: invCont.ShipSalvageHold,
 ContainerType.SHIP_SHIP_HOLD: invCont.ShipShipHold,
 ContainerType.SHIP_SMALL_SHIP_HOLD: invCont.ShipSmallShipHold,
 ContainerType.SHIP_SUBSYSTEM_HOLD: invCont.ShipSubsystemHold,
 ContainerType.STATION_CONTAINER: invCont.StationContainer,
 ContainerType.STATION_CORP_DELIVERIES: invCont.StationCorpDeliveries,
 ContainerType.STATION_CORP_HANGAR: invCont.StationCorpHangar,
 ContainerType.STATION_CORP_MEMBER: invCont.StationCorpMember,
 ContainerType.STATION_ITEMS: invCont.StationItems,
 ContainerType.STATION_SHIPS: invCont.StationShips,
 ContainerType.PLAYER_TRADE: PlayerTrade,
 ContainerType.SPACE_COMPONENT_INVENTORY: invCont.SpaceComponentInventory,
 ContainerType.STRUCTURE: invCont.Structure,
 ContainerType.STRUCTURE_AMMO_BAY: invCont.StructureAmmoBay,
 ContainerType.STRUCTURE_FUEL_BAY: invCont.StructureFuelBay,
 ContainerType.STRUCTURE_FIGHTER_BAY: invCont.StructureFighterBay,
 ContainerType.STRUCTURE_ITEM_HANGAR: invCont.StructureItemHangar,
 ContainerType.STRUCTURE_SHIP_HANGAR: invCont.StructureShipHangar,
 ContainerType.STRUCTURE_CORP_HANGAR: invCont.StructureCorpHangar,
 ContainerType.STRUCTURE_DELIVERIES_HANGAR: invCont.StructureDeliveriesHangar,
 ContainerType.STRUCTURE_DEED_BAY: invCont.StructureDeedBay,
 ContainerType.STRUCTURE_MOON_MATERIAL_BAY: invCont.StructureMoonMaterialBay,
 ContainerType.ITEM_SIPHON_PSEUDO_SILO: invCont.ItemSiphonPseudoSilo,
 ContainerType.PLEX_VAULT: PlexVault,
 ContainerType.SHIP_MOBILE_DEPOT_HOLD: invCont.ShipMobileDepotHold,
 ContainerType.SHIP_COLONY_RESOURCES_HOLD: invCont.ShipColonyResourcesHold,
 ContainerType.BASE_CELESTIAL_CONTAINER: None}
_CONTROLLER_CLASS_BY_TYPE = {ContainerType.ASSET_SAFETY_CONTAINER: invCtrl.AssetSafetyContainer,
 ContainerType.ASSET_SAFETY_CORP_CONTAINER: invCtrl.AssetSafetyCorpContainer,
 ContainerType.ASSET_SAFETY_DELIVERIES: invCtrl.AssetSafetyDeliveries,
 ContainerType.ITEM_FLOATING_CARGO: invCtrl.ItemFloatingCargo,
 ContainerType.ITEM_WRECK: invCtrl.ItemWreck,
 ContainerType.POS_CORP_HANGAR: invCtrl.POSCorpHangar,
 ContainerType.POS_FUEL_BAY: invCtrl.POSFuelBay,
 ContainerType.POS_MOBILE_REACTOR: invCtrl.POSMobileReactor,
 ContainerType.POS_PERSONAL_HANGAR: invCtrl.POSPersonalHangar,
 ContainerType.POS_REFINERY: invCtrl.POSRefinery,
 ContainerType.POS_COMPRESSION: invCtrl.POSCompression,
 ContainerType.POS_SHIP_MAINTENANCE_ARRAY: invCtrl.POSShipMaintenanceArray,
 ContainerType.POS_SILO: invCtrl.POSSilo,
 ContainerType.POS_STRONTIUM_BAY: invCtrl.POSStrontiumBay,
 ContainerType.POS_STRUCTURE_CHARGE_CRYSTAL: invCtrl.POSStructureChargeCrystal,
 ContainerType.POS_STRUCTURE_CHARGES: invCtrl.POSStructureCharges,
 ContainerType.POS_STRUCTURE_CHARGES_STORAGE: invCtrl.POSStructureChargesStorage,
 ContainerType.REDEEM_ITEMS: invCtrl.RedeemItems,
 ContainerType.SHIP_AMMO_HOLD: invCtrl.ShipAmmoHold,
 ContainerType.SHIP_BOOSTER_HOLD: invCtrl.ShipBoosterHold,
 ContainerType.SHIP_CARGO: invCtrl.ShipCargo,
 ContainerType.SHIP_COMMAND_CENTER_HOLD: invCtrl.ShipCommandCenterHold,
 ContainerType.SHIP_CORPSE_HOLD: invCtrl.ShipCorpseHold,
 ContainerType.SHIP_DRONE_BAY: invCtrl.ShipDroneBay,
 ContainerType.SHIP_FIGHTER_BAY: invCtrl.ShipFighterBay,
 ContainerType.SHIP_FRIGATE_ESCAPE_BAY: invCtrl.ShipFrigateEscapeBay,
 ContainerType.SHIP_FLEET_HANGAR: invCtrl.ShipFleetHangar,
 ContainerType.SHIP_FUEL_BAY: invCtrl.ShipFuelBay,
 ContainerType.SHIP_GAS_HOLD: invCtrl.ShipGasHold,
 ContainerType.SHIP_INDUSTRIAL_SHIP_HOLD: invCtrl.ShipIndustrialShipHold,
 ContainerType.SHIP_MAINTENANCE_BAY: invCtrl.ShipMaintenanceBay,
 ContainerType.SHIP_LARGE_SHIP_HOLD: invCtrl.ShipLargeShipHold,
 ContainerType.SHIP_MEDIUM_SHIP_HOLD: invCtrl.ShipMediumShipHold,
 ContainerType.SHIP_MINERAL_HOLD: invCtrl.ShipMineralHold,
 ContainerType.SHIP_GENERAL_MINING_HOLD: invCtrl.ShipGeneralMiningHold,
 ContainerType.SHIP_ASTEROID_HOLD: invCtrl.ShipAsteroidHold,
 ContainerType.SHIP_ICE_HOLD: invCtrl.ShipIceHold,
 ContainerType.SHIP_PLANETARY_COMMODITIES_HOLD: invCtrl.ShipPlanetaryCommoditiesHold,
 ContainerType.SHIP_QUAFE_HOLD: invCtrl.ShipQuafeHold,
 ContainerType.SHIP_SALVAGE_HOLD: invCtrl.ShipSalvageHold,
 ContainerType.SHIP_SHIP_HOLD: invCtrl.ShipShipHold,
 ContainerType.SHIP_SMALL_SHIP_HOLD: invCtrl.ShipSmallShipHold,
 ContainerType.SHIP_SUBSYSTEM_HOLD: invCtrl.ShipSubsystemHold,
 ContainerType.STATION_CONTAINER: invCtrl.StationContainer,
 ContainerType.STATION_CORP_DELIVERIES: invCtrl.StationCorpDeliveries,
 ContainerType.STATION_CORP_HANGAR: invCtrl.StationCorpHangar,
 ContainerType.STATION_CORP_MEMBER: invCtrl.StationCorpMember,
 ContainerType.STATION_ITEMS: invCtrl.StationItems,
 ContainerType.STATION_SHIPS: invCtrl.StationShips,
 ContainerType.PLAYER_TRADE: invCtrl.PlayerTrade,
 ContainerType.SPACE_COMPONENT_INVENTORY: invCtrl.SpaceComponentInventory,
 ContainerType.STRUCTURE: invCtrl.Structure,
 ContainerType.STRUCTURE_AMMO_BAY: invCtrl.StructureAmmoBay,
 ContainerType.STRUCTURE_FUEL_BAY: invCtrl.StructureFuelBay,
 ContainerType.STRUCTURE_FIGHTER_BAY: invCtrl.StructureFighterBay,
 ContainerType.STRUCTURE_ITEM_HANGAR: invCtrl.StructureItemHangar,
 ContainerType.STRUCTURE_SHIP_HANGAR: invCtrl.StructureShipHangar,
 ContainerType.STRUCTURE_CORP_HANGAR: invCtrl.StructureCorpHangar,
 ContainerType.STRUCTURE_DELIVERIES_HANGAR: invCtrl.StructureDeliveriesHangar,
 ContainerType.STRUCTURE_DEED_BAY: invCtrl.StructureDeedBay,
 ContainerType.STRUCTURE_MOON_MATERIAL_BAY: invCtrl.StructureMoonMaterialBay,
 ContainerType.ITEM_SIPHON_PSEUDO_SILO: invCtrl.ItemSiphonPseudoSilo,
 ContainerType.PLEX_VAULT: invCtrl.PlexVault,
 ContainerType.SHIP_MOBILE_DEPOT_HOLD: invCtrl.ShipMobileDepotHold,
 ContainerType.SHIP_COLONY_RESOURCES_HOLD: invCtrl.ShipColonyResourcesHold,
 ContainerType.BASE_CELESTIAL_CONTAINER: invCtrl.BaseCelestialContainer}

def GetInventoryControllerClass(invType):
    return _CONTROLLER_CLASS_BY_TYPE.get(invType, None)


def GetInventoryContainerClass(invType):
    return _CONTAINERS_CLASS_BY_TYPE.get(invType, None)
