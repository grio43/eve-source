#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\net\eveMoniker.py
import eve.common.lib.appConst as const
from carbon.common.script.net import machoNet
from carbon.common.script.net.moniker import Moniker
from cluster import SERVICE_STATION, SERVICE_AGENTMGR
from eve.common.script.sys.idCheckers import IsStation

def GetLocationBindParams():
    if session.solarsystemid:
        return (session.solarsystemid, const.groupSolarSystem)
    if session.stationid:
        return (session.stationid, const.groupStation)
    raise RuntimeError('You have no place to go')


def GetLocationSessionCheck():
    if session.solarsystemid:
        return {'solarsystemid': session.solarsystemid}
    if session.stationid:
        return {'stationid': session.stationid}
    raise RuntimeError('You have no location to check on')


def CharGetDogmaLocation():
    moniker = Moniker('dogmaIM', GetLocationBindParams())
    moniker.SetSessionCheck(GetLocationSessionCheck())
    return moniker


def GetStationDogmaLocation():
    moniker = Moniker('dogmaIM', (session.stationid, const.groupStation))
    moniker.SetSessionCheck({'stationid': session.stationid})
    return moniker


def GetShipAccess():
    if session.solarsystemid:
        moniker = Moniker('ship', (session.solarsystemid, const.groupSolarSystem))
        moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
    elif session.stationid:
        moniker = Moniker('ship', (session.stationid, const.groupStation))
        moniker.SetSessionCheck({'stationid': session.stationid})
    return moniker


def GetStationShipAccess():
    moniker = Moniker('ship', (session.stationid, const.groupStation))
    moniker.SetSessionCheck({'stationid': session.stationid})
    return moniker


def GetEntityAccess():
    if session.solarsystemid is not None:
        moniker = Moniker('entity', session.solarsystemid2)
        moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
        return moniker
    raise RuntimeError('EntityAccess only available in-flight but session is %s' % (session,))


def GetEntityLocation():
    if session.solarsystemid2 is not None:
        moniker = Moniker('entity', session.solarsystemid2)
        moniker.SetSessionCheck({'solarsystemid2': session.solarsystemid2})
        return moniker
    raise RuntimeError('EntityLocation only available with in a valid solarsystem %s' % (session,))


def GetPOSMgr():
    if session.solarsystemid is not None:
        moniker = Moniker('posMgr', session.solarsystemid)
        moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
        return moniker
    raise RuntimeError('POSMgr only available in-flight but session is %s' % (session,))


def GetReprocessingManager():
    if session.structureid:
        moniker = GetReprocessingManagerEx(session.structureid)
        moniker.SetSessionCheck({'structureid': session.structureid})
    elif session.stationid:
        moniker = GetReprocessingManagerEx(session.stationid)
        moniker.SetSessionCheck({'stationid': session.stationid})
    else:
        raise RuntimeError('asked for reprocessing manager in a weird place')
    return moniker


def GetReprocessingManagerEx(stationID):
    return Moniker('reprocessingSvc', stationID)


def GetCorpStationManager():
    moniker = GetCorpStationManagerEx(session.stationid)
    moniker.SetSessionCheck({'stationid': session.stationid})
    return moniker


def GetCorpStationManagerEx(stationID):
    return Moniker('corpStationMgr', stationID)


def GetSolarSystemInventoryMgr(solarsystemID):
    return Moniker('invbroker', (solarsystemID, const.groupSolarSystem))


def GetStationInventoryMgr(stationID):
    return Moniker('invbroker', (stationID, const.groupStation))


def GetInventoryMgr():
    if session.solarsystemid:
        moniker = GetSolarSystemInventoryMgr(session.solarsystemid)
        moniker.SetSessionCheck({'solarsystemid': session.solarsystemid})
        return moniker
    if session.stationid:
        moniker = GetStationInventoryMgr(session.stationid)
        moniker.SetSessionCheck({'stationid': session.stationid})
        return moniker
    raise RuntimeError('Caller not in solsys nor station, session is %s' % (session,))


def CharGetCrimewatchLocation():
    moniker = Moniker('crimewatch', GetLocationBindParams())
    moniker.SetSessionCheck(GetLocationSessionCheck())
    return moniker


def GetBallPark(solarsystemID):
    moniker = Moniker('beyonce', solarsystemID)
    moniker.SetSessionCheck({'solarsystemid': solarsystemID})
    return moniker


def GetCourierMissionCreator(stationID):
    return Moniker('missionMgr', ('courier', stationID))


def GetAgent(agentID, stationID = None):
    if stationID is not None:
        macho = sm.GetService('machoNet')
        nodeID = macho.CheckAddressCache(SERVICE_STATION, stationID)
        if nodeID is not None:
            macho.SetNodeOfAddress(SERVICE_AGENTMGR, agentID, nodeID)
    return Moniker('agentMgr', agentID)


def GetCorpRegistry():
    moniker = GetCorpRegistryEx(session.corpid)
    moniker.SetSessionCheck({'corpid': session.corpid})
    return moniker


def GetCorpRegistryEx(corpID):
    return Moniker('corpRegistry', corpID)


def GetAlliance():
    if session.allianceid is None:
        raise RuntimeError('YouAreNotInAnAllianceAtTheMoment')
    moniker = GetAllianceEx(session.allianceid, 1)
    moniker.SetSessionCheck({'allianceid': session.allianceid})
    return moniker


def GetAllianceEx(allianceID, isMaster = 0):
    if machoNet.mode == 'server':
        isMaster = isMaster or sm.StartServiceAndWaitForRunningState('allianceRegistry').IsAllianceLocal(allianceID)
    return Moniker('allianceRegistry', (allianceID, isMaster))


def GetWar():
    ownerID = session.corpid
    ownerType = 'corpid'
    if session.allianceid:
        ownerID = session.allianceid
        ownerType = 'allianceid'
    moniker = GetWarEx(ownerID, 1)
    moniker.SetSessionCheck({ownerType: ownerID})
    return moniker


def GetWarEx(allianceOrCorpID, isMaster = 0):
    if machoNet.mode == 'server':
        isMaster = isMaster or sm.GetService('warRegistry').IsAllianceOrCorpLocal(allianceOrCorpID)
    return Moniker('warRegistry', (allianceOrCorpID, isMaster))


def GetWarStatistic(warID):
    return Moniker('warStatisticMgr', warID)


def GetFleet(fleetID = None):
    fleetID = fleetID or session.fleetid
    moniker = Moniker('fleetObjectHandler', fleetID)
    return moniker


def GetPlanet(planetID):
    return Moniker('planetMgr', planetID)


def GetPlanetBaseManager(planetID):
    return Moniker('planetBaseBroker', planetID)


def GetPlanetOrbitalRegistry(solarSystemID):
    return Moniker('planetOrbitalRegistryBroker', solarSystemID)


def GetRepairManager(locationID, solarSystemID):
    isStation = IsStation(locationID)
    parentLocationID = locationID if isStation else solarSystemID
    locationGroup = const.groupStation if isStation else const.groupSolarSystem
    return Moniker('repairSvc', (locationID, parentLocationID, locationGroup))
