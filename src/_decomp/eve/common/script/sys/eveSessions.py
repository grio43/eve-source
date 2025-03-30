#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\eveSessions.py
import math
import blue
import localization
from carbon.common.script.net import machobase as macho
from carbon.common.script.sys.basesession import FindSessions
from carbon.common.script.sys.sessions import SessionMgr as SessionMgrBase
from carbon.common.script.sys import basesession
from carbon.common.script.sys.serviceConst import ROLE_ADMIN, ROLE_SERVICE, SERVICE_RUNNING
from cluster import SERVICE_BEYONCE, SERVICE_CHATX, SERVICE_STATION
from eve.common.lib import appConst as const
from eve.common.lib.appConst import locationCharacterGraveyard
from eve.common.script.sys.idCheckers import IsStation, IsCharacter
from inventorycommon.util import IsNPC
eveSessionsByAttribute = {'regionid': {},
 'constellationid': {},
 'corpid': {},
 'fleetid': {},
 'wingid': {},
 'squadid': {},
 'shipid': {},
 'stationid': {},
 'structureid': {},
 'locationid': {},
 'solarsystemid': {},
 'solarsystemid2': {},
 'allianceid': {},
 'warfactionid': {}}
basesession.sessionsByAttribute.update(eveSessionsByAttribute)

def GetCharInventoryLocation(charID):
    locationID, locationGroupID, charLocationID = GetCharLocation2(charID)
    if locationGroupID is None:
        if charLocationID == locationCharacterGraveyard:
            return (True, None, None)
        raise RuntimeError('Bogus character item state', charID, locationID, charLocationID)
    return (False, locationID, locationGroupID)


def GetCharLocation(charID, include_graveyard = False):
    locationID, locationGroupID, charLocationID = GetCharLocation2(charID)
    if locationGroupID is None:
        raise RuntimeError('Bogus character item state', charID, locationID, charLocationID)
    return (locationID, locationGroupID)


def GetCharLocation2(charID):
    try:
        locationID, locationGroupID, charLocationID = GetCharLocationEx(charID)
    except RuntimeError:
        locationGroupID = None

    if locationGroupID is None:
        sm.services['charUnboundMgr'].RecoverCharacter(charID)
        locationID, locationGroupID, charLocationID = GetCharLocationEx(charID)
    return (locationID, locationGroupID, charLocationID)


def IsLocationNode(session):
    if not macho.mode == 'server':
        return False
    machoNet = sm.GetService('machoNet')
    currentNodeID = machoNet.GetNodeID()
    return any((session.solarsystemid and currentNodeID == machoNet.GetNodeFromAddress(SERVICE_BEYONCE, session.solarsystemid), session.stationid and currentNodeID == machoNet.GetNodeFromAddress(SERVICE_STATION, session.stationid)))


def GetCharLocationEx(charID):
    sessions = FindSessions('charid', [charID])
    if len(sessions) and IsLocationNode(sessions[0]):
        s = sessions[0]
        if s.solarsystemid:
            return (s.solarsystemid, const.groupSolarSystem, s.shipid)
        if s.stationid and s.shipid:
            return (s.stationid, const.groupStation, s.shipid)
        if s.stationid:
            return (s.stationid, const.groupStation, s.stationid)
    else:
        while sm.services['DB2'].state != SERVICE_RUNNING:
            blue.pyos.synchro.SleepWallclock(100)

        rs = sm.services['DB2'].GetSchema('character').Characters_LocationInfo(charID)
        locationInfo = rs[0]
        if locationInfo.locationID is None:
            raise RuntimeError('No such locationID', locationInfo.locationID, 'for charID', charID)
        if locationInfo.locationGroupID in (const.groupStation, const.groupSolarSystem):
            return (locationInfo.locationID, locationInfo.locationGroupID, locationInfo.characterLocationID)
        return (locationInfo.locationID, None, locationInfo.characterLocationID)


def IsUndockingSessionChange(session, change):
    goingFromStation = change.has_key('stationid') and change.get('stationid')[0]
    goingToSpace = change.has_key('solarsystemid') and change.get('solarsystemid')[1]
    return goingFromStation and goingToSpace


class SessionMgr(SessionMgrBase):
    __guid__ = 'svc.eveSessionMgr'
    __displayname__ = 'Session manager'
    __replaceservice__ = 'sessionMgr'
    __exportedcalls__ = {'GetSessionStatistics': [ROLE_SERVICE],
     'CloseUserSessions': [ROLE_SERVICE],
     'GetProxyNodeFromID': [ROLE_SERVICE],
     'GetClientIDsFromID': [ROLE_SERVICE],
     'UpdateSessionAttributes': [ROLE_SERVICE],
     'ConnectToClientService': [ROLE_SERVICE],
     'PerformSessionChange': [ROLE_SERVICE],
     'GetLocalClientIDs': [ROLE_SERVICE],
     'EndAllGameSessions': [ROLE_ADMIN | ROLE_SERVICE],
     'PerformHorridSessionAttributeUpdate': [ROLE_SERVICE],
     'BatchedRemoteCall': [ROLE_SERVICE],
     'GetSessionDetails': [ROLE_SERVICE],
     'TerminateClientConnections': [ROLE_SERVICE | ROLE_ADMIN],
     'GetInitialValuesFromCharID': [ROLE_SERVICE],
     'RemoveSessionsFromServer': [ROLE_SERVICE],
     'ResetClientConnection': [ROLE_SERVICE]}
    __dependencies__ = []
    __notifyevents__ = ['ProcessInventoryChange', 'ProcessSessionReset'] + SessionMgrBase.__notifyevents__

    def __init__(self):
        SessionMgrBase.__init__(self)
        if macho.mode == 'server':
            self.__dependencies__ += ['config',
             'station',
             'ship',
             'corporationSvc',
             'corpmgr',
             'i2',
             'stationSvc',
             'cache']
        self.sessionChangeShortCircuitReasons = ['autopilot']
        self.additionalAttribsAllowedToUpdate = ['allianceid', 'corpid']
        self.additionalStatAttribs = ['solarsystemid', 'solarsystemid2', 'structureid']
        self.additionalSessionDetailsAttribs = ['allianceid',
         'warfactionid',
         'corpid',
         'corprole',
         'shipid',
         'regionid',
         'constellationid',
         'solarsystemid2',
         'locationid',
         'solarsystemid',
         'stationid',
         'structureid',
         'fleetid',
         'wingid',
         'squadid',
         'fleetrole',
         'corpAccountKey',
         'inDetention']

    def AppRun(self, memstream = None):
        if macho.mode == 'server':
            self.dbcharacter = self.DB2.GetSchema('character')

    def GetReason(self, oldReason, newReason, timeLeft):
        if timeLeft:
            seconds = int(math.ceil(max(1, timeLeft) / float(const.SEC)))
        reason = localization.GetByLabel('UI/Sessions/BaseReason')
        if oldReason == newReason or oldReason.startswith('fleet.') and newReason.startswith('fleet.') or oldReason.startswith('corp.') and newReason.startswith('corp.'):
            if oldReason.startswith('fleet.'):
                reason = localization.GetByLabel('UI/Sessions/FleetOperation')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason.startswith('corp.'):
                reason = localization.GetByLabel('UI/Sessions/CorpOperation')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason == 'undock':
                reason = localization.GetByLabel('UI/Sessions/Undocking')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason == 'dock':
                reason = localization.GetByLabel('UI/Sessions/Docking')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason == 'jump' and newReason == 'jump':
                reason = localization.GetByLabel('UI/Sessions/Jump')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/EstimatedTimeLeft', reason=reason, seconds=seconds)
            elif oldReason == 'jump':
                reason = localization.GetByLabel('UI/Sessions/StartgateJump')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/StartgateJumpEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'eject':
                reason = localization.GetByLabel('UI/Sessions/Ejecting')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/EjectingEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'evacuate':
                reason = localization.GetByLabel('UI/Sessions/Evacuation')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/EvacuationsEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'board':
                reason = localization.GetByLabel('UI/Sessions/Boarding')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/BoardingEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'selfdestruct':
                reason = localization.GetByLabel('UI/Sessions/SelfDestruct')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/SelfDestructEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'charsel':
                reason = localization.GetByLabel('UI/Sessions/CharacterSelection')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/CharacterSelectionEstimatedTime', reason=reason, seconds=seconds)
            elif oldReason == 'storeVessel':
                reason = localization.GetByLabel('UI/Sessions/Embarkation')
                if timeLeft:
                    reason = localization.GetByLabel('UI/Sessions/EmbarkationEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'autopilot':
            reason = localization.GetByLabel('UI/Sessions/Autopilot')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AutopilotEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'undock':
            reason = localization.GetByLabel('UI/Sessions/AreUndocking')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreUndockingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'dock':
            reason = localization.GetByLabel('UI/Sessions/AreDocking')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreDockingEstimmatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'jump':
            reason = localization.GetByLabel('UI/Sessions/AreJumping')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreJumpingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'eject':
            reason = localization.GetByLabel('UI/Sessions/AreEjecting')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreEjectingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'evacuate':
            reason = localization.GetByLabel('UI/Sessions/AreEvacuating')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreEvacuatingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'board':
            reason = localization.GetByLabel('UI/Sessions/AreBoarding')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreBoardingEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'selfdestruct':
            reason = localization.GetByLabel('UI/Sessions/AreSelfDestructing')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreSelfDestructiongEstimateTime', reason=reason, seconds=seconds)
        elif oldReason == 'charsel':
            reason = localization.GetByLabel('UI/Sessions/AreSelectingCharacter')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreSelectingCharacterEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'accelerationgate':
            reason = localization.GetByLabel('UI/Sessions/AreUsingAccelerationGate')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreUsingAccelerationGateEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason.startswith('corp.'):
            reason = localization.GetByLabel('UI/Sessions/CorpActivity')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/CorpActivityEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason.startswith('fleet.'):
            reason = localization.GetByLabel('UI/Sessions/FleetOperations')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/FleetOperationsEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'storeVessel':
            reason = localization.GetByLabel('UI/Sessions/AreBoardingVessel')
            if timeLeft:
                reason = localization.GetByLabel('UI/Sessions/AreBoardingVesselEstimatedTime', reason=reason, seconds=seconds)
        elif oldReason == 'bookmarking':
            reason = localization.GetByLabel('UI/Sessions/Bookmarking')
        return reason

    def TypeAndNodeValidationHook(self, idType, id):
        if macho.mode == 'server' and idType in ('allianceid', 'corpid'):
            machoNet = sm.GetService('machoNet')
            if machoNet.GetNodeID() != machoNet.GetNodeFromAddress(SERVICE_CHATX, id % 200):
                raise RuntimeError('Horrid session change called on incorrect node.  You must at very least perform this abomination on the right node.')

    def ProcessSessionReset(self):
        if macho.mode != 'client':
            return
        session.ClearCharacterDependantAttributes()

    def ProcessInventoryChange(self, items, change, isRemote, inventory2):
        if macho.mode != 'server':
            return
        if isRemote:
            return
        if const.ixLocationID not in change and const.ixFlag not in change:
            return
        chars = {}
        for item in items:
            if item.categoryID == const.categoryShip and item.singleton:
                for sess in FindSessions('shipid', [item.itemID]):
                    locationToCompare = sess.structureid or sess.stationid or sess.solarsystemid
                    if sess.charid == item.ownerID and (locationToCompare == item.locationID or locationToCompare in change.get(const.ixLocationID, [None, None])):
                        chars[sess.charid] = self.GetSessionValuesFromItemID(item.itemID, inventory2, item)

            elif item.groupID == const.groupCharacter:
                charValues = self.GetSessionValuesFromItemID(item.itemID, inventory2, item)
                if charValues['structureid'] and item.flagID == const.flagPilot and charValues['shipid'] is None:
                    charValues['shipid'] = charValues['structureid']
                chars[item.itemID] = charValues

        if len(chars) == 0:
            return
        for charID, updateDict in chars.iteritems():
            for sess in FindSessions('charid', [charID]):
                sess.LogSessionHistory('Transmogrifying OnInventoryChange to SetAttributes')
                sess.SetAttributes(updateDict)
                sess.LogSessionHistory('Transmogrified OnInventoryChange to SetAttributes')

    def GetSessionValuesFromItemID(self, itemID, inventory2 = None, theItem = None):
        if itemID == const.locationAbstract:
            raise RuntimeError('Invalid argument, itemID cannot be 0')

        def GetItem(id):
            return sm.services['i2'].GetItemMx(id)

        updateDict = {'shipid': None,
         'stationid': None,
         'structureid': None,
         'solarsystemid': None,
         'solarsystemid2': None,
         'regionid': None,
         'constellationid': None}
        solsysID = None
        while 1:
            if inventory2 is None:
                item = GetItem(itemID)
            elif theItem and theItem.itemID == itemID:
                item = theItem
            elif itemID < const.minPlayerItem:
                if IsStation(itemID):
                    station = self.stationSvc.GetStation(itemID)
                    updateDict['stationid'] = itemID
                    solsysID = station.solarSystemID
                    break
                else:
                    item = inventory2.InvGetItem(itemID)
            else:
                item = inventory2.InvGetItem(itemID, 1)
            if item.categoryID == const.categoryShip:
                updateDict['shipid'] = itemID
            elif item.groupID == const.groupStation:
                updateDict['stationid'] = itemID
                solsysID = item.locationID
                break
            elif item.categoryID == const.categoryStructure:
                updateDict['structureid'] = itemID
            elif item.typeID == const.typeSolarSystem:
                solsysID = item.itemID
                updateDict['solarsystemid'] = itemID
                break
            elif item.locationID == const.locationAbstract:
                break
            itemID = item.locationID

        if solsysID is not None:
            primeditems = sm.services['i2'].__primeditems__
            if solsysID in primeditems:
                updateDict['solarsystemid2'] = solsysID
                updateDict['constellationid'] = primeditems[solsysID].locationID
                updateDict['regionid'] = primeditems[updateDict['constellationid']].locationID
        return updateDict

    def GetSessionValuesFromRowset(self, si):
        sessValues = {'allianceid': si.allianceID,
         'warfactionid': si.warFactionID,
         'corpid': si.corporationID,
         'hqID': si.hqID,
         'baseID': si.baseID,
         'rolesAtAll': si.roles,
         'rolesAtHQ': si.rolesAtHQ,
         'rolesAtBase': si.rolesAtBase,
         'rolesAtOther': si.rolesAtOther,
         'fleetid': None,
         'fleetrole': None,
         'wingid': None,
         'squadid': None,
         'shipid': si.shipID,
         'stationid': None,
         'structureid': si.structureID,
         'solarsystemid': None,
         'regionid': None,
         'constellationid': None,
         'genderID': si.genderID,
         'bloodlineID': si.bloodlineID,
         'raceID': si.raceID,
         'corpAccountKey': si.corpAccountKey}
        if si.stationID:
            sessValues['stationid'] = si.stationID
            station = self.stationSvc.GetStation(si.stationID)
            sessValues['solarsystemid2'] = station.solarSystemID
        elif si.solarSystemID:
            sessValues['solarsystemid'] = si.solarSystemID
            sessValues['solarsystemid2'] = si.solarSystemID
        if 'solarsystemid2' in sessValues:
            if sessValues['solarsystemid2'] is not None:
                primeditems = sm.services['i2'].__primeditems__
                if sessValues['solarsystemid2'] in primeditems:
                    sessValues['constellationid'] = primeditems[sessValues['solarsystemid2']].locationID
                    sessValues['regionid'] = primeditems[sessValues['constellationid']].locationID
        return sessValues

    def GetInitialValuesFromCharID(self, characterID):
        if macho.mode != 'server':
            return {}
        values = self.GetSessionValuesFromRowset(self.dbcharacter.Characters_Session2(characterID)[0])
        if not values.get('stationid') and not values.get('solarsystemid'):
            sm.services['charUnboundMgr'].RecoverCharacter(characterID)
            return self.GetSessionValuesFromRowset(self.dbcharacter.Characters_Session2(characterID)[0])
        return values

    def IsPlayerCharacter(self, charID):
        return IsCharacter(charID) and not IsNPC(charID)

    def GetSession(self, charID):
        s = FindSessions('charid', [charID])
        if not s:
            return None
        return s[0]

    def GetUserSession(self, userid):
        foundSessions = FindSessions('userid', [userid])
        if not foundSessions:
            return
        for foundSession in foundSessions:
            if foundSession.charid is None:
                return foundSession

    def GetCharacterSession(self, charid):
        s = FindSessions('charid', [charid])
        if not s:
            return None
        return s[0]

    def _AddToSessionStatistics(self):
        SessionMgrBase._AddToSessionStatistics(self)
        eve_online = 0
        for sess in basesession.sessionsBySID.itervalues():
            if sess.sessionType == const.session.SESSION_TYPE_GAME:
                if sess.charid:
                    eve_online += 1

        self.sessionStatistics['EVE:Online'] = (eve_online, {None: eve_online})
        self.sessionStatistics['EVE:Trial'] = (0, {None: 0})
        self.sessionStatistics['DUST:Online'] = (0, {None: 0})
        self.sessionStatistics['DUST:Battle'] = (0, {None: 0})
        self.sessionStatistics['DUST:User'] = (0, {None: 0})
