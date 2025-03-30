#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\planetInfoSvc.py
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING
from collections import defaultdict
import trinity
import telemetry
from eve.common.script.sys import idCheckers
import inventorycommon.const as invConst
from eve.common.script.sys.idCheckers import IsSkyhook
from spacecomponents.common.helper import IsActiveComponent

class PlanetInfoSvc(Service):
    __guid__ = 'svc.planetInfo'
    __notifyevents__ = ['OnSessionChanged',
     'DoBallsAdded',
     'DoBallRemove',
     'OnLocalHackProgressUpdated',
     'DoBallsRemove']
    __servicename__ = 'PlanetInfo'
    __displayname__ = 'Planet Info Caching Service'
    __dependencies__ = ['michelle']

    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        self.LogInfo('PlanetInfo::Starting')
        self.Reset()
        self.hackProgress = {}
        self.state = SERVICE_RUNNING

    def Stop(self, memStream = None):
        if not trinity.app:
            return
        self.LogInfo('PlanetInfo::Stopping')
        self.Reset()

    def OnSessionChanged(self, isremote, session, change):
        if session.charid is None:
            return
        if 'solarsystemid' in change:
            self.Reset()

    def OnLocalHackProgressUpdated(self, hackedObjectID, hackProgress):
        self.hackProgress[hackedObjectID] = hackProgress
        bracket = sm.GetService('bracket').GetBracket(hackedObjectID)
        if bracket and bracket.sr.orbitalHackLocal is not None:
            bracket.UpdateHackProgress(hackProgress)

    def GetMyHackProgress(self, itemID):
        return self.hackProgress.get(itemID, None)

    def Reset(self):
        self.LogInfo('PlanetInfo::Reset')
        self.planets = set()
        self.orbitals = set()
        self.orbitalsByPlanetID = defaultdict(lambda : defaultdict(set))

    def GetFunctionalCustomOfficeOrbitalsForPlanet(self, planetID):
        groupIDs = (invConst.groupPlanetaryCustomsOffices, invConst.groupSkyhook)
        orbitals = self._GetOrbitalsForPlanet(planetID, groupIDs)
        ballpark = sm.GetService('michelle').GetBallpark()
        functionalPocos = set()
        for orbitalID in orbitals:
            slimItem = ballpark.GetInvItem(orbitalID)
            if IsSkyhook(slimItem.typeID) and not IsActiveComponent(ballpark.componentRegistry, slimItem.typeID, slimItem.itemID):
                continue
            functionalPocos.add(orbitalID)

        return functionalPocos

    def _GetOrbitalsForPlanet(self, planetID, groupIDs = None):
        orbitals = set()
        allPlanetOrbitals = self.orbitalsByPlanetID.get(planetID, {})
        for groupID, groupOrbitals in allPlanetOrbitals.iteritems():
            if groupIDs is None or groupID in groupIDs:
                orbitals.update(allPlanetOrbitals.get(groupID, set()))

        return orbitals

    def GetOrbitalsAtPlanet(self, orbitalID):
        for planetID, orbitsByGroupID in self.orbitalsByPlanetID.iteritems():
            for groupID, orbits in orbitsByGroupID.iteritems():
                if orbitalID in orbits:
                    return self._GetOrbitalsForPlanet(planetID)

        return set()

    def GetPocosForPlanet(self, planetID):
        return self._GetOrbitalsForPlanet(planetID, (invConst.groupPlanetaryCustomsOffices,))

    def GetSkyhooksAtPlanet(self, planetID):
        return self._GetOrbitalsForPlanet(planetID, (invConst.groupSkyhook,))

    def DoBallsAdded(self, ballItems, *args, **kwargs):
        for ball, slimItem in ballItems:
            if slimItem.groupID == invConst.groupPlanet:
                self._AddPlanet(ball, slimItem)
            elif idCheckers.IsOrbital(slimItem.categoryID):
                self._AddOrbital(ball, slimItem)

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, *args, **kwargs):
        if slimItem.groupID == invConst.groupPlanet and slimItem.itemID in self.planets:
            self._RemovePlanet(ball, slimItem)
        elif idCheckers.IsOrbital(slimItem.categoryID) and slimItem.itemID in self.orbitals:
            self._RemoveOrbital(ball, slimItem)

    def _AddPlanet(self, ball, slimItem):
        self.planets.add(slimItem.itemID)

    def _RemovePlanet(self, ball, slimItem):
        self.planets.remove(slimItem.itemID)
        if slimItem.itemID in self.orbitalsByPlanetID:
            del self.orbitalsByPlanetID[slimItem.itemID]

    def _AddOrbital(self, ball, slimItem):
        self.orbitals.add(slimItem.itemID)
        self.orbitalsByPlanetID[slimItem.planetID][slimItem.groupID].add(slimItem.itemID)

    def _RemoveOrbital(self, ball, slimItem):
        self.orbitals.remove(slimItem.itemID)
        if slimItem.planetID in self.orbitalsByPlanetID:
            for groupID, groupList in self.orbitalsByPlanetID[slimItem.planetID].iteritems():
                if slimItem.itemID in groupList:
                    groupList.remove(slimItem.itemID)
                    if len(groupList) == 0:
                        del self.orbitalsByPlanetID[slimItem.planetID][groupID]
                    break
