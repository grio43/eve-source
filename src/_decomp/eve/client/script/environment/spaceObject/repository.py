#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\repository.py
from eve.client.script.environment.spaceObject.nonInteractableObject import NonInteractableObject, ScalableNonInteractableObject
from eve.client.script.environment.spaceObject.lensFlare import LensFlare
from eve.client.script.environment.spaceObject.stationConversionMonument import StationConversionMonument
from eve.client.script.environment.spaceObject.structure import Structure
import eve.common.lib.appConst as const
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.environment.spaceObject.asteroid import Asteroid, NonInteractableAsteroid
from eve.client.script.environment.spaceObject.asteroidBelt import AsteroidBelt
from eve.client.script.environment.spaceObject.backgroundObject import BackgroundObject
from eve.client.script.environment.spaceObject.basicOrbital import BasicOrbital
from eve.client.script.environment.spaceObject.beacon import Beacon
from eve.client.script.environment.spaceObject.cargo import Cargo
from eve.client.script.environment.spaceObject.cloud import Cloud
from eve.client.script.environment.spaceObject.corpse import Corpse
from eve.client.script.environment.spaceObject.customsOffice import CustomsOffice
from eve.client.script.environment.spaceObject.destructibleEffectBeacon import DestructibleEffectBeacon
from eve.client.script.environment.spaceObject.entityShip import EntityShip, EntitySleeper
from eve.client.script.environment.spaceObject.forceField import ForceField
from eve.client.script.environment.spaceObject.harvestableGasCloud import HarvestableGasCloud
from eve.client.script.environment.spaceObject.LargeCollidableObject import LargeCollidableObject
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure
from eve.client.script.environment.spaceObject.Drone import Drone
from eve.client.script.environment.spaceObject.missile import Bomb, Missile
from eve.client.script.environment.spaceObject.MobileWarpDisruptor import MobileWarpDisruptor
from eve.client.script.environment.spaceObject.planet import Planet
from eve.client.script.environment.spaceObject.playerShip import PlayerShip
from eve.client.script.environment.spaceObject.playerOwnedStructure import PlayerOwnedStructure
from eve.client.script.environment.spaceObject.scannerProbe import ScannerProbe
from eve.client.script.environment.spaceObject.sentryGun import SentryGun
from eve.client.script.environment.spaceObject.sovereigntyClaimMarker import SovereigntyClaimMarker
from eve.client.script.environment.spaceObject.sovereigntyHub import SovereigntyHub
from eve.client.script.environment.spaceObject.spewContainer import SpewContainer
from eve.client.script.environment.spaceObject.stargate import Stargate
from eve.client.script.environment.spaceObject.station import Station
from eve.client.script.environment.spaceObject.structureDrillingPlatform import StructureDrillingPlatform
from eve.client.script.environment.spaceObject.structureSentryGun import StructureSentryGun
from eve.client.script.environment.spaceObject.sun import Sun
from eve.client.script.environment.spaceObject.warpgate import WarpGate
from eve.client.script.environment.spaceObject.wormhole import Wormhole
from eve.client.script.environment.spaceObject.wreck import Wreck
from eve.client.script.environment.spaceObject.DeployableSpaceObject import DeployableSpaceObject
from eve.client.script.environment.spaceObject.fighterSquadron import FighterSquadron
import evetypes
import threadutils
CATEGORY_TO_SPACEOBJECT_MAPPING = {const.categoryShip: PlayerShip,
 const.categoryDeployable: SpaceObject,
 const.categoryStarbase: PlayerOwnedStructure,
 const.categorySovereigntyStructure: PlayerOwnedStructure,
 const.categoryAsteroid: Asteroid,
 const.categoryOrbital: BasicOrbital,
 const.categoryEntity: EntityShip,
 const.categoryDrone: Drone,
 const.categoryFighter: FighterSquadron,
 const.categoryStructure: Structure}
GROUP_TO_SPACEOBJECT_MAPPING = {const.groupAsteroidBelt: AsteroidBelt,
 const.groupBillboard: LargeCollidableObject,
 const.groupBiomass: Corpse,
 const.groupCargoContainer: Cargo,
 const.groupWreck: Wreck,
 const.groupCloud: Cloud,
 const.groupLCODrone: Drone,
 const.groupLargeCollidableObject: LargeCollidableObject,
 const.groupLargeCollidableStructure: LargeCollidableStructure,
 const.groupDeadspaceOverseersStructure: LargeCollidableStructure,
 const.groupMoonChunk: LargeCollidableObject,
 const.groupMoon: Planet,
 const.groupPlanet: Planet,
 const.groupRogueDrone: Drone,
 const.groupSecureCargoContainer: Cargo,
 const.groupAuditLogSecureContainer: Cargo,
 const.groupDeadspaceOverseersBelongings: Cargo,
 const.groupFreightContainer: Cargo,
 const.groupStargate: Stargate,
 const.groupDisruptedGate: Stargate,
 const.groupStation: Station,
 const.groupGoalPost: Station,
 const.groupDestructibleStationServices: LargeCollidableObject,
 const.groupSun: Sun,
 const.groupSecondarySun: BackgroundObject,
 const.groupMassiveEnvironments: BackgroundObject,
 const.groupTemporaryCloud: Cloud,
 const.groupMobileWarpDisruptor: MobileWarpDisruptor,
 const.groupMobileMicroJumpDisruptor: MobileWarpDisruptor,
 const.groupWarpGate: WarpGate,
 const.groupForceField: ForceField,
 const.groupDestructibleSentryGun: SentryGun,
 const.groupDeadspaceOverseersSentry: SentryGun,
 const.groupMobileLaserSentry: StructureSentryGun,
 const.groupMobileHybridSentry: StructureSentryGun,
 const.groupMobileProjectileSentry: StructureSentryGun,
 const.groupMobileSentryGun: SentryGun,
 const.groupProtectiveSentryGun: SentryGun,
 const.groupSentryGun: SentryGun,
 const.groupDeadspaceSleeperSleeplessPatroller: EntitySleeper,
 const.groupDeadspaceSleeperSleeplessSentinel: EntitySleeper,
 const.groupDeadspaceSleeperSleeplessDefender: EntitySleeper,
 const.groupDeadspaceSleeperAwakenedPatroller: EntitySleeper,
 const.groupDeadspaceSleeperAwakenedSentinel: EntitySleeper,
 const.groupDeadspaceSleeperAwakenedDefender: EntitySleeper,
 const.groupDeadspaceSleeperEmergentPatroller: EntitySleeper,
 const.groupDeadspaceSleeperEmergentSentinel: EntitySleeper,
 const.groupDeadspaceSleeperEmergentDefender: EntitySleeper,
 const.groupBomb: Bomb,
 const.groupBombECM: Bomb,
 const.groupBombEnergy: Bomb,
 const.groupHarvestableCloud: HarvestableGasCloud,
 const.groupAsteroidRogueDroneBattleCruiser: Drone,
 const.groupAsteroidRogueDroneBattleship: Drone,
 const.groupAsteroidRogueDroneCruiser: Drone,
 const.groupAsteroidRogueDroneDestroyer: Drone,
 const.groupAsteroidRogueDroneFrigate: Drone,
 const.groupAsteroidRogueDroneHauler: Drone,
 const.groupAsteroidRogueDroneSwarm: Drone,
 const.groupAsteroidRogueDroneOfficer: Drone,
 const.groupDeadspaceRogueDroneBattleCruiser: Drone,
 const.groupDeadspaceRogueDroneBattleship: Drone,
 const.groupDeadspaceRogueDroneCruiser: Drone,
 const.groupDeadspaceRogueDroneDestroyer: Drone,
 const.groupDeadspaceRogueDroneFrigate: Drone,
 const.groupDeadspaceRogueDroneSwarm: Drone,
 const.groupAsteroidRogueDroneCommanderFrigate: Drone,
 const.groupAsteroidRogueDroneCommanderDestroyer: Drone,
 const.groupAsteroidRogueDroneCommanderCruiser: Drone,
 const.groupAsteroidRogueDroneCommanderBattleCruiser: Drone,
 const.groupMissionFighterDrone: Drone,
 const.groupScannerProbe: ScannerProbe,
 const.groupWarpDisruptionProbe: ScannerProbe,
 const.groupBurstEffectProbe: ScannerProbe,
 const.groupWormhole: Wormhole,
 const.groupSovereigntyClaimMarkers: SovereigntyClaimMarker,
 const.groupStationConversionMonuments: StationConversionMonument,
 const.groupInfrastructureHub: SovereigntyHub,
 const.groupBeacon: LargeCollidableObject,
 const.groupCovertBeacon: LargeCollidableObject,
 const.groupCynosuralBeacon: LargeCollidableObject,
 const.groupSuperWeaponBeacon: Beacon,
 const.groupEffectBeacon: SpaceObject,
 const.groupSatellite: LargeCollidableStructure,
 const.groupPlanetaryCustomsOffices: CustomsOffice,
 const.groupSpewContainer: SpewContainer,
 const.groupSpawnContainer: SpewContainer,
 const.groupControlBunker: LargeCollidableObject,
 const.groupAutoLooter: DeployableSpaceObject,
 const.groupSiphonPseudoSilo: DeployableSpaceObject,
 const.groupCynoInhibitor: DeployableSpaceObject,
 const.groupDeployableCynoGenerator: DeployableSpaceObject,
 const.groupMobileHomes: DeployableSpaceObject,
 const.groupMobileScanInhibitor: DeployableSpaceObject,
 const.groupMobileMicroJumpUnit: DeployableSpaceObject,
 const.groupCosmicSignature: LargeCollidableObject,
 const.groupMissionContainer: LargeCollidableStructure,
 const.groupCapturePointTower: LargeCollidableObject,
 const.groupEntosisCommandNode: LargeCollidableObject,
 const.groupStructureDrillingPlatform: StructureDrillingPlatform,
 const.groupAgentsinSpace: LargeCollidableObject,
 const.groupMoonMiningBeacon: LargeCollidableObject,
 const.groupLensFlare: LensFlare,
 const.groupUninteractableLocalizedEffectBeacon: LargeCollidableObject,
 const.groupNonInteractableObject: NonInteractableObject,
 const.groupNonScalableClouds: NonInteractableObject,
 const.groupTemporaryCollidableStructure: LargeCollidableStructure,
 const.groupAbyssalNpc: EntityShip,
 const.groupInteractableLocalizedEffectBeacon: LargeCollidableStructure,
 const.groupAbyssalTraces: WarpGate,
 const.groupAbyssalDroneNpc: Drone,
 const.groupIndustrialSupportFacility: LargeCollidableObject,
 const.groupPrecursorCache: LargeCollidableObject,
 const.groupDestructibleEffectBeacon: DestructibleEffectBeacon,
 const.groupInvisibleBeacon: SpaceObject,
 const.groupCosmicAnomaly: SpaceObject,
 const.groupExoticArtefact: LargeCollidableStructure,
 const.groupScalableDecorativeAsteroid: Asteroid,
 const.groupTournamentChampionMonument: StationConversionMonument,
 const.groupEncounterSurveillanceSystem: SpaceObject,
 const.groupIrregularUnidentified: LargeCollidableObject,
 const.groupInterstellarShipcaster: Structure,
 const.groupScalableNonInteractableObject: ScalableNonInteractableObject,
 const.groupNonInteractableAsteroid: NonInteractableAsteroid}

@threadutils.Memoize
def GetGroupDict():
    groupDict = dict()
    dynamicMissileGroupMappings = {groupID:Missile for groupID in evetypes.IterateGroups() if evetypes.GetIsGroupFittableNonSingletonByGroup(groupID)}
    groupDict.update(dynamicMissileGroupMappings, **GROUP_TO_SPACEOBJECT_MAPPING)
    return groupDict


def GetCategoryDict():
    return dict(CATEGORY_TO_SPACEOBJECT_MAPPING)


def GetClass(groupID, categoryID):
    groupDict = GetGroupDict()
    soClass = None
    if groupID is not None and groupID in groupDict:
        soClass = groupDict[groupID]
    elif categoryID is not None and categoryID in CATEGORY_TO_SPACEOBJECT_MAPPING:
        soClass = CATEGORY_TO_SPACEOBJECT_MAPPING[categoryID]
    return soClass


exports = {'spaceObject.GetGroupDict': GetGroupDict,
 'spaceObject.GetCategoryDict': GetCategoryDict}
