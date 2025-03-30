#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\structures\services.py
import structures
import inventorycommon.const
import industry.const
import evetypes
SERVICE_DOCKING = 1
SERVICE_FITTING = 2
SERVICE_OFFICES = 3
SERVICE_REPROCESSING = 4
SERVICE_MARKET = 5
SERVICE_MEDICAL = 6
SERVICE_MISSION = 7
SERVICE_REPAIR = 8
SERVICE_INSURANCE = 9
SERVICE_JUMP_CLONE = 10
SERVICE_LOYALTY_STORE = 11
SERVICE_FACTION_WARFARE = 12
SERVICE_SECURITY_OFFICE = 13
SERVICE_MOONMINING = 14
SERVICE_JUMP_BRIDGE = 15
SERVICE_CYNO_BEACON = 16
SERVICE_CYNO_JAMMER = 17
SERVICE_AUTOMOONMINING = 18
SERVICE_INDUSTRY = 20
SERVICE_MANUFACTURING = 21
SERVICE_MANUFACTURING_BASIC = 22
SERVICE_MANUFACTURING_CAPITAL = 23
SERVICE_MANUFACTURING_SUPERCAPITAL = 24
SERVICE_LABORATORY = 30
SERVICE_LABORATORY_RESEARCH_TIME = 31
SERVICE_LABORATORY_RESEARCH_MATERIAL = 32
SERVICE_LABORATORY_COPYING = 33
SERVICE_LABORATORY_INVENTION = 34
SERVICE_REACTIONS = 40
SERVICE_REACTIONS_COMPOSITE = 41
SERVICE_REACTIONS_BIOCHEMICAL = 42
SERVICE_REACTIONS_HYBRID = 43
SERVICES_BY_NAME = {name:value for name, value in locals().iteritems() if name.startswith('SERVICE_')}
SERVICE_NAME_BY_ID = {value:name for name, value in SERVICES_BY_NAME.iteritems()}
SERVICES = set(SERVICES_BY_NAME.values())
MANUFACTURING_SERVICES = {value for name, value in locals().iteritems() if name.startswith('SERVICE_MANUFACTURING')}
LABORATORY_SERVICES = {value for name, value in locals().iteritems() if name.startswith('SERVICE_LABORATORY')}
REACTION_SERVICES = {value for name, value in locals().iteritems() if name.startswith('SERVICE_REACTIONS')}
INDUSTRY_SERVICES = MANUFACTURING_SERVICES | LABORATORY_SERVICES | REACTION_SERVICES | {SERVICE_INDUSTRY}
META_SERVICES = {SERVICE_INDUSTRY,
 SERVICE_MANUFACTURING,
 SERVICE_LABORATORY,
 SERVICE_REACTIONS}
ONLINE_SERVICES_UNRESTRICTED_ACCESS = {SERVICE_FITTING, SERVICE_DOCKING}
ONLINE_SERVICES = ONLINE_SERVICES_UNRESTRICTED_ACCESS.union({SERVICE_REPAIR, SERVICE_INSURANCE, SERVICE_OFFICES})
STRUCTURES_WITHOUT_ONLINE_SERVICES = [inventorycommon.const.typeUpwellSmallStargate,
 inventorycommon.const.typeUpwellCynosuralSystemJammer,
 inventorycommon.const.typeUpwellCynosuralBeacon,
 inventorycommon.const.typeUpwellAutoMoonMiner]
SERVICES_THAT_OFFLINE_IF_STRUCTURE_TOO_CLOSE = [SERVICE_JUMP_BRIDGE, SERVICE_CYNO_JAMMER]
SERVICE_STATE_ONLINE = 1
SERVICE_STATE_OFFLINE = 2
SERVICE_STATE_CLEANUP = 3
_SERVICE_LABELS = {SERVICE_DOCKING: 'UI/StructureSettings/ServiceDocking',
 SERVICE_FITTING: 'UI/StructureSettings/ServiceFitting',
 SERVICE_OFFICES: 'UI/StructureSettings/ServiceCorpOffices',
 SERVICE_REPROCESSING: 'UI/StructureSettings/ServiceReprocessing',
 SERVICE_MARKET: 'UI/StructureSettings/ServiceMarket',
 SERVICE_MEDICAL: 'UI/StructureSettings/ServiceCloneBay',
 SERVICE_MISSION: 'UI/Station/Lobby/Agents',
 SERVICE_REPAIR: 'UI/Station/Repairshop',
 SERVICE_INSURANCE: 'UI/Station/Insurance',
 SERVICE_JUMP_CLONE: 'UI/StructureSettings/ServiceCloneBay',
 SERVICE_LOYALTY_STORE: 'UI/Station/LPStore',
 SERVICE_FACTION_WARFARE: 'UI/Station/MilitiaOffice',
 SERVICE_SECURITY_OFFICE: 'UI/Station/SecurityOffice',
 SERVICE_INDUSTRY: 'UI/StructureSettings/ServiceIndustry',
 SERVICE_MANUFACTURING: 'UI/StructureSettings/ServiceManufacturing',
 SERVICE_MANUFACTURING_BASIC: 'UI/StructureSettings/ServiceManufacturingBasic',
 SERVICE_MANUFACTURING_CAPITAL: 'UI/StructureSettings/ServiceManufacturingCapital',
 SERVICE_MANUFACTURING_SUPERCAPITAL: 'UI/StructureSettings/ServiceManufacturingSuperCapital',
 SERVICE_LABORATORY: 'UI/StructureSettings/ServiceResearch',
 SERVICE_LABORATORY_COPYING: 'UI/StructureSettings/ServiceBlueprintCopying',
 SERVICE_LABORATORY_INVENTION: 'UI/StructureSettings/ServiceInvention',
 SERVICE_LABORATORY_RESEARCH_TIME: 'UI/StructureSettings/ServiceResearchTimeEfficiency',
 SERVICE_LABORATORY_RESEARCH_MATERIAL: 'UI/StructureSettings/ServiceResearchMaterialEfficiency',
 SERVICE_REACTIONS: 'UI/StructureSettings/ServiceReactions',
 SERVICE_REACTIONS_HYBRID: 'UI/StructureSettings/ServiceReactionsHybrid',
 SERVICE_REACTIONS_COMPOSITE: 'UI/StructureSettings/ServiceReactionsComposite',
 SERVICE_REACTIONS_BIOCHEMICAL: 'UI/StructureSettings/ServiceReactionsBiochemical',
 SERVICE_MOONMINING: 'UI/Moonmining/MoonDrillService',
 SERVICE_JUMP_BRIDGE: 'UI/StructureSettings/ServiceJumpBridge',
 SERVICE_CYNO_BEACON: 'UI/StructureSettings/ServiceCynoBeacon',
 SERVICE_CYNO_JAMMER: 'UI/StructureSettings/ServiceCynoJammer',
 SERVICE_AUTOMOONMINING: 'UI/Moonmining/AutoMoonDrillService'}

def GetServiceLabel(serviceID):
    return _SERVICE_LABELS.get(serviceID)


_SERVICE_ICONS = {SERVICE_DOCKING: 'res:/ui/Texture/WindowIcons/docking.png',
 SERVICE_FITTING: 'res:/ui/Texture/WindowIcons/fitting.png',
 SERVICE_OFFICES: 'res:/ui/Texture/WindowIcons/corporation.png',
 SERVICE_REPROCESSING: 'res:/ui/Texture/WindowIcons/Reprocess.png',
 SERVICE_MARKET: 'res:/ui/Texture/WindowIcons/market.png',
 SERVICE_MEDICAL: 'res:/ui/Texture/WindowIcons/cloneBay.png',
 SERVICE_JUMP_CLONE: 'res:/ui/Texture/WindowIcons/cloneBay.png',
 SERVICE_INDUSTRY: 'res:/ui/Texture/WindowIcons/Industry.png',
 SERVICE_MANUFACTURING: 'res:/ui/Texture/WindowIcons/Industry.png',
 SERVICE_LABORATORY: 'res:/ui/Texture/WindowIcons/research.png',
 SERVICE_REACTIONS: 'res:/ui/Texture/WindowIcons/reactions.png'}

def GetServiceIcon(serviceID):
    if serviceID in LABORATORY_SERVICES:
        return _SERVICE_ICONS[SERVICE_LABORATORY]
    if serviceID in MANUFACTURING_SERVICES:
        return _SERVICE_ICONS[SERVICE_INDUSTRY]
    if serviceID in REACTION_SERVICES:
        return _SERVICE_ICONS[SERVICE_REACTIONS]
    return _SERVICE_ICONS.get(serviceID)


SERVICES_ACCESS_SETTINGS = {SERVICE_FITTING: structures.SETTING_HOUSING_CAN_DOCK,
 SERVICE_DOCKING: structures.SETTING_HOUSING_CAN_DOCK,
 SERVICE_OFFICES: structures.SETTING_CORP_RENT_OFFICE,
 SERVICE_REPROCESSING: structures.SETTING_REPROCESSING_TAX,
 SERVICE_MARKET: structures.SETTING_MARKET_TAX,
 SERVICE_MEDICAL: structures.SETTING_CLONINGBAY_TAX,
 SERVICE_INDUSTRY: structures.SETTING_NONE,
 SERVICE_INSURANCE: structures.SETTING_HOUSING_CAN_DOCK,
 SERVICE_REPAIR: structures.SETTING_HOUSING_CAN_DOCK,
 SERVICE_MOONMINING: structures.SETTING_DEFENSE_CAN_CONTROL_STRUCTURE,
 SERVICE_JUMP_BRIDGE: structures.SETTING_JUMP_BRIDGE_ACTIVATION,
 SERVICE_CYNO_BEACON: structures.SETTING_CYNO_BEACON,
 SERVICE_MANUFACTURING: structures.SETTING_NONE,
 SERVICE_MANUFACTURING_BASIC: structures.SETTING_MANUFACTURING_TAX,
 SERVICE_MANUFACTURING_CAPITAL: structures.SETTING_MANUFACTURING_CAPITAL_TAX,
 SERVICE_MANUFACTURING_SUPERCAPITAL: structures.SETTING_MANUFACTURING_SUPERCAPITAL_TAX,
 SERVICE_LABORATORY: structures.SETTING_NONE,
 SERVICE_LABORATORY_RESEARCH_TIME: structures.SETTING_RESEARCH_TAX,
 SERVICE_LABORATORY_RESEARCH_MATERIAL: structures.SETTING_RESEARCH_TAX,
 SERVICE_LABORATORY_COPYING: structures.SETTING_RESEARCH_TAX,
 SERVICE_LABORATORY_INVENTION: structures.SETTING_INVENTION_TAX,
 SERVICE_REACTIONS: structures.SETTING_NONE,
 SERVICE_REACTIONS_COMPOSITE: structures.SETTING_REACTION_COMPOSITE_TAX,
 SERVICE_REACTIONS_BIOCHEMICAL: structures.SETTING_REACTION_BIOCHEMICAL_TAX,
 SERVICE_REACTIONS_HYBRID: structures.SETTING_REACTION_HYBRID_TAX,
 SERVICE_LOYALTY_STORE: structures.SETTING_HOUSING_CAN_DOCK,
 SERVICE_AUTOMOONMINING: structures.SETTING_AUTOMOONMINING}
SERVICES_FROM_ACCESS_SETTINGS = {settingID:[ serviceID for serviceID, settingID2 in SERVICES_ACCESS_SETTINGS.iteritems() if settingID2 == settingID ] for settingID in SERVICES_ACCESS_SETTINGS.itervalues()}

def GetServiceID(activityID, productTypeID = None, productGroupID = None):
    if activityID in (industry.MANUFACTURING, industry.REACTION):
        if productGroupID is None:
            productGroupID = evetypes.GetGroupID(productTypeID)
    if activityID == industry.MANUFACTURING:
        if productGroupID in inventorycommon.const.superCapitalShipsGroups:
            return structures.SERVICE_MANUFACTURING_SUPERCAPITAL
        if productGroupID in inventorycommon.const.capitalShipsGroups:
            return structures.SERVICE_MANUFACTURING_CAPITAL
        return structures.SERVICE_MANUFACTURING_BASIC
    if activityID == industry.REACTION:
        if productGroupID in {inventorycommon.const.groupBiochemicalMaterial, inventorycommon.const.groupMolecularForgedMaterials}:
            return structures.SERVICE_REACTIONS_BIOCHEMICAL
        if productGroupID == inventorycommon.const.groupHybridPolymers:
            return structures.SERVICE_REACTIONS_HYBRID
        if productGroupID in inventorycommon.const.compositeReactionGroups:
            return structures.SERVICE_REACTIONS_COMPOSITE
        return structures.SERVICE_REACTIONS
    if activityID == industry.RESEARCH_MATERIAL:
        return structures.SERVICE_LABORATORY_RESEARCH_MATERIAL
    if activityID == industry.RESEARCH_TIME:
        return structures.SERVICE_LABORATORY_RESEARCH_TIME
    if activityID == industry.COPYING:
        return structures.SERVICE_LABORATORY_COPYING
    if activityID == industry.INVENTION:
        return structures.SERVICE_LABORATORY_INVENTION
    raise RuntimeError('Unknown industry activity %d for product type %d' % (activityID, productTypeID))


def GetActivityID(serviceID):
    if serviceID in MANUFACTURING_SERVICES:
        return industry.MANUFACTURING
    if serviceID in REACTION_SERVICES:
        return industry.REACTION
    if serviceID == SERVICE_LABORATORY_RESEARCH_MATERIAL:
        return industry.RESEARCH_MATERIAL
    if serviceID == SERVICE_LABORATORY_RESEARCH_TIME:
        return industry.RESEARCH_TIME
    if serviceID == SERVICE_LABORATORY_COPYING:
        return industry.COPYING
    if serviceID == SERVICE_LABORATORY_INVENTION:
        return industry.INVENTION


_MODULES_TO_SERVICES = {inventorycommon.const.typeStandupMarketHub: (SERVICE_MARKET,),
 inventorycommon.const.typeStandupCloningCenter: (SERVICE_MEDICAL,),
 inventorycommon.const.typeStandupReprocessingFacility: (SERVICE_REPROCESSING,),
 inventorycommon.const.typeStandupResearchLab: (SERVICE_LABORATORY_COPYING, SERVICE_LABORATORY_RESEARCH_MATERIAL, SERVICE_LABORATORY_RESEARCH_TIME),
 inventorycommon.const.typeStandupInventionLab: (SERVICE_LABORATORY_INVENTION,),
 inventorycommon.const.typeStandupManufacturingPlant: (SERVICE_MANUFACTURING_BASIC,),
 inventorycommon.const.typeStandupCapitalShipYard: (SERVICE_MANUFACTURING_CAPITAL,),
 inventorycommon.const.typeStandupSuperCapitalShipYard: (SERVICE_MANUFACTURING_SUPERCAPITAL, SERVICE_MANUFACTURING_CAPITAL),
 inventorycommon.const.typeStandupHyasyodaResearchLab: (SERVICE_LABORATORY_COPYING, SERVICE_LABORATORY_RESEARCH_MATERIAL, SERVICE_LABORATORY_RESEARCH_TIME),
 inventorycommon.const.typeStandupHybridReactor: (SERVICE_REACTIONS_HYBRID,),
 inventorycommon.const.typeStandupCompositeReactor: (SERVICE_REACTIONS_COMPOSITE,),
 inventorycommon.const.typeStandupBiochemicalReactor: (SERVICE_REACTIONS_BIOCHEMICAL,),
 inventorycommon.const.typeStandupMoonDrill: (SERVICE_MOONMINING,),
 inventorycommon.const.typeStandupStargateEngine: (SERVICE_JUMP_BRIDGE,),
 inventorycommon.const.typeStandupCynosuralGeneratorI: (SERVICE_CYNO_BEACON,),
 inventorycommon.const.typeStandupCynosuralJammerI: (SERVICE_CYNO_JAMMER,),
 inventorycommon.const.typeStandupLoyaltyStore: (SERVICE_LOYALTY_STORE,),
 inventorycommon.const.typeStandupMetenoxMoonDrill: (SERVICE_AUTOMOONMINING,)}

def GetServiceIDsFromModuleType(typeID):
    return _MODULES_TO_SERVICES.get(typeID, ())
