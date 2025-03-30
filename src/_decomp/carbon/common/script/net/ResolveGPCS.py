#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\ResolveGPCS.py
import types
from carbon.common.script.net.machoNetAddress import MachoAddress
from carbon.common.script.net.machoNetExceptions import UnMachoDestination, WrongMachoNode
from carbon.common.script.util.timerstuff import ClockThis
from cluster import MACHONETMSG_TYPE_RESOLVE_REQ
from machonet_tracing import IngressTracer

class ResolveGPCS:
    __guid__ = 'gpcs.Resolve'

    def CallUp(self, packet):
        if getattr(packet.destination, 'service', 0):
            if packet.payload[1] == 'MachoBindObject':
                nodeID = None
            else:
                nodeID = ClockThis('machoNet::GPCS::gpcs.Resolve::CallUp::MachoResolve', sm.StartServiceAndWaitForRunningState(packet.destination.service).MachoResolve, session.GetActualSession())
            if type(nodeID) == types.StringType:
                if packet.command == MACHONETMSG_TYPE_RESOLVE_REQ:
                    return packet.Response(0, nodeID)
                raise UnMachoDestination("Failed to resolve %s, reason='%s'" % (packet.destination.service, nodeID))
            elif nodeID is None:
                if packet.command == MACHONETMSG_TYPE_RESOLVE_REQ:
                    rsp = packet.Response(1, '')
                    rsp.source = MachoAddress(service=packet.destination.service)
                    return rsp
            else:
                if packet.command == MACHONETMSG_TYPE_RESOLVE_REQ:
                    rsp = packet.Response(1, '')
                    rsp.source = MachoAddress(nodeID=nodeID, service=packet.destination.service)
                    return rsp
                if nodeID != self.machoNet.GetNodeID():
                    IngressTracer.set_error_state(WrongMachoNode.__guid__)
                    raise WrongMachoNode(nodeID)
        return self.ForwardCallUp(packet)

    def NotifyUp(self, packet):
        if getattr(packet.destination, 'service', 0):
            nodeID = sm.StartServiceAndWaitForRunningState(packet.destination.service).MachoResolve(session.GetActualSession())
            if type(nodeID) == types.StringType:
                self.machoNet.LogError('Resolve failed during notification.  Packet lost.  Failure reason=', nodeID)
                raise UnMachoDestination("Failed to resolve %s, reason='%s'" % (packet.destination.service, nodeID))
            elif nodeID is None:
                pass
            else:
                thisNodeID = self.machoNet.GetNodeID()
                if nodeID != thisNodeID:
                    self.machoNet.LogInfo('Notification packet recieved on the wrong node(', thisNodeID, '), forwarding to the correct one ', nodeID)
                    packet.destination = MachoAddress(nodeID=nodeID, service=packet.destination.service)
                    proxyID = self.machoNet.GetProxyNodeIDFromClientID(packet.source.clientID)
                    proxyMachoNet = self.machoNet.session.ConnectToRemoteService('machoNet', nodeID=proxyID)
                    proxyMachoNet.NoBlock.ForwardNotificationToNode(packet.source, packet.destination, packet.userID, packet.payload)
                    return
        return self.ForwardNotifyUp(packet)
