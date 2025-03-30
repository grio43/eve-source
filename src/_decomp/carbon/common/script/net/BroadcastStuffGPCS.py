#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\BroadcastStuffGPCS.py
import sys
from collections import defaultdict
import blue
import bluepy
import uthread
from carbon.common.lib import const
from carbon.common.script.net import machoNet, machoNetAddress, machoNetPacket
from carbon.common.script.net.machoNetExceptions import UnMachoDestination
from carbon.common.script.sys import basesession
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING
from eveexceptions import UserError

class CoreBroadcastStuff:
    __guid__ = 'gpcs.CoreBroadcastStuff'
    __notifyRecvCount__ = defaultdict(lambda : 0)
    __notifyMissedCount__ = defaultdict(lambda : 0)
    __notifyRecvSourceCount__ = defaultdict(lambda : defaultdict(lambda : 0))
    __notifyMissedSourceCount__ = defaultdict(lambda : defaultdict(lambda : 0))

    def __init__(self):
        self.machoNet = None
        self.queue = []
        self.busrunning = 0
        self.busrate = 333

    def UpdateRecvNotificationStats(self, eventid, missed, source):
        if source.addressType == const.ADDRESS_TYPE_NODE:
            sourceId = source.nodeID
        elif source.addressType == const.ADDRESS_TYPE_CLIENT:
            sourceId = 'Client'
        else:
            sourceId = 'Unknown'
        if missed:
            CoreBroadcastStuff.__notifyMissedCount__[eventid] += 1
            CoreBroadcastStuff.__notifyMissedSourceCount__[eventid][sourceId] += 1
        else:
            CoreBroadcastStuff.__notifyRecvCount__[eventid] += 1
            CoreBroadcastStuff.__notifyRecvSourceCount__[eventid][sourceId] += 1

    def __BusDriver(self):
        try:
            while 1:
                blue.pyos.synchro.SleepWallclock(self.busrate)
                if self.machoNet is None:
                    continue
                if self.machoNet.state not in (SERVICE_START_PENDING, SERVICE_RUNNING) or machoNet.mode != 'server':
                    return
                queue = self.queue
                self.queue = []
                if queue:
                    if len(queue) == 1:
                        self.ScattercastWithoutTheStars(*queue[0])
                    else:
                        self.ProxyBroadcast('__PacketBus', queue)
                return

        finally:
            self.busrunning = 0

    def NotifyUp(self, packet):
        if packet.payload[0]:
            self.machoNet.LogInfo('BroadcastStuff::Notify(', packet.destination.broadcastID, ',...)')
            if packet.destination.broadcastID.startswith('Process'):
                sm.ChainEventWithoutTheStars(packet.destination.broadcastID, packet.payload[1])
            elif packet.destination.broadcastID.startswith('Do'):
                sm.SendEventWithoutTheStars(packet.destination.broadcastID, packet.payload[1])
            elif packet.destination.broadcastID == '__MultiEvent':
                for broadcast in packet.payload[1]:
                    broadcastID, args = broadcast
                    if broadcastID.startswith('Process'):
                        sm.ChainEventWithoutTheStars(broadcastID, args)
                    elif broadcastID.startswith('Do'):
                        sm.SendEventWithoutTheStars(broadcastID, args)
                    else:
                        sm.ScatterEventWithoutTheStars(broadcastID, args)

            elif packet.destination.broadcastID == '__PacketBus':
                self.machoNet.LogInfo('PacketBus:  handling a packet bus packet')
                merge = {}
                for each in packet.payload[1][0]:
                    k = (each[0], each[1])
                    if k in merge:
                        merge[k].append((each[2], each[3]))
                    else:
                        merge[k] = [(each[2], each[3])]

                for k, v in merge.iteritems():
                    if len(v) > 1:
                        self.ScattercastWithoutTheStars(k[0], k[1], '__MultiEvent', v)
                        self.machoNet.LogInfo('PacketBus:  scattercasting it to ', (k[0], k[1]), ' as __MultiEvent ', v)
                    else:
                        self.ScattercastWithoutTheStars(k[0], k[1], v[0][0], v[0][1])
                        self.machoNet.LogInfo('PacketBus:  scattercasting it to ', (k[0], k[1]), ' as ', v[0])

            else:
                sm.ScatterEventWithoutTheStars(packet.destination.broadcastID, packet.payload[1])
            self.UpdateRecvNotificationStats(packet.destination.broadcastID, False, packet.source)
        else:
            packet.payload = packet.payload[1]
            self.ForwardNotifyUp(packet)

    def NotifyDown(self, packet):
        packet.payload = (0, packet.payload)
        self.ForwardNotifyDown(packet)

    def Queuedcast(self, idtype, ids, method, *args):
        with bluepy.Timer('machoNet::Queuedcast'):
            callTimer = basesession.CallTimer('Queuedcast::%s::%s (Broadcast\\Client)' % (method, idtype))
            try:
                return self.QueuedcastWithoutTheStars(idtype, ids, method, args)
            finally:
                callTimer.Done()

    def QueuedcastWithoutTheStars(self, idtype, ids, method, args):
        if ids:
            self.queue.append((idtype,
             tuple(ids),
             method,
             args))
            if not self.busrunning:
                self.busrunning = 1
                uthread.worker('MachoNet::BroadcastStuff::BusDriver', self.__BusDriver)

    def Scattercast(self, idtype, ids, method, *args):
        with bluepy.Timer('machoNet::Scattercast'):
            callTimer = basesession.CallTimer('Scattercast::%s::%s (Broadcast\\Client)' % (method, idtype))
            try:
                return self.ScattercastWithoutTheStars(idtype, ids, method, args)
            finally:
                callTimer.Done()

    def ScattercastWithoutTheStars(self, idtype, ids, method, args):
        if not idtype.startswith('+'):
            idtype = '*%s' % idtype
        if ids:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype=idtype, narrowcast=ids), payload=(1, args)))

    def Objectcast(self, object, method, *args):
        with bluepy.Timer('machoNet::Objectcast'):
            callTimer = basesession.CallTimer('Objectcast::%s (Broadcast\\Client)' % method)
            try:
                self.ObjectcastWithoutTheStars(object, method, args)
            finally:
                callTimer.Done()

    def ObjectcastWithoutTheStars(self, object, method, args):
        objectID = basesession.GetObjectUUID(object)
        self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='objectID', narrowcast=[objectID]), payload=(1, args)))

    def Broadcast(self, method, *args):
        with bluepy.Timer('machoNet::Broadcast'):
            callTimer = basesession.CallTimer('Broadcast::%s (Broadcast\\Client)' % method)
            try:
                packet = machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method), payload=(1, args))
                self.ForwardNotifyDown(packet)
            finally:
                callTimer.Done()

    def ClientBroadcast(self, method, *args):
        with bluepy.Timer('machoNet::ClientBroadcast'):
            callTimer = basesession.CallTimer('ClientBroadcast::%s (Broadcast\\Client)' % method)
            try:
                packet = machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='clientID'), payload=(1, args))
                self.ForwardNotifyDown(packet)
            finally:
                callTimer.Done()

    def ClusterBroadcast(self, method, *args):
        with bluepy.Timer('machoNet::ClusterBroadcast'):
            callTimer = basesession.CallTimer('ClusterBroadcast::%s (Broadcast\\Client)' % method)
            try:
                self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='nodeID'), payload=(1, args)))
                self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='+nodeID', narrowcast=self.machoNet.GetConnectedProxyNodes()), payload=(1, args)))
                if method.startswith('Process'):
                    sm.ChainEventWithoutTheStars(method, args)
                elif method.startswith('Do'):
                    sm.SendEventWithoutTheStars(method, args)
                else:
                    sm.ScatterEventWithoutTheStars(method, args)
            finally:
                callTimer.Done()

    def ServerBroadcast(self, method, *args):
        with bluepy.Timer('machoNet::ServerBroadcast'):
            callTimer = basesession.CallTimer('ServerBroadcast::%s (Broadcast\\Client)' % method)
            try:
                self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='nodeID'), payload=(1, args)))
                if machoNet.mode == 'server':
                    if method.startswith('Process'):
                        sm.ChainEventWithoutTheStars(method, args)
                    elif method.startswith('Do'):
                        sm.SendEventWithoutTheStars(method, args)
                    else:
                        sm.ScatterEventWithoutTheStars(method, args)
            finally:
                callTimer.Done()

    NodeBroadcast = ServerBroadcast

    def NarrowcastByNodeIDsWithoutTheStars(self, nodeids, method, args, kwargs):
        if len(nodeids):
            if 'sourceNodeID' in kwargs:
                source = machoNetAddress.MachoAddress(nodeID=kwargs['sourceNodeID'], service=None, callID=None)
            else:
                source = machoNetAddress.MachoAddress()
            destination = machoNetAddress.MachoAddress(broadcastID=method, idtype='nodeID', narrowcast=nodeids)
            self.ForwardNotifyDown(machoNetPacket.Notification(source=source, destination=destination, payload=(1, args)))

    def NarrowcastByNodeIDs(self, nodeids, method, *args, **kwargs):
        with bluepy.Timer('machoNet::NarrowcastByNodeIDs'):
            callTimer = basesession.CallTimer('NarrowcastByClientIDs::%s (Broadcast\\Client)' % method)
            try:
                self.NarrowcastByNodeIDsWithoutTheStars(nodeids, method, args, kwargs)
            finally:
                callTimer.Done()

    def SinglecastByServiceMaskWithoutTheStars(self, serviceMask, method, args, kwargs):
        destination = machoNetAddress.MachoAddress(broadcastID=method, idtype='serviceMask', narrowcast=[serviceMask])
        source = machoNetAddress.MachoAddress()
        self.ForwardNotifyDown(machoNetPacket.Notification(source=source, destination=destination, payload=(1, args)))
        if machoNet.mode == 'server' and self.machoNet.serviceMask & serviceMask:
            if method.startswith('Process'):
                sm.ChainEventWithoutTheStars(method, args)
            elif method.startswith('Do'):
                sm.SendEventWithoutTheStars(method, args)
            else:
                sm.ScatterEventWithoutTheStars(method, args)

    def SinglecastByServiceMask(self, serviceMask, method, *args, **kwargs):
        with bluepy.Timer('machoNet::SinglecastByServiceMask'):
            callTimer = basesession.CallTimer('SinglecastByServiceMask:: %s (Broadcast\\Client)' % method)
            try:
                self.SinglecastByServiceMaskWithoutTheStars(serviceMask, method, args, kwargs)
            finally:
                callTimer.Done()

    def SinglecastByNodeID(self, nodeid, method, *args, **kwargs):
        with bluepy.Timer('machoNet::SinglecastByNodeID'):
            callTimer = basesession.CallTimer('SinglecastByNodeID::%s (Broadcast\\Client)' % method)
            try:
                self.NarrowcastByNodeIDsWithoutTheStars([nodeid], method, args, kwargs)
            finally:
                callTimer.Done()

    def ProxyBroadcast(self, method, *args):
        with bluepy.Timer('machoNet::ProxyBroadcast'):
            callTimer = basesession.CallTimer('ProxyBroadcast::%s (Broadcast\\Client)' % method)
            try:
                self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='+nodeID', narrowcast=self.machoNet.GetConnectedProxyNodes()), payload=(1, args)))
                if machoNet.mode == 'proxy':
                    if method.startswith('Process'):
                        sm.ChainEventWithoutTheStars(method, args)
                    elif method.startswith('Do'):
                        sm.SendEventWithoutTheStars(method, args)
                    else:
                        sm.ScatterEventWithoutTheStars(method, args)
            finally:
                callTimer.Done()

    def NarrowcastByClientIDs(self, clientids, method, *args):
        with bluepy.Timer('machoNet::NarrowcastByClientIDs'):
            callTimer = basesession.CallTimer('NarrowcastByClientIDs::%s (Broadcast\\Client)' % method)
            try:
                return self.NarrowcastByClientIDsWithoutTheStars(clientids, method, args)
            finally:
                callTimer.Done()

    def NarrowcastByClientIDsWithoutTheStars(self, clientids, method, args):
        if len(clientids):
            packet = machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='clientID', narrowcast=clientids), payload=(1, args))
            self.ForwardNotifyDown(packet)

    def SinglecastByClientID(self, clientid, method, *args):
        with bluepy.Timer('machoNet::SinglecastByClientID'):
            callTimer = basesession.CallTimer('SinglecastByClientID::%s (Broadcast\\Client)' % method)
            try:
                self.NarrowcastByClientIDsWithoutTheStars([clientid], method, args)
            finally:
                callTimer.Done()

    def ReliableSinglecastByUserID(self, userid, method, *args):
        with bluepy.Timer('machoNet::ReliableSinglecastByUserID'):
            callTimer = basesession.CallTimer('ReliableSinglecastByUserID::%s (Broadcast\\Client)' % method)
            try:
                clientIDs = sm.GetService('sessionMgr').GetClientIDsFromID('userid', userid, refresh=1)
                self.NarrowcastByClientIDsWithoutTheStars(clientIDs, method, args)
            except UnMachoDestination as e:
                self.machoNet.LogInfo('User ', userid, " was not reachable, so he didn't get this singlecast.  Should be fine and dandy.  reason=", e.payload)
                sys.exc_clear()
            except UserError as e:
                if e.msg != 'UnMachoDestination':
                    raise
                self.machoNet.LogInfo('User ', userid, " was not reachable, so he didn't get this singlecast.  Should be fine and dandy.  reason=", e.msg)
                sys.exc_clear()
            finally:
                callTimer.Done()

    def NarrowcastByUserIDs(self, userids, method, *args):
        if not userids:
            return
        with bluepy.Timer('machoNet::NarrowcastByUserIDs'):
            callTimer = basesession.CallTimer('NarrowcastByUserIDs::%s (Broadcast\\Client)' % method)
            try:
                self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='userid', narrowcast=userids), payload=(1, args)))
            finally:
                callTimer.Done()

    def SinglecastByUserID(self, userid, method, *args):
        with bluepy.Timer('machoNet::SinglecastByUserID'):
            callTimer = basesession.CallTimer('SinglecastByUserID::%s (Broadcast\\Client)' % method)
            try:
                self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='userid', narrowcast=[userid]), payload=(1, args)))
            finally:
                callTimer.Done()

    def ReliableSinglecastByCharID(self, charid, method, *args):
        with bluepy.Timer('machoNet::ReliableSinglecastByCharID'):
            callTimer = basesession.CallTimer('ReliableSinglecastByCharID::%s (Broadcast\\Client)' % method)
            try:
                clientIDs = sm.GetService('sessionMgr').GetClientIDsFromID('charid', charid, refresh=1)
                self.NarrowcastByClientIDsWithoutTheStars(clientIDs, method, args)
            except UnMachoDestination as e:
                self.machoNet.LogInfo('Character ', charid, " was not reachable, so he didn't get this singlecast.  Should be fine and dandy.  reason=", e.payload)
                sys.exc_clear()
            except UserError as e:
                if e.msg != 'UnMachoDestination':
                    raise
                self.machoNet.LogInfo('Character ', charid, " was not reachable, so he didn't get this singlecast.  Should be fine and dandy.  reason=", e.msg)
                sys.exc_clear()
            finally:
                callTimer.Done()

    def NarrowcastByCharIDs(self, charids, method, *args):
        if not charids:
            return
        with bluepy.Timer('machoNet::NarrowcastByCharIDs'):
            callTimer = basesession.CallTimer('NarrowcastByCharIDs::%s (Broadcast\\Client)' % method)
            try:
                self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='charid', narrowcast=charids), payload=(1, args)))
            finally:
                callTimer.Done()

    def SinglecastByCharID(self, charid, method, *args):
        with bluepy.Timer('machoNet::SinglecastByCharID'):
            callTimer = basesession.CallTimer('SinglecastByCharID::%s (Broadcast\\Client)' % method)
            try:
                self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='charid', narrowcast=[charid]), payload=(1, args)))
            finally:
                callTimer.Done()
