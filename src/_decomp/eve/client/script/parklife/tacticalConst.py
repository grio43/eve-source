#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\tacticalConst.py
import evetypes
import inventorycommon.const as invconst
filterGroups = {invconst.groupStationServices,
 invconst.groupSecondarySun,
 invconst.groupTemporaryCloud,
 invconst.groupSolarSystem,
 invconst.groupRing,
 invconst.groupConstellation,
 invconst.groupRegion,
 invconst.groupCloud,
 invconst.groupComet,
 invconst.groupCosmicAnomaly,
 invconst.groupCosmicSignature,
 invconst.groupGlobalWarpDisruptor,
 invconst.groupPlanetaryCloud,
 invconst.groupCommandPins,
 invconst.groupExtractorPins,
 invconst.groupPlanetaryLinks,
 invconst.groupProcessPins,
 invconst.groupSpaceportPins,
 invconst.groupStoragePins,
 invconst.groupFlashpoint,
 invconst.groupSatellite,
 invconst.groupOrbitalTarget,
 invconst.groupMobileMicroJumpDisruptor,
 invconst.groupMobileDecoyUnit,
 invconst.groupMobileVault,
 invconst.groupObservatoryDeployable,
 invconst.groupFighterDrone,
 invconst.groupFighterBomber,
 invconst.groupTestOrbitals,
 invconst.groupStructureAdministrationHub,
 invconst.groupStructureAdvertisementCenter,
 invconst.groupStructureLaboratory,
 invconst.groupStructureObservatoryArray,
 11,
 invconst.groupExtractionControlUnitPins,
 invconst.groupDefenseBunkers,
 invconst.groupAncientCompressedIce,
 invconst.groupTerranArtifacts,
 invconst.groupShippingCrates,
 invconst.groupProximityDrone,
 invconst.groupRepairDrone,
 invconst.groupUnanchoringDrone,
 invconst.groupWarpScramblingDrone,
 invconst.groupZombieEntities,
 invconst.groupForceFieldArray,
 invconst.groupLogisticsArray,
 invconst.groupMobilePowerCore,
 invconst.groupMobileShieldGenerator,
 invconst.groupMobileStorage,
 invconst.groupStealthEmitterArray,
 invconst.groupStructureRepairArray,
 invconst.groupTargetPaintingBattery,
 invconst.groupMoonChunk,
 invconst.groupAbyssalEnvironment,
 invconst.groupMassiveEnvironments,
 invconst.groupLocators,
 invconst.groupNonInteractableObject,
 invconst.groupScalableNonInteractableObject,
 invconst.groupNonScalableClouds,
 invconst.groupUninteractableLocalizedEffectBeacon,
 invconst.groupSovereigntyDisruptionStructures,
 invconst.groupInvisibleBeacon,
 invconst.groupInfestationAnchor,
 invconst.groupNonInteractableAsteroid}
validCategories = (invconst.categoryStation,
 invconst.categoryShip,
 invconst.categoryEntity,
 invconst.categoryCelestial,
 invconst.categoryAsteroid,
 invconst.categoryDrone,
 invconst.categoryDeployable,
 invconst.categoryStarbase,
 invconst.categoryStructure,
 invconst.categoryCharge,
 invconst.categorySovereigntyStructure,
 invconst.categoryOrbital,
 invconst.categoryFighter)
bombGroups = (invconst.groupBomb,
 invconst.groupBombECM,
 invconst.groupBombEnergy,
 invconst.groupScannerProbe,
 invconst.groupWarpDisruptionProbe,
 invconst.groupBurstEffectProbe,
 invconst.groupStructureAreaMissile)

class GroupStorage(object):

    def __init__(self):
        self.group_ids = set()
        self.groups = []

    def get_group_ids(self):
        if not self.group_ids:
            self.construct_groups()
        return self.group_ids

    def get_groups(self):
        if not self.groups:
            self.construct_groups()
        return self.groups

    def construct_groups(self):
        self.groups = []
        for group_id in evetypes.IterateGroups():
            category_id = evetypes.GetCategoryIDByGroup(group_id)
            if category_id == invconst.categoryCharge and group_id not in bombGroups:
                continue
            if category_id not in validCategories:
                continue
            if group_id in filterGroups:
                continue
            group_name = evetypes.GetGroupNameByGroup(group_id)
            self.groups.append((group_name.lower(), (group_id, group_name)))

        group_list = [ item[1] for item in sorted(self.groups, key=lambda data: data[0]) ]
        self.group_ids = set((each[0] for each in group_list))


group_storage = GroupStorage()

def is_interactable_entity(groupID):
    return groupID in group_storage.get_group_ids()


def get_group_ids():
    return group_storage.get_group_ids()


def get_groups():
    return group_storage.get_groups()
