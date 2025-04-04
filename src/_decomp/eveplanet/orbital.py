#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveplanet\orbital.py
from cluster import SERVICE_BEYONCE
from collections import defaultdict

class OrbitalOwnershipChanger(object):

    def __init__(self, machoNet, session, dbAccess):
        self.machoNet = machoNet
        self.session = session
        self.dbAccess = dbAccess

    def ChangeOwnerToInterBus(self, corpID):
        orbitals = self.dbAccess.GetOrbitalsForCorpID(corpID)
        orbitalInfoByNodeID = self._GetOrbitalsByNodeID(orbitals)
        self._RevertOwnershipOfOrbitals(orbitalInfoByNodeID)
        self.dbAccess.DeleteOrbitalSettings([ orbital.itemID for orbital in orbitals ])

    def _GetOrbitalsByNodeID(self, orbitals):
        orbitalInfoByNodeID = defaultdict(lambda : defaultdict(list))
        for orbital in orbitals:
            solarSystemID = orbital.locationID
            nodeID = self.machoNet.GetNodeFromAddress(SERVICE_BEYONCE, solarSystemID)
            orbitalInfoByNodeID[nodeID][solarSystemID].append(orbital.itemID)

        return orbitalInfoByNodeID

    def _RevertOwnershipOfOrbitals(self, orbitalInfoByNodeID):
        for nodeID, orbitalInfo in orbitalInfoByNodeID.iteritems():
            remoteOrbitalBroker = self.session.ConnectToRemoteService('planetOrbitalRegistryBroker', nodeID)
            remoteOrbitalBroker.RevertOrbitalsToInterBus(dict(orbitalInfo))
