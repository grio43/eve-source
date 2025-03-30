#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\infoConst.py
from eve.common.lib import appConst as const
TYPE_CHARACTER = 1
TYPE_CORPORATION = 2
TYPE_ALLIANCE = 3
TYPE_FACTION = 4
TYPE_BOOKMARK = 5
TYPE_SHIP = 6
TYPE_MODULE = 7
TYPE_CHARGE = 8
TYPE_BLUEPRINT = 9
TYPE_REACTION = 10
TYPE_DRONE = 11
TYPE_SECURITYTAG = 12
TYPE_PLANETCOMMODITY = 13
TYPE_APPAREL = 14
TYPE_GENERICITEM = 15
TYPE_SKINLICENSE = 16
TYPE_SKINMATERIAL = 17
TYPE_SKINDESCRIPTION = 18
TYPE_PLEX = 59
TYPE_AURUM = 2833
TYPE_SKILLINJECTOR = 66
TYPE_SKILLEXTRACTOR = 67
TYPE_STRUCTURE_MODULE = 68
TYPE_FIGHTER = 69
TYPE_MUTATOR = 71
TYPE_SEQUENCE_BINDERS = 4725
TYPE_DESIGN_ELEMENTS = 4726
TYPE_STARGATE = 30
TYPE_CONTROLTOWER = 31
TYPE_STATION = 33
TYPE_STRUCTURE = 34
TYPE_PLANETPIN = 35
TYPE_CUSTOMSOFFICE = 38
TYPE_STRUCTUREUPGRADE = 39
TYPE_PLANET = 40
TYPE_WORMHOLE = 41
TYPE_CONTAINER = 50
TYPE_SECURECONTAINER = 51
TYPE_CELESTIAL = 52
TYPE_ENTITY = 53
TYPE_LANDMARK = 54
TYPE_ASTEROID = 55
TYPE_DEPLOYABLE = 56
TYPE_ENTOSISNODE = 57
TYPE_COMMANDNODEBEACON = 58
TYPE_STRUCTURE_OLD = 70
TYPE_RANK = 60
TYPE_MEDAL = 61
TYPE_RIBBON = 62
TYPE_CERTIFICATE = 63
TYPE_SKILL = 65
TYPE_EXPERT_SYSTEM = 78
TYPE_SKYHOOK = 79
TYPE_UNKNOWN = 100
infoTypeByTypeID = {const.typeBookmark: TYPE_BOOKMARK,
 const.typeRank: TYPE_RANK,
 const.typeMedal: TYPE_MEDAL,
 const.typeRibbon: TYPE_RIBBON,
 const.typeCertificate: TYPE_CERTIFICATE,
 const.typeSkinMaterial: TYPE_SKINMATERIAL,
 const.typeEntosisCommandNode: TYPE_ENTOSISNODE,
 const.typeCommandNodeBeacon: TYPE_COMMANDNODEBEACON,
 const.typePlex: TYPE_PLEX,
 const.typeAurumToken: TYPE_AURUM,
 const.typeSkillInjector: TYPE_SKILLINJECTOR,
 const.typeSkillExtractor: TYPE_SKILLEXTRACTOR}
infoTypeByGroupID = {const.groupCharacter: TYPE_CHARACTER,
 const.groupCorporation: TYPE_CORPORATION,
 const.groupAlliance: TYPE_ALLIANCE,
 const.groupFaction: TYPE_FACTION,
 const.groupSecurityTags: TYPE_SECURITYTAG,
 const.groupStargate: TYPE_STARGATE,
 const.groupControlTower: TYPE_CONTROLTOWER,
 const.groupPlanetaryCustomsOffices: TYPE_CUSTOMSOFFICE,
 const.groupPlanet: TYPE_PLANET,
 const.groupWormhole: TYPE_WORMHOLE,
 const.groupMobileWarpDisruptor: TYPE_DEPLOYABLE,
 const.groupLargeCollidableStructure: TYPE_CELESTIAL,
 const.groupTemporaryCollidableStructure: TYPE_CELESTIAL,
 const.groupDeadspaceOverseersStructure: TYPE_CELESTIAL,
 const.groupHarvestableCloud: TYPE_ASTEROID,
 const.groupCompressedGas: TYPE_ASTEROID,
 const.groupSecureCargoContainer: TYPE_SECURECONTAINER,
 const.groupAuditLogSecureContainer: TYPE_SECURECONTAINER,
 const.groupLandmark: TYPE_LANDMARK,
 const.groupStation: TYPE_STATION,
 const.groupCargoContainer: TYPE_CONTAINER,
 const.groupFreightContainer: TYPE_CONTAINER,
 const.groupOrbitalConstructionPlatforms: TYPE_STRUCTURE_OLD,
 const.groupSkillInjectors: TYPE_SKILLINJECTOR,
 const.groupMutaplasmid: TYPE_MUTATOR,
 const.groupSkyhook: TYPE_SKYHOOK,
 const.groupSequenceBinders: TYPE_SEQUENCE_BINDERS,
 const.groupShipSkinDesignComponents: TYPE_DESIGN_ELEMENTS}
for skinGroup in const.SHIP_SKIN_GROUPS:
    infoTypeByGroupID[skinGroup] = TYPE_SKINLICENSE

infoTypeByCategoryID = {const.categoryShip: TYPE_SHIP,
 const.categoryModule: TYPE_MODULE,
 const.categorySubSystem: TYPE_MODULE,
 const.categoryStructureModule: TYPE_STRUCTURE_MODULE,
 const.categoryCharge: TYPE_CHARGE,
 const.categoryBlueprint: TYPE_BLUEPRINT,
 const.categoryAncientRelic: TYPE_BLUEPRINT,
 const.categoryReaction: TYPE_REACTION,
 const.categoryDrone: TYPE_DRONE,
 const.categoryFighter: TYPE_FIGHTER,
 const.categoryApparel: TYPE_APPAREL,
 const.categoryImplant: TYPE_GENERICITEM,
 const.categoryAccessories: TYPE_GENERICITEM,
 const.categoryShipSkin: TYPE_GENERICITEM,
 const.categoryStarbase: TYPE_STRUCTURE_OLD,
 const.categorySovereigntyStructure: TYPE_STRUCTURE_OLD,
 const.categoryStructure: TYPE_STRUCTURE,
 const.categoryInfrastructureUpgrade: TYPE_STRUCTUREUPGRADE,
 const.categoryEntity: TYPE_ENTITY,
 const.categoryPlanetaryInteraction: TYPE_PLANETPIN,
 const.categoryPlanetaryResources: TYPE_PLANETCOMMODITY,
 const.categoryPlanetaryCommodities: TYPE_PLANETCOMMODITY,
 const.categorySkill: TYPE_SKILL,
 const.categoryAsteroid: TYPE_ASTEROID,
 const.categoryCelestial: TYPE_CELESTIAL,
 const.categoryDeployable: TYPE_DEPLOYABLE,
 const.categoryExpertSystems: TYPE_EXPERT_SYSTEM}
ownedGroups = (const.groupWreck,
 const.groupSecureCargoContainer,
 const.groupAuditLogSecureContainer,
 const.groupCargoContainer,
 const.groupFreightContainer,
 const.groupSentryGun,
 const.groupDestructibleSentryGun,
 const.groupMobileSentryGun,
 const.groupDeadspaceOverseersSentry,
 const.groupPlanet)
ownedCategories = (const.categoryStarbase,
 const.categorySovereigntyStructure,
 const.categoryOrbital,
 const.categoryDeployable,
 const.categoryStructure)
TAB_ATTIBUTES = 1
TAB_CORPMEMBERS = 2
TAB_NEIGHBORS = 3
TAB_CHILDREN = 4
TAB_FITTING = 5
TAB_CERTREQUIREMENTS = 6
TAB_REQUIREMENTS = 7
TAB_CERTRECOMMENDEDFOR = 10
TAB_VARIATIONS = 11
TAB_LEGALITY = 13
TAB_JUMPS = 14
TAB_MODULES = 15
TAB_ORBITALBODIES = 16
TAB_SYSTEMS = 17
TAB_LOCATION = 18
TAB_AGENTINFO = 19
TAB_AGENTS = 20
TAB_ROUTE = 21
TAB_INSURANCE = 22
TAB_SERVICES = 23
TAB_STANDINGS = 24
TAB_DECORATIONS = 25
TAB_MEDALS = 27
TAB_RANKS = 28
TAB_MEMBEROFCORPS = 29
TAB_MARKETACTIVITY = 30
TAB_DATA = 31
TAB_EMPLOYMENTHISTORY = 40
TAB_ALLIANCEHISTORY = 53
TAB_FUELREQ = 41
TAB_MATERIALREQ = 42
TAB_UPGRADEMATERIALREQ = 43
TAB_PLANETCONTROL = 44
TAB_NOTES = 46
TAB_DOGMA = 47
TAB_MEMBERS = 48
TAB_UNKNOWN = 49
TAB_HIERARCHY = 50
TAB_SCHEMATICS = 51
TAB_PLANETARYPRODUCTION = 52
TAB_WARHISTORY = 54
TAB_REQUIREDFOR = 55
TAB_MASTERY = 56
TAB_CERTSKILLS = 57
TAB_TRAITS = 58
TAB_DESCRIPTION = 59
TAB_BIO = 60
TAB_STATIONS = 61
TAB_INDUSTRY = 62
TAB_ITEMINDUSTRY = 63
TAB_USEDWITH = 64
TAB_SKINLICENSE = 65
TAB_SKINMATERIAL = 66
TAB_SHIPAVAILABLESKINLICENSES = 67
TAB_SOV = 69
TAB_SOV_CONSTELLATION = 70
TAB_FIGHTER_ABILITIES = 71
TAB_DESCRIPTION_DYNAMIC = 72
TAB_STRUCTURES = 73
TAB_MUTATOR_USED_WITH = 74
TAB_PLANETARYPRODUCTIONPLANET = 75
TAB_GATE_ICONS = 76
TAB_WARHQ = 77
TAB_EXPERT_SYSTEM_SKILLS = 78
TAB_EXPERT_SYSTEM_SHIPS = 79
TAB_FW = 80
TAB_TRADES = 81
DATA_BUTTONS = 'buttons'
INFO_TABS = ((TAB_TRAITS, [], 'UI/InfoWindow/TabNames/Traits'),
 (TAB_BIO, [], 'UI/InfoWindow/TabNames/Bio'),
 (TAB_INDUSTRY, [], 'UI/InfoWindow/TabNames/Industry'),
 (TAB_DESCRIPTION_DYNAMIC, [], 'UI/InfoWindow/TabNames/Bio'),
 (TAB_DESCRIPTION, [], 'UI/InfoWindow/TabNames/Description'),
 (TAB_EXPERT_SYSTEM_SHIPS, [], 'UI/InfoWindow/TabNames/ExpertSystemShips'),
 (TAB_EXPERT_SYSTEM_SKILLS, [], 'UI/InfoWindow/TabNames/ExpertSystemSkills'),
 (TAB_ATTIBUTES, [], 'UI/InfoWindow/TabNames/Attributes'),
 (TAB_FIGHTER_ABILITIES, [], 'UI/InfoWindow/TabNames/Abilities'),
 (TAB_CORPMEMBERS, [], 'UI/InfoWindow/TabNames/CorpMembers'),
 (TAB_NEIGHBORS, [], 'UI/InfoWindow/TabNames/Neighbors'),
 (TAB_CHILDREN, [], 'UI/InfoWindow/TabNames/Children'),
 (TAB_FITTING, [], 'UI/InfoWindow/TabNames/Fitting'),
 (TAB_REQUIREMENTS, [], 'UI/InfoWindow/TabNames/Requirements'),
 (TAB_CERTSKILLS, [], 'UI/InfoWindow/TabNames/Levels'),
 (TAB_CERTRECOMMENDEDFOR, [], 'UI/InfoWindow/TabNames/RecommendedFor'),
 (TAB_MASTERY, [], 'UI/InfoWindow/TabNames/Mastery'),
 (TAB_USEDWITH, [], 'UI/InfoWindow/TabNames/UsedWith'),
 (TAB_VARIATIONS, [], 'UI/InfoWindow/TabNames/Variations'),
 (TAB_LEGALITY, [], 'UI/InfoWindow/TabNames/Legality'),
 (TAB_JUMPS, [], 'UI/InfoWindow/TabNames/Jumps'),
 (TAB_GATE_ICONS, [], 'UI/InfoWindow/TabNames/GateIcons'),
 (TAB_MODULES, [], 'UI/InfoWindow/TabNames/Modules'),
 (TAB_ORBITALBODIES, [], 'UI/InfoWindow/TabNames/OrbitalBodies'),
 (TAB_STATIONS, [], 'UI/Common/LocationTypes/Stations'),
 (TAB_STRUCTURES, [], 'UI/InfoWindow/TabNames/Structures'),
 (TAB_SYSTEMS, [], 'UI/InfoWindow/TabNames/Systems'),
 (TAB_LOCATION, [], 'UI/InfoWindow/TabNames/Location'),
 (TAB_AGENTINFO, [], 'UI/InfoWindow/TabNames/AgentInfo'),
 (TAB_AGENTS, [], 'UI/InfoWindow/TabNames/Agents'),
 (TAB_ROUTE, [], 'UI/InfoWindow/TabNames/Route'),
 (TAB_INSURANCE, [], 'UI/InfoWindow/TabNames/Insurance'),
 (TAB_SERVICES, [], 'UI/InfoWindow/TabNames/Services'),
 (TAB_STANDINGS, [], 'UI/InfoWindow/TabNames/Standings'),
 (TAB_DECORATIONS, [(TAB_MEDALS, [], 'UI/InfoWindow/TabNames/Medals'), (TAB_RANKS, [], 'UI/InfoWindow/TabNames/Ranks')], 'UI/InfoWindow/TabNames/Decorations'),
 (TAB_MEMBEROFCORPS, [], 'UI/InfoWindow/TabNames/MemberCorps'),
 (TAB_MARKETACTIVITY, [], 'UI/InfoWindow/TabNames/MarketActivity'),
 (TAB_DATA, [], 'UI/InfoWindow/TabNames/Data'),
 (TAB_EMPLOYMENTHISTORY, [], 'UI/InfoWindow/TabNames/EmploymentHistory'),
 (TAB_ALLIANCEHISTORY, [], 'UI/InfoWindow/TabNames/AllianceHistory'),
 (TAB_WARHISTORY, [], 'UI/InfoWindow/TabNames/WarHistory'),
 (TAB_FUELREQ, [], 'UI/InfoWindow/TabNames/FuelRequirements'),
 (TAB_MATERIALREQ, [], 'UI/InfoWindow/TabNames/MaterialRequirements'),
 (TAB_UPGRADEMATERIALREQ, [], 'UI/InfoWindow/TabNames/UpgradeRequirements'),
 (TAB_PLANETCONTROL, [], 'UI/InfoWindow/TabNames/PlanetControl'),
 (TAB_NOTES, [], 'UI/InfoWindow/TabNames/Notes'),
 (TAB_DOGMA, [], 'UI/InfoWindow/TabNames/Dogma'),
 (TAB_MEMBERS, [], 'UI/InfoWindow/TabNames/Members'),
 (TAB_UNKNOWN, [], 'UI/InfoWindow/TabNames/Unknown'),
 (TAB_HIERARCHY, [], 'UI/InfoWindow/TabNames/Hierarchy'),
 (TAB_SCHEMATICS, [], 'UI/InfoWindow/TabNames/Schematics'),
 (TAB_PLANETARYPRODUCTION, [], 'UI/InfoWindow/TabNames/PlanetaryProduction'),
 (TAB_PLANETARYPRODUCTIONPLANET, [], 'UI/InfoWindow/TabNames/PlanetaryProduction'),
 (TAB_REQUIREDFOR, [], 'UI/InfoWindow/TabNames/RequiredFor'),
 (TAB_ITEMINDUSTRY, [], 'UI/InfoWindow/TabNames/Industry'),
 (TAB_SKINLICENSE, [], 'UI/InfoWindow/TabNames/Attributes'),
 (TAB_SKINMATERIAL, [], 'UI/InfoWindow/TabNames/Attributes'),
 (TAB_SHIPAVAILABLESKINLICENSES, [], 'UI/InfoWindow/TabNames/Skins'),
 (TAB_SOV, [], 'UI/Sovereignty/Sovereignty'),
 (TAB_SOV_CONSTELLATION, [], 'UI/Sovereignty/Sovereignty'),
 (TAB_MUTATOR_USED_WITH, [], 'UI/InfoWindow/TabNames/UsedWith'),
 (TAB_WARHQ, [], 'UI/InfoWindow/TabNames/WarHQ'),
 (TAB_FW, [], 'UI/InfoWindow/TabNames/FactionalWarfare'),
 (TAB_TRADES, [], 'UI/InfoWindow/TabNames/Trades'))
