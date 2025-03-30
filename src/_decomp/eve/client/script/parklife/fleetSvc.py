#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\fleetSvc.py
import copy
import yaml
import eveexceptions
from carbon.common.lib.const import SEC, MIN
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service
from carbon.common.script.util.format import FmtAmt
from carbonui.control.contextMenu.menuData import MenuData
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
import evefleet.fleetSetupConst as fsConst
from eve.client.script.ui.shared.fleet.fleetbroadcast import BroadcastSettings
from eve.client.script.ui.shared.fleet.fleetregister import RegisterFleetWindow
from eve.client.script.ui.shared.fleet.fleetwindow import FleetWindow
from eve.client.script.ui.shared.fleet.fleetJoinRequestWnd import FleetJoinRequestWindow
from eve.client.script.ui.shared.fleet.fleetCompositionWnd import FleetComposition
from evefleet.client.fleetFinder_allowedEntities import GetDiffInAllowedAndBanned
from eve.client.script.ui.shared.fleet.fleet import WatchListPanel, WingName, SquadronName
from eve.client.script.ui.shared.fleet.fleetBroadcastConst import BROADCAST_COLOR_SETTING, LISTEN_BROADCAST_SETTING, broadcastNames, flagToName, iconsByBroadcastType
from evefleet import BROADCAST_SHOW_OWN
from eve.client.script.ui.util.linkUtil import GetCharIDFromTextLink
from eve.common.script.net.eveMoniker import GetFleet
from eve.common.script.sys.eveCfg import GetActiveShip, IsDockedInStructure
from eve.common.script.sys.idCheckers import IsCharacter, IsEvePlayerCharacter, IsNPC
from eveexceptions import UserError
from eveexceptions.const import UE_LOCID, UE_OWNERID
import evelink.client
import evetypes
from evefleet.client.util import GetFleetSetupOptionHint
from evefleet.fleetAdvertObject import FleetAdvertObject
from inventorycommon.const import groupAsteroidBelt, groupMoon, groupPlanet, groupWarpGate, groupStargate, groupStation, groupSkyhook
import trinity
import uthread
from eve.client.script.ui.util import uix
import blue
import states as state
from eve.client.script.ui.shared.fleet import fleetbroadcastexports, fleetBroadcastConst
import log
import carbonui.const as uiconst
import localization
import evefleet
from eve.client.script.util.eveMisc import CSPAChargedActionForMany, CSPAChargedAction
from eve.client.script.ui.shared.fleet.storeFleetSetupWnd import StoredFleetSetupListWnd
from eve.client.script.ui.shared.fleet.storeFleetSetupWnd import StoreFleetSetupWnd
import sharedSettings
from utillib import KeyVal
from carbonui.uicore import uicore
from messagebus.fleetMessenger import FleetMessenger
import eve.common.lib.appConst as const
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from eve.client.script.ui.util import utilWindows
from uihider import CommandBlockerService
FLEETBROADCASTTIMEOUT = 15
UPDATEFLEETFINDERDELAY = 60
UPDATEFLEETMEMBERDELAY_SEC = 30
MIN_BROADCAST_TIME = 2
RECONNECT_DELAY = 10
FLEETCOMPOSITION_CACHE_TIME = 20
MAX_NUM_BROADCASTS = 500
MAX_NUM_LOOTEVENTS = 500
CONNOT_BE_MOVED_INCOMPATIBLE = -1
CANNOT_BE_MOVED = 0
CAN_BE_COMMANDER = 1
CAN_ONLY_BE_MEMBER = 2
cynoTypeNames = {const.typeCovertCynosuralFieldI: 'UI/Fleet/CynoCovert',
 const.typeIndustrialCynosuralField: 'UI/Fleet/CynoIndustrial',
 const.typeCynosuralFieldI: 'UI/Fleet/CynoStandard'}

class FleetSvc(Service):
    __guid__ = 'svc.fleet'
    __notifyevents__ = ['OnFleetBroadcast',
     'ProcessSessionChange',
     'OnFleetInvite',
     'OnFleetJoin',
     'OnFleetJoinReject',
     'OnFleetLeave',
     'OnFleetDisbanded',
     'OnFleetMove',
     'OnFleetMemberChanged',
     'OnFleetMoveFailed',
     'OnFleetWingAdded',
     'OnFleetWingDeleted',
     'OnFleetSquadAdded',
     'OnFleetSquadDeleted',
     'OnFleetStateChange',
     'OnFleetJumpBeaconModuleChange',
     'OnFleetJumpBeaconDeployableChange',
     'OnBridgeModeChange',
     'OnFleetWingNameChanged',
     'OnFleetSquadNameChanged',
     'OnFleetOptionsChanged',
     'OnMemberlessFleetUnregistered',
     'OnJoinedFleet',
     'OnLeftFleet',
     'OnFleetJoinRequest',
     'OnFleetJoinRejected',
     'OnJoinRequestUpdate',
     'OnContactChange',
     'OnFleetLootEvent',
     'OnFleetMotdChanged',
     'ProcessShutdown',
     'OnSessionReset',
     'OnFleetRespawnPointsUpdate']
    __startupdependencies__ = ['settings']
    __dependencies__ = ['sessionMgr', 'clientPathfinderService']
    message_bus = None

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.semaphore = uthread.Semaphore()
        self.message_bus = FleetMessenger(sm.GetService('publicGatewaySvc'))
        self.Clear()
        sm.FavourMe(self.OnFleetMemberChanged)

    def GetFleetSetups(self):
        if self.fleetSetupsByName is None:
            self.characterSettings = sm.GetService('characterSettings')
            self.fleetSetupsByName = self.FetchFleetSetupsFromServer()
        return self.fleetSetupsByName

    def FetchFleetSetupsFromServer(self):
        ret = {}
        yamlStr = self.characterSettings.Get('fleetSetups')
        if yamlStr is not None:
            filters = yaml.safe_load(yamlStr)
            ret = {f[fsConst.FS_NAME]:f for f in filters}
        return ret

    def Clear(self):
        self.leader = None
        self.initedFleet = None
        self.members = {}
        self.wings = {}
        self.targetTags = {}
        self.fleetState = None
        self.activeModuleBeacons = {}
        self.activeDeployableBeacons = {}
        self.activeBridge = {}
        self.fleetID = None
        self.fleet = None
        self.favorites = []
        self.options = KeyVal(isFreeMove=False, isRegistered=False, autoJoinSquadID=None)
        self.isDamageUpdates = True
        self.joinRequests = {}
        self.CleanupBroadcasts()
        self.currentBroadcastOnItem = {}
        self.targetBroadcasts = {}
        self.currentTargetBroadcast = {}
        self.locationUpdateRegistrations = {}
        self.lastBroadcast = KeyVal(name=None, timestamp=0)
        self.broadcastHistory = []
        self.broadcastScope = settings.user.ui.Get('fleetBroadcastScope', evefleet.BROADCAST_ALL)
        self.updateThreadRunning = False
        self.updateAdvertThreadRunning = False
        self.currentFleetAd = None
        self.lootHistory = []
        self.memberHistory = []
        self.fleetComposition = None
        self.fleetCompositionTimestamp = 0
        self.expectingInvite = None
        self.motd = None
        self.fleetSetupsByName = None
        self.lastLoadedSetup = None
        self.respawnPoints = []

    def CleanupBroadcasts(self):
        for itemID, (gbID, gbState, data) in getattr(self, 'currentBroadcastOnItem', {}).iteritems():
            sm.GetService('stateSvc').SetState(itemID, gbState, False, gbID, *data)

    def ProcessShutdown(self):
        if session.fleetid and len(self.members) > 0:
            self.LogNotice('I will attempt to reconnect to this fleet', session.fleetid, ' when the client starts up again')
            settings.char.ui.Set('fleetReconnect', (session.fleetid, blue.os.GetWallclockTime()))
            settingsSvc = sm.GetServiceIfRunning('settings')
            if settingsSvc:
                settingsSvc.SaveSettings()

    def OnSessionReset(self):
        self.Clear()

    def OnFleetStateChange(self, fleetState):
        self.fleetState = fleetState

    def OnBridgeModeChange(self, shipID, solarsystemID, itemID, active):
        self.LogInfo('OnBridgeModeChange called:', shipID, solarsystemID, itemID, active)
        if active:
            self.activeBridge[shipID] = (solarsystemID, itemID)
        elif shipID in self.activeBridge:
            del self.activeBridge[shipID]

    def OnFleetJumpBeaconModuleChange(self, charID, solarsystemID, beaconID, typeID, active):
        self.LogInfo('OnFleetJumpBeaconModuleChange:', charID, solarsystemID, beaconID, typeID, active)
        if active:
            self.activeModuleBeacons[charID] = (solarsystemID, beaconID, typeID)
        else:
            self.activeModuleBeacons.pop(charID, None)

    def OnFleetJumpBeaconDeployableChange(self, deployableID, solarsystemID, beaconID, ownerID, active):
        self.LogInfo('OnFleetJumpBeaconDeployableChange:', deployableID, solarsystemID, beaconID, active)
        if active:
            self.activeDeployableBeacons[deployableID] = (solarsystemID, beaconID, ownerID)
        else:
            self.activeDeployableBeacons.pop(deployableID, None)

    def GetTargetTag(self, itemID):
        if self.fleetState:
            return self.fleetState.targetTags.get(itemID, None)

    def HasActiveBridge(self, shipID):
        return shipID in self.activeBridge

    def GetActiveBeacons(self):
        return self.activeModuleBeacons

    def HasActiveBeacon(self, charID):
        return charID in self.activeModuleBeacons

    def GetActiveBridgeForShip(self, shipID):
        if shipID not in self.activeBridge:
            return None
        return self.activeBridge[shipID]

    def GetActiveBeaconForChar(self, charID):
        if charID not in self.activeModuleBeacons:
            return None
        return self.activeModuleBeacons[charID]

    def InitFleet(self):
        if self.fleet is None:
            return
        oldOptions = self.options
        initState = self.fleet.GetInitState()
        self.fleetID = initState.fleetID
        self.members = initState.members
        self.wings = initState.wings
        self.options = initState.options
        self.motd = initState.motd
        cfg.eveowners.Prime(self.members.keys())
        self.fleetMemberLocations = {}
        if oldOptions != self.options:
            sm.ScatterEvent('OnFleetOptionsChanged_Local', oldOptions, self.options)
        sm.ScatterEvent('OnMyFleetInfoChanged')
        sm.ScatterEvent('OnMyFleetInited')

    def SingleChoiceBox(self, title, body, choices, suppressID):
        supp = settings.user.suppress.Get('suppress.' + suppressID, None)
        if supp is not None and not uicore.uilib.Key(uiconst.VK_SHIFT):
            return supp
        ret, block = sm.GetService('gameui').RadioButtonMessageBox(text=body, title=title, buttons=uiconst.OKCANCEL, icon=uiconst.QUESTION, radioOptions=choices, height=210, width=300, suppText=localization.GetByLabel('UI/Common/SuppressionShowMessageRemember'))
        if ret[0] in [uiconst.ID_CANCEL, uiconst.ID_CLOSE]:
            return
        retNum = 1
        if ret[1] == 'radioboxOption2Selected':
            retNum = 2
        if block:
            settings.user.suppress.Set('suppress.' + suppressID, retNum)
        else:
            settings.user.suppress.Delete('suppress.' + suppressID)
        return retNum

    def CreateFleet(self, setupName = None, adInfoData = None):
        if session.fleetid:
            raise UserError('FleetError')
        self.fleet = sm.RemoteSvc('fleetObjectHandler').CreateFleet()
        self.LogInfo('Created fleet %s' % self.fleet)
        createdAdData = self.fleet.Init(self.GetMyShipTypeID(), setupName, adInfoData=adInfoData)
        self.InitFleet()
        self.fleetID = self.fleet.GetFleetID()
        if createdAdData:
            createdAd = FleetAdvertObject(**createdAdData)
            self._FinializeRegistration(createdAd, False)
        return True

    def StartNewFleet(self, setupName = None):
        if self.fleet:
            return
        self.CreateFleet(setupName)
        self.LogFleetCreation(self.fleetID, evefleet.CREATE_SOURCE_FLEET_FINDER_WND)

    def Invite(self, charID, wingID, squadID, role):
        if self.fleet is None:
            if not self.CreateFleet():
                return
            self.LogFleetCreation(self.fleetID, evefleet.CREATE_SOURCE_MENU)
        if IsNPC(charID) or not IsCharacter(charID):
            eve.Message('NotRealPilotInvite')
            return
        msgName = None
        if charID != session.charid:
            CSPAChargedAction('CSPAFleetCheck', self.fleet, 'Invite', charID, wingID, squadID, role)

    def LeaveFleet(self):
        if self.fleet is None and session.fleetid:
            sm.RemoteSvc('fleetMgr').ForceLeaveFleet()
        else:
            self.fleet.LeaveFleet()
            self.Clear()

    def IsMember(self, charID):
        return charID in self.members

    def GetMembers(self):
        return self.members

    def GetWings(self):
        if self.fleet is None:
            return {}
        return self.wings

    def GetMembersInWing(self, wingID):
        members = {}
        for mid, m in self.members.iteritems():
            if m.wingID == wingID:
                members[mid] = m

        return members

    def GetMembersInSquad(self, squadID):
        members = {}
        for mid, m in self.members.iteritems():
            if m.squadID == squadID:
                members[mid] = m

        return members

    def ChangeWingName(self, wingID):
        if self.fleet is None:
            return
        name = ''
        ret = utilWindows.NamePopup(localization.GetByLabel('UI/Fleet/ChangeWingName'), localization.GetByLabel('UI/Common/Name/TypeInName'), name, maxLength=evefleet.MAX_NAME_LENGTH)
        if ret is not None:
            self.fleet.ChangeWingName(wingID, ret[:evefleet.MAX_NAME_LENGTH])

    def ChangeSquadName(self, squadID):
        if self.fleet is None:
            return
        name = ''
        ret = utilWindows.NamePopup(localization.GetByLabel('UI/Fleet/ChangeSquadName'), localization.GetByLabel('UI/Common/Name/TypeInName'), name, maxLength=evefleet.MAX_NAME_LENGTH)
        if ret is not None:
            self.fleet.ChangeSquadName(squadID, ret[:evefleet.MAX_NAME_LENGTH])

    def SetAcceptsFleetWarpValue(self, value):
        self.fleet.SetTakesFleetWarp(value)

    def SetAcceptConduitJumpsValue(self, value):
        self.fleet.SetAcceptsConduitJumpsValue(value)

    def SetAcceptRegroupValue(self, value):
        self.fleet.SetAcceptsRegroupValue(value)

    def TakesFleetWarp(self):
        return self.members[session.charid].memberOptOuts.acceptsFleetWarp

    def AcceptsConduitJumps(self):
        return self.members[session.charid].memberOptOuts.acceptsConduitJumps

    def AcceptsFleetRegroups(self):
        return self.members[session.charid].memberOptOuts.acceptsFleetRegroups

    def GetOptions(self):
        return self.options

    def SetOptions(self, isFreeMove = None):
        options = copy.copy(self.options)
        if isFreeMove != None:
            options.isFreeMove = isFreeMove
        return self.fleet.SetOptions(options)

    def SetDamageUpdates(self, isit):
        self.isDamageUpdates = isit
        self.RegisterForDamageUpdates()

    def IsDamageUpdates(self):
        return self.isDamageUpdates

    def GetJoinRequests(self):
        if not self.joinRequests:
            self.joinRequests = self.fleet.GetJoinRequests()
        return self.joinRequests

    def GetFleetHierarchy(self, members = None):
        if members is None:
            members = self.GetMembers()
        ret = {'commander': None,
         'wings': {},
         'squads': {},
         'name': ''}
        for wingID, wing in self.GetWings().iteritems():
            ret['wings'][wingID] = {'commander': None,
             'squads': wing.squads.keys(),
             'name': wing.name}
            for squadID, squad in wing.squads.iteritems():
                ret['squads'][squadID] = {'commander': None,
                 'members': [],
                 'name': squad.name}

        for rec in members.itervalues():
            if rec.squadID:
                self.AddToFleet(ret, rec)

        return ret

    def AddToFleet(self, fleet, rec):
        try:
            if rec.squadID != -1:
                allSquads = fleet['squads']
                squad = allSquads[rec.squadID]
                if rec.role == evefleet.fleetRoleSquadCmdr:
                    squad['commander'] = rec.charID
                    squad['members'].insert(0, rec.charID)
                elif rec.role == evefleet.fleetRoleMember:
                    squad['members'].append(rec.charID)
                else:
                    log.LogError('Unknown role in squad!', rec.role)
            elif rec.wingID != -1:
                allWings = fleet['wings']
                wing = allWings[rec.wingID]
                if rec.role == evefleet.fleetRoleWingCmdr:
                    wing['commander'] = rec.charID
            elif rec.role == evefleet.fleetRoleLeader:
                fleet['commander'] = rec.charID
            else:
                log.LogTraceback("Don't know how to add this guy! {!r}".format(rec))
        except KeyError as e:
            log.LogTraceback()

    def CheckIfIsOKWithDemotion(self, role):
        myself = self.members[session.charid]
        if myself.job & evefleet.fleetJobCreator != 0:
            return True
        if myself.role < evefleet.fleetRoleSquadCmdr and role > myself.role and eve.Message('FleetConfirmDemoteSelf', {}, uiconst.YESNO) != uiconst.ID_YES:
            return False
        return True

    def MoveMember(self, charID, wingID, squadID, role):
        self.CheckIsInFleet()
        if charID == session.charid:
            if not self.CheckIfIsOKWithDemotion(role):
                return
        if self.fleet.MoveMember(charID, wingID, squadID, role):
            sm.ScatterEvent('OnFleetMemberChanging', charID)

    def MassMove(self, charIDs, wingID, squadID, role):
        charIDs = self.FilterOutNonCharacters(charIDs)
        if len(charIDs) == 1:
            return self.MoveMember(charIDs[0], wingID, squadID, role)
        if session.charid in charIDs:
            isOkWithDemotion = self.CheckIfIsOKWithDemotion(role=role)
            if not isOkWithDemotion:
                charIDs.remove(session.charid)
        if charIDs:
            wereMoved = self.fleet.MassMoveMembers(charIDs, wingID, squadID, role)
            if wereMoved:
                sm.ScatterEvent('OnManyFleetMembersChanging', wereMoved)

    def MassInvite(self, charIDs, wingID, squadID, role):
        charIDs = self.FilterOutNonCharacters(charIDs)
        if self.fleet is None and charIDs:
            if not self.CreateFleet():
                return
        if session.charid in charIDs:
            charIDs.remove(session.charid)
        if len(charIDs) == 1:
            charID = charIDs[0]
            self.Invite(charID, wingID, squadID, role)
            if role == evefleet.fleetRoleMember:
                eve.Message('CharacterAddedAsSquadMember', {'char': charID})
            elif role == evefleet.fleetRoleSquadCmdr:
                eve.Message('CharacterAddedAsSquadCommander', {'char': charID})
            elif role == evefleet.fleetRoleWingCmdr:
                eve.Message('CharacterAddedAsWingCommander', {'char': charID})
            elif role == evefleet.fleetRoleLeader:
                eve.Message('CharacterAddedAsFleetCommander', {'char': charID})
        elif charIDs:
            try:
                CSPAChargedActionForMany('CSPAFleetCheckMany', self.fleet, 'MassInvite', charIDs, wingID, squadID, role)
            except UserError as e:
                if e.msg in ('FleetErrorMany', 'FleetNotAllowedMany', 'FleetNoPositionFoundMany', 'FleetTooManyMembersMany', 'FleetInviteMultipleErrors'):
                    notInvited = e.dict.get('notInvited', [])
                    charNameList = [ cfg.eveowners.Get(charID).name for charID in notInvited ]
                    charNames = ', '.join(charNameList)
                    if e.dict:
                        e.dict['namelist'] = charNames
                    raise UserError(e.msg, e.dict)
                else:
                    raise

    def FilterOutNonCharacters(self, charIDs):
        realCharIDs = [ eachID for eachID in charIDs if not IsNPC(eachID) and IsCharacter(eachID) ]
        return realCharIDs

    def CreateWing(self):
        self.CheckIsInFleet()
        wingID = self.fleet.CreateWing()
        if wingID:
            self.CreateSquad(wingID)

    def DeleteWing(self, wingID):
        self.CheckIsInFleet()
        self.fleet.DeleteWing(wingID)

    def CreateSquad(self, wingID):
        self.CheckIsInFleet()
        self.fleet.CreateSquad(wingID)

    def DeleteSquad(self, wingID):
        self.CheckIsInFleet()
        self.fleet.DeleteSquad(wingID)

    def SetAutoJoinSquadID(self, squadID):
        self.fleet.SetAutoJoinSquadID(squadID)

    def MakeLeader(self, charID):
        self.fleet.MakeLeader(charID)

    def KickMember(self, charID):
        if charID == session.charid:
            self.LeaveFleet()
        else:
            self.fleet.KickMember(charID)

    def DisbandFleet(self):
        if not self.IsBoss():
            raise UserError('CannotDisbandFleetIfNotBoss')
        self.fleet.DisbandFleet()

    def __VerifyRightsToRestrict(self, channel):
        return True
        ret = False
        if session.fleetrole > 3:
            ret = False
        elif session.fleetrole == 3:
            squads = self.GetFleetHierarchy()['squads']
            if squads[channel]['commander'] == session.charid:
                ret = True
        elif session.fleetrole == 2:
            wings = self.GetFleetHierarchy()['wings']
            if wings[channel]['commander'] == session.charid:
                ret = True
        elif session.fleetrole == 1:
            if session.fleetid == channel[1]:
                ret = True
        if not ret:
            raise UserError('FleetNotAllowed')

    def AddFavorite(self, charIDs):
        self.CheckIsInFleet()
        if session.charid in charIDs:
            charIDs.remove(session.charid)
        if not charIDs:
            return
        if len(self.favorites) >= evefleet.MAX_DAMAGE_SENDERS:
            raise UserError('FleetTooManyFavorites', {'num': evefleet.MAX_DAMAGE_SENDERS})
        newCharIDs = []
        for eachCharID in charIDs:
            if eachCharID not in self.members:
                continue
            if self.GetFavorite(eachCharID):
                continue
            newCharIDs.append(eachCharID)

        if not newCharIDs:
            return
        newCharsAdded = []
        for eachCharID in newCharIDs:
            if len(self.favorites) >= evefleet.MAX_DAMAGE_SENDERS:
                break
            favorite = KeyVal(charID=eachCharID, orderID=len(self.favorites))
            self.favorites.append(favorite)
            newCharsAdded.append(eachCharID)

        if not newCharsAdded:
            return
        fav = self.GetWatchlistMembers()
        sm.RemoteSvc('fleetMgr').AddToWatchlist(newCharsAdded, fav)
        sm.ScatterEvent('OnFleetFavoriteAdded', fav)
        wnd = WatchListPanel.Open(showActions=False, panelName=localization.GetByLabel('UI/Fleet/WatchList'))
        wnd.OnFleetFavoriteAdded(fav)

    def AddFavoriteSquad(self, squadID):
        squadMembers = [ memberID for memberID, m in self.members.iteritems() if m.squadID == squadID ]
        self.AddFavorite(squadMembers)

    def GetFavorite(self, charID):
        for favorite in self.favorites:
            if charID == favorite.charID:
                return favorite

    def RemoveAllFavorites(self):
        self.favorites = []
        sm.ScatterEvent('OnFleetFavoritesRemoved')

    def RemoveFavorite(self, charID):
        self.CheckIsInFleet()
        for i, favorite in enumerate(self.favorites):
            if favorite.charID == charID:
                del self.favorites[i]
                break

        favs = self.GetWatchlistMembers()
        sm.RemoteSvc('fleetMgr').RemoveFromWatchlist(charID, favs)
        sm.ScatterEvent('OnFleetFavoriteRemoved', charID)

    def ClearWatchlistBroadcastHistory(self):
        wnd = WatchListPanel.GetIfOpen()
        if wnd and not wnd.destroyed:
            wnd.ClearBroadcastHistory()
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fleet/BroadcastIconsCleared')})

    def ChangeFavoriteSorting(self, charID, orderID = -1, *args):
        if getattr(self, 'isChangingOrder', False):
            return
        try:
            setattr(self, 'isChangingOrder', True)
            favorite = self.GetFavorite(charID)
            if not favorite:
                return
            favoriteIndex = favorite.orderID
            if favoriteIndex < 0:
                return
            if favoriteIndex > len(self.favorites):
                return
            self.favorites.remove(favorite)
            if orderID == -1:
                orderID = len(self.favorites)
            newFavorite = KeyVal(charID=charID, orderID=orderID)
            self.favorites.insert(orderID, newFavorite)
        finally:
            setattr(self, 'isChangingOrder', False)

    def CloseWatchlistWindow(self):
        WatchListPanel.CloseIfOpen()

    def CloseFleetSetupList(self):
        StoredFleetSetupListWnd.CloseIfOpen()

    def GetFavorites(self):
        return self.favorites

    def IsFavorite(self, charid):
        if self.GetFavorite(charid):
            return True
        else:
            return False

    def GetMemberInfo(self, charID, fleetHierarchy = None):
        member = self.members.get(charID, None)
        if member is None:
            return
        wing = self.wings.get(member.wingID, None)
        wingName = squadName = ''
        fleet = fleetHierarchy or self.GetFleetHierarchy()
        if wing:
            wingName = WingName(fleet, wingID=member.wingID)
            squad = wing.squads.get(member.squadID, None)
            if squad:
                squadName = SquadronName(fleet, squadID=member.squadID)
        jobName = ''
        if member.job & evefleet.fleetJobCreator:
            jobName = localization.GetByLabel('UI/Fleet/Ranks/Boss')
        roleName = fleetbroadcastexports.GetRankName(member)
        return KeyVal(charID=charID, charName=cfg.eveowners.Get(charID).name, wingID=member.wingID, wingName=wingName, squadID=member.squadID, squadName=squadName, role=member.role, roleName=roleName, job=member.job, jobName=jobName)

    def GetWatchlistMembers(self):
        if self.isDamageUpdates:
            return [ f.charID for f in self.favorites ]

    def RegisterForDamageUpdates(self):
        fav = self.GetWatchlistMembers()
        sm.RemoteSvc('fleetMgr').RegisterForDamageUpdates(fav)

    def Regroup(self):
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdFleetRegroup()
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fleet/Regrouping')})

    def GetNearestBall(self, fromBall = None, getDist = 0):
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            return
        lst = []
        validNearBy = {groupAsteroidBelt,
         groupMoon,
         groupPlanet,
         groupWarpGate,
         groupStargate,
         groupStation} | evetypes.GetGroupIDsByCategory(const.categoryStructure)
        for ballID, ball in ballPark.balls.iteritems():
            slimItem = ballPark.GetInvItem(ballID)
            if slimItem and slimItem.groupID in validNearBy:
                if fromBall:
                    dist = trinity.TriVector(ball.x - fromBall.x, ball.y - fromBall.y, ball.z - fromBall.z).Length()
                    lst.append((dist, ball))
                else:
                    lst.append((ball.surfaceDist, slimItem))

        lst.sort()
        if getDist:
            return lst[0]
        if lst:
            return lst[0][1]

    def CurrentFleetBroadcastOnItem(self, itemID, gbType = None):
        currGBID, currGBType, currGBData = self.currentBroadcastOnItem.get(itemID, (None, None, None))
        if gbType in (None, currGBType):
            return currGBData
        else:
            return

    def GetCurrentFleetBroadcastOnItem(self, itemID):
        return self.currentBroadcastOnItem.get(itemID, (None, None, None))

    def GetCurrentFleetBroadcasts(self):
        return self.currentBroadcastOnItem

    def CheckIsInFleet(self, inSpace = False):
        if self.fleet is None:
            if inSpace:
                raise UserError('FleetNotInFleetInSpace')
            raise UserError('FleetNotInFleet')
        if inSpace:
            if not session.solarsystemid:
                raise UserError('FleetCannotDoInStation')
            if IsDockedInStructure():
                raise UserError('FleetCannotDoInStructure')

    def CheckCanAddFavorite(self, charid):
        if charid == session.charid:
            return False
        if self.fleet is None:
            return False
        if self.IsFavorite(charid):
            return False
        return True

    def GetFleetLocationAndInfo(self):
        ret = sm.GetService('michelle').GetRemotePark().GetFleetLocationAndInfo()
        for memberID, inf in ret.iteritems():
            ball = KeyVal(x=inf.pos[0], y=inf.pos[1], z=inf.pos[2])
            nearestBallID = self.GetNearestBall(ball).itemID
            inf.nearestBallID = nearestBallID

        return ret

    def GetFleetComposition(self):
        if self.fleet is None:
            return
        now = blue.os.GetWallclockTime()
        if self.fleetCompositionTimestamp < now:
            self.LogInfo('Fetching fleet composition')
            self.fleetComposition = self.fleet.GetFleetComposition()
            self.fleetCompositionTimestamp = now + FLEETCOMPOSITION_CACHE_TIME * SEC
        return self.fleetComposition

    def DistanceToFleetMate(self, solarSystemID, nearID):
        toSystem = cfg.evelocations.Get(solarSystemID)
        if toSystem is None or session.solarsystemid2 is None:
            raise AttributeError('Invalid solarsystem')
        fromSystem = cfg.evelocations.Get(session.solarsystemid2)
        dist = uix.GetLightYearDistance(fromSystem, toSystem)
        if dist is None:
            eve.Message('MapDistanceUnknown', {'fromSystem': cfg.FormatConvert(UE_LOCID, session.solarsystemid2),
             'toSystem': cfg.FormatConvert(UE_LOCID, solarSystemID)})
        else:
            jumps = self.clientPathfinderService.GetJumpCountFromCurrent(solarSystemID)
            eve.Message('MapDistance', {'fromSystem': cfg.FormatConvert(UE_LOCID, session.solarsystemid2),
             'toSystem': cfg.FormatConvert(UE_LOCID, solarSystemID),
             'dist': dist,
             'jumps': jumps})

    def RejectJoinRequest(self, charID):
        self.fleet.RejectJoinRequest(charID)

    def CanUpdateAdvert(self):
        if session.fleetid is None:
            return False
        if not self.IsBoss():
            return False
        if not self.IsFleetRegistered():
            return False
        return True

    def IsFleetRegistered(self):
        return getattr(self.options, 'isRegistered', False)

    def RemoveAndUpdateFleetFinderAdvert(self, what):
        if not self.CanUpdateAdvert():
            return
        fleetAd = self.RemoveFleetFinderAdvert()
        if fleetAd:
            if eve.Message('FleetUpdateFleetFinderAd_%s' % what, {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                sm.GetService('agencyNew').OpenWindow(contentGroupConst.contentGroupFleetUpRegister)

    def TryUpdateFleetFinderAdvertWithNewBoss(self):
        if not self.CanUpdateAdvert():
            return
        advertInfo = self.GetMyFleetFinderAdvert()
        if advertInfo and advertInfo.updateOnBossChange:
            allowedInfoFromStandings = self.GetAllowedAndBannedEntitiesFromStandings(advertInfo)
            allowedEntitiesInfo = KeyVal(membergroups_allowedEntities=allowedInfoFromStandings['membergroupsAllowedEntities'], public_allowedEntities=allowedInfoFromStandings['publicAllowedEntities'], membergroups_disallowedEntities=allowedInfoFromStandings['membergroupsDisallowedEntities'], public_disallowedEntities=allowedInfoFromStandings['publicDisallowedEntities'])
            fleetAdvert = self.UpdateFleetAdvertWithNewLeader(allowedEntitiesInfo)
            if fleetAdvert:
                self.currentFleetAd = fleetAdvert
                eve.Message('FleetUpdateFleetFinderAd_NewBoss2')
                return
        self.currentFleetAd = None
        self.RemoveAndUpdateFleetFinderAdvert('NewBoss')

    def BroadcastTimeRestriction(self, name):
        if self.IsTimeRestricted(name):
            self.LogInfo('Will not send broadcast', name, 'as not enough time has passed since the last one')
            return True
        else:
            self.lastBroadcast.name = name
            self.lastBroadcast.timestamp = blue.os.GetWallclockTime()
            return False

    def IsTimeRestricted(self, name):
        lastBroadcastTime = self.lastBroadcast.timestamp
        if self.lastBroadcast.name == name:
            nextAllowedBroadcast = lastBroadcastTime + MIN_BROADCAST_TIME * SEC
        else:
            nextAllowedBroadcast = lastBroadcastTime + int(float(MIN_BROADCAST_TIME) / 3.0 * float(SEC))
        if nextAllowedBroadcast > blue.os.GetWallclockTime():
            return True
        return False

    def SendGlobalBroadcast(self, name, itemID, typeID = None):
        self.CheckIsInFleet(inSpace=True)
        if self.BroadcastTimeRestriction(name):
            return
        if name not in evefleet.ALL_BROADCASTS:
            raise RuntimeError('Illegal broadcast')
        self.fleet.SendBroadcast(name, self.broadcastScope, itemID, typeID)

    def SendBubbleBroadcast(self, name, itemID, typeID = None):
        self.CheckIsInFleet(inSpace=True)
        if self.BroadcastTimeRestriction(name):
            return
        if name not in evefleet.ALL_BROADCASTS:
            raise RuntimeError('Illegal broadcast')
        sm.RemoteSvc('fleetMgr').BroadcastToBubble(name, self.broadcastScope, itemID, typeID)

    def SendSystemBroadcast(self, name, itemID, typeID = None):
        self.CheckIsInFleet(inSpace=True)
        if self.BroadcastTimeRestriction(name):
            return
        if name not in evefleet.ALL_BROADCASTS:
            raise RuntimeError('Illegal broadcast')
        sm.RemoteSvc('fleetMgr').BroadcastToSystem(name, self.broadcastScope, itemID, typeID)

    def SendBroadcast_EnemySpotted(self):
        nearestBall = self.GetNearestBall()
        nearID = None
        if nearestBall is not None:
            nearID = nearestBall.itemID
        self.SendGlobalBroadcast(evefleet.BROADCAST_ENEMY_SPOTTED, nearID)

    def SendBroadcast_NeedBackup(self):
        nearestBall = self.GetNearestBall()
        nearID = None
        if nearestBall is not None:
            nearID = nearestBall.itemID
        self.SendGlobalBroadcast(evefleet.BROADCAST_NEED_BACKUP, nearID)

    def SendBroadcast_HoldPosition(self):
        nearestBall = self.GetNearestBall()
        nearID = None
        if nearestBall is not None:
            nearID = nearestBall.itemID
        self.SendGlobalBroadcast(evefleet.BROADCAST_HOLD_POSITION, nearID)

    def SendBroadcast_TravelTo(self, solarSystemID):
        self.SendGlobalBroadcast(evefleet.BROADCAST_TRAVEL_TO, solarSystemID)

    def SendBroadcast_HealArmor(self):
        self.SendBubbleBroadcast(evefleet.BROADCAST_HEAL_ARMOR, session.shipid)

    def SendBroadcast_HealShield(self):
        self.SendBubbleBroadcast(evefleet.BROADCAST_HEAL_SHIELD, session.shipid)

    def SendBroadcast_HealCapacitor(self):
        self.SendBubbleBroadcast(evefleet.BROADCAST_HEAL_CAPACITOR, session.shipid)

    def SendBroadcast_Target(self, itemID):
        self.SendBubbleBroadcast(evefleet.BROADCAST_TARGET, itemID)

    def SendBroadcast_Heal_Target(self, itemID):
        self.SendBubbleBroadcast(evefleet.BROADCAST_REP_TARGET, itemID)

    def SendBroadcast_WarpToItemID(self, itemID):
        typeID = self._GetTypeIDForItemID(itemID)
        if not self.CanAlignOrWarpToTypeID(typeID):
            return
        return self.SendBroadcast_WarpTo(itemID, typeID)

    def SendBroadcast_AlignToItemID(self, itemID):
        typeID = self._GetTypeIDForItemID(itemID)
        if not self.CanAlignOrWarpToTypeID(typeID):
            return
        return self.SendBroadcast_AlignTo(itemID, typeID)

    def SendBroadcast_JumpToItemID(self, itemID):
        typeID = self._GetTypeIDForItemID(itemID)
        if typeID is None or evetypes.GetGroupID(typeID) != const.groupStargate:
            return
        return self.SendBroadcast_JumpTo(itemID, typeID)

    def _GetTypeIDForItemID(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        slimItem = bp.GetInvItem(itemID)
        if not slimItem:
            return None
        return slimItem.typeID

    def CanAlignOrWarpToTypeID(self, typeID):
        if typeID is None:
            return False
        categoryID = evetypes.GetCategoryID(typeID)
        if categoryID in (const.categoryEntity,
         const.categoryDrone,
         const.categoryShip,
         const.categoryFighter):
            return False
        return True

    def SendBroadcast_WarpTo(self, itemID, typeID):
        self.SendSystemBroadcast(evefleet.BROADCAST_WARP_TO, itemID, typeID)

    def SendBroadcast_AlignTo(self, itemID, typeID):
        self.SendSystemBroadcast(evefleet.BROADCAST_ALIGN_TO, itemID, typeID)

    def SendBroadcast_JumpTo(self, itemID, typeID):
        self.SendSystemBroadcast(evefleet.BROADCAST_JUMP_TO, itemID, typeID)

    def SendBroadcast_InPosition(self):
        nearestBall = self.GetNearestBall()
        nearID = None
        typeID = None
        if nearestBall is not None:
            nearID = nearestBall.itemID
            typeID = nearestBall.typeID
        self.SendGlobalBroadcast(evefleet.BROADCAST_IN_POSITION, nearID, typeID)

    def SendBroadcast_JumpBeacon(self):
        beacon = self.GetActiveBeaconForChar(session.charid)
        if beacon is None:
            raise UserError('NoActiveBeacon')
        self.SendGlobalBroadcast(evefleet.BROADCAST_JUMP_BEACON, beacon[1], beacon[2])

    def SendBroadcast_Location(self):
        locationID = session.solarsystemid2
        nearestBall = self.GetNearestBall()
        nearID = None
        if nearestBall is not None:
            nearID = nearestBall.itemID
        self.SendGlobalBroadcast('Location', nearID)

    def SendBroadcast(self, broadcastID, *args):
        if broadcastID == evefleet.BROADCAST_LOCATION:
            self.SendBroadcast_Location(*args)
        elif broadcastID == evefleet.BROADCAST_JUMP_BEACON:
            self.SendBroadcast_JumpBeacon(*args)
        elif broadcastID == evefleet.BROADCAST_HOLD_POSITION:
            self.SendBroadcast_HoldPosition(*args)
        elif broadcastID == evefleet.BROADCAST_TRAVEL_TO:
            self.SendBroadcast_TravelTo(*args)
        elif broadcastID == evefleet.BROADCAST_JUMP_TO:
            self.SendBroadcast_JumpTo(*args)
        elif broadcastID == evefleet.BROADCAST_ALIGN_TO:
            self.SendBroadcast_AlignTo(*args)
        elif broadcastID == evefleet.BROADCAST_NEED_BACKUP:
            self.SendBroadcast_NeedBackup(*args)
        elif broadcastID == evefleet.BROADCAST_WARP_TO:
            self.SendBroadcast_WarpTo(*args)
        elif broadcastID == evefleet.BROADCAST_HEAL_CAPACITOR:
            self.SendBroadcast_HealCapacitor(*args)
        elif broadcastID == evefleet.BROADCAST_HEAL_SHIELD:
            self.SendBroadcast_HealShield(*args)
        elif broadcastID == evefleet.BROADCAST_HEAL_ARMOR:
            self.SendBroadcast_HealArmor(*args)
        elif broadcastID == evefleet.BROADCAST_TARGET:
            self.SendBroadcast_Target(*args)
        elif broadcastID == evefleet.BROADCAST_REP_TARGET:
            self.SendBroadcast_Heal_Target(*args)
        elif broadcastID == evefleet.BROADCAST_ENEMY_SPOTTED:
            self.SendBroadcast_EnemySpotted(*args)
        elif broadcastID == evefleet.BROADCAST_IN_POSITION:
            self.SendBroadcast_InPosition(*args)

    def OnFleetWingNameChanged(self, wingID, name):
        self.wings = self.fleet.GetWings()
        sm.ScatterEvent('OnFleetWingNameChanged_Local', wingID, name)
        sm.ScatterEvent('OnMyFleetInfoChanged')

    def OnFleetSquadNameChanged(self, squadID, name):
        self.wings = self.fleet.GetWings()
        sm.ScatterEvent('OnFleetSquadNameChanged_Local', squadID, name)
        sm.ScatterEvent('OnMyFleetInfoChanged')

    def OnFleetInvite(self, fleetID, inviteID, msgName, msgDict):
        autoAccept = msgDict.get('autoAccept', False)
        __fleetMoniker = GetFleet(fleetID)
        if session.fleetid is not None:
            __fleetMoniker.RejectInvite(True)
            return
        if settings.user.ui.Get('autoRejectInvitations', 0) and self.expectingInvite != fleetID and not autoAccept:
            __fleetMoniker.RejectInvite(False)
            return
        if CommandBlockerService.instance().is_blocked(['window.open.fleetwindow']):
            __fleetMoniker.RejectInvite(False)
            return
        self.expectingInvite = None
        try:
            name = evelink.character_link(inviteID)
            msgDict['name'] = name
            if autoAccept or eve.Message(msgName, msgDict, uiconst.YESNO, default=uiconst.ID_NO, modal=False) == uiconst.ID_YES:
                self.sessionMgr.PerformSelectiveSessionChange('fleet.', 'fleet.acceptinvite', True, __fleetMoniker.AcceptInvite, self.GetMyShipTypeID())
                self.fleet = __fleetMoniker
                self.InitFleet()
            else:
                __fleetMoniker.RejectInvite()
        except UserError as e:
            eve.Message(e.msg, e.dict)

    def OnFleetJoin(self, member):
        if member.charID == session.charid:
            self.InitFleet()
            sm.GetService('tactical').InvalidateFlags()
        else:
            self.members[member.charID] = member
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/MemberHistoryJoined', charID=member.charID, role=fleetbroadcastexports.GetRankName(member))
            self.AddToMemberHistory(member.charID, label)
            self.UpdateFleetFinderInfo()
            sm.GetService('tactical').InvalidateFlagsExtraLimited(member.charID)
        sm.ScatterEvent('OnFleetJoin_Local', member)

    def OnFleetJoinReject(self, memberID, reasonCode):
        if reasonCode and reasonCode in evefleet.fleetRejectionReasons:
            reason = localization.GetByLabel(evefleet.fleetRejectionReasons[reasonCode])
            msg = localization.GetByLabel('UI/Fleet/InviteRejectedWithReason', charID=memberID, reason=reason)
        else:
            msg = localization.GetByLabel('UI/Fleet/InviteRejected', charID=memberID)
        eve.Message('CustomNotify', {'notify': msg})

    def OnFleetLeave(self, charID):
        self._OnFleetLeave(charID)

    def _OnFleetLeave(self, charID):
        label = localization.GetByLabel('UI/Fleet/FleetBroadcast/MemberHistoryLeft', charID=charID)
        self.AddToMemberHistory(charID, label)
        if charID == session.charid:
            self.Clear()
        if charID in self.members:
            rec = self.members.pop(charID)
            sm.GetService('tactical').InvalidateFlagsExtraLimited(charID)
        else:
            rec = KeyVal(charID=charID)
        if charID in self.activeModuleBeacons:
            del self.activeModuleBeacons[charID]
        if charID in self.activeBridge:
            del self.activeBridge[charID]
        if self.GetFavorite(charID):
            self.RemoveFavorite(charID)
        if charID == self.leader:
            self.leader = None
        if charID != session.charid:
            self.UpdateFleetFinderInfo()
        sm.ScatterEvent('OnFleetLeave_Local', rec)

    def OnFleetDisbanded(self, charIDs):
        for charID in charIDs:
            self._OnFleetLeave(charID)

    def OnFleetMemberChanged(self, charID, fleetID, oldWingID, oldSquadID, oldRole, oldJob, oldMemberOptOuts, newWingID, newSquadID, newRole, newJob, newMemberOptOuts, isOnlyMember):
        self.members[charID] = KeyVal()
        self.members[charID].charID = charID
        self.members[charID].wingID = newWingID
        self.members[charID].squadID = newSquadID
        self.members[charID].role = newRole
        self.members[charID].job = newJob
        self.members[charID].memberOptOuts = newMemberOptOuts
        sm.ScatterEvent('OnFleetMemberChanged_Local', charID, fleetID, oldWingID, oldSquadID, oldRole, oldJob, oldMemberOptOuts, newWingID, newSquadID, newRole, newJob, newMemberOptOuts)
        if oldRole != newRole:
            roleLabel = localization.GetByLabel('UI/Fleet/FleetBroadcast/MemberHistoryChangedRole', charID=charID, role=fleetbroadcastexports.GetRoleName(newRole))
            self.AddToMemberHistory(charID, roleLabel)
        if oldJob != newJob:
            if newJob & evefleet.fleetJobCreator:
                jobLabel = localization.GetByLabel('UI/Fleet/FleetBroadcast/MemberHistoryIsBoss', charID=charID)
            else:
                jobLabel = localization.GetByLabel('UI/Fleet/FleetBroadcast/MemberHistoryIsNotBoss', charID=charID)
            self.AddToMemberHistory(charID, jobLabel)
        if newRole not in (None, -1):
            self.UpdateTargetBroadcasts(charID)
        if charID == session.charid:
            self.fleetCompositionTimestamp = 0
            sm.ScatterEvent('OnMyFleetInfoChanged')
            if oldJob & evefleet.fleetJobCreator == 0 and newJob & evefleet.fleetJobCreator > 0:
                self.TryUpdateFleetFinderAdvertWithNewBoss()
            elif oldJob & evefleet.fleetJobCreator > 0 and newJob & evefleet.fleetJobCreator == 0:
                self.currentFleetAd = None
        if newJob != oldJob or newRole != oldRole:
            info = self.GetMemberInfo(charID)
            if newJob != oldJob:
                r = info.jobName
            elif newRole != oldRole:
                r = info.roleName

    def OnFleetMoveFailed(self, charID, isKicked):
        if isKicked:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fleet/MoveFailedKicked', charID=charID)})
        else:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fleet/MoveFailed', charID=charID)})

    def OnFleetWingAdded(self, wingID):
        self.wings = self.fleet.GetWings()
        sm.ScatterEvent('OnFleetWingAdded_Local', wingID)

    def OnFleetWingDeleted(self, wingID):
        self.wings = self.fleet.GetWings()
        sm.ScatterEvent('OnFleetWingDeleted_Local', wingID)

    def OnFleetSquadAdded(self, wingID, squadID):
        self.wings = self.fleet.GetWings()
        sm.ScatterEvent('OnFleetSquadAdded_Local', wingID, squadID)

    def OnFleetSquadDeleted(self, squadID):
        self.wings = self.fleet.GetWings()
        sm.ScatterEvent('OnFleetSquadDeleted_Local', squadID)

    def OnFleetOptionsChanged(self, oldOptions, options):
        self.options = options
        if self.options.isRegistered != oldOptions.isRegistered:
            self.GetFleetAdsForChar_Memoized.clear_memoized()
            sm.ScatterEvent('OnFleetFinderAdvertChanged')
            if self.options.isRegistered:
                self.AddBroadcast('FleetFinderAdvertAdded', evefleet.BROADCAST_NONE, self.GetBossID(), broadcastName=localization.GetByLabel('UI/Fleet/FleetBroadcast/FleetFinderAdvertAdded'))
        if options.isFreeMove != oldOptions.isFreeMove:
            self.AddBroadcast('FleetOptionsChanged', evefleet.BROADCAST_NONE, self.GetBossID(), broadcastName=[localization.GetByLabel('UI/Fleet/FleetBroadcast/FreeMoveUnset'), localization.GetByLabel('UI/Fleet/FleetBroadcast/FreeMoveSet')][options.isFreeMove])
        sm.ScatterEvent('OnFleetOptionsChanged_Local', oldOptions, options)

    def OnMemberlessFleetUnregistered(self):
        self.GetFleetAdsForChar_Memoized.clear_memoized()

    def OnJoinedFleet(self):
        self.RefreshFleetWindow()

    def OnLeftFleet(self):
        self.CloseFleetWindowAndReopenIfNeeded()
        self.CloseWatchlistWindow()
        self.CloseFleetCompositionWindow()
        self.CloseJoinRequestWindow()
        self.CloseRegisterFleetWindow()
        self.CloseFleetBroadcastWindow()
        self.CloseFleetSetupList()

    def OnFleetJoinRequest(self, info):
        self.joinRequests[info.charID] = info
        eve.Message('FleetMemberJoinRequest', {'name': (UE_OWNERID, info.charID),
         'corpname': (UE_OWNERID, info.corpID)})
        self.OpenJoinRequestWindow()

    def OnFleetJoinRejected(self, charID):
        eve.Message('FleetJoinRequestRejected', {'name': (UE_OWNERID, charID)})

    def OnJoinRequestUpdate(self, joinRequests):
        self.joinRequests = joinRequests
        self.OpenJoinRequestWindow()

    def OnContactChange(self, contactIDs, contactType = None):
        self.UpdateAllowedEntitiesInAdvert()

    def OpenJoinRequestWindow(self):
        self.CloseJoinRequestWindow()
        FleetJoinRequestWindow.Open()

    def CloseJoinRequestWindow(self):
        FleetJoinRequestWindow.CloseIfOpen()

    def OpenFleetCompositionWindow(self):
        self.CloseFleetCompositionWindow()
        FleetComposition.Open()

    def CloseFleetCompositionWindow(self):
        FleetComposition.CloseIfOpen()

    def CloseFleetBroadcastWindow(self):
        BroadcastSettings.CloseIfOpen()

    def OpenRegisterFleetWindow(self, info = None):
        if session.fleetid is None:
            raise UserError('FleetNotFound')
        if not self.IsBoss():
            raise UserError('FleetNotCreator')
        if info is None and self.options.isRegistered:
            info = self.GetCurrentAdvertForMyFleet()
        self.CloseRegisterFleetWindow()
        RegisterFleetWindow.Open(fleetInfo=info)

    def CloseRegisterFleetWindow(self):
        RegisterFleetWindow.CloseIfOpen()

    def RefreshFleetWindow(self):
        self.InitFleet()
        self.CloseFleetWindow()
        FleetWindow.Open()

    def CloseFleetWindowAndReopenIfNeeded(self):
        wnd = FleetWindow.GetIfOpen()
        if wnd:
            self.InitFleet()
            self.RefreshFleetWindow()

    def CloseFleetWindow(self):
        FleetWindow.CloseIfOpen()

    def AddBroadcast(self, name, scope, charID, solarSystemID = None, itemID = None, broadcastName = None, typeID = None):
        time = blue.os.GetWallclockTime()
        spaceAndOptionalGroupName = ' '
        msgLocationID = itemID
        if typeID is not None and itemID is not None and name in [evefleet.BROADCAST_IN_POSITION,
         evefleet.BROADCAST_WARP_TO,
         evefleet.BROADCAST_ALIGN_TO,
         evefleet.BROADCAST_JUMP_TO,
         evefleet.BROADCAST_TRAVEL_TO]:
            groupID = evetypes.GetGroupID(typeID)
            if groupID in (groupStargate, groupSkyhook):
                spaceAndOptionalGroupName = ' %s ' % localization.CleanImportantMarkup(evetypes.GetGroupName(typeID))
            if groupID == groupSkyhook:
                planetID = self._GetPlanetIDFromSlimItem(itemID)
                if planetID:
                    msgLocationID = planetID
        typeIDForBroadcast = None
        if name == evefleet.BROADCAST_ENEMY_SPOTTED:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventEnemySpotted', charID=charID)
        elif name == evefleet.BROADCAST_NEED_BACKUP:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventNeedBackup', charID=charID)
        elif name == evefleet.BROADCAST_HEAL_ARMOR:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventHealArmor', charID=charID)
            label += self._GetTypeNameTextFromBroadcastedItemID(itemID)
        elif name == evefleet.BROADCAST_HEAL_SHIELD:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventHealShield', charID=charID)
            label += self._GetTypeNameTextFromBroadcastedItemID(itemID)
        elif name == evefleet.BROADCAST_HEAL_CAPACITOR:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventHealCapacitor', charID=charID)
            label += self._GetTypeNameTextFromBroadcastedItemID(itemID)
        elif name == evefleet.BROADCAST_IN_POSITION:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventInPosition2', charID=charID, locationID=msgLocationID, spaceAndOptionalGroupName=spaceAndOptionalGroupName)
        elif name == evefleet.BROADCAST_HOLD_POSITION:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventHoldPosition', charID=charID)
        elif name == evefleet.BROADCAST_JUMP_BEACON:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventJumpToBeacon', charID=charID)
            typeIDForBroadcast = typeID
        elif name == evefleet.BROADCAST_LOCATION:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventLocation', charID=charID, solarsystemID=solarSystemID)
        elif name == evefleet.BROADCAST_WARP_TO:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventWarpTo2', charID=charID, locationID=msgLocationID, spaceAndOptionalGroupName=spaceAndOptionalGroupName)
        elif name == evefleet.BROADCAST_ALIGN_TO:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventAlignTo2', charID=charID, locationID=msgLocationID, spaceAndOptionalGroupName=spaceAndOptionalGroupName)
        elif name == evefleet.BROADCAST_JUMP_TO:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventJumpTo2', charID=charID, locationID=msgLocationID, spaceAndOptionalGroupName=spaceAndOptionalGroupName)
        elif name == evefleet.BROADCAST_TRAVEL_TO:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventTravelTo2', charID=charID, locationID=msgLocationID, spaceAndOptionalGroupName=spaceAndOptionalGroupName)
        elif name == evefleet.BROADCAST_TARGET:
            targetName, targetTypeName = self._GetTargetNameAndType(itemID)
            if targetName is not None and targetTypeName is not None:
                label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventTargetWithType', targetName=targetName, targetTypeName=targetTypeName)
            else:
                label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventTarget')
        elif name == evefleet.BROADCAST_REP_TARGET:
            targetName, targetTypeName = self._GetTargetNameAndType(itemID)
            if targetName is not None and targetTypeName is not None:
                label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventHealTargetWithType', targetName=targetName, targetTypeName=targetTypeName)
            else:
                label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventHealTarget')
        elif broadcastName is not None:
            label = broadcastName
        else:
            log.LogTraceback('Unknown broadcast label:%s' % name)
            label = 'Unknown broadcast label:%s' % name
        where = fleetbroadcastexports.GetBroadcastWhere(name)
        broadcast = KeyVal(name=name, charID=charID, solarSystemID=solarSystemID, itemID=itemID, time=time, broadcastLabel=label, scope=scope, where=where, typeID=typeIDForBroadcast)
        self.broadcastHistory.insert(0, broadcast)
        if len(self.broadcastHistory) > MAX_NUM_BROADCASTS:
            self.broadcastHistory.pop()
        if self.WantBroadcast(name, charID):
            sm.ScatterEvent('OnFleetBroadcast_Local', broadcast)

    def _GetTargetNameAndType(self, itemID):
        m = sm.GetService('michelle')
        bp = m.GetBallpark()
        slimItem = bp.GetInvItem(itemID)
        if slimItem is None:
            return (None, None)
        targetName = uix.GetSlimItemName(slimItem)
        targetTypeName = evetypes.GetName(slimItem.typeID)
        return (targetName, targetTypeName)

    def _GetTypeNameTextFromBroadcastedItemID(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return ''
        slimItem = bp.GetInvItem(itemID)
        if slimItem is not None:
            return ' (%s)' % evetypes.GetName(slimItem.typeID)
        return ''

    def _GetPlanetIDFromSlimItem(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.GetInvItem(itemID)
        if slimItem is not None:
            return slimItem.planetID

    def WantBroadcast(self, name, charID):
        if name not in iconsByBroadcastType:
            name = 'Event'
        if charID == session.charid:
            if settings.user.ui.Get(LISTEN_BROADCAST_SETTING % BROADCAST_SHOW_OWN, False):
                return True
        if settings.user.ui.Get(LISTEN_BROADCAST_SETTING % name, True):
            return True
        return False

    def OnFleetBroadcast(self, name, scope, charID, solarSystemID, itemID, typeID):
        self.LogInfo('OnFleetBroadcast', name, scope, charID, solarSystemID, itemID, ' I now have', len(self.broadcastHistory) + 1, 'broadcasts in my history')
        self.AddBroadcast(name, scope, charID, solarSystemID, itemID, typeID=typeID)
        if name == evefleet.BROADCAST_TARGET:
            targets = self.targetBroadcasts.setdefault(charID, [])
            if itemID in targets:
                targets.remove(itemID)
                targets.insert(0, itemID)
            else:
                targets.append(itemID)
            self.UpdateTargetBroadcasts(charID)
        else:
            stateID = getattr(state, 'gb%s' % name)
            self.BroadcastState(itemID, stateID, charID)

    def BroadcastState(self, itemID, brState, *data):
        gbID = self.NewFleetBroadcastID()
        self.currentBroadcastOnItem[itemID] = (gbID, brState, data)
        sm.GetService('stateSvc').SetState(itemID, brState, True, gbID, *data)
        blue.pyos.synchro.SleepWallclock(FLEETBROADCASTTIMEOUT * 1000)
        savedgbid, savedgbtype, saveddata = self.currentBroadcastOnItem.get(itemID, (None, None, None))
        if savedgbid == gbID:
            sm.GetService('stateSvc').SetState(itemID, brState, False, gbID, *data)
            del self.currentBroadcastOnItem[itemID]

    def CycleBroadcastScope(self):
        if self.broadcastScope == evefleet.BROADCAST_DOWN:
            self.broadcastScope = evefleet.BROADCAST_UP
        elif self.broadcastScope == evefleet.BROADCAST_UP:
            self.broadcastScope = evefleet.BROADCAST_ALL
        else:
            self.broadcastScope = evefleet.BROADCAST_DOWN
        settings.user.ui.Set('fleetBroadcastScope', self.broadcastScope)
        eve.Message('FleetBroadcastScopeChange', {'name': fleetbroadcastexports.GetBroadcastScopeName(self.broadcastScope)})
        sm.ScatterEvent('OnBroadcastScopeChange')

    def OnFleetLootEvent(self, lootEvents):
        for k, v in lootEvents.iteritems():
            loot = KeyVal(charID=k[0], solarSystemID=session.solarsystemid2, typeID=k[1], quantity=v, time=blue.os.GetWallclockTime())
            for i, l in enumerate(self.lootHistory):
                if (l.typeID, l.charID, l.solarSystemID) == (loot.typeID, loot.charID, loot.solarSystemID):
                    self.lootHistory[i].quantity += loot.quantity
                    self.lootHistory[i].time = loot.time
                    break
            else:
                self.lootHistory.insert(0, loot)

        if len(self.lootHistory) > MAX_NUM_LOOTEVENTS:
            self.lootHistory.pop()
        sm.ScatterEvent('OnFleetLootEvent_Local')

    def GetLootHistory(self):
        return self.lootHistory

    def GetBroadcastHistory(self):
        history = [ h for h in self.broadcastHistory if self.WantBroadcast(h.name, h.charID) ]
        return history

    def AddToMemberHistory(self, charID, event):
        self.memberHistory.insert(0, KeyVal(charID=charID, event=event, time=blue.os.GetWallclockTime()))
        if len(self.memberHistory) > MAX_NUM_BROADCASTS:
            self.memberHistory.pop()

    def GetMemberHistory(self):
        return self.memberHistory

    def UpdateTargetBroadcasts(self, charID):

        def BroadcastWithLabel(itemID, label):
            gbID = self.NewFleetBroadcastID()
            self.currentTargetBroadcast[itemID] = gbID
            self.BroadcastState(itemID, state.gbTarget, charID, label)
            if self.currentTargetBroadcast.get(itemID) == gbID:
                self.targetBroadcasts[charID].remove(itemID)

        role = self.members[charID].role
        for i, id_ in enumerate(self.targetBroadcasts.get(charID, [])):
            gbID, gbType, data = self.currentBroadcastOnItem.get(id_, (None, None, None))
            if gbType == state.gbTarget:
                prevCharID, number = data
                if self.IsSuperior(charID, prevCharID):
                    continue
            if role == evefleet.fleetRoleSquadCmdr:
                label = localization.GetByLabel('UI/Fleet/FleetBroadcast/TargetCodeFleet', targetID=i + 1)
            elif role == evefleet.fleetRoleSquadCmdr:
                label = localization.GetByLabel('UI/Fleet/FleetBroadcast/TargetCodeWing', targetID=i + 1)
            elif role == evefleet.fleetRoleSquadCmdr:
                label = localization.GetByLabel('UI/Fleet/FleetBroadcast/TargetCodeSquad', targetID=i + 1)
            else:
                label = localization.GetByLabel('UI/Fleet/FleetBroadcast/TargetCodeMember', targetID=i + 1)
            uthread.pool('FleetSvc::UpdateTargetBroadcasts', BroadcastWithLabel, id_, label)

    @Memoize
    def GetRankOrder(self):
        return [evefleet.fleetRoleMember,
         evefleet.fleetRoleSquadCmdr,
         evefleet.fleetRoleWingCmdr,
         evefleet.fleetRoleLeader]

    def IsSuperior(self, charID, otherCharID):

        def Rank(charID):
            return self.GetRankOrder().index(self.members[charID].role)

        return Rank(charID) > Rank(otherCharID)

    def NewFleetBroadcastID(self):
        if not hasattr(self, 'lastFleetBroadcastID'):
            self.lastFleetBroadcastID = 0
        self.lastFleetBroadcastID += 1
        return self.lastFleetBroadcastID

    def ProcessSessionChange(self, isRemote, session, change):
        if 'fleetid' in change:
            self.activeModuleBeacons = {}
            self.activeDeployableBeacons = {}
            self.activeBridge = {}
            self.initedFleet = None
            myrec = self.members.get(session.charid, KeyVal(charID=session.charid))
            self.members = {}
            self.leader = None
            if change['fleetid'][1] is None:
                self.fleet = None
                self.favorites = []
                sm.ScatterEvent('OnFleetLeave_Local', myrec)
                sm.ScatterEvent('OnLeftFleet')
            else:
                sm.ScatterEvent('OnJoinedFleet')
            sm.GetService('tactical').InvalidateFlags()
        if 'solarsystemid' in change:
            self.CleanupBroadcasts()
            if session.solarsystemid is not None and session.fleetid is not None:
                self.RegisterForDamageUpdates()
            self.UpdateFleetInfo()
        if 'shipid' in change or 'structureid' in change:
            self.UpdateFleetInfo()
        if 'charid' in change:
            if change['charid'][1] is not None:
                uthread.new(self.AttemptReconnectLazy)
        if 'corpid' in change:
            uthread.new(self.RemoveAndUpdateFleetFinderAdvert, 'ChangedCorp')

    def AttemptReconnectLazy(self):
        blue.pyos.synchro.SleepSim(RECONNECT_DELAY * 1000)
        try:
            if session.fleetid is not None or session.charid is None:
                return
            fleetReconnect = settings.char.ui.Get('fleetReconnect', None)
            if fleetReconnect:
                if fleetReconnect[1] > blue.os.GetWallclockTime() - evefleet.RECONNECT_TIMEOUT * MIN:
                    self.LogNotice('I will try to reconnect to a lost fleet', fleetReconnect[0])
                    fleet = GetFleet(fleetReconnect[0])
                    fleet.Reconnect()
                else:
                    self.LogInfo('Reconnect request', fleetReconnect, ' out of date')
        except Exception as e:
            self.LogWarn('Unable to reconnect. Error =', e)
        finally:
            settings.char.ui.Set('fleetReconnect', None)

    def UpdateFleetFinderInfo(self):
        if session.fleetid is None:
            return
        if not self.updateAdvertThreadRunning and self.IsBoss() and self.options.isRegistered:
            self.updateAdvertThreadRunning = True
            uthread.worker('Fleet::UpdateAdvertInfoThread', self.UpdateAdvertInfoThread)

    def UpdateAdvertInfoThread(self):
        try:
            self.LogInfo('Starting UpdateAdvertInfoThread...')
            self.updateAdvertThreadRunning = True
            blue.pyos.synchro.SleepWallclock(UPDATEFLEETFINDERDELAY * 1000)
            if session.fleetid is None:
                return
            if self.IsBoss() and self.options.isRegistered:
                numMembers = len(self.members)
                allowedInfoFromStandings = self.GetAllowedAndBannedEntitiesFromStandings(self.currentFleetAd)
                allowedDiffBundle = GetDiffInAllowedAndBanned(self.currentFleetAd, allowedInfoFromStandings)
                self.LogInfo('Calling UpdateAdvertInfo', session.solarsystemid2, numMembers, allowedDiffBundle)
                advertInfo = self.UpdateAdvertInfo(numMembers, KeyVal(allowedDiffBundle))
                if advertInfo:
                    self.currentFleetAd = advertInfo
        finally:
            self.updateAdvertThreadRunning = False

    def GetAllowedAndBannedEntitiesFromStandings(self, currentAd):
        membergroupsAllowedEntities = set()
        publicAllowedEntities = set()
        membergroupsDisallowedEntities = set()
        publicDisallowedEntities = set()
        ret = {'membergroupsAllowedEntities': membergroupsAllowedEntities,
         'publicAllowedEntities': publicAllowedEntities,
         'membergroupsDisallowedEntities': membergroupsDisallowedEntities,
         'publicDisallowedEntities': publicDisallowedEntities}
        addressbookSvc = sm.GetService('addressbook')
        if currentAd.IsOpenToMemberEntities():
            membergroupsMinStanding = currentAd.membergroups_minStanding
            if membergroupsMinStanding is None:
                membergroupsAllowedEntities.update(self.GetAllowedGroupIDs(KeyVal(inviteScope=currentAd.inviteScope)))
            else:
                atOrAboveStanding, belowStanding = addressbookSvc.GetContactsAboveAndBelowRelationship(membergroupsMinStanding)
                membergroupsAllowedEntities.update(atOrAboveStanding)
                if membergroupsMinStanding <= 0:
                    membergroupsDisallowedEntities.update(belowStanding)
        publicMinStanding = currentAd.public_minStanding
        if publicMinStanding is not None:
            atOrAboveStanding, belowStanding = addressbookSvc.GetContactsAboveAndBelowRelationship(publicMinStanding)
            publicAllowedEntities.update(atOrAboveStanding)
            if publicMinStanding <= 0:
                publicDisallowedEntities.update(belowStanding)
        return ret

    def UpdateAllowedEntitiesInAdvert(self):
        if session.fleetid is None or not self.IsBoss() or not self.options.isRegistered:
            return
        allowedInfoFromStandings = self.GetAllowedAndBannedEntitiesFromStandings(self.currentFleetAd)
        advertInfo = self.UpdateAdvertAllowedEntities(allowedInfoFromStandings)
        self.currentFleetAd = advertInfo

    def UpdateFleetInfo(self):
        if session.fleetid is None:
            return
        self.UpdateFleetFinderInfo()
        if not self.updateThreadRunning:
            self.updateThreadRunning = True
            uthread.worker('Fleet::UpdateFleetInfoThread', self.UpdateFleetInfoThread)

    def UpdateFleetInfoThread(self):
        try:
            self.LogInfo('Starting UpdateFleetInfoThread...')
            self.updateThreadRunning = True
            blue.pyos.synchro.SleepWallclock(UPDATEFLEETMEMBERDELAY_SEC * 1000)
            if session.fleetid is None:
                return
            self.LogInfo('Calling UpdateMemberInfo')
            self.fleet.UpdateMemberInfo(self.GetMyShipTypeID())
        finally:
            self.updateThreadRunning = False

    def OnFleetMove(self):
        oldSquadID = session.squadid
        oldWingID = session.wingid
        self.sessionMgr.PerformSelectiveSessionChange('fleet.', 'fleet.finishmove', True, self.fleet.FinishMove)

    def IsBoss(self):
        myrec = self.GetMembers().get(session.charid)
        return bool(myrec and myrec.job & evefleet.fleetJobCreator)

    def IsCommanderOrBoss(self):
        return self.IsBoss() or session.fleetrole in evefleet.fleetCmdrRoles

    def GetAutoJoinSquadID(self):
        if not session.fleetid:
            return
        return self.options.autoJoinSquadID

    def GetBossID(self):
        myrec = self.GetMembers()
        for mid, m in self.members.iteritems():
            if m.job & evefleet.fleetJobCreator:
                return mid

    def IsMySubordinate(self, charID):
        member = self.members.get(charID, None)
        if member is None:
            return False
        isSubordinate = False
        if session.fleetrole == evefleet.fleetRoleLeader or session.fleetrole == evefleet.fleetRoleWingCmdr and member.wingID == session.wingid or session.fleetrole == evefleet.fleetRoleSquadCmdr and member.squadID == session.squadid:
            isSubordinate = True
        return isSubordinate

    def CreateAndRegisterFleet(self, adInfo):
        if session.fleetid:
            if adInfo:
                self.RegisterFleet(adInfo)
            elif self.IsFleetRegistered():
                self.RemoveFleetFinderAdvert()
        else:
            adInfoData = adInfo.GetData() if adInfo else None
            self.CreateFleet(adInfoData=adInfoData)
            self.LogFleetCreation(self.fleetID, evefleet.CREATE_SOURCE_FLEETUP)
        self.GetFleetAdsForChar_Memoized.clear_memoized()

    def RegisterFleet(self, adInfo):
        self.LogInfo('RegisterFleet', adInfo.GetData())
        if session.fleetid is None:
            raise UserError('FleetNotFound')
        if not self.IsBoss():
            raise UserError('FleetNotCreator')
        isEdit = self.options.isRegistered
        createdAdInfo = self.AddFleetFinderAdvert(adInfo)
        self._FinializeRegistration(createdAdInfo, isEdit)

    def _FinializeRegistration(self, createdAd, isEdit):
        if isEdit:
            sm.ScatterEvent('OnFleetFinderAdvertChanged')
        self.currentFleetAd = createdAd
        settings.char.ui.Set('fleetAdvert_lastAdvert', createdAd.GetData(fullAdvancedOptions=False))

    def UnregisterFleet(self):
        if session.fleetid is None:
            raise UserError('FleetNotFound')
        if not self.IsBoss():
            raise UserError('FleetNotCreator')
        if eve.Message('FleetRemoveFleetFinderAd', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.RemoveFleetFinderAdvert()
            self.currentFleetAd = None

    def GetFleetAdsForChar(self):
        fleetAdvertDictsForFleets = sm.ProxySvc('fleetProxy').GetAvailableFleetAds()
        return {k:FleetAdvertObject(**v) for k, v in fleetAdvertDictsForFleets.iteritems()}

    @Memoize(0.5)
    def GetFleetAdsForChar_Memoized(self):
        return self.GetFleetAdsForChar()

    def ApplyToJoinFleet(self, fleetID, autoAccept = False):
        if session.fleetid is not None:
            if session.fleetid == fleetID:
                raise UserError('FleetYouAreAlreadyInFleet')
            confirmChangeFleet = self._ConfirmChangeFleet()
            if not confirmChangeFleet:
                return
            self.LeaveFleet()
        self.expectingInvite = fleetID
        ret = sm.ProxySvc('fleetProxy').ApplyToJoinFleet(fleetID, autoAccept)
        if ret:
            raise UserError('FleetApplicationReceived')

    def _ConfirmChangeFleet(self):
        userInput = eve.Message('AskChangeFleet', buttons=uiconst.YESNO)
        return userInput == uiconst.ID_YES

    def AskJoinFleetFromLink(self, fleetID):
        fleets = self.GetFleetAdsForChar()
        if fleetID not in fleets:
            raise UserError('FleetJoinFleetFromLinkError')
        self.ApplyToJoinFleet(fleetID)
        self.LogFleetJoinAttempts(fleetID, evefleet.JOIN_SOURCE_LINK)

    def GetCurrentAdvertForMyFleet(self):
        if session.fleetid is None or not self.options.isRegistered:
            return
        fleetAd = self.GetMyFleetFinderAdvert()
        if fleetAd is None:
            return
        fleetAd.standing = None
        if fleetAd.Get('solarSystemID', 0):
            mapSvc = sm.GetService('map')
            numJumps = self.clientPathfinderService.GetJumpCountFromCurrent(fleetAd.solarSystemID)
            fleetAd.numJumps = numJumps
            constellationID = mapSvc.GetParent(fleetAd.solarSystemID)
            fleetAd.regionID = mapSvc.GetParent(constellationID)
            fleetAd.standing = sm.GetService('standing').GetStanding(session.charid, fleetAd.leader.charID)
        return fleetAd

    def SetListenBroadcast(self, name, isit):
        if name not in iconsByBroadcastType and name != BROADCAST_SHOW_OWN:
            name = 'Event'
        settings.user.ui.Set(LISTEN_BROADCAST_SETTING % name, isit)
        sm.ScatterEvent('OnFleetBroadcastFilterChange')

    def GetMyShipTypeID(self):
        shipTypeID = None
        if session.shipid and session.solarsystemid:
            shipTypeID = sm.GetService('godma').GetItem(session.shipid).typeID
        elif GetActiveShip():
            activeShipID = GetActiveShip()
            dl = sm.GetService('clientDogmaIM').GetDogmaLocation()
            shipItem = dl.GetItem(activeShipID)
            shipTypeID = shipItem.typeID
        return shipTypeID

    def SetRemoteMotd(self, motd):
        self.CheckIsInFleet()
        self.fleet.SetMotdEx(motd)

    def GetMotd(self):
        self.CheckIsInFleet()
        if self.motd is None:
            self.motd = self.fleet.GetMotd()
        return self.motd

    def OnFleetMotdChanged(self, motd, reloadMotd):
        self.LogInfo('OnFleetMotdChanged', motd, session.fleetid)
        self.CheckIsInFleet()
        self.motd = motd
        channelWindow = sm.GetService('XmppChat').GetGroupChatWindow('fleet_' + str(session.fleetid))
        if channelWindow is not None and reloadMotd:
            channelWindow.SetMotd(sender=None, text=motd)
        else:
            self.LogError('OnFleetMotdChanged could not find fleet chat window', session.fleetid)

    def OnDropCommanderDropData(self, dragObject, draggedGuys, receivingNode, *args):
        groupType = receivingNode.groupType
        groupID = getattr(receivingNode, 'groupID', None)
        canMove = self.CanMoveAtLeastOneToThisEntry(draggedGuys, receivingNode, groupType, groupID)
        if canMove in (CANNOT_BE_MOVED, CONNOT_BE_MOVED_INCOMPATIBLE):
            return
        if groupType == 'squad':
            return self.DropOnSquadCommander(draggedGuys, groupID, canMove)
        if groupType == 'wing':
            return self.DropOnWingcommander(draggedGuys, groupID, canMove)
        if groupType == 'fleet':
            return self.DropOnFleetCommander(draggedGuys, canMove)
        if groupType == 'fleetMember':
            return self.DropOnFleetMember(draggedGuys, receivingNode)

    def DropOnSquadCommander(self, draggedGuys, newSquadID, canMove, *args):
        newWingID = self.FindWingID(newSquadID)
        if newWingID is None:
            return
        if canMove == CAN_BE_COMMANDER and len(draggedGuys) == 1:
            role = evefleet.fleetRoleSquadCmdr
        else:
            role = evefleet.fleetRoleMember
        self.HandleDroppingInGroup(draggedGuys, newWingID, newSquadID, role=role)

    def DropOnWingcommander(self, draggedGuys, newWingID, canMove):
        if canMove == CAN_BE_COMMANDER and len(draggedGuys) == 1:
            role = evefleet.fleetRoleWingCmdr
        else:
            role = evefleet.fleetRoleMember
        self.HandleDroppingInGroup(draggedGuys, newWingID, None, role=role)

    def DropOnFleetCommander(self, draggedGuys, canMove):
        members = self.GetMembers()
        if canMove == CAN_BE_COMMANDER and len(draggedGuys) == 1:
            role = evefleet.fleetRoleLeader
        else:
            role = evefleet.fleetRoleMember
        self.HandleDroppingInGroup(draggedGuys, None, None, role=role)

    def DropOnFleetMember(self, draggedGuys, receivingNode):
        droppedOnMember = receivingNode.member
        newWingID = droppedOnMember.get('wingID', None)
        newSquadID = droppedOnMember.get('squadID', None)
        self.HandleDroppingInGroup(draggedGuys, newWingID, newSquadID)

    def HandleDroppingInGroup(self, draggedGuys, newWingID, newSquadID, role = evefleet.fleetRoleMember):
        self.CheckIsInFleet()
        members = self.GetMembers()
        tryMove = []
        tryInvite = []

        def SkipBecauseAlreadyInWing(eachCharID):
            if role != evefleet.fleetRoleMember:
                return False
            member = members[eachCharID]
            if newWingID and newSquadID is None and newWingID == member.get('wingID', None):
                return True
            return False

        for eachDraggedGuy in draggedGuys:
            charID = eachDraggedGuy.charID
            if charID in members:
                if newWingID is None and newSquadID is None and role != evefleet.fleetRoleLeader:
                    continue
                if not SkipBecauseAlreadyInWing(charID):
                    tryMove.append(charID)
            else:
                tryInvite.append(charID)

        self.MassMove(tryMove, newWingID, newSquadID, role=role)
        self.MassInvite(tryInvite, newWingID, newSquadID, role=role)

    def FindWingID(self, squadID):
        for wingID, wingInfo in self.wings.iteritems():
            if getattr(wingInfo, 'squads', {}):
                if squadID in wingInfo['squads']:
                    return wingID

    def CanMoveToSquad(self, canMoveAll, draggedGuy, groupType, isFreeMove, myMemberInfo, receivingNode, isMultiMove):
        members = self.GetMembers()
        if groupType == 'fleetMember':
            droppedOnMember = receivingNode.member
            newWingID = droppedOnMember.get('wingID', None)
            newSquadID = droppedOnMember.get('squadID', None)
            allowedMove = CAN_ONLY_BE_MEMBER
        else:
            shiftDown = uicore.uilib.Key(uiconst.VK_SHIFT)
            newSquadID = receivingNode.groupID
            squadCommander = self.GetSquadCommander(newSquadID)
            newWingID = None
            if squadCommander:
                allowedMove = CAN_ONLY_BE_MEMBER
                newWingID = squadCommander.get('wingID', None)
            elif isMultiMove or shiftDown:
                allowedMove = CAN_ONLY_BE_MEMBER
            else:
                allowedMove = CAN_BE_COMMANDER
            if newWingID is None:
                newWingID = self.FindWingID(newSquadID)
                if newWingID is None:
                    return CANNOT_BE_MOVED
        memberCount = len([ guy for guy in members.itervalues() if guy.squadID == newSquadID and guy.charID != draggedGuy.charID ])
        if memberCount >= evefleet.MAX_MEMBERS_IN_SQUAD:
            return CANNOT_BE_MOVED
        elif canMoveAll or isFreeMove:
            return allowedMove
        draggedGuysMemberInfo = self.GetDraggedGuysMemberInfo(draggedGuy)
        if newWingID != session.wingid or draggedGuysMemberInfo and draggedGuysMemberInfo.wingID != session.wingid:
            return CANNOT_BE_MOVED
        elif myMemberInfo.role == evefleet.fleetRoleWingCmdr:
            return allowedMove
        elif not draggedGuysMemberInfo and myMemberInfo.role == evefleet.fleetRoleSquadCmdr and session.squadid == newSquadID:
            return allowedMove
        else:
            return CANNOT_BE_MOVED

    def CanMoveAtLeastOneToThisEntry(self, draggedGuys, receivingNode, groupType, groupID):
        isMultiMove = len(draggedGuys) > 1
        moveSet = {self.CanMoveToThisEntry(eachGuy, receivingNode, groupType, groupID, isMultiMove) for eachGuy in draggedGuys}
        if len(draggedGuys) == 1 and CAN_BE_COMMANDER in moveSet:
            return CAN_BE_COMMANDER
        if CAN_ONLY_BE_MEMBER in moveSet or CAN_BE_COMMANDER in moveSet:
            return CAN_ONLY_BE_MEMBER
        return CANNOT_BE_MOVED

    def CanMoveToThisEntry(self, draggedGuy, receivingNode, groupType, groupID, isMultiMove = False):
        guid = getattr(draggedGuy, '__guid__', None)
        if guid not in AllUserEntries() + ['TextLink']:
            return CONNOT_BE_MOVED_INCOMPATIBLE
        if guid == 'TextLink':
            charID = GetCharIDFromTextLink(draggedGuy)
            if not charID:
                return CONNOT_BE_MOVED_INCOMPATIBLE
            draggedGuy.charID = charID
        if not IsEvePlayerCharacter(draggedGuy.charID):
            return CONNOT_BE_MOVED_INCOMPATIBLE
        members = self.GetMembers()
        myMemberInfo = members[session.charid]
        canMoveAll = myMemberInfo.role == evefleet.fleetRoleLeader or myMemberInfo.job & evefleet.fleetJobCreator
        shiftDown = uicore.uilib.Key(uiconst.VK_SHIFT)
        isFreeMove = False
        if self.GetOptions().isFreeMove and draggedGuy.charID == session.charid:
            isFreeMove = True
        if groupType == 'fleet':
            if not canMoveAll:
                return CANNOT_BE_MOVED
            fleetCommander = self.GetFleetCommander()
            if fleetCommander or isMultiMove or shiftDown:
                return CAN_ONLY_BE_MEMBER
            return CAN_BE_COMMANDER
        if groupType == 'wing':
            newWingID = groupID
            wingCommander = self.GetWingCommander(newWingID)
            if wingCommander or isMultiMove or shiftDown:
                return CAN_ONLY_BE_MEMBER
            if canMoveAll:
                return CAN_BE_COMMANDER
        elif groupType in ('squad', 'fleetMember'):
            return self.CanMoveToSquad(canMoveAll, draggedGuy, groupType, isFreeMove, myMemberInfo, receivingNode, isMultiMove)
        return CANNOT_BE_MOVED

    def GetFleetCommander(self):
        members = self.GetMembers()
        for eachMember in members.itervalues():
            if eachMember.role == evefleet.fleetRoleLeader:
                return eachMember

    def GetWingCommander(self, wingID):
        members = self.GetMembers()
        for eachGuy in members.itervalues():
            if eachGuy.wingID == wingID and eachGuy.role == evefleet.fleetRoleWingCmdr:
                return eachGuy

    def GetSquadCommander(self, squadID):
        members = self.GetMembers()
        for eachGuy in members.itervalues():
            if eachGuy.squadID == squadID and eachGuy.role == evefleet.fleetRoleSquadCmdr:
                return eachGuy

    def GetDraggedGuysMemberInfo(self, draggedGuy):
        members = self.GetMembers()
        if draggedGuy.charID in members:
            return members[draggedGuy.charID]

    def ValidateWingsHaveValidNames(self):
        wingNames = set()
        for wing in self.GetWings().itervalues():
            wingName = wing.name.lower().strip()
            if not wingName or wingName in wingNames:
                raise UserError('GiveWingsUniqueNames')
            wingNames.add(wingName)

    def StoreSetup(self):
        if self.fleet is None:
            return
        self.ValidateWingsHaveValidNames()
        name = self.lastLoadedSetup or ''
        currentMotd = self.GetMotd()
        currentMaxSize = self.fleet.GetFleetMaxSize()
        defaultSquadID = self.GetAutoJoinSquadID()
        defaultSquadName = None
        if defaultSquadID:
            fleet = self.GetFleetHierarchy()
            sq = fleet['squads'].get(defaultSquadID, None)
            if sq:
                defaultSquadName = sq['name'] or localization.GetByLabel('UI/Fleet/FleetWindow/UnnamedSquad')
        currentFleetInfo = KeyVal(oldSetupName=self.lastLoadedSetup, currentMotd=currentMotd, currentOptions=self.options, currentMaxSize=currentMaxSize, currentDefaultSquadName=defaultSquadName)
        wnd = StoreFleetSetupWnd(currentFleetInfo=currentFleetInfo)
        if wnd.ShowModal() != 1:
            return
        if wnd.result is not None:
            self.StoreFleetSetup(wnd.result)

    def GetSetups(self):
        m = MenuData()
        fleetSetupsByName = self.GetFleetSetups()
        listOfSetups = sorted(fleetSetupsByName.values(), key=lambda x: x[fsConst.FS_NAME].lower())
        for eachSetup in listOfSetups:
            setupName = eachSetup[fsConst.FS_NAME]
            hint = GetFleetSetupOptionHint(eachSetup)
            m.AddEntry(setupName, func=lambda sn = setupName: self.LoadSetup(sn), hint=hint)

        return m

    def StoreFleetSetup(self, storeOptions):
        wingsInfo = {}
        wings = self.GetWings().values()
        defaultSquadID = self.GetAutoJoinSquadID()
        wings = sorted(wings, key=lambda x: x.get('wingID', None))
        defaultSquadSetting = None
        for wingIdx, wing in enumerate(wings):
            wingSquads = []
            for squad in wing.squads.itervalues():
                wingSquads.append((squad.squadID, squad.name))

            orderedWingSquads = sorted(wingSquads)
            orderedWingSquadIDs = [ x[0] for x in orderedWingSquads ]
            if defaultSquadID in orderedWingSquadIDs:
                sqIDx = orderedWingSquadIDs.index(defaultSquadID)
                _, sqdName = orderedWingSquads[sqIDx]
                defaultSquadSetting = (wing.name, sqIDx, sqdName)
            wingSquads = SortListOfTuples(orderedWingSquads)
            wingsInfo[wing.name.lower()] = {fsConst.FS_WING_NAME: wing.name,
             fsConst.FS_SQUAD_NAMES: wingSquads,
             fsConst.FS_WING_IDX: wingIdx}

        setupName = storeOptions.setupName
        fleetSetupsByName = self.GetFleetSetups()
        fleetInfo = fleetSetupsByName.get(setupName, {})
        fleetInfo[fsConst.FS_NAME] = setupName
        fleetInfo[fsConst.FS_WINGS_INFO] = wingsInfo
        if storeOptions.storeMotd:
            fleetInfo[fsConst.FS_MOTD] = self.GetMotd()
        else:
            fleetInfo.pop(fsConst.FS_MOTD, None)
        if storeOptions.storeFreeMove:
            fleetInfo[fsConst.FS_IS_FREE_MOVE] = self.options.isFreeMove
        else:
            fleetInfo.pop(fsConst.FS_IS_FREE_MOVE, None)
        if storeOptions.storeDefaultSquad and defaultSquadSetting:
            fleetInfo[fsConst.FS_DEFAULT_SQUAD] = defaultSquadSetting
        else:
            fleetInfo.pop(fsConst.FS_DEFAULT_SQUAD, None)
        if storeOptions.storeMaxSize:
            fleetInfo[fsConst.FS_MAX_SIZE] = self.fleet.GetFleetMaxSize()
        else:
            fleetInfo.pop(fsConst.FS_MAX_SIZE, None)
        fleetSetupsByName[setupName] = fleetInfo
        self.SaveSetupOnServer()

    def SaveSetupOnServer(self):
        fleetSetupsByName = self.GetFleetSetups()
        yamlFilters = yaml.safe_dump(fleetSetupsByName.values())
        self.characterSettings.Save('fleetSetups', yamlFilters)
        sm.ScatterEvent('OnFleetSetupChanged')

    def DeleteFleetSetup(self, setupName):
        fleetSetupsByName = self.GetFleetSetups()
        setupRemoved = fleetSetupsByName.pop(setupName, None)
        if setupRemoved:
            self.SaveSetupOnServer()

    def LoadSetup(self, setupName):
        eve.Message('AttemptingToLoadFleet')
        self.lastLoadedSetup = setupName
        self.fleet.LoadFleetSetup(setupName)

    def SetFleetMaxSize(self):
        currentMaxSize = self.fleet.GetFleetMaxSize()
        caption = localization.GetByLabel('UI/Fleet/FleetWindow/SetFleetMaxSize')
        minValue = 1
        maxValue = evefleet.MAX_MEMBERS_IN_FLEET
        hint = localization.GetByLabel('UI/Fleet/FleetWindow/SetFleetNumberBetween', max=FmtAmt(maxValue))
        ret = uix.QtyPopup(maxValue, minValue, currentMaxSize, caption=caption, hint=hint)
        if ret and 'qty' in ret:
            qty = ret['qty']
            self.fleet.SetFleetMaxSize(qty)

    def LoadSharedBroadcastSettings(self, settingKey, settingName):
        if eve.Message('ConfirmLoadBroadcastSettings', {}, uiconst.YESNO, default=uiconst.ID_NO) != uiconst.ID_YES:
            return
        data = sharedSettings.GetDataFromSettingKey(settingKey, None, 'ItemFilterLoadingError')
        broadcastSettings = data['broadcastSettings']
        broadcastSettingsDict = {flagToName.get(x[0]):(x[1], x[2]) for x in broadcastSettings}
        broadcastSettingsDict.update({x[0]:(x[1], x[2]) for x in broadcastSettings if x[0] == BROADCAST_SHOW_OWN})
        for name, labelName in broadcastNames.iteritems():
            settingsForName = broadcastSettingsDict.get(name)
            if settingsForName:
                checked, color = settingsForName
            else:
                checked, color = True, None
            if color:
                color = tuple(color)
            settings.user.ui.Set(LISTEN_BROADCAST_SETTING % name, checked)
            settings.user.ui.Set(BROADCAST_COLOR_SETTING % name, color)

        settings.char.ui.Set('sharedBroadcastDragCont_name', settingName)
        sm.ScatterEvent('OnFleetBroadcastFilterChange')
        BroadcastSettings.CloseIfOpen()
        BroadcastSettings.Open()

    def GetCynoTypeText(self, cynoTypeID):
        path = cynoTypeNames.get(cynoTypeID, None)
        if not path:
            return ''
        return localization.GetByLabel(path)

    def GetAllowedGroupIDs(self, advertInfo):
        allowedGroups = set()
        if evefleet.IsOpenToCorp(advertInfo):
            allowedGroups.add(session.corpid)
        if session.allianceid is not None and evefleet.IsOpenToAlliance(advertInfo):
            allowedGroups.add(session.allianceid)
        if session.warfactionid is not None and evefleet.IsOpenToMilitia(advertInfo):
            allowedGroups.add(session.warfactionid)
        return allowedGroups

    def OnFleetRespawnPointsUpdate(self, respawnPoints):
        self.respawnPoints = respawnPoints
        sm.ScatterEvent('OnFleetRespawnPointsUpdate_Local')

    def GetRespawnPoints(self):
        return self.respawnPoints

    @eveexceptions.EatsExceptions('protoClientLogs')
    def LogFleetCreation(self, fleetID, uiSource):
        self.message_bus.fleet_created(fleet_id=fleetID, ui_source=uiSource)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def LogFleetJoinAttempts(self, fleetID, uiSource):
        self.message_bus.applied_to_join(fleet_id=fleetID, ui_source=uiSource)

    def AddFleetFinderAdvert(self, adInfoObject):
        adInfoData = adInfoObject.GetData()
        fleetAdvertDict = sm.ProxySvc('fleetProxy').AddFleetFinderAdvert(adInfoData)
        self.GetFleetAdsForChar_Memoized.clear_memoized()
        if fleetAdvertDict:
            return FleetAdvertObject(**fleetAdvertDict)

    def UpdateFleetAdvertWithNewLeader(self, allowedEntitiesInfo):
        fleetAdvertDict = sm.ProxySvc('fleetProxy').UpdateFleetAdvertWithNewLeader(allowedEntitiesInfo)
        if fleetAdvertDict:
            return FleetAdvertObject(**fleetAdvertDict)

    def RemoveFleetFinderAdvert(self):
        fleetAdvertDict = sm.ProxySvc('fleetProxy').RemoveFleetFinderAdvert()
        self.GetFleetAdsForChar_Memoized.clear_memoized()
        if fleetAdvertDict:
            return FleetAdvertObject(**fleetAdvertDict)

    def GetMyFleetFinderAdvert(self):
        fleetAdvertDict = sm.ProxySvc('fleetProxy').GetMyFleetFinderAdvert()
        if fleetAdvertDict:
            return FleetAdvertObject(**fleetAdvertDict)

    def UpdateAdvertInfo(self, numMembers, allowedDiffKeyVal):
        fleetAdvertDict = sm.ProxySvc('fleetProxy').UpdateAdvertInfo(numMembers, allowedDiffKeyVal)
        if fleetAdvertDict:
            return FleetAdvertObject(**fleetAdvertDict)

    def UpdateAdvertAllowedEntities(self, allowedInfoFromStandings):
        fleetAdvertDict = sm.ProxySvc('fleetProxy').UpdateAdvertAllowedEntities(allowedInfoFromStandings)
        if fleetAdvertDict:
            return FleetAdvertObject(**fleetAdvertDict)
