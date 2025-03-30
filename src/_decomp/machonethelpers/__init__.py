#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\machonethelpers\__init__.py
from cluster import SERVICE_CLUSTERSINGLETON, SERVICE_BEYONCE

class RemoteCallHelper(object):

    def __init__(self, machoNet):
        self.machoNet = machoNet

    def GetRemoteSolarSystemBoundService(self, serviceName, solarSystemID):
        nodeID = self.machoNet.GetNodeFromAddress(SERVICE_BEYONCE, solarSystemID)
        return self.machoNet.ConnectToRemoteService(serviceName, nodeID)

    def GetClusterSingletonService(self, serviceName, numMod):
        nodeID = self.machoNet.GetNodeFromAddress(SERVICE_CLUSTERSINGLETON, numMod)
        return self.machoNet.ConnectToRemoteService(serviceName, nodeID)
