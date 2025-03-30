#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\structures\settings.py
CATEGORY_HULL_DEFENSE = 1003
CATEGORY_HULL_DOCKING = 1004
CATEGORY_MODULE_MARKET = 1008
CATEGORY_HULL_CORPOFFICE = 1009
CATEGORY_MODULE_REPROCESSING = 1010
CATEGORY_MODULE_CLONINGBAY = 1011
CATEGORY_MODULE_INDUSTRY = 1012
CATEGORY_MODULE_NAVIGATION = 1013
SETTING_NONE = 0
SETTING_REPROCESSING_TAX = 3
SETTING_MARKET_TAX = 4
SETTING_DEFENSE_CAN_CONTROL_STRUCTURE = 17
SETTING_HOUSING_CAN_DOCK = 19
SETTING_CORP_RENT_OFFICE = 20
SETTING_CLONINGBAY_TAX = 23
SETTING_INDUSTRY_TAX = 24
SETTING_REACTION_BIOCHEMICAL_TAX = 26
SETTING_REACTION_HYBRID_TAX = 27
SETTING_REACTION_COMPOSITE_TAX = 28
SETTING_MANUFACTURING_TAX = 29
SETTING_MANUFACTURING_CAPITAL_TAX = 30
SETTING_MANUFACTURING_SUPERCAPITAL_TAX = 31
SETTING_RESEARCH_TAX = 32
SETTING_INVENTION_TAX = 33
SETTING_JUMP_BRIDGE_ACTIVATION = 34
SETTING_CYNO_BEACON = 35
SETTING_AUTOMOONMINING = 36
CATEGORIES_BY_NAME = {name:value for name, value in locals().items() if name.startswith('CATEGORY_')}
SETTINGS_BY_NAME = {name:value for name, value in locals().items() if name.startswith('SETTING_')}
SETTINGS_TYPE_NONE = 1
SETTINGS_TYPE_BOOL = 2
SETTINGS_TYPE_INT = 3
SETTINGS_TYPE_FLOAT = 4
SETTINGS_TYPE_PERCENTAGE = 5
SETTINGS_TYPE_ISK = 6
SETTINGS_TYPES = {value:name for name, value in locals().items() if name.startswith('SETTINGS_TYPE_')}
SETTINGS_BY_CATEGORY = {CATEGORY_HULL_DEFENSE: (SETTING_DEFENSE_CAN_CONTROL_STRUCTURE,),
 CATEGORY_HULL_DOCKING: (SETTING_HOUSING_CAN_DOCK,),
 CATEGORY_HULL_CORPOFFICE: (SETTING_CORP_RENT_OFFICE,),
 CATEGORY_MODULE_MARKET: (SETTING_MARKET_TAX,),
 CATEGORY_MODULE_CLONINGBAY: (SETTING_CLONINGBAY_TAX,),
 CATEGORY_MODULE_REPROCESSING: (SETTING_REPROCESSING_TAX,),
 CATEGORY_MODULE_INDUSTRY: (SETTING_REACTION_BIOCHEMICAL_TAX,
                            SETTING_REACTION_HYBRID_TAX,
                            SETTING_REACTION_COMPOSITE_TAX,
                            SETTING_MANUFACTURING_TAX,
                            SETTING_MANUFACTURING_CAPITAL_TAX,
                            SETTING_MANUFACTURING_SUPERCAPITAL_TAX,
                            SETTING_RESEARCH_TAX,
                            SETTING_INVENTION_TAX,
                            SETTING_AUTOMOONMINING),
 CATEGORY_MODULE_NAVIGATION: (SETTING_JUMP_BRIDGE_ACTIVATION, SETTING_CYNO_BEACON)}
CATEGORY_LABELS = {CATEGORY_HULL_DEFENSE: 'UI/StructureSettings/ServiceDefense',
 CATEGORY_HULL_DOCKING: 'UI/StructureSettings/ServiceDocking',
 CATEGORY_HULL_CORPOFFICE: 'UI/StructureSettings/ServiceCorpOffices',
 CATEGORY_MODULE_MARKET: 'UI/StructureSettings/ServiceMarket',
 CATEGORY_MODULE_CLONINGBAY: 'UI/StructureSettings/ServiceCloneBay',
 CATEGORY_MODULE_REPROCESSING: 'UI/StructureSettings/ServiceReprocessing',
 CATEGORY_MODULE_INDUSTRY: 'UI/StructureSettings/ServiceIndustry',
 CATEGORY_MODULE_NAVIGATION: 'UI/StructureSettings/ServiceNavigation'}
CATEGORY_TEXTURES = {CATEGORY_HULL_DEFENSE: 'res:/UI/Texture/classes/ProfileSettings/defense.png',
 CATEGORY_HULL_DOCKING: 'res:/UI/Texture/classes/ProfileSettings/docking.png',
 CATEGORY_HULL_CORPOFFICE: 'res:/UI/Texture/classes/ProfileSettings/corpOffice.png',
 CATEGORY_MODULE_MARKET: 'res:/UI/Texture/classes/ProfileSettings/market.png',
 CATEGORY_MODULE_CLONINGBAY: 'res:/UI/Texture/classes/ProfileSettings/cloneBay.png',
 CATEGORY_MODULE_REPROCESSING: 'res:/UI/Texture/classes/ProfileSettings/reprocess.png',
 CATEGORY_MODULE_INDUSTRY: 'res:/UI/Texture/classes/ProfileSettings/industry.png',
 CATEGORY_MODULE_NAVIGATION: 'res:/UI/Texture/classes/ProfileSettings/navigation.png'}
SETTINGS_TEXTURES = {SETTING_MANUFACTURING_TAX: 'res:/UI/Texture/classes/Industry/manufacturing.png',
 SETTING_MANUFACTURING_CAPITAL_TAX: 'res:/UI/Texture/classes/Industry/manufacturing.png',
 SETTING_MANUFACTURING_SUPERCAPITAL_TAX: 'res:/UI/Texture/classes/Industry/manufacturing.png',
 SETTING_RESEARCH_TAX: 'res:/UI/Texture/classes/Industry/copying.png',
 SETTING_INVENTION_TAX: 'res:/UI/Texture/classes/Industry/invention.png',
 SETTING_REACTION_BIOCHEMICAL_TAX: 'res:/UI/Texture/classes/Industry/reaction.png',
 SETTING_REACTION_HYBRID_TAX: 'res:/UI/Texture/classes/Industry/reaction.png',
 SETTING_REACTION_COMPOSITE_TAX: 'res:/UI/Texture/classes/Industry/reaction.png'}

class StructureSettingObject(object):

    def __init__(self, settingID, labelPath, descLabelPath, cantAccessError, valueType, hasGroups, valueRange = None, columnLabelPath = None, decimals = None):
        self.settingID = settingID
        self.labelPath = labelPath
        self.descLabelPath = descLabelPath
        self.cantAccessError = cantAccessError
        self.valueType = valueType
        self.hasGroups = hasGroups
        self.valueRange = valueRange
        self.columnLabelPath = columnLabelPath
        self.decimals = decimals


MAX_CLONEBAY_COST = 100000000
MAX_CORPOFFICE_COST = 1000000000
MAX_TAX_PERCENTAGE = 50
MAX_INDUSTRY_TAX_PERCENTAGE = 10
MAX_ISK_TAX_PER_LO = 2000
MIN_MARKET_TAX_PERCENTAGE = 0.0
MAX_MARKET_TAX_PERCENTAGE = 11.5
INDUSTRY_DECIMALS = 2
ALL_SETTING_OBJECTS = [StructureSettingObject(SETTING_MARKET_TAX, 'UI/StructureSettings/MarketTax', 'UI/StructureSettings/SpecifyAllowedGroupsAndRate', 'StructureMarketDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(MIN_MARKET_TAX_PERCENTAGE, MAX_MARKET_TAX_PERCENTAGE)),
 StructureSettingObject(SETTING_DEFENSE_CAN_CONTROL_STRUCTURE, 'UI/StructureSettings/CanControlStructure', 'UI/StructureSettings/CanControlStructureDesc', 'StructureDefenseDenied', SETTINGS_TYPE_NONE, hasGroups=True),
 StructureSettingObject(SETTING_HOUSING_CAN_DOCK, 'UI/StructureSettings/DockingAccess', 'UI/StructureSettings/DockingAccessDesc', 'StructureDockingDenied', SETTINGS_TYPE_NONE, hasGroups=True),
 StructureSettingObject(SETTING_CORP_RENT_OFFICE, 'UI/StructureSettings/CorpOffice', 'UI/StructureSettings/CorpOfficeDesc', 'StructureCorpOfficesDenied', SETTINGS_TYPE_ISK, hasGroups=True, valueRange=(0, MAX_CORPOFFICE_COST)),
 StructureSettingObject(SETTING_CLONINGBAY_TAX, 'UI/StructureSettings/CloneBayTax', 'UI/StructureSettings/CloneBayTaxDesc', 'StructureCloneBayDenied', SETTINGS_TYPE_ISK, hasGroups=True, valueRange=(0, MAX_CLONEBAY_COST)),
 StructureSettingObject(SETTING_REPROCESSING_TAX, 'UI/StructureSettings/ReprocessingTax', 'UI/StructureSettings/ReprocessingTaxDesc', 'StructureReprocessingDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_TAX_PERCENTAGE)),
 StructureSettingObject(SETTING_REACTION_BIOCHEMICAL_TAX, 'UI/StructureSettings/ReactionsBiochemical', 'UI/StructureSettings/ReactionsBiochemicalDesc', 'StructureReactionBiochemicalDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_INDUSTRY_TAX_PERCENTAGE), decimals=INDUSTRY_DECIMALS),
 StructureSettingObject(SETTING_REACTION_COMPOSITE_TAX, 'UI/StructureSettings/ReactionsComposite', 'UI/StructureSettings/ReactionsCompositeDesc', 'StructureReactionCompositeDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_INDUSTRY_TAX_PERCENTAGE), decimals=INDUSTRY_DECIMALS),
 StructureSettingObject(SETTING_REACTION_HYBRID_TAX, 'UI/StructureSettings/ReactionsHybrid', 'UI/StructureSettings/ReactionsHybridDesc', 'StructureReactionHybridDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_INDUSTRY_TAX_PERCENTAGE), decimals=INDUSTRY_DECIMALS),
 StructureSettingObject(SETTING_MANUFACTURING_TAX, 'UI/StructureSettings/ManufacturingTax', 'UI/StructureSettings/ManufacturingTaxDesc', 'StructureManufacturingDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_INDUSTRY_TAX_PERCENTAGE), decimals=INDUSTRY_DECIMALS),
 StructureSettingObject(SETTING_MANUFACTURING_CAPITAL_TAX, 'UI/StructureSettings/ManufacturingCapitalTax', 'UI/StructureSettings/ManufacturingCapitalTaxDesc', 'StructureManufacturingCapitalDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_INDUSTRY_TAX_PERCENTAGE), decimals=INDUSTRY_DECIMALS),
 StructureSettingObject(SETTING_MANUFACTURING_SUPERCAPITAL_TAX, 'UI/StructureSettings/ManufacturingSuperCapitalTax', 'UI/StructureSettings/ManufacturingSuperCapitalTaxDesc', 'StructureManufacturingSuperCapitalDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_INDUSTRY_TAX_PERCENTAGE), decimals=INDUSTRY_DECIMALS),
 StructureSettingObject(SETTING_RESEARCH_TAX, 'UI/StructureSettings/ResearchTax', 'UI/StructureSettings/ResearchTaxDesc', 'StructureResearchDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_INDUSTRY_TAX_PERCENTAGE), decimals=INDUSTRY_DECIMALS),
 StructureSettingObject(SETTING_INVENTION_TAX, 'UI/StructureSettings/InventionTax', 'UI/StructureSettings/InventionTaxDesc', 'StructureInventionDenied', SETTINGS_TYPE_PERCENTAGE, hasGroups=True, valueRange=(0, MAX_INDUSTRY_TAX_PERCENTAGE), decimals=INDUSTRY_DECIMALS),
 StructureSettingObject(SETTING_JUMP_BRIDGE_ACTIVATION, 'UI/StructureSettings/CanActivateJumpBridge', 'UI/StructureSettings/CanActivateJumpBridgeDesc', 'ActivateJumpBridgeDenied', SETTINGS_TYPE_ISK, hasGroups=True, valueRange=(0, MAX_ISK_TAX_PER_LO)),
 StructureSettingObject(SETTING_CYNO_BEACON, 'UI/StructureSettings/CanConnectToCynoBeacon', 'UI/StructureSettings/CanConnectToCynoBeaconDesc', 'ConnectToCynoBeaconDenied', SETTINGS_TYPE_NONE, hasGroups=True),
 StructureSettingObject(SETTING_AUTOMOONMINING, 'UI/StructureSettings/CanAccessAutoMoonDrill', 'UI/StructureSettings/CanAccessAutoMoonDrillDesc', 'AccessToAutoMoonMinerDenied', SETTINGS_TYPE_NONE, hasGroups=True)]
CATEGORIES_HULL = [ value for name, value in CATEGORIES_BY_NAME.iteritems() if name.startswith('CATEGORY_HULL_') ]
CATEGORIES_MODULES = [ value for name, value in CATEGORIES_BY_NAME.iteritems() if name.startswith('CATEGORY_MODULE_') ]
SETTINGS_NAMES = {value:name for name, value in SETTINGS_BY_NAME.iteritems()}
SETTINGS_CATEGORY = {setting:service for service, settings in SETTINGS_BY_CATEGORY.iteritems() for setting in settings}
SETTING_OBJECT_BY_SETTINGID = {s.settingID:s for s in ALL_SETTING_OBJECTS}
SETTINGS_VALUE_HAS_GROUPS = {s.settingID for s in ALL_SETTING_OBJECTS if s.hasGroups}
SETTINGS_VALUE_TYPE = {s.settingID:s.valueType for s in ALL_SETTING_OBJECTS}
SETTINGS_LABELS = {s.settingID:s.labelPath for s in ALL_SETTING_OBJECTS}
SETTINGS_LABELS_DESC = {s.settingID:s.descLabelPath for s in ALL_SETTING_OBJECTS}
SETTING_ACCESS_ERRORS_BY_SETTING = {s.settingID:s.cantAccessError for s in ALL_SETTING_OBJECTS}
SETTINGS = set(SETTINGS_BY_NAME.values())

def GetAccessErrorLabel(settingID):
    return SETTING_ACCESS_ERRORS_BY_SETTING.get(settingID, 'StructureGenericSettingDenied')
