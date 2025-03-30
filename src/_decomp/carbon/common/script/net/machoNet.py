#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\net\machoNet.py
import collections
import copy
import json
import numbers
import os
import random
import socket
import struct
import weakref
import sys
import blue
import bluepy
import locks
import log
import stackless
import telemetry
import uthread
import uthread2
import carbon.common.script.net.machobase as macho
import carbon.common.script.net.ExceptionMappingGPCS as gpcs
import cluster
import monolithconfig
import monolithmetrics
import monolithsentry
import monolithdisconnectlogger
from carbon.common.script.net.addressCache import MachoAddressCache
from carbon.common.script.net.cachedObject import CachedObject as utilCachedObject
from carbon.common.script.net.GPSExceptions import GPSAddressOccupied, GPSBadAddress, GPSTransportClosed
from carbon.common.script.net.machoNetAddress import MachoAddress
from carbon.common.script.net.machoNetExceptions import MachoException, MachoWrappedException, SessionUnavailable, UnMachoChannel, UnMachoDestination, UserRejectedByVIP
from carbon.common.script.net.machoNetPacket import Notification, PingReq, IdentificationReq
from carbon.common.script.net.machoNetTransport import MachoTransport
from carbon.common.script.net.machoRunTimeStats import MachoRunTimeStats
from carbon.common.script.net.machobase import DumpsSanitized
from carbon.common.script.sys import basesession
from carbon.common.script.sys import crowset, service
from carbon.common.script.sys.buildversion import GetBuildVersionAsInt
from carbon.common.script.util import format as utilFormat
from carbon.common.script.util.weight import ChooseWeighted as weightedChoice
from carbon.common.script.sys.service import ROLE_SERVICE, ROLE_ADMIN, ROLE_ANY, ROLE_VIPLOGIN, SERVICE_RUNNING, SERVICE_START_PENDING, ROLE_GML, ROLE_PLAYER
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsEveUser, IsDustUser
from evecrypto.crypto import CryptoHash
from eveexceptions import ConnectionError, UserError
from eveprefs import prefs, boot
from monolithmetrics import _prometheus
from uthread2 import StartTasklet
from utillib import strx, KeyVal
from machonet_tracing import IngressTracer
try:
    from carbon.server.script.net.onlinedata import OnlineData
except ImportError:
    from carbon.common.script.net.onlinedata import OnlineData

METRIC_SESSIONS = 'machonet.sessions'
METRIC_SESSIONS_TOTAL = METRIC_SESSIONS + '.total'
Enter = blue.pyos.taskletTimer.EnterTasklet
Leave = blue.pyos.taskletTimer.ReturnFromTasklet
OOB_SESSIONNOTIFICATION = 1
CLUSTER_ID = 1
DEFAULT_SUBNETWORK = getattr(boot, 'preferredSubnet', '10.')
PREFERRED_SUBNETWORKS = {'server': getattr(boot, 'preferredServerSubnet', DEFAULT_SUBNETWORK),
 'proxy': getattr(boot, 'preferredProxySubnet', DEFAULT_SUBNETWORK)}
offsetMap = {'tcp:packet:client': 0,
 'tcp:packet:machoNet': 1,
 'tcp:raw:http': 2,
 'tcp:raw:http2': 3,
 'tcp:http:cow': 4,
 'tcp:raw:status': 5}
offsetMap = {'client': offsetMap,
 'server': offsetMap,
 'proxy': offsetMap}
offsetStep = {'proxy': 1000,
 'server': 10,
 'client': 10}
_cached_gps_map = None

def get_gps_map():
    global _cached_gps_map
    if _cached_gps_map is None:
        from carbon.common.script.net.SocketGPS import SecureSocketPacketTransportFactory
        from carbon.common.script.net.SocketGPS import SocketPacketTransportFactory
        from carbon.common.script.net.SocketGPS import SocketTransportFactory
        _cached_gps_map = {'client': {'tcp:raw:http': SocketTransportFactory,
                    'tcp:packet:server': SecureSocketPacketTransportFactory},
         'proxy': {'tcp:packet:client': SecureSocketPacketTransportFactory,
                   'tcp:packet:machoNet': SocketPacketTransportFactory,
                   'tcp:raw:http': SocketTransportFactory},
         'server': {'tcp:packet:machoNet': SocketPacketTransportFactory,
                    'tcp:raw:http': SocketTransportFactory}}
        import iocp
        if iocp.UsingSSL():
            from carbon.common.script.net.SocketGPS import SSLSocketPacketTransportFactory
            log.general.Log('Encryption: SSL', log.LGINFO)
            _cached_gps_map['client']['tcp:packet:server'] = SSLSocketPacketTransportFactory
            _cached_gps_map['proxy']['tcp:packet:client'] = SSLSocketPacketTransportFactory
        else:
            log.general.Log('Encryption: MachoNet', log.LGINFO)
        if iocp.UsingHTTPS():
            from carbon.common.script.net.SocketGPS import SSLSocketTransportFactory
            _cached_gps_map['proxy']['tcp:raw:http'] = SSLSocketTransportFactory
            _cached_gps_map['server']['tcp:raw:http'] = SSLSocketTransportFactory
            log.general.Log('Using HTTPS', log.LGINFO)
    return _cached_gps_map


_cached_gpcs_map = None

def get_gpcs_map():
    global _cached_gpcs_map
    if _cached_gpcs_map is None:
        from carbon.common.script.net.ExceptionWrapperGPCS import ExceptionWrapper
        from carbon.common.script.net.ExceptionMappingGPCS import ExceptionMappingGPCS
        from carbon.common.script.net.ResolveGPCS import ResolveGPCS
        from carbon.common.script.net.ObjectCallGPCS import ObjectCall
        from eve.common.script.net.eveServiceCallGPCS import ServiceCall
        from eve.common.script.net.eveBroadcastStuffGPCS import BroadcastStuff
        from carbon.common.script.net.SessionChangeGPCS import SessionChange
        _cached_gpcs_map = {'server': {None: [ExceptionWrapper,
                           ExceptionMappingGPCS,
                           ResolveGPCS,
                           ObjectCall,
                           ServiceCall,
                           BroadcastStuff],
                    'sessionchange': [SessionChange]},
         'proxy': {None: [ExceptionWrapper,
                          ExceptionMappingGPCS,
                          ObjectCall,
                          ServiceCall,
                          BroadcastStuff],
                   'sessionchange': [SessionChange]},
         'client': {None: [ExceptionWrapper,
                           ExceptionMappingGPCS,
                           ObjectCall,
                           ServiceCall,
                           BroadcastStuff],
                    'sessionchange': [SessionChange]}}
    return _cached_gpcs_map


class MachoNetService(service.Service):
    __guid__ = 'svc.machoNet'
    __displayname__ = 'MachoNet Service'
    __startupdependencies__ = []
    if boot.role == 'server':
        __startupdependencies__ = ['DB2', 'dbLog']
    __dependencies__ = []
    __configvalues__ = {'acceptThreadCount': 20,
     'cleanupInterval': 180,
     'defaultClientPortOffset': 15000,
     'defaultServerPortOffset': 10000,
     'defaultProxyPortOffset': 26000,
     'defaultTunnelPortOffset': 50000,
     'bannedIPs': [],
     'vipMode': 0,
     'reducedTimeouts': 0,
     'callTimeOutInterval': 480 if boot.role != 'client' else 3600,
     'clientKeepAliveTimerInterval': 240,
     'serverKeepAliveTimerInterval': 60,
     'clientLogonQueuePollTime': 60,
     'minimumSolCount': 0,
     'minimumProxyCount': 0,
     'nodeRefreshInterval': 30,
     'proxyStatPollInterval': 180,
     'proxyStatSmoothie': 10,
     'nodeLoadPush': 300,
     'disconnectUnauthorizedUsersPollInterval': 3600,
     'disconnectUnauthorizedUsersDelayInterval': 15,
     'clientSessionTimeoutGranularity': 60,
     'connectionLimit': 1000,
     'maxLoginsPerMinute': 60,
     'acceptDelay': 10,
     'autoLogoffAuthenticatedTransportInterval': 180,
     'debugHeartBeat': 0,
     'largeResponseWarningThreshold': 6000000,
     'largeResponseErrorThreshold': 8000000,
     'callCounterEnabled': 0}
    __exportedcalls__ = {'CheckACL': [ROLE_SERVICE | ROLE_ADMIN],
     'IsThisUserCoolForLogin': [ROLE_SERVICE],
     'GetTransport': [ROLE_SERVICE],
     'GetTransportOfNode': [ROLE_SERVICE],
     'GetNodeFromAddress': [ROLE_SERVICE | ROLE_ADMIN],
     'GetNodeIDsFromServiceMask': [ROLE_SERVICE | ROLE_ADMIN],
     'CheckAddressCache': [ROLE_SERVICE | ROLE_ADMIN],
     'LookupAddressCache': [ROLE_SERVICE | ROLE_ADMIN],
     'ClearNodeOfAddresses': [ROLE_SERVICE | ROLE_ADMIN],
     'GetFullAddressCache': [ROLE_SERVICE | ROLE_ADMIN],
     'GetFullServiceMaskAddressCache': [ROLE_SERVICE | ROLE_ADMIN],
     'GetServiceMaskByServiceID': [ROLE_SERVICE | ROLE_ADMIN],
     'GetNodeID': [ROLE_SERVICE | ROLE_ADMIN],
     'GetServerStatus': [ROLE_ANY],
     'GetGPCS': [ROLE_SERVICE],
     'GetConnectionProperties': [ROLE_ANY],
     'SetConnectionProperty': [ROLE_ADMIN],
     'RefreshConnectivity': [ROLE_ADMIN],
     'GetAddressAndStaticTagsForPrometheus': [ROLE_SERVICE | ROLE_ADMIN],
     'ConnectToServer': [ROLE_ANY],
     'ConnectToAddress': [ROLE_SERVICE],
     'StartTransportReader': [ROLE_SERVICE],
     'DisconnectFromServer': [ROLE_ANY],
     'IsConnected': [ROLE_ANY],
     'GetBasePortNumber': [ROLE_ANY],
     'GetClientSessionID': [ROLE_ANY],
     'GetServiceInfo': [ROLE_ANY],
     'GetTime': [ROLE_ANY],
     'Shutdown': [ROLE_SERVICE],
     'GracefulShutdown': [ROLE_SERVICE],
     'GracefulShutdownStarted': [ROLE_SERVICE],
     'GracefulShutdownComplete': [ROLE_SERVICE],
     'IsClusterShuttingDown': [ROLE_SERVICE],
     'TerminateUnconnectedNodes': [ROLE_SERVICE],
     'TerminateClient': [ROLE_SERVICE],
     'TerminateAllClients': [ROLE_SERVICE],
     'ConnectivityTest': [ROLE_SERVICE],
     'GetCPULoad': [ROLE_SERVICE],
     'GetNetworkStats': [ROLE_SERVICE],
     'GetBlockingCallStats': [ROLE_SERVICE],
     'GetMetrics': [ROLE_SERVICE],
     'GetConnectedSolNodes': [ROLE_SERVICE],
     'GetConnectedProxyNodes': [ROLE_SERVICE],
     'GetConnectedNodes': [ROLE_SERVICE],
     'GetClusterGameStatistics': [ROLE_SERVICE],
     'GetClusterGameStatisticsForClient': [ROLE_PLAYER],
     'GetSessionCounts': [ROLE_SERVICE],
     'SetClusterSessionCounts': [ROLE_SERVICE],
     'GetClusterSessionCounts': [ROLE_SERVICE],
     'SendProvisionalResponse': [ROLE_SERVICE],
     'GetIDOfAddress': [ROLE_SERVICE],
     'ForwardProxyBroadcast': [ROLE_SERVICE],
     'ForwardSinglecastByCharID': [ROLE_SERVICE],
     'PrimeAddressCache': [ROLE_SERVICE],
     'AreTheseServicesRunning': [ROLE_SERVICE],
     'GetValidClientCodeHash': [ROLE_SERVICE],
     'ReloadClientCodeHash': [ROLE_SERVICE],
     'GetLogonQueuePosition': [ROLE_SERVICE],
     'GetLogonQueueStats': [ROLE_SERVICE],
     'GetPolarisExternalTunnelingAddress': [ROLE_SERVICE],
     'IsResurrectedNode': [ROLE_SERVICE],
     'CalculatePortNumber': [ROLE_SERVICE],
     'GetPortOffsetStep': [ROLE_SERVICE],
     'GetGlobalConfig': [ROLE_SERVICE],
     'SetGlobalConfigValue': [ROLE_SERVICE | ROLE_ADMIN],
     'GetGlobalConfigValue': [ROLE_SERVICE | ROLE_ADMIN],
     'ForwardNotificationToNode': [ROLE_SERVICE],
     'GetBaseTunnelPortOffset': [ROLE_SERVICE],
     'PerformanceTest': [ROLE_SERVICE],
     'LogClientCall': [ROLE_SERVICE],
     'ForwardCharacterNotification': [ROLE_SERVICE],
     'DisconnectUsers': [ROLE_SERVICE],
     'SendMessageToPlayers': [ROLE_SERVICE | ROLE_ADMIN | ROLE_GML],
     'GetRuntimeDetails': [ROLE_SERVICE],
     'GetConnectedClusterName': [ROLE_ANY],
     'GetConnectedClusterMode': [ROLE_ANY]}
    __counters__ = {'dataSent': 'traffic',
     'dataReceived': 'traffic',
     'blockingCallTimes': 'traffic',
     'compressedBytes': 'traffic',
     'decompressedBytes': 'traffic',
     'broadcastsResolved': 'traffic',
     'broadcastsMissed': 'normal'}
    __notifyevents__ = {'ProcessSessionChange',
     'OnNewNode',
     'OnNodeDeath',
     'OnMachoObjectDisconnect',
     'OnObjectPublicAttributesUpdated',
     'OnClusterStarting',
     'OnRefreshConnectivity',
     'OnNodeLoadPush',
     'OnPeopleWhoShouldntBeLoggedInNotification',
     'OnVIPListChanged',
     'OnTimeReset',
     'OnClientCodeUpdated',
     'OnClearFetchedData',
     'OnGlobalConfigUpdated',
     'OnClusterDesegmentation',
     'OnCacheServiceReady',
     'OnCacheServiceGroupChange'}
    __gpcsmethodnames__ = {'Objectcast',
     'ObjectcastWithoutTheStars',
     'Queuedcast',
     'QueuedcastWithoutTheStars',
     'Scattercast',
     'ScattercastWithoutTheStars',
     'Broadcast',
     'ClientBroadcast',
     'ClusterBroadcast',
     'ServerBroadcast',
     'ProxyBroadcast',
     'NodeBroadcast',
     'NarrowcastByClientIDs',
     'NarrowcastByClientIDsWithoutTheStars',
     'NarrowcastByCharIDs',
     'NarrowcastByUserIDs',
     'NarrowcastByNodeIDs',
     'SinglecastByServiceMask',
     'SinglecastByClientID',
     'SinglecastByCharID',
     'SinglecastByNodeID',
     'SinglecastByUserID',
     'ConnectToRemoteService',
     'ConnectToAllServices',
     'ConnectToAllNeighboringServices',
     'ConnectToAllSiblingServices',
     'RemoteServiceCallWithoutTheStars',
     'RemoteServiceNotifyWithoutTheStars',
     'ResetAutoResolveCache',
     'RemoteServiceCall',
     'RemoteServiceNotify',
     'OnObjectPublicAttributesUpdated',
     'ReliableSinglecastByCharID',
     'ReliableSinglecastByUserID'}
    __pingrequestorresponse__ = {cluster.MACHONETMSG_TYPE_PING_RSP, cluster.MACHONETMSG_TYPE_PING_REQ}
    __sessioninitorchangenotification__ = {cluster.MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION, cluster.MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION}
    __clientallowedcommands__ = {cluster.MACHONETMSG_TYPE_ERRORRESPONSE,
     cluster.MACHONETMSG_TYPE_NOTIFICATION,
     cluster.MACHONETMSG_TYPE_CALL_RSP,
     cluster.MACHONETMSG_TYPE_CALL_REQ,
     cluster.MACHONETMSG_TYPE_RESOLVE_REQ,
     cluster.MACHONETMSG_TYPE_PING_REQ,
     cluster.MACHONETMSG_TYPE_PING_RSP,
     cluster.MACHONETMSG_TYPE_MOVEMENTNOTIFICATION}
    __notificationtypes__ = {cluster.MACHONETMSG_TYPE_NOTIFICATION,
     cluster.MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION,
     cluster.MACHONETMSG_TYPE_SESSIONINITIALSTATENOTIFICATION,
     cluster.MACHONETMSG_TYPE_MOVEMENTNOTIFICATION}
    __calltypes__ = {cluster.MACHONETMSG_TYPE_CALL_REQ, cluster.MACHONETMSG_TYPE_RESOLVE_REQ}
    __responsetypes__ = {cluster.MACHONETMSG_TYPE_ERRORRESPONSE, cluster.MACHONETMSG_TYPE_CALL_RSP, cluster.MACHONETMSG_TYPE_RESOLVE_RSP}
    __server_scattercast_session_variables__ = {'userid', 'objectID', 'charid'}
    metricsMap = {'CARBON:MachoChar': const.zmetricCounter_MachoChar,
     'CARBON:MachoUser': const.zmetricCounter_MachoUser}
    message_bus = None

    def __init__(self):
        self.shutdown = None
        self.fetchedServiceInfo = None
        self.clockReset = False
        self.handlingClientAuthentication = 0
        self.scheduleCount = 0
        if macho.mode == 'server':
            self.__dependencies__.append('DB2')
        self.clusterSessionStatistics = {}
        self.clusterSessionStatsHistory = []
        self.nodeCPULoadValue = {}
        self.serverNames = {}
        service.Service.__init__(self)
        if macho.mode == 'server' and ('/compileconstants' in blue.pyos.GetArg() or '/compile' in blue.pyos.GetArg()):
            self.connectToCluster = 0
        else:
            self.connectToCluster = 1
        self.acceptStart = None
        self.clientLogonQueue = KeyVal(address='', timestamp=None, position=None, history=None, reportedQueued=False)
        self.serverLogonQueue = []
        self.clientHalfBakedTransports = {}
        self.namedtransports = {}
        self.transportsByID = {}
        self.transportIDbyClientID = {}
        self.transportIDbySessionID = {}
        self.transportIDbyProxyNodeID = {}
        self.transportIDbySolNodeID = {}
        self.transportIDbyAppNodeID = {}
        self.externalAddressesByNodeID = {}
        self.channelHandlersUp = {}
        self.channelHandlersDown = {}
        self.polarisExternalTunneling = None
        self.basePortNumber = self.defaultProxyPortOffset
        self.baseTunnelPortOffset = self.defaultTunnelPortOffset
        self.nodeID = None
        self.machineID = None
        self.nodeIndex = None
        self.expectedLoadValue = {}
        self.clientIDOffset = 1
        self.stop = 1
        self.transportID = 1L
        self.calls = {}
        self.timeoutCalls = {}
        self.callsCountMax = 0
        self.callsCountMin = 0
        self.callID = 1L
        self._addressCache = MachoAddressCache()
        self.myProxyNodeID = None
        self.dontLayTracksTo = {}
        if macho.mode == 'client':
            self.authenticating = 0
            self.gettingServerStatus = 0
            self.clientSessionID = 0
        self.seq = 0L
        self.seqwait = {}
        self.notifySequenceIDByNodeID = collections.defaultdict(int)
        self.serviceInfo = {}
        self.locks = {}
        self.serviceMappings = {}
        self.serviceMaskByServiceID = {}
        self.serviceNameByServiceID = {}
        self.factories = {}
        self.spam = set()
        self.kickedTick = 0
        self.startedWhen = blue.os.GetWallclockTime()
        self.paon = None
        self.paonLock = uthread.Semaphore('MachoNet:paonLock')
        self.vipLock = uthread.Semaphore('MachoNet:vipLock')
        self.fetchedDataLock = uthread.Semaphore('MachoNet:fetchedDataLock')
        self.clusterStartLock = uthread.Semaphore('MachoNet:clusterStartLock')
        self.callCounter = collections.defaultdict(int)
        for svc in sm.services.itervalues():
            if hasattr(svc, '__machoresolve__'):
                self.serviceInfo[svc.__logname__] = svc.__machoresolve__

        self.globalConfig = None
        self.shutdownInProgress = False
        self.serviceMask = cluster.SERVICE_NONE
        self.getNodeFromAddressWarnsDone = set()
        self.statusData = {}
        self.statusCallbacks = {}
        self.onlineData = OnlineData(self)
        self.heartbeat_lagging = False

    def SendMessageToPlayers(self, message, includeEve, includeDust):
        recipients = []
        for sid, sess in basesession.allSessionsBySID.iteritems():
            userID = getattr(sess, 'userid', None)
            clientID = getattr(sess, 'clientID', None)
            if userID and clientID:
                if IsDustUser(userID) and includeDust or IsEveUser(userID) and includeEve:
                    recipients.append(clientID)

        self.NarrowcastByClientIDs(recipients, 'OnServerMessage', message)

    def ForwardNotificationToNode(self, source, destination, userID, payload):
        orginalClientID = source.clientID
        localTransport = self.transportsByID[self.transportIDbyClientID[orginalClientID]]
        packet = Notification(source=source, destination=destination, userID=userID, payload=payload)
        self.HandleMessage(localTransport, packet)
        self.SinglecastByClientID(orginalClientID, 'OnUpdateServiceMapping', destination.service, destination.nodeID)

    def GetBaseTunnelPortOffset(self):
        return self.baseTunnelPortOffset

    def IsResurrectedNode(self):
        return self.resurrectedNode

    def GetPolarisExternalTunnelingAddress(self):
        if macho.mode == 'server' and self.polarisExternalTunneling is not None and self.polarisExternalTunneling.proxyNodeID in self.transportIDbyProxyNodeID:
            return self.polarisExternalTunneling.address
        else:
            lastNodeID = None
            last = None
            for nodeID, transportID in self.transportIDbyProxyNodeID.iteritems():
                machoTransport = self.transportsByID.get(transportID, None)
                if machoTransport is not None:
                    host2, port2 = machoTransport.transport.GetAddress().split(':')
                    tmp2 = host2.split('.')
                    if last is None or int(tmp2[3]) < last:
                        last = int(tmp2[3])
                        lastNodeID = nodeID

            if macho.mode == 'server':
                self.polarisExternalTunneling = KeyVal(proxyNodeID=lastNodeID, address=self.session.ConnectToProxyServerService('machoNet', lastNodeID).GetPolarisExternalTunnelingAddress())
                return self.polarisExternalTunneling.address
            address = self.namedtransports['tcp:raw:http'].GetESPAddress()
            host, port = address.split(':')
            tmp = host.split('.')
            last = int(host.split('.')[3])
            host = '.'.join(tmp[:3]) + '.' + str(last)
            return host + ':%d' % (self.defaultTunnelPortOffset + 1)

    def SessionsFromClientIDs(self, clientIDs):
        sessions = []
        for clientID in clientIDs:
            transportID = self.transportIDbyClientID.get(clientID, None)
            if transportID is not None:
                transport = self.transportsByID.get(transportID, None)
                if transport is not None:
                    sessions.append(transport._SessionFromClientID(clientID))

        return sessions

    def GetFactory(self, factoryClass, args):
        k = args[1]
        if k not in self.factories:
            f = CreateInstance(factoryClass, args)
            if 'machoNet' in k:
                f.MaxPacketSize = 1073741824
            self.factories[k] = (factoryClass, args, f)
        else:
            n, a, f = self.factories[k]
            if n != factoryClass or a != args:
                log.LogTraceback()
                raise RuntimeError('Thou shall not GetFactory with differing factoryName or args')
        return f

    def Run(self, memStream = None):
        self.vipkeys = None
        self.vipUsers = None
        self.peopleWhoShouldntBeLoggedIn = {}
        self.heartbeatInterval = 60
        self.state = SERVICE_START_PENDING
        service.Service.Run(self, memStream)
        self.LogInfo('Running macho net')
        self.stop = 0
        self.clusterStartupPhase = False
        self.clusterIsDesegmented = False
        self.availableLoginSlots = 0
        if macho.mode in ('server', 'proxy'):
            machineName = blue.pyos.GetEnv().get('COMPUTERNAME', 'LOCALHOST').lower()
            monolithmetrics.set_macho_machine_name(machineName)
        if macho.mode == 'client' and not int(prefs.GetValue('http', 0)):
            try:
                del offsetMap[macho.mode]['tcp:raw:http']
            except StandardError:
                sys.exc_clear()

        if macho.mode == 'client':
            self.basePortNumber = self.defaultClientPortOffset
        elif macho.mode == 'server':
            self.basePortNumber = self.defaultServerPortOffset
        elif macho.mode == 'proxy':
            self.basePortNumber = self.defaultProxyPortOffset
        else:
            return
        blue.net.SetMode(macho.mode)
        self.LogInfo('Opening listen ports')
        self.resurrectedNode = False
        fixedhop = None
        nodeIndex = 0
        self.LogInfo('MachoNet is starting up using the NEW cluster configuration tables')
        for arg in blue.pyos.GetArg():
            if arg.lower().startswith('/machohop='):
                fixedhop = int(arg[len('/machohop='):])
            if arg.lower().startswith('/machoresurrection'):
                self.resurrectedNode = True

        gpsMap = get_gps_map()
        offsets = offsetMap[macho.mode].items()
        offsets = [ (k, v) for k, v in offsets if k in gpsMap[macho.mode] ]
        offsets.sort(key=lambda t: t[1])
        transports = {}
        if fixedhop is not None:
            self.basePortNumber += fixedhop * offsetStep[macho.mode]
            self.baseTunnelPortOffset += fixedhop * offsetStep[macho.mode]
            nodeIndex = fixedhop
        while True:
            try:
                for each, offset in offsets:
                    port = self.basePortNumber + offset
                    self.LogInfo('Open listen transport for ', each, ' on port ', port)
                    factory = self.GetFactory(gpsMap[macho.mode][each], (macho.mode == 'proxy' and each.endswith(':client'), each))
                    transports[each] = factory.Listen(port)

            except GPSAddressOccupied as e:
                self.LogInfo('port ', port, ' occupied')
                for each in transports.itervalues():
                    each.Close('Desired address occupied in Run')

                transports.clear()
                sys.exc_clear()
            else:
                self.nodeIndex = nodeIndex
                monolithmetrics.set_macho_node_index(self.nodeIndex)
                monolithsentry.set_macho_node_index(self.nodeIndex)
                break

            if fixedhop is not None:
                errreason = 'Failed to acquire the required port range running in fixed hop (=%d) mode.  Terminating process' % (fixedhop,)
                self.LogError(errreason)
                log.Quit(errreason)
            self.basePortNumber += offsetStep[macho.mode]
            nodeIndex += 1
            self.baseTunnelPortOffset += offsetStep[macho.mode]
            if self.basePortNumber > self.defaultTunnelPortOffset:
                raise RuntimeError("Something is seriously wrong.  I've tried plenty of port number ranges, and still no luck.")
            self.LogInfo('looping, base=', self.basePortNumber)

        self.LogInfo('All transports acquired:  ', transports, ', ', offsetMap[macho.mode])
        self.namedtransports = transports
        self.SetStatusKeyValuePair('clusterStatus', -800)
        self.SetStatusKeyValuePair('clusterStatusText', 'Sockets acqired')
        if macho.mode == 'server' or macho.mode == 'proxy':
            uthread.new(self.StatusSocketLoop)
        if macho.mode == 'proxy':
            self.nodeID = self.GetIDOfAddress(self.GetTransport('tcp:packet:client').GetInternalAddress(), clientMode=False)
            print 'nodeID=', self.nodeID
        elif macho.mode == 'server':
            self.LogInfo('Registering node')
            self.dbzcluster = self.DB2.GetSchema('zcluster')
            self.dbcluster = self.DB2.GetSchema('cluster')
            self.dbzuser = self.DB2.GetSchema('zuser')
            retry = False
            while True:
                self.dbzcluster.Nodes_TrashLimbos(self.cleanupInterval)
                host, port = self.GetTransport('tcp:packet:machoNet').GetExternalAddress().split(':')
                internalAddress = self.GetTransport('tcp:packet:machoNet').GetInternalAddress().split(':')[0]
                self.LogInfo('Registering to the cluster database. ClusterID:', CLUSTER_ID, 'machineID:', None, 'machineName:', machineName, 'nodeIndex:', nodeIndex)
                ret = self.dbzcluster.Nodes_Register2(CLUSTER_ID, None, machineName, self.nodeIndex, 'SOL', macho.version, boot.version, GetBuildVersionAsInt(), blue.os.pid, self.resurrectedNode, internalAddress)
                errreason = None
                if ret == -1:
                    errreason = "zcluster.Nodes_Register refused to accept the registration.  The cluster has already passed it's connectivity tests."
                    if not retry:
                        lastHeartBeat = self.DB2.SQL('SELECT lastHeartBeat= MAX(heartbeat) FROM zcluster.nodes')[0].lastHeartBeat
                        countDateTime = self.DB2.SQL("SELECT countDateTime = CONVERT(datetime, [value], 121) FROM zsystem.settings WHERE [group] = 'zcluster' AND [key] = 'TrashLimboNodes-LastCall'")[0].countDateTime
                        if lastHeartBeat is not None:
                            delay = 3000 + (self.cleanupInterval * const.SEC + lastHeartBeat - blue.os.GetWallclockTime()) / const.MSEC
                            if countDateTime is not None:
                                delay = max(delay, 3000 + (countDateTime + self.cleanupInterval * const.SEC - blue.os.GetWallclockTime()) / const.MSEC)
                            if delay > 0:
                                print errreason
                                self.LogWarn(errreason)
                                print 'The previous run might however be dead, delaying and retrying after ', delay, ' ms...'
                                self.LogWarn('The previous run might however be dead, delaying and retrying after ', delay, ' ms...')
                                blue.pyos.synchro.SleepWallclock(delay)
                                retry = True
                                continue
                elif ret == -2:
                    errreason = 'An app lock timeout occurred in zcluster.Nodes_Register2'
                elif ret == -3:
                    errreason = ('The machine ', machineName, ' is not a member of the specified cluster.                             Configure zcluster.proxies and zcluster.machines correctly.')
                elif ret == -4:
                    localip = GetPreferredHostByName(machineName)
                    if machineName != localip:
                        self.LogError('Did not find machine configured for', machineName, 'Retrying with the ip address:', localip)
                        machineName = localip
                        continue
                    else:
                        errreason = 'Could not find a machineName configured to match: %s. Configure zcluster.machines correctly.' % machineName
                elif isinstance(ret, numbers.Integral):
                    errreason = 'An unspecified error occurred while registering the node: %d' % ret
                if errreason:
                    self.LogError(errreason)
                    log.Quit(errreason)
                break

            self.nodeID = ret[0][0].nodeID
            self.serviceMask = ret[0][0].serviceMask
            self.clusterGroup = ret[0][0].clusterGroup
            monolithmetrics.set_macho_cluster_group(self.clusterGroup)
            monolithsentry.set_macho_cluster_group(self.clusterGroup)
            self.machineID = ret[0][0].machineID
            monolithsentry.set_macho_machine_id(self.machineID)
            if self.serviceMask is None:
                self.serviceMask = cluster.SERVICE_ALL
            monolithmetrics.set_macho_service_mask(self.serviceMask)
            monolithsentry.set_macho_service_mask(self.serviceMask)
            self.premapped = prefs.clusterMode in ('TEST', 'LIVE')
            for each in ret[1]:
                self.serviceMappings[each.serviceName] = [each.serviceID, each.serviceMask]
                self.serviceMaskByServiceID[each.serviceID] = each.serviceMask
                self.serviceNameByServiceID[each.serviceID] = each.serviceName

            for each in ret[2]:
                self.serverNames[each.nodeID] = getattr(each, 'machineName', None)

            if self.connectToCluster and not self.premapped:
                polarisNodeID = self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0)
            self.LogInfo('Server Registration Complete. NodeID:', self.nodeID, ' serviceMask:', self.serviceMask, ', machineID:', self.machineID, ' nodeIndex:', self.nodeIndex)
        else:
            self.nodeID = None
        monolithsentry.set_macho_node_id(self.nodeID)
        if macho.mode != 'client':
            monolithmetrics.event(title='Eve Node Started')
            monolithmetrics.increment(metric='node.started')
        self.SetStatusKeyValuePair('clusterStatus', -700)
        self.SetStatusKeyValuePair('clusterStatusText', 'Node registered')
        self.SetStatusCallBack('nodeID', lambda : self.nodeID)
        if self.nodeID:
            blue.net.SetMyNodeID(self.nodeID)
        if macho.mode == 'server':
            self.LogInfo('Establishing timers')
            uthread.worker('machoNet::OnHeartBeat', self.OnHeartBeat)
            uthread.worker('machoNet::OnCleanUp', self.OnCleanUp)
            uthread.worker('machoNet::GracefulShutdown', self.__GracefulShutdownWorker)
            self.acceptThreadCount = 1
            self.LogInfo('Monkeypatching acceptThreadCount. Value now ' + str(self.acceptThreadCount))
        machoListeners = [ k for k in gpsMap[macho.mode].keys() if k.find(':packet:') >= 0 ]
        machoListeners = [ k for k in machoListeners if k in offsetMap[macho.mode] ]
        for eachTransport in machoListeners:
            threadCount = self.acceptThreadCount
            if 'machoNet' in eachTransport:
                threadCount = 1
            self.LogInfo('Launching ', threadCount, ' listen threads for transport ', eachTransport)
            for eachThread in range(0, threadCount):
                uthread.new(self.AcceptLoop, eachTransport).context = 'machoNet::AcceptLoop'

        self.acceptThreadCount = 20
        self.LogInfo('Restoring value of acceptThreadCount')
        if macho.mode == 'server' and self.connectToCluster:
            self.LogInfo('Connectivity[Startup]:  Establishing communications with proxy servers')
            layTracksTo = self._GetLayTracksTo()
            if not layTracksTo:
                self.LayTracksIfNeeded('127.0.0.1:%d' % (self.defaultProxyPortOffset + offsetMap['proxy']['tcp:packet:machoNet']), None, 'machoNet::Run')
            else:
                layTracksTo = list(layTracksTo)
                random.shuffle(layTracksTo)
                for each in layTracksTo:
                    self.LayTracksIfNeeded('%s:%d' % (each.ipAddress, each.port), each.nodeID, 'machoNet::Run')

        self.SetStatusKeyValuePair('clusterStatus', -600)
        self.SetStatusKeyValuePair('clusterStatusText', 'LayTracks done')
        self.LogInfo('Creating handlers')
        machoNet = weakref.proxy(self)
        gpcsMap = get_gpcs_map()
        for each in gpcsMap[macho.mode]:
            nodes = []
            for d in gpcsMap[macho.mode][each]:
                nodes.append(CreateInstance(d))

            for i in range(0, len(nodes)):
                prior = machoNet
                next = None
                if i > 0:
                    prior = nodes[i - 1]
                if i + 1 < len(nodes):
                    next = nodes[i + 1]
                nodes[i].next = next
                nodes[i].prior = prior
                nodes[i].machoNet = machoNet

            for i in range(0, len(nodes)):
                current = nodes[i]
                while current is not None and current != machoNet:
                    if not hasattr(nodes[i], 'ForwardNotifyDown') and current.prior is not None and hasattr(current.prior, 'NotifyDown'):
                        nodes[i].ForwardNotifyDown = current.prior.NotifyDown
                    if not hasattr(nodes[i], 'ForwardCallDown') and current.prior is not None and hasattr(current.prior, 'CallDown'):
                        nodes[i].ForwardCallDown = current.prior.CallDown
                    current = current.prior

                current = nodes[i]
                while current is not None and current != machoNet:
                    if not hasattr(nodes[i], 'ForwardNotifyUp') and current.next is not None and hasattr(current.next, 'NotifyUp'):
                        nodes[i].ForwardNotifyUp = current.next.NotifyUp
                    if not hasattr(nodes[i], 'ForwardCallUp') and current.next is not None and hasattr(current.next, 'CallUp'):
                        nodes[i].ForwardCallUp = current.next.CallUp
                    current = current.next

            self.channelHandlersUp[each] = nodes[0]
            if not hasattr(self.channelHandlersUp[each], 'CallUp') and hasattr(self.channelHandlersUp[each], 'ForwardCallUp'):
                self.channelHandlersUp[each].CallUp = self.channelHandlersUp[each].ForwardCallUp
            if not hasattr(self.channelHandlersUp[each], 'NotifyUp') and hasattr(self.channelHandlersUp[each], 'ForwardNotifyUp'):
                self.channelHandlersUp[each].NotifyUp = self.channelHandlersUp[each].ForwardNotifyUp
            self.channelHandlersDown[each] = nodes[len(nodes) - 1]
            if not hasattr(self.channelHandlersDown[each], 'CallDown') and hasattr(self.channelHandlersDown[each], 'ForwardCallDown'):
                self.channelHandlersDown[each].CallDown = self.channelHandlersDown[each].ForwardCallDown
            if not hasattr(self.channelHandlersDown[each], 'NotifyDown') and hasattr(self.channelHandlersDown[each], 'ForwardNotifyDown'):
                self.channelHandlersDown[each].NotifyDown = self.channelHandlersDown[each].ForwardNotifyDown

        if macho.mode == 'server' and self.connectToCluster:
            self.dbzmetric = self.DB2.GetSchema('zmetric')
            uthread.new(self.__NodeWatcher).context = 'machoNet::NodeWatcher'
        elif macho.mode == 'proxy':
            uthread.new(self.__ClientSessionMaxTimePoll).context = 'machoNet::ClientSessionMaxTimePoll'
        uthread.new(self.__TimeoutCallLoop).context = 'machoNet::TimeoutCallLoop'
        uthread.new(self.__KATLoop).context = 'machoNet::KATLoop'
        self.acceptStart = blue.os.GetWallclockTime()
        self.SetStatusKeyValuePair('clusterStatus', -500)
        self.SetStatusKeyValuePair('clusterStatusText', 'Machonet accept start')
        self.stats = MachoRunTimeStats(self.transportsByID)
        self.stats.Enable()
        self.LogNotice('MachoNet started with acceptDelay of %d seconds. I will accept connections at %s' % (self.acceptDelay, utilFormat.FmtDateEng(self.acceptStart + self.acceptDelay * const.SEC)))
        self.state = SERVICE_RUNNING
        for each in self.__gpcsmethodnames__:
            current = self.GetGPCS()
            while 1:
                if hasattr(current, each):
                    setattr(self, each, getattr(current, each))
                    break
                if not hasattr(current, 'prior') or current.prior is None:
                    self.LogError("MachoNet GPCS doesn't contain ", each, 'current=', current)
                    break
                current = current.prior

        if macho.mode == 'server' and self.connectToCluster:
            self.dbzclient = self.DB2.GetSchema('zclient')
        if macho.mode in ('server', 'proxy'):
            self.LogNotice('Starting driftTimeMetrics on', macho.mode, machineName, nodeIndex)
            from eve.server.script.net import timedriftmetrics
            self._timeDriftMetrics = timedriftmetrics.TimeDriftMetrics(nodeIndex)
            self._timeDriftMetrics.start_worker()
        else:
            self._timeDriftMetrics = None
        sm.FavourMe(self.OnNodeDeath)

    def OnCacheServiceReady(self):
        monolithconfig.set_service_manager(sm)

    def OnCacheServiceGroupChange(self, group):
        monolithconfig.flush(group=group)

    def _begin_publishing_status(self):
        proxy_node_id = self.GetNodeID()
        proxy_name = self.GetLocalHostName()
        proxy_ipv4_address = self.namedtransports['tcp:packet:machoNet'].GetInternalAddress().split(':')[0]
        proxy_ipv4 = struct.unpack('!I', socket.inet_aton(proxy_ipv4_address))[0]
        esp_ipv4 = self.namedtransports['tcp:raw:http'].GetESPAddress()
        metrics_port = _prometheus.prometheus_port
        start_time = blue.sysinfo.processStartTime
        while True:
            try:
                self.session.ConnectToRemoteService('externalQueueMgr').PublishProxyEvent(proxy_node_id, proxy_name, proxy_ipv4, esp_ipv4, metrics_port, start_time, os.getpid())
            except Exception as e:
                log.LogException('Proxy node publish attempt failed')

            blue.synchro.SleepWallclock(5000)

    def IsClusterStarted(self):
        return self.clusterStartupPhase

    def OnClusterStarting(self, polarisNodeID):
        with self.clusterStartLock:
            if self.clusterStartupPhase:
                return
            self.SetStatusKeyValuePair('clusterStatus', -80)
            self.SetStatusKeyValuePair('clusterStatusText', 'OnClusterStarting')
            if macho.mode == 'proxy':
                StartTasklet(self._begin_publishing_status)
                uthread.new(self.__LoginQueueUpdater).context = 'machoNet::LoginQueueUpdater'
            if macho.mode == 'server' and (self.GetNodeID() == self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0) or self.IsResurrectedNode()):
                config = self.dbzcluster.Cluster_DowntimeInfo()
                if len(config):
                    when = config[0].shutdownWhen * const.MIN + blue.os.GetWallclockTime() / const.DAY * const.DAY
                    if when < blue.os.GetWallclockTime():
                        when += const.DAY
                    if self.IsResurrectedNode():
                        self.GracefulShutdown(config[0].shutdownUserID, when, 0, config[0].shutdownReason)
                    else:
                        self.session.ConnectToAllSolServerServices('machoNet').GracefulShutdown(config[0].shutdownUserID, when, 0, config[0].shutdownReason)
            for transportID, transport in self.transportsByID.iteritems():
                nodeID = getattr(transport, 'nodeID', None)
                if nodeID is None:
                    log.LogTraceback('Transport with nodeID == None connected before OnClusterStarting')
                else:
                    isProxy = nodeID in self.transportIDbyProxyNodeID
                    isPolaris = nodeID == polarisNodeID
                    address, serviceMask = self.externalAddressesByNodeID[nodeID]
                    sm.ScatterEvent('OnNewNode', nodeID, address, isProxy, isPolaris, serviceMask)

            if macho.mode == 'proxy':
                cfg.LoadCfgData()
            if macho.mode == 'server' and self.connectToCluster:
                uthread.new(self.__SessionStatWatcher).context = 'machoNet::SessionStatWatcher'
                uthread.new(self.__NodeLoadPush).context = 'machoNet::NodeLoadPush'
                uthread.new(self.__DisconnectUnauthorizedUsers).context = 'machoNet::DisconnectUnauthorizedUsers'
            sm.ScatterEvent('OnClusterStartup')
            if macho.mode == 'proxy':
                self.SetStatusKeyValuePair('clusterStatus', 0)
                self.SetStatusKeyValuePair('clusterStatusText', 'Ready')
            self.GetGlobalConfig()
            self.clusterStartupPhase = True

    def OnNewNode(self, nodeID, nodeAddress, isProxy, isPolaris, serviceMask):
        if isProxy:
            self._addressCache.UnmarkDeadNode(nodeID)
        self.LogNotice('machoNet::OnNewNode: Calling LoadNodeToServiceMaskMapping(', ','.join([str(nodeID), str(serviceMask)]), ')')
        self._addressCache.LoadNodeToServiceMaskMapping(nodeID, serviceMask)
        if macho.mode == 'server':
            clientListener = self.GetTransport('tcp:packet:client')
            self.namedtransports['tcp:packet:client'] = None
            if clientListener is not None:
                clientListener.Close('The server has accepted a proxy connection, so it is closing all direct client connections.')
            hasSpewed = False
            for transportID in self.transportIDbyClientID.values():
                transportIDs = self.transportIDbyProxyNodeID.values() + self.transportIDbySolNodeID.values()
                if transportID not in transportIDs:
                    if transportIDs:
                        if not hasSpewed:
                            hasSpewed = True
                            self.LogError('Disconnecting a node->node connection!?!  Man do I smell deep shit going on here...')
                            self.LogError('Got a new node, and started iterating over transports to close them.')
                            self.LogError("Found a deadite that isn'it a known node->node transport.")
                            self.LogError('However, that is total crud, and we know it, because this is a sol server with proxy or sol connections.')
                            self.LogError("That means there are NO direct client connections, and we've got a situation here.")
                            self.LogError("Here's a stacktrace:")
                            log.LogTraceback()
                            self.LogError("And here's the new info we got:")
                            self.LogError('nodeID=', nodeID)
                            self.LogError('address=', nodeAddress)
                            self.LogError('isPolaris=', isPolaris)
                            self.LogError('I think I need an Alkaseltzer...')
                            self.LogError('self.transportsByID[transportID]=', self.transportsByID[transportID])
                    else:
                        self.transportsByID[transportID].Close('The server has established communications with a proxy server.  All direct communications are banned.')

    def OnTimeReset(self, oldTime, newTime):
        if self.acceptStart:
            delta = newTime - oldTime
            self.LogInfo('MachoNet (%s) acceptTime adjusted for DB time change' % macho.mode, self.acceptStart, delta, self.acceptStart + delta)
            self.acceptStart += delta
        else:
            self.LogInfo('MachoNet (%s) acceptTime not adjusted for DB time change (not used yet?)' % macho.mode)

    def ConnectivityTest(self, offset, proxyNodeCount, serverNodeCount):
        if offset is not None:
            if offset and not self.clockReset and macho.mode == 'proxy':
                now = blue.os.GetWallclockTimeNow()
                newnow = now + offset
                print 'Correcting clock... advancing ', float(offset) / float(const.SEC), ' secs'
                blue.pyos.synchro.ResetClock(newnow)
                sm.ScatterEvent('OnTimeReset', now, newnow)
            self.clockReset = True
        if len(self.transportIDbySolNodeID) != serverNodeCount:
            self.LogInfo('ConnectivityTest Failed:  expected ', serverNodeCount, ' server nodes, found ', len(self.transportIDbySolNodeID))
        if len(self.transportIDbyProxyNodeID) != proxyNodeCount:
            self.LogInfo('ConnectivityTest Failed:  expected ', proxyNodeCount, ' proxy nodes, found ', len(self.transportIDbyProxyNodeID))
        return len(self.transportIDbySolNodeID) == serverNodeCount and len(self.transportIDbyProxyNodeID) == proxyNodeCount

    def OnObjectPublicAttributesUpdated(self, *args):
        pass

    def Stop(self, memStream = None, reason = 'The server is stopping'):
        self.LogInfo('Stopping macho net node ', self.nodeID)
        self.stop = 1
        self.acceptStart = None
        if macho.mode == 'server':
            if self.nodeID is not None and sm.IsServiceRunning('DB2'):
                self.DB2.SetAllowSynchronousCalls(1)
                self.dbzcluster.Nodes_Trash(self.nodeID, reason, 1)
                self.DB2.SetAllowSynchronousCalls(0)
        while len(self.namedtransports):
            ls = self.namedtransports.values()
            self.namedtransports = {}
            for each in ls:
                if each is not None:
                    try:
                        each.disconnectsilently = getattr(each, 'disconnectsilently', 2)
                        each.Close('The machoNet service is stopping')
                    except StandardError:
                        log.LogException()
                        self.LogInfo('Exception during Close ignored.')
                        sys.exc_clear()

        while len(self.transportsByID):
            ls = self.transportsByID.values()
            self.transportsByID = {}
            for each in ls:
                try:
                    each.disconnectsilently = getattr(each, 'disconnectsilently', 2)
                    each.Close('The machoNet service is stopping')
                except StandardError:
                    log.LogException()
                    self.LogInfo('Exception during Close ignored.')
                    sys.exc_clear()

        self.transportIDbySolNodeID = {}
        self.transportIDbyAppNodeID = {}
        self.transportIDbyProxyNodeID = {}
        blue.net.ClearProxyNodes()
        self.transportIDbyClientID = {}
        self.transportIDbySessionID = {}
        service.Service.Stop(self, memStream)

    def GetHtmlStateDetails(self, k, v, detailed):
        from carbon.common.script.util import htmlwriter
        wr = htmlwriter.HtmlWriter()
        if k == 'basePortNumber':
            return ('Base Port', v)
        if k == 'defaultTunnelPortOffset':
            return ('Default Tunneling Port', v)
        if k == '_addressCache':
            if detailed:
                nodeMap = self._addressCache.GetCachedServiceAddressMap()
                hd = ['Node', 'Service', 'Addresses']
                li = []
                for node in sorted(nodeMap.keys()):
                    services = {}
                    for service, address in nodeMap[node]:
                        if service in services:
                            services[service].append(address)
                        else:
                            services[service] = [address]

                    for service in sorted(services.keys()):
                        addresses = sorted(services[service])
                        li.append([node, service, ', '.join((str(addr) for addr in addresses))])

                return ('Address Cache', wr.GetTable(hd, li))
            else:
                return ('Address Cache', self._addressCache.Report())
        elif k == 'namedtransports':
            if detailed:
                hd = ['Name', 'GPS Transport']
                li = []
                for each in v.iterkeys():
                    li.append([each, v[each].__class__.__name__])

                return ('Named Transports', wr.GetTable(hd, li))
            else:
                r = ''
                comma = ''
                for each in v.iterkeys():
                    r = r + comma + each + '=' + v[each].__class__.__name__
                    comma = ', '

                return ('Named Transports', r)
        else:
            if k == 'dontLayTracksTo':
                r = ''
                comma = ''
                for each, at in v:
                    r = r + comma + '%s at %s' % (each, at)
                    comma = ', '

                return ('Currently Laying Tracks to, or have already laid tracks to ', r)
            if k == 'transportsByID':
                if detailed:
                    hd = ['TRID',
                     'Type',
                     'Address',
                     'NodeID/<br>ClientID',
                     'Dependants',
                     'Sessions',
                     'Calls',
                     'RTT<br>(ms)',
                     'TDiff<br>(ms)']
                    li = []
                    for each in v.iterkeys():
                        if v[each].nodeID:
                            theID = v[each].nodeID
                        else:
                            theID = v[each].clientID
                        r = ''
                        comma = ''
                        for sess in v[each].sessions.iterkeys():
                            r = r + comma + strx(sess) + '=' + strx(v[each].sessions[sess].sid)
                            comma = ', '

                        if abs(v[each].estimatedRTT / const.MSEC) >= 100:
                            rtt = '%d' % (v[each].estimatedRTT / const.MSEC)
                        else:
                            rtt = '%-2.1f' % (v[each].estimatedRTT / const.MSEC)
                        if abs(v[each].timeDiff / const.MSEC) >= 100:
                            tdiff = '%d' % (v[each].timeDiff / const.MSEC)
                        else:
                            tdiff = '%-2.1f' % (v[each].timeDiff / const.MSEC)
                        li.append([each,
                         v[each].transportName,
                         v[each].transport.address,
                         theID,
                         strx(v[each].dependants),
                         htmlwriter.Swing(r),
                         strx(v[each].calls),
                         rtt,
                         tdiff])
                        li.sort()

                    return ('Transports by ID', wr.GetTable(hd, li))
                else:
                    r = ''
                    comma = ''
                    for each in v.iterkeys():
                        r = r + comma + strx(each) + '=' + strx(v[each].transport.address)
                        comma = ', '

                    return ('Transports by ID', r)
            elif k == 'transportIDbyClientID':
                if detailed:
                    hd = ['ClientID', 'TRID']
                    li = []
                    for each in v.iterkeys():
                        li.append([each, v[each]])

                    return ('TransportID by ClientID', wr.GetTable(hd, li))
                else:
                    r = ''
                    comma = ''
                    for each in v.iterkeys():
                        r = r + comma + strx(each) + '=>' + strx(v[each])
                        comma = ', '

                    return ('TransportID by ClientID', r)
            elif k in ('channelHandlersUp', 'channelHandlersDown'):
                inout = 'Inbound'
                if k == 'channelHandlersDown':
                    inout = 'Outbound'
                if detailed:
                    hd = ['Channel', 'Handler']
                    li = []
                    for each in v.iterkeys():
                        li.append([each, v[each].__class__.__name__])

                    return ('%s Channel Handlers' % inout, wr.GetTable(hd, li))
                else:
                    r = ''
                    comma = ''
                    for each in v.iterkeys():
                        r = r + comma + strx(each) + '=>' + v[each].__class__.__name__
                        comma = ', '

                    return ('%s Channel Handlers' % inout, r)
            elif k == 'transportIDbySolNodeID':
                if detailed:
                    hd = ['Sol NodeID', 'TRID']
                    li = []
                    for each in v.iterkeys():
                        li.append([each, v[each]])

                    return ('TransportID by Sol NodeID', wr.GetTable(hd, li))
                else:
                    r = ''
                    comma = ''
                    for each in v.iterkeys():
                        r = r + comma + strx(each) + '=>' + strx(v[each])
                        comma = ', '

                    return ('TransportID by Sol NodeID', r)
            elif k == 'transportIDbyProxy NodeID':
                if detailed:
                    hd = ['Proxy NodeID', 'TRID']
                    li = []
                    for each in v.iterkeys():
                        li.append([each, v[each]])

                    return ('TransportID by Proxy NodeID', wr.GetTable(hd, li))
                else:
                    r = ''
                    comma = ''
                    for each in v.iterkeys():
                        r = r + comma + strx(each) + '=>' + strx(v[each])
                        comma = ', '

                    return ('TransportID by Proxy NodeID', r)
            else:
                if k == 'connectionLimit':
                    return ('Max Connections', v)
                if k == 'callID':
                    return ('Call ID', 'A running number used to identify blocking calls made on this server.  The current value is %d, so %d blocking calls have been made since the service was started.' % (v, v - 1))
                if k == 'transportID':
                    return ('Transport ID', 'A running number used to identify transports connected to this server.  The current value is %d, so %d transports have been used by the service so far.' % (v, v - 1))
                if k == 'nodeID':
                    return ('Node ID', 'For proxies and sol servers, a unique address that can be used for addressing packets to this server.  Value=%d' % v)
                if k == 'mode':
                    return ('Macho Mode', 'Whether this is a client, server, or proxy.  Value=%s' % v)
                if k == 'stop':
                    if v:
                        v = 'The service is stopping, so it will be doing so.'
                    else:
                        v = 'The service is running, so it will leave them alone for now.'
                    return ('Stop?', "Whether or not the service should shut down it's transports.  %s" % v)

    def add_session_transport_lookup(self, session_id, transport_id):
        self.transportIDbySessionID[session_id] = transport_id
        monolithmetrics.increment(metric=METRIC_SESSIONS)
        monolithmetrics.gauge(metric=METRIC_SESSIONS_TOTAL, value=len(self.transportIDbySessionID))

    def remove_session_transport_lookup(self, session_id):
        del self.transportIDbySessionID[session_id]
        monolithmetrics.decrement(metric=METRIC_SESSIONS)
        monolithmetrics.gauge(metric=METRIC_SESSIONS_TOTAL, value=len(self.transportIDbySessionID))

    def LogClientCall(self, session, objectName, method, args):
        pass

    def PerformanceTest(self, *args):
        if 'dbdip' in args:
            self.dbzcluster.Cluster_DowntimeInfo()
            return ['dbdip', args]
        return ['server', args]

    def ForwardCharacterNotification(self, charid, method, *args):
        callTimer = basesession.CallTimer('ForwardCharacterNotification::%s (Broadcast\\Client)' % method)
        try:
            clientIDs = [ sess.clientID for sess in basesession.FindSessions('charid', [charid]) ]
            if len(clientIDs):
                self.NarrowcastByClientIDsWithoutTheStars(clientIDs, method, args)
            else:
                machoNet = self.session.ConnectToSolServerService('machoNet')
                nodeID = machoNet.GetNodeFromAddress(cluster.SERVICE_CHARACTER, charid % const.CHARNODE_MOD)
                if nodeID == self.GetNodeID():
                    self.ReliableSinglecastByCharID(charid, method, *args)
                else:
                    machoNet = self.session.ConnectToRemoteService('machoNet', nodeID)
                    machoNet.ForwardCharacterNotification(charid, method, *args)
        finally:
            callTimer.Done()

    def __str__(self):
        return '<MachoNet Service>'

    def __repr__(self):
        return str(self)

    def IsConnected(self):
        if self.GetTransport('ip:packet:server') and not self.authenticating:
            return 1
        else:
            return 0

    def DisconnectFromServer(self):
        if macho.mode != 'client':
            raise AttributeError('The DisconnectFromServer method should only be called on the client')
        if self.namedtransports.has_key('ip:packet:server'):
            self.LogInfo('Closing connection to server')
            transport = self.namedtransports['ip:packet:server']
            transport.disconnectsilently = getattr(transport, 'disconnectsilently', 1)
            transport.Close('User disconnected', 'CLIENTDISCONNECTED')

    def GetServerStatus(self, address, forceQueueCheck = False):
        if self.authenticating or self.gettingServerStatus or not forceQueueCheck and address.upper() == self.clientLogonQueue.address and blue.os.GetWallclockTime() - (self.clientLogonQueue.timestamp or blue.os.GetWallclockTime()) < self.clientLogonQueuePollTime * const.SEC:
            raise UserError('AlreadyConnecting')
        self.gettingServerStatus = 1
        try:
            transport = None
            if address in self.clientHalfBakedTransports:
                transport = self.clientHalfBakedTransports[address]
                del self.clientHalfBakedTransports[address]
                if transport.IsClosed():
                    transport = None
            if transport is None:
                factory = self.GetFactory(get_gps_map()[macho.mode]['tcp:packet:server'], (0, 'tcp:packet:server'))
                transport = factory.Connect(address)
            serverInfo = transport.Authenticate(None, None, None)
            self.clientHalfBakedTransports[address] = transport
            return (lambda since = blue.os.GetWallclockTime(): sm.GetService('machoNet').GetOKMessage(since), serverInfo)
        except GPSBadAddress as e:
            sys.exc_clear()
            return (('/Carbon/MachoNet/ServerStatus/BadAddress', {}), {})
        except GPSTransportClosed as e:
            sys.exc_clear()
            if str(e.codename) != str(boot.codename) or e.reasonCode == 'HANDSHAKE_INCOMPATIBLERELEASE':
                reason = ('/Carbon/MachoNet/ServerStatus/IncompatibleRelease', {})
            elif e.version != boot.version or e.reasonCode == 'HANDSHAKE_INCOMPATIBLEVERSION':
                reason = ('/Carbon/MachoNet/ServerStatus/IncompatibleVersion', {})
            elif e.machoVersion != macho.version or e.reasonCode == 'HANDSHAKE_INCOMPATIBLEPROTOCOL':
                reason = ('/Carbon/MachoNet/ServerStatus/IncompatibleProtocol', {})
            elif e.build != boot.build or e.reasonCode == 'HANDSHAKE_INCOMPATIBLEBUILD':
                reason = ('/Carbon/MachoNet/ServerStatus/IncompatibleBuild', {})
            elif str(e.region) != str(boot.region) or e.reasonCode == 'HANDSHAKE_INCOMPATIBLEREGION':
                reason = ('/Carbon/MachoNet/ServerStatus/IncompatibleRegion', {})
            elif e.reasonCode == 'ACL_SHUTTINGDOWN':
                reason = ('/Carbon/MachoNet/ServerStatus/ShuttingDown', {})
                when = blue.os.GetWallclockTime() + random.randrange(15, 60) * const.SEC
                reason = lambda when = when, reason = reason: (reason if blue.os.GetWallclockTime() < when else None)
            elif e.reasonCode == 'ACL_NOTACCEPTING':
                reason = ('/Carbon/MachoNet/ServerStatus/NotAcceptingConnections', {})
                when = blue.os.GetWallclockTime() + random.randrange(60, 300) * const.SEC
                reason = lambda when = when, reason = reason: (reason if blue.os.GetWallclockTime() < when else None)
            elif e.reasonCode == 'ACL_ACCEPTDELAY':
                reasonMessage = '/Carbon/MachoNet/ServerStatus/StartingUp'
                when = blue.os.GetWallclockTime() + (5 + e.reasonArgs['seconds']) * const.SEC
                reason = lambda when = when: ((reasonMessage, {'progress': when - blue.os.GetWallclockTime()}) if blue.os.GetWallclockTime() < when else None)
            elif e.reasonCode == 'ACL_PROXYFULL':
                if e.reasonArgs:
                    reason = ('/Carbon/MachoNet/ServerStatus/ProxyFullWithLimit', {'limit': e.reasonArgs['limit']})
                else:
                    reason = ('/Carbon/MachoNet/ServerStatus/ProxyFull', {})
                when = blue.os.GetWallclockTime() + random.randrange(30, 120) * const.SEC
                reason = lambda when = when, reason = reason: (reason if blue.os.GetWallclockTime() < when else None)
            elif e.reasonCode == 'ACL_PROXYNOTCONNECTED':
                reason = ('/Carbon/MachoNet/ServerStatus/ProxyNotConnected', {})
                when = blue.os.GetWallclockTime() + random.randrange(30, 120) * const.SEC
                reason = lambda when = when, reason = reason: (reason if blue.os.GetWallclockTime() < when else None)
            elif e.reasonCode == 'ACL_IPADDRESSBAN':
                reason = ('/Carbon/MachoNet/ServerStatus/IPBanned', {})
            elif e.origin == 'client':
                reason = ('/Carbon/MachoNet/ServerStatus/Unknown', {})
                when = blue.os.GetWallclockTime() + random.randrange(60, 300) * const.SEC
                reason = lambda when = when, reason = reason: (reason if blue.os.GetWallclockTime() < when else None)
            else:
                reason = lambda since = blue.os.GetWallclockTime(): sm.GetService('machoNet').GetOKMessage(since)
            if e.origin == 'client':
                return (reason, {})
            else:
                return (reason, {'boot_version': getattr(e, 'version', None),
                  'boot_build': getattr(e, 'build', None),
                  'boot_codename': str(getattr(e, 'codename', None)),
                  'boot_region': str(getattr(e, 'region', None)),
                  'cluster_usercount': getattr(e, 'loggedOnUserCount', None),
                  'macho_version': getattr(e, 'machoVersion', None)})
        finally:
            self.gettingServerStatus = 0

    def GetValidClientCodeHash(self):
        if not hasattr(self, 'clientHash'):
            self.OnClientCodeUpdated()
        return getattr(self, 'clientHash')

    def ReloadClientCodeHash(self):
        clientUpdate = self.dbzclient.CodeHashes_Select(None, GetBuildVersionAsInt())
        if len(clientUpdate) > 1:
            self.LogError("Can't have more than one valid client code update")
            return
        if len(clientUpdate) == 0:
            return
        row = clientUpdate[0]
        return KeyVal(hash=row.hash, fileurl=row.fileUrl, build=row.build)

    def OnClientCodeUpdated(self):
        hs = self.session.ConnectToRemoteService('machoNet').ReloadClientCodeHash()
        setattr(self, 'clientHash', hs)

    def GetOKMessage(self, since):
        if self.clientLogonQueue.position == 1 and self.clientLogonQueue.reportedQueued:
            return ('/Carbon/MachoNet/ServerStatus/HeadOfQueue', {})
        elif self.clientLogonQueue.position > 1:
            if not self.gettingServerStatus and blue.os.GetWallclockTime() - max(self.clientLogonQueue.timestamp or since, since) > self.clientLogonQueuePollTime * const.SEC:
                return None
            self.clientLogonQueue.reportedQueued = True
            return ('/Carbon/MachoNet/ServerStatus/InQueue', {'position': self.clientLogonQueue.position})
        else:
            return ('/Carbon/MachoNet/ServerStatus/OK', {})

    def SetLogonQueuePosition(self, position):
        self.clientLogonQueue.position = position
        self.clientLogonQueue.timestamp = blue.os.GetWallclockTime()
        if position is None:
            self.clientLogonQueue.history = None
        elif self.clientLogonQueue.history is None:
            self.clientLogonQueue.history = KeyVal(initial=KeyVal(time=blue.os.GetWallclockTime(), pos=position), prev=KeyVal(time=blue.os.GetWallclockTime(), pos=position), last=KeyVal(time=blue.os.GetWallclockTime(), pos=position))
        else:
            self.clientLogonQueue.history.prev = self.clientLogonQueue.history.last
            self.clientLogonQueue.history.last = KeyVal(time=blue.os.GetWallclockTime(), pos=position)

    def GetPortOffsetStep(self, portTypeName):
        return offsetStep[portTypeName]

    def GetGlobalConfig(self):
        if macho.mode != 'client' and self.globalConfig is None:
            with locks.TempLock('Getting the values, hold your horses', locks.RLock):
                if self.globalConfig is not None:
                    return self.globalConfig
                if macho.mode == 'proxy':
                    self.globalConfig = self.session.ConnectToSolServerService('machoNet').GetGlobalConfig()
                else:
                    self.globalConfig = {k.strip():v for k, v in self.DB2.GetSchema('zsystem').GlobalConfig_Select()}
                self.LogInfo('Got the following global config:', self.globalConfig)
                sm.ScatterEvent('OnGlobalConfigChanged', self.globalConfig)
        elif macho.mode == 'client' and self.globalConfig is None:
            return {}
        return self.globalConfig

    def InitClientGlobalConfig(self, globalConfig):
        if not monolithconfig.on_client():
            self.LogWarn('InitClientGlobalConfig called on {}'.format(monolithconfig._get_boot_role()))
            return
        self.globalConfig = globalConfig
        self.LogNotice('Got global config values:', globalConfig)
        monolithconfig.defer_global_config_updates()
        sm.ScatterEvent('OnGlobalConfigChanged', globalConfig)

    def SetGlobalConfigValue(self, key, value, isDelete = False, isUpdate = True, isUpdateClients = True):
        dbzsystem = self.DB2.GetSchema('zsystem')
        if isDelete:
            dbzsystem.GlobalConfig_Delete(key)
            self.LogNotice('Global config key deleted', key)
            value = None
        else:
            rs = dbzsystem.GlobalConfig_Select(key)
            if len(rs) == 0:
                dbzsystem.GlobalConfig_Insert(key, value)
                self.LogNotice('Global config added', key, value)
            else:
                dbzsystem.GlobalConfig_Update(key, value)
                self.LogNotice('Global config updated', key, value)
        if isUpdate:
            self.ClusterBroadcast('OnGlobalConfigUpdated', key, value)
            self.LogNotice('Global config updated cluster', key, value)
        if isUpdateClients:
            self.Broadcast('OnGlobalConfigUpdated', key, value)
            self.LogNotice('Global config updated connected clients', key, value)

    def GetGlobalConfigValue(self, key):
        if key:
            row = self.DB2.GetSchema('zsystem').GlobalConfig_Select(key)[0]
            return (row.key, row.value)
        return ('', '')

    def CalculatePortNumber(self, mapname, portTypeName):
        attributeName = 'default' + portTypeName[0].upper() + portTypeName[1:] + 'PortOffset'
        basePort = getattr(self, attributeName, None)
        if basePort:
            return basePort + offsetMap[portTypeName][mapname]
        raise StandardError('Unsupported role')

    def ConnectToAddress(self, address, mapname, destMachoRole, destinationNodeID = None, named = False, withReader = True, forcedPortNumber = None):
        port = forcedPortNumber or self.CalculatePortNumber(mapname, destMachoRole)
        address += ':' + str(port)
        factory = self.GetFactory(get_gps_map()[macho.mode][mapname], (0, mapname))
        transport = factory.Connect(address)
        transportID = self.transportID
        self.transportID = self.transportID + 1
        discard, destTypeName = mapname.split(':', 1)
        ipDestTypeName = 'ip:' + destTypeName
        transport = MachoTransport(transportID, transport, ipDestTypeName, self)
        self.transportsByID[transportID] = transport
        if named:
            self.namedtransports[ipDestTypeName] = transport
        transport._AssociateWithSession(forceNodeID=self.GetNodeID())
        blue.net.EnumerateTransport(transport.transport.socket.getSocketDescriptor(), transport.transportID, transport.transportName, 0, 0, self.GetNodeID())
        if withReader:
            self.StartTransportReader(transport)
        if destinationNodeID:
            self.transportIDbyAppNodeID[destinationNodeID] = transportID
        return transport

    def StartTransportReader(self, transport):
        transport.currentReaders += 1
        uthread.new(self.TransportReader, transport).context = 'machoNet::Transport Reader::ConnectToAddress'

    @telemetry.ZONE_METHOD
    def ConnectToServer(self, address, userName, password, sockettype = 'tcp', ssoToken = None):
        if macho.mode != 'client':
            raise AttributeError('The ConnectToServer method should only be called on the client')
        if self.authenticating:
            raise UserError('AlreadyConnecting')
        if address.upper() == self.clientLogonQueue.address and self.clientLogonQueue.position > 1:
            raise UserError('AlreadyConnecting')
        loginProgressSteps = 3
        self.authenticating = 2
        try:
            self.clientSessionID += 1
            try:
                dirty = 0
                for each in session.__persistvars__:
                    if getattr(session, each) != session.GetDefaultValueOfAttribute(each):
                        self.LogError('Connecting with a dirty session.  ', each, ' was ', getattr(session, each), ' but should have been ', session.GetDefaultValueOfAttribute(each))
                        dirty = 1

                if dirty:
                    log.LogTraceback('Connecting with a dirty session')
                    raise UserError('DirtySession')
                self.LogInfo('Connecting to server ', address)
                if self.namedtransports.has_key('ip:packet:server'):
                    transport = self.namedtransports['ip:packet:server']
                    transport.disconnectsilently = getattr(transport, 'disconnectsilently', 1)
                    transport.Close('Reconnecting')
                transport = None
                try:
                    mapname = '%s:packet:server' % sockettype
                    sm.ScatterEvent('OnProcessLoginProgress', 'loginprogress::connecting', '', 1, loginProgressSteps)
                    transport = None
                    if address in self.clientHalfBakedTransports:
                        transport = self.clientHalfBakedTransports[address]
                        del self.clientHalfBakedTransports[address]
                        if transport.IsClosed():
                            transport = None
                    if transport is None:
                        factory = self.GetFactory(get_gps_map()[macho.mode]['%s:packet:server' % sockettype], (0, mapname))
                        transport = factory.Connect(address)
                    sm.ScatterEvent('OnProcessLoginProgress', 'loginprogress::authenticating', '', 2, loginProgressSteps)
                    self.LogInfo('Authenticating user ', userName)
                    self.clientLogonQueue.address = address.upper()
                    self.clientLogonQueue.timestamp = None
                    self.clientLogonQueue.position = None
                    self.clientLogonQueue.reportedQueued = False
                    response = transport.Authenticate(userName, password, ssoToken)
                    sm.GetService('objectCaching').LoadCache(transport.address)
                    transportID = self.transportID
                    self.transportID = self.transportID + 1
                    transport = MachoTransport(transportID, transport, 'ip:packet:server', self)
                    self.transportsByID[transportID] = transport
                    self.namedtransports['ip:packet:server'] = transport
                    transport.currentReaders += 1
                    uthread.new(self.TransportReader, self.transportsByID[transportID]).context = 'machoNet::TransportReader::ConnectToServer'
                    transport.userID = response['session_init']['userid']
                    self.myProxyNodeID = response['proxy_nodeid']
                    transport._AssociateWithSession()
                    self.LogInfo('ConnectToServer established transport ', transport)
                    blue.net.EnumerateTransport(transport.transport.socket.getSocketDescriptor(), transport.transportID, transport.transportName, transport.userID, 0, self.myProxyNodeID)
                    blue.net.AddProxyNode(transport.transportID, self.myProxyNodeID)
                except UnMachoDestination as e:
                    sm.ScatterEvent('OnConnectionRefused')
                    exctype, exc, tb = sys.exc_info()
                    try:
                        raise UserError('OnConnectionRefused', {'what': e.payload}), None, tb
                    finally:
                        exctype = None
                        exc = None
                        tb = None

                except UserError as e:
                    if e.msg == 'AutLogonFailureTotalUsers':
                        if not transport.IsClosed():
                            self.clientHalfBakedTransports[address] = transport
                        self.SetLogonQueuePosition(e.dict.get('position', None))
                    sm.ScatterEvent('OnConnectionRefused')
                    if e.msg != 'AuthenticationFailure':
                        log.LogTraceback()
                    raise
                except GPSBadAddress as e:
                    sm.ScatterEvent('OnConnectionRefused')
                    exctype, exc, tb = sys.exc_info()
                    try:
                        raise UserError('OnConnectionBadAddress', {'what': e.reason}), None, tb
                    finally:
                        exctype = None
                        exc = None
                        tb = None

                except GPSTransportClosed as e:
                    exctype, exc, tb = sys.exc_info()
                    try:
                        sm.ScatterEvent('OnConnectionRefused')
                        if e.reason == 'Connected transport closed':
                            raise UserError('OnConnectionFailed', {'what': 'The server was either not running or inaccessible'}), None, tb
                        else:
                            if e.reasonCode in gpcs.MESSAGES:
                                reason = gpcs.MESSAGES[e.reasonCode]
                                reasonParameters = {'what': (const.UE_LOC, reason, e.reasonArgs)}
                                err = UserError('OnConnectionFailed', reasonParameters)
                            elif e.reasonCode not in cfg.messages:
                                reasonParameters = {'what': e.reason}
                                err = UserError('OnConnectionFailed', reasonParameters)
                            else:
                                err = UserError(e.reasonCode, e.reasonArgs)
                            if e.reason == 'AutLogonFailureTotalUsers':
                                if not transport.IsClosed():
                                    self.clientHalfBakedTransports[address] = transport
                                self.SetLogonQueuePosition(e.reasonArgs.get('position', None))
                            raise err, None, tb
                    finally:
                        exctype = None
                        exc = None
                        tb = None

                except StandardError:
                    self.LogInfo('ConnectToServer blew up big time')
                    log.LogException()
                    raise

                self.serviceInfo = self.RemoteServiceCall(session, self.myProxyNodeID, 'machoNet', 'GetServiceInfo')
                sm.ChainEvent('ProcessLoginProgressDone')
                sm.ScatterEvent('OnProcessLoginProgress', 'loginprogress::done', '', 3, loginProgressSteps, response)
            finally:
                self.authenticating = 1

            global_config = response.get('config_vals', {})
            self.InitClientGlobalConfig(global_config)
            return response
        finally:
            self.authenticating = 0

    def GetBasePortNumber(self):
        return self.basePortNumber

    def GetClusterGameStatistics(self, key, default):
        return default

    def GetClusterGameStatisticsForClient(self, key, default):
        return default

    def GetConnectionProperties(self):
        retval = {}
        if macho.mode == 'proxy':
            retval['vipMode'] = self.vipMode
            retval['limit'] = self.connectionLimit
            retval['maxLoginsPerMinute'] = self.maxLoginsPerMinute
            retval['pendingConnections'] = len(self.serverLogonQueue)
            retval['availableLoginSlots'] = self.availableLoginSlots
            retval['clients'] = len(self.transportIDbyClientID)
            retval['proxies'] = len(self.transportIDbyProxyNodeID)
            retval['servers'] = len(self.transportIDbySolNodeID)
            retval['solNodeIDs'] = self.transportIDbySolNodeID.keys()
            retval['proxyNodeIDs'] = self.transportIDbyProxyNodeID.keys()
            retval['espaddress'] = self.namedtransports['tcp:raw:http'].GetESPAddress()
            retval['externaladdress'] = self.namedtransports['tcp:packet:client'].GetExternalAddress()
            retval['internaladdress'] = self.namedtransports['tcp:packet:machoNet'].GetInternalAddress()
            retval['bannedIPs'] = self.bannedIPs
            retval['acceptDelay'] = self.acceptDelay
            retval['acceptStart'] = self.acceptStart
        elif macho.mode == 'client':
            retval['bytes_out'] = self.dataSent.Current()
            retval['bytes_in'] = self.dataReceived.Current()
            retval['packets_out'] = self.dataSent.Count()
            retval['packets_in'] = self.dataReceived.Count()
            retval['blocking_calls'] = self.blockingCallTimes.Count()
            retval['blocking_call_times'] = self.blockingCallTimes.Current()
            retval['calls_outstanding'] = len(self.calls)
        else:
            retval['limit'] = self.connectionLimit
            retval['maxLoginsPerMinute'] = self.maxLoginsPerMinute
            retval['proxiedclients'] = len(self.transportIDbyClientID)
            retval['proxies'] = len(self.transportIDbyProxyNodeID)
            retval['servers'] = len(self.transportIDbySolNodeID)
            retval['solNodeIDs'] = self.transportIDbySolNodeID.keys()
            retval['proxyNodeIDs'] = self.transportIDbyProxyNodeID.keys()
            retval['address'] = self.namedtransports['tcp:packet:machoNet'].GetExternalAddress()
            retval['internaladdress'] = self.namedtransports['tcp:packet:machoNet'].GetInternalAddress()
            retval['acceptDelay'] = self.acceptDelay
        if macho.mode != 'client':
            retval['blue.os.pid'] = blue.os.pid
            created = blue.sysinfo.processStartTime
            kernel = blue.sysinfo.GetProcessTimes().systemTime
            user = blue.sysinfo.GetProcessTimes().userTime
            cputime = kernel + user
            uptime = blue.os.GetWallclockTime() - created
            memory = blue.sysinfo.GetMemory()
            retval['blue.os.started'] = utilFormat.FmtDateEng(created)
            retval['blue.os.uptime'] = utilFormat.FmtTimeEng(uptime)
            retval['blue.os.cpuload'] = self.GetCPULoad()
            retval['blue.os.cputime'] = utilFormat.FmtTimeEng(cputime)
            retval['blue.os.kerneltime'] = utilFormat.FmtTimeEng(kernel)
            retval['blue.os.usertime'] = utilFormat.FmtTimeEng(user)
            retval['blue.os.ramReal'] = memory.totalPhysical - memory.availablePhysical
            retval['blue.w32.PagefileUsage'] = memory.pageFile
            retval['blue.os.simDilation'] = blue.os.simDilation
        return retval

    def GetAddressAndStaticTagsForPrometheus(self):
        if macho.mode == 'client':
            return {}
        if sm.IsServiceRunning('tcpRawProxyService'):
            address = self.namedtransports['tcp:raw:http'].GetESPAddress()
            external_address = self.namedtransports['tcp:packet:client'].GetExternalAddress()
            internal_address = self.namedtransports['tcp:packet:machoNet'].GetInternalAddress()
        else:
            first_proxy = min(self.GetConnectedProxyNodes())
            tcp_proxy = self.session.ConnectToRemoteService('tcpRawProxyService', first_proxy)
            host, ports = tcp_proxy.GetESPTunnelingAddressByNodeID()
            port = ports.get(self.nodeID)
            address = '%s:%s' % (host, port)
            external_address = self.namedtransports['tcp:packet:machoNet'].GetExternalAddress()
            internal_address = self.namedtransports['tcp:packet:machoNet'].GetInternalAddress()
        hostname = self.GetLocalHostName()
        info = {'node_id': self.nodeID,
         'esp_tunnel_address': address,
         'role': macho.mode,
         'hostname': hostname,
         'machine_id': self.machineID,
         'metrics_port': _prometheus.prometheus_port,
         'node_index': self.nodeIndex,
         'service_mask': self.serviceMask,
         'external_address': external_address.split(':')[0],
         'internal_address': internal_address.split(':')[0]}
        if macho.mode == 'server':
            info['cluster_group'] = self.clusterGroup
        else:
            info['cluster_group'] = 0
        return info

    def GetCPULoad(self):
        now = blue.os.GetWallclockTime()
        then = now - const.MIN * 5
        total = 0L
        lastTime = now
        i = len(blue.pyos.cpuUsage) - 1
        while i > 0 and blue.pyos.cpuUsage[i].timestamp >= then:
            total += blue.pyos.cpuUsage[i].userProcessCpuUsage
            lastTime = blue.pyos.cpuUsage[i].timestamp
            i -= 1

        if lastTime == now:
            return 0.0
        return min(100.0 * (float(total) / (float(now) - float(lastTime))), 100.0)

    def GetNetworkStats(self, socketServers):
        import _socket
        if not socketServers:
            stackless.set_schedule_callback(None)
            self.scheduleCount = 0
            return
        if self.scheduleCount == 0:

            def ScheduleCounter(prev, next):
                self.scheduleCount += 1

            stackless.set_schedule_callback(ScheduleCounter)
        stats = _socket.getstats()
        headings = stats.keys()
        line = [ stats[k] for k in headings ]

        def replace(a, b):
            headings[headings.index(a)] = b

        replace('BytesReceived', 'bytesRecvd')
        replace('BytesSent', 'bytesSent')
        replace('PacketsSent', 'countWrites')
        replace('PacketsReceived', 'countReads')
        stats = {'global socket stats': [headings, line]}
        return KeyVal(stats=stats, scheduleCount=self.scheduleCount, taskletCount=len(bluepy.tasklets))

    def GetBlockingCallStats(self):
        min = self.callsCountMin
        max = self.callsCountMax
        self.callsCountMin = self.callsCountMax = len(self.calls)
        return (min, max)

    def GetMetrics(self):
        from carbon.common.script.net.BroadcastStuffGPCS import CoreBroadcastStuff
        from carbon.common.script.net.ServiceCallGPCS import CoreServiceCall
        kv = KeyVal({'CallsReceived': {},
         'CallsSent': {},
         'NotificationsReceived': {},
         'NotificationsSent': {}})
        for functionName, receivedCount in CoreServiceCall.__recvServiceCallCount__.iteritems():
            kv.CallsReceived[functionName] = receivedCount

        for functionName, sentCount in CoreServiceCall.__sendServiceCallCount__.iteritems():
            kv.CallsSent[functionName] = sentCount

        for functionName, receivedCount in CoreBroadcastStuff.__notifyRecvCount__.iteritems():
            kv.NotificationsReceived[functionName] = receivedCount

        for functionName, sentCount in CoreServiceCall.__sendNotifyCount__.iteritems():
            kv.NotificationsSent[functionName] = sentCount

        return kv

    def SetConnectionProperty(self, k, v, doPersist = True):
        if k == 'vipMode':
            monolithmetrics.event('Eve VIP Mode Changed', 'VIP Mode set to: %s' % v)
        if k == 'limit':
            self.connectionLimit = v
        elif k in ('maxLoginsPerMinute', 'vipMode'):
            if doPersist:
                setattr(self, k, v)
            else:
                self.__dict__[k] = v
            if k == 'maxLoginsPerMinute':
                self.availableLoginSlots = min(self.availableLoginSlots, self.maxLoginsPerMinute)
        elif k == 'maxTrialUsers':
            self.maxTrialUsers = v
        elif k in ('bannedIPs', 'allowedIPs', 'useIPACL', 'acceptDelay'):
            if doPersist:
                setattr(self, k, v)
            else:
                self.__dict__[k] = v
        elif k == 'bannedIPs':
            self.bannedIPs = v
            bannz0red = []
            for clientID, transportID in self.transportIDbyClientID.items():
                if transportID not in self.transportsByID:
                    continue
                transport = self.transportsByID[transportID]
                for bannedIP in v:
                    if transport.transport.address.startswith(bannedIP):
                        bannz0red.append(transport)
                        break

            for transport in bannz0red:
                transport.Close('Your IP address has been banned', 'ACL_IPADDRESSBAN', {'address': transport.transport.address.split(':')[0]})

        elif k == 'acceptDelay':
            self.acceptDelay = v

    def CheckACL(self, address, espCheck = False):
        if not espCheck and self.shutdown is not None:
            if self.shutdown.when < blue.os.GetWallclockTime():
                self.LogInfo('Rejecting connection from ', address, " because we're shutting down")
                return ('The cluster is shutting down', 'ACL_SHUTTINGDOWN')
            if self.shutdown.when - blue.os.GetWallclockTime() < 3 * const.MIN:
                self.LogInfo('Rejecting connection from ', address, " because we're shutting down in less than 3 minutes")
                return ('The cluster is shutting down in a few moments', 'ACL_SHUTTINGDOWN', {'when': (17, self.shutdown.when)})
        if not espCheck and self.acceptDelay and blue.os.GetWallclockTime() - self.acceptStart < const.SEC * self.acceptDelay:
            self.LogInfo('Rejecting connection from ', address, " because we're still starting and our accept delay hasn't passed")
            return ('Starting up...(%d sec.)' % (self.acceptDelay - (blue.os.GetWallclockTime() - self.acceptStart) / const.SEC), 'ACL_ACCEPTDELAY', {'seconds': self.acceptDelay - (blue.os.GetWallclockTime() - self.acceptStart) / const.SEC})
        if not self.clusterStartupPhase:
            if prefs.clusterMode in ('LIVE', 'TEST'):
                self.LogWarn('Accept Delay too low, the accept delay should represent the time from startup until the first user can connect')
            self.LogInfo('Rejecting connection from ', address, " because we're still starting")
            return ('Starting up...', 'ACL_ACCEPTDELAY', {'seconds': 0})
        if not self.transportIDbySolNodeID:
            self.LogInfo('Rejecting connection from ', address, ' because we do not have a sol server connection')
            return ('Proxy not connected', 'ACL_PROXYNOTCONNECTED')
        if espCheck:
            return
        if self.connectionLimit == 0 or self.maxLoginsPerMinute == 0:
            self.LogInfo('Rejecting connection from ', address, " because we're not accepting any connections")
            return ('Not accepting', 'ACL_NOTACCEPTING')
        for each in self.bannedIPs:
            if address.startswith(each):
                self.LogInfo('Rejecting connection from ', address, ' because the IP address is banned by the ', each, ' rule')
                return ('Your IP address has been banned', 'ACL_IPADDRESSBAN', {'address': address.split(':')[0]})

    def GetSessionCounts(self, attr = None, default = None):
        if default is None:
            default = [0, {}]
        sessionMgr = sm.services.get('sessionMgr', None)
        if sessionMgr is None:
            if attr is not None:
                return default
            return {}
        else:
            stats = sessionMgr.GetSessionStatistics()
            if attr is None:
                return stats
            return stats.get(attr, default)

    def SetClusterSessionCounts(self, clusterSessionStatistics):
        now = blue.os.GetWallclockTime()
        self.clusterSessionStatsHistory.append((now, clusterSessionStatistics))
        if len(self.clusterSessionStatsHistory) > self.proxyStatSmoothie:
            self.clusterSessionStatsHistory = self.clusterSessionStatsHistory[1:]

    def GetClusterSessionCounts(self, attr = None, default = None):
        if default is None:
            default = [0, {}]
        if len(self.clusterSessionStatsHistory) == 0:
            if attr is not None:
                return default
            return {}
        else:
            stats = self.clusterSessionStatsHistory[-1][1]
            if attr is None:
                return stats
            return stats.get(attr, default)

    def __SessionStatWatcher(self):
        allProxies = None
        while not getattr(self, 'stop', True):
            blue.pyos.synchro.SleepWallclock(1000 * self.proxyStatPollInterval)
            if self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0) == self.GetNodeID():
                self.LogInfo('SessionStatWatcher collecting session statistics from all proxies')
                try:
                    if allProxies is None:
                        allProxies = self.session.ConnectToAllProxyServerServices('machoNet')
                    self.__SessionStatWatcher2(allProxies)
                except StandardError:
                    self.LogError('Exception during session stat stuff')
                    log.LogException()
                    sys.exc_clear()

    def __SessionStatWatcher2(self, allProxies):
        if self.transportIDbyProxyNodeID:
            allStats = allProxies.GetSessionCounts()
            summ = {}
            for isError, nodeID, stats in allStats:
                if not isError:
                    for attribute, countsTuple in stats.iteritems():
                        if attribute not in summ:
                            summ[attribute] = [0, {}]
                        valueCounts = countsTuple[1]
                        for attrValue, count in valueCounts.iteritems():
                            summ[attribute][0] += count
                            if attrValue not in summ[attribute][1]:
                                summ[attribute][1][attrValue] = count
                            else:
                                summ[attribute][1][attrValue] += count

                else:
                    log.LogTraceback('Exception during proxy stat poll for proxy %s' % str(nodeID))
                    sys.exc_clear()
                    return

            self.clusterSessionStatistics = summ
            self._StoreMetricsToDB(self.clusterSessionStatistics)
            allProxies.SetClusterSessionCounts(self.clusterSessionStatistics)

    def GetNumberOfEVEUsersConnected(self):
        return self.clusterSessionStatistics.get('EVE:Online', [None, None])[0]

    def _StoreMetricsToDB(self, metrics):
        try:
            for virtualAttr, zmetric in self.metricsMap.iteritems():
                count = metrics[virtualAttr][0] if virtualAttr in metrics else 0
                if count > 0:
                    try:
                        self.dbzmetric.SimpleCounters_Insert(zmetric, count)
                    except StandardError:
                        log.LogException('Error writing metric %s (%s) to zmetric.simpleCounters' % (zmetric, virtualAttr))
                        sys.exc_clear()

        except StandardError:
            log.LogException()
        except:
            log.LogException()
            raise

    def _GetLayTracksTo(self):
        with self.paonLock:
            if self.paon is None or blue.os.GetWallclockTime() - self.paon[1] > 5 * const.SEC:
                self.LogInfo('Connectivity[PAON]: Fetching node/proxy info')
                rowDescriptor = blue.DBRowDescriptor((('nodeID', const.DBTYPE_I4), ('ipAddress', const.DBTYPE_STR), ('port', const.DBTYPE_I4)))
                layTracksTo = crowset.CRowset(rowDescriptor, [])
                proxies = self.dbzcluster.Proxies_Select()
                if not proxies and macho.mode == 'server':
                    ip = self.namedtransports['tcp:packet:machoNet'].GetExternalAddress().split(':')[0]
                    clientport = self.defaultProxyPortOffset + offsetMap[macho.mode]['tcp:packet:client']
                    serverport = self.defaultProxyPortOffset + offsetMap[macho.mode]['tcp:packet:machoNet']
                    proxyNodeID = self.GetIDOfAddress(ip + ':%d' % clientport, clientMode=False)
                    layTracksTo.InsertNew([proxyNodeID, ip, serverport])
                    self.LogWarn('Connectivity[PAON]:  Warning:  No proxy servers registered in DB, defaulting to localhost')
                for proxy in proxies:
                    if proxy.enabled == 1:
                        for i in xrange(proxy.nodeCount):
                            proxyIpAddress = GetPreferredHostByName(proxy.ipAddress)
                            clientport = self.defaultProxyPortOffset + offsetMap[macho.mode]['tcp:packet:client'] + 1000 * i
                            serverport = self.defaultProxyPortOffset + offsetMap[macho.mode]['tcp:packet:machoNet'] + 1000 * i
                            proxyNodeID = self.GetIDOfAddress('%s:%d' % (proxyIpAddress, clientport), clientMode=False)
                            if self.GetNodeID() != proxyNodeID:
                                self.LogInfo('Connectivity[PAON]: Laying tracks to self=', self.GetNodeID(), ' proxy=', proxyNodeID)
                                layTracksTo.InsertNew([proxyNodeID, proxyIpAddress, serverport])

                for sol in self.dbzcluster.Nodes_SelectOthers2(self.nodeID):
                    port = self.defaultServerPortOffset + offsetStep[macho.mode] * sol.nodeIndex
                    port += offsetMap[macho.mode]['tcp:packet:machoNet']
                    self.LogInfo('Connectivity[PAON]: Laying tracks to self=', self.GetNodeID(), ' sol=', sol.nodeID, ' at:', sol.machineName, ':', port)
                    layTracksTo.InsertNew([sol.nodeID, sol.machineName, port])

                self.paon = (layTracksTo, blue.os.GetWallclockTime())
            else:
                self.LogInfo('Connectivity[PAON]: Node/proxy info is up to date')
        self.LogInfo('Connectivity[PAON]: returning ', len(self.paon[0]), ' proxies and servers')
        return self.paon[0]

    def OnRefreshConnectivity(self):
        self.RefreshConnectivity()

    def RefreshConnectivity(self):
        if macho.mode == 'server':
            self.LogInfo('Connectivity[RefreshConnectivity]:  Refreshing communications with proxy servers')
            layTracksTo = self._GetLayTracksTo()
            if not layTracksTo:
                addresses = [('127.0.0.1:%d' % (self.defaultProxyPortOffset + offsetMap['proxy']['tcp:packet:machoNet']), None)]
            else:
                addresses = []
                for each in layTracksTo:
                    addresses.append(('%s:%d' % (each.ipAddress, each.port), each.nodeID))

            current = []
            for each in self.transportsByID.itervalues():
                current.append(each)

            for node, addr in self.LayingTracksTo():
                self.LogInfo('Connectivity[RefreshConnectivity]:  Already laying tracks to node ', node, ' at ', addr)

            random.shuffle(addresses)
            for address, nodeID in addresses:
                self.LayTracksIfNeeded(address, nodeID, 'RefreshConnectivity')

            self.LogInfo('Connectivity[RefreshConnectivity]:  End')
            return len(layTracksTo)

    def GracefulShutdown(self, userID, when, duration, explanationLabel):
        if when:
            self.LogNotice('Graceful Shutdown requested by ', userID, ' to occur at ', utilFormat.FmtDateEng(when), ', duration ', duration or 0, ' minutes, explanation: ', explanationLabel)
            if when < blue.os.GetWallclockTime() + const.HOUR:
                notify = blue.os.GetWallclockTime()
            else:
                notify = when - const.HOUR
            self.shutdown = KeyVal(notify=notify, userID=userID, when=when, duration=duration, explanationLabel=explanationLabel)
        else:
            self.LogNotice('Graceful Shutdown cancelled by ', userID, ', explanation: ', explanationLabel)
            self.shutdown = None
            if self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0) == self.GetNodeID():
                self.Broadcast('OnClusterShutdownCancelled', explanationLabel)
                sm.ScatterEvent('OnClusterShutdownCancelled', explanationLabel)
                self.dbzcluster.Broadcasts_Insert(userID, 'LOCALIZED:' + explanationLabel)

    def __GracefulShutdownWorker(self):
        pollingInterval = 10
        while not getattr(self, 'stop', True):
            try:
                if self.shutdown is not None and self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0) == self.GetNodeID():
                    self.LogInfo('GracefulShutdownWorker:  Probing')
                    now = blue.os.GetWallclockTime()
                    if self.shutdown.notify is not None:
                        self.__BroadcastShutdownInformation(now, pollingInterval)
                    elif self.shutdown.when < now:
                        self.__PerformGracefulShutdown()
            except Exception:
                log.LogException('Exception in shutdown worker')
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(pollingInterval * 1000)

    def __BroadcastShutdownInformation(self, now, pollingInterval):
        self.LogInfo('GracefulShutdownWorker:  Checking Notification, now=', now, ', notify=', self.shutdown.notify)
        sortOfNow = now + pollingInterval * 2 * const.SEC
        if sortOfNow <= self.shutdown.notify:
            return
        self.LogInfo('GracefulShutdownWorker:  Sending Notification')
        if self.shutdown.when - sortOfNow > 15 * const.MIN:
            self.LogInfo('GracefulShutdownWorker:  Prepping 15 minute Notification')
            self.shutdown.notify = self.shutdown.when - 15 * const.MIN
        elif self.shutdown.when - sortOfNow > 5 * const.MIN:
            self.LogInfo('GracefulShutdownWorker:  Prepping 5 minute Notification')
            self.shutdown.notify = self.shutdown.when - 5 * const.MIN
        else:
            self.LogInfo('GracefulShutdownWorker:  Prepping actual shutdown')
            self.shutdown.notify = None
        args = (self.shutdown.explanationLabel, self.shutdown.when, self.shutdown.duration)
        self.Broadcast('OnClusterShutdownInitiated', *args)
        sm.ScatterEvent('OnClusterShutdownInitiated', *args)
        self.dbzcluster.Broadcasts_Insert(self.shutdown.userID, self.shutdown.explanationLabel)

    def __PerformGracefulShutdown(self):
        self.LogNotice('GracefulShutdownWorker:  Shutdown Initiated')
        eventID = None
        nodeCount = proxyCount = -1
        exceptionCount = 0
        try:
            counterDate = self.DB2.SaveMetricsDate()
            if counterDate:
                eventID = self.dbLog.LogProcessClusterShutdownStarted('machoNet')
                dbzmetric = self.DB2.GetSchema('zmetric')
                alles = self.session.ConnectToAllSolServerServices('machoNet').GetMetrics()
                nodeCount = len(alles)
                summaryReceived = {}
                summarySent = {}
                for isException, nodeID, kv in alles:
                    blue.pyos.BeNice()
                    if isException:
                        exceptionCount += 1
                        continue
                    for functionName, receivedCount in kv.CallsReceived.iteritems():
                        if receivedCount > 0:
                            if functionName in summaryReceived:
                                summaryReceived[functionName] += receivedCount
                            else:
                                summaryReceived[functionName] = receivedCount

                    for functionName, receivedCount in kv.NotificationsReceived.iteritems():
                        if receivedCount > 0:
                            if functionName in summaryReceived:
                                summaryReceived[functionName] += receivedCount
                            else:
                                summaryReceived[functionName] = receivedCount

                    for functionName, sentCount in kv.CallsSent.iteritems():
                        if sentCount > 0:
                            if functionName in summarySent:
                                summarySent[functionName] += sentCount
                            else:
                                summarySent[functionName] = sentCount

                    for functionName, sentCount in kv.NotificationsSent.iteritems():
                        if sentCount > 0:
                            if functionName in summarySent:
                                summarySent[functionName] += sentCount
                            else:
                                summarySent[functionName] = sentCount

                for functionName, receivedCount in summaryReceived.iteritems():
                    dbzmetric.KeyCounters_UpdateMulti(30021, 'D', counterDate, 2000000004, None, unicode(functionName), receivedCount)

                for functionName, sentCount in summarySent.iteritems():
                    dbzmetric.KeyCounters_UpdateMulti(30022, 'D', counterDate, 2000000004, None, unicode(functionName), sentCount)

                alles = self.session.ConnectToAllProxyServerServices('machoNet').GetMetrics()
                proxyCount = len(alles)
                summaryReceived = {}
                summarySent = {}
                for isException, nodeID, kv in alles:
                    blue.pyos.BeNice()
                    if isException:
                        exceptionCount += 1
                        continue
                    for functionName, receivedCount in kv.CallsReceived.iteritems():
                        if receivedCount > 0:
                            if functionName in summaryReceived:
                                summaryReceived[functionName] += receivedCount
                            else:
                                summaryReceived[functionName] = receivedCount

                    for functionName, receivedCount in kv.NotificationsReceived.iteritems():
                        if receivedCount > 0:
                            if functionName in summaryReceived:
                                summaryReceived[functionName] += receivedCount
                            else:
                                summaryReceived[functionName] = receivedCount

                    for functionName, sentCount in kv.CallsSent.iteritems():
                        if sentCount > 0:
                            if functionName in summarySent:
                                summarySent[functionName] += sentCount
                            else:
                                summarySent[functionName] = sentCount

                    for functionName, sentCount in kv.NotificationsSent.iteritems():
                        if sentCount > 0:
                            if functionName in summarySent:
                                summarySent[functionName] += sentCount
                            else:
                                summarySent[functionName] = sentCount

                for functionName, receivedCount in summaryReceived.iteritems():
                    dbzmetric.KeyCounters_UpdateMulti(30023, 'D', counterDate, 2000000004, None, unicode(functionName), receivedCount)

                for functionName, sentCount in summarySent.iteritems():
                    dbzmetric.KeyCounters_UpdateMulti(30024, 'D', counterDate, 2000000004, None, unicode(functionName), sentCount)

        except Exception:
            log.LogException('Exception in shutdown worker - Metrics phase')
            sys.exc_clear()

        if eventID:
            self.dbLog.LogProcessClusterShutdownCompleted(eventID, int_1=nodeCount, int_2=proxyCount, int_3=exceptionCount)
        log.Quit = None
        self.LogNotice('Metrics phase completed. Notifying all nodes of immediate shutdown')
        eventID = self.dbLog.LogProcessClusterShutdownStarted('gracefulClusterShutdown')
        if self.message_bus is None:
            from carbon.common.script.net.messagebus.machoNetMessenger import MachoNetMessenger
            self.message_bus = MachoNetMessenger(sm.GetService('externalQueueMgr'))
        self.message_bus.shutdown_requested()
        try:
            self.session.ConnectToAllServices('machoNet').GracefulShutdownStarted()
        except StandardError:
            log.LogException('Exception in shutdown worker - GracefulShutdownStarted phase')
            sys.exc_clear()

        self.LogNotice('Terminating connected clients')
        massLogoutEvent = None
        try:
            self.session.ConnectToAllProxyServerServices('machoNet').TerminateAllClients('The cluster is shutting down')
            massLogoutEvent = uthread2.Event()
            sm.ChainEvent('ProcessClientTerminatedBecauseOfShutDown', massLogoutEvent)
        except Exception:
            log.LogException('Exception in shutdown worker - client disconnection phase')
            sys.exc_clear()

        self.LogNotice('Calling ProcessClusterShutdown')
        try:
            sm.ChainEvent('ProcessClusterShutdown')
        except Exception:
            log.LogException('Exception in shutdown worker - ChainEvent ProcessClusterShutdown phase')
            sys.exc_clear()

        self.LogNotice('Calling GracefulShutdownComplete')
        try:
            self.session.ConnectToAllServices('machoNet').GracefulShutdownComplete(self.GetNodeID())
        except Exception:
            log.LogException('Exception in shutdown worker - GracefulShutdownComplete phase')
            sys.exc_clear()

        self.LogNotice('Polaris node Completing GracefulShutdown')
        self.dbLog.LogProcessClusterShutdownCompleted(eventID)
        if massLogoutEvent is not None:
            startTime = blue.os.GetWallclockTimeNow()
            massLogoutEvent.wait(10.0)
            self.LogNotice('Waited', (blue.os.GetWallclockTimeNow() - startTime) / const.MSEC, 'milliseconds for mass logout event')
        self.GracefulShutdownComplete(None)

    def IsClusterShuttingDown(self):
        return self.shutdownInProgress

    def GracefulShutdownStarted(self):
        self.shutdownInProgress = True
        self.LogNotice('Cluster GracefulShutdownStarted on node', self.nodeID, ' - Disabling ObjectKillah')
        try:
            basesession.objectKillaThread.kill()
        except StandardError:
            self.LogException()

        if macho.mode == 'proxy':
            self.LogNotice('GracefulShutdownStarted on node', self.nodeID, ' - Setting VIP mode')
            self.SetConnectionProperty('vipMode', True, doPersist=False)
        sm.ChainEvent('ProcessGracefulShutdownStarted')
        self.LogNotice('GracefulShutdownStarted done on node %s' % self.nodeID)

    def GracefulShutdownComplete(self, callerNodeID):
        if callerNodeID == self.nodeID and macho.mode == 'server':
            return
        sm.ChainEvent('ProcessGracefulShutdownComplete')
        nodeString = 'Master' if callerNodeID is None else 'Slave'
        self.LogNotice('GracefulShutdownComplete running on %s %s node %s; called from %s' % (nodeString,
         macho.mode,
         self.nodeID,
         callerNodeID))
        if macho.mode == 'server':
            try:
                self.LogNotice('GracefulShutdownComplete (%s node %s) - Trashing node... ' % (nodeString, self.nodeID))
                self.dbzcluster.Nodes_Trash(self.nodeID, 'Graceful Cluster Shutdown - %s' % nodeString, 1)
            except StandardError:
                self.LogException('Exception while trashing %s node %s' % (nodeString, self.nodeID))

        self.LogNotice('Threading out Terminate in GracefulShutdownComplete (%s) stackless.runcount = %s' % (self.nodeID, stackless.getruncount()))
        uthread.worker('Shutdown thread', bluepy.Terminate, 0, 'Graceful Cluster Shutdown (%s - %s)' % (self.nodeID, nodeString))

    def Shutdown(self, who):
        self.LogError('Shutdown requested by ', who, '.  Shutting down.')
        if macho.mode == 'server':
            self.dbzcluster.Nodes_Trash(self.nodeID, 'Shutdown called by %s' % who, 1)
        bluepy.Terminate(0, 'Shutdown called by %s' % who)

    def TerminateUnconnectedNodes(self):
        if macho.mode == 'proxy':
            for each in self.nodeCPULoadValue.iterkeys():
                if each not in self.transportIDbySolNodeID:
                    self.LogNotice('Terminating unconnected node', each)
                    uthread.worker('machoNet::ServerBroadcast::OnNodeDeath', self.ServerBroadcast, 'OnNodeDeath', each, 1, "It's Terminate Unconnected Nodes' fault")

    def TerminateClient(self, reason, clientID):
        if macho.mode != 'proxy':
            return
        transportID = self.transportIDbyClientID.get(clientID, None)
        if transportID is not None:
            transport = self.transportsByID.get(transportID, None)
            if transport is not None:
                self.LogInfo('Closing transport', transportID, transport)
                transport.Close(reason)

    def TerminateAllClients(self, reason):
        if macho.mode != 'proxy':
            return
        while self.transportIDbyClientID:
            for clientID in self.transportIDbyClientID.keys():
                transport = self.transportsByID.get(self.transportIDbyClientID[clientID], None)
                if transport.transportName == 'tcp:packet:client':
                    monolithdisconnectlogger.log_server_shutdown_disconnect(transport.transport.address)
                self.TerminateClient(reason, clientID)

            monolithmetrics.flush()

        self.LogNotice('All clients terminated on', macho.mode, 'node', self.nodeID)

    def __NodeWatcher(self):
        connectionCount = -1
        while not self.IsClusterShuttingDown() and not self.stop:
            self.LogInfo('NodeWatcher:  Probing')
            try:
                if len(self.transportIDbyProxyNodeID) + len(self.transportIDbySolNodeID) != connectionCount or macho.mode == 'server' and not len(self.transportIDbyProxyNodeID) or macho.mode == 'proxy' and not len(self.transportIDbySolNodeID):
                    self.LogWarn("I think I've got a connectivity problem.  Attempting autorefresh.")
                    connectionCount = self.RefreshConnectivity()
                self.LogInfo('NodeWatcher: Sleeping for ', self.nodeRefreshInterval, ' seconds')
            except Exception:
                log.LogException('Exception during NodeWatcher')
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(1000 * self.nodeRefreshInterval)

        if self.stop:
            self.LogNotice('NodeWatcher: Shutting down due to node shutdown')
        else:
            self.LogNotice('NodeWatcher: Shutting down due to cluster shutdown')

    def __LoginQueueUpdater(self):
        while not getattr(self, 'stop', True):
            self.availableLoginSlots = min(len(self.serverLogonQueue), self.availableLoginSlots)
            maxConnections = max(0, self.connectionLimit - len(self.transportIDbyClientID))
            self.availableLoginSlots = min(self.availableLoginSlots + self.maxLoginsPerMinute, maxConnections)
            if len(self.serverLogonQueue) > self.availableLoginSlots:
                self.LogWarn('Some clients are waiting in a login queue. Clients at login screen:', len(self.serverLogonQueue), 'Available slots:', self.availableLoginSlots)
            blue.pyos.synchro.SleepWallclock(const.MIN / const.MSEC)

    def __ClientSessionMaxTimePoll(self):
        while not getattr(self, 'stop', True):
            self.LogInfo('ClientSessionMaxTimePoll: Sleeping for ', self.clientSessionTimeoutGranularity, ' seconds')
            blue.pyos.synchro.SleepWallclock(1000 * self.clientSessionTimeoutGranularity)
            try:
                for transportID in self.transportIDbyClientID.values():
                    if transportID in self.transportsByID:
                        transport = self.transportsByID[transportID]
                        clientID = transport.clientID
                        if clientID in transport.sessions:
                            s = transport.sessions[clientID]
                            if s.maxSessionTime and s.maxSessionTime < blue.os.GetWallclockTime():
                                transport.Close('Game Time Expired', 'GAMETIMEEXPIRED')

            except Exception:
                log.LogException('Exception during __ClientSessionMaxTimePoll')
                sys.exc_clear()

    def __NodeLoadPush(self):
        while not getattr(self, 'stop', True):
            try:
                blue.pyos.synchro.SleepWallclock(1000 * self.nodeLoadPush)
                if macho.mode == 'server' and self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0) == self.GetNodeID():
                    cluGetNodes = self.dbzcluster.Nodes_Select2()
                    self.nodeCPULoadValue = {}
                    for r in cluGetNodes:
                        self.nodeCPULoadValue[r.nodeID] = r.currentCpu or 0.0
                        self.serverNames[r.nodeID] = r.machineName or None

                    self.ClusterBroadcast('OnNodeLoadPush', self.nodeCPULoadValue, self.serverNames)
            except UnMachoDestination as e:
                self.LogWarn('UnMachoDestination (', e, ') while attempting to acquire load stats')
                sys.exc_clear()
            except StandardError:
                self.LogError('Exception while attempting to acquire load stats')
                log.LogException()
                sys.exc_clear()

    def __DisconnectUnauthorizedUsers(self):
        while not getattr(self, 'stop', True):
            try:
                blue.pyos.synchro.SleepWallclock(1000 * self.disconnectUnauthorizedUsersPollInterval)
                if self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0) == self.GetNodeID():
                    peopleWhoShouldntBeLoggedIn = self.dbzcluster.Sessions_SelectInactive()
                    if peopleWhoShouldntBeLoggedIn:
                        self.ProxyBroadcast('OnPeopleWhoShouldntBeLoggedInNotification', peopleWhoShouldntBeLoggedIn)
            except StandardError:
                self.LogError('Exception while attempting to disconnect unauthorized users')
                log.LogException()
                sys.exc_clear()

    def DisconnectUsers(self, userIDs):
        clientIDs = [ s.clientID for s in basesession.FindSessions('userid', userIDs) ]
        for cid in clientIDs:
            if cid in self.transportIDbyClientID:
                tid = self.transportIDbyClientID[cid]
                t = self.transportsByID[tid]
                t.Close('Client disconnected', 'CLIENTDISCONNECTED')

    def OnPeopleWhoShouldntBeLoggedInNotification(self, peopleWhoShouldntBeLoggedIn):
        lastPeopleWhoShouldntBeLoggedIn = self.peopleWhoShouldntBeLoggedIn
        self.peopleWhoShouldntBeLoggedIn = {}
        for sessionID, status in peopleWhoShouldntBeLoggedIn:
            if sessionID not in self.transportIDbySessionID:
                continue
            transportID = self.transportIDbySessionID.get(sessionID, None)
            if transportID is not None:
                transport = self.transportsByID[transportID]
                if status in (5, 12, 13):
                    uthread.worker('machoNet::DelayedClose', self.__DelayedClose, transport, 'ACCOUNTBANNED')
            elif sessionID in lastPeopleWhoShouldntBeLoggedIn:
                self.LogOffSession(sessionID)
            else:
                self.peopleWhoShouldntBeLoggedIn[sessionID] = True

    def __DelayedClose(self, transport, message):
        clientID = transport.clientID
        if message == 'ACCOUNTBANNED':
            self.SinglecastByClientID(clientID, 'OnServerMessage', ('/Carbon/MachoNet/DelayedCloseNotification/AccountBanned', {}))
        blue.pyos.synchro.SleepWallclock(self.disconnectUnauthorizedUsersDelayInterval * 1000)
        transport.Close(message, message)

    def OnNodeLoadPush(self, nodeCPULoadValue, serverNames):
        self.nodeCPULoadValue = nodeCPULoadValue
        self.serverNames = serverNames

    def GetLocalHostName(self):
        if macho.mode == 'client':
            return None
        return blue.pyos.GetEnv().get('COMPUTERNAME', 'UNKNOWNHOST')

    class Sequencer(uthread.TaskletSequencer):

        def __init__(self, machoNet):
            uthread.TaskletSequencer.__init__(self)
            self.machoNet = machoNet

        def OnSleep(self, sequence):
            self.machoNet.LogInfo('Sequencer: Going to sleep, I am %d, expected %d, queue:%r' % (sequence, self.expected, self.queue))

        def OnWakeUp(self, sequence):
            self.machoNet.LogInfo('Sequencer: Waking up, I am %d, expected %d, queue:%r' % (sequence, self.expected, self.queue))

        def OnWakingUp(self, sequence, target):
            self.machoNet.LogInfo('Sequencer: Waking dude up, I am %d, dude %d, queue:%r' % (sequence, target, self.queue))

    def WaitForSequenceNumber(self, address, seq):
        if not seq or macho.mode != 'client':
            return
        if address.addressType == const.ADDRESS_TYPE_NODE and address.nodeID:
            try:
                sequencer = self.seqwait[address.nodeID]
            except KeyError:
                sequencer = self.Sequencer(self)
                self.seqwait[address.nodeID] = sequencer

            if sequencer.IsClosed():
                self.LogError('Sequence Tasklet is closed in WaitForSequenceNumber')
            sequencer.Pass(seq)
        else:
            self.LogWarn('Unexpected source address type in wait for sequence number, address=', address)

    def OnNodeDeath(self, nodeID, confirmed, reason = None):
        self.LogNotice('machoNet::OnNodeDeath(', ','.join([str(nodeID), str(confirmed), str(reason)]), ') running on node', self.nodeID)
        if self._addressCache.IsDeadNode(nodeID):
            self.LogNotice('OnNodeDeath - Already handled the death of', nodeID)
            return
        if not self._addressCache.IsKnownNode(nodeID):
            self.LogNotice('machoNet::OnNodeDeath: Node', nodeID, 'is totally alien to this node...')
            return
        if not confirmed:
            return
        self._addressCache.MarkDeadNode(nodeID)
        if macho.mode == 'server':
            if self.nodeID == int(nodeID):
                self.dbzcluster.Nodes_Trash(self.nodeID, 'Some (proxy) sent me an OnNodeDeath for my own nodeID', 1)
                log.Quit('Some (proxy) sent me an OnNodeDeath for my own nodeID')
            else:
                self.dbzcluster.Nodes_Trash(int(nodeID), 'Killed by node %s, because: %s' % (self.nodeID, reason))
        transport = self.GetTransportOfNode(nodeID)
        if transport is not None:
            transport.Close(reason=reason, noSend=True)

    def LayTracksIfNeeded(self, address, nodeID, whencemsg):
        if self.DontLayTracksTo(nodeID):
            return
        self.LogInfo('Connectivity[%s]:  ' % whencemsg, self.nodeID, ' laying tracks to ', nodeID, ' at ', address)
        uthread.worker('machoNet::LayTracksIfNeeded', self.LayTracks, address, nodeID, whencemsg)

    def DontLayTracksTo(self, nodeID):
        if nodeID == self.nodeID:
            return True
        if nodeID in self.transportIDbySolNodeID or nodeID in self.transportIDbyProxyNodeID:
            return True
        if nodeID in self.dontLayTracksTo:
            return True
        return False

    def LayingTracksTo(self):
        return self.dontLayTracksTo.items()

    def LayTracks(self, address, nodeID, whence):
        if self.DontLayTracksTo(nodeID):
            return
        logname = 'Connectivity[LayTracks tid = %s, %s]:' % (id(stackless.getcurrent()), whence)
        self.LogInfo(logname, 'start', repr(address), 'nodeID=', nodeID)
        self.dontLayTracksTo[nodeID] = address
        try:
            if nodeID == self.GetNodeID():
                self.LogError(logname, 'Trying to lay tracks to self!')
                log.LogTraceback()
                return
            if self.nodeID is None:
                self.LogError(logname, 'Cannot lay tracks before we have a node ID. Sleeping...')
                while self.nodeID is None:
                    blue.pyos.synchro.SleepWallclock(100)

                self.LogInfo(logname, 'Woke up, have nodeID', self.nodeID)
            if False:
                nodeType = self.GetNodeTypeFromID(nodeID)
                if nodeType == macho.mode and nodeID <= self.nodeID:
                    self.LogInfo(logname, 'Not laying tracks to a higher ranking node (%d to %d), expecting incoming connection.' % (self.nodeID, nodeID))
                    return
                if nodeType == 'server' and macho.mode == 'proxy':
                    self.LogInfo(logname, 'Not laying tracks from proxy to server, expecting incoming connection.')
                    return
            try:
                factory = self.GetFactory(get_gps_map()[macho.mode]['tcp:packet:machoNet'], (0, 'tcp:packet:machoNet'))
                self.LogInfo(logname, 'Attempting connect to ', repr(address))
                transport = factory.Connect(address)
                self.LogInfo(logname, 'Connect succeeded! [%r->%r]' % (transport.localaddress, transport.address))
                try:
                    transportID = self.transportID
                    self.transportID = self.transportID + 1
                    transport = MachoTransport(transportID, transport, 'tcp:packet:machoNet', self)
                    others = []
                    if macho.mode == 'server':
                        layTracksTo = self._GetLayTracksTo()
                        for each in layTracksTo:
                            others.append(('%s:%d' % (each.ipAddress, each.port), each.nodeID))

                        myaddress = self.GetTransport('tcp:packet:machoNet').GetExternalAddress()
                    else:
                        myaddress = self.GetTransport('tcp:packet:machoNet').GetInternalAddress()
                    self.LogInfo(logname, 'sending idrq to node', nodeID, 'at', address)
                    transport.Write(IdentificationReq(nodeID=self.nodeID, source=MachoAddress(nodeID=self.nodeID), myaddress=myaddress, others=others, isProxy=macho.mode == 'proxy', isApp=False, serviceMask=self.serviceMask))
                    response = transport.Read()
                    self.LogInfo(logname, 'got response to idrq from', nodeID, 'at', address)
                    if response.command != cluster.MACHONETMSG_TYPE_IDENTIFICATION_RSP:
                        raise RuntimeError('UnexpectedResponse', 'Got a bad response to IdentificationReq')
                    if nodeID and response.nodeID != nodeID:
                        self.LogError(logname, 'I thought I was connecting to ', nodeID, ', but got a response from ', response.nodeID)
                        log.LogTraceback('Got a misguided response to IdentificationReq (expected: %s, actual: %s)' % (nodeID, response.nodeID))
                        raise RuntimeError('UnexpectedResponse', 'Got a misguided response to IdentificationReq')
                    accepted, reason = response.accepted
                    if not accepted:
                        self.LogInfo(logname, response.nodeID, ' rejected connection: ', repr(reason))
                        transport.Close('%s rejected connection: %r.' % (response.nodeID, reason), noSend=True)
                    elif response.nodeID in self.transportIDbyProxyNodeID or response.nodeID in self.transportIDbySolNodeID:
                        self.LogError(logname, "I've already got a connection established to ", response.nodeID, ".  Two's a crowd in this case.  Ciao.")
                        transport.Close("I've already got a connection established to %s." % response.nodeID)
                    else:
                        self.LogInfo(logname, 'Succesfully established a connection to ', response.nodeID, ' reason: ', repr(reason))
                        transport.nodeID = response.nodeID
                        blue.net.EnumerateTransport(transport.transport.socket.getSocketDescriptor(), transport.transportID, transport.transportName, 0, 0, transport.nodeID)
                        if response.isProxy:
                            self.transportIDbyProxyNodeID[transport.nodeID] = transportID
                            blue.net.AddProxyNode(transportID, transport.nodeID)
                        else:
                            self.transportIDbySolNodeID[transport.nodeID] = transportID
                        self.transportsByID[transportID] = transport
                        transport.currentReaders += 1
                        uthread.worker('machoNet::TransportReader::LayTracks', self.TransportReader, self.transportsByID[transportID])
                        self.externalAddressesByNodeID[response.nodeID] = (address, response.serviceMask)
                        if self.clusterStartupPhase:
                            if macho.mode == 'proxy':
                                polarisID = self.session.ConnectToSolServerService('machoNet').GetNodeFromAddress(cluster.SERVICE_POLARIS, 0)
                            else:
                                polarisID = self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0)
                            isPolaris = response.nodeID == polarisID
                            sm.ScatterEvent('OnNewNode', response.nodeID, address, response.isProxy, isPolaris, response.serviceMask)
                    others = response.others
                    for otherAddress, otherNodeID in others:
                        self.LayTracksIfNeeded(otherAddress, otherNodeID, 'LayTracks::response.others')

                except GPSTransportClosed as e:
                    transport.Close(e.reason)
                    raise
                except Exception:
                    log.LogException()
                    transport.Close('LayTracks blew up')

            except GPSTransportClosed as e:
                ps = 'proxy' if macho.mode != 'proxy' else 'server'
                self.LogWarn(logname, 'Failed to connect to ', ps, ' on ', address, repr(e))
            except Exception:
                log.LogException()

        finally:
            del self.dontLayTracksTo[nodeID]
            self.LogInfo(logname, 'End')

    def RegisterXmlRpc(self):

        def GracefulShutdownWrapper(whenMinutes, duration, explaination):
            userID = 0
            when = whenMinutes * const.MIN + blue.os.GetWallclockTime()
            self.session.ConnectToAllSolServerServices('machoNet').GracefulShutdown(userID, when, duration, explaination)
            return True

        sm.services['xmlrpcService'].Register(ROLE_ADMIN, GracefulShutdownWrapper, 'machoNet', 'GracefulShutdown')

        def IsReady():
            return self.clusterStartupPhase

        sm.services['xmlrpcService'].Register(ROLE_ANY, IsReady, 'machoNet')

        def SetVIPMode(onoff):
            s = self.session.ConnectToAllProxyServerServices('machoNet')
            s.SetConnectionProperty('vipMode', onoff)
            return self.vipMode

        sm.services['xmlrpcService'].Register(ROLE_ADMIN, SetVIPMode, 'machoNet')

        def SetProxyConnectionLimit(limit):
            s = self.session.ConnectToAllProxyServerServices('machoNet')
            s.SetConnectionProperty('limit', limit)
            return self.connectionLimit

        sm.services['xmlrpcService'].Register(ROLE_ADMIN, SetProxyConnectionLimit, 'machoNet')

    def _MapServiceNameToServiceID(self, serviceName):
        if serviceName in self.serviceMappings:
            serviceID = self.serviceMappings[serviceName][0]
            return serviceID
        return serviceName

    def SetNodeOfAddress(self, service, address, nodeID):
        if nodeID is None:
            self._addressCache.RemoveServiceAddress(service, address)
        else:
            self._addressCache.SetServiceAddress(service, address, nodeID)

    def CheckAddressCache(self, service, address, lazyGetIfNotFound = False):
        suggestedNodeID, service, address = self._GetNodeFromAddressAdjustments(service, address)
        if isinstance(service, str):
            if macho.mode != 'client':
                calledBy = log.WhoCalledMe()
                if calledBy not in self.getNodeFromAddressWarnsDone:
                    self.LogWarn('Passing a string(', service, ') serviceID into CheckAddressCache, will be mapped to a int internally. Please update the usage at:', calledBy)
                    self.getNodeFromAddressWarnsDone.add(calledBy)
            serviceID = self._MapServiceNameToServiceID(service)
            if serviceID:
                service = serviceID
        nodeID = self._addressCache.GetByServiceAddress(service, address)
        if not nodeID and lazyGetIfNotFound:
            uthread.new(self.GetNodeFromAddress, service, address)
        return nodeID

    def LookupAddressCache(self, serviceName, address):
        return self._addressCache.GetByServiceAddress(serviceName, address)

    def BlockGetNodeFromAddress(self):
        self.isGetNodeFromAddressBlocked = True

    def UnblockGetNodeFromAddress(self):
        self.isGetNodeFromAddressBlocked = False

    @bluepy.TimedFunction('machoNet::GetNodeFromAddress')
    def GetNodeFromAddress(self, serviceID, address):
        if getattr(self, 'isGetNodeFromAddressBlocked', False):
            if (serviceID, address) != (cluster.SERVICE_POLARIS, 0):
                raise RuntimeError('somebody called GetNodeFromAddress while blocked (%s, %s)' % (serviceID, address))
        suggestedNodeID, serviceID, address = self._GetNodeFromAddressAdjustments(serviceID, address)
        if isinstance(serviceID, str):
            calledBy = log.WhoCalledMe()
            if calledBy not in self.getNodeFromAddressWarnsDone:
                stack = ''
                for i in xrange(10):
                    stack += '%s\n' % log.WhoCalledMe(i)

                self.LogWarn('Passing a string(', serviceID, ') serviceID into GetNodeFromAddress, will be mapped to a int internally. Please update the usage at:', stack)
                self.getNodeFromAddressWarnsDone.add(calledBy)
            serviceID = self._MapServiceNameToServiceID(serviceID)
            if not serviceID:
                log.LogTraceback(extraText='Received a servicename into GetNodeFromAddress which did no map to a valid servicemask:' + str(serviceID))
        if address is None:
            raise RuntimeError('GetNodeFromAddress only works if you specify an address...')
        key = (serviceID, address)
        while 1:
            nodeID = self._addressCache.GetByServiceAddress(serviceID, address)
            if nodeID is None:
                myNodeID = self.nodeID
                if not self.connectToCluster:
                    myNodeID = -1
                uthread.Lock(self, serviceID, address)
                try:
                    nodeID = self._addressCache.GetByServiceAddress(serviceID, address)
                    if nodeID is None:
                        borkPrevention = 10
                        serviceMask = self.serviceMaskByServiceID[serviceID]
                        for i in xrange(100):
                            if serviceMask not in self.expectedLoadValue:
                                uthread.Lock(self, 'CluGetExpectedLoadValue')
                                try:
                                    self.expectedLoadValue[serviceID] = self.dbzcluster.LoadStats_ExpectedLoadValue(serviceID)
                                finally:
                                    uthread.UnLock(self, 'CluGetExpectedLoadValue')

                            nodeID = self._GetNodeFromAddressFromDB(myNodeID, serviceID, int(address), suggestedNodeID, self.expectedLoadValue[serviceID], serviceMask)
                            if nodeID <= 0:
                                if nodeID == -1:
                                    self.LogError('zcluster.Cluster_NodeFromAddress informed us that an app lock timeout occurred')
                                    self.LogError('Sleeping and retrying.  This is very bad.')
                                    blue.pyos.synchro.SleepWallclock(15000)
                                    continue
                                elif nodeID == -2:
                                    self.LogError("zcluster.Cluster_NodeFromAddress informed us that we're dead")
                                    log.LogTraceback()
                                    blue.pyos.synchro.SleepWallclock(60000)
                                    self.dbzcluster.Nodes_Trash(self.nodeID, "zcluster.Cluster_NodeFromAddress informed us that we're dead", 1)
                                    log.Quit("zcluster.Cluster_NodeFromAddress informed us that we're dead")
                                elif nodeID == -3:
                                    if borkPrevention > 0:
                                        self.LogWarn('Cluster Segmentation Initial Fragmentation Prevention for ', key, ': Sleeping for ', 1 + self.heartbeatInterval / 10, ' seconds to allow other segments to pass the safety time.')
                                        blue.pyos.synchro.SleepWallclock(1000 * (1 + self.heartbeatInterval / 10))
                                        borkPrevention = borkPrevention - 1
                                        continue
                                    if borkPrevention == 0:
                                        log.LogTraceback("Couldn't allocate address on any server.  Cluster borked beyond recognition.  Performing emergency cluster desegmentation.")
                                        self.dbzcluster.Cluster_Desegmentation()
                                        self.ClusterBroadcast('OnClusterDesegmentation')
                                        continue
                                    else:
                                        log.LogTraceback("Couldn't allocate address on any server after desegmentification.  Cluster borked beyond recognition.")
                                        raise RuntimeError('The address you asked for could not be allocated on any server.  This cluster must be seriously borked, to say the least...')
                                elif nodeID == -4:
                                    self.LogWarn('zcluster.Cluster_NodeFromAddress informed us that the address we requested (', serviceID, ',', address, ") was recently mapped on a node that has not yet acknowledged it's death")
                                    self.LogWarn('Sleeping and retrying.')
                                    blue.pyos.synchro.SleepWallclock(15000)
                                    continue
                                else:
                                    self.LogError('zcluster.Cluster_NodeFromAddress went haywire')
                                    log.LogTraceback('Bork Bork in zcluster.Cluster_NodeFromAddress')
                                    self.dbzcluster.Nodes_Trash(self.nodeID, 'zcluster.Cluster_NodeFromAddress went haywire and returned an illegal value', 1)
                                    log.Quit('zcluster.Cluster_NodeFromAddress went haywire and returned an illegal value')
                            if nodeID == 0:
                                log.LogTraceback('zcluster.Cluster_NodeFromAddress returned 0???')
                                nodeID = None
                            if nodeID is not None:
                                self._addressCache.SetServiceAddress(serviceID, address, nodeID)
                                break
                            else:
                                log.LogTraceback('zcluster.Cluster_NodeFromAddress returned 0 or None???  Entering bork-prevention loop')
                                blue.pyos.synchro.SleepWallclock(5000)

                        if nodeID is None:
                            log.LogTraceback('Failing to acquire a nodeID for address (%s).  Raising.' % strx(key))
                            raise RuntimeError('GetNodeFromAddress failed to acquire a nodeID for the address (1)')
                finally:
                    uthread.UnLock(self, serviceID, address)

                if nodeID is None:
                    raise RuntimeError("Couldn't resolve %s:%s to a node" % (serviceID, address))
            if nodeID is None:
                log.LogTraceback('Failed to acquire a nodeID for address (%s).  Raising.' % strx(key))
                raise RuntimeError('GetNodeFromAddress failed to acquire a nodeID for the address (2)')
            if self._addressCache.IsDeadNode(nodeID):
                self.LogError('Tried to return a dead mapping: Dead Node ', nodeID, ' has been registered in the address cache for ', key)
                self._addressCache.RemoveAllForNode(nodeID)
                blue.pyos.synchro.SleepWallclock(3000)
            else:
                break

        return nodeID

    def ClearNodeOfAddresses(self, addresses):
        totalCleared = 0
        for service, address in addresses:
            try:
                self.LogWarn('ClearNodeOfAddresses: clearing (', service, ', ', address, ')')
                uthread.Lock(self, service, address)
                self.SetNodeOfAddress(service, address, None)
                totalCleared += 1
            finally:
                uthread.UnLock(self, service, address)

        return totalCleared

    def GetNodeIDsFromServiceMask(self, serviceMask):
        return self._addressCache.GetByServiceMask(serviceMask)

    def GetFullAddressCache(self):
        return (dict(self._addressCache.GetCachedServiceAddressMap()), dict(self._addressCache.GetCachedServiceMaskMap()))

    def GetFullServiceMaskAddressCache(self):
        return self._addressCache.GetCachedServiceMaskMap()

    def GetServiceMaskByServiceID(self, serviceID):
        return self.serviceMaskByServiceID.get(serviceID, None)

    def OnClusterDesegmentation(self):
        self.LogWarn('Cluster desegmentation')
        self.clusterIsDesegmented = True
        for nodeID in self.transportIDbySolNodeID.iterkeys():
            self._addressCache.LoadNodeToServiceMaskMapping(nodeID, cluster.SERVICE_ALL)

        if macho.mode == 'server':
            self.serviceMask = cluster.SERVICE_ALL

    def _GetNodeFromAddressFromDB(self, myNodeID, serviceMapping, address, suggestedNodeID, expectedLoadValue, serviceMask):
        return self.dbzcluster.Cluster_NodeFromAddress(myNodeID, serviceMapping, address, suggestedNodeID, expectedLoadValue, serviceMask)

    def GuessNodeIDFromAddress(self, serviceName, address):
        return None

    def _GetNodeFromAddressAdjustments(self, service, address):
        return (None, service, address)

    def PrimeAddressCache(self, allMappings):
        mapped = 0
        for each in allMappings:
            if self._addressCache.IsDeadNode(each.nodeID):
                continue
            serviceID = self._MapServiceNameToServiceID(each.serviceName)
            if self._addressCache.SetServiceAddress(serviceID or each.serviceName, each.addressID, each.nodeID):
                mapped += 1

        if mapped:
            self.LogInfo('PrimeAddressCache mapped %d new addresses' % mapped)

    def ClearAddressCache(self):
        self._addressCache.Clear()

    def RemoveAllForNode(self, nodeId):
        self._addressCache.RemoveAllForNode(nodeId)

    def HandleUnMachoDestination(self, nodeID, packet):
        if self.IsClusterShuttingDown():
            return
        self._addressCache.RemoveAllForNode(nodeID)
        self.LogWarn('UnMachoDestination received.  Performing provisional node death handling for packet=', packet)
        if self._addressCache.IsKnownNode(nodeID):
            self.ServerBroadcast('OnNodeDeath', nodeID, 0)

    def AreTheseServicesRunning(self, requiredServices):
        for required in requiredServices:
            if required not in sm.services:
                self.LogInfo('AreTheseServicesRunning:  Waiting for %s to initiate startup' % required)
                return required

        for s in sm.services.itervalues():
            if s.state == service.SERVICE_FAILED:
                self.LogInfo('AreTheseServicesRunning:  %s was SERVICE_FAILED' % s.__guid__)
                if s.__error__:
                    raise s.__error__[1], None, s.__error__[2]
                else:
                    raise RuntimeError, 'Service %s failed' % s.__guid__
            if s.state != service.SERVICE_RUNNING:
                self.LogInfo('AreTheseServicesRunning:  Waiting for %s' % s.__guid__)
                return s.__guid__.split('.')[1]
            for dependant in s.__dependencies__:
                if dependant not in sm.services:
                    self.LogInfo('AreTheseServicesRunning:  Waiting for %s, which is a dependant of %s, to initiate startup' % (dependant, s.__guid__.split('.')[1]))
                    return dependant

        if 'config' in requiredServices:
            import __builtin__
            if 'const' not in dir(__builtin__):
                self.LogInfo('AreTheseServicesRunning:  const not in builtin')
                return 'config::const'
            if 'cfg' not in dir(__builtin__):
                self.LogInfo('AreTheseServicesRunning:  cfg not in builtin')
                return 'config::cfg'

    def GetNodeID(self):
        if not hasattr(self, 'nodeID'):
            return
        if macho.mode == 'server':
            while self.nodeID is None:
                self.LogError("Some dude is trying to get our nodeID before we're up and running...  Can't have that, now can we?  Let's sleeping on it.")
                log.LogTraceback()
                blue.pyos.synchro.SleepWallclock(1000)

        return self.nodeID

    def GetAcceptDelay(self):
        return self.acceptDelay

    def GetNodeTypeFromID(self, nodeID):
        if nodeID >= const.maxNodeID:
            return 'proxy'
        else:
            return 'server'

    def GetClientSessionID(self):
        if macho.mode == 'client':
            return (self.clientSessionID, session.userid)
        return 0

    def GetMachoTransportByClientID(self, clientID):
        return self.transportsByID.get(self.transportIDbyClientID.get(clientID, None), None)

    def GetSessionByClientID(self, clientID):
        transport = self.GetMachoTransportByClientID(clientID)
        if transport is None:
            return
        else:
            return transport.sessions.get(clientID, None)

    def GetConnectedProxyNodes(self):
        return self.transportIDbyProxyNodeID.keys()

    def GetConnectedSolNodes(self):
        return self.transportIDbySolNodeID.keys()

    def GetConnectedNodes(self):
        return self.GetConnectedProxyNodes() + self.GetConnectedSolNodes()

    def GetTransportOfNode(self, nodeID):
        transportID = self.transportIDbyProxyNodeID.get(nodeID, None) or self.transportIDbySolNodeID.get(nodeID, None) or self.transportIDbyAppNodeID.get(nodeID, None)
        return self.transportsByID.get(transportID, None)

    def GetMachoTransportsByTransportIDs(self, ids):
        retval = []
        for each in ids:
            if self.transportsByID.has_key(each):
                retval.append(self.transportsByID[each])

        return retval

    def GetTransport(self, transportName):
        return self.namedtransports.get(transportName, None)

    def OnHeartBeat(self):
        while not getattr(self, 'stop', True):
            blue.pyos.synchro.SleepWallclock(int(self.heartbeatInterval * 1000))
            if self.nodeID is not None and (self.shutdown is None or self.shutdown.when > blue.os.GetWallclockTime()):
                try:
                    secs = self.dbzcluster.Nodes_HeartBeat(self.nodeID)
                    if self.debugHeartBeat:
                        self.LogNotice('Node', self.nodeID, 'Done sending Heartbeat @ ', utilFormat.FmtDateEng(blue.os.GetWallclockTime()), ' result ', repr(secs))
                except ConnectionError as e:
                    self.LogError('!! ---------------------------------------------------------- !!')
                    self.LogError('ConnectionError exception:[%s]. If SHUTDOWN, then possibly due to a too long/unrecoverable DB Cluster fail over.' % e)
                    self.LogError('!! ---------------------------------------------------------- !!')
                    log.LogException()
                    self._OnHeartBeatLost('ConnectionError exception:[%s]. If SHUTDOWN, then possibly due to a too long/unrecoverable DB Cluster fail over.')
                except StandardError:
                    self.LogError('!! ---------------------------------------------------------- !!')
                    self.LogError('Oh my God!  An exception during zcluster.Nodes_HeartBeat!!!')
                    self.LogError('!! ---------------------------------------------------------- !!')
                    log.LogException()
                    self._OnHeartBeatLost('Exception during zcluster.Nodes_HeartBeat')

                if not __debug__:
                    if secs > self.cleanupInterval:
                        self._OnHeartBeatLagging()
                        if not hasattr(self, 'slowdeath'):
                            self.slowdeath = 1
                            self.LogError('Node ', self.nodeID, ' is dead.  The server is configured with a ', self.cleanupInterval, " second cleanup interval, but it's been ", secs, ' seconds since')
                            self.LogError("he last performed a heartbeat.  That means every other server on the network have assumed that he's dead")
                            self.LogError('and will remove his entries from the database, effectively turning him into a mummy that wanders around,')
                            self.LogError('borking up everything.')
                        self.LogError("The server is overloaded and dead as far as everybody is concerned.  This may NEVER happen on a live server.  It's heartbeat is supposed to be every ", self.heartbeatInterval, " secs, but it's down to ", secs, '.  Braindeath occurred at ', self.cleanupInterval)
                        self.LogError('A reboot is probably in order.')
                    elif secs > self.cleanupInterval - self.heartbeatInterval:
                        self.LogError("The server is extremely loaded, and basically taking the highway to doom.  It's heartbeat is supposed to be every ", self.heartbeatInterval, " secs, but it's down to ", secs, '.  Braindeath occurs at ', self.cleanupInterval)
                    elif secs > self.heartbeatInterval * 4 / 3:
                        self.LogWarn("The server is very loaded, beware...    It's heartbeat is supposed to be every ", self.heartbeatInterval, " secs, but it's down to ", secs, '.  Braindeath occurs at ', self.cleanupInterval)
                    elif secs < 0:
                        self.LogError('!! ---------------------------------------------------------- !!')
                        self.LogError("Oh my God!  I've been removed from zcluster.nodes!!!  That means I'm already dead, I just didn't know about it!!!!")
                        self.LogError("How embarrassing.  I must be causing all sorts of trouble.  I think I'll just lie down and die of shame.")
                        self.LogError('!! ---------------------------------------------------------- !!')
                        self._OnHeartBeatLost("zcluster.Nodes_HeartBeat indicated that I've been removed from zcluster.nodes")
                    else:
                        self._OnHeartBeatNormal()

    def _OnHeartBeatLagging(self):
        if not self.heartbeat_lagging:
            self.heartbeat_lagging = True
            sm.ScatterEvent('OnNodeHeartbeatLagging')

    def _OnHeartBeatNormal(self):
        if self.heartbeat_lagging:
            self.heartbeat_lagging = False
            sm.ScatterEvent('OnNodeHeartbeatBackToNormal')

    def _OnHeartBeatLost(self, reason = 'zcluster.Nodes_HeartBeat problem'):
        cleanup_timeout_in_seconds = 10
        sm.ScatterEvent('OnNodeHeartbeatLost', reason=reason, cleanup_timeout_in_seconds=cleanup_timeout_in_seconds)
        self.Stop(reason=reason)
        uthread2.sleep(cleanup_timeout_in_seconds + 1)
        log.Quit(reason)

    def OnCleanUp(self):
        if not __debug__:
            while not getattr(self, 'stop', True):
                try:
                    blue.pyos.synchro.SleepWallclock(int(self.cleanupInterval * 1000))
                    self.dbzcluster.Nodes_TrashLimbos(self.cleanupInterval)
                except Exception:
                    log.LogException('Exception during OnCleanUp.  Ignoring.')
                    sys.exc_clear()

    def GetGPCS(self, channel = None):
        if macho.mode == 'client':
            while self.authenticating == 2:
                blue.pyos.synchro.SleepWallclock(500)

        while not self.state == SERVICE_RUNNING:
            self.LogError("GetGPCS shouldn't be called on machoNet before it's running...")
            log.LogTraceback()
            blue.pyos.synchro.SleepWallclock(500)

        return self.channelHandlersDown.get(channel, None)

    def Ping(self, pingCount = 5, nodeID = None, silent = False):
        if nodeID is None:
            address = MachoAddress()
            daNode = 'random node'
        else:
            address = MachoAddress(nodeID=nodeID)
            daNode = 'node %s' % nodeID

        def prepared_print(prepared):
            lengths = [0] * len(prepared[0])
            for i in range(len(prepared[0])):
                for each in prepared:
                    each[i] = strx(each[i])
                    if len(each[i]) > lengths[i]:
                        lengths[i] = len(each[i]) + 1

                for each in prepared:
                    each[i] += ' ' * (lengths[i] - len(each[i]))

            for i in range(0, len(prepared)):
                each = prepared[i]
                if i < 2:
                    each[1] = each[1][:-lengths[3] + 1]
                    each[2] = each[2][:-lengths[3] + 1]
                else:
                    each[1] = each[1][-lengths[3]:]
                    each[2] = each[2][-lengths[3]:]

            for each in prepared:
                x = ''
                for other in each:
                    x += other

                if not silent:
                    print x

        summaries = []
        for i in range(pingCount):
            if not silent:
                print '---------------------------------------------------------------------------------------------'
                print ' MachoNet Ping statistics for %s' % daNode
                print '---------------------------------------------------------------------------------------------'
            prepared = [['Where',
              'TickID',
              'Time',
              'Time-Tick',
              'curr-start',
              'curr-start',
              'Time-Last Time',
              'Time-Last Time'], ['',
              '',
              '',
              '',
              '(blues)',
              '(millisecs)',
              '(blues)',
              '(millisecs)']]
            retval = self._BlockingCall(PingReq(destination=address, times=[(blue.os.GetWallclockTime(), blue.os.GetWallclockTimeNow(), macho.mode + '::start')]))
            retval.times.append((blue.os.GetWallclockTime(), blue.os.GetWallclockTimeNow(), macho.mode + '::stop'))
            for n in range(len(retval.times)):
                each = retval.times[n]
                stopminusstartb = ''
                stopminusstartm = ''
                m = 0
                if each[2] in ('proxy::after_tasklet', 'server::after_tasklet', 'client::after_tasklet'):
                    m = 1
                elif each[2] in ('proxy::writing', 'server::turnaround', 'client::stop'):
                    m = 2
                if m:
                    other = retval.times[n - m]
                    stopminusstartb = long(round(float(each[1] - other[1])))
                    stopminusstartm = long(round(float(each[1] - other[1]) * 10.0 / float(const.MSEC)))
                    if stopminusstartm:
                        stopminusstartm = str(stopminusstartm / 10) + '.' + str(stopminusstartm % 10)
                    else:
                        stopminusstartm = ''
                tmltb = ''
                tmltm = ''
                if n > 2:
                    tmltb = long(each[1]) - long(retval.times[n - 1][1])
                    tmltm = long(round(float(tmltb) * 10.0 / float(const.MSEC)))
                    if tmltm:
                        tmltm = str(tmltm / 10) + '.' + str(tmltm % 10)
                    else:
                        tmltm = ''
                prepared.append([each[2],
                 each[0],
                 each[1],
                 each[1] - each[0],
                 stopminusstartb,
                 stopminusstartm,
                 tmltb,
                 tmltm])

            prepared_print(prepared)
            clientFirst = len(prepared)
            proxyFirst = len(prepared)
            serverFirst = len(prepared)
            for i in reversed(range(len(prepared))):
                if prepared[i][0].startswith('client::'):
                    clientFirst = i
                if prepared[i][0].startswith('proxy::'):
                    proxyFirst = i
                if prepared[i][0].startswith('server::'):
                    serverFirst = i

            clientLast = -1
            proxyLast = -1
            serverLast = -1
            for i in range(len(prepared)):
                if prepared[i][0].startswith('client::'):
                    clientLast = i
                if prepared[i][0].startswith('proxy::'):
                    proxyLast = i
                if prepared[i][0].startswith('server::'):
                    serverLast = i

            cr = 10000000000.0
            if clientFirst < clientLast:
                cr = (float(prepared[clientLast][2].strip()) - float(prepared[clientFirst][2].strip())) / const.MSEC
                if not silent:
                    print 'client roundtrip:  ', cr, ' msec'
            pr = 10000000000.0
            if proxyFirst < proxyLast:
                pr = (float(prepared[proxyLast][2].strip()) - float(prepared[proxyFirst][2].strip())) / const.MSEC
                if not silent:
                    print 'proxy roundtrip:   ', cr, ' msec'
            server1 = [ p[0].strip() for p in prepared ].index('proxy::writing')
            server2 = [ p[0].strip() for p in prepared ].index('proxy::handle_message', server1)
            diff = float(prepared[server2][2]) - float(prepared[server1][2])
            diff /= const.MSEC
            pspr = diff
            if not silent:
                print 'proxy-server-proxy rountrip: %sms' % pspr
            tickids = []
            for each in prepared[2:]:
                if each[1] not in tickids:
                    tickids.append(each[1])

            if not silent:
                print 'Roundtrip tick count=', len(tickids)
            summaries.append((cr,
             pr,
             pspr,
             len(tickids)))

        average = [ sum([ s[i] for s in summaries ]) / len(summaries) for i in range(len(summaries[0])) ]
        minerage = [ min([ s[i] for s in summaries ]) for i in range(len(summaries[0])) ]
        if not silent:
            print 'Totals for: Client rountrip, proxy roundtrip, proxy-server-proxy roundtrip, tickcount'
            print 'Average: ' + repr(average)
            print 'Minimum: ' + repr(minerage)
        return retval.times

    def GetServiceInfo(self):
        with self.fetchedDataLock:
            if self.fetchedServiceInfo is None:
                if macho.mode == 'proxy':
                    self.fetchedServiceInfo = self.session.ConnectToRemoteService('machoNet').GetServiceInfo()
                    self.fetchedServiceInfo.GetCachedObject()
                else:
                    serviceInfo = {}
                    for svc in sm.services.itervalues():
                        if hasattr(svc, '__machoresolve__'):
                            serviceInfo[svc.__logname__] = svc.__machoresolve__

                    self.fetchedServiceInfo = utilCachedObject(1, 'machoNet.serviceInfo', serviceInfo)
            return self.fetchedServiceInfo

    def ClearFetchedData(self):
        with self.fetchedDataLock:
            self.fetchedServiceInfo = None
            if macho.mode == 'server':
                self.ProxyBroadcast('OnClearFetchedData')

    def OnClearFetchedData(self):
        if macho.mode == 'proxy':
            self.ClearFetchedData()

    def OnGlobalConfigUpdated(self, key, value):
        self.LogNotice('OnGlobalConfigUpdated', key, value)
        if self.globalConfig is None:
            self.globalConfig = self.GetGlobalConfig() or {}
        if value is None:
            if key in self.globalConfig:
                del self.globalConfig[key]
        else:
            self.globalConfig[key] = value
        monolithconfig.trigger_global_config_updates()
        sm.ScatterEvent('OnGlobalConfigChanged', self.globalConfig)

    @bluepy.TimedFunction('machoNet::__IsVIP')
    def __IsVIP(self, vipKey):
        if vipKey is None:
            return False
        with self.vipLock:
            if self.vipkeys is None:
                self.__PrimeVIPList()
            return vipKey in self.vipkeys

    @bluepy.TimedFunction('machoNet::__IsVIPbyUser')
    def __IsVIPbyUser(self, userID):
        if userID is None:
            return False
        with self.vipLock:
            if self.vipUsers is None:
                self.__PrimeVIPList()
            return userID in self.vipUsers

    def __PrimeVIPList(self):
        self.vipkeys = set()
        self.vipUsers = set()
        for r in self.session.ConnectToSolServerService('DB2').CallProc('zuser.Users_SelectByRole', ROLE_VIPLOGIN):
            self.vipkeys.add(CryptoHash(utilFormat.CaseFold(r.userName)))
            self.vipUsers.add(r.userID)

    def OnVIPListChanged(self):
        with self.vipLock:
            self.vipkeys = None
            self.vipUsers = None

    def IsThisUserCoolForLogin(self, userID):
        if self.IsInVIP():
            return self.__IsVIPbyUser(userID)
        return True

    def IsInVIP(self):
        return bool(self.vipMode)

    @bluepy.TimedFunction('machoNet::GetLogonQueuePosition')
    def GetLogonQueuePosition(self, transportID, vipKey):
        if self.__IsVIP(vipKey):
            return 1
        try:
            position = self.serverLogonQueue.index(transportID) + 2
        except ValueError:
            log.LogException()
            position = 2

        position -= self.availableLoginSlots
        return max(1, position)

    def PutTransportInLogonQueue(self, transportID):
        self.serverLogonQueue.append(transportID)

    def RemoveTransportFromLogonQueue(self, transportID):
        self.serverLogonQueue.remove(transportID)

    def GetLogonQueueStats(self):
        loggedInConnections = len(self.transportIDbyClientID)
        pendingConnections = len(self.serverLogonQueue)
        return (loggedInConnections, pendingConnections, self.availableLoginSlots)

    def Authenticate(self, transport, request, sessionID):
        clientID = self.GetIDOfAddress(transport.address, clientMode=True)
        ssoToken = request.get('user_sso_token', None)
        authSvc = self.session.ConnectToRemoteService('authentication')
        loginInfo, access_token, computer_hash = authSvc.Login(sessionID, request['user_name'], request['user_password'], request['user_password_hash'], const.userConnectTypeClient, transport.address, clientID, request, ssoToken=ssoToken, clientVersion=request['boot_build'])
        ret = {'sessionID': sessionID,
         'user_clientid': clientID,
         'session_init': loginInfo,
         'access_token': access_token,
         'computer_hash': computer_hash}
        user_id = loginInfo['userid']
        if not self.IsThisUserCoolForLogin(user_id):
            ipaddress = transport.address.split(':')[0]
            authSvc.Logout(sessionID, ipaddress=ipaddress)
            raise UserRejectedByVIP()
        transport.sessionID = sessionID
        uthread.worker('machoNet::AutoLogOffClient', self.__AutoLogOffClient, transport, sessionID)
        return ret

    def __AutoLogOffClient(self, transport, sessionID):
        blue.pyos.synchro.SleepWallclock(self.autoLogoffAuthenticatedTransportInterval * 1000)
        if sessionID not in self.transportIDbySessionID and not transport.IsClosed():
            transport.Close('Authentication Timeout', 'HANDSHAKE_TIMEOUT_AUTHENTICATED')
            ipaddress = transport.address.split(':')[0]
            self.session.ConnectToRemoteService('authentication').Logout(sessionID, ipaddress=ipaddress)

    def LogOffSession(self, sessionID, ipaddress = None):
        if sessionID and not self.IsClusterShuttingDown():
            uthread.worker('machoNet::LogOffSession', self.session.ConnectToRemoteService('authentication').Logout, sessionID, ipaddress=ipaddress)

    def GetTime(self):
        return blue.os.GetWallclockTimeNow()

    def SendProvisionalResponse(self, method, *args, **keywords):
        if currentcall:
            timeout = keywords.get('machoTimeout', self.callTimeOutInterval)
            response = currentcall.packet.Response(payload=())
            response.oob['provisional'] = (timeout, method, args)
            response.trace_id = None
            response.parent_span_id = None
            self.LogInfo('Sending provisional response and updating timeout interval', response)
            self._NonBlockingCall(response)
        else:
            self.LogWarn('Ignoring provisional response request, currentcall=', currentcall)

    def __TimeoutCall(self, channel):
        channel.send_exception(RuntimeError, ('OnMachoTimeout', {'what': 'A low-level timeout occurred during a remote service request'}))

    def __TimeoutCallLoop(self):
        while not getattr(self, 'stop', True):
            try:
                timeout = []
                blue.pyos.synchro.SleepWallclock(100 * self.callTimeOutInterval)
                if self.reducedTimeouts:
                    timeoutCalls = self.timeoutCalls
                else:
                    timeoutCalls = self.calls
                for k in timeoutCalls.keys():
                    if blue.os.GetWallclockTime() > self.calls[k][1]:
                        v = self.calls[k]
                        timeout.append((self.__TimeoutCall, (v[0],)))
                        del self.calls[k]
                        if k in self.timeoutCalls:
                            del self.timeoutCalls[k]
                        self.callsCountMin = min(self.callsCountMin, len(self.calls))
                        if k in v[2]:
                            del v[2][k]

                if timeout:
                    uthread.parallel(timeout)
            except Exception:
                log.LogException('Exception during Timeout Call Loop')
                sys.exc_clear()

    def __KATLoop(self):
        if macho.mode == 'client':
            keepAliveTimerInterval = self.clientKeepAliveTimerInterval
        else:
            keepAliveTimerInterval = self.serverKeepAliveTimerInterval
        while not getattr(self, 'stop', True):
            try:
                blue.pyos.synchro.SleepWallclock(keepAliveTimerInterval * 1000 / 4)
                if not self.clockReset:
                    continue
                time = blue.os.GetWallclockTime()
                clientCheck = time - self.clientKeepAliveTimerInterval * const.SEC
                clientDead = time - 3 * self.clientKeepAliveTimerInterval * const.SEC
                serverCheck = time - self.serverKeepAliveTimerInterval * const.SEC
                serverDead = time - 3 * self.serverKeepAliveTimerInterval * const.SEC
                for transport in self.transportsByID.itervalues():
                    if not transport.lastPing:
                        continue
                    if transport.clientID:
                        check, dead = clientCheck, clientDead
                    else:
                        check, dead = serverCheck, serverDead
                    req, resp = transport.lastPing
                    if resp >= check:
                        continue
                    if hasattr(transport, 'done_broadcasting_close'):
                        continue
                    if resp < dead and req > resp:
                        if transport.clientID:
                            transport.Close('Client Transport keep-alive timer has expired', 'KEEPALIVEEXPIRED')
                        else:
                            transport.Close('Proxy/Server Transport keep-alive timer was determined expired by %s #%s' % (macho.mode, self.nodeID))
                    elif not transport.pinging:
                        uthread.worker('machoNet::KATPing', self.__KATPing, transport)

            except Exception:
                log.LogException('Exception during KAT Loop')
                sys.exc_clear()

    def __KATPing(self, transport):
        try:
            transport.pinging = True
            try:
                t0 = blue.os.GetWallclockTimeNow()
                if not transport.lastPing:
                    transport.lastPing = [0, 0]
                transport.lastPing[0] = t0
                response = self._BlockingCall(PingReq(destination=transport.GetMachoAddressOfOtherSide(), times=[]))
                t1 = blue.os.GetWallclockTimeNow()
                tResponse = response.times[0][1] - transport.estimatedRTT / 2
                tDiff = t1 - t0
                transport.estimatedRTT = transport.estimatedRTT * 0.85 + (t1 - t0) * 0.15
                transport.timeDiff = transport.timeDiff * 0.85 + (t0 + (t1 - t0) / 2 - tResponse) * 0.15
                transport.lastPing[1] = t1
            finally:
                transport.pinging = False

        except UnMachoDestination as e:
            self.LogWarn('UnMachoDestination encountered while pinging ', transport.GetMachoAddressOfOtherSide(), '.  Probably irrelevant')
            sys.exc_clear()
        except GPSTransportClosed as e:
            self.LogInfo("KATPing detected a closed transport.  That's what it's supposed to do...")
            if transport.transportID in self.transportsByID:
                self.transportsByID[transport.transportID].Close('KATPing detected that the socket was closed', 'KEEPALIVEEXPIRED')
            sys.exc_clear()
        except StandardError:
            self.LogError("Unhandled exception in KATPing.  Shouldn't be a problem, but I wanna see it")
            self.LogError('Worst case, transport keepalive timers should be failing to do their job')
            log.LogException()
            sys.exc_clear()

    def _BlockingCall(self, packet, destTransport = None):
        if destTransport is None:
            transports = self._GetTransports(packet.destination)
            if len(transports) > 1:
                raise UnMachoDestination('A blocking call cannot be performed using a forking address.  Use ConnectToAllNeighboringServices instead.')
            destTransport = transports[0]
        callID = self.callID
        self.callID += 1
        if macho.mode == 'client':
            source = MachoAddress(clientID=0, callID=callID)
        else:
            source = MachoAddress(nodeID=self.nodeID, callID=callID)
        packet.source = source
        self.calls[callID] = [uthread.Channel('machoNet::BlockingCall'),
         blue.os.GetWallclockTime() + packet.oob.get('machoTimeout', self.callTimeOutInterval) * const.SEC,
         destTransport.calls,
         callID]
        packetTimeout = packet.oob.get('machoTimeout', None)
        if packetTimeout:
            self.timeoutCalls[callID] = blue.os.GetWallclockTime() + packetTimeout * const.SEC
        self.callsCountMax = max(self.callsCountMax, len(self.calls))
        try:
            destTransport.calls[callID] = self.calls[callID][0]
            before = blue.os.GetWallclockTime()
            try:
                destTransport.Write(packet)
                while 1:
                    retval = self.calls[callID][0].receive()
                    if macho.mode == 'client':
                        destTransport.TagPacketSizes(packet, retval)
                    provisional = retval.oob.get('provisional', None)
                    if provisional is None:
                        break
                    if macho.mode == 'client':
                        self.LogInfo('Received Provisional Response, provisional=', provisional)
                        self.calls[callID][1] = blue.os.GetWallclockTime() + provisional[0] * const.SEC
                        if provisional[1].startswith('Process'):
                            sm.ChainEventWithoutTheStars(provisional[1], provisional[2])
                        elif provisional[1].startswith('Do'):
                            sm.SendEventWithoutTheStars(provisional[1], provisional[2])
                        else:
                            sm.ScatterEventWithoutTheStars(provisional[1], provisional[2])

            finally:
                if destTransport.calls.has_key(callID):
                    del destTransport.calls[callID]
                after = blue.os.GetWallclockTime()
                diff = after - before
                self.blockingCallTimes.Add(diff)

        except ReferenceError:
            exctype, exc, tb = sys.exc_info()
            try:
                raise RuntimeError('ReferenceError'), None, tb
            finally:
                exctype = None
                xc = None
                tb = None

        finally:
            if callID in self.timeoutCalls:
                del self.timeoutCalls[callID]
            if self.calls.has_key(callID):
                del self.calls[callID]
                self.callsCountMin = min(self.callsCountMin, len(self.calls))
            if destTransport.calls.has_key(callID):
                del destTransport.calls[callID]

        if retval.command == cluster.MACHONETMSG_TYPE_ERRORRESPONSE:
            if retval.code == cluster.MACHONETERR_UNMACHODESTINATION:
                raise UnMachoDestination(retval.payload)
            elif retval.code == cluster.MACHONETERR_UNMACHOCHANNEL:
                raise UnMachoChannel(retval.payload)
            elif retval.code == cluster.MACHONETERR_WRAPPEDEXCEPTION:
                raise MachoWrappedException(retval.payload)
            else:
                raise MachoException(retval.payload)
        return retval

    CallDown = _BlockingCall

    def _NonBlockingCall(self, packet):
        try:
            transports = self._GetTransports(packet.destination)
            for each in transports:
                each.Write(packet)
                each.TagPacketSizes(packet)

        except UnMachoDestination as e:
            self.LogInfo("_NonBlockingCall failed for an UnMachoDestination.  The reason given was '", e.payload, "'.  Generally speaking, this is probably just fine and dandy.")
            self.LogInfo('Packet=', packet)
            sys.exc_clear()
        except GPSTransportClosed as e:
            self.LogInfo("_NonBlockingCall failed for a closed transport.  The reason given was '", e.reason, "'.  Generally speaking, this is probably just fine and dandy.")
            self.LogInfo('Packet=', packet)
            sys.exc_clear()

    NotifyDown = _NonBlockingCall

    def __TransportChoice(self, transportIDs):
        if len(transportIDs) == 1:
            return transportIDs[0]
        options = []
        for transportID in transportIDs:
            try:
                nodeID = self.transportsByID.get(transportID).nodeID
                cpu = self.nodeCPULoadValue.get(nodeID, 1.0)
                weight = 1.0 / float(max(0.01, cpu))
            except:
                weight = 1.0

            options.append([weight, transportID])

        if len(options) > 1:
            options.sort(lambda x, y: cmp(y[0], x[0]))
            options.pop()
        return weightedChoice(options)

    @bluepy.TimedFunction('machoNet::_GetTransports')
    def _GetTransports(self, destAddress, srcTransport = None):
        if macho.mode == 'client':
            srcTransport = self.namedtransports.get('tcp:packet:machoNet', None)
            if srcTransport and destAddress.addressType == const.ADDRESS_TYPE_BROADCAST and len(destAddress.narrowcast) == 1:
                appNodeID = destAddress.narrowcast[0]
                if appNodeID in self.transportIDbyAppNodeID:
                    machoTransport = self.transportsByID[self.transportIDbyAppNodeID[appNodeID]]
                    return [machoTransport]
            if not self.namedtransports.has_key('ip:packet:server'):
                raise GPSTransportClosed('The transport has not yet been connected, or authentication was not successful.')
            return [self.namedtransports['ip:packet:server']]
        else:
            transportID = None
            if destAddress.addressType == const.ADDRESS_TYPE_ANY:
                if srcTransport is not None and srcTransport.dependants:
                    mk, mv = [], 0
                    for k, v in srcTransport.dependants.iteritems():
                        if v > mv:
                            mk = [k]
                            mv = v
                        elif v == mv:
                            mk.append(k)

                    if mk:
                        transportID = self.__TransportChoice(mk)
                    else:
                        transportID = self.__TransportChoice(srcTransport.dependants.keys())
                elif macho.mode == 'server':
                    if self.transportIDbyProxyNodeID:
                        transportID = random.choice(self.transportIDbyProxyNodeID.values())
                    else:
                        raise UnMachoDestination('Could not connect to any proxy server')
                elif self.transportIDbySolNodeID:
                    transportID = self.__TransportChoice(self.transportIDbySolNodeID.values())
                else:
                    raise UnMachoDestination('Could not connect to any sol server')
            elif destAddress.addressType == const.ADDRESS_TYPE_NODE:
                if self._addressCache.IsDeadNode(destAddress.nodeID):
                    raise UnMachoDestination('The specified proxy or server node (%s) is dead' % destAddress.nodeID)
                if self.transportIDbySolNodeID.has_key(destAddress.nodeID):
                    transportID = self.transportIDbySolNodeID[destAddress.nodeID]
                elif self.transportIDbyProxyNodeID.has_key(destAddress.nodeID):
                    transportID = self.transportIDbyProxyNodeID[destAddress.nodeID]
                elif self.transportIDbyAppNodeID.has_key(destAddress.nodeID):
                    transportID = self.transportIDbyAppNodeID[destAddress.nodeID]
                elif macho.mode == 'server':
                    if len(self.transportIDbyProxyNodeID):
                        transportID = random.choice(self.transportIDbyProxyNodeID.values())
                else:
                    if not self._addressCache.IsDeadNode(destAddress.nodeID):
                        self._addressCache.MarkDeadNode(destAddress.nodeID)
                        reason = "The node wasn't registered in the proxy's transportIDbySolNodeID or transportIDbyProxyNodeID maps"
                        self.LogNotice('Sending OnNodeDeath for', destAddress.nodeID, 'because', reason)
                        self.ServerBroadcast('OnNodeDeath', destAddress.nodeID, 1, reason)
                    raise UnMachoDestination('The specified proxy or server node (%s) could not be reached' % destAddress.nodeID)
            elif destAddress.addressType == const.ADDRESS_TYPE_CLIENT:
                if self.transportIDbyClientID.has_key(destAddress.clientID):
                    transportID = self.transportIDbyClientID[destAddress.clientID]
                else:
                    raise UnMachoDestination('The client (%s) could not be reached' % destAddress.clientID)
            else:
                if destAddress.addressType == const.ADDRESS_TYPE_BROADCAST:
                    retval = []
                    transportIDs = self.GetTransportIDsFromBroadcastAddress(destAddress)
                    for each in transportIDs:
                        retval.append(self.transportsByID[each])

                    if not len(retval):
                        self.LogInfo('None of the specified destination addresses could be reached for ', destAddress)
                    return retval
                raise UnMachoDestination('The specified address type is invalid')
            if transportID is None:
                self.LogError('Some dude is sending a weird address (', destAddress, ")that doesn't resolve to a transport ID")
                log.LogTraceback()
                raise UnMachoDestination('The transportID is invalid')
            if not self.transportsByID.has_key(transportID):
                raise UnMachoDestination('The transportID does not identify a known transport')
            return [self.transportsByID[transportID]]

    def GetTransportIDsFromBroadcastAddress(self, destAddress):
        return self._GetTransportIDsFromBroadcastAddress(destAddress)

    @bluepy.TimedFunction('machoNet::_GetTransportIDsFromBroadcastAddress')
    def _GetTransportIDsFromBroadcastAddress(self, destAddress):
        if destAddress.idtype is None:
            idtype = None
            scattered = 0
        elif destAddress.idtype[0] in ('*', '+'):
            idtype = destAddress.idtype[1:]
            scattered = 1
        else:
            idtype = destAddress.idtype
            scattered = 0
        if len(destAddress.narrowcast):
            clientIDs = []
            nodeIDs = []
            done = 0
            if idtype == 'clientID':
                if macho.mode == 'server' and len(destAddress.narrowcast) >= 2 * len(self.transportIDbyProxyNodeID):
                    nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                else:
                    clientIDs = destAddress.narrowcast
                done = 1
            elif idtype == 'nodeID':
                nodeIDs = destAddress.narrowcast
                done = 1
            elif idtype == 'serviceMask':
                nodeIDs = self.ResolveServiceMaskToNodeIDs(destAddress.narrowcast[0])
                done = 1
            elif macho.mode == 'server':
                if idtype in self.__server_scattercast_session_variables__:
                    if scattered:
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                elif len(destAddress.narrowcast) == 1:
                    done, nodeIDs = self._GetServerBroadcastNodesSingle(idtype, destAddress, scattered)
                    if done is None:
                        self.LogWarn('Sending a packet by some funky address type (', idtype, ').  Resorting to scattercast')
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                else:
                    done, nodeIDs = self._GetServerBroadcastNodesMultiple(idtype, destAddress, scattered)
                    if done is None:
                        if not scattered:
                            self.LogWarn('Sending a packet via a non-scattered complex address that resorts to a scattercast.  address: ', destAddress)
                        else:
                            self.LogInfo('Sending a packet via a scattered complex address.  address: ', destAddress)
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
            if not done:
                notfound = []
                if len(destAddress.narrowcast) == 1 and (idtype, destAddress.narrowcast[0]) in self.spam:
                    spam = 1
                elif macho.mode == 'server':
                    if self.transportIDbyProxyNodeID:
                        spam, clientIDs, notfound = basesession.FindClientsAndHoles(idtype, destAddress.narrowcast, len(self.transportIDbyProxyNodeID) * 2)
                    else:
                        spam, clientIDs, notfound = basesession.FindClientsAndHoles(idtype, destAddress.narrowcast, 20)
                else:
                    spam, clientIDs, notfound = basesession.FindClientsAndHoles(idtype, destAddress.narrowcast, None)
                if len(destAddress.narrowcast) == 1 and spam:
                    self.LogInfo('Interpreting ', destAddress.narrowcast, ' as a persistant spam address.')
                    if len(self.spam) > 1000:
                        self.spam.clear()
                    self.spam.add((idtype, destAddress.narrowcast[0]))
                if spam or macho.mode == 'server' and destAddress.idtype[0] == '*' and len(notfound):
                    clientIDs = []
                    if macho.mode == 'server':
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                    else:
                        nodeIDs = self.transportIDbySolNodeID.iterkeys()
            transportIDs = set()
            if macho.mode == 'server' and self.transportIDbyProxyNodeID:
                for clientID in clientIDs:
                    try:
                        nodeID = self.GetProxyNodeIDFromClientID(clientID)
                    except Exception as e:
                        self.LogWarn('Unable to map clientID', repr(clientID), 'to proxyID. Dropping message Exception type=', type(e), ' args=', e.args)
                        continue

                    if nodeID in self.transportIDbyProxyNodeID:
                        transportIDs.add(self.transportIDbyProxyNodeID[nodeID])
                        if len(transportIDs) == len(self.transportIDbyProxyNodeID):
                            if len(transportIDs) > 2:
                                self.LogWarn('All proxies targeted in a clientID based routing decision.  If this happens frequently, the caller should resort to a better casting method.')
                            break

            else:
                for each in clientIDs:
                    if each in self.transportIDbyClientID and self.transportIDbyClientID[each] in self.transportsByID:
                        transportIDs.add(self.transportIDbyClientID[each])
                    else:
                        self.LogInfo('Transport for client ', each, ' not found while sending narrowcast.')

            for each in nodeIDs:
                if macho.mode == 'server' and each in self.transportIDbyProxyNodeID and self.transportIDbyProxyNodeID[each] in self.transportsByID:
                    transportIDs.add(self.transportIDbyProxyNodeID[each])
                elif macho.mode == 'proxy' and each in self.transportIDbySolNodeID and self.transportIDbySolNodeID[each] in self.transportsByID:
                    transportIDs.add(self.transportIDbySolNodeID[each])
                elif each in self.transportIDbyAppNodeID and self.transportIDbyAppNodeID[each] in self.transportsByID:
                    transportIDs.add(self.transportIDbyAppNodeID[each])
                elif each in self.transportIDbySolNodeID and self.transportIDbySolNodeID[each] in self.transportsByID:
                    transportIDs.add(self.transportIDbySolNodeID[each])
                else:
                    self.LogInfo('Transport for node', each, 'not found while sending narrowcast.')

            transportIDs = list(transportIDs)
        elif idtype == 'nodeID':
            if destAddress.idtype[0] == '+':
                transportIDs = self.transportIDbyProxyNodeID.values()
            else:
                transportIDs = self.transportIDbySolNodeID.values()
        elif idtype == 'clientID' and macho.mode == 'server':
            transportIDs = self.transportIDbyProxyNodeID.values()
        elif macho.mode == 'server':
            transportIDs = self.transportsByID.keys()
        else:
            transportIDs = self.transportIDbyClientID.values()
        if transportIDs:
            self.broadcastsResolved.Add(len(transportIDs))
        else:
            self.broadcastsMissed.Add()
        return transportIDs

    def __GetServerBroadcastNodesStub(self, idtype, destAddress, scattered):
        done = None
        nodeIDs = None
        return (done, nodeIDs)

    _GetServerBroadcastNodesSingle = __GetServerBroadcastNodesStub
    _GetServerBroadcastNodesMultiple = __GetServerBroadcastNodesStub

    def ResolveServiceMaskToNodeIDs(self, serviceMask):
        return self._addressCache.ResolveServiceMask(serviceMask)

    def IsServiceMapped(self, serviceID):
        return bool(1 << serviceID - 1 & self.serviceMask)

    def OnMachoObjectDisconnect(self, objectID, clientID, refID):
        sess = None
        if macho.mode == 'client':
            sess = session
        elif clientID in self.transportIDbyClientID:
            transportID = self.transportIDbyClientID[clientID]
            if transportID in self.transportsByID:
                transport = self.transportsByID[transportID]
                sess = transport.sessions.get(clientID, None)
        if sess is not None:
            sess.UnregisterMachoObject(objectID, refID)

    def ProcessSessionChange(self, isremote, sess, change):
        if 'charid' in change and change['charid'][1] is not None and hasattr(sess, 'clientID'):
            blue.net.MapCharToClient(change['charid'][1], sess.clientID)
        if 'userid' in change and change['userid'][1] is None or 'charid' in change and change['charid'][0] is not None:
            clientID = getattr(sess, 'clientID', 0)
            if not clientID and 'clientID' in change:
                clientID = change['clientID'][0]
            if clientID:
                if clientID in self.transportIDbyClientID and self.transportIDbyClientID[clientID] not in self.transportIDbyProxyNodeID.itervalues() and self.transportIDbyClientID[clientID] not in self.transportIDbySolNodeID.itervalues():
                    transportID = self.transportIDbyClientID[clientID]
                    if 'userid' in change and change['userid'][1] is None:
                        reason = "The user's connection has been usurped on the " + macho.mode
                    else:
                        reason = 'Hot-swapping characters is not permitted'
                    if macho.mode == 'server' and (len(self.transportIDbyProxyNodeID) or len(self.transportIDbySolNodeID)):
                        self.LogError('Usurping node->node connection!?!  Man do I smell deep shit going on here...')
                        self.LogError('Received a session change notification where userID or charID was disappearing.')
                        self.LogError('The session has a clientID(', clientID, "), so we should disconnect it's transport (", transportID, ').')
                        self.LogError("This should be safe, because the transport isn'it a known node->node transport.")
                        self.LogError('However, that is total crud, and we know it, because this is a sol server with proxy connections.')
                        self.LogError("That means there are NO direct client connections, and we've got a situation here.")
                        self.LogError("Here's a stacktrace:")
                        log.LogTraceback()
                        self.LogError("And here's a session dump:")
                        sess.LogSessionError('USURPSERVER')
                        self.LogError("And here's the change we got:")
                        self.LogError('isremote=', isremote)
                        self.LogError('session=', sess)
                        self.LogError('change=', change)
                        self.LogError("and here's some important info")
                        self.LogError('self.transportIDbyClientID=', self.transportIDbyClientID)
                        self.LogError('self.transportIDbyProxyNodeID=', self.transportIDbyProxyNodeID)
                        self.LogError('self.transportIDbySolNodeID=', self.transportIDbySolNodeID)
                        self.LogError('self.transportsByID[transportID]=', self.transportsByID[transportID])
                        self.LogError('Odds are that this server is going down anyway, and an explanation will be found elsewhere')
                    else:
                        uthread.worker('machoNet::DelayedTransportCloseFromProcessSessionChange', self.transportsByID[transportID].Close, reason)
        elif not isremote and 'charid' in change and change['charid'][1] is not None and self.shutdown is not None and self.shutdown.notify is not None and self.shutdown.when - const.HOUR <= blue.os.GetWallclockTime():
            clientID = getattr(sess, 'clientID', 0)
            if not clientID and 'clientID' in change:
                clientID = change['clientID'][1]
            if clientID:
                self.SinglecastByClientID(clientID, 'OnClusterShutdownInitiated', self.shutdown.explanationLabel, self.shutdown.when, self.shutdown.duration)

    def HandleAccept(self, transname, transport, llv):
        transportID = self.transportID
        counter = 0
        try:
            self.transportID = self.transportID + 1
            while not transport.IsClosed():
                if counter > 0:
                    blue.pyos.synchro.SleepWallclock(3000)
                try:
                    sessionID = basesession.GetNewSid()
                    if llv:
                        eveInVIP = self.IsInVIP()
                        llvresponse = transport.HandleClientAuthentication(self.onlineData.get_logon_count(), transportID, counter, sessionID, eveInVIP)
                        counter += 1
                        if not llvresponse or type(llvresponse) is str and llvresponse != 'OK':
                            self.LogError('Low-level version check failure while accepting from ', transport.address, '.  Undoubtedly a handshake request.')
                            continue
                        elif type(llvresponse) is str:
                            self.LogInfo('Finished dealing with accept from ', transport.address, ', probably a queue request')
                            continue
                    if self.stop:
                        return
                    if llv:
                        machoTransport = MachoTransport(transportID, transport, transname, self)
                        self.transportsByID[transportID] = machoTransport
                        transport.SetKeepalive(20, 20)
                        machoTransport.clientID = transport.handShake['user_clientid']
                        machoTransport.userID = transport.handShake['session_init']['userid']
                        machoTransport.sessionID = sessionID
                        blue.net.EnumerateTransport(machoTransport.transport.socket.getSocketDescriptor(), machoTransport.transportID, machoTransport.transportName, machoTransport.userID, machoTransport.clientID, 0)
                        blue.net.AddClient(machoTransport.clientID, machoTransport.transportID)
                        s = basesession.CreateSession(sessionID, const.session.SESSION_TYPE_GAME)
                        if macho.mode == 'proxy':
                            self.session.ConnectToSolServerService('userSvc').ProcessEVESessionCreated(sessionID, transport.address)
                        elif macho.mode == 'server':
                            sm.ChainEvent('ProcessEVESessionCreated', sessionID, transport.address)
                        s.__dict__['clientID'] = machoTransport.clientID
                        llvresponse['session_init']['role'] |= s.role
                        machoTransport.sessions[machoTransport.clientID] = s
                        self.transportIDbyClientID[machoTransport.clientID] = machoTransport.transportID
                        self.add_session_transport_lookup(machoTransport.sessionID, machoTransport.transportID)
                        s.LogSessionHistory('Authenticating user %s via machoNet from address %s' % (llvresponse['user_name'], transport.address))
                        s.SetAttributes(llvresponse['session_init'])
                        s.LogSessionHistory('Authenticated user %s via machoNet from address %s' % (llvresponse['user_name'], transport.address))
                        if not s.role & ROLE_VIPLOGIN:
                            self.LogInfo('non-vip transport', machoTransport, 'has connected, with session', s, 'There are', self.availableLoginSlots, 'login slots remaining')
                            self.availableLoginSlots -= 1
                    else:
                        machoTransport = MachoTransport(transportID, transport, transname, self)
                        self.transportsByID[transportID] = machoTransport
                        blue.net.EnumerateTransport(machoTransport.transport.socket.getSocketDescriptor(), machoTransport.transportID, machoTransport.transportName, 0, 0, 0)
                    machoTransport.currentReaders += 1
                    uthread.worker('machoNet::TransportReader', self.TransportReader, self.transportsByID[transportID])
                except GPSTransportClosed as e:
                    sys.exc_clear()
                except Exception as e:
                    log.LogException()
                    self.LogWarn('Caught %s' % `e`)
                    sys.exc_clear()
                except StandardError:
                    log.LogException()
                    self.LogWarn('Exception in HandleListenTransport')
                    sys.exc_clear()

                return

        finally:
            if llv:
                try:
                    self.RemoveTransportFromLogonQueue(transportID)
                except AttributeError:
                    pass
                except ValueError:
                    pass

    def AcceptLoop(self, transname):
        try:
            listenTransport = self.GetTransport(transname)
            while not getattr(self, 'stop', True):
                try:
                    self.LogInfo('Blocking on accept for ', transname)
                    transport = None
                    transport = listenTransport.Accept()
                    self.LogInfo('Accepted a transport from ', transport.address)
                    uthread.worker('machoNet::HandleAccept', self.HandleAccept, transname, transport, transname != 'tcp:packet:machoNet')
                except GPSTransportClosed:
                    sys.exc_clear()
                    self.LogWarn('ListenTransport closed')
                    return

        except StandardError:
            log.LogException()
            self.LogError('AcceptLoop bombed')
            sys.exc_clear()

    def TransportReader(self, srcTransport):
        srcTransport.currentReaders -= 1
        try:
            while 1:
                if srcTransport.currentReaders > srcTransport.desiredReaders:
                    return
                sys.exc_clear()
                try:
                    theMessage = None
                    msgSession = None
                    theMessage = srcTransport.Read()
                    if srcTransport.currentReaders < srcTransport.desiredReaders:
                        srcTransport.currentReaders += 1
                        uthread.worker('machoNet::TransportReader', self.TransportReader, srcTransport)
                    if theMessage.command == cluster.MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION and macho.mode == 'proxy':
                        destTransports = self._GetTransports(theMessage.destination, srcTransport)
                        if len(destTransports) == 1:
                            destTransport = destTransports[0]
                            if srcTransport.transportName == 'tcp:packet:machoNet':
                                if srcTransport.transportID in destTransport.dependants:
                                    destTransport.dependants[srcTransport.transportID] += 1
                                theMessage.destination = theMessage.source
                                theMessage.source = MachoAddress(clientID=destTransport.clientID)
                                msgSession = destTransport._SessionAndChannelAndIDFromPacket(theMessage)[0]
                                theMessage.sessionVersion = msgSession.receivedVersion
                                msgSession.receivedVersion += 1
                                self.LogInfo('Proxy incremented receivedVersion of session(', msgSession.sid, ') to ', msgSession.receivedVersion)
                                try:
                                    self.HandleMessage(destTransport, theMessage, 1)
                                except StandardError:
                                    self.LogError('MAJOR BORKUPP!!!  This is baaaaddddddd')
                                    log.LogTraceback()
                                    msgSession.LogSessionError('Session state change bombed')
                                    raise

                                msgSession.version += 1
                                self.LogInfo('Proxy incrementing actual session(', msgSession.sid, ")'s version number to ", msgSession.version)
                            else:
                                self.LogError('Funky Session Change packet received, ', theMessage)
                        elif len(destTransports):
                            self.LogError('Received a session change notification destined for ', len(destTransports), ' transports.  packet=', theMessage)
                        else:
                            self.LogWarn('Ignoring non-routable session change notification.  Hopefully a disconnect event? packet=', theMessage)
                    elif theMessage.command % 2:
                        self.HandleMessage(srcTransport, theMessage)
                    else:
                        msgSession = srcTransport._SessionAndChannelAndIDFromPacket(theMessage)[0]
                        theMessage.sessionVersion = msgSession.receivedVersion
                        if theMessage.command in self.__sessioninitorchangenotification__:
                            msgSession.receivedVersion += 1
                            self.LogInfo('Node incremented receivedVersion of session(', msgSession.sid, ') to ', msgSession.receivedVersion)
                            self.HandleMessage(srcTransport, theMessage)
                            msgSession.version += 1
                            self.LogInfo('Node incrementing actual session(', msgSession.sid, ")'s version number to ", msgSession.version)
                        else:
                            self.HandleMessage(srcTransport, theMessage)
                except SessionUnavailable as e:
                    self.LogError('Message abandoned in TransportReader due to unavailable user session')
                    srcTransport.Write(theMessage.ErrorResponse(cluster.MACHONETERR_WRAPPEDEXCEPTION, (DumpsSanitized(RuntimeError(e.payload)),)))
                    sys.exc_clear()
                except UnMachoDestination as e:
                    if theMessage.destination.addressType != const.ADDRESS_TYPE_CLIENT or theMessage.command == cluster.MACHONETMSG_TYPE_CALL_REQ:
                        srcTransport.Write(theMessage.ErrorResponse(cluster.MACHONETERR_UNMACHODESTINATION, e.payload))
                    else:
                        self.LogWarn('Message abandoned in TransportReader due to unroutable destination address, reason=', e.payload)
                        self.LogWarn('Packet=', theMessage)
                    sys.exc_clear()
                except GPSTransportClosed:
                    raise

        except GPSTransportClosed as e:
            srcTransport.Close(**e.GetCloseArgs())
            sys.exc_clear()
        except TaskletExit:
            self.LogInfo('TransportReader is shutting down - tasklet exit command received.')
            sys.exc_clear()
        except StandardError:
            log.LogException()
            srcTransport.Close('TransportReader is shutting down - an unhandled exception has occurred.', 'UNHANDLEDEXCEPTION')
            sys.exc_clear()
        except:
            log.LogException()
            srcTransport.Close('TransportReader shutting down - a bizzarre low level exception has occurred.', 'UNHANDLEDEXCEPTION')
            sys.exc_clear()

    def IsMessageSane(self, srcTransport, theMessage):
        if srcTransport.transportName == 'tcp:packet:client':
            if theMessage.destination.addressType in self.__borc__:
                srcTransport.Close('Client is trying to send C2C')
                return False
            if theMessage.command not in self.__clientallowedcommands__:
                srcTransport.Close('Client is trying to send disallowed commands')
                return False
            if getattr(srcTransport, 'userID', None) is None:
                srcTransport.Close('Client is trying to send over unauthenticated wire, message=%s' % strx(theMessage))
                return False
            if hasattr(srcTransport, 'userID') and srcTransport.userID != theMessage.userID:
                srcTransport.Close('User is trying to spoof another user')
                return False
        elif macho.mode == 'proxy' or macho.mode == 'server':
            if srcTransport.nodeID is None and theMessage.command != cluster.MACHONETMSG_TYPE_IDENTIFICATION_REQ:
                self.LogError('Unidentified or fubarred wire?')
                log.LogTraceback()
                self.LogError('Extra info, tn=', srcTransport.transportName, ', t.node=', srcTransport.nodeID, ', transport=', srcTransport)
                self.LogError('Msg=', theMessage)
                srcTransport.Close('Server or Proxy is trying to send over unidentified wire, message=%s' % strx(theMessage))
                return False
            if macho.mode == 'proxy':
                if srcTransport.nodeID is not None and theMessage.source.addressType == const.ADDRESS_TYPE_NODE and theMessage.source.nodeID != srcTransport.nodeID:
                    if self.ShouldAcceptForwardedMessage(srcTransport, theMessage):
                        pass
                    elif theMessage.command != cluster.MACHONETMSG_TYPE_RESOLVE_RSP:
                        raise RuntimeError('Server is trying to pull a fast one.  source=%s, transport=%s' % (theMessage.source.nodeID, srcTransport.nodeID))
        return True

    __borc__ = (const.ADDRESS_TYPE_BROADCAST, const.ADDRESS_TYPE_CLIENT)
    __aorb__ = (const.ADDRESS_TYPE_ANY, const.ADDRESS_TYPE_BROADCAST)

    @bluepy.TimedFunction('machoNet::HandleMessage')
    def HandleMessage(self, srcTransport, theMessage, skipSanityCheck = 0):
        with IngressTracer(theMessage):
            if theMessage.command in self.__pingrequestorresponse__:
                theMessage.times.append((blue.os.GetWallclockTime(), blue.os.GetWallclockTimeNow(), macho.mode + '::handle_message'))
                theMessage.Changed()
            try:
                if srcTransport.transportID not in self.transportsByID:
                    self.LogWarn("Packet received on a transport that wasn't in transportsByID.  transport=", srcTransport)
                    self.LogWarn('Packet=', theMessage)
                    srcTransport.Close("Packet received on a transport that wasn't in transportsByID")
                    return
                if self.stop:
                    srcTransport.Close('The service is stopping')
                    return
                if not skipSanityCheck:
                    if not self.IsMessageSane(srcTransport, theMessage):
                        return
                if self.callCounterEnabled:
                    try:
                        self.callCounter[theMessage.source.addressType, theMessage.destination.addressType] += 1
                    except Exception as e:
                        self.LogError('Error adding to callCounter', e)
                        sys.exc_clear()

                if theMessage.source.addressType == const.ADDRESS_TYPE_CLIENT and theMessage.source.clientID not in self.transportIDbyClientID:
                    self.transportIDbyClientID[theMessage.source.clientID] = srcTransport.transportID
                    blue.net.AddClient(theMessage.source.clientID, srcTransport.transportID)
                if theMessage.command % 2:
                    if theMessage.destination.addressType in self.__aorb__:
                        srcTransport.Close('A response must be sent to a specific address, not a forking one')
                elif theMessage.source.addressType in self.__aorb__:
                    srcTransport.Close('A request must be sent from a specific address, not a forking one')
                forward = 0
                routesTo = theMessage.RoutesTo(MachoAddress(nodeID=self.nodeID))
                if macho.mode == 'client' or routesTo:
                    if theMessage.command in self.__notificationtypes__:
                        if macho.mode == 'proxy':
                            if theMessage.command == cluster.MACHONETMSG_TYPE_SESSIONCHANGENOTIFICATION:
                                try:
                                    srcTransport.SessionNotification(theMessage)
                                except UnMachoDestination as e:
                                    self.LogInfo('UnMachoDestination encountered while forwarding session change notification: ', e)
                                    sys.exc_clear()

                            elif theMessage.destination.addressType == const.ADDRESS_TYPE_NODE and theMessage.destination.nodeID == self.nodeID:
                                try:
                                    srcTransport.SessionNotification(theMessage)
                                except UnMachoDestination as e:
                                    self.LogInfo('UnMachoDestination encountered while handling a proxy notification: ', e)
                                    sys.exc_clear()

                            elif theMessage.destination.addressType == const.ADDRESS_TYPE_BROADCAST and theMessage.destination.idtype == '+nodeID':
                                try:
                                    srcTransport.SessionNotification(theMessage)
                                except UnMachoDestination as e:
                                    self.LogInfo('UnMachoDestination encountered while handling a proxy broadcast: ', e)
                                    sys.exc_clear()

                            else:
                                if routesTo == 2:
                                    theMessage2 = copy.deepcopy(theMessage)
                                    srcTransport.SessionNotification(theMessage2)
                                forward = 1
                        else:
                            srcTransport.SessionNotification(theMessage)
                    elif theMessage.command in self.__calltypes__:
                        if macho.mode == 'proxy' and not (theMessage.destination.addressType == const.ADDRESS_TYPE_NODE and theMessage.destination.nodeID == self.nodeID):
                            forward = 1
                        else:
                            with IngressTracer.record_process_call_ms():
                                ret = srcTransport.SessionCall(theMessage)
                            if srcTransport.nodeID in self.transportIDbyProxyNodeID:
                                IngressTracer.record_ingress_proxy_id(srcTransport.nodeID)
                            with IngressTracer.record_write_response_ms():
                                srcTransport.Write(ret)
                    elif theMessage.command in self.__responsetypes__ or theMessage.command == cluster.MACHONETMSG_TYPE_PING_RSP and (macho.mode != 'proxy' or theMessage.destination.addressType == const.ADDRESS_TYPE_NODE and theMessage.destination.nodeID == self.nodeID):
                        if self.calls.has_key(theMessage.destination.callID):
                            if self.calls[theMessage.destination.callID][0].balance < 0:
                                self.calls[theMessage.destination.callID][0].send(theMessage)
                            else:
                                self.LogWarn("Call Response received, but the call wasn't being waited upon in self.calls, so the response will disappear... ", theMessage)
                        elif theMessage.command == cluster.MACHONETMSG_TYPE_ERRORRESPONSE and theMessage.originalCommand == cluster.MACHONETMSG_TYPE_NOTIFICATION:
                            self.LogWarn("An error response was received for a notification from us.  Notifcations don't have responses, so this message will disappear... ", theMessage)
                        else:
                            self.LogError('Call Response received on', macho.mode, ", but the call wasn't in self.calls, so the response will disappear... ", theMessage)
                    elif theMessage.command == cluster.MACHONETMSG_TYPE_TRANSPORTCLOSED:
                        srcTransport.SessionClosed(theMessage.clientID, 'Session terminated due to remote transport closed notification', theMessage.isRemote)
                    elif theMessage.command in self.__pingrequestorresponse__:
                        if macho.mode == 'proxy' and not (theMessage.destination.addressType == const.ADDRESS_TYPE_NODE and theMessage.destination.nodeID == self.nodeID):
                            forward = 1
                        elif theMessage.command == cluster.MACHONETMSG_TYPE_PING_REQ:
                            theMessage.times.append((blue.os.GetWallclockTime(), blue.os.GetWallclockTimeNow(), macho.mode + '::turnaround'))
                            theResponse = theMessage.Response(times=theMessage.times[:])
                            srcTransport.Write(theResponse)
                    elif theMessage.command == cluster.MACHONETMSG_TYPE_IDENTIFICATION_REQ:
                        if self.nodeID is None:
                            raise RuntimeError, 'no node ID'
                        if macho.mode == 'server':
                            myaddress = self.GetTransport('tcp:packet:machoNet').GetExternalAddress()
                            others = [ ('%s:%d' % (each.ipAddress, each.port), each.nodeID) for each in self._GetLayTracksTo() ]
                        else:
                            myaddress = self.GetTransport('tcp:packet:machoNet').GetInternalAddress()
                            others = []
                        if self.transportIDbyProxyNodeID.has_key(theMessage.nodeID) or self.transportIDbySolNodeID.has_key(theMessage.nodeID):
                            self.LogWarn('Rejecting connection attempt from ', theMessage.nodeID, ' because I already have such a connection')
                            response = (False, 'I already have a socket for this node')
                        elif theMessage.nodeID in self.dontLayTracksTo and theMessage.nodeID > self.nodeID:
                            self.LogInfo('Rejecting connection attempt from ', theMessage.nodeID, ' because I was already establishing such a connection, and I have priority', self.nodeID, 'vs.', theMessage.nodeID)
                            response = (False, 'I am already connecting to this node')
                        else:
                            self.LogInfo('Accepting connection from ', theMessage.nodeID)
                            response = (True, 'OK')
                        if response[0]:
                            srcTransport.nodeID = theMessage.nodeID
                            blue.net.SetTransportNodeID(srcTransport.transportID, theMessage.nodeID)
                            if theMessage.isProxy:
                                thedict = self.transportIDbyProxyNodeID
                            elif theMessage.isApp:
                                thedict = self.transportIDbyAppNodeID
                            else:
                                thedict = self.transportIDbySolNodeID
                            thedict[theMessage.nodeID] = srcTransport.transportID
                            try:
                                isApp = self.nodeID in self.transportIDbyAppNodeID
                                srcTransport.Write(theMessage.Response(response, self.nodeID, others, macho.mode == 'proxy', isApp, self.serviceMask))
                            except:
                                del thedict[theMessage.nodeID]
                                raise

                            self.externalAddressesByNodeID[theMessage.nodeID] = (theMessage.myaddress, theMessage.serviceMask)
                            if self.clusterStartupPhase:
                                if macho.mode == 'proxy':
                                    polarisID = self.session.ConnectToSolServerService('machoNet').GetNodeFromAddress(cluster.SERVICE_POLARIS, 0)
                                else:
                                    polarisID = self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0)
                                isPolaris = theMessage.nodeID == polarisID
                                sm.ScatterEvent('OnNewNode', theMessage.nodeID, theMessage.myaddress, theMessage.isProxy, isPolaris, theMessage.serviceMask)
                        else:
                            isPolaris = macho.mode == 'server' and self.GetNodeID() == self.GetNodeFromAddress(cluster.SERVICE_POLARIS, 0)
                            isApp = self.nodeID in self.transportIDbyAppNodeID
                            srcTransport.Write(theMessage.Response(response, self.nodeID, others, macho.mode == 'proxy', isApp, self.serviceMask))
                            srcTransport.Close(response[1], noSend=True)
                        others = list(theMessage.others)
                        random.shuffle(others)
                        for otherAddress, otherNodeID in others:
                            self.LayTracksIfNeeded(otherAddress, otherNodeID, 'IdentificationReq.others')

                    else:
                        srcTransport.Close('Command %d is not allowed at this node' % theMessage.command)
                else:
                    forward = 1
                if forward:
                    if macho.mode != 'proxy':
                        self.LogError('TransportReader is rejecting the message violently')
                        srcTransport.Close("Client and server nodes do not forward packets.  Something's wrong, dude.")
                        return
                    try:
                        destTransports = self._GetTransports(theMessage.destination, srcTransport)
                        if theMessage.destination.addressType == const.ADDRESS_TYPE_BROADCAST and macho.mode == 'proxy':
                            theMessage.destination.narrowcast = []
                            theMessage.Changed()
                        for each in destTransports:
                            self.FragileWrite(each, theMessage)

                    except UnMachoDestination as e:
                        if theMessage.destination.addressType != const.ADDRESS_TYPE_CLIENT or theMessage.command == cluster.MACHONETMSG_TYPE_CALL_REQ:
                            srcTransport.Write(theMessage.ErrorResponse(cluster.MACHONETERR_UNMACHODESTINATION, e.payload))
                        else:
                            self.LogWarn('Message abandoned due to unroutable destination address, reason=', e.payload)
                            self.LogWarn('Packet=', theMessage)
                        sys.exc_clear()

            except GPSTransportClosed as e:
                srcTransport.Close('Connected transport closed')
                sys.exc_clear()
                return
            except StandardError:
                log.LogException('TransportReader standard error')
                if srcTransport.transportName == 'tcp:packet:client':
                    srcTransport.Close('TransportReader blew up', 'UNHANDLEDEXCEPTION')
                else:
                    self.LogError('Playing chicken with a freight train, eh?  Sorry dude, but the show must go on...')
                sys.exc_clear()
            except:
                log.LogException('TransportReader non-standard error')
                srcTransport.Close('TransportReader blew up - non-standard error', 'UNHANDLEDEXCEPTION')
                raise

    def ShouldAcceptForwardedMessage(self, transport, theMessage):
        if transport.nodeID in self.transportIDbyAppNodeID:
            return True
        return False

    @bluepy.TimedFunction('machoNet::FragileWrite')
    def FragileWrite(self, destTransport, message):
        try:
            if message.command in self.__pingrequestorresponse__:
                message.times.append((blue.os.GetWallclockTime(), blue.os.GetWallclockTimeNow(), macho.mode + '::writing'))
                message.Changed()
            destTransport.Write(message)
        except GPSTransportClosed as e:
            destTransport.Close('Wrote packet on a closed socket.  Close reason was: ' + strx(e.reason))
            sys.exc_clear()
        except StandardError:
            self.LogWarn("Write died of natural or bizzarre causes.  Could be natural.  Could be bizzarre.  Here's a trace:")
            log.LogException()
            destTransport.Close('Write died of natural or bizzarre causes.')
            sys.exc_clear()
        except:
            destTransport.Close('Write died of natural or bizzarre causes, probably shutdown.')
            raise

    def GetProxyNodeIDFromClientID(self, clientID):
        try:
            proxyNodeID = clientID % 10000000000L
        except TypeError as e:
            raise UnMachoDestination('%s is not a valid clientID' % repr(clientID))

        if macho.mode == 'server' and proxyNodeID not in self.transportIDbyProxyNodeID:
            raise UnMachoDestination('The proxy node in question is not reachable')
        return proxyNodeID

    def GetIDOfAddress(self, address, clientMode = True, customIDData = None):
        ipaddr, port = address.split(':')
        ipaddr = GetPreferredHostByName(ipaddr)
        x = ipaddr.split('.')
        if clientMode:
            t = self.clientIDOffset
            self.clientIDOffset += 1
            return t * 10000000000L + self.nodeID
        elif customIDData:
            basePort, portOffset, idRangeBase = customIDData
            hops = (int(port) - basePort - portOffset) / 1000
            if hops < 0:
                log.LogTraceback('hops (orchestrator agent) fuxx0red')
                self.LogError('How is this even related to orchestrator?')
                self.LogError('hops: ', hops)
                self.LogError('port: ', port)
                self.LogError('om: ', offsetMap[macho.mode]['tcp:packet:machoNet'])
            return idRangeBase + int(x[3]) + hops * 1000
        else:
            hops = (int(port) - self.defaultProxyPortOffset - offsetMap[macho.mode]['tcp:packet:client']) / 1000
            if hops < 0:
                log.LogTraceback('hops fuxx0red')
                self.LogError('hops: ', hops)
                self.LogError('port: ', port)
                self.LogError('dpopo: ', self.defaultProxyPortOffset)
                self.LogError('om: ', offsetMap[macho.mode]['tcp:packet:client'])
            return 1000000000 + int(x[3]) + hops * 1000

    def SetStatusKeyValuePair(self, key, value):
        self.statusData[key] = value

    def SetStatusCallBack(self, key, function):
        self.statusCallbacks[key] = function

    def StatusSocketLoop(self):
        try:
            self.LogInfo('Starting status socket')
            statusSocket = socket.socket()
            statusSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port = self.basePortNumber + offsetMap[macho.mode]['tcp:raw:status']
            statusSocket.bind(('', port))
            statusSocket.listen(socket.SOMAXCONN)
            while True:
                try:
                    self._SendStatus(statusSocket)
                except:
                    log.LogException('Status socket loop threw an exception')

        except:
            log.LogException('Status socket threw and exception, and is now stopping')

    def _SendStatus(self, statusSocket):
        s, address = statusSocket.accept()
        self.LogInfo('Sending server status to %s', address)
        data = {}
        data.update(self.statusData)
        stackless.current.block_trap = True
        for key, function in self.statusCallbacks.iteritems():
            try:
                data[key] = function()
            except:
                log.LogException('Callback function for key %s failed', key)

        stackless.current.block_trap = False
        s.send('%s %s\r\n\r\n%s' % ('HTTP/1.0', '200', json.dumps(data)))
        s.close()

    def ForwardProxyBroadcast(self, *args):
        self.ProxyBroadcast(*args)

    def ForwardSinglecastByCharID(self, *args):
        self.SinglecastByCharID(*args)

    def GetRuntimeDetails(self):
        proxy_macho_net = self.session.ConnectToProxyServerService('machoNet')
        connectionProps = proxy_macho_net.GetConnectionProperties()
        vip_mode = connectionProps['vipMode']
        online_players = self.onlineData.get_logon_count()
        build_number = boot.build
        return {'players': online_players,
         'vip': vip_mode,
         'build': build_number,
         'start_time': blue.sysinfo.processStartTime}

    def GetConnectedClusterName(self):
        if monolithconfig.on_client():
            proxy_macho_net = self.session.ConnectToProxyServerService('machoNet')
            return proxy_macho_net.GetConnectedClusterName()
        return prefs.clusterName

    def GetConnectedClusterMode(self):
        if monolithconfig.on_client():
            proxy_macho_net = self.session.ConnectToProxyServerService('machoNet')
            return proxy_macho_net.GetConnectedClusterMode()
        return prefs.clusterMode


def WhitelistDumper():
    while True:
        f = file('wl.txt', 'wt')
        vals = blue.marshal.globalsWhitelist.values()
        vals.sort()
        for v in vals:
            print >> f, v[0] + '.' + v[1]

        f.close()
        blue.pyos.synchro.SleepWallclock(5000)


def CollectWhitelist():
    blue.marshal.globalsWhitelist = {}
    blue.marshal.collectWhitelist = True
    uthread.new(WhitelistDumper)


def RegisterPortOffset(mapname, portOffset, modeRoleBootMacho = None):
    if modeRoleBootMacho is None:
        modeRoleBootMacho = boot.role
    offsetMap[modeRoleBootMacho][mapname] = portOffset


def GetPreferredHostByName(name):
    addressList = socket.gethostbyname_ex(name)[2]
    lookingFor = PREFERRED_SUBNETWORKS.get(macho.mode, DEFAULT_SUBNETWORK)
    for address in addressList:
        if address.startswith(lookingFor):
            return address

    if addressList:
        return addressList[0]


def CreateInstance(cls, arguments = ()):
    instance = cls(*arguments)
    for each in getattr(instance, '__persistvars__', []):
        if not hasattr(instance, each):
            setattr(instance, each, None)

    for each in getattr(instance, '__nonpersistvars__', []):
        if not hasattr(instance, each):
            setattr(instance, each, None)

    return instance


mode = boot.role
