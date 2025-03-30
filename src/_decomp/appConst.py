#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\lib\appConst.py
import collections
from carbon.common.lib.const import *
from eve.common.lib.infoEventConst import *
from inventorycommon.const import *
from dogma.const import *
from crimewatch.const import *
from eveexceptions.const import *
from probescanning.const import *
from eve.common.script.util.notificationconst import *
from evefleet.const import *
from eveuniverse.security import securityClassZeroSec, securityClassLowSec, securityClassHighSec
from marketutil.const import *
FEMALE = 0
MALE = 1
NO_ACTIVITY = 0
INDUSTRY_MANUFACTURING = 101
INDUSTRY_RESEARCH_TIME = 102
INDUSTRY_RESEARCH_MATERIAL = 103
INDUSTRY_COPYING = 104
INDUSTRY_INVENTION = 105
INDUSTRY_REACTION = 106
HARVEST_MINING = 201
HARVEST_SALVAGING = 202
HARVEST_PLANETS = 203
charLockInTransferQueue = 1
charLockOnSale = 2
charLockNeedsRedeeming = 3
FROZEN_CHARACTER_STATES = (charLockOnSale, charLockNeedsRedeeming)
intervalEveUser = 10
ACT_IDX_START = 0
ACT_IDX_DURATION = 1
ACT_IDX_ENV = 2
ACT_IDX_REPEAT = 3
AU = 149597870700.0
LIGHTYEAR = 9460000000000000.0
GRIDSIZE = 7864320
ALSCActionNone = 0
ALSCActionAdd = 6
ALSCActionAssemble = 1
ALSCActionConfigure = 10
ALSCActionEnterPassword = 9
ALSCActionLock = 7
ALSCActionMove = 4
ALSCActionRepackage = 2
ALSCActionSetName = 3
ALSCActionSetPassword = 5
ALSCActionUnlock = 8
ALSCPasswordNeededToOpen = 1
ALSCPasswordNeededToLock = 2
ALSCPasswordNeededToUnlock = 4
ALSCPasswordNeededToViewAuditLog = 8
ALSCLockAddedItems = 16
CTPC_CHAT = 8
CTPC_MAIL = 9
CTPG_CASH = 6
CTPG_SHARES = 7
CTV_ADD = 1
CTV_COMMS = 5
CTV_GIVE = 4
CTV_REMOVE = 2
CTV_SET = 3
SCCPasswordTypeConfig = 2
SCCPasswordTypeGeneral = 1
agentTypeBasicAgent = 2
agentTypeEventMissionAgent = 8
agentTypeGenericStorylineMissionAgent = 6
agentTypeNonAgent = 1
agentTypeResearchAgent = 4
agentTypeCONCORDAgent = 5
agentTypeStorylineMissionAgent = 7
agentTypeTutorialAgent = 3
agentTypeFactionalWarfareAgent = 9
agentTypeEpicArcAgent = 10
agentTypeAura = 11
agentTypeCareerAgent = 12
agentTypeHeraldry = 13
auraAgentIDs = [3019499,
 3019493,
 3019495,
 3019490,
 3019497,
 3019496,
 3019486,
 3019498,
 3019492,
 3019500,
 3019489,
 3019494]
incarnaTutorialEpicArcs = (64, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77)
agentRangeSameSystem = 1
agentRangeSameOrNeighboringSystemSameConstellation = 2
agentRangeSameOrNeighboringSystem = 3
agentRangeNeighboringSystemSameConstellation = 4
agentRangeNeighboringSystem = 5
agentRangeSameConstellation = 6
agentRangeSameOrNeighboringConstellationSameRegion = 7
agentRangeSameOrNeighboringConstellation = 8
agentRangeNeighboringConstellationSameRegion = 9
agentRangeNeighboringConstellation = 10
agentRangeNearestEnemyCombatZone = 11
agentRangeNearestCareerHub = 12
agentIskMultiplierLevel1 = 1
agentIskMultiplierLevel2 = 2
agentIskMultiplierLevel3 = 4
agentIskMultiplierLevel4 = 8
agentIskMultiplierLevel5 = 16
agentIskMultipliers = (agentIskMultiplierLevel1,
 agentIskMultiplierLevel2,
 agentIskMultiplierLevel3,
 agentIskMultiplierLevel4,
 agentIskMultiplierLevel5)
agentLpMultiplierLevel1 = 20
agentLpMultiplierLevel2 = 60
agentLpMultiplierLevel3 = 180
agentLpMultiplierLevel4 = 540
agentLpMultiplierLevel5 = 4860
agentLpMultipliers = (agentLpMultiplierLevel1,
 agentLpMultiplierLevel2,
 agentLpMultiplierLevel3,
 agentLpMultiplierLevel4,
 agentLpMultiplierLevel5)
agentIskRandomLowValue = 11000
agentIskRandomHighValue = 16500
agentDivisionBusiness = 25
agentDivisionExploration = 26
agentDivisionIndustry = 27
agentDivisionMilitary = 28
agentDivisionAdvMilitary = 29
agentDivisionHeraldry = 37
agentDivisionsCareer = [agentDivisionBusiness,
 agentDivisionExploration,
 agentDivisionIndustry,
 agentDivisionMilitary,
 agentDivisionAdvMilitary]
agentDialogueButtonViewMission = 1
agentDialogueButtonRequestMission = 2
agentDialogueButtonAccept = 3
agentDialogueButtonAcceptChoice = 4
agentDialogueButtonAcceptRemotely = 5
agentDialogueButtonComplete = 6
agentDialogueButtonCompleteRemotely = 7
agentDialogueButtonContinue = 8
agentDialogueButtonDecline = 9
agentDialogueButtonDefer = 10
agentDialogueButtonQuit = 11
agentDialogueButtonStartResearch = 12
agentDialogueButtonCancelResearch = 13
agentDialogueButtonBuyDatacores = 14
agentDialogueButtonLocateCharacter = 15
agentDialogueButtonLocateAccept = 16
agentDialogueButtonLocateReject = 17
agentDialogueButtonYes = 18
agentDialogueButtonNo = 19
agentMissionBriefingMissionID = 'ContentID'
agentMissionBriefingDeclineTime = 'Decline Time'
agentMissionBriefingExpirationTime = 'Expiration Time'
agentMissionBriefingTitleID = 'Mission Title ID'
agentMissionBriefingBriefingID = 'Mission Briefing ID'
agentMissionBriefingKeywords = 'Mission Keywords'
agentMissionBriefingImage = 'Mission Image'
agentMissionBriefingAcceptTimestamp = 'AcceptTimestamp'
allianceApplicationAccepted = 2
allianceApplicationEffective = 3
allianceApplicationNew = 1
allianceApplicationRejected = 4
allianceCreationCost = 1000000000
allianceMembershipCost = 2000000
allianceRelationshipCompetitor = 3
allianceRelationshipEnemy = 4
allianceRelationshipFriend = 2
allianceRelationshipNAP = 1
ancestrySangDoCaste = 34
ancestrySaanGoCaste = 35
ancestryJingKoCaste = 36
ancestryUndefined = 64
bloodlineAchura = 11
bloodlineAmarr = 5
bloodlineBrutor = 4
bloodlineCivire = 2
bloodlineDeteis = 1
bloodlineGallente = 7
bloodlineIntaki = 8
bloodlineJinMei = 12
bloodlineKhanid = 13
bloodlineModifier = 10
bloodlineNiKunni = 6
bloodlineSebiestor = 3
bloodlineStatic = 9
bloodlineVherokior = 14
bloodlineDrifter = 19
bloodlines = [bloodlineAchura,
 bloodlineAmarr,
 bloodlineBrutor,
 bloodlineCivire,
 bloodlineDeteis,
 bloodlineGallente,
 bloodlineIntaki,
 bloodlineJinMei,
 bloodlineKhanid,
 bloodlineModifier,
 bloodlineNiKunni,
 bloodlineSebiestor,
 bloodlineStatic,
 bloodlineVherokior,
 bloodlineDrifter]
characterTypes = [typeCharacter,
 typeCharacterLegacy1,
 typeCharacterLegacy2,
 typeCharacterLegacy3,
 typeCharacterLegacy4,
 typeCharacterLegacy5,
 typeCharacterLegacy6,
 typeCharacterLegacy7,
 typeCharacterLegacy8,
 typeCharacterLegacy9,
 typeCharacterLegacy10,
 typeCharacterLegacy11,
 typeCharacterLegacy12,
 typeCharacterLegacy13,
 typeCharacterLegacy14]
raceCaldari = 1
raceMinmatar = 2
raceAmarr = 4
raceGallente = 8
raceJove = 16
raceAngel = 32
raceSleepers = 64
raceORE = 128
raceTriglavian = 135
races = {raceCaldari: 'Caldari',
 raceMinmatar: 'Minmatar',
 raceAmarr: 'Amarr',
 raceGallente: 'Gallente',
 raceJove: 'Jove',
 raceAngel: 'Angel',
 raceSleepers: 'Sleepers',
 raceORE: 'ORE',
 raceTriglavian: 'Triglavian'}
schoolImperialAcademy = 11
schoolHedionUniversity = 12
schoolRoyalAmarrInstitute = 13
schoolRepublicMilitarySchool = 14
schoolRepublicUniversity = 15
schoolPatorTechSchool = 16
schoolStateWarAcademy = 17
schoolScienceAndTradeInstitute = 18
schoolSchoolOfAppliedKnowledge = 19
schoolFederalNavyAcademy = 20
schoolUniversityOfCaille = 21
schoolCenterForAdvancedStudies = 22
schoolSocietyOfConsciousThought = 23
schoolMaterialInstitute = 24
schoolAcademyOfAggressiveBehaviour = 25
raceBySchool = {schoolImperialAcademy: raceAmarr,
 schoolHedionUniversity: raceAmarr,
 schoolRoyalAmarrInstitute: raceAmarr,
 schoolRepublicMilitarySchool: raceMinmatar,
 schoolRepublicUniversity: raceMinmatar,
 schoolPatorTechSchool: raceMinmatar,
 schoolStateWarAcademy: raceCaldari,
 schoolScienceAndTradeInstitute: raceCaldari,
 schoolSchoolOfAppliedKnowledge: raceCaldari,
 schoolFederalNavyAcademy: raceGallente,
 schoolUniversityOfCaille: raceGallente,
 schoolCenterForAdvancedStudies: raceGallente,
 schoolSocietyOfConsciousThought: raceJove,
 schoolMaterialInstitute: raceJove,
 schoolAcademyOfAggressiveBehaviour: raceJove}
cacheEosNpcToNpcStandings = 109998
cacheAutAffiliates = 109997
cacheAutCdkeyTypes = 109996
cacheEveWarnings = 109995
cacheEveMessages = 1000001
cacheMapSolarSystemLoadRatios = 1409996
cacheMapPlanets = 1409993
cacheShipInsurancePrices = 2000007
cacheStaStations = 2209988
cacheStaStationsStatic = 2209987
cacheStaOldStationsStatic = 2210000
cacheMktOrderStates = 2409999
cacheCrpCorporations = 2809996
cacheCrpNpcMembers = 2809994
cacheCrpPlayerCorporationIDs = 2809993
cacheAgtPrices = 3009989
cacheRedeemWhitelist = 6300001
cachePetCategories = 8109999
cachePetQueues = 8109998
cachePetCategoriesVisible = 8109997
cachePetGMQueueOrder = 8109996
cachePetOsTypes = 8109995
cacheCertificates = 5100001
cacheCertificateRelationships = 5100004
cachePlanetBlacklist = 7309999
cacheEspCorporations = 1
cacheEspAlliances = 2
cacheEspSolarSystems = 3
cacheCargoContainers = 5
cachePriceHistory = 6
corpLogoChangeCost = 100
corpMaxSize = 12600
COMMUNITY_FITTING_CORP = 1000282
corpRoleDirector = 1
corpRoleDeliveriesHangarTake = 2
corpRoleDeliveriesHangarQuery = 4
corpRoleDeliveriesHangarContainerTake = 8
corpRolePersonnelManager = 128
corpRoleAccountant = 256
corpRoleSecurityOfficer = 512
corpRoleFactoryManager = 1024
corpRoleStationManager = 2048
corpRoleAuditor = 4096
corpRoleHangarCanTake1 = 8192
corpRoleHangarCanTake2 = 16384
corpRoleHangarCanTake3 = 32768
corpRoleHangarCanTake4 = 65536
corpRoleHangarCanTake5 = 131072
corpRoleHangarCanTake6 = 262144
corpRoleHangarCanTake7 = 524288
corpRoleHangarCanQuery1 = 1048576
corpRoleHangarCanQuery2 = 2097152
corpRoleHangarCanQuery3 = 4194304
corpRoleHangarCanQuery4 = 8388608
corpRoleHangarCanQuery5 = 16777216
corpRoleHangarCanQuery6 = 33554432
corpRoleHangarCanQuery7 = 67108864
corpRoleAccountCanTake1 = 134217728
corpRoleAccountCanTake2 = 268435456
corpRoleAccountCanTake3 = 536870912
corpRoleAccountCanTake4 = 1073741824
corpRoleAccountCanTake5 = 2147483648L
corpRoleAccountCanTake6 = 4294967296L
corpRoleAccountCanTake7 = 8589934592L
corpRoleDiplomat = 17179869184L
corpRoleBrandManager = 34359738368L
corpRoleEquipmentConfig = 2199023255552L
corpRoleContainerCanTake1 = 4398046511104L
corpRoleContainerCanTake2 = 8796093022208L
corpRoleContainerCanTake3 = 17592186044416L
corpRoleContainerCanTake4 = 35184372088832L
corpRoleContainerCanTake5 = 70368744177664L
corpRoleContainerCanTake6 = 140737488355328L
corpRoleContainerCanTake7 = 281474976710656L
corpRoleCanRentOffice = 562949953421312L
corpRoleCanRentFactorySlot = 1125899906842624L
corpRoleCanRentResearchSlot = 2251799813685248L
corpRoleJuniorAccountant = 4503599627370496L
corpRoleStarbaseConfig = 9007199254740992L
corpRoleTrader = 18014398509481984L
corpRoleChatManager = 36028797018963968L
corpRoleContractManager = 72057594037927936L
corpRoleInfrastructureTacticalOfficer = 144115188075855872L
corpRoleStarbaseCaretaker = 288230376151711744L
corpRoleFittingManager = 576460752303423488L
corpRoleProjectManager = 1152921504606846976L
corpRoleTerrestrialLogisticsOfficer = 2305843009213693952L
corpRoleSkillPlanManager = 4611686018427387904L
corpRoleLocationTypeHQ = 1
corpRoleLocationTypeBase = 2
corpRoleLocationTypeOther = 3
corpHangarTakeRolesByFlag = {flagCorpSAG1: corpRoleHangarCanTake1,
 flagCorpSAG2: corpRoleHangarCanTake2,
 flagCorpSAG3: corpRoleHangarCanTake3,
 flagCorpSAG4: corpRoleHangarCanTake4,
 flagCorpSAG5: corpRoleHangarCanTake5,
 flagCorpSAG6: corpRoleHangarCanTake6,
 flagCorpSAG7: corpRoleHangarCanTake7,
 flagCorpGoalDeliveries: corpRoleDeliveriesHangarTake}
corpHangarQueryRolesByFlag = {flagCorpSAG1: corpRoleHangarCanQuery1,
 flagCorpSAG2: corpRoleHangarCanQuery2,
 flagCorpSAG3: corpRoleHangarCanQuery3,
 flagCorpSAG4: corpRoleHangarCanQuery4,
 flagCorpSAG5: corpRoleHangarCanQuery5,
 flagCorpSAG6: corpRoleHangarCanQuery6,
 flagCorpSAG7: corpRoleHangarCanQuery7,
 flagCorpGoalDeliveries: corpRoleDeliveriesHangarQuery}
corpContainerTakeRolesByFlag = {flagCorpSAG1: corpRoleContainerCanTake1,
 flagCorpSAG2: corpRoleContainerCanTake2,
 flagCorpSAG3: corpRoleContainerCanTake3,
 flagCorpSAG4: corpRoleContainerCanTake4,
 flagCorpSAG5: corpRoleContainerCanTake5,
 flagCorpSAG6: corpRoleContainerCanTake6,
 flagCorpSAG7: corpRoleContainerCanTake7,
 flagCorpGoalDeliveries: corpRoleDeliveriesHangarContainerTake}
allCorpHangarRoles = set(list(corpHangarTakeRolesByFlag.values()) + list(corpHangarQueryRolesByFlag.values()) + list(corpContainerTakeRolesByFlag.values()))
locationalCorpRoles = allCorpHangarRoles - {corpRoleDirector}
corpStationMgrGraceMinutes = 60
corpDivisionDistribution = 22
corpDivisionMining = 23
corpDivisionSecurity = 24
corpDivisionHeraldry = 37
corporationStartupCost = 1599800
corporationAdvertisementFlatFee = 500000
corporationAdvertisementDailyRate = 250000
corporationMaxCorpRecruiters = 6
corporationMaxRecruitmentAds = 3
corporationMaxRecruitmentAdDuration = 28
corporationMinRecruitmentAdDuration = 3
corporationRecMaxTitleLength = 40
corporationRecMaxMessageLength = 1000
corpNameMaxLenTQ = 50
corpNameMaxLenSR = 30
allianceNameMaxLenTQ = 50
allianceNameMaxLenSR = 30
disabledDatasetsDungeons = 300005
disabledDatasetsMissions = 3000002
disabledDatasets = {disabledDatasetsDungeons: 'Dungeons',
 disabledDatasetsMissions: 'Missions'}
dunArchetypeCOSMOSFlags = 1
dunArchetypeLandmarks = 2
dunArchetypeMilitaryDepot = 3
dunArchetypeMilitaryInstallation = 4
dunArchetypeMilitaryOutPost = 6
dunArchetypeNavalShipyard = 8
dunArchetypePrisonFacility = 14
dunArchetypeSinCity = 16
dunArchetypeZTest = 19
dunArchetypeAgentMissionDungeon = 20
dunArchetypeAgentOfferDungeon = 21
dunArchetypeAgentsInSpace = 22
dunArchetypeCombatSites = 24
dunArchetypeAgentStaticDungeons = 26
dunArchetypeOreAnomaly = 27
dunArchetypeIceBelt = 28
dunArchetypeCombatHacking = 29
dunArchetypeGasClouds = 30
dunArchetypeEscalatingPathDungeons = 31
dunArchetypeFactionalWarfareComplexNovice = 33
dunArchetypeFactionalWarfareComplexSmall = 34
dunArchetypeFactionalWarfareComplexMedium = 35
dunArchetypeFactionalWarfareComplexLarge = 36
dunArchetypeCombatSimulator = 37
dunArchetypeWormhole = 38
dunArchetypeGhostSites = 39
dunArchetypeEventSites = 43
dunArchetypeRelicSites = 44
dunArchetypeDataSites = 45
dunArchetypeIncursionSites = 46
dunArchetypeResourceWars = 47
dunArchetypeInceptionSites = 48
dunArchetypeDrifterSites = 49
dunArchetypeSitesOfInterest = 50
dunArchetypeAbyssalSites = 51
dunArchetypeIncursionSitesScout = 60
dunArchetypeIncursionSitesVanguard = 61
dunArchetypeIncursionSitesAssult = 62
dunArchetypeIncursionSitesHeadquarter = 63
dunArchetypeIncursionSitesBoss = 64
dunArchetypeInvasionSites = 65
dunArchetypeFactionaWarfareBattlefieldSites = 68
dunArchetypeHomefrontSites = 70
dunArchetypeInsurgencyItemTraderPirate = 72
dunArchetypeInsurgencyItemTraderAntiPirate = 73
dunArchetypeInsurgencyWarehouseRaid = 74
dunArchetypeInsurgencyWarehouseCorpOutpostRaidSmall = 75
dunArchetypeInsurgencyWarehouseCorpOutpostRaidMedium = 76
dunArchetypeInsurgencyWarehouseCorpOutpostRaidLarge = 77
dunArchetypeInsurgencyWarehouseCorpOutpostRaidXLarge = 78
dunArchetypeInsurgencyMiningFleetAmubsh = 79
dunArchetypesFactionalWarfare = (dunArchetypeFactionalWarfareComplexNovice,
 dunArchetypeFactionalWarfareComplexSmall,
 dunArchetypeFactionalWarfareComplexMedium,
 dunArchetypeFactionalWarfareComplexLarge,
 dunArchetypeFactionaWarfareBattlefieldSites)
dunArchetypesIncursionSites = (dunArchetypeIncursionSites,
 dunArchetypeIncursionSitesScout,
 dunArchetypeIncursionSitesVanguard,
 dunArchetypeIncursionSitesAssult,
 dunArchetypeIncursionSitesHeadquarter,
 dunArchetypeIncursionSitesBoss)
dunArchetypesInsurgencySites = (dunArchetypeInsurgencyItemTraderPirate,
 dunArchetypeInsurgencyItemTraderAntiPirate,
 dunArchetypeInsurgencyWarehouseRaid,
 dunArchetypeInsurgencyWarehouseCorpOutpostRaidSmall,
 dunArchetypeInsurgencyWarehouseCorpOutpostRaidMedium,
 dunArchetypeInsurgencyWarehouseCorpOutpostRaidLarge,
 dunArchetypeInsurgencyWarehouseCorpOutpostRaidXLarge,
 dunArchetypeInsurgencyMiningFleetAmubsh)
dunEventMessageEnvironment = 3
dunEventMessageImminentDanger = 1
dunEventMessageMissionInstruction = 7
dunEventMessageMissionObjective = 6
dunEventMessageMood = 4
dunEventMessageNPC = 2
dunEventMessageStory = 5
dunEventMessageWarning = 8
dunExpirationDelay = 48
dungeonGateUnlockPeriod = 66
dungeonKeylockUnlocked = 0
dungeonKeylockPrivate = 1
dungeonKeylockPublic = 2
dungeonKeylockTrigger = 3
dungeonKeyLockOwner = 4
dungeonKeySoftLockOwnerSuspect = 5
dunWanderingNpcGroups = [groupBoss, groupNpcIndustrialCommand]
dunEventMessageParamCharacter = 0
dunEventMessageParamFleet = 1
dunEventMessageParamRoom = 2
dunEventMessageParamDungeon = 3
DUNGEON_ORIGIN_UNDEFINED = None
DUNGEON_ORIGIN_STATIC = 1
DUNGEON_ORIGIN_AGENT = 2
DUNGEON_ORIGIN_PLAYTEST = 3
DUNGEON_ORIGIN_EDIT = 4
DUNGEON_ORIGIN_DISTRIBUTION = 5
DUNGEON_ORIGIN_PATH = 6
DUNGEON_ORIGIN_TUTORIAL = 7
DUNGEON_ORIGIN_ATOM_ACTION = 9
dungeonSpawnBelts = 0
dungeonSpawnGate = 1
dungeonSpawnNear = 2
dungeonSpawnDeep = 3
dungeonSpawnReinforcments = 4
dungeonSpawnStations = 5
dungeonSpawnFaction = 6
dungeonSpawnConcord = 7
dungeonSpawnSuns = 8
dungeonSpawnLocations = {dungeonSpawnBelts: 'Asteroid Belts',
 dungeonSpawnGate: 'Star Gates',
 dungeonSpawnNear: 'Near Planet',
 dungeonSpawnDeep: 'Deep Space',
 dungeonSpawnStations: 'Stations',
 dungeonSpawnSuns: 'The Sun'}
locationAbstract = 0
locationAssetSafety = 2004
locationSystem = 1
locationBank = 2
locationTemp = 5
locationTrading = 7
locationGraveyard = 8
locationUniverse = 9
locationHiddenSpace = 9000001
locationJunkyard = 10
locationCorporation = 13
locationTradeSessionJunkyard = 1008
locationCharacterGraveyard = 1501
locationCorporationGraveyard = 1502
locationStructureGraveyard = 1507
locationRAMInstalledItems = 2003
locationAlliance = 3007
locationMinJunkyardID = 1000
locationMaxJunkyardID = 1999
minEveMarketGroup = 0
maxEveMarketGroup = 350000
minDustMarketGroup = 350001
maxDustMarketGroup = 999999
factionNoFaction = 0
factionAmarrEmpire = 500003
factionAmmatar = 500007
factionAngelCartel = 500011
factionCONCORDAssembly = 500006
factionCaldariState = 500001
factionGallenteFederation = 500004
factionGuristasPirates = 500010
factionInterBus = 500013
factionJoveEmpire = 500005
factionKhanidKingdom = 500008
factionMinmatarRepublic = 500002
factionMordusLegion = 500018
factionORE = 500014
factionOuterRingExcavations = 500014
factionSanshasNation = 500019
factionSerpentis = 500020
factionSistersOfEVE = 500016
factionSocietyOfConsciousThought = 500017
factionTheBloodRaiderCovenant = 500012
factionTheServantSistersofEVE = 500016
factionTheSyndicate = 500009
factionThukkerTribe = 500015
factionUnknown = 500021
factionMordusLegionCommand = 500018
factionTheInterBus = 500013
factionAmmatarMandate = 500007
factionTheSociety = 500017
factionDrifters = 500024
factionRogueDrones = 500025
factionTriglavian = 500026
factionEDENCOM = 500027
factionDeathless = 500029
factions = (factionAmarrEmpire,
 factionAmmatar,
 factionAngelCartel,
 factionCONCORDAssembly,
 factionCaldariState,
 factionGallenteFederation,
 factionGuristasPirates,
 factionInterBus,
 factionJoveEmpire,
 factionKhanidKingdom,
 factionMinmatarRepublic,
 factionMordusLegion,
 factionORE,
 factionOuterRingExcavations,
 factionSanshasNation,
 factionSerpentis,
 factionSistersOfEVE,
 factionSocietyOfConsciousThought,
 factionTheBloodRaiderCovenant,
 factionTheServantSistersofEVE,
 factionTheSyndicate,
 factionThukkerTribe,
 factionMordusLegionCommand,
 factionTheInterBus,
 factionAmmatarMandate,
 factionTheSociety,
 factionDrifters,
 factionTriglavian,
 factionEDENCOM,
 factionDeathless)
factionsEmpires = (factionAmarrEmpire,
 factionCaldariState,
 factionGallenteFederation,
 factionMinmatarRepublic)
factionsPirates = (factionAngelCartel,
 factionGuristasPirates,
 factionTheBloodRaiderCovenant,
 factionSanshasNation,
 factionSerpentis,
 factionDeathless)
factionsWithoutAgents = (factionDrifters,
 factionJoveEmpire,
 factionCONCORDAssembly,
 factionSocietyOfConsciousThought,
 factionDrifters,
 factionTriglavian,
 factionEDENCOM)
factionsWhoseStandingsAreNotAffectedBySkillBonuses = (factionDrifters,
 factionRogueDrones,
 factionTriglavian,
 factionEDENCOM)
factionByRace = {raceCaldari: factionCaldariState,
 raceMinmatar: factionMinmatarRepublic,
 raceAmarr: factionAmarrEmpire,
 raceGallente: factionGallenteFederation}
raceByFaction = {factionID:raceID for raceID, factionID in factionByRace.iteritems()}
corpHeraldry = 1000419
corpHomefront = 1000413
refSkipLog = -1
refUndefined = 0
refPlayerTrading = 1
refMarketTransaction = 2
refGMCashTransfer = 3
refATMWithdraw = 4
refATMDeposit = 5
refBackwardCompatible = 6
refMissionReward = 7
refCloneActivation = 8
refInheritance = 9
refPlayerDonation = 10
refCorporationPayment = 11
refDockingFee = 12
refOfficeRentalFee = 13
refFactorySlotRentalFee = 14
refRepairBill = 15
refBounty = 16
refBountyPrize = 17
refInsurance = 19
refMissionExpiration = 20
refMissionCompletion = 21
refShares = 22
refCourierMissionEscrow = 23
refMissionCost = 24
refAgentMiscellaneous = 25
refPaymentToLPStore = 26
refAgentLocationServices = 27
refAgentDonation = 28
refAgentSecurityServices = 29
refAgentMissionCollateralPaid = 30
refAgentMissionCollateralRefunded = 31
refAgentMissionReward = 33
refAgentMissionTimeBonusReward = 34
refCSPA = 35
refCSPAOfflineRefund = 36
refCorporationAccountWithdrawal = 37
refCorporationDividendPayment = 38
refCorporationRegistrationFee = 39
refCorporationLogoChangeCost = 40
refReleaseOfImpoundedProperty = 41
refMarketEscrow = 42
refMarketFinePaid = 44
refBrokerfee = 46
refAllianceRegistrationFee = 48
refWarFee = 49
refAllianceMaintainanceFee = 50
refContrabandFine = 51
refCloneTransfer = 52
refAccelerationGateFee = 53
refTransactionTax = 54
refJumpCloneInstallationFee = 55
refJumpCloneActivationFee = 128
refManufacturing = 56
refResearchingTechnology = 57
refResearchingTimeProductivity = 58
refResearchingMaterialProductivity = 59
refCopying = 60
refDuplicating = 61
refReverseEngineering = 62
refContractAuctionBid = 63
refContractAuctionBidRefund = 64
refContractCollateral = 65
refContractRewardRefund = 66
refContractAuctionSold = 67
refContractReward = 68
refContractCollateralRefund = 69
refContractCollateralPayout = 70
refContractPrice = 71
refContractBrokersFee = 72
refContractSalesTax = 73
refContractDeposit = 74
refContractDepositSalesTax = 75
refSecureEVETimeCodeExchange = 76
refContractAuctionBidCorp = 77
refContractCollateralCorp = 78
refContractPriceCorp = 79
refContractBrokersFeeCorp = 80
refContractDepositCorp = 81
refContractDepositRefund = 82
refContractRewardAdded = 83
refContractRewardAddedCorp = 84
refBountyPrizes = 85
refCorporationAdvertisementFee = 86
refMedalCreation = 87
refMedalIssuing = 88
refAttributeRespecification = 90
refSovereignityRegistrarFee = 91
refSovereignityUpkeepAdjustment = 95
refPlanetaryImportTax = 96
refPlanetaryExportTax = 97
refPlanetaryConstruction = 98
refRewardManager = 99
refBountySurcharge = 101
refContractReversal = 102
refStorePurchase = 106
refStoreRefund = 107
refPlexConversion = 108
refAurumGiveAway = 109
refAurumTokenConversion = 111
refDatacoreFee = 112
refWarSurrenderFee = 113
refWarAllyContract = 114
refBountyReimbursement = 115
refKillRightBuy = 116
refSecurityTagProcessingFee = 117
refIndustryTeamEscrow = 118
refIndustryTeamEscrowReimbursement = 119
refIndustryFacilityTax = 120
refSweatAurum = 121
refInfrastructureHubBill = 122
refAssetSafetyTax = 123
refRaffleTicketSale = 143
refRafflePayout = 144
refRaffleTax = 145
refRaffleTicketRepayment = 146
refOpportunityReward = 124
refProjectDiscoveryReward = 125
refReprocessingTax = 127
refReaction = 135
refUnderConstruction = 166
refAllignmentBasedGateToll = 168
refProjectPayouts = 170
refInsurgencyCorruptionContributionReward = 172
refInsurgencySuppressionContributionReward = 173
refDailyGoalPayouts = 174
refDailyGoalPayoutsTax = 175
refCosmeticMarketComponentItemPurchase = 178
refCosmeticMarketSkinSaleBrokerFee = 179
refCosmeticMarketSkinPurchase = 180
refCosmeticMarketSkinSale = 181
refCosmeticMarketSkinSaleTax = 182
refCosmeticMarketSkinTransaction = 183
COSMETIC_MARKET_TRANSACTION_REFS = [refCosmeticMarketComponentItemPurchase,
 refCosmeticMarketSkinSaleBrokerFee,
 refCosmeticMarketSkinPurchase,
 refCosmeticMarketSkinSale,
 refCosmeticMarketSkinSaleTax,
 refCosmeticMarketSkinTransaction]
refCareerProgramPayouts = 185
refExternalTradeFreeze = 136
refExternalTradeThaw = 137
refExternalTradeDelivery = 138
refDuelWagerEscrow = 132
refDuelWagerPayment = 133
refDuelWagerRefund = 134
refStructureGateJump = 140
refSkillPurchase = 141
refItemTraderPayment = 142
refRedeemedISKToken = 147
refMarketProviderTax = 149
refESSMainBankAutopayment = 155
refMilestoneRewardPayment = 156
refMaxEve = 10000
refCorporationTaxNpcBounties = 92
refCorporationTaxAgentRewards = 93
refCorporationTaxAgentBonusRewards = 94
refCorporationTaxRewards = 103
refProjectDiscoveryTaxRewards = 126
refOperationCompletedReward = 129
refResourceWarsReward = 131
refSeasonChallengeReward = 139
refIsOwner = [refCorporationPayment,
 refCSPA,
 refCSPAOfflineRefund,
 refBounty,
 refBountyPrize,
 refKillRightBuy,
 refCorporationAccountWithdrawal,
 refCorporationDividendPayment,
 refCorporationLogoChangeCost,
 refWarFee,
 refAllianceMaintainanceFee]
refIsLocation = [refBountyPrizes,
 refPlanetaryImportTax,
 refPlanetaryExportTax,
 refPlanetaryConstruction]
derivedTransactionParentMapping = {refCorporationTaxNpcBounties: refBountyPrize,
 refCorporationTaxAgentRewards: refAgentMissionReward,
 refCorporationTaxAgentBonusRewards: refAgentMissionTimeBonusReward,
 refCorporationTaxRewards: refRewardManager,
 refProjectDiscoveryTaxRewards: refProjectDiscoveryReward,
 refDailyGoalPayoutsTax: refDailyGoalPayouts}
refGroupCorpAlliance = 1
refGroupAgentsAndMissions = 2
refGroupTrade = 3
refGroupBounty = 4
refGroupIndustry = 5
refGroupTransfer = 6
refGroupMisc = 7
refGroupHypernetRelay = 8
refGroups = {refGroupCorpAlliance: (refCorporationAdvertisementFee,
                        refAllianceMaintainanceFee,
                        refAllianceRegistrationFee,
                        refCorporationDividendPayment,
                        refCorporationLogoChangeCost,
                        refCorporationPayment,
                        refCorporationRegistrationFee,
                        refMedalCreation,
                        refMedalIssuing,
                        refOfficeRentalFee,
                        refShares,
                        refWarAllyContract,
                        refWarFee,
                        refWarSurrenderFee),
 refGroupAgentsAndMissions: (refAgentLocationServices,
                             refAgentMiscellaneous,
                             refAgentMissionCollateralPaid,
                             refAgentMissionCollateralRefunded,
                             refAgentMissionReward,
                             refCorporationTaxAgentRewards,
                             refAgentMissionTimeBonusReward,
                             refCorporationTaxAgentBonusRewards,
                             refMissionReward,
                             refCorporationTaxRewards,
                             refOperationCompletedReward),
 refGroupTrade: (refBrokerfee,
                 refContractAuctionBid,
                 refContractAuctionBidCorp,
                 refContractAuctionBidRefund,
                 refContractAuctionSold,
                 refContractBrokersFee,
                 refContractBrokersFeeCorp,
                 refContractCollateral,
                 refContractCollateralPayout,
                 refContractCollateralRefund,
                 refContractDeposit,
                 refContractDepositCorp,
                 refContractDepositRefund,
                 refContractDepositSalesTax,
                 refContractPrice,
                 refContractPriceCorp,
                 refContractReversal,
                 refContractReward,
                 refContractRewardRefund,
                 refContractSalesTax,
                 refExternalTradeDelivery,
                 refExternalTradeFreeze,
                 refExternalTradeThaw,
                 refItemTraderPayment,
                 refPaymentToLPStore,
                 refMarketEscrow,
                 refMarketTransaction,
                 refPlayerTrading,
                 refSkillPurchase,
                 refStorePurchase,
                 refStoreRefund,
                 refMarketProviderTax),
 refGroupBounty: (refBounty,
                  refBountyPrize,
                  refCorporationTaxNpcBounties,
                  refBountyPrizes,
                  refBountyReimbursement,
                  refBountySurcharge),
 refGroupIndustry: (refCopying,
                    refDatacoreFee,
                    refIndustryFacilityTax,
                    refManufacturing,
                    refPlanetaryConstruction,
                    refPlanetaryExportTax,
                    refPlanetaryImportTax,
                    refReaction,
                    refReprocessingTax,
                    refResearchingMaterialProductivity,
                    refResearchingTechnology,
                    refResearchingTimeProductivity),
 refGroupTransfer: (refCorporationAccountWithdrawal, refGMCashTransfer, refPlayerDonation),
 refGroupHypernetRelay: (refRaffleTicketSale,
                         refRafflePayout,
                         refRaffleTax,
                         refRaffleTicketRepayment)}
refGroupByRefType = {}
for refGroupID, refTypeIDs in refGroups.iteritems():
    for refTypeID in refTypeIDs:
        refGroupByRefType[refTypeID] = refGroupID

for refTypeID in COSMETIC_MARKET_TRANSACTION_REFS:
    refGroupByRefType[refTypeID] = refGroupTrade

recDescription = 'DESC'
recDescNpcBountyList = 'NBL'
recDescNpcBountyListTruncated = 'NBLT'
recStoreItems = 'STOREITEMS'
recDescOwners = 'OWNERIDS'
recDescOwnersTrunc = 'OWNERST'
minCorporationTaxAmount = 100000.0
stationServiceBountyMissions = 1
stationServiceAssassinationMissions = 2
stationServiceCourierMission = 3
stationServiceInterbus = 4
stationServiceReprocessingPlant = 5
stationServiceRefinery = 6
stationServiceMarket = 7
stationServiceBlackMarket = 8
stationServiceStockExchange = 9
stationServiceCloning = 10
stationServiceSurgery = 11
stationServiceDNATherapy = 12
stationServiceRepairFacilities = 13
stationServiceFactory = 14
stationServiceLaboratory = 15
stationServiceGambling = 16
stationServiceFitting = 17
stationServicePaintshop = 18
stationServiceNews = 19
stationServiceStorage = 20
stationServiceInsurance = 21
stationServiceDocking = 22
stationServiceOfficeRental = 23
stationServiceJumpCloneFacility = 24
stationServiceLoyaltyPointStore = 25
stationServiceNavyOffices = 26
stationServiceSecurityOffice = 27
CLONE_STATION_SERVICES = [stationServiceCloning, stationServiceSurgery, stationServiceDNATherapy]
stationPolarisIII = 60014845
stationPolarisIV = 60014848
stationDoomheim = 60000001
stationServiceAccessRules = {stationPolarisIII: {stationServiceRefinery: {'minimumStanding': 10,
                                              'minimumCharSecurity': 10,
                                              'maximumCharSecurity': 10},
                     stationServiceRepairFacilities: {'minimumStanding': 0,
                                                      'minimumCharSecurity': 0,
                                                      'maximumCharSecurity': 10},
                     stationServiceNews: {'minimumStanding': -10,
                                          'minimumCharSecurity': -10,
                                          'maximumCharSecurity': 10},
                     stationServiceDocking: {'minimumStanding': 0,
                                             'minimumCharSecurity': -10,
                                             'maximumCharSecurity': 10}},
 stationPolarisIV: {stationServiceRefinery: {'minimumStanding': -10,
                                             'minimumCharSecurity': 10,
                                             'maximumCharSecurity': 10}}}
billTypeMarketFine = 1
billTypeRentalBill = 2
billTypeBrokerBill = 3
billTypeWarBill = 4
billTypeAllianceMaintainanceBill = 5
billTypeSovereignityMarker = 6
billTypeInfrastructureHub = 7
billUnpaid = 0
billPaid = 1
billCancelled = 2
billHidden = 3
conAvailMyAlliance = 3
conAvailMyCorp = 2
conAvailMyself = 1
conAvailPublic = 0
conStatusOutstanding = 0
conStatusInProgress = 1
conStatusFinishedIssuer = 2
conStatusFinishedContractor = 3
conStatusFinished = 4
conStatusCancelled = 5
conStatusRejected = 6
conStatusFailed = 7
conStatusDeleted = 8
conStatusReversed = 9
conStatusBidOnBy = 10
conStatusRequiresAttention = -1
conTypeNothing = 0
conTypeItemExchange = 1
conTypeAuction = 2
conTypeCourier = 3
conTypeLoan = 4
facwarIskDestroyedToLoyaltyPointRatio = 3077
facwarCorporationJoining = 0
facwarCorporationActive = 1
facwarCorporationLeaving = 2
facwarWarningStandingCharacter = 0
facwarWarningStandingCorporation = 1
facwarMinStandingsToJoinDefault = -0.0001
facwarSolarSystemUpgradeThresholds = [0,
 40000,
 60000,
 90000,
 140000,
 200000,
 300000]
facwarSolarSystemMaxLPPool = facwarSolarSystemUpgradeThresholds[-1]
facWarSolarSystemMaxLevel = 5
facwarLPGainBonus = [0.5,
 1.0,
 1.75,
 2.5,
 3.25]
facwarIHubInteractDist = 2500.0
facwarCaptureBleedLPs = 0.1
facwarDefensivePlexingLPMultiplier = 0.75
facwarMinLPDonation = 10
facwarMaxLPUnknownGroup = 25000
facwarMaxLPPayout = {groupAssaultFrigate: 10000,
 groupAttackBattlecruiser: 15000,
 groupBattlecruiser: 15000,
 groupBattleship: 50000,
 groupBlackOps: 150000,
 groupBlockadeRunner: 150000,
 groupCapitalIndustrialShip: 150000,
 groupCapsule: 50000,
 groupCarrier: 150000,
 groupCombatReconShip: 50000,
 groupCommandDestroyer: 10000,
 groupCommandShip: 50000,
 groupCovertOps: 10000,
 groupCruiser: 10000,
 groupDestroyer: 3000,
 groupDreadnought: 150000,
 groupLancerDreadnought: 150000,
 groupElectronicAttackShips: 10000,
 groupExhumer: 50000,
 groupExpeditionFrigate: 10000,
 groupForceReconShip: 50000,
 groupFreighter: 150000,
 groupFrigate: 2000,
 groupHeavyAssaultCruiser: 50000,
 groupHeavyInterdictors: 50000,
 groupIndustrial: 50000,
 groupIndustrialCommandShip: 150000,
 groupInterceptor: 10000,
 groupInterdictor: 10000,
 groupJumpFreighter: 150000,
 groupLogistics: 50000,
 groupLogisticsFrigate: 10000,
 groupMarauders: 150000,
 groupMiningBarge: 10000,
 groupPrototypeExplorationShip: 10000,
 groupRookieship: 2000,
 groupShuttle: 2000,
 groupStealthBomber: 10000,
 groupStrategicCruiser: 100000,
 groupSupercarrier: 150000,
 groupTitan: 150000,
 groupTransportShip: 150000,
 groupTacticalDestroyer: 10000,
 groupFlagCruiser: 50000}
facwarMaxLPPayoutFactionOverwrites = {groupBattleship: 150000,
 groupBattlecruiser: 75000,
 groupCruiser: 50000,
 groupDestroyer: 15000,
 groupFrigate: 10000,
 groupIndustrial: 150000}
facwarStatTypeKill = 0
facwarStatTypeLoss = 1
facwarStatTypeVictoryPoints = 2
blockAmarrCaldari = 1
blockGallenteMinmatar = 2
blockSmugglingCartel = 3
blockTerrorist = 4
cargoContainerLifetime = 120
wreckLifetimeRookieSystem = 30
costJumpClone = 900000
crpApplicationAppliedByCharacter = 0
crpApplicationRenegotiatedByCharacter = 1
crpApplicationAcceptedByCharacter = 2
crpApplicationRejectedByCharacter = 3
crpApplicationRejectedByCorporation = 4
crpApplicationRenegotiatedByCorporation = 5
crpApplicationAcceptedByCorporation = 6
crpApplicationWithdrawnByCharacter = 7
crpApplicationInvitedByCorporation = 8
crpApplicationMaxSize = 1000
crpApplicationEndStatuses = [crpApplicationRejectedByCorporation,
 crpApplicationWithdrawnByCharacter,
 crpApplicationAcceptedByCharacter,
 crpApplicationRejectedByCharacter]
crpApplicationOpenStatuses = [crpApplicationAppliedByCharacter, crpApplicationRenegotiatedByCharacter, crpApplicationRenegotiatedByCorporation]
crpApplicationActiveStatuses = [crpApplicationAcceptedByCorporation, crpApplicationAppliedByCharacter, crpApplicationInvitedByCorporation]
deftypeHouseWarmingGift = 34
deftypeCorpseMale = 25
deftypeCorpseFemale = 29148
directorConcordSecurityLevelMax = 1000
directorConcordSecurityLevelMin = 450
directorConvoySecurityLevelMin = 450
directorPirateGateSecurityLevelMax = 349
directorPirateGateSecurityLevelMin = -1000
directorPirateSecurityLevelMax = 849
directorPirateSecurityLevelMin = -1000
entityApproaching = 3
entityCombat = 1
entityDeparting = 4
entityDeparting2 = 5
entityEngage = 10
entityFleeing = 7
entityIdle = 0
entityMining = 2
entityOperating = 9
entityPursuit = 6
entitySalvaging = 18
graphicIDBrokenPod = 20391
graphicIDBrokenGoldenPod = 22235
graphicCorpLogoLibNoShape = 415
graphicCorpLogoLibShapes = {415: 'res:/UI/Texture/corpLogoLibs/415.png',
 416: 'res:/UI/Texture/corpLogoLibs/416.png',
 417: 'res:/UI/Texture/corpLogoLibs/417.png',
 418: 'res:/UI/Texture/corpLogoLibs/418.png',
 419: 'res:/UI/Texture/corpLogoLibs/419.png',
 420: 'res:/UI/Texture/corpLogoLibs/420.png',
 421: 'res:/UI/Texture/corpLogoLibs/421.png',
 422: 'res:/UI/Texture/corpLogoLibs/422.png',
 423: 'res:/UI/Texture/corpLogoLibs/423.png',
 424: 'res:/UI/Texture/corpLogoLibs/424.png',
 425: 'res:/UI/Texture/corpLogoLibs/425.png',
 426: 'res:/UI/Texture/corpLogoLibs/426.png',
 427: 'res:/UI/Texture/corpLogoLibs/427.png',
 428: 'res:/UI/Texture/corpLogoLibs/428.png',
 429: 'res:/UI/Texture/corpLogoLibs/429.png',
 430: 'res:/UI/Texture/corpLogoLibs/430.png',
 431: 'res:/UI/Texture/corpLogoLibs/431.png',
 432: 'res:/UI/Texture/corpLogoLibs/432.png',
 433: 'res:/UI/Texture/corpLogoLibs/433.png',
 434: 'res:/UI/Texture/corpLogoLibs/434.png',
 435: 'res:/UI/Texture/corpLogoLibs/435.png',
 436: 'res:/UI/Texture/corpLogoLibs/436.png',
 437: 'res:/UI/Texture/corpLogoLibs/437.png',
 438: 'res:/UI/Texture/corpLogoLibs/438.png',
 439: 'res:/UI/Texture/corpLogoLibs/439.png',
 440: 'res:/UI/Texture/corpLogoLibs/440.png',
 441: 'res:/UI/Texture/corpLogoLibs/441.png',
 442: 'res:/UI/Texture/corpLogoLibs/442.png',
 443: 'res:/UI/Texture/corpLogoLibs/443.png',
 444: 'res:/UI/Texture/corpLogoLibs/444.png',
 445: 'res:/UI/Texture/corpLogoLibs/445.png',
 446: 'res:/UI/Texture/corpLogoLibs/446.png',
 447: 'res:/UI/Texture/corpLogoLibs/447.png',
 448: 'res:/UI/Texture/corpLogoLibs/448.png',
 449: 'res:/UI/Texture/corpLogoLibs/449.png',
 450: 'res:/UI/Texture/corpLogoLibs/450.png',
 451: 'res:/UI/Texture/corpLogoLibs/451.png',
 452: 'res:/UI/Texture/corpLogoLibs/452.png',
 453: 'res:/UI/Texture/corpLogoLibs/453.png',
 454: 'res:/UI/Texture/corpLogoLibs/454.png',
 455: 'res:/UI/Texture/corpLogoLibs/455.png',
 456: 'res:/UI/Texture/corpLogoLibs/456.png',
 457: 'res:/UI/Texture/corpLogoLibs/457.png',
 458: 'res:/UI/Texture/corpLogoLibs/458.png',
 459: 'res:/UI/Texture/corpLogoLibs/459.png',
 460: 'res:/UI/Texture/corpLogoLibs/460.png',
 461: 'res:/UI/Texture/corpLogoLibs/461.png',
 462: 'res:/UI/Texture/corpLogoLibs/462.png',
 463: 'res:/UI/Texture/corpLogoLibs/463.png',
 464: 'res:/UI/Texture/corpLogoLibs/464.png',
 465: 'res:/UI/Texture/corpLogoLibs/465.png',
 466: 'res:/UI/Texture/corpLogoLibs/466.png',
 467: 'res:/UI/Texture/corpLogoLibs/467.png',
 468: 'res:/UI/Texture/corpLogoLibs/468.png',
 469: 'res:/UI/Texture/corpLogoLibs/469.png',
 470: 'res:/UI/Texture/corpLogoLibs/470.png',
 471: 'res:/UI/Texture/corpLogoLibs/471.png',
 472: 'res:/UI/Texture/corpLogoLibs/472.png',
 473: 'res:/UI/Texture/corpLogoLibs/473.png',
 474: 'res:/UI/Texture/corpLogoLibs/474.png',
 475: 'res:/UI/Texture/corpLogoLibs/475.png',
 476: 'res:/UI/Texture/corpLogoLibs/476.png',
 477: 'res:/UI/Texture/corpLogoLibs/477.png',
 478: 'res:/UI/Texture/corpLogoLibs/478.png',
 479: 'res:/UI/Texture/corpLogoLibs/479.png',
 480: 'res:/UI/Texture/corpLogoLibs/480.png',
 481: 'res:/UI/Texture/corpLogoLibs/481.png',
 482: 'res:/UI/Texture/corpLogoLibs/482.png',
 483: 'res:/UI/Texture/corpLogoLibs/483.png',
 484: 'res:/UI/Texture/corpLogoLibs/484.png',
 485: 'res:/UI/Texture/corpLogoLibs/485.png',
 486: 'res:/UI/Texture/corpLogoLibs/486.png',
 487: 'res:/UI/Texture/corpLogoLibs/487.png',
 488: 'res:/UI/Texture/corpLogoLibs/488.png',
 489: 'res:/UI/Texture/corpLogoLibs/489.png',
 490: 'res:/UI/Texture/corpLogoLibs/490.png',
 491: 'res:/UI/Texture/corpLogoLibs/491.png',
 492: 'res:/UI/Texture/corpLogoLibs/492.png',
 493: 'res:/UI/Texture/corpLogoLibs/493.png',
 494: 'res:/UI/Texture/corpLogoLibs/494.png',
 495: 'res:/UI/Texture/corpLogoLibs/495.png',
 496: 'res:/UI/Texture/corpLogoLibs/496.png',
 497: 'res:/UI/Texture/corpLogoLibs/497.png',
 498: 'res:/UI/Texture/corpLogoLibs/498.png',
 499: 'res:/UI/Texture/corpLogoLibs/499.png',
 500: 'res:/UI/Texture/corpLogoLibs/500.png',
 501: 'res:/UI/Texture/corpLogoLibs/501.png',
 502: 'res:/UI/Texture/corpLogoLibs/502.png',
 503: 'res:/UI/Texture/corpLogoLibs/503.png',
 504: 'res:/UI/Texture/corpLogoLibs/504.png',
 505: 'res:/UI/Texture/corpLogoLibs/505.png',
 506: 'res:/UI/Texture/corpLogoLibs/506.png',
 507: 'res:/UI/Texture/corpLogoLibs/507.png',
 508: 'res:/UI/Texture/corpLogoLibs/508.png',
 509: 'res:/UI/Texture/corpLogoLibs/509.png',
 510: 'res:/UI/Texture/corpLogoLibs/510.png',
 511: 'res:/UI/Texture/corpLogoLibs/511.png',
 512: 'res:/UI/Texture/corpLogoLibs/512.png',
 513: 'res:/UI/Texture/corpLogoLibs/513.png',
 514: 'res:/UI/Texture/corpLogoLibs/514.png',
 515: 'res:/UI/Texture/corpLogoLibs/515.png',
 516: 'res:/UI/Texture/corpLogoLibs/516.png',
 517: 'res:/UI/Texture/corpLogoLibs/517.png',
 518: 'res:/UI/Texture/corpLogoLibs/518.png',
 519: 'res:/UI/Texture/corpLogoLibs/519.png',
 520: 'res:/UI/Texture/corpLogoLibs/520.png',
 521: 'res:/UI/Texture/corpLogoLibs/521.png',
 522: 'res:/UI/Texture/corpLogoLibs/522.png',
 523: 'res:/UI/Texture/corpLogoLibs/523.png',
 524: 'res:/UI/Texture/corpLogoLibs/524.png',
 525: 'res:/UI/Texture/corpLogoLibs/525.png',
 526: 'res:/UI/Texture/corpLogoLibs/526.png',
 527: 'res:/UI/Texture/corpLogoLibs/527.png',
 528: 'res:/UI/Texture/corpLogoLibs/528.png',
 529: 'res:/UI/Texture/corpLogoLibs/529.png',
 530: 'res:/UI/Texture/corpLogoLibs/530.png',
 531: 'res:/UI/Texture/corpLogoLibs/531.png',
 532: 'res:/UI/Texture/corpLogoLibs/532.png',
 533: 'res:/UI/Texture/corpLogoLibs/533.png',
 534: 'res:/UI/Texture/corpLogoLibs/534.png',
 535: 'res:/UI/Texture/corpLogoLibs/535.png',
 536: 'res:/UI/Texture/corpLogoLibs/536.png',
 537: 'res:/UI/Texture/corpLogoLibs/537.png',
 538: 'res:/UI/Texture/corpLogoLibs/538.png',
 539: 'res:/UI/Texture/corpLogoLibs/539.png',
 540: 'res:/UI/Texture/corpLogoLibs/540.png',
 541: 'res:/UI/Texture/corpLogoLibs/541.png',
 542: 'res:/UI/Texture/corpLogoLibs/542.png',
 543: 'res:/UI/Texture/corpLogoLibs/543.png',
 544: 'res:/UI/Texture/corpLogoLibs/544.png',
 545: 'res:/UI/Texture/corpLogoLibs/545.png',
 546: 'res:/UI/Texture/corpLogoLibs/546.png',
 547: 'res:/UI/Texture/corpLogoLibs/547.png',
 548: 'res:/UI/Texture/corpLogoLibs/548.png',
 549: 'res:/UI/Texture/corpLogoLibs/549.png',
 550: 'res:/UI/Texture/corpLogoLibs/550.png',
 551: 'res:/UI/Texture/corpLogoLibs/551.png',
 552: 'res:/UI/Texture/corpLogoLibs/552.png',
 553: 'res:/UI/Texture/corpLogoLibs/553.png',
 554: 'res:/UI/Texture/corpLogoLibs/554.png',
 555: 'res:/UI/Texture/corpLogoLibs/555.png',
 556: 'res:/UI/Texture/corpLogoLibs/556.png',
 557: 'res:/UI/Texture/corpLogoLibs/557.png',
 558: 'res:/UI/Texture/corpLogoLibs/558.png',
 559: 'res:/UI/Texture/corpLogoLibs/559.png',
 560: 'res:/UI/Texture/corpLogoLibs/560.png',
 561: 'res:/UI/Texture/corpLogoLibs/561.png',
 562: 'res:/UI/Texture/corpLogoLibs/562.png',
 563: 'res:/UI/Texture/corpLogoLibs/563.png',
 564: 'res:/UI/Texture/corpLogoLibs/564.png',
 565: 'res:/UI/Texture/corpLogoLibs/565.png',
 566: 'res:/UI/Texture/corpLogoLibs/566.png',
 567: 'res:/UI/Texture/corpLogoLibs/567.png',
 568: 'res:/UI/Texture/corpLogoLibs/568.png',
 569: 'res:/UI/Texture/corpLogoLibs/569.png',
 570: 'res:/UI/Texture/corpLogoLibs/570.png',
 571: 'res:/UI/Texture/corpLogoLibs/571.png',
 572: 'res:/UI/Texture/corpLogoLibs/572.png',
 573: 'res:/UI/Texture/corpLogoLibs/573.png',
 574: 'res:/UI/Texture/corpLogoLibs/574.png',
 575: 'res:/UI/Texture/corpLogoLibs/575.png',
 576: 'res:/UI/Texture/corpLogoLibs/576.png',
 577: 'res:/UI/Texture/corpLogoLibs/577.png'}
CORPLOGO_BLEND = 1
CORPLOGO_SOLID = 2
CORPLOGO_GRADIENT = 3
graphicCorpLogoLibColors = {671: ((0.125, 0.125, 0.125, 1.0), CORPLOGO_SOLID),
 672: ((0.59, 0.5, 0.35, 1.0), CORPLOGO_GRADIENT),
 673: ((0.66, 0.83, 1.0, 1.0), CORPLOGO_BLEND),
 674: ((1.0, 1.0, 1.0, 1.0), CORPLOGO_BLEND),
 675: ((0.29, 0.29, 0.29, 1.0), CORPLOGO_GRADIENT),
 676: ((0.66, 1.04, 2.0, 1.0), CORPLOGO_BLEND),
 677: ((2.0, 1.4, 0.5, 1.0), CORPLOGO_BLEND),
 678: ((0.57, 0.6, 0.6, 1.0), CORPLOGO_BLEND),
 679: ((1.0, 0.47, 0.0, 1.0), CORPLOGO_BLEND),
 680: ((0.59, 0.0, 0.0, 1.0), CORPLOGO_BLEND),
 681: ((0.49, 0.5, 0.5, 1.0), CORPLOGO_GRADIENT),
 682: ((0.0, 0.0, 0.0, 0.5), CORPLOGO_SOLID),
 683: ((0.49, 0.5, 0.5, 0.41), CORPLOGO_SOLID),
 684: ((0.91, 0.91, 0.91, 1.0), CORPLOGO_SOLID),
 685: ((1.0, 0.7, 0.24, 1.0), CORPLOGO_SOLID)}
CORPLOGO_DEFAULT_COLOR = ((1.0, 1.0, 1.0, 1.0), CORPLOGO_BLEND)
iconDuration = 1392
iconFemale = 3267
iconMale = 3268
iconModuleArmorRepairer = 21426
iconModuleMutadaptiveArmorRepairer = 22091
iconModuleDroneCommand = 2987
iconModuleECCMProjector = 110
iconModuleECM = 109
iconModuleEnergyNeutralizer = 1283
iconModuleEnergyTransfer = 1035
iconModuleFocusedWarpScrambler = 21489
iconModuleGuidanceDisruptor = 21437
iconModuleHullRepairer = 21428
iconModuleNosferatu = 1029
iconModuleRemoteTracking = 3346
iconModuleSensorBooster = 74
iconModuleSensorDamper = 105
iconModuleShieldBooster = 86
iconModuleStasisWeb = 1284
iconModuleTargetPainter = 2983
iconModuleTrackingDisruptor = 1639
iconModuleStasisGrappler = 21581
iconModuleWarpScrambler = 111
iconModuleFighterTackle = 21613
iconModuleWarpScramblerMWD = 3433
iconModuleTethering = 91
iconSkill = 33
iconUnknown = 0
iconWillpower = 3127
iconShieldBurst = 21700
iconArmorBurst = 21687
iconInformationBurst = 21691
iconSkirmishBurst = 21704
iconMiningBurst = 21695
iconTitanGeneratorMulti = 21724
iconIndustrialInvulnerability = 21730
iconNotTethered = 21877
iconWeatherLightning = 21903
iconWeatherXenonGas = 21904
iconWeatherCaustic = 21905
iconWeatherDarkness = 21906
iconWeatherInfernal = 21907
iconAoeBioluminescence = 21936
iconAoeCausticCloud = 21937
iconAoeFilamentCloud = 21938
iconAoePointDefense = 21939
iconAoePulseBattery = 21941
iconAoeDamageBoost = 10883
iconCloakingDevice = 2106
iconLinkedToESSReserveBank = 24809
iconLinkedToESSMainBank = 24809
iconLinkedToAnalysisBeacon = 24926
iconDoomsday = 2934
iconDeathZoneProtected = 25801
iconDeathZoneGracePriod = 25802
iconDeathZoneDamage = 25803
iconBountyHunting = 25862
iconLinkedToTowGameObjective = 25870
iconTractorBeam = 2986
iconBreacherPod = 26395
iconLinkedToTraceGate = 26684
invulnerabilityDocking = 5500
invulnerabilityJumping = 4000
invulnerabilityRestoring = 60000
invulnerabilityUndocking = 30000
invulnerabilityWarpingIn = 10000
invulnerabilityWarpingOut = 5000
invulnerabilityRecloning = 60000
jumpRadiusFactor = 130
jumpRadiusRandom = 15000
lifetimeOfDefaultContainer = 120
lifetimeOfDurableContainers = 43200
lockedContainerAccessTime = 180000
maxBoardingDistance = 6550
maxBuildDistance = 10000
maxCargoContainerTransferDistance = 2500
maxConfigureDistance = 5000
maxDockingDistance = 50000
maxDungeonPlacementDistanceInCentiAU = 300
maxDungeonPlacementDistanceFromTheSunInCentiAU = 0.4
maxItemCountPerLocation = 1000
maxPetitionsPerDay = 2
maxSelfDestruct = 15000
maxStargateJumpingDistance = 2500
maxWormholeEnterDistance = 5000
maxWarpEndDistance = 100000
maxDroneAssist = 50
maxApproachDistance = 10000000
maxFleetBroadcastTargetDistance = 10000000
minAutoPilotWarpInDistance = 10000
minCloakingDistance = 2000
minDungeonPlacementDistanceInCentiAU = 25
minDungeonPlacementDistanceFromTheSunInCentiAU = 0.0666
minJumpDriveDistance = 100000
minSpawnContainerDelay = 60000
minSpecialTutorialSpawnContainerDelay = 60000
minWarpDistance = 150000
minWarpEndDistance = 0
minCaptureBracketDistance = 200000
mktMinimumFee = 100
mktMinimumSccSurcharge = 25
mktModificationDelay = 300
mktOrderCancelled = 3
mktOrderExpired = 2
npcCorpMax = 1999999
npcCorpMin = 1000000
npcDivisionAccounting = 1
npcDivisionAdministration = 2
npcDivisionAdvisory = 3
npcDivisionArchives = 4
npcDivisionAstrosurveying = 5
npcDivisionCommand = 6
npcDivisionDistribution = 7
npcDivisionFinancial = 8
npcDivisionIntelligence = 9
npcDivisionInternalSecurity = 10
npcDivisionLegal = 11
npcDivisionManufacturing = 12
npcDivisionMarketing = 13
npcDivisionMining = 14
npcDivisionPersonnel = 15
npcDivisionProduction = 16
npcDivisionPublicRelations = 17
npcDivisionRD = 18
npcDivisionSecurity = 19
npcDivisionStorage = 20
npcDivisionSurveillance = 21
onlineCapacitorChargeRatio = 95
onlineCapacitorRemainderRatio = 33
outlawSecurityStatus = -5
petitionMaxChatLogSize = 200000
petitionMaxCombatLogSize = 200000
posShieldStartLevel = 0.505
posMaxShieldPercentageForWatch = 0.95
posMinDamageDiffToPersist = 0.05
rentalPeriodOffice = 30
secLevelForBounty = -1
sentryTargetSwitchDelay = 40000
shipHidingCombatDelay = 120000
shipHidingDelay = 60000
shipHidingPvpCombatDelay = 900000
simulationTimeStep = 1000
skillEventGift = 24
skillEventCharCreation = 33
skillEventClonePenalty = 34
skillEventGMGive = 39
skillEventHaltedAccountLapsed = 260
skillEventTaskMaster = 35
skillEventTrainingCancelled = 38
skillEventTrainingComplete = 37
skillEventTrainingStarted = 36
skillEventQueueTrainingCompleted = 53
skillEventSkillInjected = 56
skillEventFreeSkillPointsUsed = 307
skillEventGMReverseFreeSkillPointsUsed = 309
skillEventSkillRemoved = 177
skillEventSkillExtracted = 431
skillEventSkillExtractionReverted = 432
solarsystemTimeout = 86400
sovereigntyDisruptorAnchorRange = 20000
sovereigntyDisruptorAnchorRangeMinBetween = 45000
starbaseSecurityLimit = 800
terminalExplosionDelay = 60
warpJitterRadius = 2500
warpSpeedToAUPerSecond = 0.001
solarSystemPolaris = 30000380
solarSystemZarzakh = 30100000
maxLoyaltyStoreBulkOffers = 100
approachRange = 50
contestionStateNone = 0
contestionStateContested = 1
contestionStateVulnerable = 2
contestionStateCaptured = 3
medalMinNameLength = 3
medalMaxNameLength = 100
medalMaxDescriptionLength = 1000
medalMinDescriptionLength = 10
medalStatus = {1: 'deleted',
 2: 'private',
 3: 'public'}
respecTimeInterval = 365 * DAY
respecMinimumAttributeValue = 17
respecMaximumAttributeValue = 27
respecTotalRespecPoints = 99
remoteHomeStationChangeInterval = 365 * DAY
shipNotWarping = 0
shipWarping = 1
shipAligning = 2
warpTypeNone = 0
warpTypeRegular = 1
warpTypeForced = 2
planetResourceScanDistance = 1000000000
planetResourceProximityDistant = 0
planetResourceProximityRegion = 1
planetResourceProximityConstellation = 2
planetResourceProximitySystem = 3
planetResourceProximityPlanet = 4
planetResourceProximityLimits = [(2, 6),
 (4, 10),
 (6, 15),
 (10, 20),
 (15, 30)]
planetResourceScanningRanges = [9.0,
 7.0,
 5.0,
 3.0,
 1.0]
planetResourceUpdateTime = 1 * HOUR
planetResourceMaxValue = 1.21
MAX_DISPLAY_QUALITY = planetResourceMaxValue * 255 * 0.5
skillsWithHintPerMinute = 50
INVALID_WORMHOLE_CLASS_ID = 0
HIGH_SEC_WORMHOLE_CLASS_ID = 7
LOW_SEC_WORMHOLE_CLASS_ID = 8
ZERO_SEC_WORMHOLE_CLASS_ID = 9
TRIGLAVIAN_WORMHOLE_CLASS_ID = 25
WH_SLIM_MAX_SHIP_MASS_SMALL = 1
WH_SLIM_MAX_SHIP_MASS_MEDIUM = 2
WH_SLIM_MAX_SHIP_MASS_LARGE = 3
WH_SLIM_MAX_SHIP_MASS_VERYLARGE = 4
agentMissionAccepted = 'accepted'
agentMissionCompleted = 'completed'
agentMissionDeclined = 'declined'
agentMissionDungeonMoved = 'dungeon_moved'
agentMissionFailed = 'failed'
agentMissionModified = 'modified'
agentMissionOffered = 'offered'
agentMissionOfferDeclined = 'offer_declined'
agentMissionOfferExpired = 'offer_expired'
agentMissionOfferRemoved = 'offer_removed'
agentMissionProlonged = 'prolong'
agentMissionQuit = 'quit'
agentMissionResearchStarted = 'research_started'
agentMissionResearchUpdatePPD = 'research_update_ppd'
agentMissionReset = 'reset'
agentTalkToMissionCompleted = 'talk_to_completed'
agentMissionStateAllocated = 0
agentMissionStateOffered = 1
agentMissionStateAccepted = 2
agentMissionStateFailed = 3
agentMissionStateCompleted = 4
agentMissionStateDeclined = 5
agentMissionStateQuit = 6
agentMissionStateCantReplay = 7
agentMissionDungeonStarted = 0
agentMissionDungeonCompleted = 1
agentMissionDungeonFailed = 2
missionTypeTrade = 'UI/Agents/MissionTypes/Trade'
missionTypeCourier = 'UI/Agents/MissionTypes/Courier'
missionTypeEncounter = 'UI/Agents/MissionTypes/Encounter'
missionTypeMining = 'UI/Agents/MissionTypes/Mining'
missionTypeStoryline = 'UI/Agents/MissionTypes/Storyline'
missionTypeStorylineMining = 'UI/Agents/MissionTypes/StorylineMining'
missionTypeStorylineTrade = 'UI/Agents/MissionTypes/StorylineTrade'
missionTypeStorylineEncounter = 'UI/Agents/MissionTypes/StorylineEncounter'
missionTypeStorylineCourier = 'UI/Agents/MissionTypes/StorylineCourier'
missionTypeStorylineInteraction = 'UI/Agents/MissionTypes/StorylineAgentInteraction'
missionTypeEpicArc = 'UI/Agents/MissionTypes/EpicArc'
missionTypeEpicArcMining = 'UI/Agents/MissionTypes/EpicArcMining'
missionTypeEpicArcTrade = 'UI/Agents/MissionTypes/EpicArcTrade'
missionTypeEpicArcEncounter = 'UI/Agents/MissionTypes/EpicArcEncounter'
missionTypeEpicArcCourier = 'UI/Agents/MissionTypes/EpicArcCourier'
missionTypeEpicArcInteraction = 'UI/Agents/MissionTypes/EpicArcAgentInteraction'
missionTypeEpicArcTalkToAgent = 'UI/Agents/MissionTypes/EpicArcTalkToAgent'
missionTypeResearch = 'UI/Agents/MissionTypes/Research'
missionTypeResearchEncounter = 'UI/Agents/MissionTypes/ResearchEncounter'
missionTypeResearchCourier = 'UI/Agents/MissionTypes/ResearchCourier'
missionTypeResearchTrade = 'UI/Agents/MissionTypes/ResearchTrade'
missionTypeHeraldry = 'UI/Agents/MissionTypes/Heraldry'
rookieAgentList = [3018681,
 3018821,
 3018822,
 3018823,
 3018824,
 3018680,
 3018817,
 3018818,
 3018819,
 3018820,
 3018682,
 3018809,
 3018810,
 3018811,
 3018812,
 3018678,
 3018837,
 3018838,
 3018839,
 3018840,
 3018679,
 3018841,
 3018842,
 3018843,
 3018844,
 3018677,
 3018845,
 3018846,
 3018847,
 3018848,
 3018676,
 3018825,
 3018826,
 3018827,
 3018828,
 3018675,
 3018805,
 3018806,
 3018807,
 3018808,
 3018672,
 3018801,
 3018802,
 3018803,
 3018804,
 3018684,
 3018829,
 3018830,
 3018831,
 3018832,
 3018685,
 3018813,
 3018814,
 3018815,
 3018816,
 3018683,
 3018833,
 3018834,
 3018835,
 3018836]
epicArcNPEArcs = [64,
 67,
 68,
 69,
 70,
 71,
 72,
 73,
 74,
 75,
 76,
 77]
petitionPropertyAgentMissionReq = 2
petitionPropertyAgentMissionNoReq = 3
petitionPropertyAgents = 4
petitionPropertyShipID = 5
petitionPropertyStarbaseLocation = 6
petitionPropertyCharacter = 7
petitionPropertyUserCharacters = 8
petitionPropertyWebAddress = 9
petitionPropertyCorporations = 10
petitionPropertyChrAgent = 11
petitionPropertyOS = 12
petitionPropertyChrEpicArc = 13
marketCategoryBluePrints = 2
marketCategoryShips = 4
marketCategoryShipEquipment = 9
marketCategoryAmmunitionAndCharges = 11
marketCategoryTradeGoods = 19
marketCategoryImplantesAndBoosters = 24
marketCategorySkills = 150
marketCategoryDrones = 157
marketCategoryManufactureAndResearch = 475
marketCategoryStarBaseStructures = 477
marketCategoryShipModifications = 955
marketCategoryStructureEquipment = 2202
marketCategoryStructureModifications = 2203
marketCategorySpecialEditionAssets = 1659
marketGroupMutaplasmids = 2436
maxCharFittings = 500
maxCorpFittings = 600
maxAllianceFittings = 600
maxLengthFittingName = 50
maxLengthFittingDescription = 500
maxNumFittingItems = 255
dungeonCompletionDestroyLCS = 0
dungeonCompletionDestroyGuards = 1
dungeonCompletionDestroyLCSandGuards = 2
defaultPadding = 4
sovereigntyClaimStructuresGroups = (groupSovereigntyClaimMarkers, groupSovereigntyDisruptionStructures)
sovereigntyStructuresGroups = (groupSovereigntyClaimMarkers,
 groupSovereigntyDisruptionStructures,
 groupSovereigntyStructures,
 groupInfrastructureHub)
mailingListBlocked = 0
mailingListAllowed = 1
mailingListMemberMuted = 0
mailingListMemberDefault = 1
mailingListMemberOperator = 2
mailingListMemberOwner = 3
ALLIANCE_SERVICE_MOD = 200
CORPNODE_MOD = 200
CHARNODE_MOD = 128
PLANETARYMGR_MOD = 128
BATTLEINSTANCEMANANGER_MOD = 128
BATTLEQUICKMATCHER_MOD = 64
mailTypeMail = 1
mailTypeNotifications = 2
mailStatusMaskRead = 1
mailStatusMaskReplied = 2
mailStatusMaskForwarded = 4
mailStatusMaskTrashed = 8
mailStatusMaskDraft = 16
mailStatusMaskAutomated = 32
mailLabelInbox = 1
mailLabelSent = 2
mailLabelCorporation = 4
mailLabelAlliance = 8
mailLabelsSystem = mailLabelInbox + mailLabelSent + mailLabelCorporation + mailLabelAlliance
mailMaxRecipients = 50
mailMaxGroups = 1
mailMaxSubjectSize = 150
mailMaxBodySize = 8000
mailMaxTaggedBodySize = 10000
mailMaxLabelSize = 40
mailMaxNumLabels = 25
mailMaxPerPage = 100
mailTrialAccountTimer = 1
mailMaxMessagePerMinute = 5
mailinglistMaxMembers = 3000
mailinglistMaxMembersUpdated = 1000
mailingListMaxNameSize = 60
notificationsMaxUpdated = 100
calendarMonday = 0
calendarTuesday = 1
calendarWednesday = 2
calendarThursday = 3
calendarFriday = 4
calendarSaturday = 5
calendarSunday = 6
calendarJanuary = 1
calendarFebruary = 2
calendarMarch = 3
calendarApril = 4
calendarMay = 5
calendarJune = 6
calendarJuly = 7
calendarAugust = 8
calendarSeptember = 9
calendarOctober = 10
calendarNovember = 11
calendarDecember = 12
calendarNumDaysInWeek = 7
calendarTagPersonal = 1
calendarTagCorp = 2
calendarTagAlliance = 4
calendarTagCCP = 8
calendarTagAutomated = 16
calendarViewRangeInMonths = 12
calendarMaxTitleSize = 40
calendarMaxDescrSize = 500
calendarMaxInvitees = 50
calendarMaxInviteeDisplayed = 100
calendarAutoEventPosFuel = 1
calendarAutoEventMoonExtaction = 2
eventResponseUninvited = 0
eventResponseDeleted = 1
eventResponseDeclined = 2
eventResponseUndecided = 3
eventResponseAccepted = 4
eventResponseMaybe = 5
calendarStartYear = 2003
soundNotifications = {'shield': {'defaultThreshold': 0.25,
            'soundEventName': 'ui_notify_negative_05_play',
            'thresholdSettingsName': 'shieldThreshold',
            'localizationLabel': 'UI/Inflight/NotifySettingsWindow/ShieldAlertLevel',
            'defaultStatus': 1},
 'armour': {'defaultThreshold': 0.4,
            'soundEventName': 'ui_notify_negative_03_play',
            'localizationLabel': 'UI/Inflight/NotifySettingsWindow/ArmorAlertLevel',
            'defaultStatus': 1},
 'hull': {'defaultThreshold': 0.95,
          'soundEventName': 'ui_notify_negative_01_play',
          'localizationLabel': 'UI/Inflight/NotifySettingsWindow/HullAlertLevel',
          'defaultStatus': 1},
 'capacitor': {'defaultThreshold': 0.3,
               'soundEventName': 'ui_notify_negative_04_play',
               'localizationLabel': 'UI/Inflight/NotifySettingsWindow/CapacitorAlertLevel',
               'defaultStatus': 1},
 'cargoHold': {'defaultThreshold': 0.2,
               'soundEventName': 'ui_notify_positive_08_play',
               'localizationLabel': 'UI/Inflight/NotifySettingsWindow/CargoHoldAlertLevel',
               'defaultStatus': 0},
 'NameToIndices': {'shield': 0,
                   'armour': 1,
                   'hull': 2,
                   'capacitor': 3,
                   'cargoHold': 4}}
costReceiverTypeOwner = 0
costReceiverTypeMailingList = 1
costContactMax = 1000000
contactHighStanding = 10
contactGoodStanding = 5
contactNeutralStanding = 0
contactBadStanding = -5
contactHorribleStanding = -10
contactAll = 100
contactBlocked = 200
contactWatchlist = 300
contactNotifications = 400
developmentIndices = [attributeDevIndexMilitary,
 attributeDevIndexIndustrial,
 attributeDevIndexSovereignty,
 attributeDevIndexUpgrade]
sovAudioEventStopOnline = 0
sovAudioEventStopDestroyed = 1
sovAudioEventFlagVulnerable = 2
sovAudioEventFlagDestroyed = 3
sovAudioEventFlagClaimed = 4
sovAudioEventOutpostReinforced = 5
sovAudioEventOutpostCaptured = 6
sovAudioEventHubReinforced = 7
sovAudioEventHubDestroyed = 8
sovAudioEventOutpostAttacked = 9
sovAudioEventFiles = {sovAudioEventStopOnline: ('msg_stop_online_play', 'SovAudioMsg_StopOnline'),
 sovAudioEventStopDestroyed: ('msg_stop_destroyed_play', 'SovAudioMsg_StopDestroyed'),
 sovAudioEventFlagVulnerable: ('msg_flag_vulnerable_play', 'SovAudioMsg_FlagVulnerable'),
 sovAudioEventFlagDestroyed: ('msg_flag_destroyed_play', 'SovAudioMsg_FlagDestroyed'),
 sovAudioEventFlagClaimed: ('msg_flag_claimed_play', 'SovAudioMsg_FlagClaimed'),
 sovAudioEventOutpostReinforced: ('msg_outpost_reinforced_play', 'SovAudioMsg_OutpostReinforced'),
 sovAudioEventOutpostCaptured: ('msg_outpost_captureed_play', 'SovAudioMsg_OutpostCaptured'),
 sovAudioEventOutpostAttacked: ('msg_outpost_attacked_play', 'SovAudioMsg_OutpostUnderAttack'),
 sovAudioEventHubReinforced: ('msg_hub_reinforced_play', 'SovAudioMsg_HubReinforced'),
 sovAudioEventHubDestroyed: ('msg_hub_destroyed_play', 'SovAudioMsg_HubDestroyed')}
maxLong = 9223372036854775807L
maxContacts = 1024
maxAllianceContacts = 2600
maxContactsPerPage = 50
contactMaxLabelSize = 40
pwnStructureStateAnchored = 'anchored'
pwnStructureStateAnchoring = 'anchoring'
pwnStructureStateOnline = 'online'
pwnStructureStateOnlining = 'onlining'
pwnStructureStateUnanchored = 'unanchored'
pwnStructureStateUnanchoring = 'unanchoring'
pwnStructureStateVulnerable = 'vulnerable'
pwnStructureStateInvulnerable = 'invulnerable'
pwnStructureStateReinforced = 'reinforced'
pwnStructureStateOperating = 'operating'
pwnStructureStateIncapacitated = 'incapacitated'
pwnStructureStateAnchor = 'anchor'
pwnStructureStateUnanchor = 'unanchor'
pwnStructureStateOffline = 'offline'
pwnStructureStateOnlineActive = 'online - active'
pwnStructureStateOnlineStartingUp = 'online - starting up'
piLaunchOrbitDecayTime = DAY * 5
piCargoInOrbit = 0
piCargoDeployed = 1
piCargoClaimed = 2
piCargoDeleted = 3
piSECURITY_BANDS_LABELS = [(0, '[-1;-0.75]'),
 (1, ']-0.75;-0.45]'),
 (2, ']-0.45;-0.25]'),
 (3, ']-0.25;0.0['),
 (4, '[0.0;0.15['),
 (5, '[0.15;0.25['),
 (6, '[0.25;0.35['),
 (7, '[0.35;0.45['),
 (8, '[0.45;0.55['),
 (9, '[0.55;0.65['),
 (10, '[0.65;0.75['),
 (11, '[0.75;1.0]')]
vcPrefixAlliance = 'allianceid'
vcPrefixFleet = 'fleetid'
vcPrefixCorp = 'corpid'
vcPrefixSquad = 'squadid'
vcPrefixWing = 'wingid'
vcPrefixInst = 'inst'
vcPrefixTeam = 'team'
incursionStateWithdrawing = 0
incursionStateMobilizing = 1
incursionStateEstablished = 2
invasionStageScouts = 1
invasionStageOutrift = 2
invasionStageWorldArk = 3
invasionStageRetreat = 4
invasionStageDreadnought = 5
invasionStageTriglavianVictory = 6
invasionStageTriglavianEstablishmentEscalation = 7
invasionStageTriglavianEstablishment = 8
invasionStageScoutsAndPatrols = 9
invasionStageEmpireFortification = 10
invasionStageEmpireFortificationEscalation = 11
invasionStageEmpireFortifiedSystem = 12
invasionStageTriglavianMinorVictory = 13
invasionStageEDENCOMMinorVictory = 14
invasionStageMassiveEDENCOMFortification = 15
invasionStageMassiveTriglavianInvasion = 16
CHAPTER_THREE_NON_FINAL_TALES_NOT_AFFECTED_BY_INFLUENCE = (invasionStageTriglavianMinorVictory,
 invasionStageEDENCOMMinorVictory,
 invasionStageMassiveEDENCOMFortification,
 invasionStageMassiveTriglavianInvasion)
rewardIneligibleReasonTrialAccount = 1
rewardIneligibleReasonInvalidGroup = 2
rewardIneligibleReasonShipCloaked = 3
rewardIneligibleReasonNotInFleet = 4
rewardIneligibleReasonNotBestFleet = 5
rewardIneligibleReasonNotTop5 = 6
rewardIneligibleReasonNotRightAmountOfPlayers = 7
rewardIneligibleReasonTaleAlreadyEnded = 8
rewardIneligibleReasonNotInRange = 9
rewardIneligibleReasonNoISKLost = 10
rewardIneligibleReasonNotTopN = 11
rewardIneligibleReasonLowContribution = 12
rewardPirateFOBIskBounty = 23
rewardInvasions = 26
rewardCriteriaAllSecurityBands = 0
rewardCriteriaHighSecurity = 1
rewardCriteriaLowSecurity = 2
rewardCriteriaNullSecurity = 3
rewardInvalidGroups = {groupCapsule,
 groupShuttle,
 groupRookieship,
 groupPrototypeExplorationShip}
rewardInvalidGroupsLimitedRestrictions = {groupCapsule, groupShuttle, groupPrototypeExplorationShip}
creditsISK = 0
creditsAURUM = 1
creditsDustMPLEX = 2
taleGuristasFOB = 63
taleBloodRaidersFOB = 64
dbMaxCountForIntList = 750
dbMaxCountForBigintList = 350
dbMaxQuantity = 2147483647
singletonBlueprintOriginal = 1
singletonBlueprintCopy = 2
metaGroupUnused = 0
metaGroupTech1 = 1
metaGroupTech2 = 2
metaGroupStoryline = 3
metaGroupFaction = 4
metaGroupOfficer = 5
metaGroupDeadspace = 6
metaGroupTech3 = 14
metaGroupAbyssal = 15
metaGroupPremium = 17
metaGroupLimitedTime = 19
metaGroupStructureTech1 = 54
metaGroupStructureTech2 = 53
metaGroupStructureFaction = 52
metaGroupsUsed = [metaGroupStoryline,
 metaGroupFaction,
 metaGroupOfficer,
 metaGroupDeadspace,
 metaGroupAbyssal]
NCC_MIN_NORMAL_BACKGROUND_ID = 1
DEFAULT_FEMALE_PAPERDOLL_MODEL = 'res:/Graphics/Character/Female/Skeleton/masterSkeletonFemale.gr2'
DEFAULT_MALE_PAPERDOLL_MODEL = 'res:/Graphics/Character/Male/Skeleton/masterSkeletonMale.gr2'
PAPERDOLL_LODS_IN_SEPARATE_FOLDER = True
PAPERDOLL_LOD_RED_FILES = True
CYNOJAM_JAMSHIPS = 1
CYNOJAM_JAMSHIPS_AND_JUMPBRIDGE = 2
completionTypeRookieArcCompletion = 1
GROUP_CAPSULES = 0
GROUP_FRIGATES = 1
GROUP_DESTROYERS = 2
GROUP_CRUISERS = 3
GROUP_BATTLESHIPS = 4
GROUP_BATTLECRUISERS = 5
GROUP_CAPITALSHIPS = 6
GROUP_INDUSTRIALS = 7
GROUP_POS = 8
GROUP_STRUCTURES = 9
OVERVIEW_NORMAL_COLOR = (1.0, 1.0, 1.0)
OVERVIEW_HOSTILE_COLOR = (1.0, 0.1, 0.1)
OVERVIEW_NPC_NEUTRAL_COLOR = (0.3, 0.7, 1.0)
OVERVIEW_AUTO_PILOT_DESTINATION_COLOR = (1.0, 1.0, 0.0)
OVERVIEW_FORBIDDEN_CONTAINER_COLOR = (1.0, 1.0, 0.0)
OVERVIEW_ABANDONED_CONTAINER_COLOR = (0.2, 0.5, 1.0)
OVERVIEW_OWN_SHIP_COLOR = (0.7, 0.7, 0.7)
OVERVIEW_IGNORE_TYPES = (typeUnlitModularEffectBeacon,
 typeChunkSmall,
 typeChunkMedium,
 typeChunkLarge,
 typeChunkExtraLarge,
 typeTriglavianStellarHarvesterPhaseTwo,
 typeTriglavianStellarHarvesterPhaseThree,
 typeTriglavianStellarHarvesterPhaseFour,
 typeEDENCOMStockpileTenshu1,
 typeEDENCOMStockpileTenshu2)
MAX_BOOKMARK_NAME_LENGTH = 100
MAX_BOOKMARK_DESCRIPTION_LENGTH = 3900
MAX_FOLDER_NAME_LENGTH = 40
MAX_FOLDER_DESCRIPTION_LENGTH = 3900
MAX_BOOKMARKS_IN_SHARED_FOLDER = 500
MAX_BOOKMARKS_IN_PERSONAL_FOLDER = 3000
MAX_ACTIVE_SHARED_BOOKMARK_FOLDERS = 3
MAX_ACTIVE_PERSONAL_BOOKMARK_FOLDERS = 5
MAX_CREATED_BOOKMARK_FOLDERS = 30
MAX_KNOWN_BOOKMARK_FOLDERS = 30
MAX_SUBFOLDERS = 30
BOOKMARK_ACTION_THROTTLE_KEY = 'BookmarkActionThrottleKey'
BOOKMARK_THROTTLE_MAX_TIMES = 30
BOOKMARK_THROTTLE_DURATION = MIN
ACCESS_NONE = 0
ACCESS_PERSONAL = 1
ACCESS_VIEW = 2
ACCESS_USE = 3
ACCESS_MANAGE = 4
ACCESS_ADMIN = 5
MAX_DRONE_RECONNECTS = 25
PLAYER_STATUS_ACTIVE = 0
PLAYER_STATUS_AFK = 1
DEFAULT_SIGNATURE_RADIUS = 1000.0
warningISKBuying = 244
CHT_MAX_STRIPPED_INPUT = 253
CHT_MAX_INPUT = CHT_MAX_STRIPPED_INPUT * 2
mapHistoryStatJumps = 1
mapHistoryStatKills = 3
mapHistoryStatFacWarKills = 5
zmetricCounter_EVEOnline = 10
zmetricCounter_EVETrial = 11
MIN_BOUNTY_AMOUNT_CHAR = 1000000
MIN_BOUNTY_AMOUNT_CORP = 20000000
MIN_BOUNTY_AMOUNT_ALLIANCE = 100000000
MAX_BOUNTY_AMOUNT = 100000000000L
containerGroupIDs = {groupWreck,
 groupCargoContainer,
 groupSpawnContainer,
 groupSecureCargoContainer,
 groupAuditLogSecureContainer,
 groupFreightContainer,
 groupDeadspaceOverseersBelongings,
 groupMissionContainer}
WARS_PER_PAGE = 50
GAME_TIME_TYPE_PLEX = 0
GAME_TIME_TYPE_BUDDY = 1
GAME_TIME_TYPE_WINGMAN = 2
GAME_TIME_TYPE_GM = 3
GAME_TIME_TYPE_SIGNUP_BONUS_14 = 4
canFitShipGroups = [1298,
 1299,
 1300,
 1301,
 1872,
 1879,
 1880,
 1881,
 2065,
 2396,
 2476,
 2477,
 2478,
 2479,
 2480,
 2481,
 2482,
 2483,
 2484,
 2485]
canFitShipTypes = [1302,
 1303,
 1304,
 1305,
 1944,
 2103,
 2463,
 2486,
 2487,
 2488,
 2758]
entityMaxSignatureRadiusSmall = 85
entityMaxSignatureRadiusMedium = 240
stationOwnersWithSecurityService = (ownerCONCORD, ownerDED)
defaultDockingView = 'hangar'
legalOffensiveTargetOwnerIDs = {ownerNone,
 ownerSystem,
 ownerUnknown,
 factionUnknown,
 factionTriglavian,
 factionEDENCOM}
microJumpDriveDistance = 100000
IHUB_DAILY_UPKEEP_BASE_COST = 6000000
IHUB_BILLING_DURATION_DAYS = 7
SKILL_TRADING_BUCKET_SIZE = 500000
SKILL_TRADING_FREE_ZONE = 5000000
SKILL_TRADING_LOW_DIMINISH = (50000000, 0.2)
SKILL_TRADING_MEDIUM_DIMINISH = (80000000, 0.4)
SKILL_TRADING_FULL_DIMINISH = 0.7
SKILL_TRADING_MINIMUM_SP_TO_EXTRACT = 5000000 + SKILL_TRADING_BUCKET_SIZE
SKILL_TRADING_MAXIMUM_INJECT_STACK_SIZE = 10000
SKILL_TRADING_SMALL_INJECTOR_DIVISOR = 5
DEFAULT_UNDOCKPOINT_CATEGORY = 'undockPoint'
SUPERCAPITAL_UNDOCKPOINT_CATEGORY = 'undockPointSupercapital'
CAPITAL_UNDOCKPOINT_CATEGORY = 'undockPointCapital'
LARGE_UNDOCKPOINT_CATEGORY = 'undockPointLarge'
SMALL_UNDOCKPOINT_CATEGORY = 'undockPointSmall'
BALL_CUSTOM_INFO_FORMAT_STRING_ACCELERATION_GATE_JUMPING = 'AccelerationGateJumping:{gate_ball_dungeon_object_id}'
BALL_CUSTOM_INFO_ACCELERATION_GATE_JUMPING = 'AccelerationGateJumping:'
PERIMETER_LOOK_DEFAULT = 0
PERIMETER_LOOK_RED = 1
PERIMETER_LOOK_BLUE = 2
PERIMETER_LOOK_GREEN = 3
PERIMETER_LOOK_GOLD = 4
PERIMETER_LOOK_CAPTURE_DEFENDER = 5
PERIMETER_LOOK_CAPTURE_ATTACKER = 6
PERIMETER_LOOK_IDLE = 7
PERIMETER_LOOK_CONTESTED = 10
PERIMETER_LOOK_JOVIAN = 11
PERIMETER_BUBBLE_LOOK_JOVIAN = 0
PERIMETER_BUBBLE_LOOK_RED = 1
PERIMETER_BUBBLE_LOOK_BLUE = 2
PERIMETER_BUBBLE_LOOK_GREEN = 3
PERIMETER_BUBBLE_LOOK_GOLD = 4
PERIMETER_BUBBLE_LOOK_TURQUOISE = 5
maximumCharacterNameLength = 37
SECURE_URL_FLAG = 'client-secure-url-string-flag'
SECURE_URL_FALLBACK = 'https://secure.eveonline.com'
STORE_URL_FLAG = 'client-store-url-string-flag'
STORE_URL_FALLBACK = 'https://store.eveonline.com'
