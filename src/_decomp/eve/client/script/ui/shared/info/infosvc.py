#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\infosvc.py
import copy
import sys
import evelink.client
from eve.client.script.ui.shared.skins.uiutil import OPEN_SKINR_BUTTON_INFO_WINDOW_ANALYTIC_ID
from collections import defaultdict, OrderedDict
from eve.client.script.ui.inflight.itemTrader.itemTraderController import Recipe
from eve.client.script.ui.inflight.itemTrader.offerBrowser import RecipeEntry
from eve.client.script.ui.inflight.itemTrader.recipeUtil import GetSortedRecipeGroupsAndData
from evePathfinder.core import IsUnreachableJumpCount
import blue
import eveformat.client
import telemetry
import utillib
import carbonui.const as uiconst
import dogma.attributes.format as attributeFormat
import evetypes
import inventorycommon.typeHelpers
import itertoolsext
import localization
import log
import uthread
import dynamicitemattributes
import dogma.const
import dogma.data as dogma_data
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_CONTENT, ROLE_GML, ROLE_WORLDMOD
from carbon.common.script.util import timerstuff
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate, FmtDist
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.uicore import uicore
from carbonui.control.button import Button
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from characterdata.factions import get_faction_name, get_faction_races, get_station_count, get_station_system_count
from characterdata.races import get_race_name
from contrabandtypes.data import get_contraband_types_in_faction
from corruptionsuppression.client.systemEffectsClient import CorruptionWarpSpeedIncreaserCheckerClient
from corruptionsuppression.systemEffects import WARP_SPEED_INCREASE_STAGE_THRESHOLD
from dbuff.client.uiFormatters import GetDbuffInfoEntriesForItem
from dogma.attributes.format import FormatValue, FormatUnit
from dogma.attributes.format import GetFormatAndValue, GetFormattedAttributeAndValue, GetAttribute
from dogma.const import attributeDataTypeTypeHex
from eve.client.script.ui.control.damageGaugeContainers import DamageEntry
from eve.client.script.ui.control.entries.button import ButtonEntry
from eve.client.script.ui.control.entries.certificate import CertEntry
from eve.client.script.ui.control.entries.divider import DividerEntry
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.header import Header, Subheader
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.label_text import LabelMultilineTextTop, LabelTextSides, LabelTextSidesAttributes, LabelTextSidesMoreInfo, LabelTextTop
from eve.client.script.ui.control.entries.space import Space
from eve.client.script.ui.control.entries.status_bar import StatusBar
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.entries.universe import LabelLocationTextTop, SystemNameHeader, LocationGroup, LocationTextEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.skillTreeEntry import SkillTreeEntry
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SHOWINFO
from eve.client.script.ui.shared.dynamicItem.info import FormatAttributeBonusRange
from eve.client.script.ui.shared.info.infoUtil import GetAttributeTooltipTitleAndDescription, GetFittingAttributeIDs
from eve.client.script.ui.shared.info.attribute import Attribute, CreateAttribute, MutatedAttribute, FloatCloseEnough
from eve.client.script.ui.shared.info.shipInfoWindow import ShipInfoWindow
from eve.client.script.ui.shared.mapView.mapViewUtil import OpenMap
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SERVICE_SecurityOffice, STARMODE_SETTLED_SYSTEMS_BY_CORP
from eve.client.script.ui.shared.medalribbonranks import MedalRibbonEntry, RankEntry
from eve.client.script.ui.shared.neocom.Alliances.all_ui_home import PrimeTimeHourEntryHorizontal
from eve.client.script.ui.shared.neocom.charsheet.charSheetUtil import GetMedalScrollEntries
from eve.client.script.ui.shared.neocom.corporation.war.warEntry import WarEntry
from eve.client.script.ui.shared.neocom.wallet.walletUtil import FmtWalletCurrency
from eve.client.script.ui.shared.userentry import AgentEntry, User
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.station.stationServiceEntry import StationServiceEntry
from eve.client.script.ui.structure.structureSettings.groupEntryCont import VALUE_TYPES
from eve.client.script.ui.structure.structureSettings.uiSettingUtil import GetUnit
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipHeaderDescriptionWrapper
from eve.client.script.ui.util import uix
from eve.common.script.net import eveMoniker
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.util import industryCommon
from eve.common.script.util.structuresCommon import IsStationServiceAvailable
from eveexceptions import ExceptionEater, UserError
from eveprefs import prefs
from eveservices.menu import StartMenuService
from eveservices.xmppchat import GetChatService
from evestations.data import service_in_station_operation
from evestations.standingsrestriction import get_station_standings_restriction_info_many
from evetypes.skills import get_types_with_skill_type
from eveuniverse.solar_systems import is_directional_scanner_suppressed
from evewar.warPermitUtil import GetLabelPathForAllowWar
from inventoryrestrictions import is_contractable, can_view_market_details
from itemcompression.data import is_compressible_type, is_compressed_type
from npcs.npccorporations import get_corporation_faction_id
from npcs.npccorporations import get_corporation_ids_by_faction_id
from npcs.npccorporations import get_npc_corporation
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError
from sovereignty.upgrades.client.data_types import UpgradeStaticData
from sovereignty.upgrades.client.errors import SovUpgradeDataUnavailableError
from spacecomponents.common.data import get_space_component_for_type, get_space_component_names_for_type
from spacecomponents.common.helper import GetItemTraderComponent
from stackless_response_router.exceptions import TimeoutException
from typematerials.data import is_reprocessable_type
from inventorycommon.util import GetTypeVolume, GetVolumeForPlasticItem
from localization import GetByLabel
from npcs.client.components.entity_bounty import get_entity_bounty
from npcs.divisions import get_division_name
from spacecomponents.client import factory
from spacecomponents.client.display import IterAttributeCollectionInInfoOrder
from structures.services import GetServiceLabel, GetServiceIcon, META_SERVICES, STRUCTURES_WITHOUT_ONLINE_SERVICES, ONLINE_SERVICES
from utillib import KeyVal
from eve.common.script.util.eveFormat import FmtISK, FmtPlanetAttributeKeyVal
import structures
from eve.client.script.ui.shared.info.infoConst import *
from eve.client.script.ui.shared.info.infoWindow import InfoWindow, AttributeRowEntry
import expertSystems.client
from eve.common.lib import appConst as const
GENERIC_ATTRIBUTES_TO_AVOID = (const.attributeMass,)
SUN_STATISTICS_ATTRIBUTES = ['spectralClass',
 'luminosity',
 'age',
 'radius',
 'temperature',
 'power']
ASTEROID_BELT_STATISTICS_ATTRIBUTES = ['density',
 'massDust',
 'orbitPeriod',
 'orbitRadius',
 'eccentricity']
FINISHED_WARS_FOLDER_THRESHOLD = 100
MIN_IN_MS = 60000
MOON_STATISTICS_ATTRIBUTES = ['density',
 'escapeVelocity',
 'massDust',
 'orbitPeriod',
 'orbitRadius',
 'pressure',
 'radius',
 'surfaceGravity',
 'temperature']
PLANET_STATISTICS_ATTRIBUTES = ['density',
 'eccentricity',
 'escapeVelocity',
 'massDust',
 'orbitPeriod',
 'orbitRadius',
 'pressure',
 'radius',
 'surfaceGravity',
 'temperature']
CELESTIAL_STATISTICS_ATTRIBUTES_BY_GROUPID = {const.groupPlanet: PLANET_STATISTICS_ATTRIBUTES,
 const.groupMoon: MOON_STATISTICS_ATTRIBUTES,
 const.groupAsteroidBelt: ASTEROID_BELT_STATISTICS_ATTRIBUTES}
DAMAGE_ATTRIBUTES = [const.attributeEmDamage,
 const.attributeThermalDamage,
 const.attributeKineticDamage,
 const.attributeExplosiveDamage]

class Info(Service):
    __exportedcalls__ = {'ShowInfo': [],
     'GetAttributeScrollListForType': [],
     'GetAttributeScrollListForItem': [],
     'GetSolarSystemReport': [],
     'GetKillsRecentKills': [],
     'GetKillsRecentLosses': [],
     'GetEmploymentHistorySubContent': [],
     'GetAllianceMembersSubContent': []}
    __guid__ = 'svc.info'
    __notifyevents__ = ('DoSessionChanging',
     'OnItemChange',
     'OnAllianceRelationshipChanged',
     'OnContactChange',
     'OnShowOwnerDetailsWindow')
    __servicename__ = 'info'
    __displayname__ = 'Information Service'
    __dependencies__ = ['dataconfig', 'map']
    __startupdependencies__ = ['settings', 'sovHubSvc']

    def Run(self, memStream = None):
        self.LogInfo('Starting InfoSvc')
        self.wnds = {}
        self.rwWindows = []
        self.lastActive = {}
        self._usedWithTypeIDs = None
        self._usedWithInitializing = False
        self.TryInitializeUsedWith()
        self.ClearWnds()

    def OnItemChange(self, item, change, location):
        if item.categoryID != const.categoryCharge and (item.locationID == eve.session.shipid or const.ixLocationID in change and change[const.ixLocationID] == eve.session.shipid):
            self.itemchangeTimer = timerstuff.AutoTimer(1000, self.DelayOnItemChange, item, change)
        itemGone = False
        if const.ixLocationID in change and idCheckers.IsJunkLocation(item.locationID):
            itemGone = True
        if const.ixQuantity in change and item.stacksize == 0:
            log.LogTraceback('infoSvc processing ixQuantity change')
            itemGone = True
        if const.ixStackSize in change and item.stacksize == 0:
            itemGone = True
        if itemGone:
            for each in self._GetOpenWindowsForType(item.typeID):
                if each is None or each.destroyed:
                    self._UnregisterWindow(each)
                    continue
                if each.itemID == item.itemID:
                    if isinstance(each, self._GetInfoWindowClass(item.typeID)):
                        each.ReconstructInfoWindow(each.typeID)

    def _GetInfoWindowClass(self, typeID):
        if evetypes.GetCategoryID(typeID) == const.categoryShip:
            return ShipInfoWindow
        return InfoWindow

    def _GetOpenWindows(self, wndType):
        if wndType in self.wnds:
            return self.wnds[wndType]
        return []

    def _GetOpenWindowsForType(self, typeID):
        wndClass = self._GetInfoWindowClass(typeID)
        return self._GetOpenWindows(wndClass)

    def _RegisterWindow(self, wnd):
        wndType = wnd.__class__
        if wndType not in self.wnds:
            self.wnds[wndType] = []
        self.wnds[wndType].append(wnd)

    def _UnregisterWindow(self, wnd):
        wndType = type(wnd)
        if wndType in self.wnds:
            self.wnds[wndType].remove(wnd)

    def _GetLastActive(self, wndType):
        if wndType in self.lastActive:
            return self.lastActive[wndType]

    def _GetLastActiveForType(self, typeID):
        wndClass = self._GetInfoWindowClass(typeID)
        return self._GetLastActive(wndClass)

    def _SetLastActive(self, wnd):
        wndType = wnd.__class__
        self.lastActive[wndType] = wnd

    def _ClearLastActive(self, wndType):
        if wndType in self.lastActive:
            self.lastActive.pop(wndType)

    def DelayOnItemChange(self, item, change):
        self.itemchangeTimer = None
        for each in self._GetOpenWindowsForType(item.typeID):
            if each is None or each.destroyed:
                self._UnregisterWindow(each)
                continue
            if each.itemID == eve.session.shipid and not each.IsMinimized() and isinstance(each, self._GetInfoWindowClass(item.typeID)):
                each.ReconstructInfoWindow(each.typeID, each.itemID, each.rec)

    def OnContactChange(self, contactIDs, contactType = None):
        for contactID in contactIDs:
            self.UpdateWnd(contactID)

    def OnAllianceRelationshipChanged(self, *args):
        for allianceid in (args[0], args[1]):
            self.UpdateWnd(allianceid)

    def GetFighterAttributes(self):
        if not hasattr(self, 'fighterAttributes'):
            fighterAttributes = OrderedDict()
            fighterAttributes[GetByLabel('UI/Common/FighterBase')] = {'normalAttributes': [const.attributeVolume,
                                  const.attributeMass,
                                  const.attributeAgility,
                                  const.attributeMaxVelocity,
                                  const.attributeSignatureRadius,
                                  const.attributeFighterSquadronMaxSize,
                                  const.attributeFighterRefuelingTime,
                                  const.attributeFighterSquadronOrbitRange]}
            fighterAttributes[GetByLabel('UI/Common/Shield')] = {'normalAttributes': [const.attributeShieldCapacity, const.attributeShieldRechargeRate],
             'groupedAttributes': [('em', const.attributeShieldEmDamageResonance),
                                   ('thermal', const.attributeShieldThermalDamageResonance),
                                   ('kinetic', const.attributeShieldKineticDamageResonance),
                                   ('explosive', const.attributeShieldExplosiveDamageResonance)]}
            fighterAttributes[GetByLabel('UI/Fitting/FittingWindow/Targeting')] = {'normalAttributes': [const.attributeScanResolution,
                                  const.attributeMaxTargetRange,
                                  const.attributeMaxLockedTargets,
                                  const.attributeScanLadarStrength,
                                  const.attributeScanMagnetometricStrength,
                                  const.attributeScanRadarStrength,
                                  const.attributeScanGravimetricStrength]}
            self.fighterAttributes = fighterAttributes
        return self.fighterAttributes

    def GetEntityAttributes(self):
        if not hasattr(self, 'entityAttributes'):
            entityAttributes = OrderedDict()
            entityAttributes[GetByLabel('UI/Fitting/Structure')] = {'normalAttributes': [],
             'groupedAttributes': [('em', const.attributeEmDamageResonance),
                                   ('thermal', const.attributeThermalDamageResonance),
                                   ('kinetic', const.attributeKineticDamageResonance),
                                   ('explosive', const.attributeExplosiveDamageResonance)]}
            entityAttributes[GetByLabel('UI/Common/Armor')] = {'normalAttributes': [],
             'groupedAttributes': [('em', const.attributeArmorEmDamageResonance),
                                   ('thermal', const.attributeArmorThermalDamageResonance),
                                   ('kinetic', const.attributeArmorKineticDamageResonance),
                                   ('explosive', const.attributeArmorExplosiveDamageResonance)]}
            entityAttributes[GetByLabel('UI/Common/Shield')] = {'normalAttributes': [],
             'groupedAttributes': [('em', const.attributeShieldEmDamageResonance),
                                   ('thermal', const.attributeShieldThermalDamageResonance),
                                   ('kinetic', const.attributeShieldKineticDamageResonance),
                                   ('explosive', const.attributeShieldExplosiveDamageResonance)]}
            self.entityAttributes = entityAttributes
        return self.entityAttributes

    def GetShipAndDroneAttributes(self):
        if not hasattr(self, 'shipAttributes'):
            shipAttributes = OrderedDict()
            shipAttributes[GetByLabel('UI/Fitting/Structure')] = {'normalAttributes': [const.attributeHp,
                                  const.attributeCapacity,
                                  const.attributeStructureDamageLimit,
                                  const.attributeDroneCapacity,
                                  const.attributeFrigateEscapeBayCapacity,
                                  const.attributeDroneBandwidth,
                                  const.attributeMass,
                                  const.attributeVolume,
                                  const.attributeAgility,
                                  const.attributeSpecialAmmoHoldCapacity,
                                  const.attributeSpecialGasHoldCapacity,
                                  const.attributeSpecialIceHoldCapacity,
                                  const.attributeSpecialIndustrialShipHoldCapacity,
                                  const.attributeSpecialLargeShipHoldCapacity,
                                  const.attributeSpecialMediumShipHoldCapacity,
                                  const.attributeSpecialMineralHoldCapacity,
                                  const.attributeGeneralMiningHoldCapacity,
                                  const.attributeSpecialAsteroidHoldCapacity,
                                  const.attributeSpecialSalvageHoldCapacity,
                                  const.attributeSpecialShipHoldCapacity,
                                  const.attributeSpecialSmallShipHoldCapacity,
                                  const.attributeSpecialCommandCenterHoldCapacity,
                                  const.attributeSpecialPlanetaryCommoditiesHoldCapacity,
                                  const.attributeSpecialSubsystemHoldCapacity,
                                  const.attributeSpecialCorpseHoldCapacity,
                                  const.attributeSpecialBoosterHoldCapacity,
                                  const.attributeSpecialMobileDepotHoldCapacity,
                                  const.attributeSpecialColonyResourcesHoldCapacity],
             'groupedAttributes': [('em', const.attributeEmDamageResonance),
                                   ('thermal', const.attributeThermalDamageResonance),
                                   ('kinetic', const.attributeKineticDamageResonance),
                                   ('explosive', const.attributeExplosiveDamageResonance)]}
            shipAttributes[GetByLabel('UI/Common/Armor')] = {'normalAttributes': [const.attributeArmorHP, const.attributeArmorDamageLimit],
             'groupedAttributes': [('em', const.attributeArmorEmDamageResonance),
                                   ('thermal', const.attributeArmorThermalDamageResonance),
                                   ('kinetic', const.attributeArmorKineticDamageResonance),
                                   ('explosive', const.attributeArmorExplosiveDamageResonance)]}
            shipAttributes[GetByLabel('UI/Common/Shield')] = {'normalAttributes': [const.attributeShieldCapacity, const.attributeShieldRechargeRate, const.attributeShieldDamageLimit],
             'groupedAttributes': [('em', const.attributeShieldEmDamageResonance),
                                   ('thermal', const.attributeShieldThermalDamageResonance),
                                   ('kinetic', const.attributeShieldKineticDamageResonance),
                                   ('explosive', const.attributeShieldExplosiveDamageResonance)]}
            shipAttributes[GetByLabel('UI/Common/EWarResistances')] = {'normalAttributes': [const.attributeECMResistance,
                                  const.attributeRemoteAssistanceImpedance,
                                  const.attributeRemoteRepairImpedance,
                                  const.attributeEnergyWarfareResistance,
                                  const.attributeSensorDampenerResistance,
                                  const.attributeStasisWebifierResistance,
                                  const.attributeTargetPainterResistance,
                                  const.attributeWeaponDisruptionResistance]}
            shipAttributes[GetByLabel('UI/Fitting/FittingWindow/Capacitor')] = {'normalAttributes': [const.attributeCapacitorCapacity, const.attributeRechargeRate]}
            shipAttributes[GetByLabel('UI/Fitting/FittingWindow/Targeting')] = {'normalAttributes': [const.attributeMaxTargetRange,
                                  const.attributeMaxRange,
                                  const.attributeMaxLockedTargets,
                                  const.attributeSignatureRadius,
                                  const.attributeSignatureResolution,
                                  const.attributeScanResolution,
                                  const.attributeScanLadarStrength,
                                  const.attributeScanMagnetometricStrength,
                                  const.attributeScanRadarStrength,
                                  const.attributeScanGravimetricStrength,
                                  const.attributeProximityRange,
                                  const.attributeFalloff,
                                  const.attributeTrackingSpeed]}
            shipAttributes[GetByLabel('UI/InfoWindow/SharedFacilities')] = {'normalAttributes': [const.attributeFleetHangarCapacity,
                                  const.attributeShipMaintenanceBayCapacity,
                                  const.attributeMaxJumpClones,
                                  const.attributeReclonerFuelType]}
            shipAttributes[GetByLabel('UI/InfoWindow/FighterFacilities')] = {'normalAttributes': [const.attributeFighterCapacity,
                                  const.attributeFighterTubes,
                                  const.attributeFighterLightSlots,
                                  const.attributeFighterSupportSlots,
                                  const.attributeFighterHeavySlots,
                                  const.attributeFighterStandupLightSlots,
                                  const.attributeFighterStandupSupportSlots,
                                  const.attributeFighterStandupHeavySlots]}
            shipAttributes[GetByLabel('UI/InfoWindow/OnDeath')] = {'normalAttributes': [const.attributeOnDeathAOERadius,
                                  const.attributeOnDeathSignatureRadius,
                                  const.attributeOnDeathDamageEM,
                                  const.attributeOnDeathDamageTherm,
                                  const.attributeOnDeathDamageKin,
                                  const.attributeOnDeathDamageExp]}
            shipAttributes[GetByLabel('UI/InfoWindow/JumpDriveSystems')] = {'normalAttributes': [const.attributeJumpDriveCapacitorNeed,
                                  const.attributeJumpDriveRange,
                                  const.attributeJumpDriveConsumptionType,
                                  const.attributeJumpDriveConsumptionAmount,
                                  const.attributeJumpDriveDuration,
                                  const.attributeJumpPortalCapacitorNeed,
                                  const.attributeJumpPortalConsumptionMassFactor,
                                  const.attributeJumpPortalDuration,
                                  const.attributeSpecialFuelBayCapacity,
                                  const.attributeGroupJumpDriveConsumptionAmount,
                                  const.attributeConduitJumpPassengerCount]}
            shipAttributes[GetByLabel('UI/Compare/Propulsion')] = {'normalAttributes': [const.attributeMaxVelocity]}
            self.shipAttributes = shipAttributes
        return self.shipAttributes

    def GetAttributeOrder(self):
        if not hasattr(self, 'attributeOrder'):
            self.attributeOrder = [const.attributePrimaryAttribute,
             const.attributeSecondaryAttribute,
             const.attributeRequiredSkill1,
             const.attributeRequiredSkill2,
             const.attributeRequiredSkill3,
             const.attributeRequiredSkill4,
             const.attributeRequiredSkill5,
             const.attributeRequiredSkill6]
        return self.attributeOrder

    def GetStatusAttributeInfo(self):
        if not hasattr(self, 'statusAttributeInfo'):
            cargoCapacityColor = (0.0, 0.31, 0.4)
            shipBayLoadFunc = self.GetCurrentShipBayLoad
            self.statusAttributeInfo = {const.attributeCpuOutput: {'label': GetByLabel('UI/Common/Cpu'),
                                        'loadAttributeID': const.attributeCpuLoad,
                                        'color': (0.203125, 0.3828125, 0.37890625, 1.0)},
             const.attributePowerOutput: {'label': GetByLabel('UI/Common/Powergrid'),
                                          'loadAttributeID': const.attributePowerLoad,
                                          'color': (0.40625, 0.078125, 0.03125, 1.0)},
             const.attributeUpgradeCapacity: {'label': GetByLabel('UI/Common/Calibration'),
                                              'loadAttributeID': const.attributeUpgradeLoad},
             const.attributeMaxJumpClones: {'label': GetByLabel('UI/InfoWindow/JumpClonesStatusBar'),
                                            'loadAttributeFunc': self.GetCurrentShipCloneCount},
             const.attributeCapacity: {'loadAttributeFunc': shipBayLoadFunc,
                                       'color': cargoCapacityColor},
             const.attributeDroneCapacity: {'label': GetByLabel('UI/Common/DroneBay'),
                                            'loadAttributeFunc': shipBayLoadFunc,
                                            'color': cargoCapacityColor},
             const.attributeSpecialAmmoHoldCapacity: {'label': GetByLabel('UI/Ship/AmmoHold'),
                                                      'loadAttributeFunc': shipBayLoadFunc,
                                                      'color': cargoCapacityColor},
             const.attributeSpecialGasHoldCapacity: {'label': GetByLabel('UI/Ship/GasHold'),
                                                     'loadAttributeFunc': shipBayLoadFunc,
                                                     'color': cargoCapacityColor},
             const.attributeSpecialIndustrialShipHoldCapacity: {'label': GetByLabel('UI/Ship/IndustrialShipHold'),
                                                                'loadAttributeFunc': shipBayLoadFunc,
                                                                'color': cargoCapacityColor},
             const.attributeSpecialLargeShipHoldCapacity: {'label': GetByLabel('UI/Ship/LargeShipHold'),
                                                           'loadAttributeFunc': shipBayLoadFunc,
                                                           'color': cargoCapacityColor},
             const.attributeSpecialMediumShipHoldCapacity: {'label': GetByLabel('UI/Ship/MediumShipHold'),
                                                            'loadAttributeFunc': shipBayLoadFunc,
                                                            'color': cargoCapacityColor},
             const.attributeSpecialMineralHoldCapacity: {'label': GetByLabel('UI/Ship/MineralHold'),
                                                         'loadAttributeFunc': shipBayLoadFunc,
                                                         'color': cargoCapacityColor},
             const.attributeGeneralMiningHoldCapacity: {'label': GetByLabel('UI/Ship/GeneralMiningHold'),
                                                        'loadAttributeFunc': shipBayLoadFunc,
                                                        'color': cargoCapacityColor},
             const.attributeSpecialAsteroidHoldCapacity: {'label': GetByLabel('UI/Ship/AsteroidHold'),
                                                          'loadAttributeFunc': shipBayLoadFunc,
                                                          'color': cargoCapacityColor},
             const.attributeSpecialSalvageHoldCapacity: {'label': GetByLabel('UI/Ship/SalvageHold'),
                                                         'loadAttributeFunc': shipBayLoadFunc,
                                                         'color': cargoCapacityColor},
             const.attributeSpecialShipHoldCapacity: {'label': GetByLabel('UI/Ship/ShipHold'),
                                                      'loadAttributeFunc': shipBayLoadFunc,
                                                      'color': cargoCapacityColor},
             const.attributeSpecialSmallShipHoldCapacity: {'label': GetByLabel('UI/Ship/SmallShipHold'),
                                                           'loadAttributeFunc': shipBayLoadFunc,
                                                           'color': cargoCapacityColor},
             const.attributeSpecialCommandCenterHoldCapacity: {'label': GetByLabel('UI/Ship/CommandCenterHold'),
                                                               'loadAttributeFunc': shipBayLoadFunc,
                                                               'color': cargoCapacityColor},
             const.attributeSpecialPlanetaryCommoditiesHoldCapacity: {'label': GetByLabel('UI/Ship/PlanetaryCommoditiesHold'),
                                                                      'loadAttributeFunc': shipBayLoadFunc,
                                                                      'color': cargoCapacityColor},
             const.attributeFleetHangarCapacity: {'label': GetByLabel('UI/Ship/FleetHangar'),
                                                  'loadAttributeFunc': shipBayLoadFunc,
                                                  'color': cargoCapacityColor},
             const.attributeShipMaintenanceBayCapacity: {'label': GetByLabel('UI/Ship/ShipMaintenanceBay'),
                                                         'loadAttributeFunc': shipBayLoadFunc,
                                                         'color': cargoCapacityColor},
             const.attributeSpecialFuelBayCapacity: {'label': GetByLabel('UI/Ship/FuelBay'),
                                                     'loadAttributeFunc': shipBayLoadFunc,
                                                     'color': cargoCapacityColor},
             const.attributeSpecialSubsystemHoldCapacity: {'label': GetByLabel('UI/Ship/SubsystemBay'),
                                                           'loadAttributeFunc': shipBayLoadFunc,
                                                           'color': cargoCapacityColor},
             const.attributeSpecialCorpseHoldCapacity: {'label': GetByLabel('UI/Ship/CorpseBay'),
                                                        'loadAttributeFunc': shipBayLoadFunc,
                                                        'color': cargoCapacityColor},
             const.attributeFrigateEscapeBayCapacity: {'label': GetByLabel('UI/Ship/FrigateEscapeBay'),
                                                       'loadAttributeFunc': shipBayLoadFunc,
                                                       'color': cargoCapacityColor},
             const.attributeSpecialBoosterHoldCapacity: {'label': GetByLabel('UI/Ship/BoosterBay'),
                                                         'loadAttributeFunc': shipBayLoadFunc,
                                                         'color': cargoCapacityColor},
             const.attributeSpecialMobileDepotHoldCapacity: {'label': GetByLabel('UI/Ship/MobileDepotHold'),
                                                             'loadAttributeFunc': shipBayLoadFunc,
                                                             'color': cargoCapacityColor},
             const.attributeSpecialColonyResourcesHoldCapacity: {'label': GetByLabel('UI/Ship/InfrastructureHold'),
                                                                 'loadAttributeFunc': shipBayLoadFunc,
                                                                 'color': cargoCapacityColor}}
        return self.statusAttributeInfo

    def Stop(self, memStream = None):
        self.ClearWnds()
        self.lastActive = {}
        self.wnds = {}

    def ClearWnds(self):
        self.wnds = {}
        if getattr(uicore, 'registry', None):
            for each in uicore.registry.GetWindows()[:]:
                if each is not None and not each.destroyed and each.windowID and each.windowID in ('infowindow', 'shipInfoWindow'):
                    each.Close()

    def DoSessionChanging(self, isremote, session, change):
        if session.charid is None:
            self.ClearWnds()
        if 'charid' in change and change['charid'][1] is None:
            self.TryInitializeUsedWith()

    def GetSolarSystemReport(self, solarsystemID = None):
        solarsystemID = solarsystemID or eve.session.solarsystemid or eve.session.solarsystemid2
        if solarsystemID is None:
            return
        items = self.map.GetSolarsystemItems(solarsystemID)
        types = {}
        for celestial in items:
            types.setdefault(celestial.groupID, []).append(celestial)

        for groupID in types.iterkeys():
            if groupID == const.groupStation:
                continue

    def ShowInfo(self, typeID, itemID = None, new = 0, rec = None, parentID = None, abstractinfo = None, selectTabType = None, addNewWindow = False, params = None):
        if itemID == const.factionUnknown:
            eve.Message('KillerOfUnknownFaction')
            return
        modal = uicore.registry.GetModalWindow()
        createNew = new or not settings.user.ui.Get('useexistinginfownd', 1) or uicore.uilib.Key(uiconst.VK_SHIFT)
        self.CleanUpWindows()
        self.CleanUpRwWindows()
        useWnd = None
        wnds = self._GetOpenWindowsForType(typeID)
        if len(wnds) and not createNew:
            lastActive = self._GetLastActive(typeID)
            if lastActive is not None and lastActive in wnds:
                if not lastActive.destroyed:
                    useWnd = lastActive
            wnd = wnds[-1]
            if not modal or modal and modal.parent == wnd.parent:
                if not wnd.destroyed:
                    useWnd = wnd
        shouldReuseExistingWindow = useWnd and not modal
        if shouldReuseExistingWindow and not addNewWindow:
            useWnd.ReconstructInfoWindow(typeID, itemID, rec=rec, parentID=parentID, abstractinfo=abstractinfo, selectTabType=selectTabType, params=params)
            useWnd.Maximize()
        else:
            useWnd = self.CreateInfoWindow(typeID, itemID, rec, parentID, modal, abstractinfo, selectTabType, params)
            self._RegisterWindow(useWnd)
        if modal and not modal.destroyed and modal.windowID != 'progresswindow':
            useWnd.ShowModal()
        return useWnd

    def CloseRwWindows(self):
        for each in self.rwWindows:
            if each and not each.destroyed:
                each.Close()

        self.rwWindows = []

    def CleanUpWindows(self):
        for values in self.wnds.itervalues():
            for each in values:
                if each is None or each.destroyed:
                    self._UnregisterWindow(each)

    def CleanUpRwWindows(self):
        for each in self.rwWindows:
            if each is None or each.destroyed:
                self.rwWindows.remove(each)

    def CreateInfoWindow(self, typeID, itemID, rec, parentID, modal, abstractinfo, selectTabType, params = None):
        wndClass = self._GetInfoWindowClass(typeID)
        return wndClass.Open(windowInstanceID=blue.os.GetWallclockTime(), typeID=typeID, itemID=itemID, rec=rec, parentID=parentID, ignoreStack=modal, abstractinfo=abstractinfo, selectTabType=selectTabType, params=params)

    def UpdateWnd(self, itemID, maximize = 0):
        for values in self.wnds.itervalues():
            for wnd in values:
                if isinstance(wnd, InfoWindow):
                    if wnd.itemID == itemID or getattr(wnd.sr, 'corpID', None) == itemID or getattr(wnd.sr, 'allianceID', None) == itemID:
                        wnd.ReconstructInfoWindow(wnd.typeID, wnd.itemID)
                        if maximize:
                            wnd.Maximize()
                        break

    def UnregisterWindow(self, wnd, *args):
        self._UnregisterWindow(wnd)
        if self._GetLastActive(wnd.__class__) == wnd:
            self._ClearLastActive(wnd.__class__)

    def OnActivateWnd(self, wnd):
        self._SetLastActive(wnd)

    def GetRankEntry(self, rank, hilite = False):
        facwarcurrrank = getattr(rank, 'currentRank', 1)
        facwarfaction = getattr(rank, 'factionID', None)
        if rank and facwarfaction is not None:
            lbl, _ = sm.GetService('facwar').GetRankLabel(facwarfaction, facwarcurrrank)
            if hilite:
                lbl = GetByLabel('UI/FactionWarfare/CurrentRank', currentRankName=lbl)
            return GetFromClass(RankEntry, {'label': get_faction_name(facwarfaction),
             'text': lbl,
             'rank': facwarcurrrank,
             'warFactionID': facwarfaction,
             'selected': False,
             'typeID': const.typeRank,
             'showinfo': 1,
             'line': 1})

    def GetMedalEntry(self, info, details, *args):
        d = details
        numAwarded = 0
        if type(info) == list:
            m = info[0]
            numAwarded = len(info)
        else:
            m = info
        sublevel = 1
        if args:
            sublevel = args[0]
        medalribbondata = uix.FormatMedalData(d)
        title = m.title
        if numAwarded > 0:
            title = GetByLabel('UI/InfoWindow/MedalAwardedNumTimes', medalName=title, numTimes=numAwarded)
        description = m.description
        medalTitleText = GetByLabel('UI/InfoWindow/MedalTitle')
        return GetFromClass(MedalRibbonEntry, {'label': title,
         'text': description,
         'sublevel': sublevel,
         'id': m.medalID,
         'line': 1,
         'abstractinfo': medalribbondata,
         'typeID': const.typeMedal,
         'itemID': m.medalID,
         'icon': 'ui_51_64_4',
         'showinfo': True,
         'sort_%s' % medalTitleText: '_%s' % title.lower(),
         'iconsize': 26})

    def EditContact(self, wnd, itemID, edit):
        addressBookSvc = sm.GetService('addressbook')
        addressBookSvc.AddToPersonalMulti(itemID, 'contact', edit)

    def UpdateContactButtons(self, wnd, itemID):
        addressBookSvc = sm.GetService('addressbook')
        if not addressBookSvc.IsInAddressBook(itemID, 'contact'):
            wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/PeopleAndPlaces/AddContact'),
              self.EditContact,
              (wnd, itemID, False),
              81)]
        else:
            wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/PeopleAndPlaces/EditContact'),
              self.EditContact,
              (wnd, itemID, True),
              81)]

    def GetCurrentShipCloneCount(self, attributeID):
        if eveCfg.GetActiveShip():
            return len(sm.GetService('clonejump').GetShipClones())
        return 0

    def GetCurrentShipBayLoad(self, attributeID):
        attributeToInventoryFlagMap = {const.attributeCapacity: const.flagCargo,
         const.attributeDroneCapacity: const.flagDroneBay,
         const.attributeFrigateEscapeBayCapacity: const.flagFrigateEscapeBay,
         const.attributeSpecialAmmoHoldCapacity: const.flagSpecializedAmmoHold,
         const.attributeSpecialGasHoldCapacity: const.flagSpecializedGasHold,
         const.attributeSpecialIndustrialShipHoldCapacity: const.flagSpecializedIndustrialShipHold,
         const.attributeSpecialLargeShipHoldCapacity: const.flagSpecializedLargeShipHold,
         const.attributeSpecialMediumShipHoldCapacity: const.flagSpecializedMediumShipHold,
         const.attributeSpecialMineralHoldCapacity: const.flagSpecializedMineralHold,
         const.attributeGeneralMiningHoldCapacity: const.flagGeneralMiningHold,
         const.attributeSpecialAsteroidHoldCapacity: const.flagSpecialAsteroidHold,
         const.attributeSpecialIceHoldCapacity: const.flagSpecializedIceHold,
         const.attributeSpecialSalvageHoldCapacity: const.flagSpecializedSalvageHold,
         const.attributeSpecialShipHoldCapacity: const.flagSpecializedShipHold,
         const.attributeSpecialSmallShipHoldCapacity: const.flagSpecializedSmallShipHold,
         const.attributeSpecialCommandCenterHoldCapacity: const.flagSpecializedCommandCenterHold,
         const.attributeSpecialPlanetaryCommoditiesHoldCapacity: const.flagSpecializedPlanetaryCommoditiesHold,
         const.attributeFleetHangarCapacity: const.flagFleetHangar,
         const.attributeShipMaintenanceBayCapacity: const.flagShipHangar,
         const.attributeSpecialFuelBayCapacity: const.flagSpecializedFuelBay,
         const.attributeSpecialSubsystemHoldCapacity: const.flagSubsystemBay,
         const.attributeSpecialCorpseHoldCapacity: const.flagCorpseBay,
         const.attributeSpecialBoosterHoldCapacity: const.flagBoosterBay,
         const.attributeSpecialMobileDepotHoldCapacity: const.flagMobileDepotHold,
         const.attributeSpecialColonyResourcesHoldCapacity: const.flagColonyResourcesHold}
        return sm.GetService('clientDogmaIM').GetDogmaLocation().GetCapacity(eveCfg.GetActiveShip(), attributeID, attributeToInventoryFlagMap[attributeID]).used

    def GetStatusBarEntryForAttribute(self, attributeID, itemID = None, typeID = None, modifiedAttribute = None):
        data = self.GetStatusBarDataForAttribute(attributeID, itemID, typeID, modifiedAttribute)
        if data is None:
            return
        return GetFromClass(StatusBar, data=data)

    def GetStatusBarDataForAttribute(self, attributeID, itemID = None, typeID = None, modifiedAttribute = None):
        if itemID is None or itemID != eveCfg.GetActiveShip():
            return
        statusAttributeInfo = self.GetStatusAttributeInfo().get(attributeID, None)
        if statusAttributeInfo is None:
            return
        GAV = self.GetGAVFunc(itemID, typeID)
        total = GAV(attributeID)
        if total == 0.0:
            return
        loadAttributeID = statusAttributeInfo.get('loadAttributeID', attributeID)
        loadGetterFunc = statusAttributeInfo.get('loadAttributeFunc', GAV)
        load = loadGetterFunc(loadAttributeID)
        status = load / float(total)
        attributeFormatInfo = attributeFormat.GetAttribute(attributeID)
        return {'attributeID': attributeID,
         'label': statusAttributeInfo.get('label', dogma_data.get_attribute_display_name(attributeID)),
         'text': GetByLabel('UI/InfoWindow/StatusAttributeLabel', numerator=load, denominator=total, unit=FormatUnit(attributeFormatInfo.unitID)),
         'value': status,
         'iconID': attributeFormatInfo.iconID,
         'color': statusAttributeInfo.get('color', Color.GRAY3),
         'gradientBrightnessFactor': 1.2,
         'modifiedAttribute': modifiedAttribute,
         'itemID': itemID}

    def UpdateDataShip(self, wnd, typeID, itemID):
        wnd.dynamicTabs.append(TAB_TRAITS)
        attributesByCaption = self.GetShipAndDroneAttributes()
        attributeEntries, _ = self.GetItemAttributeScrolllistAndAttributesList(itemID, typeID, attributesByCaption)
        wnd.data[TAB_ATTIBUTES]['items'] += attributeEntries
        data = self.GetWarpSpeedData(typeID, itemID)
        if data:
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data))
        wnd.dynamicTabs.append(TAB_FITTING)
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)
        if typeID in cfg.certificates['masteries']:
            wnd.dynamicTabs.append(TAB_MASTERY)
        if sm.GetService('shipTree').IsInShipTree(typeID):
            wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/InfoWindow/ShowInISIS'),
              self.ShowShipInISIS,
              typeID,
              81)]
        wnd.dynamicTabs.append(TAB_SHIPAVAILABLESKINLICENSES)

    def GetWarpSpeedData(self, typeID, itemID):
        shipinfo = sm.GetService('godma').GetItem(itemID) if itemID is not None else None
        warpSpeedText, warpSpeedWithMultipliers, typeWarpSpeedWithMultipliers, corruptionWarpSpeedIncrease = self.GetBaseWarpSpeed(typeID, shipinfo, itemID)
        if warpSpeedText:

            def OnBaseWarpClicked(aID, iID):
                logLine = 'Base warp speed for %s = %s' % (iID, warpSpeedText)
                self.LogError(logLine)
                return self.OnAttributeClick(aID, iID)

            attributeID = const.attributeBaseWarpSpeed
            iconID = dogma_data.get_attribute_icon_id(attributeID)
            displayName = dogma_data.get_attribute_display_name(attributeID)
            data = {'attributeID': attributeID,
             'line': 1,
             'label': displayName,
             'text': warpSpeedText,
             'iconID': iconID,
             'OnClick': (OnBaseWarpClicked, attributeID, itemID),
             'itemID': itemID}
            if warpSpeedWithMultipliers != typeWarpSpeedWithMultipliers:
                m = CreateAttribute(attributeID, warpSpeedWithMultipliers, typeWarpSpeedWithMultipliers)
                data['modifiedAttribute'] = m
                data['extraModifyingAttrIDs'] = [const.attributeWarpSpeedMultiplier]
                if not FloatCloseEnough(corruptionWarpSpeedIncrease, 0):
                    direction = -1 if corruptionWarpSpeedIncrease < 0.0 else 1
                    factorText = GetByLabel('UI/PirateInsurgencies/CorruptionWarpSpeedHint', stageThreshold=WARP_SPEED_INCREASE_STAGE_THRESHOLD)
                    data['extraModifyingFactors'] = [(factorText, direction)]
            return data

    def ApplyAttributeTooltip(self, entries):
        for entry in entries:
            if not hasattr(entry, 'attributeID'):
                continue
            tooltipTitleText, tooltipDescriptionText = GetAttributeTooltipTitleAndDescription(entry.attributeID)
            if tooltipTitleText:
                entry.tooltipPanelClassInfo = TooltipHeaderDescriptionWrapper(header=tooltipTitleText, description=tooltipDescriptionText, tooltipPointer=uiconst.POINT_RIGHT_2)

    def GetGroupedAttributesEntry(self, groupedAttributes, itemID, typeID):
        attributeDictForType, attributeDict = self.GetAttributeDictForItem(itemID, typeID)
        modifiedAttributesDict = self.FindAttributesThatHaveBeenModified(attributeDictForType, attributeDict)
        attributeInfoList = []
        for dmgType, eachAttributeID in groupedAttributes:
            if eachAttributeID not in attributeDict:
                dogmaAttributeInfo = attributeFormat.GetAttribute(eachAttributeID)
                if dogmaAttributeInfo.unitID in (const.unitInverseAbsolutePercent, const.unitInversedModifierPercent):
                    value = 1
                else:
                    value = 0
            else:
                value = attributeDict[eachAttributeID]
            formatInfo = GetFormattedAttributeAndValue(eachAttributeID, value)
            if not formatInfo:
                attributeInfoList.append(None)
                continue
            attributeTypeInfoUnitID = dogma_data.get_attribute_unit_id(eachAttributeID)
            if attributeTypeInfoUnitID in (const.unitInverseAbsolutePercent, const.unitInversedModifierPercent):
                value = 1 - value
            modifiedAttribute = modifiedAttributesDict.get(eachAttributeID)
            attributeInfo = {'dmgType': dmgType,
             'text': formatInfo.displayName,
             'iconID': formatInfo.iconID,
             'value': value,
             'valueText': formatInfo.value,
             'attributeID': eachAttributeID,
             'modifiedAttribute': modifiedAttribute,
             'itemID': itemID}
            attributeInfoList.append(attributeInfo)

        return GetFromClass(DamageEntry, {'attributeInfoList': attributeInfoList,
         'OnClick': lambda attributeID: self.OnAttributeClick(attributeID, itemID)})

    def ShowShipInISIS(self, typeID):
        sm.GetService('shipTreeUI').OpenAndShowShip(typeID)

    def UpdateSkyhook(self, wnd, typeID, itemID):
        attributeScroll = wnd.data[TAB_ATTIBUTES]['items']
        attributeScroll.append(GetFromClass(Header, {'label': GetByLabel('UI/Common/Other')}))
        slimitem = sm.GetService('michelle').GetItem(itemID)
        banAttrs = self.GetAttributesSuppressedByComponents(typeID)
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID, banAttrs=banAttrs)
        attributeScroll += attributeScrollListForItem
        if slimitem and slimitem.planetID:
            planetSlimItem = sm.GetService('michelle').GetItem(slimitem.planetID)
            data = {'line': 1,
             'label': evetypes.GetGroupName(planetSlimItem.typeID),
             'text': cfg.evelocations.Get(slimitem.planetID).name,
             'typeID': planetSlimItem.typeID,
             'itemID': planetSlimItem.itemID}
            attributeScroll.append(GetFromClass(LabelTextSidesAttributes, data=data))
        uthread.new(self.FetchDynamicOrbitalAttributes, wnd, wnd.data[TAB_ATTIBUTES], itemID)

    def UpdateSequenceBinder(self, wnd, typeID, itemID):
        wnd.data[DATA_BUTTONS].append((GetByLabel('UI/Personalization/ShipSkins/OpenSKINR'),
         uicore.cmd.OpenShipSKINRWindow,
         (),
         None,
         False,
         False,
         False,
         None,
         None,
         Button,
         None,
         None,
         None,
         None,
         None,
         OPEN_SKINR_BUTTON_INFO_WINDOW_ANALYTIC_ID))

    def UpdateDesignElement(self, wnd, typeID, itemID):
        wnd.data[DATA_BUTTONS].append((GetByLabel('UI/Personalization/ShipSkins/OpenSKINR'),
         uicore.cmd.OpenShipSKINRWindow,
         (),
         None,
         False,
         False,
         False,
         None,
         None,
         Button,
         None,
         None,
         None,
         None,
         None,
         OPEN_SKINR_BUTTON_INFO_WINDOW_ANALYTIC_ID))

    def UpdateStructure(self, wnd, typeID, itemID):
        if itemID and isinstance(itemID, long):
            wnd.dynamicTabs.append(TAB_DESCRIPTION_DYNAMIC)
        wnd.dynamicTabs.append(TAB_TRAITS)
        attributesByCaption = self.GetShipAndDroneAttributes()
        attributeEntries, addedAttributes = self.GetItemAttributeScrolllistAndAttributesList(itemID, typeID, attributesByCaption)
        wnd.data[TAB_ATTIBUTES]['items'] += attributeEntries
        fittingAttributes = GetFittingAttributeIDs() + [const.attributeCpuLoad, const.attributePowerLoad]
        banAttrs = addedAttributes + self.GetSkillAttrs() + fittingAttributes
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID, typeID, banAttrs=banAttrs)
        if attributeScrollListForItem:
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/Miscellaneous')}))
            wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)
        wnd.dynamicTabs.append(TAB_FITTING)
        structureInfo = None
        structureOwner = None
        outOfCommissionText = '<b><color=red>%s</color></b>' % GetByLabel('UI/Structures/StructureOutOfCommission')
        if itemID is not None:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(itemID)
            if structureInfo:
                structureOwner = structureInfo.ownerID
                solarsystemID = structureInfo.solarSystemID
                mapData = cfg.mapSystemCache.Get(solarsystemID)
                constellationID = mapData.constellationID
                regionID = mapData.regionID
                if not structureInfo.inSpace:
                    wnd.data[TAB_LOCATION]['items'].append(GetFromClass(Text, {'line': 1,
                     'text': outOfCommissionText}))
                for locID in [regionID, constellationID, solarsystemID]:
                    mapItem = self.map.GetItem(locID)
                    if mapItem is not None:
                        if mapItem.typeID == const.typeSolarSystem:
                            text = self.GetColorCodedSecurityStringForSystem(mapItem.itemID, mapItem.itemName)
                            text = text.replace('<t>', ' ')
                        else:
                            text = mapItem.itemName
                        entry = GetFromClass(LabelTextTop, {'line': 1,
                         'label': evetypes.GetName(mapItem.typeID),
                         'text': text,
                         'typeID': mapItem.typeID,
                         'itemID': mapItem.itemID})
                        wnd.data[TAB_LOCATION]['items'].append(entry)

        if itemID is not None and structureInfo is not None:
            serviceEntryList = self.GetServicesForStructure(itemID, typeID)
            if not structureInfo.inSpace:
                wnd.data[TAB_SERVICES]['items'].append(GetFromClass(Text, {'line': 1,
                 'text': outOfCommissionText}))
            wnd.data[TAB_SERVICES]['items'] += serviceEntryList
            wars = getattr(structureInfo, 'wars', None)
            if wars:
                wnd.dynamicTabs.append(TAB_WARHQ)
        if structureInfo and evetypes.IsUpwellStargate(typeID):
            destinations = sm.RemoteSvc('structureJumpBridgeMgr').GetLinkedStructure(itemID)
            if destinations:
                destinationStructureID, destinationSolarsystemID = destinations
                structureInfo = sm.GetService('structureDirectory').GetStructureInfo(destinationStructureID)
                if structureInfo:
                    structureLink = GetShowInfoLink(structureInfo.typeID, structureInfo.itemName, destinationStructureID)
                    destLabel = GetByLabel('UI/InfoWindow/DestinationJumpBridgeInSolarsystem', structureLink=structureLink, solarsystem=destinationSolarsystemID)
                    wnd.data[TAB_JUMPS]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                     'label': GetByLabel('UI/Common/Jump'),
                     'text': destLabel,
                     'typeID': const.groupSolarSystem,
                     'itemID': destinationSolarsystemID}))
        if structureOwner is not None:
            wnd.data[DATA_BUTTONS] = [(GetByLabel('UI/Inflight/SetDestination'),
              self.SetDestination,
              (itemID,),
              81)]

    def GetServicesForStructure(self, structureID, typeID):
        serviceList = []
        servicesAndValues = sm.GetService('structureServices').CharacterGetServices(structureID).items()
        for serviceID, settingValue in sorted(servicesAndValues):
            if serviceID in META_SERVICES:
                continue
            if typeID in STRUCTURES_WITHOUT_ONLINE_SERVICES and serviceID in ONLINE_SERVICES:
                continue
            valueText = self._GetValueText(serviceID, settingValue)
            if valueText is None:
                continue
            icon = GetServiceIcon(serviceID)
            if icon is None:
                icon = stationServiceConst.serviceDataByServiceID[serviceID].iconID
            serviceList.append(GetFromClass(LabelTextSides, {'line': 2,
             'selectable': 0,
             'label': GetByLabel(GetServiceLabel(serviceID)),
             'iconID': icon,
             'iconsize': 24,
             'height': 28,
             'iconoffset': 8,
             'labeloffset': 8,
             'text': valueText}))

        return serviceList

    def _GetValueText(self, serviceID, settingValue):
        settingIDForService = structures.SERVICES_ACCESS_SETTINGS.get(serviceID, None)
        if settingIDForService is None:
            return
        settingInfo = structures.SETTING_OBJECT_BY_SETTINGID.get(settingIDForService, None)
        if not settingInfo:
            return
        valueText = ''
        settingType = settingInfo.valueType
        if settingType in VALUE_TYPES:
            unit = GetUnit(settingType)
            value = settingValue
            if settingType == structures.SETTINGS_TYPE_ISK:
                valueText = FmtISK(value, 0)
            elif settingType == structures.SETTINGS_TYPE_PERCENTAGE:
                if settingInfo.decimals == 2:
                    valueText = GetByLabel('UI/Common/Formatting/PercentageDecimals2', percentage=value)
                else:
                    valueText = GetByLabel('UI/Common/Formatting/PercentageDecimal', percentage=value)
            else:
                if settingType == structures.SETTINGS_TYPE_INT:
                    value = int(value)
                valueText = '%s %s' % (value, unit)
        return valueText

    def UpdateDataDrone(self, wnd, typeID, itemID):
        attributesByCaption = self.GetShipAndDroneAttributes()
        attributeEntries, addedAttributes = self.GetItemAttributeScrolllistAndAttributesList(itemID, typeID, attributesByCaption)
        wnd.data[TAB_ATTIBUTES]['items'] += attributeEntries
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID, typeID, banAttrs=addedAttributes + self.GetSkillAttrs())
        if attributeScrollListForItem:
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/Miscellaneous')}))
            wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)

    def UpdateDataFighter(self, wnd, typeID, itemID):
        attributesByCaption = self.GetFighterAttributes()
        attributeEntries, addedAttributes = self.GetItemAttributeScrolllistAndAttributesList(itemID, typeID, attributesByCaption)
        wnd.data[TAB_ATTIBUTES]['items'] += attributeEntries
        wnd.dynamicTabs.append(TAB_FIGHTER_ABILITIES)
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)

    def GetItemAttributeScrolllistAndAttributesList(self, itemID, typeID, attributesByCaption):
        attrDict = self.GetAttributeDictForType(typeID)
        addedAttributes = []
        scrollList = []
        for caption, attrs in attributesByCaption.iteritems():
            normalAttributes = attrs['normalAttributes']
            groupedAttributes = attrs.get('groupedAttributes', [])
            shipAttr = [ each for each in normalAttributes if each in attrDict ]
            newEntries = []
            if shipAttr:
                attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID, attrList=shipAttr)
                newEntries += attributeScrollListForItem
                addedAttributes += [ x.attributeID for x in attributeScrollListForItem ]
                for eachNode in attributeScrollListForItem:
                    if getattr(eachNode, 'attributeIDs', None):
                        addedAttributes += eachNode.attributeIDs

            if groupedAttributes:
                entry = self.GetGroupedAttributesEntry(groupedAttributes, itemID, typeID)
                addedAttributes += [ g[1] for g in groupedAttributes ]
                newEntries.append(entry)
            if newEntries:
                scrollList.append(GetFromClass(Header, {'label': caption}))
                scrollList += newEntries

        return (scrollList, addedAttributes)

    def UpdateDataModule(self, wnd, typeID, itemID):
        if not itemID:
            damageTypes = dogma_data.get_type_attributes(typeID)
            firstAmmoLoaded = itertoolsext.first_or_default([ x for x in damageTypes if x.attributeID == const.attributeAmmoLoaded ])
            if firstAmmoLoaded:
                damageScrollList = self.GetAttributeScrollListForType(typeID=firstAmmoLoaded.value, attrList=DAMAGE_ATTRIBUTES)
                wnd.data[TAB_ATTIBUTES]['items'] += damageScrollList
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID, banAttrs=[const.attributeCpu,
         const.attributePower,
         const.attributeRigSize,
         const.attributeUpgradeCost,
         const.attributeMass] + self.GetSkillAttrs())
        wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        wnd.data[TAB_ATTIBUTES]['items'] += GetDbuffInfoEntriesForItem(itemID, typeID)
        effectTypeScrollList = self.GetEffectTypeInfo(typeID=typeID, effList=[const.effectHiPower,
         const.effectMedPower,
         const.effectLoPower,
         const.effectRigSlot,
         const.effectSubSystem,
         const.effectServiceSlot,
         const.effectTurretFitted,
         const.effectLauncherFitted])
        wnd.data[TAB_FITTING]['items'] += effectTypeScrollList
        fittingScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID, attrList=(const.attributeCpu,
         const.attributePower,
         const.attributeRigSize,
         const.attributeServiceSlots,
         const.attributeUpgradeCost))
        wnd.data[TAB_FITTING]['items'] += fittingScrollListForItem
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)
        wnd.dynamicTabs.append(TAB_TRAITS)
        if self.GetUsedWithTypeIDs(wnd.typeID):
            wnd.dynamicTabs.append(TAB_USEDWITH)

    def UpdateComponentData(self, wnd, typeID, itemID):
        attributeScroll = wnd.data[TAB_ATTIBUTES]['items']
        spaceComponentScrollList = self.GetSpaceComponentAttrItemInfo(typeID, itemID)
        attributeScroll += spaceComponentScrollList

    def UpdateInfrastructureUpgrades(self, wnd, typeID, itemID):
        try:
            staticInfo = self.sovHubSvc.GetStaticDataForUpgrade(typeID)
        except (SovUpgradeDataUnavailableError, TimeoutException):
            return

        if staticInfo is None:
            return
        attributeEntries = [GetFromClass(Header, {'label': GetByLabel('UI/Sovereignty/SovHub/Upgrades/ResourceConsumption')})]
        if staticInfo.power:
            attributeEntries.append(GetFromClass(LabelTextSides, {'label': localization.GetByLabel('UI/Sovereignty/SovHub/Upgrades/PowerCost'),
             'text': staticInfo.power}))
        if staticInfo.workforce:
            attributeEntries.append(GetFromClass(LabelTextSides, {'label': localization.GetByLabel('UI/Sovereignty/SovHub/Upgrades/WorkforceCost'),
             'text': staticInfo.workforce}))
        if staticInfo.fuel_type_id and (staticInfo.consumption_per_hour or staticInfo.startup_cost):
            attributeEntries.append(GetFromClass(LabelTextSides, {'label': localization.GetByLabel('UI/Sovereignty/SovHub/Upgrades/FuelType'),
             'text': evetypes.GetName(staticInfo.fuel_type_id),
             'iconID': evetypes.GetIconID(staticInfo.fuel_type_id),
             'typeID': staticInfo.fuel_type_id}))
            attributeEntries.append(GetFromClass(LabelTextSides, {'label': localization.GetByLabel('UI/Sovereignty/SovHub/Upgrades/FuelStartupCost'),
             'text': localization.GetByLabel('UI/InfoWindow/ValueAndUnit', value=staticInfo.startup_cost, unit=FormatUnit(dogma.const.unitUnits))}))
            attributeEntries.append(GetFromClass(LabelTextSides, {'label': localization.GetByLabel('UI/Sovereignty/SovHub/Upgrades/FuelConsumptionPerHour'),
             'text': localization.GetByLabel('UI/InfoWindow/ValueAndUnit', value=staticInfo.consumption_per_hour, unit=FormatUnit(dogma.const.unitUnits))}))
        attributeScroll = wnd.data[TAB_ATTIBUTES]['items']
        attributeScroll += attributeEntries

    def UpdateDataDeployable(self, wnd, typeID, itemID):
        attributeScroll = wnd.data[TAB_ATTIBUTES]['items']
        banAttrs = self.GetAttributesSuppressedByComponents(typeID)
        banAttrs.extend(self.GetSkillAttrs())
        attributeScroll.append(GetFromClass(Header, {'label': GetByLabel('UI/Common/Other')}))
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID, banAttrs=banAttrs)
        attributeScroll += attributeScrollListForItem
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)

    def UpdateDataSecureContainer(self, wnd, itemID):
        self.UpdateDataModule(wnd, wnd.typeID, itemID)
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        ball = bp.GetBall(itemID)
        if not ball or ball.isFree:
            return
        bpr = sm.GetService('michelle').GetRemotePark()
        if bpr:
            expiry = bpr.GetContainerExpiryDate(itemID)
            daysLeft = max(0, (expiry - blue.os.GetWallclockTime()) / const.DAY)
            expiryText = GetByLabel('UI/Common/NumDays', numDays=daysLeft)
            expiryLabel = GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/Common/Expires'),
             'text': expiryText,
             'iconID': const.iconDuration})
            wnd.data[TAB_ATTIBUTES]['items'].append(expiryLabel)

    def UpdateDataCharge(self, wnd, typeID, itemID):
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID, banAttrs=self.GetSkillAttrs())
        wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        bsd, bad = self.GetBaseDamageValue(typeID)
        if bad is not None and bsd is not None:
            text = localization.formatters.FormatNumeric(bsd[0], useGrouping=True, decimalPlaces=1)
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/InfoWindow/BaseShieldDamageLabel'),
             'text': text,
             'iconID': bsd[1]}))
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/InfoWindow/BaseArmorDamageLabel'),
             'text': localization.formatters.FormatNumeric(bad[0], useGrouping=True, decimalPlaces=1),
             'iconID': bad[1]}))
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)
        wnd.data[TAB_ATTIBUTES]['items'] += GetDbuffInfoEntriesForItem(itemID, typeID)
        if self.GetUsedWithTypeIDs(wnd.typeID):
            wnd.dynamicTabs.append(TAB_USEDWITH)

    @telemetry.ZONE_METHOD
    def AddUsedWithForOneTypeAndTryConstructForAll(self, typeID):
        if evetypes.GetCategoryID(typeID) == const.categoryCharge:
            self._AddUsedWithForAmmoTypeID(typeID)
        else:
            self._AddUsedWithTypeIDs([typeID])
        self.TryInitializeUsedWith()

    def TryInitializeUsedWith(self):
        if not session.charid:
            return
        if not self._usedWithInitializing:
            self._usedWithInitializing = True
            uthread.new(self.ConstructUsedWithAllTypeIDs)

    @telemetry.ZONE_METHOD
    def ConstructUsedWithAllTypeIDs(self):
        try:
            typeIDs = evetypes.GetTypeIDsByCategories((const.categoryModule, const.categoryStructureModule))
            self._AddUsedWithTypeIDs(typeIDs)
        finally:
            self._usedWithInitializing = False

    @telemetry.ZONE_METHOD
    def _AddUsedWithTypeIDs(self, typeIDs):
        usedWith = defaultdict(set)
        godmaStateManager = sm.GetService('godma').GetStateManager()
        for typeID in typeIDs:
            if not evetypes.IsPublished(typeID):
                continue
            godmaType = godmaStateManager.GetType(typeID)
            for attrName in ('chargeGroup1', 'chargeGroup2', 'chargeGroup3', 'chargeGroup4'):
                if not godmaType.AttributeExists(attrName):
                    continue
                groupID = getattr(godmaType, attrName)
                if not evetypes.GroupExists(groupID):
                    continue
                for typeIDInGroup in evetypes.GetTypeIDsByGroup(groupID):
                    if not evetypes.IsPublished(typeIDInGroup):
                        continue
                    if hasattr(godmaType, 'capacity') and godmaType.capacity < evetypes.GetVolume(typeIDInGroup):
                        continue
                    chargeGodmaType = godmaStateManager.GetType(typeIDInGroup)
                    if not godmaType.chargeSize or chargeGodmaType.chargeSize == godmaType.chargeSize:
                        usedWith[typeIDInGroup].add(typeID)
                        usedWith[typeID].add(typeIDInGroup)

            blue.pyos.BeNice()

        if self._usedWithTypeIDs is None:
            self._usedWithTypeIDs = usedWith
        else:
            self._usedWithTypeIDs.update(usedWith)

    def _AddUsedWithForAmmoTypeID(self, chargeTypeID):
        if not evetypes.IsPublished(chargeTypeID):
            return
        dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
        launcherGroupAttributes = [const.attributeLauncherGroup,
         const.attributeLauncherGroup2,
         const.attributeLauncherGroup3,
         const.attributeLauncherGroup4,
         const.attributeLauncherGroup5,
         const.attributeLauncherGroup6]
        moduleTypeIDs = set()
        for attributeID in launcherGroupAttributes:
            launhcerGroupID = dogmaStaticMgr.GetTypeAttribute(chargeTypeID, attributeID)
            if launhcerGroupID is None:
                continue
            moduleTypeIDs.update(evetypes.GetTypeIDsByGroup(int(launhcerGroupID)))

        self._AddUsedWithTypeIDs(moduleTypeIDs)

    @telemetry.ZONE_METHOD
    def GetUsedWithTypeIDs(self, typeID):
        if self._usedWithTypeIDs is None:
            self.AddUsedWithForOneTypeAndTryConstructForAll(typeID)
        return self._usedWithTypeIDs.get(typeID, None)

    def UpdateDataCharacter(self, wnd, typeID, itemID):
        if not idCheckers.IsNPC(itemID):
            if session.charid != itemID:
                wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/Chat/StartConversation'), lambda : GetChatService().Invite(itemID))]
                self.UpdateContactButtons(wnd, itemID)
            wnd.dynamicTabs.append(TAB_EMPLOYMENTHISTORY)
            self.UpdateDataDecorations(wnd, typeID, itemID)
        else:
            self.UpdateDataAgent(wnd, typeID, itemID)
        wnd.dynamicTabs.append(TAB_NOTES)
        if itemID != session.charid:
            wnd.dynamicTabs.append(TAB_STANDINGS)

    def UpdateDataDecorations(self, wnd, typeID, itemID):
        medalsEntries = GetMedalScrollEntries(itemID, True, True)
        wnd.data[TAB_MEDALS]['items'] = medalsEntries
        rank = sm.GetService('facwar').GetCharacterRankInfo(itemID)
        if rank:
            wnd.data[TAB_RANKS]['items'].append(self.GetRankEntry(rank))
        if not medalsEntries and not rank:
            wnd.dynamicTabs.append(TAB_DECORATIONS)

    def UpdateDataCorp(self, wnd, typeID, itemID):
        if not idCheckers.IsNPC(itemID):
            self.UpdateContactButtons(wnd, itemID)
            wnd.dynamicTabs.append(TAB_ALLIANCEHISTORY)
            wnd.dynamicTabs.append(TAB_WARHISTORY)
        parallelCalls = []
        parallelCalls.append((sm.RemoteSvc('config').GetStationSolarSystemsByOwner, (itemID,)))
        if idCheckers.IsNPC(itemID):
            parallelCalls.append((sm.RemoteSvc('corporationSvc').GetCorpInfo, (itemID,)))
        else:
            parallelCalls.append((lambda : None, ()))
        parallelCalls.append((get_npc_corporation, (itemID,)))
        systems, corpmktinfo, npcCorpInfo = uthread.parallel(parallelCalls)
        if npcCorpInfo and getattr(npcCorpInfo, 'factionID', None):
            wnd.dynamicTabs.append(TAB_WARHISTORY)
        founderdone = 0
        if evetypes.GetGroupID(cfg.eveowners.Get(wnd.corpinfo.ceoID).typeID) == const.groupCharacter:
            if wnd.corpinfo.creatorID == wnd.corpinfo.ceoID:
                ceoLabel = GetByLabel('UI/Corporations/CorpUIHome/CeoAndFounder')
                founderdone = 1
            else:
                ceoLabel = GetByLabel('UI/Corporations/Common/CEO')
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': ceoLabel,
             'text': cfg.eveowners.Get(wnd.corpinfo.ceoID).name,
             'typeID': cfg.eveowners.Get(wnd.corpinfo.ceoID).typeID,
             'itemID': wnd.corpinfo.ceoID}))
        if not founderdone and evetypes.GetGroupID(cfg.eveowners.Get(wnd.corpinfo.creatorID).typeID) == const.groupCharacter:
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/Corporations/Common/Founder'),
             'text': cfg.eveowners.Get(wnd.corpinfo.creatorID).name,
             'typeID': cfg.eveowners.Get(wnd.corpinfo.creatorID).typeID,
             'itemID': wnd.corpinfo.creatorID}))
        if wnd.corpinfo.allianceID:
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/Common/Alliance'),
             'text': cfg.eveowners.Get(wnd.corpinfo.allianceID).name,
             'typeID': const.typeAlliance,
             'itemID': wnd.corpinfo.allianceID}))
        for configName, label in [('tickerName', GetByLabel('UI/Corporations/CorpUIHome/TickerName')),
         ('shares', GetByLabel('UI/Corporations/CorpUIHome/Shares')),
         ('memberCount', GetByLabel('UI/Corporations/CorpUIHome/MemberCount')),
         ('taxRate', GetByLabel('UI/Corporations/CorpUIHome/ISKTaxRate')),
         ('loyaltyPointTaxRate', GetByLabel('UI/Corporations/CorpUIHome/LPTaxRate')),
         ('friendlyFire', GetByLabel('UI/Corporations/CorpUIHome/FriendlyFire'))]:
            if configName == 'memberCount' and idCheckers.IsNPC(itemID):
                continue
            val = getattr(wnd.corpinfo, configName, 0.0)
            decoClass = LabelTextSidesAttributes
            moreInfoHint = ''
            if configName == 'taxRate':
                val = GetByLabel('UI/Common/Percentage', percentage=val * 100)
                decoClass = LabelTextSidesMoreInfo
                min_isk_amount_text = FmtWalletCurrency(amt=const.minCorporationTaxAmount, currency=const.creditsISK)
                moreInfoHint = GetByLabel('UI/Corporations/BaseCorporationUI/ISKTaxRateDescription', min_isk_amount=min_isk_amount_text)
            elif configName == 'loyaltyPointTaxRate':
                val = GetByLabel('UI/Common/Percentage', percentage=val * 100)
                decoClass = LabelTextSidesMoreInfo
                moreInfoHint = GetByLabel('UI/Corporations/BaseCorporationUI/LPTaxRateDescription')
            elif isinstance(val, int):
                val = localization.formatters.FormatNumeric(val, useGrouping=True, decimalPlaces=0)
            elif configName == 'friendlyFire':
                statusText = sm.GetService('corp').GetCorpFriendlyFireStatus(wnd.corpinfo.aggressionSettings)
                val = statusText
                decoClass = LabelTextSidesMoreInfo
                moreInfoHint = GetByLabel('UI/Corporations/FriendlyFire/Description')
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(decoClass, {'line': 1,
             'label': label,
             'text': val,
             'moreInfoHint': moreInfoHint}))

        if not idCheckers.IsNPC(itemID):
            allowedFactionIDs = sm.GetService('fwEnlistmentSvc').GetCorpAllowedEnlistmentFactions(itemID)
            factionNames = sorted([ cfg.eveowners.Get(factionID).name for factionID in allowedFactionIDs ])
            rightTextLabels = [ (x, None) for x in factionNames ] or [(GetByLabel('UI/Corporations/CorpUIHome/NoFwFactionsPermitted'), None)]
            label = GetByLabel('UI/Corporations/CorpUIHome/PermittedFwFactions')
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelMultilineTextTop, {'label': label,
             'rightTextLabels': rightTextLabels}))
            allowWar = getattr(wnd.corpinfo, 'allowWar', None)
            label = GetByLabel('UI/WarPermit/WarPermitStatus')
            text = GetByLabel(GetLabelPathForAllowWar(allowWar))
            moreInfoHint = GetByLabel('UI/WarPermit/WarPermitExplanation')
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesMoreInfo, {'line': 1,
             'label': label,
             'text': text,
             'moreInfoHint': moreInfoHint}))
        if wnd.corpinfo.url:
            linkTag = '<url=%s>' % wnd.corpinfo.url
            url = GetByLabel('UI/Corporations/CorpUIHome/URLPlaceholder', linkTag=linkTag, url=wnd.corpinfo.url)
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/Corporations/CorpUIHome/URL'),
             'text': url}))
        if npcCorpInfo is not None and idCheckers.IsNPC(itemID):
            sizeDict = {'T': GetByLabel('UI/Corporations/TinyCorp'),
             'S': GetByLabel('UI/Corporations/SmallCorp'),
             'M': GetByLabel('UI/Corporations/MediumCorp'),
             'L': GetByLabel('UI/Corporations/LargeCorp'),
             'H': GetByLabel('UI/Corporations/HugeCorp')}
            txt = sizeDict[npcCorpInfo.size]
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/Corporations/CorpSize'),
             'text': txt}))
            extentDict = {'N': GetByLabel('UI/Corporations/NationalCrop'),
             'G': GetByLabel('UI/Corporations/GlobalCorp'),
             'R': GetByLabel('UI/Corporations/RegionalCorp'),
             'L': GetByLabel('UI/Corporations/LocalCorp'),
             'C': GetByLabel('UI/Corporations/ConstellationCorp')}
            txt = extentDict[npcCorpInfo.extent]
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/Corporations/CorpExtent'),
             'text': txt}))
        if itemID == session.corpid:
            for charinfo in sm.GetService('corp').GetMembersAsEveOwners():
                if not idCheckers.IsNPC(charinfo.ownerID):
                    entry = GetFromClass(User, {'info': charinfo,
                     'charID': charinfo.ownerID})
                    wnd.data[TAB_CORPMEMBERS]['items'].append(entry)

            wnd.data[TAB_CORPMEMBERS]['headers'].append(GetByLabel('UI/Common/NameCharacter'))
        solarSystemDict = {}
        corpName = cfg.eveowners.Get(itemID).name
        mapHintCallback = lambda : GetByLabel('UI/InfoWindow/SystemSettledByCorp', corpName=corpName)
        for solarSys in systems:
            solarSystemDict[solarSys.solarSystemID] = (2.0,
             1.0,
             (mapHintCallback, ()),
             None)

        pathfinder = sm.GetService('clientPathfinderService')
        stationIDs = set()
        stationIDsBySolarSystemID = {}
        solarSystems = []
        for solarSys in systems:
            solarSystemID = solarSys.solarSystemID
            parentConstellation = self.map.GetParent(solarSystemID)
            if not parentConstellation:
                continue
            parentRegion = self.map.GetParent(parentConstellation)
            name_with_path = ' / '.join([ self.map.GetItem(each).itemName for each in (solarSys.solarSystemID, parentConstellation, parentRegion) ])
            autopilotNumJumps = pathfinder.GetAutopilotJumpCount(session.solarsystemid2, solarSystemID)
            if IsUnreachableJumpCount(autopilotNumJumps):
                solarSystemText = GetByLabel('UI/InfoWindow/LocationNoRoute', locationName=name_with_path)
            else:
                solarSystemText = GetByLabel('UI/InfoWindow/LocationAndRoute', locationName=name_with_path, numJump=autopilotNumJumps)
            sortKey = (autopilotNumJumps, solarSystemText)
            solarSystemText = self.GetColorCodedSecurityStringForSystem(solarSystemID, solarSystemText)
            systemInfo = (solarSystemID, solarSystemText)
            solarSystems.append((sortKey, systemInfo))
            solarsystemItems = cfg.GetLocationsLocalBySystem(solarSystemID, False)
            stationsInSystem = [ each for each in solarsystemItems if evetypes.GetGroupID(each.typeID) == const.groupStation ]
            for eachStation in stationsInSystem:
                stationIDs.add(eachStation.itemID)

            stationIDsBySolarSystemID[solarSystemID] = stationsInSystem

        solarSystems = SortListOfTuples(solarSystems)
        if len(stationIDs):
            cfg.evelocations.Prime(stationIDs)
            cfg.stations.Prime(stationIDs)
        for eachSolarSystemID, solarSystemText in solarSystems:

            def GetSolarSystemMenu(solarSystemEntry):
                n = solarSystemEntry.sr.node
                return sm.GetService('menu').GetMenuFromItemIDTypeID(n.solarSystemID, const.typeSolarSystem)

            data = {'label': solarSystemText,
             'solarSystemID': eachSolarSystemID,
             'tabs': [30],
             'OnGetMenu': lambda args: GetSolarSystemMenu(args),
             'labelState': uiconst.UI_DISABLED}
            entry = GetFromClass(SystemNameHeader, data)
            wnd.data[TAB_STATIONS]['items'].append(entry)
            stationsInSystem = stationIDsBySolarSystemID.get(eachSolarSystemID, [])
            stationsInSystem = filter(lambda x: getattr(cfg.stations.GetIfExists(x.itemID), 'ownerID', None) == itemID, stationsInSystem)
            stationEntryList = self.GetStationEntryList(stationsInSystem, 1)
            wnd.data[TAB_STATIONS]['items'] += stationEntryList

        def ShowMap(*args):
            OpenMap(hightlightedSolarSystems=solarSystemDict, starColorMode=(STARMODE_SETTLED_SYSTEMS_BY_CORP, itemID))

        wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/Commands/ShowLocationOnMap'),
          ShowMap,
          (),
          66)]
        if not idCheckers.IsNPC(itemID) and not wnd.corpinfo.deleted:
            if sm.GetService('corp').GetActiveApplication(itemID) is not None:
                buttonLabel = GetByLabel('UI/Corporations/CorpApplications/ViewApplication')
            else:
                buttonLabel = GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ApplyToJoin')
            wnd.data[DATA_BUTTONS] += [(buttonLabel, sm.GetService('corp').ApplyForMembership, (itemID,))]

        def SortStuff(a, b):
            for i in range(3):
                x, y = a[i], b[i]
                if x < y:
                    return -1
                if x > y:
                    return 1

            return 0

        if corpmktinfo is not None:
            sellStuff = []
            buyStuff = []
            for each in corpmktinfo:
                if evetypes.Exists(each.typeID):
                    typeName = evetypes.GetName(each.typeID)
                    groupName = evetypes.GetGroupName(each.typeID)
                    categoryName = evetypes.GetCategoryName(each.typeID)
                    if each.sellPrice is not None:
                        sellStuff.append((typeName,
                         groupName,
                         categoryName,
                         each.typeID,
                         each.sellPrice,
                         each.sellQuantity,
                         each.sellDate,
                         each.sellStationID))
                    if each.buyPrice is not None:
                        buyStuff.append((typeName,
                         groupName,
                         categoryName,
                         each.typeID,
                         each.buyPrice,
                         each.buyQuantity,
                         each.buyDate,
                         each.buyStationID))

            sellStuff.sort(SortStuff)
            buyStuff.sort(SortStuff)
            for stuff, label in ((sellStuff, GetByLabel('UI/InfoWindow/Supply')), (buyStuff, GetByLabel('UI/InfoWindow/Demand'))):
                if stuff:
                    wnd.data[TAB_MARKETACTIVITY]['items'].append(GetFromClass(Header, {'label': label}))
                    for each in stuff:
                        typeName, groupName, categoryName, typeID, price, quantity, lastActivity, station = each
                        if lastActivity:
                            txt = GetByLabel('UI/InfoWindow/CategoryGroupTypeForPrice', categoryName=categoryName, groupName=groupName, typeName=typeName, price=price)
                        else:
                            txt = GetByLabel('UI/InfoWindow/CategoryGroupTypeForPriceAndLastTransaction', categoryName=categoryName, groupName=groupName, typeName=typeName, price=price, date=FmtDate(lastActivity, 'ls'), amount=quantity, location=station)
                        wnd.data[TAB_MARKETACTIVITY]['items'].append(GetFromClass(Text, {'line': 1,
                         'typeID': typeID,
                         'text': txt}))

        if idCheckers.IsNPC(itemID):
            wnd.dynamicTabs.append(TAB_AGENTS)
        wnd.dynamicTabs.append(TAB_STANDINGS)

    def UpdateDataAlliance(self, wnd):
        if not idCheckers.IsNPC(wnd.itemID):
            self.UpdateContactButtons(wnd, wnd.itemID)
            wnd.dynamicTabs.append(TAB_WARHISTORY)
        rec = wnd.allianceinfo
        executor = cfg.eveowners.Get(rec.executorCorpID)
        data = {'line': 1,
         'label': GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/Executor'),
         'text': executor.ownerName,
         'typeID': const.typeCorporation,
         'itemID': rec.executorCorpID}
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data))
        data = {'line': 1,
         'label': GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/ShortName'),
         'text': rec.shortName}
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data))
        data = {'line': 1,
         'label': GetByLabel('UI/InfoWindow/CreatedByCorp'),
         'text': cfg.eveowners.Get(rec.creatorCorpID).ownerName,
         'typeID': const.typeCorporation,
         'itemID': rec.creatorCorpID}
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data))
        data = {'line': 1,
         'label': GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreatedBy'),
         'text': cfg.eveowners.Get(rec.creatorCharID).ownerName,
         'typeID': const.typeCharacter,
         'itemID': rec.creatorCharID}
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data))
        data = {'line': 1,
         'label': GetByLabel('UI/InfoWindow/StartDate'),
         'text': FmtDate(rec.startDate, 'ls'),
         'typeID': None,
         'itemID': None}
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data))
        primeTimeInfo = KeyVal(currentPrimeHour=rec.currentPrimeHour, newPrimeHour=rec.newPrimeHour, newPrimeHourValidAfter=rec.newPrimeHourValidAfter)
        params = {'line': 1,
         'label': GetByLabel('UI/Sovereignty/DefaultVulnerabilityTime'),
         'text': '',
         'primeTimeInfo': primeTimeInfo}
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(PrimeTimeHourEntryHorizontal, params))
        allowWar = getattr(rec, 'allowWar', None)
        label = GetByLabel('UI/WarPermit/WarPermitStatus')
        text = GetByLabel(GetLabelPathForAllowWar(allowWar))
        moreInfoHint = GetByLabel('UI/WarPermit/WarPermitExplanation')
        data = {'line': 1,
         'label': label,
         'text': text,
         'moreInfoHint': moreInfoHint}
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesMoreInfo, data))
        if rec.currentCapital:
            allianceCapital = cfg.evelocations.Get(rec.currentCapital, None)
            if allianceCapital:
                capitalLink = GetShowInfoLink(const.typeSolarSystem, allianceCapital.name, rec.currentCapital)
                data = {'line': 1,
                 'label': GetByLabel('UI/Sovereignty/CurrentCapital'),
                 'text': capitalLink}
                wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data))
        if rec.url:
            linkTag = '<url=%s>' % rec.url
            url = GetByLabel('UI/Corporations/CorpUIHome/URLPlaceholder', linkTag=linkTag, url=rec.url)
            data = {'line': 1,
             'label': GetByLabel('UI/Common/URL'),
             'text': url}
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data))
        wnd.dynamicTabs.append(TAB_MEMBERS)
        wnd.dynamicTabs.append(TAB_STANDINGS)

    def UpdateDataStargate(self, wnd, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            slimItem = bp.GetInvItem(itemID)
            if slimItem is not None:
                locs = []
                for each in slimItem.jumps:
                    if each.locationID not in locs:
                        locs.append(each.locationID)
                    if each.toCelestialID not in locs:
                        locs.append(each.toCelestialID)

                if len(locs):
                    cfg.evelocations.Prime(locs)
                for each in slimItem.jumps:
                    destLabel = GetByLabel('UI/InfoWindow/DestinationInSolarsystem', destination=each.toCelestialID, solarsystem=each.locationID)
                    wnd.data[TAB_JUMPS]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                     'label': GetByLabel('UI/Common/Jump'),
                     'text': destLabel,
                     'typeID': const.groupSolarSystem,
                     'itemID': each.locationID}))

                wnd.dynamicTabs.append(TAB_GATE_ICONS)

    def GetCelestialStatisticsForCelestial(self, celestialID, celestialGroupID):
        statistics = OrderedDict()
        celestial = cfg.mapSolarSystemContentCache.celestials[celestialID]
        if not hasattr(celestial, 'statistics'):
            return statistics
        celestialStatistics = celestial.statistics
        attributeNames = CELESTIAL_STATISTICS_ATTRIBUTES_BY_GROUPID[celestialGroupID]
        attributeNames.sort()
        for attributeName in attributeNames:
            statistics[attributeName] = getattr(celestialStatistics, attributeName)

        return statistics

    def GetCelestialStatisticsForSun(self, sun):
        statistics = OrderedDict()
        if not hasattr(sun, 'statistics'):
            return statistics
        sunStatistics = sun.statistics
        attributeNames = SUN_STATISTICS_ATTRIBUTES
        sovereigntyResourceSvc = sm.GetService('sovereigntyResourceSvc')
        starPowerMax = None
        starPower = sovereigntyResourceSvc.planetProductionStaticData.get_power_production_for_star(sun.id)
        if starPower:
            starPowerMax = max(starPower, 0)
        for attributeName in attributeNames:
            if attributeName == 'power':
                if starPowerMax is not None:
                    statistics[attributeName] = starPowerMax
            else:
                statistics[attributeName] = getattr(sunStatistics, attributeName)

        return statistics

    def GetSovStatisticsForPlanet(self, planetID):
        sovereigntyResourceSvc = sm.GetService('sovereigntyResourceSvc')
        try:
            reagentTypeID, reagentAmountsInfo, power, workforce = sovereigntyResourceSvc.GetPlanetResourceInfoParallel(planetID)
        except DataUnavailableError:
            return {}

        ret = {}
        if reagentTypeID:
            ret['reagentType'] = reagentTypeID
        if reagentAmountsInfo and reagentAmountsInfo[0]:
            amount, periodInSec = reagentAmountsInfo
            amountPerMinute = round(float(amount) / (float(periodInSec) / 60), 1)
            ret['reagentAmountPerMinute'] = amountPerMinute
        if power:
            ret['power'] = power
        if workforce:
            ret['workforce'] = workforce
        return ret

    def UpdateDataCelestial(self, wnd, typeID, itemID, parentID):
        if not itemID:
            self.LogWarn('Failed to update info data for celestial item: itemID is %s' % itemID)
            return
        _, regionID, constellationID, solarsystemID, _itemID = self.map.GetParentLocationID(itemID)
        if idCheckers.IsCelestial(itemID):
            if wnd.groupID == const.groupSun:
                statistics = self.GetCelestialStatisticsForSun(cfg.mapSolarSystemContentCache[solarsystemID].star)
            else:
                statistics = self.GetCelestialStatisticsForCelestial(itemID, wnd.groupID)
                if wnd.groupID == const.groupPlanet:
                    sovStats = self.GetSovStatisticsForPlanet(itemID)
                    statistics.update(sovStats)
            for attributeName, attributeValue in statistics.iteritems():
                label, value, tID = FmtPlanetAttributeKeyVal(attributeName, attributeValue)
                data = {'line': 1,
                 'label': label,
                 'text': value}
                if tID:
                    data['typeID'] = tID
                wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, data=data))

        if solarsystemID is not None:
            itemID = self.GetOrbitalBodies(wnd, itemID, solarsystemID, typeID)
            if typeID == const.typeSolarSystem:
                self.GetStationTab(wnd, itemID)
                if sm.GetService('sov').IsSystemConquarable(solarsystemID):
                    wnd.dynamicTabs.append(TAB_SOV)
                if sm.GetService('fwWarzoneSvc').IsWarzoneSolarSystem(solarsystemID):
                    wnd.dynamicTabs.append(TAB_FW)
                if is_directional_scanner_suppressed(itemID):
                    entry = GetFromClass(Generic, {'line': 1,
                     'label': GetByLabel('UI/InfoWindow/DscanDisabled')})
                    wnd.data[TAB_ATTIBUTES]['items'].append(entry)
        typeGroupID = evetypes.GetGroupID(typeID)
        neighborGrouping = {const.groupConstellation: GetByLabel('UI/InfoWindow/AdjacentConstellations'),
         const.groupRegion: GetByLabel('UI/InfoWindow/AdjacentRegions'),
         const.groupSolarSystem: GetByLabel('UI/InfoWindow/AdjacentSolarSystem')}
        childGrouping = {const.groupRegion: GetByLabel('UI/InfoWindow/RelatedConstellation'),
         const.groupConstellation: GetByLabel('UI/InfoWindow/RelatedSolarSystem')}
        if typeGroupID == const.groupConstellation:
            children = self.map.GetLocationChildren(itemID)
            childrenEntriesToSort = []
            for childID in children:
                childItem = self.map.GetItem(childID)
                if childItem is not None:
                    text = self.GetColorCodedSecurityStringForSystem(childItem.itemID, childItem.itemName)
                    childTypeName = evetypes.GetName(childItem.typeID)
                    genericDisplayLabel = '%s - %s' % (childTypeName, childItem.itemName)
                    entry = GetFromClass(LabelLocationTextTop, {'line': 1,
                     'label': childTypeName,
                     'text': text,
                     'typeID': childItem.typeID,
                     'itemID': childItem.itemID,
                     'tabs': [35],
                     'tabMargin': -2,
                     'genericDisplayLabel': genericDisplayLabel})
                    childrenEntriesToSort.append((childItem.itemName, entry))

            if childrenEntriesToSort:
                childrenEntries = SortListOfTuples(childrenEntriesToSort)
                wnd.data[TAB_CHILDREN]['items'] += childrenEntries
            wnd.data[TAB_CHILDREN]['name'] = childGrouping.get(const.groupConstellation, GetByLabel('UI/InfoWindow/UnknownTabName'))
            sovSvc = sm.GetService('sov')
            if any([ sovSvc.IsSystemConquarable(solarSystemID) for solarSystemID in children ]):
                wnd.dynamicTabs.append(TAB_SOV_CONSTELLATION)
        elif typeGroupID == const.groupRegion:
            children = self.map.GetLocationChildren(itemID)
            childrenEntriesToSort = []
            for childID in children:
                childItem = self.map.GetItem(childID)
                if childItem is not None:
                    childTypeName = evetypes.GetName(childItem.typeID)
                    genericDisplayLabel = '%s - %s' % (childTypeName, childItem.itemName)
                    entry = GetFromClass(LabelLocationTextTop, {'line': 1,
                     'label': childTypeName,
                     'text': childItem.itemName,
                     'typeID': childItem.typeID,
                     'itemID': childItem.itemID,
                     'genericDisplayLabel': genericDisplayLabel})
                    childrenEntriesToSort.append((childItem.itemName, entry))

            if childrenEntriesToSort:
                childrenEntries = SortListOfTuples(childrenEntriesToSort)
                wnd.data[TAB_CHILDREN]['items'] += childrenEntries
            wnd.data[TAB_CHILDREN]['name'] = childGrouping.get(const.groupRegion, GetByLabel('UI/InfoWindow/UnknownTabName'))
        if typeGroupID in [const.groupConstellation, const.groupRegion, const.groupSolarSystem]:
            neigbors = self.map.GetNeighbors(itemID)
            childrenEntriesToSort = []
            for childID in neigbors:
                childItem = self.map.GetItem(childID)
                if childItem is not None:
                    if childItem.typeID == const.groupSolarSystem:
                        text = self.GetColorCodedSecurityStringForSystem(childID, childItem.itemName)
                    else:
                        text = childItem.itemName
                    childTypeName = evetypes.GetName(childItem.typeID)
                    genericDisplayLabel = '%s - %s' % (childTypeName, childItem.itemName)
                    entry = GetFromClass(LabelLocationTextTop, {'line': 1,
                     'label': childTypeName,
                     'text': text,
                     'typeID': childItem.typeID,
                     'itemID': childItem.itemID,
                     'tabs': [35],
                     'tabMargin': -2,
                     'genericDisplayLabel': genericDisplayLabel})
                    childrenEntriesToSort.append((childItem.itemName, entry))

            if childrenEntriesToSort:
                childrenEntries = SortListOfTuples(childrenEntriesToSort)
                wnd.data[TAB_NEIGHBORS]['items'] += childrenEntries
            wnd.data[TAB_NEIGHBORS]['name'] = neighborGrouping.get(typeGroupID, GetByLabel('UI/InfoWindow/UnknownTabName'))
        if evetypes.GetGroupID(typeID) in [const.groupConstellation, const.groupSolarSystem]:
            shortestRoute = sm.GetService('starmap').ShortestGeneralPath(itemID)
            shortestRoute = shortestRoute[1:]
            wasRegion = None
            wasConstellation = None
            if len(shortestRoute) > 0:
                wnd.data[TAB_ROUTE]['items'].append(GetFromClass(Header, {'label': GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=len(shortestRoute))}))
            for i in range(len(shortestRoute)):
                childID = shortestRoute[i]
                childItem = self.map.GetItem(childID)
                parentConstellation = self.map.GetParent(childID)
                parentRegion = self.map.GetParent(parentConstellation)
                nameWithPath = GetByLabel('UI/InfoWindow/SolarsystemLocation', region=parentRegion, constellation=parentConstellation, solarsystem=childID)
                nameWithPath = self.GetColorCodedSecurityStringForSystem(childID, nameWithPath)
                jumpDescription = GetByLabel('UI/InfoWindow/RegularJump', numJumps=i + 1)
                if i > 0:
                    if wasRegion != parentRegion:
                        jumpDescription = GetByLabel('UI/InfoWindow/RegionJump', numJumps=i + 1)
                    elif wasConstellation != parentConstellation:
                        jumpDescription = GetByLabel('UI/InfoWindow/ConstellationJump', numJumps=i + 1)
                wasRegion = parentRegion
                wasConstellation = parentConstellation
                if childItem is not None:
                    genericDisplayLabel = cfg.evelocations.Get(childID).name
                    wnd.data[TAB_ROUTE]['items'].append(GetFromClass(LabelLocationTextTop, {'line': 1,
                     'label': jumpDescription,
                     'text': nameWithPath,
                     'typeID': childItem.typeID,
                     'itemID': childItem.itemID,
                     'tabs': [35],
                     'tabMargin': -2,
                     'genericDisplayLabel': genericDisplayLabel}))

        groupID = evetypes.GetGroupID(typeID)

        def ShowMap(idx, *args):
            OpenMap(interestID=itemID)

        if groupID in [const.groupSolarSystem, const.groupConstellation, const.groupRegion]:
            if groupID == const.groupSolarSystem:
                systemID = itemID
                constellationID = self.map.GetParent(itemID)
                regionID = self.map.GetParent(constellationID)
            elif groupID == const.groupConstellation:
                constellationID = itemID
                regionID = self.map.GetParent(constellationID)
            elif groupID == const.groupRegion:
                regionID = itemID
            wnd.data[DATA_BUTTONS] = [(GetByLabel('UI/Inflight/BookmarkLocation'),
              self.Bookmark,
              (itemID, typeID, parentID),
              81)]
            if idCheckers.IsKnownSpaceSystem(itemID) or idCheckers.IsKnownSpaceConstellation(itemID) or idCheckers.IsKnownSpaceRegion(itemID):
                wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/Commands/ShowLocationOnMap'),
                  ShowMap,
                  [const.groupSolarSystem, const.groupConstellation, const.groupRegion].index(groupID),
                  81)]
        itemTraderComponent = GetItemTraderComponent(typeID)
        if itemTraderComponent:
            recipes = {Recipe(recipeID) for recipeID in itemTraderComponent.recipes}
            recipesByGroup = GetSortedRecipeGroupsAndData(recipes)
            for groupName, recipeDataList in recipesByGroup:
                entry = GetFromClass(Generic, {'line': 1,
                 'label': groupName})
                wnd.data[TAB_TRADES]['items'].append(entry)
                for recipeData in recipeDataList:
                    entry = GetFromClass(RecipeEntry, recipeData)
                    wnd.data[TAB_TRADES]['items'].append(entry)

    def GetOrbitalBodies(self, wnd, itemID, solarsystemID, typeID):
        solarsystem = self.map.GetSolarsystemItems(solarsystemID, False)
        sun = None
        if evetypes.GetGroupID(typeID) == const.groupSolarSystem:
            for each in solarsystem:
                if evetypes.GetGroupID(each.typeID) == const.groupSun:
                    sun = each.itemID

            if sun:
                itemID = sun
        if solarsystemID == itemID and sun:
            rootID = [ each for each in solarsystem if evetypes.GetGroupID(each.typeID) == const.groupSun ][0].itemID
        else:
            rootID = itemID
        groupSort = {const.groupStargate: -1,
         const.groupAsteroidBelt: 1,
         const.groupMoon: 2,
         const.groupPlanet: 3}

        def DrawOrbitItems(rootID, indent):
            tmp = [ each for each in solarsystem if each.orbitID == rootID and evetypes.GetCategoryID(each.typeID) != const.categoryStructure ]
            tmp.sort(lambda a, b: cmp(*[ groupSort.get(evetypes.GetGroupID(each.typeID), 0) for each in (a, b) ]) or cmp(a.celestialIndex, b.celestialIndex) or cmp(a.orbitIndex, b.orbitIndex))
            for each in tmp:
                name = cfg.evelocations.Get(each.itemID).name
                planet = False
                if idCheckers.IsStation(each.itemID):
                    continue
                elif each.groupID == const.groupMoon:
                    name = '<color=0xff888888>' + name + '</color>'
                elif each.groupID == const.groupAsteroidBelt:
                    name = '<color=0xffdddddd>' + name + '</color>'
                elif each.groupID == const.groupPlanet:
                    planet = True
                if planet:
                    planetTypeName = evetypes.GetName(each.typeID)
                    genericDisplayLabel = '%s - %s' % (planetTypeName, name)
                    data = {'line': 1,
                     'text': indent * '    ' + name + ' %s' % planetTypeName,
                     'typeID': each.typeID,
                     'itemID': each.itemID,
                     'locationID': solarsystemID,
                     'genericDisplayLabel': genericDisplayLabel,
                     'isDragObject': True}
                    entry = GetFromClass(LocationTextEntry, data)
                    wnd.data[TAB_ORBITALBODIES]['items'].append(entry)
                else:
                    data = {'line': 1,
                     'text': indent * '    ' + name,
                     'genericDisplayLabel': StripTags(name),
                     'typeID': each.typeID,
                     'itemID': each.itemID,
                     'isDragObject': True}
                    entry = GetFromClass(LocationTextEntry, data)
                    wnd.data[TAB_ORBITALBODIES]['items'].append(entry)
                DrawOrbitItems(each.itemID, indent + 1)

        if sun:
            DrawOrbitItems(rootID, 0)
        if evetypes.GetGroupID(typeID) == const.groupSolarSystem:
            structuresInSolarsystem = [ x for x in solarsystem if evetypes.GetCategoryID(x.typeID) == const.categoryStructure ]
            structureEntryList = []
            for eachStructure in structuresInSolarsystem:
                name = cfg.evelocations.Get(eachStructure.itemID).name
                data = {'line': 1,
                 'text': name,
                 'genericDisplayLabel': StripTags(name),
                 'typeID': eachStructure.typeID,
                 'itemID': eachStructure.itemID,
                 'isDragObject': True}
                entry = GetFromClass(LocationTextEntry, data)
                structureEntryList.append((name.lower(), entry))

            sortedStructureEntryList = SortListOfTuples(structureEntryList)
            wnd.data[TAB_STRUCTURES]['items'].extend(sortedStructureEntryList)
        itemID = solarsystemID
        return itemID

    def GetStationTab(self, wnd, solarsystemID):
        solarsystem = self.map.GetSolarsystemItems(solarsystemID, False)
        allStations = [ each for each in solarsystem if evetypes.GetGroupID(each.typeID) == const.groupStation ]
        if not allStations:
            return
        stationEntryList = self.GetStationEntryList(allStations)
        wnd.data[TAB_STATIONS]['items'] += stationEntryList

    def GetStationEntryList(self, stationList, sublevel = 0):
        entryList = []
        stationList.sort(lambda a, b: cmp(a.celestialIndex, b.celestialIndex) or cmp(a.orbitIndex, b.orbitIndex))
        stationIDs = []
        for each in stationList:
            stationIDs.append(each.itemID)

        if len(stationIDs):
            cfg.evelocations.Prime(stationIDs)
        for each in stationList:
            name = cfg.evelocations.Get(each.itemID).name
            entry = GetFromClass(LocationGroup, {'GetSubContent': self.GetStationSubContent,
             'label': name,
             'MenuFunction': self.GetMenuLocationMenu,
             'id': ('infownd_stations', each.itemID),
             'groupItems': [],
             'iconMargin': 18,
             'allowCopy': 1,
             'showicon': 'hide',
             'showlen': 0,
             'itemID': each.itemID,
             'typeID': each.typeID,
             'state': 'locked',
             'sublevel': sublevel})
            entryList.append(entry)

        return entryList

    def GetStationSubContent(self, nodedata, *args):
        itemID = nodedata.itemID
        stationInfo = self.map.GetStation(itemID)
        serviceEntryList = self.GetServicesForStation(stationInfo, itemID, iconoffset=20)
        return serviceEntryList

    def GetMenuLocationMenu(self, node):
        stationInfo = sm.GetService('ui').GetStationStaticInfo(node.itemID)
        return StartMenuService().CelestialMenu(node.itemID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID)

    def UpdateDataControlTower(self, wnd, typeID, itemID):
        self.UpdateDataModule(wnd, typeID, itemID)
        wnd.dynamicTabs.append(TAB_FUELREQ)

    def UpdateDataAsteroidOrCloud(self, wnd, typeID, itemID):
        formatedValue = localization.formatters.FormatNumeric(evetypes.GetVolume(typeID), useGrouping=True, decimalPlaces=3)
        value = GetByLabel('UI/InfoWindow/ValueAndUnit', value=formatedValue, unit=FormatUnit(const.unitVolume))
        fields = [(GetByLabel('UI/Common/Volume'), value)]
        if typeID not in const.RESOURCE_WARS_ORE_TYPES and is_reprocessable_type(typeID):
            reprocessingField = (GetByLabel('UI/InfoWindow/UnitsToRefine'), localization.formatters.FormatNumeric(int(evetypes.GetPortionSize(typeID)), useGrouping=True))
            fields.append(reprocessingField)
        try:
            fields.append((GetByLabel('UI/Generic/FormatPlanetAttributes/attributeRadius'), FormatValue(sm.GetService('michelle').GetBallpark().GetBall(itemID).radius, const.unitLength)))
        except:
            sys.exc_clear()

        for header, text in fields:
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': header,
             'text': text}))

    def UpdateDataFaction(self, wnd, typeID, itemID):
        races = get_faction_races(itemID) or [const.raceCaldari,
         const.raceMinmatar,
         const.raceAmarr,
         const.raceGallente]
        stations = get_station_count(itemID)
        systems = get_station_system_count(itemID)
        memberRaceList = []
        for raceID in races:
            memberRaceList.append(get_race_name(raceID))

        if len(memberRaceList) > 0:
            memberRaceText = localization.formatters.FormatGenericList(memberRaceList)
            wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
             'label': GetByLabel('UI/InfoWindow/MemberRaces'),
             'text': memberRaceText}))
        text = localization.formatters.FormatNumeric(systems, useGrouping=True)
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
         'label': GetByLabel('UI/InfoWindow/SettledSystems'),
         'text': text}))
        text = localization.formatters.FormatNumeric(stations, useGrouping=True)
        wnd.data[TAB_ATTIBUTES]['items'].append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
         'label': GetByLabel('UI/Common/Stations'),
         'text': text}))
        wnd.data[TAB_ATTIBUTES]['name'] = GetByLabel('UI/InfoWindow/TabNames/Statistics')

        def SortFunc(x, y):
            xname = cfg.eveowners.Get(x).name
            if xname.startswith('The '):
                xname = xname[4:]
            yname = cfg.eveowners.Get(y).name
            if yname.startswith('The '):
                yname = yname[4:]
            if xname < yname:
                return -1
            if xname > yname:
                return 1
            return 0

        corpsOfFaction = get_corporation_ids_by_faction_id(itemID, default=[])
        corpsOfFaction = copy.copy(corpsOfFaction)
        corpsOfFaction.sort(SortFunc)
        for corpID in corpsOfFaction:
            corp = cfg.eveowners.Get(corpID)
            entry = GetFromClass(User, {'info': corp,
             'charID': corp.ownerID})
            wnd.data[TAB_MEMBEROFCORPS]['items'].append(entry)

        newEntries = []
        regions, constellations, solarsystems = sm.GetService('faction').GetFactionLocations(itemID)
        if regions:
            wnd.data[TAB_SYSTEMS]['items'].append(GetFromClass(Header, {'label': GetByLabel('UI/Common/Regions')}))
        for regionID in regions:
            nameWithPath = self.map.GetItem(regionID).itemName
            entry = GetFromClass(LabelTextSides, {'line': 1,
             'label': nameWithPath,
             'text': '',
             'typeID': const.typeRegion,
             'itemID': regionID})
            newEntries.append((nameWithPath, entry))

        newEntries = SortListOfTuples(newEntries)
        wnd.data[TAB_SYSTEMS]['items'].extend(newEntries)
        newEntries = []
        if constellations:
            wnd.data[TAB_SYSTEMS]['items'].append(GetFromClass(Header, {'label': GetByLabel('UI/Common/Constellations')}))
        for constellationID in constellations:
            regionID = self.map.GetParent(constellationID)
            nameWithPath = GetByLabel('UI/InfoWindow/ConstellationLocation', region=regionID, constellation=constellationID)
            sortValue = [ cfg.evelocations.Get(x).name for x in [regionID, constellationID] ]
            entry = GetFromClass(LabelTextSides, {'line': 1,
             'label': nameWithPath,
             'text': '',
             'typeID': const.typeConstellation,
             'itemID': constellationID})
            newEntries.append((sortValue, entry))

        newEntries = SortListOfTuples(newEntries)
        wnd.data[TAB_SYSTEMS]['items'].extend(newEntries)
        newEntries = []
        if solarsystems:
            wnd.data[TAB_SYSTEMS]['items'].append(GetFromClass(Header, {'label': GetByLabel('UI/Common/SolarSystems')}))
        for solarsystemID in solarsystems:
            constellationID = self.map.GetParent(solarsystemID)
            regionID = self.map.GetParent(constellationID)
            nameWithPath = GetByLabel('UI/InfoWindow/SolarsystemLocation', region=regionID, constellation=constellationID, solarsystem=solarsystemID)
            sortValue = [ cfg.evelocations.Get(x).name for x in [regionID, constellationID, solarsystemID] ]
            entry = GetFromClass(LabelTextSides, {'line': 1,
             'label': nameWithPath,
             'text': '',
             'typeID': const.typeSolarSystem,
             'itemID': solarsystemID})
            newEntries.append((sortValue, entry))

        newEntries = SortListOfTuples(newEntries)
        wnd.data[TAB_SYSTEMS]['items'].extend(newEntries)
        wnd.data[TAB_SYSTEMS]['name'] = GetByLabel('UI/InfoWindow/ControlledTerritory')
        illegalities = get_contraband_types_in_faction(itemID)
        illegalitiesItems = illegalities.items()
        illegalitiesItems.sort(key=lambda x: evetypes.GetName(x[0]))
        for tmpTypeID, illegality in illegalitiesItems:
            txtList = self.__GetIllegalityStringList(illegality)
            wnd.data[TAB_LEGALITY]['items'].append(GetFromClass(Item, {'line': 1,
             'label': evetypes.GetName(tmpTypeID),
             'typeID': tmpTypeID,
             'getIcon': True}))
            for eachTxt in txtList:
                wnd.data[TAB_LEGALITY]['items'].append(GetFromClass(Generic, {'line': 1,
                 'label': eachTxt,
                 'sublevel': 2}))

        if illegalities:
            wnd.data[TAB_LEGALITY]['items'].insert(0, GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/IllegalTypes')}))
        wnd.dynamicTabs.append(TAB_STANDINGS)

    def UpdateDataAgent(self, wnd, typeID, itemID):
        agentID = itemID or sm.GetService('godma').GetType(typeID).agentID
        try:
            details = sm.GetService('agents').GetAgentMoniker(agentID).GetInfoServiceDetails()
            if details is not None:
                agentInfo = sm.GetService('agents').GetAgentByID(agentID)
                if agentInfo:
                    typeDict = {const.agentTypeGenericStorylineMissionAgent: GetByLabel('UI/InfoWindow/AgentTypeStorylineImportant'),
                     const.agentTypeStorylineMissionAgent: GetByLabel('UI/InfoWindow/AgentTypeStorylineImportant'),
                     const.agentTypeEventMissionAgent: GetByLabel('UI/InfoWindow/AgentTypeEvent'),
                     const.agentTypeCareerAgent: GetByLabel('UI/InfoWindow/AgentTypeCareer')}
                    t = typeDict.get(agentInfo.agentTypeID, None)
                    if t:
                        wnd.data[TAB_AGENTINFO]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                         'label': GetByLabel('UI/InfoWindow/AgentType'),
                         'text': t}))
                if agentInfo and agentInfo.agentTypeID not in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent):
                    wnd.data[TAB_AGENTINFO]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                     'label': GetByLabel('UI/InfoWindow/AgentDivision'),
                     'text': get_division_name(agentInfo.divisionID).replace('&', '&amp;')}))
                if details.stationID:
                    stationinfo = sm.GetService('ui').GetStationStaticInfo(details.stationID)
                    wnd.data[TAB_AGENTINFO]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                     'label': GetByLabel('UI/InfoWindow/AgentLocation'),
                     'text': cfg.evelocations.Get(details.stationID).name,
                     'typeID': stationinfo.stationTypeID,
                     'itemID': details.stationID}))
                else:
                    agentSolarSystemID = sm.GetService('agents').GetSolarSystemOfAgent(agentID)
                    if agentSolarSystemID is not None:
                        wnd.data[TAB_AGENTINFO]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                         'label': GetByLabel('UI/InfoWindow/AgentLocation'),
                         'text': cfg.evelocations.Get(agentSolarSystemID).name,
                         'typeID': const.typeSolarSystem,
                         'itemID': agentSolarSystemID}))
                if agentInfo and agentInfo.agentTypeID not in (const.agentTypeGenericStorylineMissionAgent, const.agentTypeStorylineMissionAgent):
                    level = localization.formatters.FormatNumeric(details.level, decimalPlaces=0)
                    wnd.data[TAB_AGENTINFO]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                     'label': GetByLabel('UI/InfoWindow/AgentLevel'),
                     'text': level}))
                for data in details.services:
                    serviceInfo = sm.GetService('agents').ProcessAgentInfoKeyVal(data)
                    for entry in serviceInfo:
                        wnd.data[TAB_AGENTINFO]['items'].append(GetFromClass(Header, {'label': entry[0]}))
                        for entryDetails in entry[1]:
                            wnd.data[TAB_AGENTINFO]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                             'label': entryDetails[0],
                             'text': entryDetails[1]}))

                if details.incompatible:
                    if type(details.incompatible) is tuple:
                        incText = GetByLabel(details.incompatible[0], **details.incompatible[1])
                    elif details.incompatible == 'Not really an agent':
                        incText = None
                    else:
                        incText = details.incompatible
                    if incText:
                        wnd.data[TAB_AGENTINFO]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                         'label': GetByLabel('UI/InfoWindow/AgentCompatibility'),
                         'text': incText}))
            wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/Chat/StartConversationAgent'),
              sm.StartService('agents').OpenDialogueWindow,
              (itemID,),
              66)]
        except (UserError, RuntimeError):
            pass

    def UpdateDataOrbital(self, wnd, itemID):
        self.UpdateDataModule(wnd, wnd.typeID, itemID)
        uthread.new(self.FetchDynamicOrbitalAttributes, wnd, wnd.data[TAB_ATTIBUTES], itemID)

    def FetchDynamicOrbitalAttributes(self, wnd, data, itemID):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return
        if ballpark.GetBall(itemID) is not None:
            taxRate = eveMoniker.GetPlanetOrbitalRegistry(session.solarsystemid).GetTaxRate(itemID)
            if taxRate is not None:
                text = GetByLabel('UI/Common/Percentage', percentage=taxRate * 100)
            else:
                text = GetByLabel('UI/PI/Common/CustomsOfficeAccessDenied')
            data['items'].append(GetFromClass(LabelTextSides, {'line': 1,
             'label': GetByLabel('UI/PI/Common/CustomsOfficeTaxRateLabel'),
             'text': text,
             'icon': 'ui_77_32_46'}))
            wnd.maintabs.ReloadVisible()
        else:
            log.LogInfo('Unable to fetch tax rate for customs office in a different system')

    def UpdateDataIllegal(self, wnd, typeID):
        illegalities = inventorycommon.typeHelpers.GetIllegality(typeID)
        if illegalities:
            wnd.data[TAB_LEGALITY]['items'].append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/LegalImplications')}))
        illegalitiesItems = illegalities.items()
        illegalitiesItems.sort(key=lambda x: cfg.eveowners.Get(x[0]).name)
        for tmpFactionID, illegality in illegalities.iteritems():
            txtList = self.__GetIllegalityStringList(illegality)
            wnd.data[TAB_LEGALITY]['items'].append(GetFromClass(User, {'line': 1,
             'charID': tmpFactionID,
             'typeID': const.typeFaction}))
            for eachTxt in txtList:
                wnd.data[TAB_LEGALITY]['items'].append(GetFromClass(Generic, {'line': 1,
                 'label': eachTxt,
                 'sublevel': 2}))

    def UpdateDataGenericItem(self, wnd, typeID, itemID):
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID, banAttrs=self.GetSkillAttrs())
        wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)

    def UpdateDataSecurityTag(self, wnd, typeID, itemID):
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID)
        wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        ShowSecurityOfficeMap = lambda : OpenMap(starColorMode=STARMODE_SERVICE_SecurityOffice)
        wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/Commands/ShowSecurityOffices'),
          ShowSecurityOfficeMap,
          (),
          66)]

    def UpdateDataSkill(self, wnd, typeID, itemID):
        self.UpdateDataGenericItem(wnd, typeID, itemID)
        if len(get_types_with_skill_type(typeID)) > 0:
            wnd.dynamicTabs.append(TAB_REQUIREDFOR)

    def UpdateDataStation(self, wnd, typeID, itemID):
        stationInfo = self.map.GetStation(itemID)
        if stationInfo:
            serviceEntryList = self.GetServicesForStation(stationInfo, itemID)
            wnd.data[TAB_SERVICES]['items'] += serviceEntryList
            stationLocationInfo = [stationInfo.regionID, stationInfo.constellationID, stationInfo.solarSystemID]
        elif itemID in cfg.oldStations:
            solarSystemID = cfg.oldStations.Get(itemID).solarSystemID
            solarSystemInfo = cfg.mapSystemCache.Get(solarSystemID)
            stationLocationInfo = [solarSystemID, solarSystemInfo.constellationID, solarSystemInfo.regionID]
        else:
            return
        for locID in stationLocationInfo:
            mapItem = self.map.GetItem(locID)
            if mapItem is not None:
                if mapItem.typeID == const.typeSolarSystem:
                    text = self.GetColorCodedSecurityStringForSystem(mapItem.itemID, mapItem.itemName)
                    text = text.replace('<t>', ' ')
                else:
                    text = mapItem.itemName
                wnd.data[TAB_LOCATION]['items'].append(GetFromClass(LabelTextTop, {'line': 1,
                 'label': evetypes.GetName(mapItem.typeID),
                 'text': text,
                 'typeID': mapItem.typeID,
                 'itemID': mapItem.itemID}))

        stationOwnerID = None
        if session.solarsystemid is not None:
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark:
                slimitem = ballpark.GetInvItem(itemID)
                if slimitem is not None:
                    stationOwnerID = slimitem.ownerID
        if stationOwnerID is None and stationInfo and stationInfo.ownerID:
            stationOwnerID = stationInfo.ownerID
        if stationOwnerID is not None:
            wnd.GetCorpLogo(stationOwnerID, parent=wnd.subinfolinkcontainer)
            wnd.subinfolinkcontainer.height = 64
        wnd.data[DATA_BUTTONS] = [(GetByLabel('UI/Inflight/SetDestination'),
          self.SetDestination,
          (itemID,),
          81)]

    def IsServiceAvailable(self, serviceID, stationInfo):
        stationOperationID = stationInfo.operationID
        serviceAlwaysPresent = serviceID == stationServiceConst.serviceIDAlwaysPresent
        if serviceAlwaysPresent or service_in_station_operation(stationOperationID, serviceID):
            return True
        repairServiceID = const.stationServiceRepairFacilities
        solarSystemID = session.solarsystemid2
        return serviceID == repairServiceID and IsStationServiceAvailable(solarSystemID, stationInfo, serviceID)

    def GetServicesForStation(self, stationInfo, itemID, iconoffset = 4):
        serviceEntryList = []
        sortServices = []
        for info in stationServiceConst.serviceData:
            if info.serviceID == structures.SERVICE_FACTION_WARFARE:
                factionID = get_corporation_faction_id(stationInfo.ownerID)
                if not factionID or factionID not in const.factionsEmpires:
                    continue
            elif info.serviceID == structures.SERVICE_SECURITY_OFFICE:
                if not sm.GetService('securityOfficeSvc').CanAccessServiceInStation(itemID):
                    continue
            for stationServiceID in info.stationServiceIDs:
                if self.IsServiceAvailable(stationServiceID, stationInfo):
                    if hasattr(info, 'iconID'):
                        icon = info.iconID
                    else:
                        icon = info.texturePath
                    sortServices.append((info.label, (info.label, icon, get_station_standings_restriction_info_many(info.stationServiceIDs, itemID))))
                    break

        if sortServices:
            sortServices = SortListOfTuples(sortServices)
            for displayName, iconpath, standingsRestriction in sortServices:
                serviceEntryList.append(GetFromClass(StationServiceEntry, {'line': 1,
                 'label': displayName,
                 'selectable': 0,
                 'iconoffset': iconoffset,
                 'icon': iconpath,
                 'standingsRestriction': standingsRestriction}))

        return serviceEntryList

    def UpdateDataRank(self, wnd):
        characterRanks = sm.StartService('facwar').GetCharacterRankOverview(session.charid)
        characterRanks = [ each for each in characterRanks if each.factionID == wnd.abstractinfo.warFactionID ]
        for x in range(9, -1, -1):
            hilite = False
            if characterRanks:
                if characterRanks[0].currentRank == x:
                    hilite = True
            rank = utillib.KeyVal(currentRank=x, factionID=wnd.abstractinfo.warFactionID)
            wnd.data[TAB_HIERARCHY]['items'].append(self.GetRankEntry(rank, hilite=hilite))

    def UpdateDataCertificate(self, wnd):
        wnd.dynamicTabs.append(TAB_CERTSKILLS)
        recommendedForScrollList = self.GetRecommendedFor(wnd.abstractinfo.certificateID)
        wnd.data[TAB_CERTRECOMMENDEDFOR]['items'] += recommendedForScrollList

    def UpdateDataPlanetPin(self, wnd, typeID, itemID):
        banAttrs = self.GetSkillAttrs()
        if evetypes.GetGroupID(typeID) == const.groupExtractorPins:
            banAttrs.extend([const.attributePinCycleTime, const.attributePinExtractionQuantity])
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID, banAttrs=banAttrs)
        wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        wnd.dynamicTabs.append(TAB_REQUIREMENTS)
        if evetypes.GetGroupID(typeID) == const.groupProcessPins:
            wnd.dynamicTabs.append(TAB_SCHEMATICS)

    def UpdateDataPlanet(self, wnd, typeID, itemID, parentID):
        if sm.GetService('machoNet').GetGlobalConfig().get('enableDustLink'):
            if session.solarsystemid is not None:
                slimitem = sm.GetService('michelle').GetBallpark().GetInvItem(itemID)
                if slimitem is not None and slimitem.corpID is not None:
                    wnd.dynamicTabs.append(TAB_PLANETCONTROL)
        wnd.dynamicTabs.append(TAB_PLANETARYPRODUCTIONPLANET)
        if itemID:
            wnd.data[DATA_BUTTONS] += [(GetByLabel('UI/PI/Common/ViewInPlanetMode'), sm.GetService('menu').ViewPlanetaryProduction, (itemID,))]
        self.UpdateDataCelestial(wnd, typeID, itemID, parentID)

    def UpdateDataDogma(self, wnd, typeID):
        container = wnd.data[TAB_DOGMA]['items']
        container.append(GetFromClass(Header, {'label': 'Type Attributes'}))
        typeattribs = dogma_data.get_type_attributes(typeID)
        tattribs = []
        for ta in typeattribs:
            v = ta.value
            a = dogma_data.get_attribute(ta.attributeID)
            if v is None:
                v = a.defaultValue
            tattribs.append([a.attributeID,
             a.name,
             v,
             a.dataType,
             a.description])

        tattribs.sort(lambda x, y: cmp(x[1], y[1]))
        for ta in tattribs:
            attributeName = ta[1]
            v = ta[2]
            dataType = ta[3]
            description = ta[4]
            if dataType == attributeDataTypeTypeHex:
                v = hex(int(v))
            entry = GetFromClass(LabelTextTop, {'line': 1,
             'label': attributeName,
             'text': '%s<br>%s' % (v, description)})
            container.append(entry)

        container.append(GetFromClass(Header, {'label': 'Effects'}))
        teffects = []
        for te in dogma_data.get_type_effects(typeID):
            e = dogma_data.get_effect(te.effectID)
            teffects.append([e, e.effectName])

        teffects.sort(lambda x, y: cmp(x[1], y[1]))
        for e, effectName in teffects:
            entry = GetFromClass(Subheader, {'label': effectName})
            container.append(entry)
            header = sorted([ k for k in dir(e) if '__' not in k ])
            for columnName in header:
                entry = GetFromClass(LabelTextTop, {'line': 1,
                 'label': columnName,
                 'text': '%s' % getattr(e, columnName)})
                container.append(entry)

    def UpdateDataEntity(self, wnd):
        bounty = get_entity_bounty(wnd.typeID, wnd.itemID)
        if bounty > 0:
            wnd.Wanted(bounty, False, True, isNPC=True)
        with ExceptionEater():
            damageEntryScrollList = self.GetEntityDamageScrollList(wnd.typeID)
            wnd.data[TAB_ATTIBUTES]['items'] += damageEntryScrollList
        entityAttributes = self.GetEntityAttributes()
        attributeEntries, _ = self.GetItemAttributeScrolllistAndAttributesList(None, wnd.typeID, entityAttributes)
        wnd.data[TAB_ATTIBUTES]['items'] += attributeEntries

    def UpdateDataMutator(self, wnd, typeID):
        attributes = wnd.data[TAB_ATTIBUTES]['items']
        attributes.extend(self.GetAttributeScrollListForType(typeID=typeID))
        mutator = dynamicitemattributes.GetMutator(typeID)
        mutations = []
        for attributeID, attribute in mutator.attributeIDs.iteritems():
            mutations.append(GetFromClass(LabelTextSidesAttributes, {'attributeID': attributeID,
             'line': 1,
             'label': dogma_data.get_attribute_display_name(attributeID),
             'text': FormatAttributeBonusRange(attributeID, attribute.min, attribute.max),
             'iconID': dogma_data.get_attribute_icon_id(attributeID)}))

        if mutations:
            attributes.append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/Mutations')}))
            attributes.extend(sorted(mutations, key=lambda e: e.label))
        wnd.dynamicTabs.append(TAB_MUTATOR_USED_WITH)

    def UpdateExpertSystem(self, wnd, typeID):
        wnd.dynamicTabs.append(TAB_EXPERT_SYSTEM_SKILLS)
        wnd.dynamicTabs.append(TAB_EXPERT_SYSTEM_SHIPS)
        if expertSystems.is_expert_systems_enabled():
            browseInStoreLabel = GetByLabel('UI/InfoWindow/ViewExpertSystemInStore')
            wnd.data[DATA_BUTTONS] = [(browseInStoreLabel,
              self.ViewExpertSystemInStore,
              typeID,
              81)]

    def UpdateMarketButtons(self, wnd):
        typeID = wnd.typeID
        if not typeID:
            return
        if can_view_market_details(typeID):
            showMarketDetailsLabel = GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails')
            wnd.data[DATA_BUTTONS] += [(showMarketDetailsLabel,
              self.ShowMarketDetails,
              typeID,
              81)]
        elif is_contractable(typeID) and evetypes.IsPublished(typeID):
            findInContractsLabel = GetByLabel('UI/Inventory/ItemActions/FindInContracts')
            wnd.data[DATA_BUTTONS] += [(findInContractsLabel,
              self.FindInContracts,
              typeID,
              81)]
        if industryCommon.IsBlueprintCategory(evetypes.GetCategoryID(wnd.typeID)):
            from eve.client.script.ui.shared.industry.industryWnd import Industry
            itemID = wnd.itemID
            bpData = wnd.GetBlueprintData()
            viewInIndustryLabel = GetByLabel('UI/Industry/ViewInIndustry')
            wnd.data[DATA_BUTTONS] += [(viewInIndustryLabel,
              Industry.OpenOrShowBlueprint,
              (itemID, typeID, bpData),
              81)]

    def UpdateWindowData(self, wnd, typeID, itemID, parentID = None):
        evetypes.RaiseIFNotExists(typeID)
        self.UpdateMarketButtons(wnd)
        self.UpdateComponentData(wnd, typeID, itemID)
        if wnd.IsType(TYPE_CHARACTER):
            self.UpdateDataCharacter(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_CORPORATION):
            self.UpdateDataCorp(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_ALLIANCE):
            self.UpdateDataAlliance(wnd)
        elif wnd.IsType(TYPE_FACTION):
            self.UpdateDataFaction(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_SHIP):
            self.UpdateDataShip(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_STRUCTURE):
            self.UpdateStructure(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_MODULE, TYPE_STRUCTURE_OLD, TYPE_STRUCTUREUPGRADE, TYPE_APPAREL, TYPE_STRUCTURE_MODULE):
            self.UpdateDataModule(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_DRONE):
            self.UpdateDataDrone(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_FIGHTER):
            self.UpdateDataFighter(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_CUSTOMSOFFICE):
            self.UpdateDataOrbital(wnd, itemID)
        elif wnd.IsType(TYPE_SECURECONTAINER):
            self.UpdateDataSecureContainer(wnd, itemID)
        elif wnd.IsType(TYPE_CHARGE):
            self.UpdateDataCharge(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_BLUEPRINT):
            wnd.dynamicTabs.append(TAB_INDUSTRY)
        elif wnd.IsType(TYPE_STARGATE):
            self.UpdateDataStargate(wnd, itemID)
        elif wnd.IsType(TYPE_CELESTIAL):
            self.UpdateDataCelestial(wnd, typeID, itemID, parentID)
        elif wnd.IsType(TYPE_ASTEROID):
            self.UpdateDataAsteroidOrCloud(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_CONTROLTOWER):
            self.UpdateDataControlTower(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_GENERICITEM):
            self.UpdateDataGenericItem(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_SKILL):
            self.UpdateDataSkill(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_SECURITYTAG):
            self.UpdateDataSecurityTag(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_STATION) and itemID is not None:
            self.UpdateDataStation(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_RANK) and wnd.abstractinfo is not None:
            self.UpdateDataRank(wnd)
        elif wnd.IsType(TYPE_CERTIFICATE) and wnd.abstractinfo is not None:
            self.UpdateDataCertificate(wnd)
        elif wnd.IsType(TYPE_PLANETPIN):
            self.UpdateDataPlanetPin(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_PLANETCOMMODITY):
            wnd.dynamicTabs.append(TAB_PLANETARYPRODUCTION)
        elif wnd.IsType(TYPE_PLANET):
            self.UpdateDataPlanet(wnd, typeID, itemID, parentID)
        elif wnd.IsType(TYPE_ENTITY):
            self.UpdateDataEntity(wnd)
        elif wnd.IsType(TYPE_DEPLOYABLE):
            self.UpdateDataDeployable(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_SKINLICENSE):
            wnd.dynamicTabs.append(TAB_SKINLICENSE)
        elif wnd.IsType(TYPE_SKINMATERIAL):
            wnd.dynamicTabs.append(TAB_SKINMATERIAL)
        elif wnd.IsType(TYPE_MUTATOR):
            self.UpdateDataMutator(wnd, typeID)
        elif wnd.IsType(TYPE_EXPERT_SYSTEM):
            self.UpdateExpertSystem(wnd, typeID)
        elif wnd.IsType(TYPE_SKYHOOK):
            self.UpdateSkyhook(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_SEQUENCE_BINDERS):
            self.UpdateSequenceBinder(wnd, typeID, itemID)
        elif wnd.IsType(TYPE_DESIGN_ELEMENTS):
            self.UpdateDesignElement(wnd, typeID, itemID)
        if self.HasVariations(typeID):
            wnd.dynamicTabs.append(TAB_VARIATIONS)
        if self.IsIndustryItem(typeID):
            wnd.dynamicTabs.append(TAB_ITEMINDUSTRY)
        if wnd.IsUpgradeable():
            wnd.dynamicTabs.append(TAB_UPGRADEMATERIALREQ)
        if not wnd.IsType(TYPE_FACTION):
            self.UpdateDataIllegal(wnd, typeID)
        if evetypes.GetGroupID(typeID) == const.groupAgentsinSpace and sm.GetService('godma').GetType(typeID).agentID:
            self.UpdateDataAgent(wnd, typeID, itemID)
        if typeID == const.typePlasticWrap:
            attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=itemID, typeID=typeID)
            wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        if evetypes.GetCategoryID(typeID) == const.categoryInfrastructureUpgrade:
            self.UpdateInfrastructureUpgrades(wnd, typeID, itemID)
        if self.IsAttributesTabShown(wnd) and not wnd.data[TAB_ATTIBUTES]['items']:
            self.UpdateAttributes(wnd)
        if prefs.GetValue('showdogmatab', 0) == 1:
            self.UpdateDataDogma(wnd, typeID)
        if wnd.IsType(TYPE_SHIP) or wnd.IsType(TYPE_DRONE):
            self.ApplyAttributeTooltip(wnd.data[TAB_ATTIBUTES]['items'])

    def IsIndustryItem(self, typeID):
        if evetypes.GetGroupID(typeID) == const.groupStation:
            return False
        if is_reprocessable_type(typeID):
            return True
        if typeID in cfg.blueprintsByMaterialTypeIDs:
            return True
        if is_compressible_type(typeID) or is_compressed_type(typeID):
            return True
        return False

    def HasVariations(self, typeID):
        if evetypes.GetGroupID(typeID) == const.groupCommandPins:
            return False
        variants = evetypes.GetVariations(typeID)
        return variants is not None and len(variants) > 0

    def UpdateAttributes(self, wnd):
        attributeScrollListForItem = self.GetAttributeScrollListForItem(itemID=wnd.itemID, typeID=wnd.typeID)
        wnd.data[TAB_ATTIBUTES]['items'] += attributeScrollListForItem
        try:
            effectTypeScrollList = self.GetEffectTypeInfo(wnd.typeID, dogma_data.get_all_effect_ids())
            wnd.data[TAB_ATTIBUTES]['items'] += effectTypeScrollList
        except Exception:
            sys.exc_clear()

    def IsAttributesTabShown(self, wnd):
        noShowCatergories = (const.categoryEntity,
         const.categoryStation,
         const.categoryAncientRelic,
         const.categoryBlueprint,
         const.categoryShipSkin,
         const.categoryExpertSystems)
        noShowGroups = (const.groupMoon,
         const.groupPlanet,
         const.groupConstellation,
         const.groupSolarSystem,
         const.groupRegion,
         const.groupLargeCollidableObject,
         const.groupCharacter,
         const.groupCorporation,
         const.groupAlliance,
         const.groupMoonChunk,
         const.groupIndustrialSupportFacility,
         const.groupStationConversionMonument,
         const.groupTournamentChampionMonument)
        return wnd.categoryID not in noShowCatergories and wnd.groupID not in noShowGroups

    def GetEntityDamageScrollList(self, typeID):
        attributeDictForType = self.GetAttributeDictForType(typeID)
        totalDps = 0
        missileTypeID = attributeDictForType.get(const.attributeEntityMissileTypeID, None)
        isShootingMissiles = self.TypeHasEffect(const.effectMissileLaunchingForEntity, typeID=typeID)
        if missileTypeID and isShootingMissiles:
            missileRof = attributeDictForType.get(const.attributeMissileLaunchDuration, 1000.0) / 1000
            missileMultiplier = attributeDictForType.get(const.attributeMissileDamageMultiplier, 1.0) / missileRof
            attributeDictForMissile = self.GetAttributeDictForType(missileTypeID)
            missileDpsByDamageType = {x:attributeDictForMissile.get(x, 0.0) * missileMultiplier for x in DAMAGE_ATTRIBUTES}
            totalDps += sum((x for x in missileDpsByDamageType.itervalues()))
        else:
            missileDpsByDamageType = {}
        isShootingTurrets = self.TypeHasEffect(const.effectTargetAttack, typeID=typeID) or self.TypeHasEffect(const.effectTargetDisintegratorAttack, typeID=typeID)
        if isShootingTurrets:
            turretRof = attributeDictForType.get(const.attributeRateOfFire, 1.0) / 1000
            turretDamageMultiplier = attributeDictForType.get(const.attributeDamageMultiplier, 1.0) / turretRof
            turretDpsByDamageType = {x:attributeDictForType.get(x, 0.0) * turretDamageMultiplier for x in DAMAGE_ATTRIBUTES}
            totalDps += sum((x for x in turretDpsByDamageType.itervalues()))
        else:
            turretDpsByDamageType = {}
        if totalDps <= 0:
            return []
        dpsByDamageType = {}
        for eachDamageType in DAMAGE_ATTRIBUTES:
            turretValue = turretDpsByDamageType.get(eachDamageType, 0.0)
            missileValue = missileDpsByDamageType.get(eachDamageType, 0.0)
            dpsByDamageType[eachDamageType] = round((turretValue + missileValue) / totalDps, 2)

        unitDict = {x:const.unitAbsolutePercent for x in DAMAGE_ATTRIBUTES}
        scrolllist, _ = self.GetAttributeRows(DAMAGE_ATTRIBUTES, dpsByDamageType, None, overrideUnitDict=unitDict)
        return scrolllist

    def GetInsuranceName(self, fraction):
        fraction = '%.1f' % fraction
        label = {'0.5': 'UI/Insurance/BasicInsurance',
         '0.6': 'UI/Insurance/StandardInsurance',
         '0.7': 'UI/Insurance/BronzeInsurance',
         '0.8': 'UI/Insurance/SilverInsurance',
         '0.9': 'UI/Insurance/GoldInsurance',
         '1.0': 'UI/Insurance/PlatinumInsurance'}.get(fraction, fraction)
        return GetByLabel(label)

    def GetGAVFunc(self, itemID, typeID):
        info = sm.GetService('godma').GetItem(itemID)
        if info is not None:
            return lambda attributeID: getattr(info, dogma_data.get_attribute_name(attributeID))
        dogmaLocation = self.GetDogmaLocation(itemID)
        if dogmaLocation.IsItemLoaded(itemID):
            return lambda attributeID: dogmaLocation.GetAttributeValue(itemID, attributeID)
        info = sm.GetService('godma').GetStateManager().GetShipType(typeID)
        return lambda attributeID: getattr(info, dogma_data.get_attribute_name(attributeID))

    def GetCertEntry(self, certificate, level):
        entry = {'label': certificate.GetName(),
         'level': level,
         'iconID': 'res:/UI/Texture/Classes/Certificates/level%sSmall.png' % level,
         'id': ('CertEntry', '%s_%s' % (certificate.certificateID, level)),
         'certificate': certificate,
         'certID': certificate.certificateID,
         'GetSubContent': CertEntry.GetSubContent,
         'genericDisplayLabel': StripTags(certificate.GetName())}
        return entry

    def GetAgentScrollGroups(self, agents, scroll):
        dudesToPrime = []
        locationsToPrime = []
        for each in agents:
            dudesToPrime.append(each.agentID)
            if each.stationID:
                locationsToPrime.append(each.stationID)
            locationsToPrime.append(each.solarsystemID)

        cfg.eveowners.Prime(dudesToPrime)
        cfg.evelocations.Prime(locationsToPrime)

        def SortFunc(level, agentID, x, y):
            if x[level] < y[level]:
                return -1
            if x[level] > y[level]:
                return 1
            xname = cfg.eveowners.Get(x[agentID]).name
            yname = cfg.eveowners.Get(y[agentID]).name
            if xname < yname:
                return -1
            if xname > yname:
                return 1
            return 0

        agents.sort(lambda x, y: SortFunc(agents.header.index('level'), agents.header.index('agentID'), x, y))
        allAgents = sm.RemoteSvc('agentMgr').GetAgents().Index('agentID')
        divisions = {}
        for each in agents:
            if allAgents[each[0]].divisionID not in divisions:
                divisions[allAgents[each[0]].divisionID] = 1

        for divisionID in sorted(divisions, key=lambda _divisionID: get_division_name(_divisionID).lower()):
            amt = 0
            for agent in agents:
                if agent.divisionID == divisionID:
                    amt += 1

            label = GetByLabel('UI/InfoWindow/AgentDivisionWithCount', divisionName=get_division_name(divisionID).replace('&', '&amp;'), numAgents=amt)
            scroll.append(GetFromClass(ListGroup, {'GetSubContent': self.GetCorpAgentListSubContent,
             'label': label,
             'agentdata': (divisionID, agents),
             'id': ('AGENTDIVISIONS', divisionID),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'showlen': 0}))

    def CompareTypes(self, wnd):
        from eve.client.script.ui.shared.neocom.compare import TypeCompare
        typeWnd = TypeCompare.Open()
        typeWnd.AddEntry(wnd.variationTypeDict)

    def GetBaseWarpSpeed(self, typeID, shipinfo = None, itemID = None):
        defaultWSM = 1.0
        defaultBWS = 3.0
        wsm = dogma_data.get_type_attribute(typeID, const.attributeWarpSpeedMultiplier, defaultWSM)
        bws = dogma_data.get_type_attribute(typeID, const.attributeBaseWarpSpeed, defaultBWS)
        typeWsm = wsm
        typeBws = bws
        if shipinfo:
            wsm = getattr(shipinfo, 'warpSpeedMultiplier', defaultWSM)
            bws = getattr(shipinfo, 'baseWarpSpeed', defaultBWS)
        elif self.IsItemSimulated(itemID):
            dogmaLocation = self.GetDogmaLocation(itemID)
            dogmaItem = dogmaLocation.SafeGetDogmaItem(itemID)
            if dogmaItem:
                wsm = dogmaLocation.GetAttributeValue(itemID, const.attributeWarpSpeedMultiplier)
                bws = dogmaLocation.GetAttributeValue(itemID, const.attributeBaseWarpSpeed)
        multipliers = max(1.0, bws) * wsm
        corruptionWarpSpeedIncrease = 0.0
        if itemID == session.shipid:
            corruptionWarpSpeedChecker = CorruptionWarpSpeedIncreaserCheckerClient(session.solarsystemid2)
            corruptionWarpSpeedIncrease = corruptionWarpSpeedChecker.GetWarpSpeedIncrease(session.warfactionid)
            multipliers += corruptionWarpSpeedIncrease
        warpSpeedWithMultipliers = multipliers * const.AU
        typeWarpSpeedWithMultipliers = max(1.0, typeBws) * typeWsm * const.AU
        warpSpeedText = GetByLabel('UI/Fitting/FittingWindow/WarpSpeed', distText=FmtDist(warpSpeedWithMultipliers, 2))
        return (warpSpeedText,
         warpSpeedWithMultipliers,
         typeWarpSpeedWithMultipliers,
         corruptionWarpSpeedIncrease)

    def GetBaseDamageValue(self, typeID):
        bsd = None
        bad = None
        typeAttributesByAttributeID = dogma_data.get_type_attributes_by_id(typeID)
        vals = []
        for attrID in DAMAGE_ATTRIBUTES:
            if attrID in typeAttributesByAttributeID:
                vals.append(typeAttributesByAttributeID[attrID].value)

        if len(vals) == 4:
            bsd = (vals[0] * 1.0 + vals[1] * 0.8 + vals[2] * 0.6 + vals[3] * 0.4, 69)
            bad = (vals[0] * 0.4 + vals[1] * 0.65 + vals[2] * 0.75 + vals[3] * 0.9, 68)
        return (bsd, bad)

    def GetKillsRecentKills(self, num, startIndex):
        shipKills = sm.RemoteSvc('charMgr').GetRecentShipKillsAndLosses(num, startIndex)
        return [ k for k in shipKills if k.finalCharacterID == eve.session.charid ]

    def GetKillsRecentLosses(self, num, startIndex):
        shipKills = sm.RemoteSvc('charMgr').GetRecentShipKillsAndLosses(num, startIndex)
        return [ k for k in shipKills if k.victimCharacterID == eve.session.charid ]

    def FindInContracts(self, typeID):
        sm.GetService('contracts').FindRelated(typeID, None, None, None, None, None)

    def ShowMarketDetails(self, typeID):
        uthread.new(sm.StartService('marketutils').ShowMarketDetails, typeID, None)

    def ViewExpertSystemInStore(self, typeID):
        from expertSystems.client.util import browse_expert_systems
        browse_expert_systems(typeID)

    def GetAllianceHistorySubContent(self, itemID):
        scrolllist = []
        allianceHistory = sm.RemoteSvc('allianceRegistry').GetEmploymentRecord(itemID)

        def AddToScroll(**data):
            scrolllist.append(GetFromClass(LabelTextTop, data))

        if len(allianceHistory) == 0:
            AddToScroll(line=True, text='', label=GetByLabel('UI/InfoWindow/NoRecordsFound'), typeID=None, itemID=None)
        toPrime = set()
        for allianceRec in allianceHistory[:-1]:
            toPrime.add(allianceRec.allianceID)

        toPrime = filter(None, toPrime)
        cfg.eveowners.Prime(toPrime)
        lastQuit = None
        for allianceRec in allianceHistory[:-1]:
            if allianceRec.allianceID is None:
                lastQuit = allianceRec.startDate
            else:
                alliance = cfg.eveowners.Get(allianceRec.allianceID)
                if allianceRec.startDate:
                    sd = FmtDate(allianceRec.startDate, 'ln')
                else:
                    sd = GetByLabel('UI/InfoWindow/UnknownAllianceStartDate')
                if allianceRec.deleted:
                    nameTxt = GetByLabel('UI/InfoWindow/AllianceClosed', allianceName=alliance.name)
                else:
                    nameTxt = alliance.name
                if lastQuit:
                    ed = FmtDate(lastQuit, 'ln')
                    text = GetByLabel('UI/InfoWindow/InAllianceFromAndTo', allianceName=nameTxt, fromDate=sd, toDate=ed)
                else:
                    text = GetByLabel('UI/InfoWindow/InAllianceFromAndToThisDay', allianceName=nameTxt, fromDate=sd)
                AddToScroll(line=True, label=GetByLabel('UI/Common/Alliance'), text=text, typeID=alliance.typeID, itemID=allianceRec.allianceID)
                lastQuit = None

        if len(allianceHistory) > 1:
            scrolllist.append(GetFromClass(DividerEntry))
        if len(allianceHistory) >= 1:
            AddToScroll(line=True, label=GetByLabel('UI/InfoWindow/CorporationFounded'), text=FmtDate(allianceHistory[-1].startDate, 'ln'), typeID=None, itemID=None)
        return scrolllist

    def GetWarHistorySubContent(self, itemID, warFactionID = None):
        regwars = sm.RemoteSvc('warsInfoMgr').GetWarsByOwnerID(itemID)
        facwars = []
        scrolllist = []
        if (idCheckers.IsAlliance(itemID) or idCheckers.IsCorporation(itemID)) and warFactionID:
            facwars = sm.GetService('facwar').GetFactionWarsForWarFactionID(warFactionID).values()
        notStartedWars = []
        ongoingWars = []
        finishedWars = []
        currentTime = blue.os.GetWallclockTime()
        for war in regwars:
            warFinished = war.timeFinished
            timeStarted = war.timeStarted
            if warFinished and warFinished < currentTime:
                finishedWars.append(war)
            elif timeStarted > currentTime:
                notStartedWars.append(war)
            else:
                ongoingWars.append(war)

        warsGroupedByTypes = [facwars, ongoingWars, notStartedWars]
        if len(finishedWars) < FINISHED_WARS_FOLDER_THRESHOLD:
            warsGroupedByTypes.append(finishedWars)
        self.PrimeWarTypes(warsGroupedByTypes)
        if ongoingWars:
            myLabel = GetByLabel('UI/Corporations/Wars/ActiveWars')
            warGroup = self.GetNormalWarGroup(sorted(ongoingWars, key=lambda w: w.timeStarted), myLabel, 'ongoingWars')
            scrolllist.append(warGroup)
        if facwars:
            myLabel = GetByLabel('UI/Corporations/Wars/FactionalWars')
            warGroup = self.GetNormalWarGroup(facwars, myLabel, 'factional')
            scrolllist.append(warGroup)
        if notStartedWars:
            myLabel = GetByLabel('UI/Corporations/Wars/PendingWars')
            warGroup = self.GetNormalWarGroup(sorted(notStartedWars, key=lambda w: w.timeStarted), myLabel, 'notStartedWars')
            scrolllist.append(warGroup)
        if finishedWars:
            myLabel = GetByLabel('UI/Corporations/Wars/FinishedWars')
            warGroup = self.GetFinishedWarsGroup(sorted(finishedWars, key=lambda w: w.timeFinished), myLabel, 'finished')
            scrolllist.append(warGroup)
        return scrolllist

    def PrimeWarTypes(self, warsGroupedByTypes):
        owners = set()
        for wars in warsGroupedByTypes:
            ownersForWars = self.GetOwnersForWars(wars)
            owners.update(ownersForWars)

        if len(owners):
            cfg.eveowners.Prime(owners)
            cfg.corptickernames.Prime(owners)

    def GetOwnersForWars(self, wars):
        owners = set()
        for war in wars:
            if war.declaredByID not in owners:
                owners.add(war.declaredByID)
            if war.againstID not in owners:
                owners.add(war.againstID)

        return owners

    def GetFinishedWarsGroup(self, groupItems, label, groupType):
        subContentFunc = self.GetFinishedWarSubContent
        return self.GetWarGroup(groupItems, label, groupType, subContentFunc)

    def GetNormalWarGroup(self, groupItems, label, groupType, sublevel = 0):
        subContentFunc = self.GetWarSubContent
        return self.GetWarGroup(groupItems, label, groupType, subContentFunc, sublevel)

    def GetWarGroup(self, groupItems, label, groupType, subContentFunc, sublevel = 0):
        return GetFromClass(ListGroup, {'GetSubContent': subContentFunc,
         'label': label,
         'id': ('war', groupType, label),
         'state': 'locked',
         'BlockOpenWindow': 1,
         'showicon': 'hide',
         'showlen': 1,
         'groupName': groupType,
         'groupItems': groupItems,
         'updateOnToggle': 0,
         'sublevel': sublevel})

    def GetWarSubContent(self, items, *args):
        scrolllist = []
        data = utillib.KeyVal()
        data.label = ''
        wars = items.groupItems
        if items.groupName != 'factional':
            wars = sorted(wars, key=lambda x: x.timeDeclared, reverse=True)
        for war in wars:
            data.war = war
            scrolllist.append(GetFromClass(WarEntry, data))

        return scrolllist

    def GetFinishedWarSubContent(self, items, *args):
        finishedWars = items.groupItems
        if len(finishedWars) < FINISHED_WARS_FOLDER_THRESHOLD:
            self.PrimeWarTypes([finishedWars])
            return self.GetWarSubContent(items)
        warsByYears = self.GetWarsByYearList(finishedWars)
        scrolllist = []
        for eachYear, warList in warsByYears:
            warGroup = self.GetWarGroup(warList, eachYear, 'eachYear_%s' % eachYear, self.GetYearSubcontentForFinishedWars, sublevel=1)
            scrolllist.append(warGroup)

        return scrolllist

    def GetWarsByYearList(self, warList):
        warsByYears = defaultdict(set)
        for eachWar in warList:
            year, _, _, _, _, _, _, _ = blue.os.GetTimeParts(eachWar.timeFinished)
            warsByYears[year].add(eachWar)

        if not warsByYears:
            return []
        warsByYearsList = warsByYears.items()
        warsByYearsList.sort(key=lambda x: x[0], reverse=True)
        return warsByYearsList

    def GetYearSubcontentForFinishedWars(self, items, *args):
        wars = items.groupItems
        self.PrimeWarTypes([wars])
        return self.GetWarSubContent(items)

    def GetEmploymentHistorySubContent(self, itemID):
        scrolllist = []
        employmentHistory, charTransfers = sm.RemoteSvc('corporationSvc').GetEmployementRecordAndCharacterTransfers(itemID)
        nextDate = None
        nextDateRaw = None
        corpIDsToPrime = {j.corporationID for j in employmentHistory}
        cfg.eveowners.Prime(corpIDsToPrime)
        for job in employmentHistory:
            corp = cfg.eveowners.Get(job.corporationID)
            corpName = evelink.client.owner_link(job.corporationID)
            if job.deleted:
                nameText = GetByLabel('UI/InfoWindow/CorporationClosed', corpName=corpName)
            else:
                nameText = corpName
            date = FmtDate(job.startDate, 'ls')
            if nextDate is None:
                text = GetByLabel('UI/InfoWindow/InCorpFromAndToThisDay', corpName=nameText, fromDate=date)
            else:
                text = GetByLabel('UI/InfoWindow/InCorpFromAndTo', corpName=nameText, fromDate=date, toDate=nextDate)
            endDate = nextDateRaw or blue.os.GetWallclockTime()
            diff = endDate - job.startDate
            numDays = max(1, diff / const.DAY)
            numDaysText = GetByLabel('UI/Common/NumDays', numDays=numDays).strip()
            text = '%s (%s)' % (text, numDaysText)
            nextDate = date
            nextDateRaw = job.startDate
            entry = GetFromClass(Text, {'text': text,
             'typeID': corp.typeID,
             'itemID': job.corporationID})
            scrolllist.append(entry)

        if charTransfers:
            scrolllist.append(GetFromClass(Space, {'height': 20}))
            groupEntry = GetFromClass(ListGroup, {'GetSubContent': self.GetCharacterTranfersSubContent,
             'label': GetByLabel('UI/InfoWindow/CharacterTransfers'),
             'groupItems': charTransfers,
             'id': ('character_transfers', 1),
             'showlen': 1,
             'showicon': 'hide',
             'state': 'locked'})
            scrolllist.append(groupEntry)
        return scrolllist

    def GetCharacterTranfersSubContent(self, nodedata, *args):
        charTransfers = nodedata.groupItems
        scrollList = []
        for eachTransfer in charTransfers:
            text = GetByLabel('UI/InfoWindow/CharacterTransferredDate', transferDate=eachTransfer.transferDate)
            entry = GetFromClass(Generic, {'label': text,
             'sublevel': 1})
            scrollList.append((eachTransfer.transferDate, entry))

        scrollList = SortListOfTuples(scrollList, reverse=True)
        return scrollList

    def GetAllianceMembersSubContent(self, itemID):
        members = sm.RemoteSvc('allianceRegistry').GetAllianceMembers(itemID)
        cfg.eveowners.Prime([ m.corporationID for m in members ])
        scrolllist = []
        for m in members:
            corp = cfg.eveowners.Get(m.corporationID)
            scrolllist.append(GetFromClass(LabelTextTop, {'line': True,
             'label': GetByLabel('UI/Common/Corporation'),
             'text': corp.name,
             'typeID': corp.typeID,
             'itemID': m.corporationID}))

        return scrolllist

    def GetCorpAgentListSubContent(self, tmp, *args):
        divisionID, agents = tmp.agentdata
        scrolllist = []
        scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/AvailableToYou')}))
        noadd = 1
        for agent in agents:
            if agent.divisionID != divisionID:
                continue
            isLimitedToFacWar = False
            if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and sm.StartService('facwar').GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
                isLimitedToFacWar = True
            if sm.GetService('standing').CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID) and isLimitedToFacWar == False:
                scrolllist.append(GetFromClass(AgentEntry, {'charID': agent.agentID,
                 'defaultDivisionID': agent.divisionID}))
                noadd = 0

        if noadd:
            scrolllist.pop(-1)
        scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/NotAvailableToYou')}))
        noadd = 1
        for agent in agents:
            if agent.divisionID != divisionID:
                continue
            isLimitedToFacWar = False
            if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and sm.StartService('facwar').GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
                isLimitedToFacWar = True
            if not sm.GetService('standing').CanUseAgent(agent.factionID, agent.corporationID, agent.agentID, agent.level, agent.agentTypeID) or isLimitedToFacWar == True:
                scrolllist.append(GetFromClass(AgentEntry, {'charID': agent.agentID,
                 'defaultDivisionID': agent.divisionID}))
                noadd = 0

        if noadd:
            scrolllist.pop(-1)
        return scrolllist

    def __GetIllegalityString(self, illegality):
        textList = self.__GetIllegalityStringList(illegality)
        if len(textList) > 0:
            text = ' / '.join(textList)
        else:
            text = ''
        return text

    def __GetIllegalityStringList(self, illegality):
        textList = []
        if illegality.standingLoss > 0.0:
            t = GetByLabel('UI/InfoWindow/StandingLoss', standingLoss=illegality.standingLoss)
            textList.append(t)
        if illegality.confiscateMinSec <= 1.0:
            t = GetByLabel('UI/InfoWindow/ConfiscationInSec', confiscateMinSec=max(illegality.confiscateMinSec, 0.0))
            textList.append(t)
        if illegality.fineByValue > 0.0:
            t = GetByLabel('UI/InfoWindow/FineOfEstimatedMarketValue', fine=illegality.fineByValue * 100.0)
            textList.append(t)
        if illegality.attackMinSec <= 1.0:
            t = GetByLabel('UI/InfoWindow/AttackInSec', attackMinSec=max(illegality.attackMinSec, 0.0))
            textList.append(t)
        return textList

    def GetAttributeScrollListForItem(self, itemID, typeID, attrList = None, banAttrs = []):
        attributeDictForType, attributeDict = self.GetAttributeDictForItem(itemID, typeID)
        modifiedAttributesDict = self.FindAttributesThatHaveBeenModified(attributeDictForType, attributeDict)
        modifiedAttributesDict = self.FindMutatedAttributes(typeID, itemID, attributeDictForType, modifiedAttributesDict)
        if not attributeDict:
            attributeDict = attributeDictForType
        scrolllist = self.GetAttributeScrollListFromAttributeDict(attrdict=attributeDict, attrList=attrList, banAttrs=banAttrs, itemID=itemID, typeID=typeID, modifiedAttributesDict=modifiedAttributesDict)
        return scrolllist

    def FindAttributesThatHaveBeenModified(self, typeDict, itemDict):
        modifiedAttributes = {}
        for itemAttributeKey, itemValue in itemDict.iteritems():
            typeValue = typeDict.get(itemAttributeKey, dogma_data.get_attribute_default_value(itemAttributeKey))
            if itemValue != typeValue:
                m = CreateAttribute(itemAttributeKey, itemValue, typeValue)
                modifiedAttributes[itemAttributeKey] = m

        return modifiedAttributes

    def FindMutatedAttributes(self, typeID, itemID, typeAttributes = None, attributes = None):
        if typeAttributes is None:
            typeAttributes = self.GetAttributeDictForType(typeID)
        if attributes is None:
            attributes = {}
        dynamicItemSvc = sm.GetService('dynamicItemSvc')
        if not dynamicItemSvc.IsDynamicItem(typeID) or itemID is None:
            return attributes
        item = dynamicItemSvc.GetDynamicItem(itemID)
        sourceAttributes = self.GetAttributeDictForType(item.sourceTypeID)
        mutatorAttributes = dynamicitemattributes.GetMutatorAttributes(item.mutatorTypeID)
        for attributeID, mutatorAttribute in mutatorAttributes.iteritems():
            if attributeID in attributes:
                attribute = attributes[attributeID]
            else:
                attribute = Attribute(attributeID, typeAttributes[attributeID])
            sourceValue = sourceAttributes[attributeID]
            attributes[attributeID] = MutatedAttribute(attribute, sourceValue, mutatorAttribute.min * sourceValue, mutatorAttribute.max * sourceValue, getattr(mutatorAttribute, 'highIsGood', None))

        return attributes

    def GetDogmaLocation(self, itemID):
        if self.IsItemSimulated(itemID):
            dogmaLocation = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        else:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        return dogmaLocation

    def IsItemSimulated(self, itemID):
        if isinstance(itemID, tuple):
            itemID = itemID[0]
        if isinstance(itemID, basestring):
            return True
        return False

    def GetSpaceComponentAttrItemInfo(self, typeID, itemID):
        scrolllist = []
        attributeCollection = {}
        componentNames = get_space_component_names_for_type(typeID)
        if len(componentNames) == 0:
            return scrolllist
        componentInstances = self.GetComponentInstance(itemID)
        for componentName in componentNames:
            try:
                componentClass = factory.GetComponentClass(componentName)
                if hasattr(componentClass, 'GetAttributeInfo'):
                    instance = componentInstances.get(componentName)
                    attributes = get_space_component_for_type(typeID, componentName)
                    attributeList = componentClass.GetAttributeInfo(typeID, attributes, instance, localization)
                    attributeCollection[componentName] = attributeList
            except KeyError:
                pass

        for attributeList in IterAttributeCollectionInInfoOrder(attributeCollection):
            for entryClass, entryData in attributeList:
                scrolllist.append(GetFromClass(entryClass, entryData))

        return scrolllist

    def GetComponentInstance(self, itemID):
        componentInstances = {}
        if itemID:
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark:
                try:
                    componentInstances = ballpark.componentRegistry.GetComponentsByItemID(itemID)
                except KeyError:
                    pass

        return componentInstances

    def GetAttributesSuppressedByComponents(self, typeID):
        componentNames = get_space_component_names_for_type(typeID)
        suppressedAttributeIDs = []
        for componentName in componentNames:
            self._TryAddSuppressedComponentAttributeIDs(componentName, suppressedAttributeIDs)

        return suppressedAttributeIDs

    def _TryAddSuppressedComponentAttributeIDs(self, componentName, suppressedAttributeIDs):
        try:
            componentClass = factory.GetComponentClass(componentName)
            if hasattr(componentClass, 'GetSuppressedDogmaAttributeIDs'):
                suppressedAttributeIDs.extend(componentClass.GetSuppressedDogmaAttributeIDs())
        except KeyError:
            pass

    def GetAttributeScrollListForType(self, typeID, attrList = None, attrValues = None, banAttrs = [], itemID = None):
        attributeDict, itemAttributeDict = self.GetAttributeDictForItem(itemID, typeID)
        if itemAttributeDict:
            attributeDict = itemAttributeDict
        scrolllist = self.GetAttributeScrollListFromAttributeDict(attrdict=attributeDict, attrList=attrList, attrValues=attrValues, banAttrs=banAttrs, itemID=itemID, typeID=typeID)
        return scrolllist

    def GetAttributeRows(self, tryAddAttributeIDs, attrdict, itemID, modifiedAttributesDict = {}, overrideUnitDict = None):
        overrideUnitDict = overrideUnitDict or {}
        newScrollEntries = []
        attributeListInfo = [(0, const.damageTypeAttributes, 'UI/Common/Damage'),
         (1, const.damageResistanceBonuses, 'UI/Inflight/ModuleRacks/Tooltips/DamageResistanceBonuses'),
         (2, const.hullDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/HullDamageResistanceHeader'),
         (3, const.armorDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/ArmorDamageResistanceHeader'),
         (4, const.shieldDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/ShieldDamageResistanceHeader'),
         (5, const.sensorStrength, 'UI/Inflight/ModuleRacks/Tooltips/SensorStrength'),
         (6, const.sensorStrengthPercentAttrs, 'UI/Inflight/ModuleRacks/Tooltips/EcmJammerStrength'),
         (7, const.sensorStrengthBonusAttrs, 'UI/Inflight/ModuleRacks/Tooltips/SensorStrengthBonuses'),
         (8, const.passiveArmorDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/ArmorDamageResistanceHeader'),
         (9, const.passiveShieldDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/ShieldDamageResistanceHeader')]
        allGroupedAttributes = []
        for attributeGroup in attributeListInfo:
            allGroupedAttributes += attributeGroup[1]

        attributesAdded = []
        for eachAttributeID in tryAddAttributeIDs:
            if eachAttributeID not in allGroupedAttributes or eachAttributeID in attributesAdded:
                continue
            for eachAttributeListInfo in attributeListInfo:
                sortIdx, eachAttributeList, textPath = eachAttributeListInfo
                if eachAttributeID not in eachAttributeList:
                    continue
                allAttributes = []
                for xID in eachAttributeList:
                    value = attrdict.get(xID, 0)
                    formatInfo = GetFormattedAttributeAndValue(xID, value, overrideUnitDict.get(xID, None))
                    if formatInfo:
                        formatValue = formatInfo.value
                    else:
                        formatValue = None
                    allAttributes.append((xID, formatValue))

                validValues = filter(None, [ a[1] for a in allAttributes ])
                if not validValues:
                    continue
                modifiedAttributes = {x:modifiedAttributesDict[x] for x in eachAttributeList if x in modifiedAttributesDict}
                entry = GetFromClass(AttributeRowEntry, {'labelPath': textPath,
                 'attributeValues': allAttributes,
                 'attributeIDs': [ a[0] for a in allAttributes ],
                 'OnClickAttr': lambda attributeID: self.OnAttributeClick(attributeID, itemID),
                 'modifiedAttributesDict': modifiedAttributes,
                 'itemID': itemID})
                newScrollEntries.append((sortIdx, entry))
                attributesAdded += eachAttributeList
                break

        newScrollEntries = SortListOfTuples(newScrollEntries)
        return (newScrollEntries, attributesAdded)

    def GetAttributeRowData(self, tryAddAttributeIDs, attrdict, itemID, modifiedAttributesDict = {}, overrideUnitDict = None):
        overrideUnitDict = overrideUnitDict or {}
        newScrollEntries = []
        attributeListInfo = [(0, const.damageTypeAttributes, 'UI/Common/Damage'),
         (1, const.damageResistanceBonuses, 'UI/Inflight/ModuleRacks/Tooltips/DamageResistanceBonuses'),
         (2, const.hullDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/HullDamageResistanceHeader'),
         (3, const.armorDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/ArmorDamageResistanceHeader'),
         (4, const.shieldDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/ShieldDamageResistanceHeader'),
         (5, const.sensorStrength, 'UI/Inflight/ModuleRacks/Tooltips/SensorStrength'),
         (6, const.sensorStrengthPercentAttrs, 'UI/Inflight/ModuleRacks/Tooltips/EcmJammerStrength'),
         (7, const.sensorStrengthBonusAttrs, 'UI/Inflight/ModuleRacks/Tooltips/SensorStrengthBonuses'),
         (8, const.passiveArmorDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/ArmorDamageResistanceHeader'),
         (9, const.passiveShieldDamageTypeResonanceAttributes, 'UI/Inflight/ModuleRacks/Tooltips/ShieldDamageResistanceHeader')]
        allGroupedAttributes = []
        for attributeGroup in attributeListInfo:
            allGroupedAttributes += attributeGroup[1]

        attributesAdded = []
        for eachAttributeID in tryAddAttributeIDs:
            if eachAttributeID not in allGroupedAttributes or eachAttributeID in attributesAdded:
                continue
            for eachAttributeListInfo in attributeListInfo:
                sortIdx, eachAttributeList, textPath = eachAttributeListInfo
                if eachAttributeID not in eachAttributeList:
                    continue
                allAttributes = []
                for xID in eachAttributeList:
                    value = attrdict.get(xID, 0)
                    formatInfo = GetFormattedAttributeAndValue(xID, value, overrideUnitDict.get(xID, None))
                    if formatInfo:
                        formatValue = formatInfo.value
                    else:
                        formatValue = None
                    allAttributes.append((xID, formatValue))

                validValues = filter(None, [ a[1] for a in allAttributes ])
                if not validValues:
                    continue
                modifiedAttributes = {x:modifiedAttributesDict[x] for x in eachAttributeList if x in modifiedAttributesDict}
                entry = {'labelPath': textPath,
                 'attributeValues': allAttributes,
                 'attributeIDs': [ a[0] for a in allAttributes ],
                 'OnClickAttr': lambda attributeID: self.OnAttributeClick(attributeID, itemID),
                 'modifiedAttributesDict': modifiedAttributes,
                 'itemID': itemID}
                newScrollEntries.append(entry)
                attributesAdded += eachAttributeList
                break

        return (newScrollEntries, attributesAdded)

    def GetAttributeScrollListFromAttributeDict(self, attrdict, attrList = None, attrValues = None, banAttrs = [], itemID = None, typeID = None, modifiedAttributesDict = {}):
        scrolllist = []
        if attrValues:
            for each in attrValues.displayAttributes:
                attrdict[each.attributeID] = each.value

        attrList = attrList or attrdict.keys()
        aggregateAttributes = defaultdict(list)
        for attrID in tuple(attrList):
            if attrID in const.canFitShipGroups or attrID in const.canFitShipTypes:
                dgmType = dogma_data.get_attribute(attrID)
                value = attrdict[attrID]
                formattedValue = GetFormatAndValue(dgmType, value)
                groupOrType = 'group' if attrID in const.canFitShipGroups else 'type'
                aggregateAttributes['canFitShip'].append((formattedValue, groupOrType, value))
                attrList.remove(attrID)

        order = self.GetAttributeOrder()
        tryAddAttributeIDs = []
        for attrID_ in order:
            if attrID_ in attrList and attrID_ not in banAttrs:
                tryAddAttributeIDs.append(attrID_)

        for attrID_ in attrList:
            if attrID_ not in order and attrID_ not in banAttrs:
                tryAddAttributeIDs.append(attrID_)

        newAttributeRows, attributesAddedInRows = self.GetAttributeRows(tryAddAttributeIDs, attrdict, itemID, modifiedAttributesDict)

        def TryAddAttributeEntry(attrID):
            if attrID not in attrdict:
                return
            modifiedAttribute = modifiedAttributesDict.get(attrID)
            listItem = self.GetEntryForAttribute(attrID, attrdict[attrID], itemID, typeID=typeID, modifiedAttribute=modifiedAttribute)
            if listItem:
                scrolllist.append(listItem)

        for attrID_ in tryAddAttributeIDs:
            if attrID_ not in attributesAddedInRows:
                TryAddAttributeEntry(attrID_)

        attributeValues = aggregateAttributes.get('canFitShip')
        if attributeValues is not None:
            attrID = const.canFitShipTypes[0]
            iconID = dogma_data.get_attribute_icon_id(attrID)
            displayName = dogma_data.get_attribute_display_name(attrID)
            rightTextLabels = []
            for text, groupOrType, value in attributeValues:
                if groupOrType == 'group':
                    groupID = int(value)
                    typeIDs = evetypes.GetTypeIDsByGroup(groupID)
                    typeNames = [ evetypes.GetName(x) for x in typeIDs if evetypes.IsPublished(x) ]
                    typeNames.sort()
                    if typeNames:
                        headerLabelPath = 'UI/InfoWindow/StructureTypes' if evetypes.GetCategoryIDByGroup(groupID) == const.categoryStructure else 'UI/InfoWindow/ShipTypes'
                        typeNames.insert(0, localization.GetByLabel(headerLabelPath))
                    hintText = '<br>'.join(typeNames)
                    rightTextLabels.append((text, hintText))
                else:
                    rightTextLabels.append((text, None))

            listItem = GetFromClass(LabelMultilineTextTop, {'attributeID': attrID,
             'OnClick': (self.OnAttributeClick, attrID, itemID),
             'line': 1,
             'label': displayName,
             'rightTextLabels': rightTextLabels,
             'iconID': iconID,
             'typeID': None,
             'itemID': itemID})
            scrolllist.append(listItem)
        scrolllist += newAttributeRows
        return scrolllist

    def GetAttributeDictForItem(self, itemID, typeID):
        attributeDictForType = self.GetAttributeDictForType(typeID)
        if not itemID:
            return (attributeDictForType, attributeDictForType)
        if dynamicitemattributes.IsDynamicType(typeID):
            attributeDictForType = sm.GetService('dynamicItemSvc').GetDynamicItemAttributes(itemID)
        attributeDictForItem = {}
        attributeDictForItem.update(attributeDictForType)
        itemAttributesDict = self.GetDisplayAttributesForItem(itemID)
        if not itemAttributesDict:
            itemAttributesDict = self.GetDisplayAttributeForDogmaItem(itemID, attributeDictForType.keys())
        attributeDictForItem.update(itemAttributesDict)
        return (attributeDictForType, attributeDictForItem)

    def GetAttributeDictForType(self, typeID):
        typeAttributesByAttributeID = dogma_data.get_type_attributes_by_id(typeID)
        attributeIDs = {const.attributeCapacity, const.attributeVolume}
        attributeIDs.update(typeAttributesByAttributeID.keys())
        ret = {}
        for attributeID in attributeIDs:
            attribute = dogma_data.get_attribute(attributeID)
            if attribute.dataType == dogma.const.attributeDataTypeTypeMirror:
                try:
                    ret[attributeID] = evetypes.GetAttributeForType(typeID, attribute.name)
                except Exception:
                    pass

            else:
                ret[attributeID] = typeAttributesByAttributeID[attributeID].value

        return ret

    def GetDisplayAttributesForItem(self, itemID):
        godmaItem = sm.GetService('godma').GetItem(itemID)
        if not godmaItem:
            return {}
        displayAttributes = {a.attributeID:a.value for a in godmaItem.displayAttributes}
        if evetypes.GetCategoryID(godmaItem.typeID) in (const.categoryCharge, const.groupFrequencyCrystal):
            self._UpdateChargeDamageWithDamageModifier(godmaItem, displayAttributes)
        return displayAttributes

    def _UpdateChargeDamageWithDamageModifier(self, godmaChargeItem, displayAttributes):
        if not godmaChargeItem.IsFitted():
            return
        dogmaLocation = self.GetDogmaLocation(godmaChargeItem.itemID)
        moduleID = dogmaLocation.GetSlotOther(godmaChargeItem.locationID, godmaChargeItem.flagID)
        if not moduleID:
            return
        moduleItem = dogmaLocation.SafeGetDogmaItem(moduleID)
        if self.TypeHasEffect(const.effectLauncherFitted, typeID=moduleItem.typeID):
            damageModifier = dogmaLocation.GetAccurateAttributeValue(session.charid, const.attributeMissileDamageMultiplier)
        else:
            damageModifier = dogmaLocation.GetAccurateAttributeValue(moduleID, const.attributeDamageMultiplier)
        if not damageModifier:
            return
        for eachAttributeID in DAMAGE_ATTRIBUTES:
            if eachAttributeID in displayAttributes:
                displayAttributes[eachAttributeID] *= damageModifier

    def GetDisplayAttributeForDogmaItem(self, itemID, attributeKeys):
        dogmaLocation = self.GetDogmaLocation(itemID)
        if not dogmaLocation.IsItemLoaded(itemID):
            return {}
        attributeDict = {}
        for attributeID in attributeKeys:
            value = dogmaLocation.GetAttributeValue(itemID, attributeID)
            attributeDict[attributeID] = value

        return attributeDict

    def GetEntryForAttribute(self, attributeID, value, itemID = None, typeID = None, modifiedAttribute = None):
        listItem = self.GetStatusBarEntryForAttribute(attributeID, itemID=itemID, typeID=typeID, modifiedAttribute=modifiedAttribute)
        if listItem:
            return listItem
        data = self.GetDataForAttribute(attributeID, value, itemID, typeID, modifiedAttribute)
        if data is None:
            return
        listItem = GetFromClass(LabelTextSidesAttributes, data=data)
        return listItem

    def GetDataForAttribute(self, attributeID, value, itemID = None, typeID = None, modifiedAttribute = None):
        if attributeID == const.attributeMetaLevel:
            metaLevel = evetypes.GetMetaLevel(typeID)
            if metaLevel is not None:
                value = metaLevel
        attribute = GetAttribute(attributeID)
        if attribute.unitID == const.unitMilliseconds and value >= 5 * MIN_IN_MS:
            formatInfo = GetFormattedAttributeAndValue(attributeID, value / MIN_IN_MS / 60, const.unitHour)
        else:
            formatInfo = GetFormattedAttributeAndValue(attributeID, value)
        if not formatInfo:
            return
        if itemID and formatInfo.infoTypeID and typeID != formatInfo.infoTypeID:
            itemID = None
        if attributeID == const.attributeVolume:
            if typeID == const.typePlasticWrap and itemID is not None:
                packagedVolume = GetVolumeForPlasticItem(itemID)
                value = packagedVolume
            else:
                packagedVolume = GetTypeVolume(typeID, 1)
            if value != packagedVolume:
                text = GetByLabel('UI/InfoWindow/ItemVolumeWithPackagedVolume', volume=value, packaged=packagedVolume, unit=FormatUnit(const.unitVolume))
            else:
                formatedValue = FormatValue(value, const.attributeVolume)
                text = GetByLabel('UI/InfoWindow/ValueAndUnit', value=formatedValue, unit=FormatUnit(const.unitVolume))
        else:
            text = formatInfo.value
        return {'attributeID': attributeID,
         'OnClick': (self.OnAttributeClick, attributeID, itemID),
         'line': 1,
         'label': formatInfo.displayName,
         'text': text,
         'iconID': formatInfo.iconID,
         'typeID': formatInfo.infoTypeID,
         'itemID': itemID,
         'modifiedAttribute': modifiedAttribute}

    def OnAttributeClick(self, id_, itemID):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not ctrl:
            return
        if not shift and itemID is not None and (itemID >= const.minPlayerItem or idCheckers.IsCharacter(itemID)):
            sm.GetService('godma').LogAttributeViaGodma(itemID, id_)
        if eve.session.role & ROLE_CONTENT == ROLE_CONTENT and ctrl and shift:
            self.GetUrlAdamDogmaAttribute(id_)

    def GetUrlAdamDogmaAttribute(self, id_):
        uthread.new(self.ClickURL, 'http://adam:50001/gd/type.py?action=DogmaModifyAttributeForm&attributeID=%s' % id_)

    def ClickURL(self, url, *args):
        blue.os.ShellExecute(url)

    def GetSkillAttrs(self):
        skillAttrs = [ getattr(const, 'attributeRequiredSkill%s' % i, None) for i in xrange(1, 7) if hasattr(const, 'attributeRequiredSkill%s' % i) ] + [ getattr(const, 'attributeRequiredSkill%sLevel' % i, None) for i in xrange(1, 7) if hasattr(const, 'attributeRequiredSkill%sLevel' % i) ]
        return skillAttrs

    def GetReqSkillInfo(self, typeID, reqSkills = [], showPrereqSkills = True):
        scrolllist = []
        i = 1
        commands = []
        skills = None
        if typeID is not None:
            skills = sm.GetService('skills').GetRequiredSkills(typeID).items()
        if reqSkills:
            skills = reqSkills
        if skills is None:
            return
        for skillID, lvl in skills:
            ret = self.DrawSkillTree(skillID, lvl, scrolllist, 0, showPrereqSkills=showPrereqSkills)
            commands += ret
            i += 1

        cmds = {}
        for typeID, level in commands:
            typeID, level = int(typeID), int(level)
            currentLevel = cmds.get(typeID, 0)
            cmds[typeID] = max(currentLevel, level)

        if i > 1 and eve.session.role & ROLE_GML == ROLE_GML:
            scrolllist.append(GetFromClass(ButtonEntry, {'label': 'GM: Give me these skills',
             'caption': 'Give',
             'OnClick': self.DoGiveSkills,
             'args': (cmds,)}))
        return scrolllist

    def GetRecommendedFor(self, certID):
        recommendedFor = sm.StartService('certificates').GetCertificateRecommendationsFromCertificateID(certID)
        recommendedGroups = {}
        for typeID in recommendedFor:
            if not evetypes.IsPublished(typeID):
                continue
            groupID = evetypes.GetGroupID(typeID)
            current = recommendedGroups.get(groupID, [])
            current.append(typeID)
            recommendedGroups[groupID] = current

        scrolllist = []
        for groupID, value in recommendedGroups.iteritems():
            label = evetypes.GetGroupNameByGroup(groupID)
            scrolllist.append((label, GetFromClass(ListGroup, {'GetSubContent': self.GetEntries,
              'label': label,
              'groupItems': value,
              'id': ('cert_shipGroups', groupID),
              'sublevel': 0,
              'showlen': 1,
              'showicon': 'hide',
              'state': 'locked'})))

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def GetEntries(self, data, *args):
        scrolllist = []
        for typeID in data.groupItems:
            entry = self.CreateEntry(typeID)
            scrolllist.append(entry)

        return scrolllist

    def CreateEntry(self, typeID, *args):
        return GetFromClass(Item, {'line': 1,
         'label': evetypes.GetName(typeID),
         'sublevel': 1,
         'showinfo': 1,
         'typeID': typeID,
         'getIcon': True})

    def DoGiveSkills(self, cmds, button):
        cntFrom = 1
        cntTo = len(cmds) + 1
        sm.GetService('loading').ProgressWnd('GM Skill Gift', '', cntFrom, cntTo)
        for typeID, level in cmds.iteritems():
            cntFrom = cntFrom + 1
            sm.GetService('loading').ProgressWnd('GM Skill Gift', 'Training of the skill %s to level %d has been completed' % (evetypes.GetName(typeID), level), cntFrom, cntTo)
            sm.RemoteSvc('slash').SlashCmd('/giveskill me %s %s' % (typeID, level))

        sm.GetService('loading').ProgressWnd('Done', '', cntTo, cntTo)
        sm.GetService('skills').ForceRefresh()

    def DoRemoveSkill(self, typeID):
        sm.RemoteSvc('slash').SlashCmd('/removeskill me %s' % typeID)
        ShowQuickMessage('Skill %s has been removed' % evetypes.GetName(typeID))

    def GetGMGiveSkillMenu(self, typeID):
        subMenu = (('Remove', self.DoRemoveSkill, (typeID,)),
         ('0', self.DoGiveSkills, ({typeID: 0}, None)),
         ('1', self.DoGiveSkills, ({typeID: 1}, None)),
         ('2', self.DoGiveSkills, ({typeID: 2}, None)),
         ('3', self.DoGiveSkills, ({typeID: 3}, None)),
         ('4', self.DoGiveSkills, ({typeID: 4}, None)),
         ('5', self.DoGiveSkills, ({typeID: 5}, None)))
        return (('GM: Modify skill level', subMenu), ('GM: typeID: %s' % typeID, blue.pyos.SetClipboardData, (str(typeID),)))

    def DoCreateMaterials(self, commands, header = 'GML: Create in cargo', qty = 10, button = None):
        runs = {'qty': qty}
        if qty > 1:
            runs = uix.QtyPopup(100000, 1, qty, None, header)
        if runs is not None and runs.has_key('qty') and runs['qty'] > 0:
            cntFrom = 1
            cntTo = len(commands) + 1
            sm.GetService('loading').ProgressWnd(GetByLabel('UI/Common/GiveLoot'), '', cntFrom, cntTo)
            for typeID, quantity in commands:
                cntFrom = cntFrom + 1
                actualQty = quantity * runs['qty']
                qtyText = '%(quantity)s items(s) of %(typename)s' % {'quantity': quantity * runs['qty'],
                 'typename': evetypes.GetName(typeID)}
                sm.GetService('loading').ProgressWnd(GetByLabel('UI/Common/GiveLoot'), qtyText, cntFrom, cntTo)
                if actualQty > 0:
                    if session.role & ROLE_WORLDMOD:
                        sm.RemoteSvc('slash').SlashCmd('/create %s %d' % (typeID, actualQty))
                    elif session.role & ROLE_GML:
                        sm.RemoteSvc('slash').SlashCmd('/load me %s %d' % (typeID, actualQty))

            sm.GetService('loading').ProgressWnd('Done', '', cntTo, cntTo)

    def DrawSkillTree(self, typeID, lvl, scrolllist, indent, done = None, firstID = None, showPrereqSkills = True):
        thisSet = [(typeID, lvl)]
        if done is None:
            done = []
        if firstID is None:
            firstID = typeID
        scrolllist.append(GetFromClass(SkillTreeEntry, {'line': 1,
         'typeID': typeID,
         'lvl': lvl,
         'indent': indent + 1,
         'origin': ORIGIN_SHOWINFO}))
        done.append(typeID)
        current = typeID
        if showPrereqSkills:
            for typeID, lvl in sm.GetService('skills').GetRequiredSkills(typeID).iteritems():
                if typeID == current:
                    log.LogWarn('Here I have skill which has it self as required skill... skillTypeID is ' + str(typeID))
                    continue
                newSet = self.DrawSkillTree(typeID, lvl, scrolllist, indent + 1, done, firstID)
                thisSet = thisSet + newSet

        return thisSet

    def GetEffectTypeInfo(self, typeID, effList):
        scrolllist = []
        thisTypeEffects = dogma_data.get_type_effects(typeID)
        for effectID in effList:
            itemDgmEffect = self.TypeHasEffect(effectID, thisTypeEffects)
            if not itemDgmEffect:
                continue
            effTypeInfo = dogma_data.get_effect(effectID)
            if effTypeInfo.published:
                scrolllist.append(GetFromClass(LabelTextSidesAttributes, {'line': 1,
                 'label': dogma_data.get_effect_display_name(effectID),
                 'text': dogma_data.get_effect_description(effectID),
                 'iconID': effTypeInfo.iconID}))

        return scrolllist

    def FilterZero(self, value):
        if value == 0:
            return None
        return value

    def TypeHasEffect(self, effectID, itemEffectTypeInfo = None, typeID = None):
        if itemEffectTypeInfo is None:
            itemEffectTypeInfo = dogma_data.get_type_effects(typeID)
        for itemDgmEffect in itemEffectTypeInfo:
            if itemDgmEffect.effectID == effectID:
                return itemDgmEffect

        return 0

    def SetDestination(self, itemID):
        sm.StartService('starmap').SetWaypoint(itemID, clearOtherWaypoints=True)

    def Bookmark(self, itemID, typeID, parentID, *args):
        sm.GetService('addressbook').BookmarkLocationPopup(itemID, typeID, parentID)

    def GetColorCodedSecurityStringForSystem(self, solarsystemID, itemName):
        return u'{security_status}<t>{item_name}'.format(security_status=eveformat.solar_system_security_status(solarsystemID), item_name=itemName)

    def OnShowOwnerDetailsWindow(self, targetID):
        if idCheckers.IsCharacter(targetID):
            self.ShowInfo(const.typeCharacter, targetID)
        elif idCheckers.IsCorporation(targetID):
            self.ShowInfo(const.typeCorporation, targetID)
        elif idCheckers.IsAlliance(targetID):
            self.ShowInfo(const.typeAlliance, targetID)
