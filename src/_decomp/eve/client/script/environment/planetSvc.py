#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\planetSvc.py
import blue
import gametime
import geo2
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING
from eve.client.script.environment.planet import clientPlanet
from eve.common.lib import appConst
from eve.common.script.net import eveMoniker
from eve.common.script.util import planetCommon
from eve.common.script.util.planetCommon import NETWORK_UPDATE_DELAY

class PlanetService(Service):
    __guid__ = 'svc.planetSvc'
    __servicename__ = 'planetSvc'
    __displayName__ = 'Planet Service'
    __notifyevents__ = ['OnMajorPlanetStateUpdate',
     'OnPlanetChangesSubmitted',
     'OnPlanetViewChanged',
     'OnSessionReset']

    def __init__(self):
        super(PlanetService, self).__init__()
        self.planets = {}
        self.simPlanets = {}
        self.colonizationData = None
        self.state = SERVICE_RUNNING
        self.foreignColoniesByPlanet = {}
        self.commandPinsByPlanet = {}
        self.extractorsByPlanet = {}
        self._lastSubmitTimestamp = None
        self._submittingInProgress = set()

    def ReInitialize(self):
        self.planets = {}
        self.simPlanets = {}
        self.colonizationData = None
        self.state = SERVICE_RUNNING
        self.foreignColoniesByPlanet = {}
        self.commandPinsByPlanet = {}
        self.extractorsByPlanet = {}

    def Run(self, memStream = None):
        self.LogInfo('Starting planet service')

    def OnSessionReset(self):
        self.ReInitialize()

    def GetPlanet(self, planetID):
        if planetID not in self.planets:
            self.planets[planetID] = self.GetClientPlanet(planetID)
        ret = self.planets[planetID]
        return ret

    def GetClientPlanet(self, planetID):
        return clientPlanet.ClientPlanet(self, planetID)

    def GetMyPlanets(self):
        if self.colonizationData is None:
            self.colonizationData = sm.RemoteSvc('planetMgr').GetPlanetsForChar()
        return self.colonizationData

    def GetMyPlanetsData(self):
        planets = self.GetMyPlanets()
        return [ self.GetPlanet(planet.planetID) for planet in planets ]

    @staticmethod
    def IsSystemWithinScanRange(solarSystemID):
        remoteSensing = sm.GetService('skills').GetEffectiveLevel(appConst.typeRemoteSensing)
        if not remoteSensing:
            return (False, False)
        currentLocation = cfg.evelocations.Get(session.solarsystemid2)
        currentPosition = (currentLocation.x, currentLocation.y, currentLocation.z)
        systemLocation = cfg.evelocations.Get(solarSystemID)
        systemPosition = (systemLocation.x, systemLocation.y, systemLocation.z)
        distanceFromSystem = geo2.Vec3Distance(currentPosition, systemPosition) / appConst.LIGHTYEAR
        maxRanges = appConst.planetResourceScanningRanges[:]
        maxRanges.reverse()
        maxScanRange = maxRanges[remoteSensing - 1]
        return (distanceFromSystem <= maxScanRange, distanceFromSystem > max(maxRanges))

    def IsPlanetColonizedByMe(self, planetID):
        planets = self.GetMyPlanets()
        for planet in planets:
            if planetID == planet.planetID:
                return True

        return False

    def GetColonyForCharacter(self, planetID, characterID):
        if planetID not in self.foreignColoniesByPlanet:
            self.foreignColoniesByPlanet[planetID] = {}
        colonyData = self.foreignColoniesByPlanet[planetID].get(characterID, None)
        if colonyData is None or colonyData.timestamp + planetCommon.PLANET_CACHE_TIMEOUT < blue.os.GetWallclockTime():
            self.LogInfo('GetColonyForCharacter :: Fetching fresh data due to lack of colony or expired timestamp for planet', planetID, 'character', characterID)
            remotePlanet = eveMoniker.GetPlanet(planetID)
            colonyData = utillib.KeyVal(timestamp=blue.os.GetWallclockTime())
            colonyData.data = remotePlanet.GetFullNetworkForOwner(planetID, characterID)
            self.foreignColoniesByPlanet[planetID][characterID] = colonyData
        return colonyData.data

    def GetPlanetCommandPins(self, planetID):
        pinData = self.commandPinsByPlanet.get(planetID, None)
        if pinData is None or pinData.timestamp + planetCommon.PLANET_CACHE_TIMEOUT < blue.os.GetWallclockTime():
            self.LogInfo('GetPlanetCommandPins :: Fetching fresh data due to lack of data or expired timestamp for planet', planetID)
            remotePlanet = eveMoniker.GetPlanet(planetID)
            pinData = utillib.KeyVal(timestamp=blue.os.GetWallclockTime())
            pinData.data = remotePlanet.GetCommandPinsForPlanet(planetID)
            self.commandPinsByPlanet[planetID] = pinData
        return pinData.data

    def GetExtractorsForPlanet(self, planetID):
        extractorData = self.extractorsByPlanet.get(planetID, None)
        if extractorData is None or extractorData.timestamp + planetCommon.PLANET_CACHE_TIMEOUT < blue.os.GetWallclockTime():
            self.LogInfo('GetPlanetExtractors :: Fetching fresh data due to lack of data or expired timestamp for planet', planetID)
            remotePlanet = eveMoniker.GetPlanet(planetID)
            extractorData = utillib.KeyVal(timestamp=blue.os.GetWallclockTime())
            extractorData.data = remotePlanet.GetExtractorsForPlanet(planetID)
            self.extractorsByPlanet[planetID] = extractorData
        return extractorData.data

    def OnMajorPlanetStateUpdate(self, planetID, numCommandCentersChanged = False):
        if planetID in self.planets:
            self.planets[planetID].Init()
        if planetID in self.simPlanets:
            self.simPlanets[planetID].Init()
        if numCommandCentersChanged:
            self._UpdateColonyPresence(planetID)
        else:
            self._UpdateColonyNumberOfPins(planetID)
        sm.ScatterEvent('OnPlanetPinsChanged', planetID)

    def OnPlanetChangesSubmitted(self, planetID):
        self._UpdateColonyNumberOfPins(planetID)

    def _UpdateColonyPresence(self, planetID):
        if planetID not in self.planets:
            self.colonizationData = [ colony for colony in self.colonizationData if colony.planetID != planetID ]
        elif self.colonizationData is not None:
            colony = self.planets[planetID].GetColony(session.charid)
            if colony is None or colony.colonyData is None or len(colony.colonyData.pins) < 1:
                self.colonizationData = [ colony for colony in self.colonizationData if colony.planetID != planetID ]
            else:
                addColony = True
                for c in self.colonizationData:
                    if c.planetID == planetID:
                        c.numberOfPins = len(colony.colonyData.pins)
                        addColony = False
                        break

                if addColony:
                    planet = self.GetPlanet(planetID)
                    newEntry = utillib.KeyVal(solarSystemID=self.planets[planetID].solarSystemID, planetID=planetID, typeID=self.planets[planetID].GetPlanetTypeID(), numberOfPins=len(colony.colonyData.pins), celestialIndex=planet.celestialIndex)
                    self.colonizationData.append(newEntry)
        sm.ScatterEvent('OnColonyPinCountUpdated', planetID)

    def _UpdateColonyNumberOfPins(self, planetID):
        planet = self.planets.get(planetID, None)
        if not planet:
            return
        data = self.GetMyPlanets()
        for dataRow in data:
            if dataRow.planetID == planetID:
                colony = planet.GetColony(session.charid)
                if colony is not None and colony.colonyData is not None:
                    if dataRow.numberOfPins != len(colony.colonyData.pins):
                        dataRow.numberOfPins = len(colony.colonyData.pins)
                        sm.ScatterEvent('OnColonyPinCountUpdated', planetID)
                else:
                    dataRow.numberOfPins = 0
                    sm.ScatterEvent('OnColonyPinCountUpdated', planetID)
                break

    def OnPlanetViewChanged(self, newPlanetID, oldPlanetID):
        if oldPlanetID in self.planets:
            self.planets[oldPlanetID].StopTicking()

    def ScatterOnPlanetCommandCenterDeployedOrRemoved(self, planetID):
        self._UpdateColonyPresence(planetID)
        sm.ScatterEvent('OnPlanetCommandCenterDeployedOrRemoved')

    def SetSubmittingInProgressForPlanet(self, planetID):
        self._submittingInProgress.add(planetID)
        self._lastSubmitTimestamp = gametime.GetWallclockTime()

    def RemoveSubmittingInProgressForPlanet(self, planetID):
        self._submittingInProgress.discard(planetID)

    def IsSubmittingInProgressOrThrottled(self):
        if self._submittingInProgress:
            return True
        if self._lastSubmitTimestamp is None:
            return False
        timeSinceLastSubmit = gametime.GetWallclockTime() - self._lastSubmitTimestamp
        if timeSinceLastSubmit < NETWORK_UPDATE_DELAY:
            return True
        return False

    def IsSubmittingInProgressForPlanet(self, planetID):
        return planetID in self._submittingInProgress
