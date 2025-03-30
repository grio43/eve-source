#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\net\eveMachoNet.py
import sys
from collections import defaultdict
from itertools import ifilter
import carbon.common.script.net.machoNet as macho
import log
from carbon.common.script.net.machoNet import MachoNetService
from carbon.common.script.sys import basesession
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from cluster import SERVICE_BEYONCE, SERVICE_CHATX, SERVICE_STATION, SERVICE_PLANETMGR, SERVICE_POLARIS
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
from eveexceptions import ExceptionEater
from eveprefs import prefs, boot
from stringutil import strx

class EveMachoNetService(macho.MachoNetService):
    __guid__ = 'svc.eveMachoNet'
    __replaceservice__ = 'machoNet'
    __startupdependencies__ = MachoNetService.__startupdependencies__
    if boot.role in ('server', 'proxy'):
        __startupdependencies__.extend(['eventLog'])
    __gpcsmethodnames__ = {'Broadcast',
     'ClusterBroadcast',
     'ConnectToAllNeighboringServices',
     'ConnectToAllServices',
     'ConnectToAllSiblingServices',
     'ConnectToRemoteService',
     'NarrowcastByAllianceIDs',
     'NarrowcastByCharIDs',
     'NarrowcastByClientIDs',
     'NarrowcastByClientIDsWithoutTheStars',
     'NarrowcastByCorporationIDs',
     'NarrowcastByFleetIDs',
     'NarrowcastByNodeIDs',
     'NarrowcastByShipIDs',
     'NarrowcastBySolarSystemID2s',
     'NarrowcastBySolarSystemIDs',
     'NarrowcastByStationIDs',
     'NarrowcastByStructureIDs',
     'NarrowcastByUserIDs',
     'SinglecastByServiceMask',
     'NodeBroadcast',
     'Objectcast',
     'ObjectcastWithoutTheStars',
     'OnObjectPublicAttributesUpdated',
     'ProxyBroadcast',
     'Queuedcast',
     'QueuedcastWithoutTheStars',
     'ReliableSinglecastByCharID',
     'ReliableSinglecastByUserID',
     'RemoteServiceCall',
     'RemoteServiceCallWithoutTheStars',
     'RemoteServiceNotify',
     'RemoteServiceNotifyWithoutTheStars',
     'ResetAutoResolveCache',
     'Scattercast',
     'ScattercastWithoutTheStars',
     'ServerBroadcast',
     'SinglecastByAllianceID',
     'SinglecastByRegionID',
     'SinglecastByCharID',
     'SinglecastByClientID',
     'SinglecastByCorporationID',
     'SinglecastByFleetID',
     'SinglecastByNodeID',
     'SinglecastByShipID',
     'SinglecastBySolarSystemID',
     'SinglecastBySolarSystemID2',
     'SinglecastByStationID',
     'SinglecastByStructureID',
     'SinglecastByUserID'}
    __server_scattercast_session_variables__ = {'userid',
     'charid',
     'shipid',
     'objectID',
     'fleetid',
     'wingid',
     'squadid'}
    __notifyevents__ = MachoNetService.__notifyevents__
    __notifyevents__.add('OnGlobalConfigChanged')
    MachoNetService.metricsMap.update({'EVE:Online': const.zmetricCounter_EVEOnline,
     'EVE:Trial': const.zmetricCounter_EVETrial})

    def __init__(self):
        MachoNetService.__init__(self)
        self.logAllClientCalls = prefs.GetValue('logAllClientCalls', None)
        self.clientCallLogChannel = log.Channel(str(macho.mode), 'ClientCalls')
        self.sessionWatchIDs = None
        try:
            self.sessionWatchIDs = ({int(s) for s in strx(prefs.GetValue('sessionWatch_userID', '')).split(',') if s},
             {int(s) for s in strx(prefs.GetValue('sessionWatch_charID', '')).split(',') if s},
             {int(s) for s in strx(prefs.GetValue('sessionWatch_corpID', '')).split(',') if s},
             {int(s) for s in strx(prefs.GetValue('sessionWatch_userType', '')).split(',') if s})
            if len(self.sessionWatchIDs[0]) == 0 and len(self.sessionWatchIDs[1]) == 0 and len(self.sessionWatchIDs[2]) == 0 and len(self.sessionWatchIDs[3]) == 0:
                self.sessionWatchIDs = None
        except:
            log.LogException()
            sys.exc_clear()

        self.clusterSolarsystemStatistics = ({}, {}, 0)
        self.clusterSolarsystemStatisticsForClient = ({}, {}, 0)

    def Run(self, memStream = None):
        super(EveMachoNetService, self).Run(memStream)
        if macho.mode == 'server' and self.connectToCluster:
            self.dbzuser = self.DB2.GetSchema('zuser')
        if macho.mode in ('server', 'proxy') and prefs.GetValue('seclogEnabled', False):
            self.eventLog.SetupChannel('security', {'persistInterval': 1000,
             'logPath': prefs.GetValue('seclogPath', 'c:\\seclog'),
             'maxEvents': 10000000,
             'maxEventLength': 100000,
             'delimeter': '\\t',
             'logFileNameFormat': 'seclog_%(dateTime)s_%(nodeID)s.txt',
             'logFileCycleMinutes': 5})

    def GetClusterGameStatistics(self, key, default):
        if key == 'EVE':
            return self.clusterSolarsystemStatistics
        else:
            return default

    def GetClusterGameStatisticsForClient(self, key, default):
        if key == 'EVE':
            return self.clusterSolarsystemStatisticsForClient
        else:
            return default

    def SetClusterSessionCounts(self, clusterSessionStatistics):
        if clusterSessionStatistics is not None:
            self._AddToSessionCounter(clusterSessionStatistics)
            if len(self.clusterSessionStatsHistory) == self.proxyStatSmoothie:
                oldestStatistics = self.clusterSessionStatsHistory[0][1]
                self._RemoveFromSessionCounter(oldestStatistics)
            numSamples = min(self.proxyStatSmoothie, len(self.clusterSessionStatsHistory) + 1)
            sol, station, c = self.clusterSolarsystemStatistics
            self.clusterSolarsystemStatistics = (sol, station, numSamples)
            self.SetClientSafeStatistics(sol, station, numSamples)
        MachoNetService.SetClusterSessionCounts(self, clusterSessionStatistics)

    def SetClientSafeStatistics(self, sol, station, numSamples):
        newSol = {}
        newStation = {}
        for counterDictionary, newDictionary in ((sol, newSol), (station, newStation)):
            for eachSolarsystemShortID, value in counterDictionary.iteritems():
                solarSystemID = eachSolarsystemShortID + 30000000
                if IsKnownSpaceSystem(solarSystemID):
                    newDictionary[eachSolarsystemShortID] = value

        self.clusterSolarsystemStatisticsForClient = (newSol, newStation, numSamples)

    def _AddToSessionCounter(self, statisticsToUse):
        self._AddOrRemoveFromCounter(statisticsToUse, modifier=1)

    def _RemoveFromSessionCounter(self, statisticsToUse):
        self._AddOrRemoveFromCounter(statisticsToUse, modifier=-1)

    def _AddOrRemoveFromCounter(self, statisticsToUse, modifier):
        sol, station, c = self.clusterSolarsystemStatistics
        if 'solarsystemid2' in statisticsToUse:
            solarsystemidCounts = self._GetSessionVariableCountsBySolarSystem(statisticsToUse, 'solarsystemid')
            dockedInStructuresBySolarSystemID = self.GetDockedInStructuresBySolarSystemID(statisticsToUse)
            for solarsystemid, solarsystemid2Count in self._GetSessionVariableCountsBySolarSystem(statisticsToUse, 'solarsystemid2').iteritems():
                solID = solarsystemid - 30000000
                sol[solID] = sol.get(solID, 0) + modifier * solarsystemid2Count
                numInSpaceOrStructure = solarsystemidCounts.get(solarsystemid, 0)
                numInSpace = numInSpaceOrStructure - dockedInStructuresBySolarSystemID.get(solarsystemid, 0)
                stationCount = solarsystemid2Count - numInSpace
                if stationCount > 0:
                    station[solID] = station.get(solID, 0) + modifier * stationCount

    def GetDockedInStructuresBySolarSystemID(self, clusterSessionStatistics):
        structureidCounts = self._GetSessionVariableCountsBySolarSystem(clusterSessionStatistics, 'structureid')
        dockedInStructuresBySolarSystemID = defaultdict(int)
        for eachStructureID, count in structureidCounts.iteritems():
            try:
                structureLocation = cfg.evelocations.Get(eachStructureID)
                dockedInStructuresBySolarSystemID[structureLocation.solarSystemID] += count
            except KeyError:
                pass

        return dockedInStructuresBySolarSystemID

    def _GetSessionVariableCountsBySolarSystem(self, statisticsToUse, sessionVariable):
        if sessionVariable in statisticsToUse:
            return statisticsToUse[sessionVariable][1]
        else:
            return {}

    def _StoreMetricsToDB(self, metrics):
        try:
            MachoNetService._StoreMetricsToDB(self, metrics)
            onlineCount = metrics['EVE:Online'][0] if 'EVE:Online' in metrics else 0
            trialCount = metrics['EVE:Trial'][0] if 'EVE:Trial' in metrics else 0
            onlineCount2 = 0
            trialCount2 = 0
            self.dbzuser.OnlineCounts_Insert(onlineCount, trialCount, onlineCount2, trialCount2)
        except StandardError:
            log.LogException()
            sys.exc_clear()
        except:
            log.LogException()
            raise

    def _GetNodeFromAddressFromDB(self, myNodeID, serviceMapping, address, suggestedNodeID, expectedLoadValue, serviceMask):
        if serviceMapping == SERVICE_BEYONCE and (address < const.minSolarSystem or address > const.maxSolarSystem):
            raise RuntimeError('Address is not a solar system (%s)' % address)
        return MachoNetService._GetNodeFromAddressFromDB(self, myNodeID, serviceMapping, address, suggestedNodeID, expectedLoadValue, serviceMask)

    def GuessNodeIDFromAddress(self, serviceName, address):
        return
        alternatives = []
        if serviceName in ('aggressionMgr', 'director', 'entity'):
            alternatives = [('beyonce', address)]
            for each in ('aggressionMgr', 'director', 'entity'):
                alternatives.append((each, address))

        elif serviceName == 'brokerMgr':
            alternatives = [('station', address)]
        elif serviceName in ('i2', 'dogmaIM', 'invbroker', 'ship'):
            if address[1] == const.groupSolarSystem:
                alternatives = [('beyonce', address[0])]
            elif address[1] == const.groupStation:
                alternatives = [('station', address[0])]
            for each in ('i2', 'dogmaIM', 'invbroker', 'ship'):
                alternatives.append((each, address))

        elif serviceName in ('corpStationMgr', 'factory', 'broker'):
            alternatives = [('station', address)]
        elif serviceName == 'tradeMgr':
            alternatives = [('station', address[0])]
        elif serviceName == 'station' and macho.mode == 'server':
            try:
                key = ('beyonce', sm.services['stationSvc'].GetStation(address, prime=0).solarSystemID)
                if key[1]:
                    alternatives.append(key)
            except StandardError:
                log.LogException('Could not locate the station you asked for without blocking')
                sys.exc_clear()

        for alt_service, alt_address in alternatives:
            nodeID = self._addressCache.GetByServiceAddress(alt_service, alt_address)
            if nodeID is not None:
                self._addressCache.SetServiceAddress(serviceName, address, nodeID)
                return nodeID

    def _GetNodeFromAddressAdjustments(self, service, address):
        if macho.mode == 'server' and service == SERVICE_STATION:
            if address == const.doomheimStationID:
                log.LogWarn('Getting node address for Doomheim station [%s].' % const.doomheimStationID)
                stationAddress = const.eveUniverseLocationID
            else:
                try:
                    stationAddress = sm.StartService('stationSvc').GetStation(address).solarSystemID
                except StandardError:
                    log.LogException()
                    raise RuntimeError('The station you asked for does not reside in any known solar system')

            key = (SERVICE_BEYONCE, stationAddress)
            service, address = key
        suggestedNodeID = None
        if service in ('beyonce', SERVICE_BEYONCE) and int(address) == 30000380:
            suggestedNodeID = self.GetNodeFromAddress(SERVICE_POLARIS, 0)
        if service in ('planetMgr', SERVICE_PLANETMGR):
            address = address % const.PLANETARYMGR_MOD
        return (suggestedNodeID, service, address)

    def _GetTransportIDsFromBroadcastAddress(self, address):
        if address.idtype is None:
            idtype = None
            scattered = 0
        elif address.idtype[0] in ('*', '+'):
            idtype = address.idtype[1:]
            scattered = 1
        else:
            idtype = address.idtype
            scattered = 0
        if len(address.narrowcast):
            clientIDs = []
            nodeIDs = []
            done = 0
            if idtype == 'clientID':
                if macho.mode == 'server' and len(address.narrowcast) >= 2 * len(self.transportIDbyProxyNodeID):
                    nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                else:
                    clientIDs = address.narrowcast
                done = 1
            elif idtype == 'nodeID':
                nodeIDs = address.narrowcast
                done = 1
            elif idtype == 'serviceMask':
                nodeIDs = self.ResolveServiceMaskToNodeIDs(address.narrowcast[0])
                done = 1
            elif macho.mode == 'server':
                if idtype in self.__server_scattercast_session_variables__:
                    if scattered:
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                elif len(address.narrowcast) == 1:
                    if idtype == 'stationid':
                        nodeID = self.CheckAddressCache(SERVICE_STATION, address.narrowcast[0], lazyGetIfNotFound=True)
                        if self.GetNodeID() == nodeID:
                            if scattered:
                                self.LogInfo('Scattercasting by stationID on the right node.  Ignored.')
                        else:
                            self.LogWarn('Sending a packet by stationid on the wrong node.  Resorting to a scattercast.')
                            self.LogWarn('nodeID: ', nodeID, ', my nodeID: ', self.GetNodeID(), ', stationID: ', address.narrowcast[0])
                            nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                            done = 1
                    elif idtype in ('solarsystemid', 'solarsystemid2'):
                        nodeID = self.CheckAddressCache(SERVICE_BEYONCE, address.narrowcast[0], lazyGetIfNotFound=True)
                        if self.GetNodeID() == nodeID:
                            if scattered:
                                self.LogInfo('Scattercasting by solarsystemid on the right node.  Ignored.')
                        else:
                            self.LogWarn('Sending a packet by solarsystemid on the wrong node.  Resorting to a scattercast.')
                            self.LogWarn('nodeID: ', nodeID, ', my nodeID: ', self.GetNodeID(), ', solarsystemid(2): ', address.narrowcast[0])
                            nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                            done = 1
                    elif idtype == 'corpid':
                        nodeID = self.CheckAddressCache(SERVICE_CHATX, address.narrowcast[0] % 200, lazyGetIfNotFound=True)
                        if self.GetNodeID() == nodeID:
                            if scattered:
                                self.LogInfo('Scattercasting by corpid on the right node.  Ignored.')
                        else:
                            self.LogWarn('Sending a packet by corpid on the wrong node.  Resorting to a scattercast.')
                            self.LogWarn('nodeID: ', nodeID, ', my nodeID: ', self.GetNodeID(), ', corpID: ', address.narrowcast[0])
                            nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                            done = 1
                    elif idtype == 'allianceid':
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                    elif idtype == 'regionid':
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                    elif idtype == 'structureid':
                        try:
                            solarSystemID = cfg.evelocations.Get(address.narrowcast[0]).solarSystemID
                        except AttributeError:
                            solarSystemID = sm.GetService('structureDirectory').GetStructureInfo_(address.narrowcast[0]).solarSystemID

                        nodeID = self.CheckAddressCache(SERVICE_BEYONCE, solarSystemID, lazyGetIfNotFound=True)
                        if self.GetNodeID() == nodeID:
                            if scattered:
                                self.LogInfo('Scattercasting by solarsystemid on the right node.  Ignored.')
                        else:
                            self.LogWarn('Sending a packet by structureid on the wrong node.  Resorting to a scattercast.')
                            self.LogWarn('nodeID: ', nodeID, ', my nodeID: ', self.GetNodeID(), ', structureid: ', address.narrowcast[0], 'solarSystemID: ', solarSystemID)
                            nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                            done = 1
                    else:
                        self.LogWarn('Sending a packet by some funky address type (', idtype, ').  Resorting to scattercast')
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                elif idtype == 'corpid&corprole' and len(address.narrowcast[0]) == 1:
                    nodeID = self.CheckAddressCache(SERVICE_CHATX, address.narrowcast[0][0] % 200, lazyGetIfNotFound=True)
                    if self.GetNodeID() == nodeID:
                        if scattered:
                            self.LogInfo('Scattercasting by corpid&corprole on the right node.  Ignored.')
                    else:
                        self.LogWarn('Sending a packet by corpid&corprole on the wrong node.  Resorting to a scattercast.')
                        self.LogWarn('nodeID: ', nodeID, ', my nodeID: ', self.GetNodeID(), ', corpID: ', address.narrowcast[0][0])
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                elif idtype in ('stationid&corpid&corprole', 'stationid&corpid') and len(address.narrowcast[0]) == 1 and len(address.narrowcast[1]) == 1:
                    stationNodeID = self.CheckAddressCache(SERVICE_STATION, address.narrowcast[0][0], lazyGetIfNotFound=True)
                    corpNodeID = self.CheckAddressCache(SERVICE_CHATX, address.narrowcast[1][0] % 200, lazyGetIfNotFound=True)
                    if self.GetNodeID() in (stationNodeID, corpNodeID):
                        if scattered:
                            self.LogInfo('Scattercasting by stationid&corpid&corprole on the station node or corp node.  Ignored.')
                    else:
                        self.LogWarn('Sending a packet by stationid&corpid&corprole on the wrong node.  Resorting to a scattercast.')
                        self.LogWarn('corpNodeID: ', corpNodeID, ', stationNodeID: ', stationNodeID, ', my nodeID: ', self.GetNodeID(), ', corpID: ', address.narrowcast[1][0], ', stationID: ', address.narrowcast[0][0])
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                elif idtype == 'corpid&corprole&solarsystemid' and len(address.narrowcast[0]) == 1 and len(address.narrowcast[2]) == 1:
                    solNodeID = self.CheckAddressCache(SERVICE_BEYONCE, address.narrowcast[2][0], lazyGetIfNotFound=True)
                    corpNodeID = self.CheckAddressCache(SERVICE_CHATX, address.narrowcast[0][0] % 200, lazyGetIfNotFound=True)
                    if self.GetNodeID() in (solNodeID, corpNodeID):
                        if scattered:
                            self.LogInfo('Scattercasting by corpid&corprole&solarsystemid on the solarsystem node or corp node.  Ignored.')
                    else:
                        self.LogWarn('Sending a packet by corpid&corprole&solarsystemid on the wrong node.  Resorting to a scattercast.')
                        self.LogWarn('corpNodeID: ', corpNodeID, ', solNodeID: ', solNodeID, ', my nodeID: ', self.GetNodeID(), ', corpID: ', address.narrowcast[0][0], ', solarsystemID: ', address.narrowcast[2][0])
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                elif idtype in ('corpid&solarsystemid', 'solarsystemid&corpid') and len(address.narrowcast[0]) == 1 and len(address.narrowcast[1]) == 1:
                    if idtype == 'solarsystemid&corpid':
                        idxSol = 0
                        idxCorp = 1
                    else:
                        idxSol = 1
                        idxCorp = 0
                    solNodeID = self.CheckAddressCache(SERVICE_BEYONCE, address.narrowcast[idxSol][0], lazyGetIfNotFound=True)
                    corpNodeID = self.CheckAddressCache(SERVICE_CHATX, address.narrowcast[idxCorp][0] % 200, lazyGetIfNotFound=True)
                    if self.GetNodeID() in (solNodeID, corpNodeID):
                        if scattered:
                            self.LogInfo('Scattercasting by corpid&corprole&solarsystemid on the solarsystem node or corp node.  Ignored.')
                    else:
                        self.LogWarn('Sending a packet by corpid&corprole&solarsystemid on the wrong node.  Resorting to a scattercast.')
                        self.LogWarn('corpNodeID: ', corpNodeID, ', solNodeID: ', solNodeID, ', my nodeID: ', self.GetNodeID(), ', corpID: ', address.narrowcast[idxCorp][0], ', solarsystemID: ', address.narrowcast[idxSol][0])
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                        done = 1
                elif idtype == 'allianceid&corprole':
                    nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                    done = 1
                else:
                    if not scattered:
                        self.LogWarn('Sending a packet via a non-scattered complex address that resorts to a scattercast.  address: ', address)
                    else:
                        self.LogInfo('Sending a packet via a scattered complex address.  address: ', address)
                    nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                    done = 1
            if not done:
                notfound = []
                if len(address.narrowcast) == 1 and (idtype, address.narrowcast[0]) in self.spam:
                    spam = 1
                elif macho.mode == 'server':
                    if self.transportIDbyProxyNodeID:
                        spam, clientIDs, notfound = basesession.FindClientsAndHoles(idtype, address.narrowcast, len(self.transportIDbyProxyNodeID) * 2)
                    else:
                        spam, clientIDs, notfound = basesession.FindClientsAndHoles(idtype, address.narrowcast, 20)
                else:
                    spam, clientIDs, notfound = basesession.FindClientsAndHoles(idtype, address.narrowcast, None)
                if len(address.narrowcast) == 1 and spam:
                    self.LogInfo('Interpreting ', address.narrowcast, ' as a persistant spam address.')
                    if len(self.spam) > 1000:
                        self.spam.clear()
                    self.spam.add((idtype, address.narrowcast[0]))
                if spam or macho.mode == 'server' and address.idtype[0] == '*' and len(notfound):
                    clientIDs = []
                    if macho.mode == 'server':
                        nodeIDs = self.transportIDbyProxyNodeID.iterkeys()
                    else:
                        nodeIDs = self.transportIDbySolNodeID.iterkeys()
            transportIDs = set()
            if macho.mode == 'server' and self.transportIDbyProxyNodeID:
                for clientID in ifilter(None, clientIDs):
                    try:
                        nodeID = self.GetProxyNodeIDFromClientID(clientID)
                    except Exception as e:
                        self.LogWarn('Unable to map clientID', repr(clientID), 'to proxyID. Dropping message Exception type=', type(e), ' args=', e.args)
                        continue

                    if nodeID in self.transportIDbyProxyNodeID:
                        transportIDs.add(self.transportIDbyProxyNodeID[nodeID])
                        if len(transportIDs) == len(self.transportIDbyProxyNodeID):
                            if len(transportIDs) > 2:
                                self.LogInfo('All proxies targeted in a clientID based routing decision. If this happens frequently, the caller might consider a better casting method.', address)
                            break

            else:
                for each in clientIDs:
                    if self.transportIDbyClientID.has_key(each) and self.transportsByID.has_key(self.transportIDbyClientID[each]):
                        transportIDs.add(self.transportIDbyClientID[each])
                    else:
                        self.LogInfo('Transport for client ', each, ' not found while sending narrowcast.')

            for nodeId in nodeIDs:
                if macho.mode == 'server' and nodeId in self.transportIDbyProxyNodeID and self.transportIDbyProxyNodeID[nodeId] in self.transportsByID:
                    transportIDs.add(self.transportIDbyProxyNodeID[nodeId])
                elif macho.mode == 'proxy' and nodeId in self.transportIDbySolNodeID and self.transportIDbySolNodeID[nodeId] in self.transportsByID:
                    transportIDs.add(self.transportIDbySolNodeID[nodeId])
                elif nodeId in self.transportIDbyAppNodeID and self.transportIDbyAppNodeID[nodeId] in self.transportsByID:
                    transportIDs.add(self.transportIDbyAppNodeID[nodeId])
                elif nodeId in self.transportIDbySolNodeID and self.transportIDbySolNodeID[nodeId] in self.transportsByID:
                    transportIDs.add(self.transportIDbySolNodeID[nodeId])
                else:
                    self.LogInfo('Transport for node ', nodeId, ' not found while sending narrowcast.')

            transportIDs = list(transportIDs)
        elif idtype == 'nodeID':
            if address.idtype[0] == '+':
                transportIDs = self.transportIDbyProxyNodeID.values()
            else:
                transportIDs = self.transportIDbySolNodeID.values()
        elif macho.mode == 'server':
            transportIDs = self.transportsByID.keys()
        else:
            transportIDs = self.transportIDbyClientID.values()
        if transportIDs:
            self.broadcastsResolved.Add(len(transportIDs))
        else:
            self.broadcastsMissed.Add()
        return transportIDs

    def OnGlobalConfigChanged(self, config):
        if 'oldShutdown' in config:
            val = int(config['oldShutdown'])
            self.LogNotice('Setting oldShutdown to', val)
            prefs.SetValue('oldShutdown', val)
        settings = {}
        if 'stacklessioVersion' in config:
            settings['version'] = int(config['stacklessioVersion'])
        if 'stacklessioUseNoblock' in config:
            settings['useNoblock'] = bool(config['stacklessioUseNoblock'])
        if 'stacklessioAllocChunkSize' in config:
            settings['allocChunkSize'] = int(config['stacklessioAllocChunkSize'])
        if settings:
            import stacklessio._socket
            stacklessio._socket.apply_settings(settings)
            self.LogNotice('Applied stacklessio settings for client: ', repr(settings))

    def LogClientCall(self, session, objectName, method, args, kwargs):
        with ExceptionEater('LogClientCall'):

            def CleanKeywordArgs(kwargs):
                if not kwargs or 'machoVersion' not in kwargs:
                    return kwargs
                cleanKwargs = kwargs.copy()
                del cleanKwargs['machoVersion']
                return cleanKwargs

            excludedMethods = ['GetTime']
            if method in excludedMethods:
                return
            charID = getattr(session, 'charid', None)
            userID = getattr(session, 'userid', None)
            solarSystemID = getattr(session, 'solarsystemid2', None)
            argString = None
            if self.eventLog.IsChannelOpen('security'):
                argString = repr(args)
                kwargString = repr(CleanKeywordArgs(kwargs))
                self.eventLog.LogOwnerEvent('ClientCall', charID, solarSystemID, userID, objectName, method, len(argString), argString[:1024], len(kwargString), kwargString[:1024], eventLogChannel='security')
            logAll = self.logAllClientCalls
            if logAll is None and prefs.clusterMode == 'LOCAL':
                logAll = 1
            if logAll:
                self.clientCallLogChannel = log.Channel(str(macho.mode), 'ClientCalls')
                callerInfo = 'User %s' % session.userid
                try:
                    callerInfo = 'Char %s (%s)' % (session.charid, cfg.eveowners.Get(session.charid).name)
                except:
                    pass

                kwargsTxt = ''
                if kwargs:
                    kk = CleanKeywordArgs(kwargs)
                    if kk:
                        kwargsTxt = '. kwargs = %s' % repr(kk)
                self.clientCallLogChannel.Log('%s called %s.%s%s%s' % (callerInfo,
                 objectName,
                 method,
                 repr(args)[:128],
                 kwargsTxt[:128]), log.LGNOTICE)
            if not self.sessionWatchIDs:
                return
            if not charID:
                return
            corpID = getattr(session, 'corpid', None)
            userType = getattr(session, 'userType', None)
            logIt = False
            if userID in self.sessionWatchIDs[0]:
                logIt = True
            elif charID in self.sessionWatchIDs[1]:
                logIt = True
            elif corpID in self.sessionWatchIDs[2]:
                logIt = True
            elif userType in self.sessionWatchIDs[3]:
                logIt = True
            elif session.role & ROLEMASK_ELEVATEDPLAYER:
                logIt = True
            if logIt:
                if argString is None:
                    argString = repr(args)
                    kwargString = repr(CleanKeywordArgs(kwargs))
                self.eventLog.LogOwnerEvent('ClientCall', charID, solarSystemID, userID, objectName, method, len(argString), argString[:1024], len(kwargString), kwargString[:1024])
                self.eventLog.LogOwnerEventJson('ClientCall', charID, solarSystemID, userID=userID, objectName=objectName, method=method, argsLen=len(argString), args=argString[:1024], kwargsLen=len(kwargString), kwargs=kwargString[:1024])

    def IsValidNodeID(self, node_id):
        if node_id == self.nodeID:
            return True
        if self.GetTransportOfNode(node_id) is not None:
            return True
        return False
