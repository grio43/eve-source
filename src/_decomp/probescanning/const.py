#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\const.py
import inventorycommon.const
import dogma.const
MAX_PROBES = 8
probeStateInactive = 0
probeStateIdle = 1
probeStateMoving = 2
probeStateWarping = 3
probeStateScanning = 4
probeStateReturning = 5
probeResultPerfect = 1.0
probeResultInformative = 0.75
probeResultGood = 0.25
probeResultUnusable = 0.001
scanDifficultyVeryEasy = 1
scanDifficultyEasy = 2
scanDifficultyMedium = 3
scanDifficultyHard = 4
scanDifficultyVeryHard = 5
scanProbeNumberOfRangeSteps = 8
scanProbeBaseNumberOfProbes = 4
AU = 149597870700.0
MAX_PROBE_DIST_FROM_SUN_SQUARED = (AU * 250) ** 2
probeScanGroupStarBase = 0
probeScanGroupScrap = 1
probeScanGroupFighters = 2
probeScanGroupSignatures = 3
probeScanGroupShips = 4
probeScanGroupStructures = 5
probeScanGroupDrones = 6
probeScanGroupCelestials = 7
probeScanGroupAnomalies = 8
probeScanGroupCharges = 9
probeScanGroupNPCs = 10
probeScanGroupOrbitals = 11
probeScanGroupDeployable = 12
probeScanGroupSovereignty = 13
probeScanGroupAbyssalTraces = 14
coreScannerProbeTypeID = 30013
combatScannerProbeTypeID = 30028
probeLauncherTypeID = 17938
expandedProbeLauncherTypeID = 18639
probeScanGroups = {}
probeScanGroups[probeScanGroupScrap] = {inventorycommon.const.groupAuditLogSecureContainer,
 inventorycommon.const.groupBiomass,
 inventorycommon.const.groupCargoContainer,
 inventorycommon.const.groupFreightContainer,
 inventorycommon.const.groupSecureCargoContainer,
 inventorycommon.const.groupWreck}
probeScanGroups[probeScanGroupSignatures] = {inventorycommon.const.groupCosmicSignature}
probeScanGroups[probeScanGroupAnomalies] = {inventorycommon.const.groupCosmicAnomaly}
probeScanGroups[probeScanGroupShips] = {inventorycommon.const.groupAssaultFrigate,
 inventorycommon.const.groupAttackBattlecruiser,
 inventorycommon.const.groupBattlecruiser,
 inventorycommon.const.groupBattleship,
 inventorycommon.const.groupBlackOps,
 inventorycommon.const.groupBlockadeRunner,
 inventorycommon.const.groupCapitalIndustrialShip,
 inventorycommon.const.groupCapsule,
 inventorycommon.const.groupCarrier,
 inventorycommon.const.groupCombatReconShip,
 inventorycommon.const.groupCommandDestroyer,
 inventorycommon.const.groupCommandShip,
 inventorycommon.const.groupCovertOps,
 inventorycommon.const.groupCruiser,
 inventorycommon.const.groupDestroyer,
 inventorycommon.const.groupDreadnought,
 inventorycommon.const.groupLancerDreadnought,
 inventorycommon.const.groupElectronicAttackShips,
 inventorycommon.const.groupEliteBattleship,
 inventorycommon.const.groupExhumer,
 inventorycommon.const.groupExpeditionFrigate,
 inventorycommon.const.groupForceReconShip,
 inventorycommon.const.groupForceAux,
 inventorycommon.const.groupFreighter,
 inventorycommon.const.groupFrigate,
 inventorycommon.const.groupHeavyAssaultCruiser,
 inventorycommon.const.groupHeavyInterdictors,
 inventorycommon.const.groupIndustrial,
 inventorycommon.const.groupIndustrialCommandShip,
 inventorycommon.const.groupInterceptor,
 inventorycommon.const.groupInterdictor,
 inventorycommon.const.groupJumpFreighter,
 inventorycommon.const.groupLogisticsFrigate,
 inventorycommon.const.groupLogistics,
 inventorycommon.const.groupMarauders,
 inventorycommon.const.groupMiningBarge,
 inventorycommon.const.groupSupercarrier,
 inventorycommon.const.groupPrototypeExplorationShip,
 inventorycommon.const.groupRookieship,
 inventorycommon.const.groupShuttle,
 inventorycommon.const.groupStealthBomber,
 inventorycommon.const.groupTacticalDestroyer,
 inventorycommon.const.groupTitan,
 inventorycommon.const.groupTransportShip,
 inventorycommon.const.groupStrategicCruiser,
 inventorycommon.const.groupFlagCruiser}
probeScanGroups[probeScanGroupAbyssalTraces] = [inventorycommon.const.groupAbyssalTraces]
probeScanGroups[probeScanGroupNPCs] = [inventorycommon.const.groupNpcBattleship,
 inventorycommon.const.groupNpcCruiser,
 inventorycommon.const.groupNpcFrigate,
 inventorycommon.const.groupNpcMiningBarge,
 inventorycommon.const.groupNpcMiningExhumer,
 inventorycommon.const.groupNpcMiningFrigate,
 inventorycommon.const.groupNpcMiningHauler,
 inventorycommon.const.groupNpcForceAuxiliary,
 inventorycommon.const.groupNpcDreadnought,
 inventorycommon.const.groupNpcTitan,
 inventorycommon.const.groupBoss,
 inventorycommon.const.groupInvasionNPCs,
 inventorycommon.const.groupInvasionAmarrNPCs,
 inventorycommon.const.groupInvasionCaldariNPCs,
 inventorycommon.const.groupInvasionGallenteNPCs,
 inventorycommon.const.groupInvasionMinmatarNPCs,
 inventorycommon.const.groupNPCCapsule,
 inventorycommon.const.groupInsurgencyRoamingPirateNPCs,
 inventorycommon.const.groupInsurgencyRoamingEnforcerNPCs]
probeScanGroups[probeScanGroupStarBase] = {inventorycommon.const.groupAssemblyArray,
 inventorycommon.const.groupControlTower,
 inventorycommon.const.groupCorporateHangarArray,
 inventorycommon.const.groupElectronicWarfareBattery,
 inventorycommon.const.groupEnergyNeutralizingBattery,
 inventorycommon.const.groupJumpPortalArray,
 inventorycommon.const.groupMobileHybridSentry,
 inventorycommon.const.groupMobileLaboratory,
 inventorycommon.const.groupMobileLaserSentry,
 inventorycommon.const.groupMobileMissileSentry,
 inventorycommon.const.groupMobileProjectileSentry,
 inventorycommon.const.groupMobileReactor,
 inventorycommon.const.groupMoonMining,
 inventorycommon.const.groupReprocessingArray,
 inventorycommon.const.groupCompressionArray,
 inventorycommon.const.groupScannerArray,
 inventorycommon.const.groupSensorDampeningBattery,
 inventorycommon.const.groupShieldHardeningArray,
 inventorycommon.const.groupShipMaintenanceArray,
 inventorycommon.const.groupSilo,
 inventorycommon.const.groupStasisWebificationBattery,
 inventorycommon.const.groupWarpScramblingBattery,
 inventorycommon.const.groupCynosuralSystemJammer,
 inventorycommon.const.groupCynosuralGeneratorArray,
 inventorycommon.const.groupPersonalHangar}
probeScanGroups[probeScanGroupSovereignty] = {inventorycommon.const.groupInfrastructureHub, inventorycommon.const.groupSovereigntyClaimMarkers}
probeScanGroups[probeScanGroupDeployable] = {inventorycommon.const.groupMobileWarpDisruptor,
 inventorycommon.const.groupMobileStorage,
 inventorycommon.const.groupMobileScanInhibitor,
 inventorycommon.const.groupMobileMicroJumpUnit,
 inventorycommon.const.groupMobileHomes,
 inventorycommon.const.groupCynoInhibitor,
 inventorycommon.const.groupDeployableCynoGenerator,
 inventorycommon.const.groupSiphonPseudoSilo,
 inventorycommon.const.groupAutoLooter,
 inventorycommon.const.groupMercenaryDen}
probeScanGroups[probeScanGroupOrbitals] = {inventorycommon.const.groupOrbitalConstructionPlatforms, inventorycommon.const.groupOrbitalInfrastructure, inventorycommon.const.groupSkyhook}
probeScanGroups[probeScanGroupStructures] = {inventorycommon.const.groupStructureCitadel,
 inventorycommon.const.groupStructureIndustrialArray,
 inventorycommon.const.groupStructureDrillingPlatform,
 inventorycommon.const.groupStructureNpcForwardOperatingBase,
 inventorycommon.const.groupStructureJumpBridge,
 inventorycommon.const.groupStructureCynoJammer,
 inventorycommon.const.groupStructureCynoBeacon,
 inventorycommon.const.groupUpwellMoonDrill}
probeScanGroups[probeScanGroupDrones] = {inventorycommon.const.groupCapDrainDrone,
 inventorycommon.const.groupCombatDrone,
 inventorycommon.const.groupElectronicWarfareDrone,
 inventorycommon.const.groupLogisticDrone,
 inventorycommon.const.groupMiningDrone,
 inventorycommon.const.groupStasisWebifyingDrone,
 inventorycommon.const.groupSalvageDrone}
probeScanGroups[probeScanGroupFighters] = {inventorycommon.const.groupLightFighter,
 inventorycommon.const.groupSupportFighter,
 inventorycommon.const.groupHeavyFighter,
 inventorycommon.const.groupStructureLightFighter,
 inventorycommon.const.groupStructureSupportFighter,
 inventorycommon.const.groupStructureHeavyFighter}
probeScanGroups[probeScanGroupCharges] = {inventorycommon.const.groupScannerProbe, inventorycommon.const.groupSurveyProbe, inventorycommon.const.groupWarpDisruptionProbe}
probeScanGroups[probeScanGroupCelestials] = {inventorycommon.const.groupAsteroidBelt,
 inventorycommon.const.groupForceField,
 inventorycommon.const.groupMoon,
 inventorycommon.const.groupPlanet,
 inventorycommon.const.groupStargate,
 inventorycommon.const.groupSun,
 inventorycommon.const.groupStation}
probeScanCosmicSignatureAttributes = {dogma.const.attributeScanLadarStrength,
 dogma.const.attributeScanMagnetometricStrength,
 dogma.const.attributeScanRadarStrength,
 dogma.const.attributeScanWormholeStrength,
 dogma.const.attributeScanAllStrength}
SCAN_STRENGTHS = [dogma.const.attributeScanGravimetricStrength,
 dogma.const.attributeScanLadarStrength,
 dogma.const.attributeScanMagnetometricStrength,
 dogma.const.attributeScanRadarStrength,
 dogma.const.attributeScanWormholeStrength]
COMBAT_TARGETS = [probeScanGroupShips,
 probeScanGroupDrones,
 probeScanGroupCharges,
 probeScanGroupStructures,
 probeScanGroupNPCs,
 probeScanGroupDeployable,
 probeScanGroupFighters,
 probeScanGroupStarBase,
 probeScanGroupOrbitals,
 probeScanGroupSovereignty,
 probeScanGroupAbyssalTraces]
SCAN_STRENGTH_ATTRIBUTE_ID = 1371
SCAN_DEVIATION_ATTRIBUTE_ID = 1372
SCAN_DURATION_ATTRIBUTE_ID = 73
SCAN_STRENGTH_BONUS_ATTRIBUTE_IDS = [846, 1907]
SCAN_DEVIATION_BONUS_ATTRIBUTE_IDS = [1156, 1905]
SCAN_DURATION_BONUS_ATTRIBUTE_IDS = [1906]
SCAN_DURATION_ALTERNATE_ATTRIBUTE_IDS = [66]
SCANNING_IMPLANTS_TYPE_IDS = [27186,
 27187,
 27188,
 27190,
 27191,
 27192,
 27193,
 27194,
 27195,
 28808,
 28809,
 28810,
 28811,
 28812,
 28813,
 33971,
 33972,
 33973,
 33974,
 33975,
 33976]
SCANNING_SKILLS_TYPE_IDS = [25739,
 25811,
 25810,
 3412]
SCANNING_SUBSYSTEM_TYPE_IDS = {45595: dogma.const.subsystemBonusMinmatarElectronic,
 45586: dogma.const.subsystemBonusAmarrElectronic,
 45589: dogma.const.subsystemBonusCaldariElectronic,
 45592: dogma.const.subsystemBonusGallenteElectronic}
attributeImplantSetSister = 1284

def GetCosmicSignatureGroups():
    return {(inventorycommon.const.groupCosmicSignature, attributeID) for attributeID in probeScanCosmicSignatureAttributes}


def GetDroneFighterAndChargeGroups():
    return probeScanGroups[probeScanGroupDrones].union(probeScanGroups[probeScanGroupFighters].union(probeScanGroups[probeScanGroupCharges])).copy()


def GetShipGroups():
    return probeScanGroups[probeScanGroupShips].union(probeScanGroups[probeScanGroupNPCs]).copy()


def GetStructureGroups():
    return probeScanGroups[probeScanGroupStructures].union(probeScanGroups[probeScanGroupSovereignty].union(probeScanGroups[probeScanGroupStarBase].union(probeScanGroups[probeScanGroupOrbitals]))).copy()


def GetDeployableGroups():
    return probeScanGroups[probeScanGroupDeployable].copy()
