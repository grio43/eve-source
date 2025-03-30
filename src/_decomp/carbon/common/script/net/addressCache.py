#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\addressCache.py
from cluster import SERVICE_ALL
from collections import defaultdict
from itertools import chain

class MachoAddressCache(object):
    __guid__ = 'gps.AddressCache'

    def __init__(self):
        self._nodeIDsByServiceAddress = {}
        self._nodeIDsByServiceMask = defaultdict(set)
        self._deadNodes = set()
        self._knownNodes = set()

    @staticmethod
    def _extractBits(i):
        cur = 1
        ret = []
        while i > 0:
            if i & 1:
                ret.append(cur)
            cur = cur + 1
            i = i >> 1

        return ret

    def GetByServiceAddress(self, service, address):
        try:
            return self._nodeIDsByServiceAddress[service, address]
        except KeyError:
            return None

    def SetServiceAddress(self, service, address, nodeID):
        key = (service, address)
        result = key not in self._nodeIDsByServiceAddress
        self._nodeIDsByServiceAddress[key] = nodeID
        self._knownNodes.add(nodeID)
        return result

    def RemoveServiceAddress(self, service, address):
        try:
            del self._nodeIDsByServiceAddress[service, address]
            return True
        except KeyError:
            return False

    def GetCachedServiceAddressMap(self):
        nodeMap = defaultdict(list)
        for serviceAddress, nodeID in self._nodeIDsByServiceAddress.iteritems():
            nodeMap[nodeID].append(serviceAddress)

        return nodeMap

    def GetByServiceMask(self, serviceMask):
        return self._nodeIDsByServiceMask[serviceMask]

    def SetNodeForServiceMask(self, nodeID, serviceMask):
        result = nodeID in self._nodeIDsByServiceMask[serviceMask]
        if not result:
            self._nodeIDsByServiceMask[serviceMask].add(nodeID)
            self._knownNodes.add(nodeID)
        return result

    def LoadNodeToServiceMaskMapping(self, nodeID, serviceMask):
        if serviceMask is None:
            serviceMask = SERVICE_ALL
        for bit in self._extractBits(serviceMask):
            self._nodeIDsByServiceMask[bit].add(nodeID)

        self._knownNodes.add(nodeID)

    def ResolveServiceMask(self, serviceMask):
        nodeIDs = set()
        for bit in self._extractBits(serviceMask):
            nodeIDs.update(self.GetByServiceMask(bit))

        return nodeIDs

    def IsDeadNode(self, nodeID):
        return nodeID in self._deadNodes

    def MarkDeadNode(self, nodeID):
        self.RemoveAllForNode(nodeID)
        self._deadNodes.add(nodeID)

    def UnmarkDeadNode(self, nodeID):
        self._deadNodes.discard(nodeID)

    def RemoveAllForNode(self, nodeID):
        for serviceAddress in {sAddr for sAddr, nID in self._nodeIDsByServiceAddress.iteritems() if nID == nodeID}:
            del self._nodeIDsByServiceAddress[serviceAddress]

        for serviceMaskMapping in self._nodeIDsByServiceMask.itervalues():
            serviceMaskMapping.discard(nodeID)

    def GetCachedServiceMaskMap(self):
        return self._nodeIDsByServiceMask

    def IsKnownNode(self, nodeID):
        return nodeID in self._knownNodes

    def Clear(self):
        self._nodeIDsByServiceAddress.clear()
        self._nodeIDsByServiceMask.clear()

    def Report(self):
        return '%d service addresses cached along with %d serviceMask addresses' % (len(self._nodeIDsByServiceAddress), len(self._nodeIDsByServiceMask))
