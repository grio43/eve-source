#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_tracking.py
import utillib
from carbon.common.script.util.format import FmtDate
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import NiceFilter
from eve.client.script.ui.control import eveScroll
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.quickFilter import QuickFilterEdit
import evetypes
import uthread
from eve.client.script.ui.util import uix
import carbonui.const as uiconst
import localization
from eve.client.script.ui.shared.userentry import User
from eveservices.menu import StartMenuService
from bannedwords.client import bannedwords
from eve.common.lib import appConst as const

class CorpMemberTracking(Container):
    __guid__ = 'form.CorpMemberTracking'
    __nonpersistvars__ = []
    is_loaded = False

    def Load(self, panel_id, *args):
        if self.is_loaded:
            return
        self.is_loaded = True
        toppar = Container(name='toppar', parent=self, align=uiconst.TOTOP, height=32, padTop=10)
        self.sr.fltRole = Combo(label=localization.GetByLabel('UI/Corporations/Common/Role'), parent=toppar, options=self._GetRoleOptions(), name='rolegroup', callback=self.OnFilterChange, width=146)
        self.sr.fltOnline = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/OnlineOnly'), parent=toppar, settingsKey='corpMembersOnline', checked=settings.char.ui.Get('corpMembersOnline'), align=uiconst.CENTERLEFT, callback=self.OnFilterChange, pos=(self.sr.fltRole.width + 16,
         0,
         250,
         0), settingsPath=('char', 'ui'))
        self.quickFilter = QuickFilterEdit(name='filterMembers', parent=toppar, align=uiconst.TORIGHT, left=4, isCharacterField=True)
        self.quickFilter.ReloadFunction = lambda : self.ShowMemberTracking()
        memberIDs = sm.GetService('corp').GetMemberIDs()
        cfg.eveowners.Prime(memberIDs)
        self.sr.scroll = eveScroll.Scroll(name='member_tracking', parent=self, padding=(0, 8, 0, 0))
        self.ShowMemberTracking()

    def _GetRoleOptions(self):
        viewOptionsList2 = [(localization.GetByLabel('UI/Common/All'), None)]
        self.sr.roleGroupings = sm.GetService('corp').GetRoleGroupings()
        for grp in self.sr.roleGroupings.itervalues():
            if grp.roleGroupID in (1, 2):
                for c in grp.columns:
                    role = c[1][0][1]
                    viewOptionsList2.append([role.shortDescription, role.roleID])

        return viewOptionsList2

    def OnFilterChange(self, *args):
        self.ShowMemberTracking()

    def OnReturn(self, *args):
        uthread.new(self.ShowMemberTracking)

    def GetLastLoggedOnText(self, numHours):
        if numHours == None:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/MoreThanAMonth')
        elif numHours < 0:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/Online')
        elif numHours < 1:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/LessThanAnHour')
        elif numHours < 24:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/Hours', hourCount=int(numHours), hours=numHours)
        elif numHours < 168:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/LastWeek')
        elif numHours < 720:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/LastMonth')
        else:
            return localization.GetByLabel('UI/Corporations/CorpMemberTracking/MoreThanAMonth')

    def ShowMemberTracking(self):
        fltRole = self.sr.fltRole.GetValue()
        fltOnline = self.sr.fltOnline.GetValue()
        scrolllist = []
        header = [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/LastOnlineColumnHeader'),
         localization.GetByLabel('UI/Corporations/Common/Title'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberBase'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/JoinedColumnHeader')]
        if eve.session.corprole & const.corpRoleDirector > 0:
            header.extend([localization.GetByLabel('UI/Common/Ship'),
             localization.GetByLabel('UI/Common/Location'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Members/FactionEnlistment'),
             localization.GetByLabel('UI/Common/Online'),
             localization.GetByLabel('UI/Common/Offline')])
        sm.GetService('loading').Cycle('Loading')
        try:
            memberTracking = sm.GetService('corp').GetMemberTrackingInfo()
            memberNames = []
            for member in memberTracking:
                memberNames.append(utillib.KeyVal(name=cfg.eveowners.Get(member.characterID).name, member=member))

            guestFilter = self.quickFilter.GetValue()
            if len(guestFilter):
                bannedwords.check_search_words_allowed(guestFilter)
                memberNames = NiceFilter(self.quickFilter.QuickFilter, memberNames)
            corpFactionID = sm.GetService('facwar').GetCorporationWarFactionID(session.corpid)
            amIDirector = eve.session.corprole & const.corpRoleDirector > 0
            locationsToPrime = set()
            for each in memberNames:
                member = each.member
                if member.baseID:
                    locationsToPrime.add(member.baseID)
                if amIDirector and member.locationID:
                    locationsToPrime.add(member.locationID)

            cfg.evelocations.Prime(locationsToPrime)
            for each in memberNames:
                member = each.member
                if fltRole and not (member.roles & fltRole > 0 or member.grantableRoles & fltRole > 0 or member.roles & const.corpRoleDirector > 0):
                    continue
                if fltOnline > 0:
                    if member.lastOnline == None or member.lastOnline >= 0:
                        continue
                base = ''
                if member.baseID:
                    base = cfg.evelocations.Get(member.baseID).locationName
                name = cfg.eveowners.Get(member.characterID).ownerName
                label = '%s<t>%s<t>%s<t>%s<t>%s' % (name,
                 self.GetLastLoggedOnText(member.lastOnline),
                 member.title,
                 base,
                 FmtDate(member.startDateTime, 'ln'))
                if eve.session.corprole & const.corpRoleDirector > 0:
                    shipTypeName = localization.GetByLabel('UI/Generic/None')
                    if member.shipTypeID is not None:
                        shipTypeName = evetypes.GetName(member.shipTypeID)
                    locationName = localization.GetByLabel('UI/Generic/Unknown')
                    if member.locationID is not None:
                        try:
                            locationName = cfg.evelocations.Get(member.locationID).locationName
                        except KeyError:
                            pass

                    factionID = corpFactionID or member.factionID
                    factionName = cfg.eveowners.Get(factionID).name if factionID else '-'
                    label += '<t>%s<t>%s<t>%s<t>%s<t>%s' % (shipTypeName,
                     locationName,
                     factionName,
                     FmtDate(member.logonDateTime, 'ls') if member.logonDateTime is not None else localization.GetByLabel('UI/Generic/Unknown'),
                     FmtDate(member.logoffDateTime, 'ls') if member.logoffDateTime is not None else localization.GetByLabel('UI/Generic/Unknown'))
                sort_key = 'sort_%s' % localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Tracking/LastOnlineColumnHeader')
                data = {'charID': member.characterID,
                 'corporationID': member.corporationID,
                 'label': label,
                 'showinfo': True,
                 'typeID': const.typeCharacter,
                 'itemID': member.characterID,
                 'slimuser': True,
                 sort_key: member.lastOnline}
                if eve.session.corprole & const.corpRoleDirector > 0:
                    data['logonDateTime'] = member.logonDateTime
                    data['logoffDateTime'] = member.logoffDateTime
                scrolllist.append(GetFromClass(MemberTracking, data))

        finally:
            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'member_tracking'
            self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist, headers=header, noContentHint=localization.GetByLabel('UI/Common/NoDataAvailable'))
            sm.GetService('loading').StopCycle()

    def OnMemberMenu(self, entry):
        selected = self.sr.scroll.GetSelected()
        if selected:
            return StartMenuService().CharacterMenu([ each.charID for each in selected if hasattr(each, 'charID') ])
        return []


class MemberTracking(User):
    __guid__ = 'listentry.MemberTracking'

    def Startup(self, *args):
        User.Startup(self, *args)
        self.sr.label = self.sr.namelabel
        self.sr.label.maxLines = 1
        self.sr.namelabel.left = const.defaultPadding
        self.sr.picture.state = uiconst.UI_HIDDEN

    def Load(self, node):
        User.Load(self, node)
        sublevel = node.sublevel or 0
        offset = sublevel * 16
        labelLeft = const.defaultPadding + offset
        self.sr.label.left = self.sr.namelabel.left = labelLeft

    def GetHeight(self, *args):
        node, width = args
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 6
        return node.height

    def GetMenu(self):
        m = User.GetMenu(self)
        return m
