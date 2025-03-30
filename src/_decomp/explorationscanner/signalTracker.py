#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\explorationscanner\signalTracker.py
import logging
import random
import geo2
import ccpProfile
from carbon.common.script.util import mathCommon
from dogma.const import attributeSignatureRadius
from eve.common.lib.appConst import AU
from eveuniverse.solar_systems import is_sensor_overlay_suppressed
from explorationscanner.common.cosmicAnomalyInfo import CosmicAnomalyInfo
from explorationscanner.common.signatureInfo import SignatureInfo
from explorationscanner.common.staticSiteInfo import StaticSiteInfo
from explorationscanner.common.structureInfo import StructureInfo
from inventorycommon.const import groupCosmicAnomaly, groupCosmicSignature
from probescanning.const import SCAN_STRENGTHS
from sensorsuite import common
from utillib import KeyVal
logger = logging.getLogger(__name__)
minSignatureSignalStrength = 2
maxSignatureSignalStrength = 20
deviationAtMinStrength = 8 * AU
deviationAtMaxStrength = 4 * AU

def CalculateDeviationForSignal(sigRadius, scanStrength):
    signalStrength = sigRadius / scanStrength
    if signalStrength < minSignatureSignalStrength:
        deviation = deviationAtMinStrength
    elif signalStrength > maxSignatureSignalStrength:
        deviation = deviationAtMaxStrength
    else:
        errorFraction = 1 - (signalStrength - minSignatureSignalStrength) / (maxSignatureSignalStrength - minSignatureSignalStrength)
        deviation = deviationAtMaxStrength + errorFraction * (deviationAtMinStrength - deviationAtMaxStrength)
    return deviation


class SignalTracker:
    __notifyevents__ = ['OnDungeonInstanceAdded',
     'OnDungeonInstanceRemoved',
     'OnStructureAdded',
     'OnStructureRemoved']

    def __init__(self, ballpark, scanMgr, solarSystemID, machoNet, dungeonExplorationMgr, keeper):
        self.ballpark = ballpark
        self.scanMgr = scanMgr
        self.solarSystemID = solarSystemID
        self.machoNet = machoNet
        self.dungeonExplorationMgr = dungeonExplorationMgr
        self.keeper = keeper
        self.LogInfo = scanMgr.LogInfo
        self.LogWarn = scanMgr.LogWarn
        self.LogError = scanMgr.LogError
        self.newClients = set()
        self.activeClients = set()
        self.trackedAnomalies = set()
        self.addedCosmicAnomalies = {}
        self.removedCosmicAnomalies = set()
        self.trackedSignatures = set()
        self.addedCosmicSignatures = {}
        self.removedCosmicSignatures = set()
        self.trackedStructures = set()
        self.addedStructures = {}
        self.removedStructures = set()
        self.cachedPositionDeviations = {}
        self.staticContent = None
        sm.RegisterNotify(self)
        logger.info('Initialized SignalTracker for solar system %s initialized', self.solarSystemID)

    def Release(self):
        sm.UnregisterNotify(self)

    def RegisterCharacterForUpdates(self, charID):
        self.newClients.add(charID)

    def UnregisterCharacterForUpdates(self, charID):
        self.newClients.discard(charID)
        self.activeClients.discard(charID)

    def DoUpdateTick(self):
        self.NarrowcastUpdatesForSites('OnSignalTrackerAnomalyUpdate', self.addedCosmicAnomalies, self.removedCosmicAnomalies)
        self.NarrowcastUpdatesForSites('OnSignalTrackerSignatureUpdate', self.addedCosmicSignatures, self.removedCosmicSignatures)
        self.NarrowcastUpdatesForSites('OnSignalTrackerStructureUpdate', self.addedStructures, self.removedStructures)
        if len(self.newClients):
            fullState = self.GetFullState()
            self.machoNet.NarrowcastByCharIDs(list(self.newClients), 'OnSignalTrackerFullState', self.solarSystemID, fullState)
            self.activeClients.update(self.newClients)
            self.newClients = set()

    def NarrowcastUpdatesForSites(self, remoteHandlerName, addedSites, removeSites):
        if len(addedSites) or len(removeSites):
            if not is_sensor_overlay_suppressed(self.solarSystemID):
                self.machoNet.NarrowcastByCharIDs(list(self.activeClients), remoteHandlerName, self.solarSystemID, addedSites, removeSites)
            addedSites.clear()
            removeSites.clear()

    def GetStaticSites(self):
        if self.staticContent is None:
            logger.info('System %s is loading static content', self.solarSystemID)
            signatures = {}
            staticSites = {}
            staticSpawns = self.keeper.GetStaticSpawns(self.solarSystemID)
            for staticSpawn in staticSpawns:
                if staticSpawn.clientRestricted:
                    continue
                dungeon = self.keeper.GetDungeonData(staticSpawn.dungeonID).dungeon
                spawnID = self.keeper.GetSpawnID(staticSpawn.spawnPointID)
                spawn = self.keeper.GetSpawn(spawnID)
                beaconID = spawn.entryPoints[dungeon.entryObjectID]
                slimItem = self.ballpark.slims[beaconID]
                if slimItem.groupID == groupCosmicSignature:
                    strengths = [ self.ballpark.dogmaLM.GetAttributeValue(beaconID, attrID) for attrID in SCAN_STRENGTHS ]
                    bestTargetStrength = max(strengths)
                    if bestTargetStrength > 0:
                        signatureRadius = self.ballpark.dogmaLM.GetAttributeValue(beaconID, attributeSignatureRadius)
                        signatures[beaconID] = self.GetClientCosmicSignatureInfo(beaconID, staticSpawn.dungeonID, spawn.spawnpointID, signatureRadius, bestTargetStrength)
                    else:
                        logger.error('Skipping static dungeon site %s with beaconID %s of type %s because it has scan strength of zero.', staticSpawn.dungeonID, beaconID, slimItem.typeID)
                else:
                    staticSites[beaconID] = StaticSiteInfo(spawn.entryPos, dungeon.dungeonNameID, dungeon.factionID)

            logger.info('System %s processed %s static sites. %s landmarks and %s signature sites', self.solarSystemID, len(staticSpawns), len(staticSites), len(signatures))
            self.staticContent = (staticSites, signatures)
            return self.staticContent
        return self.staticContent

    def GetStructures(self):
        structures = {}
        structuresInSolarSystem = self.ballpark.GetStructures()
        for structure in structuresInSolarSystem:
            structureInfo = self.GetStructureInfo(structure.id)
            if structureInfo:
                structures[structure.id] = structureInfo

        return structures

    @ccpProfile.TimedFunction('ScanMgr::SignalTracker::GetFullState')
    def GetFullState(self):
        if is_sensor_overlay_suppressed(self.solarSystemID):
            return ({},
             {},
             {},
             {})
        dungeons = self.dungeonExplorationMgr.GetInstancesForSolarsystem(self.solarSystemID)
        anomalies = {}
        signatures = {}
        for dungeon in dungeons.itervalues():
            if not dungeon.isScannable:
                continue
            try:
                slimItem = self.ballpark.slims[dungeon.signatureID]
            except KeyError:
                continue

            if slimItem.groupID not in (groupCosmicAnomaly, groupCosmicSignature):
                continue
            if slimItem.groupID == groupCosmicAnomaly:
                anomalies[dungeon.signatureID] = self.GetClientCosmicAnomalyInfo(dungeon)
            elif slimItem.groupID == groupCosmicSignature and dungeon.scanStrengthValue > 0:
                signatures[dungeon.signatureID] = self.GetClientCosmicSignatureInfoFromDungeon(dungeon)

        staticSites, extraSignatures = self.GetStaticSites()
        signatures.update(extraSignatures)
        structures = self.GetStructures()
        return (anomalies,
         signatures,
         staticSites,
         structures)

    @ccpProfile.TimedFunction('ScanMgr::SignalTracker::GetClientCosmicAnomalyInfo')
    def GetClientCosmicAnomalyInfo(self, instance):
        signatureID = instance.signatureID
        instanceID = instance.instanceID
        dungeonID = instance.dungeonID
        scanStrength = instance.scanStrengthAttribute
        ball = self.ballpark.balls.get(signatureID, None)
        if ball is None:
            return
        position = (ball.x, ball.y, ball.z)
        targetID = self.scanMgr.GetScanTargetID(signatureID, targetSeedID=instanceID)
        dungeonData = self.keeper.GetDungeonData(dungeonID).dungeon
        difficulty = common.MapDungeonDifficulty(dungeonData.difficulty)
        archetypeID = dungeonData.archetypeID
        factionID = dungeonData.factionID
        dungeonNameID = dungeonData.dungeonNameID
        entryObjectTypeID = getattr(dungeonData, 'entryTypeID', None)
        shipRestrictions = self.keeper.GetDungeonShipRestrictions(dungeonID)
        allowedTypes = shipRestrictions['allowedShipTypes']
        return CosmicAnomalyInfo(position, targetID, difficulty, dungeonID, archetypeID, instanceID, dungeonNameID, factionID, scanStrength, allowedTypes, entryObjectTypeID, self.solarSystemID)

    @ccpProfile.TimedFunction('ScanMgr::SignalTracker::GetClientCosmicSignatureInfoFromDungeon')
    def GetClientCosmicSignatureInfoFromDungeon(self, dungeon):
        return self.GetClientCosmicSignatureInfo(dungeon.signatureID, dungeon.dungeonID, dungeon.instanceID, dungeon.signatureRadius, dungeon.scanStrengthValue)

    def GetClientCosmicSignatureInfo(self, signatureID, dungeonID, targetSeedID, signatureRadius, scanStrengthValue):
        ball = self.ballpark.balls.get(signatureID, None)
        if ball is None:
            return
        targetID = self.scanMgr.GetScanTargetID(signatureID, targetSeedID=targetSeedID)
        if signatureID in self.cachedPositionDeviations:
            position, difficulty, deviation, archetypeID = self.cachedPositionDeviations[signatureID]
        else:
            deviation = CalculateDeviationForSignal(signatureRadius, scanStrengthValue)
            position = (ball.x, ball.y, ball.z)
            offset = mathCommon.RandomVector(random.random() * deviation)
            position = geo2.Vec3AddD(position, offset)
            dungeonData = self.keeper.GetDungeonData(dungeonID).dungeon
            difficulty = common.MapDungeonDifficulty(dungeonData.difficulty)
            archetypeID = dungeonData.archetypeID
            self.cachedPositionDeviations[signatureID] = (position,
             difficulty,
             deviation,
             archetypeID)
        return SignatureInfo(position, targetID, difficulty, deviation)

    def GetStructureInfo(self, structureID):
        ball = self.ballpark.balls.get(structureID, None)
        slimItem = self.ballpark.slims.get(structureID, None)
        if ball is None or slimItem is None:
            return
        if not ball.isGlobal:
            return
        typeID = slimItem.typeID
        groupID = slimItem.groupID
        categoryID = slimItem.categoryID
        position = (ball.x, ball.y, ball.z)
        randomlyGeneratedTargetID = self.scanMgr.GetScanTargetID(structureID)
        return StructureInfo(typeID, groupID, categoryID, position, randomlyGeneratedTargetID)

    def _NotifyClientsInSolarSystem(self, event, *args):
        self.machoNet.SinglecastBySolarSystemID2(self.solarSystemID, event, *args)

    def OnDungeonInstanceAdded(self, solarSystemID, instance):
        if solarSystemID != self.solarSystemID:
            return
        slimItem = self.ballpark.slims[instance.signatureID]
        if slimItem.groupID == groupCosmicAnomaly:
            self._TrackCosmicAnomaly(instance)
        elif slimItem.groupID == groupCosmicSignature and instance.scanStrengthValue > 0:
            self._TrackCosmicSignature(instance)

    def _TrackCosmicAnomaly(self, instance):
        cosmicAnomaly = self.GetClientCosmicAnomalyInfo(instance)
        signatureID = instance.signatureID
        self.addedCosmicAnomalies[signatureID] = cosmicAnomaly
        self.trackedAnomalies.add(signatureID)
        cosmicAnomalyData = KeyVal(dictLikeObject=cosmicAnomaly.AsDictionary())
        self._NotifyClientsInSolarSystem('OnCosmicAnomalyAdded', cosmicAnomalyData)

    def _TrackCosmicSignature(self, instance):
        cosmicSignature = self.GetClientCosmicSignatureInfoFromDungeon(instance)
        signatureID = instance.signatureID
        targetID = cosmicSignature.targetID
        self.addedCosmicSignatures[signatureID] = self.GetClientCosmicSignatureInfoFromDungeon(instance)
        self.trackedSignatures.add(signatureID)
        self._NotifyClientsInSolarSystem('OnCosmicSignatureAdded', targetID)

    def OnDungeonInstanceRemoved(self, solarSystemID, instanceID, signatureID, dungeonID):
        if solarSystemID != self.solarSystemID:
            return
        if signatureID in self.trackedAnomalies:
            self.trackedAnomalies.discard(signatureID)
            self.removedCosmicAnomalies.add(signatureID)
            self._NotifyClientsInSolarSystem('OnCosmicAnomalyRemoved', instanceID, dungeonID, self.solarSystemID)
        elif signatureID in self.trackedSignatures:
            self.trackedSignatures.discard(signatureID)
            self.removedCosmicSignatures.add(signatureID)
            self.cachedPositionDeviations.pop(signatureID, None)

    def OnStructureAdded(self, solarSystemID, structureID):
        if solarSystemID != self.solarSystemID:
            return
        if structureID in self.trackedStructures:
            return
        structureInfo = self.GetStructureInfo(structureID)
        if structureInfo:
            self.addedStructures[structureID] = structureInfo
            self.trackedStructures.add(structureID)

    def OnStructureRemoved(self, solarSystemID, structureID):
        if solarSystemID != self.solarSystemID:
            return
        if structureID in self.trackedStructures:
            self.trackedStructures.discard(structureID)
            self.removedStructures.add(structureID)
