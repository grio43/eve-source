#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleet.py
import eveicon
from carbon.common.script.util.commonutils import GetAttrs
from carbonui.control.animatedsprite import AnimSprite
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import ParanoidDecoMethod, SortListOfTuples
from eve.client.script.parklife import states as state
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.listgroup import ListGroup as Group
from eve.client.script.ui.inflight.baseTacticalEntry import BaseTacticalEntry
from eve.client.script.ui.inflight.actions import ActionPanel
from eve.client.script.ui.inflight.bracketsAndTargets.targetIconCont import TargetIconCont
from eve.client.script.ui.services.menuAction import Action
from eve.client.script.ui.shared.fleet.fleetConst import FLEET_VIEW_FLAT_LIST_SETTING
from eve.client.script.ui.shared.radialMenu.radialMenu import RadialMenuSpaceCharacter
import weakref
from eve.client.script.ui.util.linkUtil import GetCharIDFromTextLink
from eve.client.script.ui.util import uix
from eve.client.script.util.bubble import SlimItemFromCharID, InBubble
from eve.common.script.sys.idCheckers import IsCharacter
import uthread
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
import destiny
import blue
from eve.client.script.ui.shared.fleet import fleetbroadcastexports, fleetBroadcastConst
import carbonui.const as uiconst
import log
import telemetry
import localization
from collections import defaultdict
import evefleet.client
from evefleet import fleetActivityNames, ACTIVITY_MISC
from menucheckers import CelestialChecker, SessionChecker
from utillib import KeyVal
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from menu import MenuLabel, MenuList
from carbonui.uianimations import animations
CONNOT_BE_MOVED_INCOMPATIBLE = -1
CANNOT_BE_MOVED = 0
CAN_BE_COMMANDER = 1
CAN_ONLY_BE_MEMBER = 2
COLOR_CANNOT_BE_MOVED = (1,
 0,
 0,
 0.15)
COLOR_CAN_BE_COMMANDER = (1,
 1,
 1,
 0.2)
COLOR_CAN_ONLY_BE_MEMBER = (1,
 1,
 1,
 0.07)
EDIT_MODE_CONFIG = 'fleet_watchlistcolor_editMode'
WATCHLIST_COLORS_CONFIG = 'fleet_watchlistcolors'

def CommanderName(group):
    cmdr = group['commander']
    if cmdr:
        return cfg.eveowners.Get(cmdr).name
    else:
        return '<color=0x%%(alpha)xffffff>%s</color>' % localization.GetByLabel('UI/Fleet/FleetWindow/NoCommander')


def SquadronName(fleet, squadID):
    squadron = fleet['squads'][squadID]
    squadronName = squadron['name']
    if squadronName == '':
        squadno = GroupNumber(fleet, 'squad', squadID)
        squadronName = localization.GetByLabel('UI/Fleet/DefaultSquadName', squadNumber=squadno)
    return squadronName


def WingName(fleet, wingID):
    wing = fleet['wings'][wingID]
    wingName = wing['name']
    if wingName == '':
        wingno = GroupNumber(fleet, 'wing', wingID)
        wingName = localization.GetByLabel('UI/Fleet/DefaultWingName', wingNumber=wingno)
    return wingName


def GroupNumber(fleet, groupType, groupID):
    ids = fleet['%ss' % groupType].keys()
    ids.sort()
    return ids.index(groupID) + 1


def GetSquadMenu(squadID):
    m = MenuList()
    fleetSvc = sm.GetService('fleet')
    if fleetSvc.IsCommanderOrBoss():
        m = MenuList([(MenuLabel('UI/Fleet/FleetWindow/ChangeName'), lambda : fleetSvc.ChangeSquadName(squadID)), (MenuLabel('UI/Fleet/FleetWindow/DeleteSquad'), lambda : fleetSvc.DeleteSquad(squadID))])
        if squadID == fleetSvc.GetAutoJoinSquadID():
            m.append((MenuLabel('UI/Fleet/FleetWindow/RemoveSquadAsAutoJoin'), lambda : fleetSvc.SetAutoJoinSquadID(None)))
        else:
            m.append((MenuLabel('UI/Fleet/FleetWindow/SetSquadAsAutoJoin'), lambda : fleetSvc.SetAutoJoinSquadID(squadID)))
    m.append((MenuLabel('UI/Fleet/FleetWindow/AddSquadMembersToWatchlist'), lambda : fleetSvc.AddFavoriteSquad(squadID)))
    return m


class MyFleetPanel(Container):
    __guid__ = 'form.FleetView'
    __notifyevents__ = ['OnFleetMemberChanging',
     'OnManyFleetMembersChanging',
     'OnCollapsed',
     'OnExpanded',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnFleetWingAdded_Local',
     'OnFleetWingDeleted_Local',
     'OnFleetSquadAdded_Local',
     'OnFleetSquadDeleted_Local',
     'OnFleetMemberChanged_Local',
     'OnFleetWingNameChanged_Local',
     'OnFleetSquadNameChanged_Local',
     'OnFleetOptionsChanged_Local']

    def PostStartup(self):
        sm.RegisterNotify(self)
        header = self
        header.baseHeight = 30
        self.sr.topEntry = FleetRoleCont(parent=header, align=uiconst.TOTOP, height=16, padBottom=8)
        self.sr.scroll = eveScroll.Scroll(parent=self)
        self.sr.scroll.sr.content.OnDropData = self.OnDropData
        self.members = {}
        self.myGroups = {}
        self.pending_RefreshFromRec = []
        self.scrollToProportion = 0
        self.fleet = None
        self.HandleFleetChanged()
        FLEET_VIEW_FLAT_LIST_SETTING.on_change.connect(self.HandleFleetChanged)

    def LoadPanel(self):
        if not self.sr.Get('inited', 0):
            setattr(self.sr, 'inited', 1)
            self.PostStartup()
        if session.fleetid is not None:
            if getattr(self.sr, 'scroll', None):
                self.sr.scroll._OnResize()

    def OnFleetMemberChanging(self, charID):
        rec = self.members.get(charID)
        if rec is not None:
            rec.changing = True
            self.RefreshFromRec(rec)

    def OnManyFleetMembersChanging(self, charIDs):
        squadMembersByWingID = defaultdict(list)
        otherMembers = []
        for eachCharID in charIDs:
            rec = self.members.get(eachCharID)
            if rec is None:
                continue
            if not FLEET_VIEW_FLAT_LIST_SETTING.is_enabled() and rec.squadID not in (None, -1) and rec.wingID not in (None, -1):
                rec.changing = True
                squadMembersByWingID[rec.wingID].append(rec)
            else:
                otherMembers.append(eachCharID)

        for charsInWing in squadMembersByWingID.itervalues():
            recForFirstChar = charsInWing[0]
            if recForFirstChar:
                self.RefreshFromRec(recForFirstChar)

        for charID in otherMembers:
            self.OnFleetMemberChanging(charID)

    def UpdateHeader(self):
        from eve.client.script.ui.shared.fleet.fleetwindow import FleetWindow
        wnd = FleetWindow.GetIfOpen()
        if wnd:
            wnd.UpdateHeader()

    def CheckHint(self):
        if not self.sr.scroll.GetNodes():
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Fleet/NoFleet'))
        else:
            self.sr.scroll.ShowHint()
        self.UpdateHeader()

    def OnFleetWingAdded_Local(self, *args):
        self.HandleFleetChanged()

    def OnFleetWingDeleted_Local(self, *args):
        self.HandleFleetChanged()

    def OnFleetSquadAdded_Local(self, *args):
        self.HandleFleetChanged()

    def OnFleetSquadDeleted_Local(self, *args):
        self.HandleFleetChanged()

    def OnFleetSquadNameChanged_Local(self, squadID, name):
        self.fleet['squads'][squadID]['name'] = name
        headerNode = self.HeaderNodeFromGroupTypeAndID('squad', squadID)
        if headerNode:
            numMembers = len(sm.GetService('fleet').GetMembersInSquad(squadID))
            if numMembers == 0:
                headerNode.label = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderEmpty', unitName=name)
            else:
                headerNode.groupInfo = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderWithCount', unitName=name, memberCount=numMembers)
            if headerNode.panel:
                headerNode.panel.Load(headerNode)

    def OnFleetOptionsChanged_Local(self, oldOptions, newOptions):
        oldSquadID = oldOptions.autoJoinSquadID
        newSquadID = newOptions.autoJoinSquadID
        if oldSquadID == newSquadID:
            return
        if not FleetSvc().IsCommanderOrBoss():
            return
        oldHeaderNode = self.HeaderNodeFromGroupTypeAndID('squad', oldSquadID)
        newHeaderNode = self.HeaderNodeFromGroupTypeAndID('squad', newSquadID)
        for eachHeaderNode in (oldHeaderNode, newHeaderNode):
            if eachHeaderNode and eachHeaderNode.panel:
                eachHeaderNode.showAsAutoJoinSquad = eachHeaderNode.groupID == newSquadID
                eachHeaderNode.panel.Load(eachHeaderNode)

    def OnFleetWingNameChanged_Local(self, wingID, name):
        self.fleet['wings'][wingID]['name'] = name
        headerNode = self.HeaderNodeFromGroupTypeAndID('wing', wingID)
        if headerNode:
            numMembers = len(sm.GetService('fleet').GetMembersInWing(wingID))
            if numMembers == 0:
                headerNode.groupInfo = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderEmpty', unitName=name)
            else:
                headerNode.groupInfo = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderWithCount', unitName=name, memberCount=numMembers)
            if headerNode.panel:
                headerNode.panel.Load(headerNode)

    def OnFleetJoin_Local(self, rec):
        if not self or self.destroyed:
            return
        if rec.charID == session.charid:
            self.HandleFleetChanged()
        else:
            self.AddChar(rec)

    def AddChar(self, rec):
        if self.fleet is None:
            return
        self.members[rec.charID] = rec
        FleetSvc().AddToFleet(self.fleet, rec)
        if not FLEET_VIEW_FLAT_LIST_SETTING.is_enabled():
            self.HandleFleetChanged()
        self.RefreshFromRec(rec)

    def OnFleetLeave_Local(self, rec):
        if rec.charID == session.charid:
            return
        self.RemoveChar(rec.charID)
        if rec.role == evefleet.fleetRoleSquadCmdr:
            self.FlashHeader('squad', rec.squadID)
        elif rec.role == evefleet.fleetRoleWingCmdr:
            self.FlashHeader('wing', rec.wingID)
        elif rec.role == evefleet.fleetRoleLeader:
            self.FlashHeader('fleet', session.fleetid)

    def RemoveChar(self, charID):
        rec = self.members.pop(charID, None)
        if rec is None or self.fleet is None:
            return
        if None not in (rec.squadID, rec.wingID):
            self.RemoveFromFleet(self.fleet, rec)
            if FLEET_VIEW_FLAT_LIST_SETTING.is_enabled():
                self.RemoveCharFromScroll(charID)
            else:
                self.HandleFleetChanged()
            self.RefreshFromRec(rec, removing=1)

    def OnFleetMemberChanged_Local(self, charID, fleetID, oldWingID, oldSquadID, oldRole, oldJob, oldMemberOptOuts, newWingID, newSquadID, newRole, newJob, newMemberOptOuts):
        rec = self.members[charID]

        def UpdateRec():
            rec.changing = False
            rec.role, rec.job = newRole, newJob
            rec.wingID, rec.squadID = newWingID, newSquadID
            rec.memberOptOuts = newMemberOptOuts

        if (oldWingID, oldSquadID) != (newWingID, newSquadID):
            if FLEET_VIEW_FLAT_LIST_SETTING.is_enabled():
                UpdateRec()
                self.RefreshFromRec(rec)
            else:
                if evefleet.fleetRoleLeader in (oldRole, newRole):
                    self.HandleFleetChanged()
                else:
                    self.RemoveChar(charID)
                    UpdateRec()
                    self.AddChar(rec)
                self.UpdateHeader()
        else:
            UpdateRec()
            if oldRole == evefleet.fleetRoleSquadCmdr != newRole:
                self.fleet['squads'][rec.squadID]['commander'] = None
            elif oldRole == evefleet.fleetRoleMember != newRole:
                self.fleet['squads'][rec.squadID]['commander'] = rec.charID
            self.RefreshFromRec(rec)
        if oldRole == evefleet.fleetRoleSquadCmdr and (newRole != evefleet.fleetRoleSquadCmdr or newSquadID != oldSquadID):
            self.FlashHeader('squad', oldSquadID)
        elif oldRole == evefleet.fleetRoleWingCmdr and (newRole != evefleet.fleetRoleWingCmdr or newWingID != oldWingID):
            self.FlashHeader('wing', oldWingID)
        elif oldRole == evefleet.fleetRoleLeader != newRole:
            self.FlashHeader('fleet', session.fleetid)

    def FlashHeader(self, groupType, groupID):
        uthread.new(self.FlashHeader_thread, groupType, groupID)

    def FlashHeader_thread(self, groupType, groupID):
        headerNode = self.HeaderNodeFromGroupTypeAndID(groupType, groupID)
        if headerNode and headerNode.panel:
            if hasattr(headerNode.panel, 'Flash'):
                headerNode.panel.Flash()

    def RemoveFromFleet(self, fleet, rec):

        def Name(charID):
            return charID and cfg.eveowners.Get(charID).name

        def RemoveCommander(group, charID):
            if group['commander'] == charID:
                group['commander'] = None
            else:
                log.LogError('Commander is', Name(group['commander']), 'not', Name(charID))

        if rec.squadID != -1:
            squad = fleet['squads'][rec.squadID]
            if rec.role == evefleet.fleetRoleSquadCmdr:
                RemoveCommander(squad, rec.charID)
            try:
                squad['members'].remove(rec.charID)
            except ValueError:
                log.LogError(Name(rec.charID), 'not in squad.')

        elif rec.wingID != -1:
            RemoveCommander(fleet['wings'][rec.wingID], rec.charID)
        else:
            RemoveCommander(fleet, rec.charID)

    def RefreshFromRec(self, rec, removing = 0):
        self.scrollToProportion = self.sr.scroll.GetScrollProportion()
        if getattr(self, 'loading_RefreshFromRec', 0):
            self.pending_RefreshFromRec.append(rec)
            return
        setattr(self, 'loading_RefreshFromRec', 1)
        try:
            if FLEET_VIEW_FLAT_LIST_SETTING.is_enabled():
                if not removing:
                    self.AddOrUpdateScrollEntry(rec.charID)
            elif rec.wingID not in (None, -1):
                self.RefreshRecMemberInWing(rec.wingID, rec.squadID)
            else:
                self.HandleFleetChanged()
            self.UpdateHeader()
            self.loading_RefreshFromRec = 0
            if self.pending_RefreshFromRec:
                recToRefresh = self.pending_RefreshFromRec.pop(0)
                self.RefreshFromRec(recToRefresh)
        finally:
            self.sr.scroll.ScrollToProportion(self.scrollToProportion)
            setattr(self, 'loading_RefreshFromRec', 0)

    def RefreshRecMemberInWing(self, wingID, squadID):
        inSquad = squadID not in (None, -1)
        if inSquad:
            loadingVariable = 'refreshing_squadMembers_wingID_%s' % wingID
            pendingVariable = 'pendingRefresing_squadMembers_wingID_%s' % wingID
        else:
            loadingVariable = 'refreshing_non_squadMembers_wingID_%s' % wingID
            pendingVariable = 'pending_non_refreshingWingID_%s' % wingID
        if getattr(self, loadingVariable, False):
            setattr(self, pendingVariable, True)
            return
        setattr(self, loadingVariable, True)
        wingHeaderNode = self.HeaderNodeFromGroupTypeAndID('wing', wingID)
        try:
            if inSquad:
                if wingHeaderNode:
                    self.ReloadScrollEntry(wingHeaderNode)
            else:
                fleetHeaderNode = self.HeaderNodeFromGroupTypeAndID('fleet', session.fleetid)
                if fleetHeaderNode:
                    self.ReloadScrollEntry(fleetHeaderNode)
        finally:
            setattr(self, loadingVariable, False)
            if getattr(self, pendingVariable, False):
                setattr(self, pendingVariable, False)
                self.RefreshRecMemberInWingCaller_thread(wingID, squadID)

    def RefreshRecMemberInWingCaller_thread(self, wingID, squadID):
        blue.pyos.synchro.SleepWallclock(0)
        self.RefreshRecMemberInWing(wingID, squadID)

    def ReloadScrollEntry(self, headerNode):
        if headerNode:
            scroll = getattr(headerNode, 'scroll', None)
            if scroll:
                scroll.PrepareSubContent(headerNode)

    def HeaderNodeFromGroupTypeAndID(self, groupType, groupID):
        for entry in self.sr.scroll.GetNodes():
            if entry.groupType == groupType and entry.groupID == groupID:
                return entry

    def HandleFleetChanged(self, *args):
        uthread.pool('FleetView::HandleFleetChanged', self.DoHandleFleetChanged)

    def DoHandleFleetChanged(self):
        if not self or self.destroyed:
            return
        if getattr(self, 'loading_HandleFleetChanged', 0):
            setattr(self, 'pending_HandleFleetChanged', 1)
            return
        setattr(self, 'loading_HandleFleetChanged', 1)
        blue.pyos.synchro.SleepWallclock(1000)
        setattr(self, 'pending_HandleFleetChanged', 0)
        try:
            try:
                self.members = FleetSvc().GetMembers().copy()
                if session.charid in self.members:
                    self.sr.scroll.Load(contentList=[])
                    self.LoadFleet()
                    self.CheckHint()
                setattr(self, 'loading_HandleFleetChanged', 0)
                if getattr(self, 'pending_HandleFleetChanged', 0):
                    setattr(self, 'pending_HandleFleetChanged', 0)
                    self.HandleFleetChanged()
            finally:
                setattr(self, 'loading_HandleFleetChanged', 0)

        except:
            pass

    def EmptyGroupEntry(self, label, indent, groupType, groupID):
        return GetFromClass(EmptyGroup, {'label': label,
         'indent': indent,
         'groupType': groupType,
         'groupID': groupID})

    def MakeCharEntry(self, charID, sublevel = 0, isLast = False):
        data = self.GetMemberData(charID, sublevel=sublevel)
        data.isLast = isLast
        data.groupType = 'fleetMember'
        return GetFromClass(FleetMember, data)

    def MakeSquadEntry(self, squadID, sublevel = 0):
        headerdata = self.GetHeaderData('squad', squadID, sublevel)
        if headerdata.numMembers == 0:
            return GetFromClass(EmptyGroup, {'squadID': squadID,
             'groupType': 'squad',
             'groupID': squadID,
             'label': localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderEmpty', unitName=SquadronName(self.fleet, squadID)),
             'GetMenu': self.EmptySquadMenu,
             'indent': 2,
             'showAsAutoJoinSquad': headerdata.showAsAutoJoinSquad})
        else:
            return GetFromClass(FleetHeader, headerdata)

    def EmptySquadMenu(self, entry):
        return GetSquadMenu(entry.sr.node.squadID)

    def MakeWingEntry(self, wingID, sublevel = 0):
        headerdata = self.GetHeaderData('wing', wingID, sublevel)
        return GetFromClass(FleetHeader, headerdata)

    def MakeFleetEntry(self):
        headerdata = self.GetHeaderData('fleet', session.fleetid, 0)
        return GetFromClass(FleetHeader, headerdata)

    def AddToScroll(self, *entries):
        self.sr.scroll.AddEntries(-1, entries)

    def RemoveCharFromScroll(self, charID):
        for entry in self.sr.scroll.GetNodes():
            if entry.charID == charID:
                self.sr.scroll.RemoveEntries([entry])
                return

    def LoadFleet(self):
        fleetMembers = {}
        for charID, member in self.members.iteritems():
            if None not in (member.squadID, member.wingID):
                fleetMembers[charID] = member
            if charID == session.charid:
                self.myGroups['squad'] = member.squadID
                self.myGroups['wing'] = member.wingID

        self.fleet = FleetSvc().GetFleetHierarchy(fleetMembers)
        if FLEET_VIEW_FLAT_LIST_SETTING.is_enabled():
            scrollList = []
            for charID in self.members.keys():
                entry = self.MakeCharEntry(charID, sublevel=1, isLast=True)
                scrollList.append((cfg.eveowners.Get(charID).name.lower(), entry))

            scrollList = SortListOfTuples(scrollList)
            self.sr.scroll.Load(contentList=scrollList)
        else:
            self.AddToScroll(self.MakeFleetEntry())
            self.sr.scroll.ScrollToProportion(self.scrollToProportion)

    def GetMemberData(self, charID, slimItem = None, member = None, sublevel = 0):
        if slimItem is None:
            slimItem = SlimItemFromCharID(charID)
        data = KeyVal()
        data.charRec = cfg.eveowners.Get(charID)
        data.itemID = data.id = data.charID = charID
        data.typeID = data.charRec.typeID
        data.squadID = None
        data.wingID = None
        data.displayName = data.charRec.name
        data.roleIcons = []
        member = member or self.members.get(charID)
        if member:
            data.squadID = member.squadID
            data.wingID = member.wingID
            data.role = member.role
            if member.job & evefleet.fleetJobCreator:
                data.roleIcons.append({'id': '73_20',
                 'hint': localization.GetByLabel('UI/Fleet/Ranks/Boss')})
            if member.role == evefleet.fleetRoleLeader:
                data.roleIcons.append({'id': '73_17',
                 'hint': localization.GetByLabel('UI/Fleet/Ranks/FleetCommander')})
            elif member.role == evefleet.fleetRoleWingCmdr:
                data.roleIcons.append({'id': '73_18',
                 'hint': localization.GetByLabel('UI/Fleet/Ranks/WingCommander')})
            elif member.role == evefleet.fleetRoleSquadCmdr:
                data.roleIcons.append({'id': '73_19',
                 'hint': localization.GetByLabel('UI/Fleet/Ranks/SquadCommander')})
            if False in (member.memberOptOuts.acceptsFleetWarp, member.memberOptOuts.acceptsConduitJumps, member.memberOptOuts.acceptsFleetRegroups):
                hintList = []
                if not member.memberOptOuts.acceptsFleetWarp:
                    hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/DoesNotTakeFleetWarp'))
                if not member.memberOptOuts.acceptsConduitJumps:
                    hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/DoesNotAcceptConduitJumps'))
                if not member.memberOptOuts.acceptsFleetRegroups:
                    hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/DoesNotAcceptFleetRegroup'))
                hint = '<br>'.join(hintList)
                data.roleIcons.append({'id': '73_47',
                 'hint': hint})
        data.label = data.displayName
        data.isSub = 0
        data.sort_name = data.displayName
        data.sublevel = sublevel
        data.member = member
        if slimItem:
            data.slimItem = weakref.ref(slimItem)
        else:
            data.slimItem = None
        data.changing = getattr(member, 'changing', False)
        return data

    def GetHeaderData(self, gtype, gid, sublevel):
        data = KeyVal()
        data.id = ('fleet', '%s_%s' % (gtype, gid))
        data.groupType = gtype
        data.groupID = gid
        data.rawText = ''
        data.displayName = data.label = ''
        data.sublevel = sublevel
        data.expanded = True
        data.showicon = 'hide'
        data.hideFill = True
        data.hideTopLine = True
        data.hideExpanderLine = True
        data.showlen = False
        data.BlockOpenWindow = 1
        data.labelstyle = {'uppercase': True,
         'fontsize': 9,
         'letterspacing': 2}
        data.myGroups = self.myGroups
        group = self.GetGroup(gtype, gid)
        data.commanderName = CommanderName(group) % {'alpha': 119}
        data.commanderData = None
        fleetSvc = sm.GetService('fleet')
        if gtype == 'squad':
            data.GetSubContent = self.SquadContentGetter(gid, sublevel)
            num = len(fleetSvc.GetMembersInSquad(gid))
            if num == 0:
                data.groupInfo = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderEmpty', unitName=SquadronName(self.fleet, gid))
            else:
                data.groupInfo = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderWithCount', unitName=SquadronName(self.fleet, gid), memberCount=num)
            if fleetSvc.options.autoJoinSquadID == gid and FleetSvc().IsCommanderOrBoss():
                data.showAsAutoJoinSquad = True
            else:
                data.showAsAutoJoinSquad = False
        elif gtype == 'wing':
            data.GetSubContent = self.WingContentGetter(gid, sublevel)
            num = len(fleetSvc.GetMembersInWing(gid))
            data.groupInfo = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderWithCount', unitName=WingName(self.fleet, gid), memberCount=num)
        elif gtype == 'fleet':
            data.GetSubContent = self.FleetContentGetter(gid, sublevel)
            num = len(self.members)
            data.groupInfo = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeaderWithCount', unitName=localization.GetByLabel('UI/Fleet/Fleet'), memberCount=num)
            data.scroll = self.sr.scroll
        else:
            raise NotImplementedError
        data.numMembers = num
        if group['commander']:
            commanderData = self.GetMemberData(group['commander'])
            data.commanderData = commanderData
        data.openByDefault = data.open = True
        return data

    def AddOrUpdateScrollEntry(self, charID):
        newEntry = self.MakeCharEntry(charID)
        newEntry.sublevel = 1
        newEntry.isLast = 1
        for i, data in enumerate(self.sr.scroll.GetNodes()):
            if data.Get('id', None) == charID:
                newEntry.panel = data.Get('panel', None)
                scroll = data.Get('scroll', None)
                if scroll is not None:
                    newEntry.scroll = scroll
                newEntry.idx = i
                self.sr.scroll.GetNodes()[i] = newEntry
                if newEntry.panel is not None:
                    newEntry.panel.Load(newEntry)
                return

        self.sr.scroll.AddEntries(-1, [newEntry])
        self.sr.scroll.Sort(by='name')

    def SquadContentGetter(self, squadID, sublevel):

        def GetContent(*blah):
            squad = self.fleet['squads'][squadID]
            ret = []
            if squad['members']:
                sortedMembers = SortListOfTuples([ ((charID != squad['commander'], self.members[charID].job != evefleet.fleetJobCreator, cfg.eveowners.Get(charID).name.lower()), charID) for charID in squad['members'] ])
                if squad['commander'] is not None:
                    sortedMembers.remove(squad['commander'])
                for i in range(len(sortedMembers)):
                    charID = sortedMembers[i]
                    ret.append(self.MakeCharEntry(charID, sublevel=sublevel + 1, isLast=i == len(sortedMembers) - 1))

            if not ret:
                emptyGroupEntry = self.EmptyGroupEntry(localization.GetByLabel('UI/Fleet/FleetWindow/SquadEmpty'), sublevel + 1, 'squad', squadID)
                ret = [emptyGroupEntry]
            return ret

        return GetContent

    def WingContentGetter(self, wingID, sublevel):

        def GetContent(*blah):
            wing = self.fleet['wings'][wingID]
            ret = []
            squads = wing['squads'][:]
            squads.sort()
            for squadID in squads:
                ret.append(self.MakeSquadEntry(squadID, sublevel + 1))

            if not ret:
                emptyGroupEntery = self.EmptyGroupEntry(localization.GetByLabel('UI/Fleet/FleetWindow/WingEmpty'), sublevel + 1, 'wing', wingID)
                ret = [emptyGroupEntery]
            return ret

        return GetContent

    def FleetContentGetter(self, fleetID, sublevel):

        def GetContent(*blah):
            ret = []
            wings = self.fleet['wings'].keys()
            wings.sort()
            for wingID in wings:
                ret.append(self.MakeWingEntry(wingID, sublevel + 1))

            return ret

        return GetContent

    def GetGroup(self, groupType, groupID):
        if groupType == 'fleet':
            return self.fleet
        if groupType == 'wing':
            return self.fleet['wings'][groupID]
        if groupType == 'squad':
            return self.fleet['squads'][groupID]
        raise NotImplementedError

    def GetMemberEntry(self, charID):
        for entry in self.sr.scroll.GetNodes():
            if entry.charID == charID:
                return entry

    def OnExpanded(self, wnd, *args):
        pass

    def OnDropData(self, dragObject, droppedGuys, *args):
        if not sm.GetService('fleet').IsCommanderOrBoss():
            return
        sm.GetService('fleet').DropOnFleetCommander(droppedGuys, CAN_ONLY_BE_MEMBER)


class FleetHeader(Group):
    __guid__ = 'listentry.FleetHeader'
    isDragObject = True

    def Startup(self, *args, **kw):
        Group.Startup(self, *args, **kw)
        text_gaugepar = Container(name='text_gaugepar', parent=self, idx=0, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        text_gaugepar.width = 0
        self.sr.text_gaugepar = text_gaugepar
        self.sr.label.parent.width = 0
        self.sr.label.parent.SetParent(text_gaugepar)
        Container(name='toppush', parent=self.sr.label.parent, align=uiconst.TOTOP, height=14)
        roleIconsContainer = Container(name='roleIconsContainer', parent=self.sr.label.parent, width=0, align=uiconst.TORIGHT)
        self.roleIconsContainer = roleIconsContainer
        self.sr.topLabel = eveLabel.EveLabelMedium(text='', parent=self.sr.label.parent, left=0, top=0, state=uiconst.UI_DISABLED, color=None, idx=0)
        self.sr.bottomLabel = eveLabel.EveLabelMedium(text='', parent=self.sr.label.parent, left=0, top=12, state=uiconst.UI_DISABLED, color=None, idx=0)
        changing = AnimSprite(icons=[ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ], align=uiconst.TOPRIGHT, parent=self, pos=(0, 13, 16, 16))
        self.sr.changing = changing
        changing.state = uiconst.UI_NORMAL
        self.sr.myGroupSelection = Fill(name='myGroupSelection', bgParent=self, padding=(0, 1, 0, 1), color=(0.0, 0.5, 0.0, 0.1))
        self.sr.myGroupSelection.display = False
        self.movingHilite = Fill(bgParent=self, name='movingHilite', color=(1, 0, 0, 0.25))
        self.movingHilite.display = False

    def Load(self, node, *args, **kw):
        sublevel = node.Get('sublevel', 0)
        if node.groupType != 'fleet':
            node.hasArrow = True
        Group.Load(self, node, *args, **kw)
        self.sr.label.left += 2
        self.sr.topLabel.left = self.sr.label.left
        self.sr.bottomLabel.left = self.sr.label.left
        if node.commanderData and node.commanderData.itemID == session.charid:
            self.sr.myGroupSelection.display = True
        else:
            isMyGroup = node.myGroups.get(node.groupType, None) == node.groupID or node.groupType == 'fleet'
            if isMyGroup:
                self.sr.expander.icon.ignoreColorBlindMode = False
                self.sr.expander.SetRGBA(0.0, 0.5, 0.0, 0.8)
        label = self.GetTopLabelText(node)
        self.sr.topLabel.text = label
        self.sr.bottomLabel.top = max(12, self.sr.topLabel.top + self.sr.topLabel.textheight)
        bottomLabelText = self.GetBottomLabelText(node)
        self.sr.bottomLabel.text = bottomLabelText
        icons = getattr(node.commanderData, 'roleIcons', [])
        UpdateRoleIcons(self.roleIconsContainer, icons)
        if node.commanderData and node.commanderData.changing:
            self.sr.changing.state = uiconst.UI_DISABLED
            self.hint = localization.GetByLabel('UI/Fleet/FleetWindow/MemberChanging')
            self.sr.changing.Play()
        else:
            self.hint = None
            self.sr.changing.Stop()
            self.sr.changing.state = uiconst.UI_HIDDEN
        autoJoinIcon = getattr(self, 'autoJoinIcon', None)
        if node.showAsAutoJoinSquad:
            left = self.sr.topLabel.left + self.sr.topLabel.textwidth + 4
            if autoJoinIcon is None or autoJoinIcon.destroyed:
                self.autoJoinIcon = Sprite(parent=self, texturePath='res:/UI/Texture/classes/fleet/defaultSquad.png', hint=localization.GetByLabel('UI/Fleet/FleetWindow/DefaultSquadHint'), align=uiconst.TOPLEFT, pos=(left,
                 0,
                 16,
                 16))
            self.autoJoinIcon.display = True
            self.autoJoinIcon.left = left
        elif autoJoinIcon:
            autoJoinIcon.display = False

    def OnDropData(self, dragObject, droppedGuys, *args):
        try:
            sm.GetService('fleet').OnDropCommanderDropData(dragObject, droppedGuys, self.sr.node)
        finally:
            self.movingHilite.display = False

    def OnDragEnter(self, dragObj, nodes):
        draggedGuy = nodes[0]
        if hasattr(draggedGuy, 'charID'):
            if self.sr.node.commanderData and self.sr.node.commanderData.itemID == draggedGuy.charID:
                return
        groupType = self.sr.node.groupType
        groupID = self.sr.node.groupID
        isMultiMove = len(nodes) > 1
        canMove = sm.GetService('fleet').CanMoveToThisEntry(draggedGuy, self.sr.node, groupType, groupID=groupID, isMultiMove=isMultiMove)
        if canMove == CONNOT_BE_MOVED_INCOMPATIBLE:
            return
        if canMove == CANNOT_BE_MOVED:
            self.movingHilite.SetRGBA(*COLOR_CANNOT_BE_MOVED)
        elif canMove == CAN_BE_COMMANDER:
            self.movingHilite.SetRGBA(*COLOR_CAN_BE_COMMANDER)
        else:
            self.movingHilite.SetRGBA(*COLOR_CAN_ONLY_BE_MEMBER)
        self.movingHilite.display = True

    def OnDragExit(self, dragObj, nodes):
        self.movingHilite.display = False

    def GetHeight(self, *args):
        node, width = args
        topLabelHeight = uix.GetTextHeight('<b>' + node.groupInfo + '</b>', maxLines=1)
        bottomLabelHeight = uix.GetTextHeight(node.commanderName, maxLines=1)
        node.height = max(12, topLabelHeight) + bottomLabelHeight + 2
        return node.height

    def ToggleAllSquads(self, node, isOpen = True):
        toggleThread = uthread.new(self.ToggleAllSquads_thread, node, isOpen)
        toggleThread.context = 'FleetHeader::ToggleAllSquads'

    def ToggleAllSquads_thread(self, node, isOpen = True):
        if isOpen:
            self.DoToggleFleetHeader(node, isOpen, groupType='fleet')
            self.DoToggleFleetHeader(node, isOpen, groupType='wing')
        self.DoToggleFleetHeader(node, isOpen, groupType='squad')

    def ToggleAllWings(self, node, isOpen = True):
        toggleThread = uthread.new(self.ToggleAllWings_thread, node, isOpen)
        toggleThread.context = 'FleetHeader::ToggleAllWings'

    def ToggleAllWings_thread(self, node, isOpen = True):
        if isOpen:
            self.DoToggleFleetHeader(node, isOpen, groupType='fleet')
        self.DoToggleFleetHeader(node, isOpen, groupType='wing')

    def DoToggleFleetHeader(self, node, isOpen, groupType):
        scroll = node.scroll
        for entry in scroll.GetNodes():
            if entry.__guid__ != 'listentry.FleetHeader':
                continue
            if entry.groupType == groupType:
                if entry.panel:
                    self.ShowOpenState(isOpen)
                    self.UpdateLabel()
                    uicore.registry.SetListGroupOpenState(entry.id, isOpen)
                    scroll.PrepareSubContent(entry)
                else:
                    uicore.registry.SetListGroupOpenState(entry.id, isOpen)
                    entry.scroll.PrepareSubContent(entry)

    def OnMouseDown(self, *args):
        commanderData = self.sr.node.commanderData
        if commanderData is None:
            return
        GetMenuService().TryExpandActionMenu(itemID=commanderData.charID, clickedObject=self, radialMenuClass=RadialMenuSpaceCharacter)

    def GetMenu(self):
        m = MenuList()
        commanderData = self.sr.node.commanderData
        if commanderData:
            m += GetMenuService().FleetMenu(commanderData.charID, unparsed=False)
            m += [None]
            m.append(MenuEntryData(MenuLabel('UI/Common/Pilot', {'character': commanderData.charID}), subMenuData=lambda : self._GetPilotSubMenuData(commanderData.charID), texturePath=eveicon.person))
        m += [None]
        if self.sr.node.groupType == 'squad':
            return m + GetSquadMenu(self.sr.node.groupID)
        if self.sr.node.groupType == 'wing':
            return m + self.GetWingMenu(self.sr.node.groupID)
        if self.sr.node.groupType == 'fleet':
            m += self.GetFleetMenu()
            m += [None]
            m += [(MenuLabel('UI/Fleet/FleetWindow/OpenAllWings'), self.ToggleAllWings, (self.sr.node, True)),
             (MenuLabel('UI/Fleet/FleetWindow/CloseAllWings'), self.ToggleAllWings, (self.sr.node, False)),
             (MenuLabel('UI/Fleet/FleetWindow/OpenAllSquads'), self.ToggleAllSquads, (self.sr.node, True)),
             (MenuLabel('UI/Fleet/FleetWindow/CloseAllSquads'), self.ToggleAllSquads, (self.sr.node, False))]
            return m
        raise NotImplementedError

    def _GetPilotSubMenuData(self, charID):
        subMenuData = GetMenuService().CharacterMenu(charID)
        return MenuList(subMenuData).filter(['UI/Fleet/Fleet', 'UI/Commands/ShowInfo'])

    def GetFleetMenu(self):
        ret = MenuList()
        if session.fleetrole != evefleet.fleetRoleLeader:
            ret += [(MenuLabel('UI/Fleet/LeaveMyFleet'), FleetSvc().LeaveFleet)]
        if FleetSvc().IsBoss() or session.fleetrole == evefleet.fleetRoleLeader:
            ret.extend([None, (MenuLabel('UI/Fleet/FleetWindow/CreateNewWing'), lambda : FleetSvc().CreateWing())])
        else:
            ret.append(None)
        if session.fleetrole in evefleet.fleetCmdrRoles:
            ret.append((MenuLabel('UI/Fleet/FleetWindow/Regroup'), lambda : FleetSvc().Regroup()))
        if FleetSvc().HasActiveBeacon(session.charid):
            ret.append((MenuLabel('UI/Fleet/FleetBroadcast/Commands/JumpBeacon'), lambda : FleetSvc().SendBroadcast_JumpBeacon()))
        ret.append((MenuLabel('UI/Fleet/FleetBroadcast/Commands/Location'), lambda : FleetSvc().SendBroadcast_Location()))
        return ret

    def GetWingMenu(self, wingID):
        if FleetSvc().IsBoss() or session.fleetrole in (evefleet.fleetRoleLeader, evefleet.fleetRoleWingCmdr):
            return MenuList([(MenuLabel('UI/Fleet/FleetWindow/DeleteWing'), lambda : sm.GetService('fleet').DeleteWing(wingID)), (MenuLabel('UI/Fleet/FleetWindow/ChangeName'), lambda : sm.GetService('fleet').ChangeWingName(wingID)), (MenuLabel('UI/Fleet/FleetWindow/CreateNewSquad'), lambda : sm.GetService('fleet').CreateSquad(wingID))])
        else:
            return MenuList()

    def Flash(self):
        sm.GetService('ui').BlinkSpriteA(self.sr.topLabel, 1.0, 400, 8, passColor=0)
        sm.GetService('ui').BlinkSpriteA(self.sr.bottomLabel, 1.0, 400, 8, passColor=0)

    def GetDragData(self, *args):
        commanderData = self.sr.node.commanderData
        if commanderData:
            info = cfg.eveowners.Get(commanderData.charID)
            fakeNode = self.sr.node
            fakeNode.info = info
            fakeNode.charID = commanderData.charID
            fakeNode.itemID = commanderData.charID
            return [fakeNode]
        else:
            return []

    @classmethod
    def GetTopLabelText(cls, node, *args):
        label = localization.GetByLabel('UI/Fleet/FleetWindow/UnitHeader', unitTitle=node.groupInfo)
        if node.numMembers == 0:
            label = '<color=0x88ffffff>%s</color>' % label
        return label

    @classmethod
    def GetBottomLabelText(cls, node, *args):
        label = node.commanderName
        return label

    @classmethod
    def GetCopyData(cls, node):
        sublevel = node.Get('sublevel', 0)
        indent = ' ' * sublevel * 4
        topLabel = cls.GetTopLabelText(node)
        bottomLabel = cls.GetBottomLabelText(node)
        text = indent + '-' + topLabel + '\n ' + indent + bottomLabel
        return text


def UpdateRoleIcons(parent, icons):
    parent.Flush()
    left = 0
    if icons is not None and len(icons):
        parent.width = len(icons) * 20
        for icon in icons:
            iconpath = icon['id']
            eveIcon.Icon(icon=iconpath, parent=parent, pos=(left,
             0,
             16,
             16), align=uiconst.TOPLEFT, hint=icon['hint'])
            left += 20


def FleetSvc():
    return sm.GetService('fleet')


def GetFleetMenu():
    ret = MenuList([(localization.GetByLabel('UI/Fleet/LeaveMyFleet'), FleetSvc().LeaveFleet)])
    if FleetSvc().IsBoss() or session.fleetrole == evefleet.fleetRoleLeader:
        ret.extend([None, (localization.GetByLabel('UI/Fleet/FleetWindow/Regroup'), lambda : FleetSvc().Regroup())])
    else:
        ret.append(None)
    if FleetSvc().HasActiveBeacon(session.charid):
        ret.append((localization.GetByLabel('UI/Fleet/FleetBroadcast/Commands/JumpBeacon'), lambda : FleetSvc().SendBroadcast_JumpBeacon()))
    ret.append((localization.GetByLabel('UI/Fleet/FleetBroadcast/Commands/Location'), lambda : FleetSvc().SendBroadcast_Location()))
    return ret


class EmptyGroup(Generic):
    __guid__ = 'listentry.EmptyGroup'

    def Load(self, data):
        Generic.Load(self, data)
        self.sr.label.left = 20 + 16 * data.indent
        self.sr.label.opacity = 0.7
        self.sr.label.Update()
        self.movingHilite = Fill(bgParent=self, name='movingHilite', color=(1, 0, 0, 0.25))
        self.movingHilite.display = False
        autoJoinIcon = getattr(self, 'autoJoinIcon', None)
        if data.showAsAutoJoinSquad:
            left = self.sr.label.left + self.sr.label.textwidth + 4
            if autoJoinIcon is None or autoJoinIcon.destroyed:
                self.autoJoinIcon = Sprite(parent=self, texturePath='res:/UI/Texture/classes/fleet/defaultSquad.png', hint=localization.GetByLabel('UI/Fleet/FleetWindow/DefaultSquadHint'), align=uiconst.CENTERLEFT, pos=(left,
                 0,
                 16,
                 16))
            self.autoJoinIcon.display = True
            self.autoJoinIcon.left = left
        elif autoJoinIcon:
            autoJoinIcon.display = False

    def OnDropData(self, dragObject, droppedGuys, *args):
        try:
            sm.GetService('fleet').OnDropCommanderDropData(dragObject, droppedGuys, self.sr.node)
        finally:
            self.movingHilite.display = False

    def OnDragEnter(self, dragObj, nodes):
        draggedGuy = nodes[0]
        groupType = self.sr.node.groupType
        groupID = self.sr.node.groupID
        isMultiMove = len(nodes) > 1
        canMove = sm.GetService('fleet').CanMoveToThisEntry(draggedGuy, self.sr.node, groupType, groupID=groupID, isMultiMove=isMultiMove)
        if canMove == CONNOT_BE_MOVED_INCOMPATIBLE:
            return
        if canMove == CANNOT_BE_MOVED:
            self.movingHilite.SetRGBA(*COLOR_CANNOT_BE_MOVED)
        elif canMove == CAN_BE_COMMANDER:
            self.movingHilite.SetRGBA(*COLOR_CAN_BE_COMMANDER)
        else:
            self.movingHilite.SetRGBA(*COLOR_CAN_ONLY_BE_MEMBER)
        self.movingHilite.display = True

    def OnDragExit(self, dragObj, nodes):
        self.movingHilite.display = False

    @classmethod
    def GetCopyData(cls, node):
        sublevel = node.Get('isSub', 0)
        indent = ' ' * sublevel * 4
        return indent + node.label


class FleetMember(BaseTacticalEntry):
    __guid__ = 'listentry.FleetMember'
    isDragObject = True

    def Startup(self, *args, **kw):
        BaseTacticalEntry.Startup(self, *args, **kw)
        idx = self.sr.label.parent.children.index(self.sr.label)
        text_gaugepar = Container(name='text_gaugepar', parent=self, idx=idx, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        text_gaugepar.width = 0
        textpar = Container(name='textpar', parent=text_gaugepar, idx=idx, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=True)
        self.sr.text_gaugepar = text_gaugepar
        self.children.remove(self.sr.label)
        textpar.children.append(self.sr.label)
        Container(name='toppush', parent=textpar, align=uiconst.TOTOP, height=2)
        roleIconsContainer = Container(name='roleIconsContainer', parent=textpar, width=0, align=uiconst.TORIGHT)
        self.roleIconsContainer = roleIconsContainer
        changing = AnimSprite(icons=[ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ], align=uiconst.TOPRIGHT, parent=self, pos=(0, 0, 16, 16))
        self.sr.changing = changing
        changing.state = uiconst.UI_HIDDEN
        self.sr.myGroupSelection = Fill(name='myGroupSelection', bgParent=self, padding=(0, 1, 0, 1), color=(0.0, 0.5, 0.0, 0.15))
        self.sr.myGroupSelection.display = False
        self.movingHilite = Fill(bgParent=self, name='movingHilite', color=(1, 0, 0, 0.25))
        self.movingHilite.display = False

    def Load(self, node):
        Generic.Load(self, node)
        data = node
        if settings.user.ui.Get('flatFleetView', False):
            left = 0
        else:
            left = 20
            if node.itemID == session.charid:
                self.sr.myGroupSelection.display = True
        indent = left + node.sublevel * 16
        self.sr.label.left = indent
        selected, = sm.GetService('stateSvc').GetStates(data.itemID, [state.selected])
        if selected:
            self.Select()
        icons = node.Get('roleIcons', None)
        UpdateRoleIcons(self.roleIconsContainer, icons)
        if node.changing:
            self.sr.changing.state = uiconst.UI_DISABLED
            self.hint = localization.GetByLabel('UI/Fleet/FleetWindow/MemberChanging')
            self.sr.changing.Play()
        else:
            self.hint = None
            self.sr.changing.Stop()
            self.sr.changing.state = uiconst.UI_HIDDEN
        self.sr.label.Update()

    def GetHeight(_self, *args):
        node, width = args
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 4
        return node.height

    def GetDragData(self, *args):
        selectedNodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        for eachNode in selectedNodes:
            info = cfg.eveowners.Get(eachNode.itemID)
            eachNode.info = info

        return selectedNodes

    def OnDropData(self, dragObject, droppedGuys, *args):
        if FLEET_VIEW_FLAT_LIST_SETTING.is_enabled():
            self.movingHilite.display = False
            return
        try:
            sm.GetService('fleet').OnDropCommanderDropData(dragObject, droppedGuys, self.sr.node)
        finally:
            self.movingHilite.display = False

    def OnDragEnter(self, dragObj, nodes):
        draggedGuy = nodes[0]
        if hasattr(draggedGuy, 'charID'):
            if self.sr.node.itemID == draggedGuy.charID:
                return
        isMultiMove = len(nodes) > 1
        canMove = sm.GetService('fleet').CanMoveToThisEntry(draggedGuy, self.sr.node, 'fleetMember', groupID=None, isMultiMove=isMultiMove)
        if canMove == CONNOT_BE_MOVED_INCOMPATIBLE:
            return
        if canMove == CANNOT_BE_MOVED:
            self.movingHilite.SetRGBA(*COLOR_CANNOT_BE_MOVED)
        else:
            self.movingHilite.SetRGBA(*COLOR_CAN_ONLY_BE_MEMBER)
        self.movingHilite.display = True

    def OnDragExit(self, dragObj, nodes):
        self.movingHilite.display = False

    def GetMenu(self):
        return GetFleetMemberMenuOptions(self.sr.node.charID)

    def OnMouseDown(self, *args):
        GetMenuService().TryExpandActionMenu(itemID=self.sr.node.charID, clickedObject=self, radialMenuClass=RadialMenuSpaceCharacter)

    @classmethod
    def GetCopyData(cls, node):
        sublevel = node.Get('isSub', 0)
        indent = ' ' * sublevel * 4
        return indent + node.label

    GetMenu = ParanoidDecoMethod(GetMenu, ('sr', 'node'))


class FleetAction(Action):

    def ApplyAttributes(self, attributes):
        super(FleetAction, self).ApplyAttributes(attributes)
        self.broadcastID = attributes.broadcastID
        texturePath = attributes.texturePath
        self.func = attributes.func
        self.sr.icon = self.icon = GlowSprite(texturePath=texturePath, parent=self, align=uiconst.CENTER, pos=(1, 0, 16, 16), state=uiconst.UI_DISABLED)
        self.sr.fill = Fill(parent=self, state=uiconst.UI_HIDDEN, width=self.width, height=self.height, align=uiconst.RELATIVE, color=(1, 1, 1, 0.5))

    def Prepare_(self, icon = None):
        pass

    def OnMouseMove(self, *args):
        pass

    def OnClick(self, *args):
        self.func()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.broadcastID:
            return
        cmdName = 'CmdFleetBroadcast_%s' % self.broadcastID
        cmd = uicore.cmd.commandMap.GetCommandByName(cmdName)
        shortcutStr = cmd.GetShortcutAsString()
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.hint, cellPadding=(0, 0, 7, 0), colSpan=tooltipPanel.columns - 1, width=200, autoFitToText=True)
        if shortcutStr:
            tooltipPanel.AddShortcutCell(shortcutStr)
        else:
            tooltipPanel.AddCell()


class FleetRoleCont(Container):
    __guid__ = 'xtriui.FleetRoleCont'
    __notifyevents__ = ['OnMyFleetInfoChanged', 'OnSessionChanged']
    __dependencies__ = ['fleet']
    default_height = 16
    default_name = 'fleetRoleCont'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.buttons = {}
        self.roleIconsContainer = Container(name='roleIconsContainer', parent=self, align=uiconst.TOLEFT)
        self.UpdateRoleIcons()

    def UpdateRoleIcons(self):
        info = sm.GetService('fleet').GetMemberInfo(session.charid)
        if info is None:
            return
        icons = []
        if info.role == evefleet.fleetRoleLeader:
            icons.append({'id': 'ui_73_16_17',
             'hint': localization.GetByLabel('UI/Fleet/Ranks/FleetCommander')})
        elif info.role == evefleet.fleetRoleWingCmdr:
            icons.append({'id': 'ui_73_16_18',
             'hint': localization.GetByLabel('UI/Fleet/Ranks/WingCommander')})
        elif info.role == evefleet.fleetRoleSquadCmdr:
            icons.append({'id': 'ui_73_16_19',
             'hint': localization.GetByLabel('UI/Fleet/Ranks/SquadCommander')})
        if info.job & evefleet.fleetJobCreator:
            icons.append({'id': 'ui_73_16_20',
             'hint': localization.GetByLabel('UI/Fleet/Ranks/Boss')})
        self.display = bool(icons)
        UpdateRoleIcons(self.roleIconsContainer, icons)

    def OnMyFleetInfoChanged(self):
        self.UpdateRoleIcons()

    def OnSessionChanged(self, isRemote, sess, change):
        if not self.destroyed:
            self.UpdateRoleIcons()


class WatchListPanel(ActionPanel):
    __guid__ = 'form.WatchListPanel'
    __notifyevents__ = ['OnFleetFavoriteAdded',
     'OnFleetFavoriteRemoved',
     'OnFleetFavoritesRemoved',
     'OnFleetMemberChanged_Local',
     'DoBallsAdded',
     'DoBallRemove',
     'OnFleetBroadcast_Local',
     'OnMyFleetInfoChanged',
     'DoBallsRemove',
     'OnSlimItemChange',
     'OnStateChange',
     'OnFleetWatchlistColorChanged']
    __dependencies__ = ['fleet']
    default_windowID = 'watchlistpanel'
    cursor = uiconst.UICURSOR_HASMENU

    def ApplyAttributes(self, attributes):
        super(WatchListPanel, self).ApplyAttributes(attributes)
        self.MakeKillable()

    def IsFavorite(self, charid):
        if sm.GetService('fleet').GetFavorite(charid):
            return True
        else:
            return False

    def AddBroadcastIcon(self, charid, icon, hint):
        if not self.IsFavorite(charid):
            return
        self.broadcasts[charid] = KeyVal(icon=icon, hint=hint, timestamp=blue.os.GetWallclockTime())
        for eachNode in self.sr.scroll.GetNodes():
            if eachNode.charID != charid:
                continue
            if eachNode.charID in self.broadcasts:
                eachNode.icon = self.broadcasts[eachNode.charID].icon
                eachNode.hint = localization.GetByLabel('UI/Fleet/Watchlist/WatchlistHintWithBroadcast', role=fleetbroadcastexports.GetRankName(eachNode.member), broadcast=self.broadcasts[eachNode.charID].hint, time=self.broadcasts[eachNode.charID].timestamp)
            else:
                eachNode.icon = None
                eachNode.hint = localization.GetByLabel('UI/Fleet/Watchlist/WatchlistHint', role=fleetbroadcastexports.GetRankName(eachNode.member))
            if eachNode.panel:
                eachNode.panel.Load(eachNode)

    def OnFleetBroadcast_Local(self, broadcast):
        if broadcast.name not in fleetBroadcastConst.iconsByBroadcastType:
            icon = 'ui_38_16_70'
        else:
            icon = fleetBroadcastConst.iconsByBroadcastType[broadcast.name]
        self.AddBroadcastIcon(broadcast.charID, icon, broadcast.broadcastLabel)

    def ClearBroadcastHistory(self):
        self.broadcasts = {}
        self.UpdateAll(keepPosition=True)

    def ClearColors(self):
        settings.char.ui.Set(WATCHLIST_COLORS_CONFIG, {})
        self.UpdateAll()

    def OnMyFleetInfoChanged(self):
        self.UpdateAll(keepPosition=True)

    def PostStartup(self):
        self.scope = uiconst.SCOPE_INGAME
        self.name = 'watchlistpanel'
        self.broadcasts = {}
        self.sr.scroll = eveScroll.Scroll(parent=self.sr.main)
        self.sr.scroll.sr.content.OnDropData = self.DropInWatchList
        self.sr.scroll.OnChar = self.OnChar
        self.SetMinSize((256, 50))

    def OnChar(self, *args):
        return False

    def GetMenuMoreOptions(self):
        menuData = super(WatchListPanel, self).GetMenuMoreOptions()
        menuData += self.GetWatchListMenu()
        return menuData

    def GetWatchListMenu(self):
        ret = MenuList()
        if IsInColorEditMode():
            ret.append((localization.GetByLabel('UI/Fleet/Watchlist/ExitColorEditMode'), self.ChangeColorEditMode, (False,)))
        else:
            ret.append((localization.GetByLabel('UI/Fleet/Watchlist/EnterColorEditMode'), self.ChangeColorEditMode, (True,)))
        if FleetSvc().IsDamageUpdates():
            ret.append((localization.GetByLabel('UI/Fleet/Watchlist/TurnOffDamageUpdates'), self.SetDamageUpdates, (False,)))
        else:
            ret.append((localization.GetByLabel('UI/Fleet/Watchlist/TurnOnDamageUpdates'), self.SetDamageUpdates, (True,)))
        ret.append(None)
        ret.append((MenuLabel('UI/Fleet/Watchlist/ClearWatchList'), sm.GetService('fleet').RemoveAllFavorites))
        ret.append((localization.GetByLabel('UI/Fleet/Watchlist/ClearBroadcastIcons'), self.ClearBroadcastHistory))
        ret.append((localization.GetByLabel('UI/Fleet/Watchlist/ClearAllColors'), self.ClearColors))
        return ret

    def SetDamageUpdates(self, isit):
        FleetSvc().SetDamageUpdates(isit)
        self.UpdateAll()

    def ChangeColorEditMode(self, on):
        settings.char.ui.Set(EDIT_MODE_CONFIG, bool(on))
        self.UpdateAll()

    def UpdateAll(self, keepPosition = False):
        scrollTo = self.sr.scroll.GetScrollProportion() if keepPosition else 0.0
        self.sr.scroll.Clear()
        favorites = sm.GetService('fleet').GetFavorites()
        self.UpdateHintAndKillableState(favorites)
        entries = []
        for character in favorites:
            data = self.GetEntryData(character.charID)
            if data is not None:
                entries.append(GetFromClass(WatchListEntry, data))

        self.sr.scroll.AddEntries(-1, entries)
        if scrollTo:
            self.sr.scroll.ScrollToProportion(scrollTo, threaded=False)
        if self.panelname:
            self.SetCaption('%s [%s]' % (self.panelname, len(entries)))

    def UpdateHintAndKillableState(self, favorites = None):
        if favorites is None:
            favorites = sm.GetService('fleet').GetFavorites()
        if favorites:
            self.MakeUnKillable()
        else:
            self.MakeKillable()
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Fleet/Watchlist/DropFleetMembers'))

    def UpdateSlimItem(self, charID):
        if not sm.GetService('fleet').GetMemberInfo(charID):
            return
        for node in self.sr.scroll.GetNodes():
            if node.charID == charID:
                slimItem = SlimItemFromCharID(charID)
                node.slimItem = weakref.ref(slimItem) if slimItem else None
                node.slimItemID = None
                if node.panel:
                    node.panel.Load(node)
                return

    def RemoveCharacterFromScroll(self, charID):
        for node in self.sr.scroll.GetNodes():
            if node.charID == charID:
                self.sr.scroll.RemoveNodes([node])
                if self.panelname:
                    self.SetCaption('%s [%s]' % (self.panelname, len(self.sr.scroll.sr.nodes)))
                self.UpdateHintAndKillableState()
                return

    def OnFleetFavoriteAdded(self, charIDs):
        self.UpdateAll(keepPosition=True)

    def OnFleetFavoriteRemoved(self, charID):
        if self.destroyed:
            return
        self.RemoveCharacterFromScroll(charID)

    def OnFleetFavoritesRemoved(self):
        if self.destroyed:
            return
        self.UpdateAll()

    def OnFleetWatchlistColorChanged(self):
        self.UpdateAll()

    def OnFleetMemberChanged_Local(self, charID, *args):
        if sm.GetService('fleet').GetFavorite(charID):
            self.UpdateAll(keepPosition=True)

    def DoBallsAdded(self, lst):
        for ball, slimItem in lst:
            if ball.id < destiny.DSTLOCALBALLS:
                return
            if sm.GetService('fleet').GetFavorite(slimItem.charID):
                self.UpdateSlimItem(slimItem.charID)

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if slimItem is None:
            return
        if getattr(slimItem, 'charID', None):
            if sm.GetService('fleet').GetFavorite(slimItem.charID):
                self.UpdateSlimItem(slimItem.charID)

    def GetEntryData(self, charID):
        slimItem = SlimItemFromCharID(charID)
        data = KeyVal()
        member = sm.GetService('fleet').GetMemberInfo(charID)
        if not member:
            return
        data.charRec = cfg.eveowners.Get(charID)
        data.itemID = data.id = data.charID = charID
        data.typeID = data.charRec.typeID
        data.squadID = member.squadID
        data.wingID = member.wingID
        data.displayName = member.charName
        data.roleString = member.roleName
        data.label = localization.GetByLabel('UI/Common/CharacterNameLabel', charID=charID)
        data.member = member
        data.slimItem = None
        if charID in self.broadcasts:
            data.icon = self.broadcasts[charID].icon
            data.hint = localization.GetByLabel('UI/Fleet/Watchlist/WatchlistHintWithBroadcast', role=fleetbroadcastexports.GetRankName(member), broadcast=self.broadcasts[charID].hint, time=self.broadcasts[charID].timestamp)
        else:
            data.icon = None
            data.hint = localization.GetByLabel('UI/Fleet/Watchlist/WatchlistHint', role=fleetbroadcastexports.GetRankName(member))
        data.colorcoded = GetColorForCharID(charID)
        data.inColorSettingMode = IsInColorEditMode()
        if slimItem:
            data.slimItem = weakref.ref(slimItem)
        return data

    def DropInWatchList(self, dragObj, nodes, idx = None, *args):
        if dragObj.__guid__ == 'listentry.WatchListEntry':
            if len(nodes) != 1:
                return
            self.Move(dragObj, nodes, idx)
        else:
            charIDsToAdd = []
            for eachNode in nodes:
                textlinkCharID = GetCharIDFromTextLink(eachNode)
                if textlinkCharID:
                    itemID = textlinkCharID
                elif eachNode.__guid__ == 'uicontrols.Label':
                    itemID = self.GetLabelCharID(dragObj, eachNode)
                elif eachNode.__guid__ == 'listentry.FleetCompositionEntry':
                    itemID = eachNode.charID
                elif eachNode.__guid__ in AllUserEntries():
                    itemID = eachNode.itemID
                else:
                    continue
                if not FleetSvc().IsFavorite(itemID):
                    charIDsToAdd.append(itemID)

            if charIDsToAdd:
                FleetSvc().AddFavorite(charIDsToAdd)
                if idx is not None and len(charIDsToAdd) == 1:
                    self.Move(dragObj, nodes, idx)

    def Move(self, dragObj, entries, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        charID = entries[0].itemID
        if not charID:
            charID = self.GetLabelCharID(dragObj, entries[0])
        if not charID:
            return
        if idx is not None:
            if selected:
                selected = selected[0]
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = idx
        else:
            newIdx = len(self.sr.scroll.GetNodes()) - 1
        sm.GetService('fleet').ChangeFavoriteSorting(charID, newIdx)
        self.UpdateAll(keepPosition=True)

    def GetLabelCharID(self, dragObj, entry):
        if dragObj.__guid__ == 'uicontrols.Label':
            labelInfo = entry.url.split('//')
            try:
                charID = int(labelInfo[1])
            except:
                return None

            isCharacter = IsCharacter(charID)
            if isCharacter:
                return charID
            else:
                return None

    def OnSlimItemChange(self, oldSlim, newSlim):
        newSlimCharID = newSlim.charID
        for node in self.sr.scroll.GetNodes():
            if node.charID == newSlimCharID:
                node.slimItem = weakref.ref(newSlim)
                node.slimItemID = None
                if node.panel:
                    node.panel.UpdateShipIcon()

    def OnStateChange(self, itemID, flag, newState, *args):
        if flag not in (state.targeting, state.targeted):
            return
        for node in self.sr.scroll.GetNodes():
            if node.slimItemID == itemID and node.panel is not None:
                node.panel.OnChangingState(itemID, flag, newState)
                return


class WatchListEntry(BaseTacticalEntry):
    __guid__ = 'listentry.WatchListEntry'
    __notifyevents__ = []
    isDragObject = True

    def Startup(self, *args, **kw):
        BaseTacticalEntry.Startup(self, *args, **kw)
        self.colorcodedFill = Fill(bgParent=self, color=(0, 0, 0, 0))
        self.colorPickerParent = Container(name='colorPickerParent', parent=self, align=uiconst.TORIGHT, width=27)
        self.colorPicker = evefleet.client.FleetColorPickerCont(parent=self.colorPickerParent, align=uiconst.CENTERLEFT, callback=self.SetColorForEntry, idx=0)
        self.targetIconCont = TargetIconCont(parent=self, align=uiconst.CENTERLEFT, pos=(-1, 0, 18, 18))
        self.stateItemID = None
        self.leftPar = Container(name='leftPar', parent=self, align=uiconst.TOLEFT_NOPUSH, width=16)
        self.shipIcon = Sprite(parent=self.leftPar, align=uiconst.CENTERLEFT, pos=(0, 0, 16, 16))
        self.sr.posIndicatorCont = Container(name='posIndicator', parent=self, align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_DISABLED, height=2)
        self.sr.posIndicator = Fill(parent=self.sr.posIndicatorCont, state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.5))
        self.sr.gaugesContainer = Container(name='gaugesContainer', parent=self, align=uiconst.TORIGHT, width=78)
        labelContainer = Container(name='labelContainer', parent=self, align=uiconst.TOALL, clipChildren=True)
        self.sr.label.SetParent(labelContainer)
        self.broadcastIconContainer = Container(name='broadcastIconContainer', parent=self, align=uiconst.TORIGHT, width=20, idx=labelContainer.GetOrder())
        self.sr.icon = eveIcon.Icon(parent=self.broadcastIconContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16))
        self.sr.progress = AnimSprite(parent=self.leftPar, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN, pos=(0, 0, 16, 16), icons=[ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ])

    def Load(self, node):
        Generic.Load(self, node)
        data = node
        self.sr.label.left = 20
        self.UpdateDamage()
        selected, = sm.GetService('stateSvc').GetStates(data.itemID, [state.selected])
        if selected:
            self.Select()
        if node.icon is None:
            self.sr.icon.display = False
        else:
            self.sr.icon.LoadIcon(node.icon)
            self.sr.icon.display = True
        self.sr.label.Update()
        targeting, targeted = sm.GetService('stateSvc').GetStates(self.GetShipID(), [state.targeting, state.targeted])
        if targeting:
            self.targetIconCont.StartTargeting()
        elif targeted:
            self.targetIconCont.SetTargetedIcon()
        if node.colorcoded:
            fillColor = node.colorcoded + (0.25,)
            self.colorcodedFill.SetRGBA(*fillColor)
        self.UpdateShipIcon()
        if node.inColorSettingMode:
            self.colorPickerParent.display = True
            self.colorPicker.SetCurrentFill(self.sr.node.colorcoded)
        else:
            self.colorPickerParent.display = False

    def UpdateShipIcon(self):
        node = self.sr.node
        slimItem = node.slimItem
        if slimItem:
            if slimItem():
                typeID = slimItem().typeID
                texturePath = sm.GetService('bracket').GetBracketIcon(typeID)
            else:
                texturePath = None
            self.shipIcon.SetTexturePath(texturePath)
        self.SetShipIconDisplay()

    def SetShipIconDisplay(self):
        if InBubble(self.GetShipID()):
            self.shipIcon.display = True
        else:
            self.shipIcon.display = False

    def UpdateDamage(self):
        if not sm.GetService('fleet').IsDamageUpdates():
            self.HideDamageDisplay()
            return False
        self.SetShipIconDisplay()
        if BaseTacticalEntry.UpdateDamage(self):
            animations.SpColorMorphTo(self.sr.label, startColor=self.sr.label.rgb, endColor=eveColor.CHERRY_RED[:3], duration=0.5, curveType=uiconst.ANIM_WAVE, loops=5)

    def GetShipID(self):
        if not self.sr.node:
            return
        else:
            known = self.sr.node.Get('slimItemID', None)
            self.stateItemID = known
            if known:
                return known
            item = SlimItemFromCharID(self.sr.node.charID)
            if item is None:
                return
            self.sr.node.slimItemID = item.itemID
            self.stateItemID = item.itemID
            return item.itemID

    def GetHeight(_self, *args):
        return 24

    def OnClick(self, *args):
        item = SlimItemFromCharID(self.sr.node.charID)
        if item:
            loadedCombatCmd = uicore.cmd.GetCombatCmdLoadedName()
            itemID = item.itemID
            if loadedCombatCmd and loadedCombatCmd.name == 'CmdLockTargetItem':
                if sm.GetService('target').IsTarget(itemID):
                    sm.GetService('stateSvc').SetState(itemID, state.activeTarget, 1)
                    return
            uicore.cmd.ExecuteCombatCommand(itemID, uiconst.UI_CLICK)

    def OnDblClick(self, *args):
        if self.sr.node:
            self.sr.node.scroll.SelectNode(self.sr.node)

    def OnMouseDown(self, *args):
        GetMenuService().TryExpandActionMenu(itemID=self.sr.node.charID, clickedObject=self, radialMenuClass=RadialMenuSpaceCharacter)

    def GetMenu(self):
        m = []
        shipItem = SlimItemFromCharID(self.sr.node.charID)
        if shipItem:
            sessionChecker = SessionChecker(session, sm)
            celestial = CelestialChecker(shipItem, cfg, sessionChecker)
            if celestial.OfferBroadcastHealTarget():
                m += [MenuEntryData(MenuLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastHealTarget'), lambda : sm.GetService('fleet').SendBroadcast_Heal_Target(shipItem.itemID), texturePath=eveicon.heal_first_aid)]
        m += GetFleetMemberMenuOptions(self.sr.node.charID)
        return m

    def SetColorForEntry(self, color, *args):
        allColors = settings.char.ui.Get(WATCHLIST_COLORS_CONFIG, {})
        allColors[self.sr.node.charID] = color
        self.sr.node.colorcoded = color
        settings.char.ui.Set(WATCHLIST_COLORS_CONFIG, allColors)
        sm.ScatterEvent('OnFleetWatchlistColorChanged')

    def InitGauges(self):
        parent = self.sr.gaugesContainer
        if getattr(self, 'gaugesInited', False):
            self.sr.gaugeParent.state = uiconst.UI_DISABLED
            return
        barw, barh = (22, 8)
        borderw = 2
        barsw = (barw + borderw) * 3 + borderw
        par = Container(name='gauges', parent=parent, align=uiconst.TORIGHT, width=barsw + 2, height=0, left=0, top=0, idx=0)
        self.sr.gauges = []
        l = 2
        for each in ('STRUCT', 'ARMOR', 'SHIELD'):
            g = Container(name=each, align=uiconst.CENTERLEFT, width=barw, height=barh, left=l)
            g.name = 'gauge_%s' % each.lower()
            g.sr.bar = Fill(parent=g, align=uiconst.TOLEFT, color=eveColor.SILVER_GREY)
            Fill(parent=g, color=eveColor.CHERRY_RED[:3])
            par.children.append(g)
            self.sr.gauges.append(g)
            setattr(self.sr, 'gauge_%s' % each.lower(), g)
            l += barw + borderw

        self.sr.gaugeParent = par
        self.gaugesInited = True

    def GetDragData(self, *args):
        info = cfg.eveowners.Get(self.sr.node.itemID)
        self.sr.node.info = info
        self.sr.node.scroll.SelectNode(self.sr.node)
        return [self.sr.node]

    def OnDropData(self, dragObj, nodes, *args):
        if len(nodes) > 1:
            return
        if GetAttrs(self, 'parent', 'OnDropData'):
            self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)

    def OnDragEnter(self, dragObj, nodes, *args):
        if len(nodes) > 1:
            return
        node = nodes[0]
        charID = getattr(node, 'charID', None)
        if not charID:
            return
        if self.sr.node.charID == charID:
            return
        guid = getattr(node, '__guid__', None)
        if guid == 'listentry.WatchListEntry':
            self.sr.posIndicator.state = uiconst.UI_DISABLED
        if sm.GetService('fleet').CheckCanAddFavorite(charID):
            self.sr.posIndicator.state = uiconst.UI_DISABLED

    def OnDragExit(self, *args):
        self.sr.posIndicator.state = uiconst.UI_HIDDEN

    def OnChangingState(self, itemID, flag, newState):
        if flag == state.targeting:
            self.targetIconCont.HandleTargetingChanges(newState)
        elif flag == state.targeted:
            self.targetIconCont.HandleTargetedChanges(newState)

    def GetIdForItem(self):
        return self.GetShipID()


def GetFleetMemberMenuOptions(charID):
    shipItem = SlimItemFromCharID(charID)
    if shipItem is None:
        ret = MenuList()
    else:
        ret = MenuList([ entry for entry in sm.GetService('menu').CelestialMenu(shipItem.itemID) if _IsWantedOption(entry) ])
        ret += [None]
    ret += GetMenuService().FleetMenu(charID, unparsed=False)
    ret += [None]
    ret.append(MenuEntryData(MenuLabel('UI/Common/Pilot', {'character': charID}), subMenuData=lambda : GetMenuService().CharacterMenu(charID), texturePath=eveicon.person))
    return ret.filter({'UI/Fleet/Fleet', 'UI/Commands/ShowInfo'})


wantedOptions = {'UI/Inflight/LockTarget',
 'UI/Inflight/ApproachObject',
 'UI/Inflight/OrbitObject',
 'UI/Inflight/Submenus/KeepAtRange',
 'UI/Fleet/JumpThroughToSystem'}

def _IsWantedOption(entry):
    if not entry:
        return False
    elif isinstance(entry, MenuEntryData):
        return entry.GetLabelPath() in wantedOptions
    else:
        return isinstance(entry[0], MenuLabel) and entry[0][0] in wantedOptions


def IsInColorEditMode():
    return bool(settings.char.ui.Get(EDIT_MODE_CONFIG, True))


def GetColorForCharID(charID):
    allColors = settings.char.ui.Get(WATCHLIST_COLORS_CONFIG, {})
    return allColors.get(charID)


def GetAllFleetActivities():
    return {k:localization.GetByLabel(v) for k, v in fleetActivityNames.iteritems()}


def GetFleetActivityName(activityID):
    if activityID not in fleetActivityNames:
        activityID = ACTIVITY_MISC
    labelPath = fleetActivityNames.get(activityID, 'UI/Agency/Fleetup/UnknownActivity')
    return localization.GetByLabel(labelPath)
