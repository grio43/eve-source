#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_auditing.py
import string
import blue
import localization
import uthread
from carbon.common.script.util.format import FmtDate, GetTimeParts
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.datepicker import DatePicker
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.util import searchOld
from eve.common.lib import appConst as const
from evecorporation.roles import iter_role_names
from localization import GetByLabel

class CorpAuditing(Container):
    auditorMessageID = 60180
    is_loaded = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.notext = None
        self.fromDatePicker = None
        self.toDatePicker = None
        self.sr.mostRecentItem = None
        self.sr.oldestItem = None
        self.sr.memberID = None

    def Load(self, panel_id, *args):
        if self.is_loaded:
            return
        self.is_loaded = True
        self.topCont = ContainerAutoSize(name='topCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(0, 32, 0, 0))
        self.ConstructBackForwardButtons()
        filterCont = FlowContainer(name='filterCont', parent=self.topCont, contentSpacing=(16, 24), align=uiconst.TOTOP)
        nowSecs = blue.os.GetWallclockTime()
        year, month, wd, day, hour, min, sec, ms = GetTimeParts(nowSecs + const.DAY)
        now = [year, month, day]
        year, month, wd, day, hour, min, sec, ms = GetTimeParts(nowSecs - const.WEEK + const.DAY)
        lastWeek = [year, month, day]
        self.fromDatePicker = DatePicker(name='datepicker', parent=filterCont, align=uiconst.NOALIGN, width=256)
        self.fromDatePicker.Startup(lastWeek, False, 4, None, None)
        self.toDatePicker = DatePicker(name='datepicker', parent=filterCont, align=uiconst.NOALIGN, width=256)
        self.toDatePicker.Startup(now, False, 4, None, None)
        memberIDs = sm.GetService('corp').GetMemberIDs()
        if len(memberIDs) < 24:
            memberlist = []
            cfg.eveowners.Prime(memberIDs)
            for charID in memberIDs:
                memberlist.append([cfg.eveowners.Get(charID).name, charID])

            self.memberCombo = Combo(label=GetByLabel('UI/Wallet/WalletWindow/Member'), parent=filterCont, align=uiconst.NOALIGN, width=100, options=memberlist, name='memberID', select=settings.user.ui.Get('memberID', None), callback=self.OnComboChange)
        else:
            self.searchMemberEdit = SingleLineEditText(name='searchMember', parent=filterCont, width=92, align=uiconst.NOALIGN, maxLength=37, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/SearcForMember'), isCharacterField=True)
            self.searchMemberEdit.OnReturn = self.SearchMember
        self.sr.scroll = eveScroll.Scroll(name='auditing', parent=self, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.ShowJournal()

    def ConstructBackForwardButtons(self):
        topRightCont = ContainerAutoSize(parent=self.topCont, align=uiconst.TORIGHT)
        buttonCont = ContainerAutoSize(parent=topRightCont, align=uiconst.TOPRIGHT, height=Button.default_height)
        self.sr.fwdBtn = Button(parent=buttonCont, texturePath='res:/UI/Texture/icons/77_32_41.png', iconSize=20, align=uiconst.TORIGHT, func=self.Browse, args=1, hint=localization.GetByLabel('UI/Browser/Forward'))
        self.sr.backBtn = Button(parent=buttonCont, texturePath='res:/UI/Texture/icons/77_32_42.png', iconSize=20, align=uiconst.TORIGHT, func=self.Browse, args=-1, hint=localization.GetByLabel('UI/Browser/Back'), padRight=4)

    def Browse(self, backforth, *args):
        self.ShowJournal(backforth)

    def OnComboChange(self, entry, header, value, *args):
        uthread.new(self.ShowJournal)

    def OnReturn(self, *args):
        uthread.new(self.ShowJournal)

    def SearchMember(self, *args):
        uthread.new(self.ShowJournal)

    def ParseDatePart(self, dateString):
        __dateseptbl = string.maketrans('/-. ', '----')
        date = string.translate(dateString, __dateseptbl)
        dp = date.split('-', 2)
        month = {1: localization.GetByLabel('UI/Common/Months/January'),
         2: localization.GetByLabel('UI/Common/Months/February'),
         3: localization.GetByLabel('UI/Common/Months/March'),
         4: localization.GetByLabel('UI/Common/Months/April'),
         5: localization.GetByLabel('UI/Common/Months/May'),
         6: localization.GetByLabel('UI/Common/Months/June'),
         7: localization.GetByLabel('UI/Common/Months/July'),
         8: localization.GetByLabel('UI/Common/Months/August'),
         9: localization.GetByLabel('UI/Common/Months/September'),
         10: localization.GetByLabel('UI/Common/Months/October'),
         11: localization.GetByLabel('UI/Common/Months/November'),
         12: localization.GetByLabel('UI/Common/Months/December')}
        return '%s %s, %s' % (month[int(dp[1])], int(dp[2]), int(dp[0]))

    def ParseDate(self, dateString):
        date = None
        if not dateString or len(str(dateString)) == 0:
            return
        if ' ' in dateString:
            d, t = dateString.split(' ')
            date = self.ParseDatePart(d)
            date += ' ' + t
        else:
            date = self.ParseDatePart(dateString)
        return "'%s'" % date

    def ShowJournal(self, browse = None):
        if self.sr.notext:
            self.sr.scroll.ShowHint(None)
        if eve.session.corprole & const.corpRoleAuditor != const.corpRoleAuditor:
            self.sr.notext = 1
            self.sr.scroll.Load(contentList=[])
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/AuditorRoleRequired', auditorMessageID=self.auditorMessageID))
            return
        memberIDs = sm.GetService('corp').GetMemberIDs()
        if len(memberIDs) < 24:
            memberID = self.memberCombo.GetValue()
        else:
            string = self.searchMemberEdit.GetValue()
            if not string:
                eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/HaveToFindMember')})
                uicore.registry.SetFocus(self.searchMemberEdit)
                return
            memberID = searchOld.Search(string.lower(), const.groupCharacter, filterCorpID=eve.session.corpid, searchWndName='corpMemberAuditingJournalSearch')
            if memberID:
                self.searchMemberEdit.SetValue(cfg.eveowners.Get(memberID).name)
        if memberID is None:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/HaveToFindMember')})
            return
        sm.GetService('loading').Cycle('Loading')
        fromDate = self.fromDatePicker.GetValue()
        toDate = self.toDatePicker.GetValue()
        if fromDate == toDate:
            toDate = toDate + const.DAY
        if browse is not None:
            interval = toDate - fromDate
            if browse == 1:
                toDate = toDate + interval
                fromDate = fromDate + interval
            else:
                toDate = toDate - interval
                fromDate = fromDate - interval
        year, month, wd, day, hour, min, sec, ms = GetTimeParts(fromDate)
        self.fromDatePicker.ycombo.SetValue(year)
        self.fromDatePicker.mcombo.SetValue(month)
        self.fromDatePicker.dcombo.SetValue(day)
        year, month, wd, day, hour, min, sec, ms = GetTimeParts(toDate)
        self.toDatePicker.ycombo.SetValue(year)
        self.toDatePicker.mcombo.SetValue(month)
        self.toDatePicker.dcombo.SetValue(day)
        scrolllist = []
        rowsPerPage = 10
        logItemEventRows, crpRoleHistroyRows = sm.RemoteSvc('corpmgr').AuditMember(memberID, fromDate, toDate, rowsPerPage)
        logItems = []
        for row in logItemEventRows:
            logItems.append(row)

        roleItems = []
        for row in crpRoleHistroyRows:
            roleItems.append(row)

        logItems.sort(lambda x, y: cmp(y.eventDateTime, x.eventDateTime))
        roleItems.sort(lambda x, y: cmp(y.changeTime, x.changeTime))
        roles = {roleID:roleName for roleID, roleName in iter_role_names()}
        self.sr.mostRecentItem = None
        self.sr.oldestItem = None
        ix = 0
        if 0 == len(logItems) and 0 == len(roleItems):
            self.sr.mostRecentItem = toDate
            self.sr.oldestItem = fromDate
        while len(logItems) or len(roleItems):
            ix += 1
            if ix > rowsPerPage:
                break
            logItem = None
            roleItem = None
            if len(logItems):
                logItem = logItems[0]
            if len(roleItems):
                roleItem = roleItems[0]
            if logItem is not None and roleItem is not None:
                if logItem.eventDateTime > roleItem.changeTime:
                    roleItem = None
                else:
                    logItem = None
            time = ''
            action = ''
            if logItem is not None:
                del logItems[0]
                time = FmtDate(logItem.eventDateTime, 'ss')
                if self.sr.mostRecentItem is None:
                    self.sr.mostRecentItem = logItem.eventDateTime
                if self.sr.oldestItem is None:
                    self.sr.oldestItem = logItem.eventDateTime
                if self.sr.oldestItem > logItem.eventDateTime:
                    self.sr.oldestItem = logItem.eventDateTime
                if self.sr.mostRecentItem < logItem.eventDateTime:
                    self.sr.mostRecentItem = logItem.eventDateTime
                corpName = cfg.eveowners.Get(logItem.corporationID).name if logItem.corporationID else ''
                if logItem.eventTypeID == 12:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/CreatedCorporation', corpName=corpName)
                elif logItem.eventTypeID == 13:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/DeletedCorporation', corpName=corpName)
                elif logItem.eventTypeID == 14:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/LeftCorporation', corpName=corpName)
                elif logItem.eventTypeID == 15:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/AppliedForMembershipOfCorporation', corpName=corpName)
                elif logItem.eventTypeID == 16:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/BecameCEOOfCorporation', corpName=corpName)
                elif logItem.eventTypeID == 17:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/LeftCEOPositionOfCorporation', corpName=corpName)
                elif logItem.eventTypeID == 44:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/JoinedCorporation', corpName=corpName)
                else:
                    action = 'logItem'
            if roleItem is not None:
                del roleItems[0]
                time = FmtDate(roleItem.changeTime, 'ss')
                if self.sr.mostRecentItem is None:
                    self.sr.mostRecentItem = roleItem.changeTime
                if self.sr.oldestItem is None:
                    self.sr.oldestItem = roleItem.changeTime
                if self.sr.oldestItem > roleItem.changeTime:
                    self.sr.oldestItem = roleItem.changeTime
                if self.sr.mostRecentItem < roleItem.changeTime:
                    self.sr.mostRecentItem = roleItem.changeTime
                rolesBefore = []
                rolesAfter = []
                for roleID in roles.iterkeys():
                    if roleItem.oldRoles & roleID == roleID:
                        rolesBefore.append(roleID)
                    if roleItem.newRoles & roleID == roleID:
                        rolesAfter.append(roleID)

                added = []
                removed = []
                kept = []
                for roleID in roles.iterkeys():
                    if roleID in rolesBefore:
                        if roleID in rolesAfter:
                            kept.append(roleID)
                        else:
                            removed.append(roleID)
                    elif roleID in rolesAfter:
                        added.append(roleID)

                issuerID = roleItem.issuerID
                if issuerID == -1:
                    issuerID = const.ownerCONCORD
                actionOwner = cfg.eveowners.GetIfExists(issuerID)
                addedRoleNames = [ roles[roleID] for roleID in added ]
                removedRoleNames = [ roles[roleID] for roleID in removed ]
                keptRoleNames = [ roles[roleID] for roleID in kept ]
                cerberizedAddedRoleNames = localization.formatters.FormatGenericList(addedRoleNames)
                cerberizedRemovedRoleNames = localization.formatters.FormatGenericList(removedRoleNames)
                cerberizedKeptRoleNames = localization.formatters.FormatGenericList(keptRoleNames)
                rolesAddedLabel = ''
                rolesRemovedLabel = ''
                rolesKeptLabel = ''
                if len(addedRoleNames) > 0:
                    rolesAddedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/RolesAdded', listOfAddedRoles=cerberizedAddedRoleNames)
                if len(removedRoleNames) > 0:
                    rolesRemovedLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/RolesRemoved', listOfRemovedRoles=cerberizedRemovedRoleNames)
                if len(keptRoleNames) > 0:
                    rolesKeptLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/RolesKept', listOfKeptRoles=cerberizedKeptRoleNames)
                summaryLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/SummaryOfChanges', firstListMessage=rolesAddedLabel, secondListMessage=rolesRemovedLabel, thirdListMessage=rolesKeptLabel)
                unknownIssuer = localization.GetByLabel('UI/Common/Unknown')
                corpName = cfg.eveowners.Get(roleItem.corporationID).name
                if actionOwner is None:
                    if roleItem.grantable:
                        action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/UnknownCharChangedGrantableRoles', charName=unknownIssuer, changedChar=roleItem.charID, corpName=corpName, whatChanged=summaryLabel)
                    else:
                        action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/UnknownCharChangedRoles', charName=unknownIssuer, changedChar=roleItem.charID, corpName=corpName, whatChanged=summaryLabel)
                elif roleItem.grantable:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/KnownCharChangedGrantableRoles', changingChar=issuerID, changedChar=roleItem.charID, corpName=corpName, whatChanged=summaryLabel)
                else:
                    action = localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/KnownCharChangedRoles', changingChar=issuerID, changedChar=roleItem.charID, corpName=corpName, whatChanged=summaryLabel)
            scrolllist.append(GetFromClass(Text, {'text': '%s<t>%s' % (time, action),
             'line': 1,
             'canOpen': 'Action'}))

        self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Date'), localization.GetByLabel('UI/Common/Action')], noContentHint=localization.GetByLabel('UI/Common/NoDataAvailable'))
        if not len(scrolllist):
            self.sr.notext = 1
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Auditing/NoAuditingRecordsFound'))
        else:
            self.sr.notext = 0
        self.sr.fwdBtn.state = uiconst.UI_NORMAL
        self.sr.backBtn.state = uiconst.UI_NORMAL
        sm.GetService('loading').StopCycle()
