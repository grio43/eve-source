#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\evemailingListConfig.py
import math
import utillib
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.neocom.evemail import MailWindow
from eve.client.script.ui.shared.userentry import UserSimple
from eve.common.lib import appConst as const
import evetypes
import carbonui.const as uiconst
import uthread
import localization
from eve.client.script.ui.util import searchOld
from eve.client.script.ui.util.linkUtil import GetItemIDFromTextLink
from eveexceptions import UserError
from eveservices.menu import GetMenuService
PAD = 6
SPACING = 22
EDITHEIGHT = 32
FIELDWIDTH = 70
FIELDSPACE = 10
BUTTONTOP = 2
FILTER_ALL = 0
FILTER_MEMBERS = 1
FILTER_MUTED = 2
FILTER_OPERATORS = 3
FILTER_BYNAME = 4
ACTION_SETMEMBER = 0
ACTION_SETMUTED = 1
ACTION_SETOPERATOR = 2
ACTION_KICK = 3
NUMPERPAGE = 50
ALLOWED_GROUP_IDS = [const.groupCharacter, const.groupCorporation, const.groupAlliance]

class MaillistSetupWindow(Window):
    __guid__ = 'form.MaillistSetupWindow'
    default_iconNum = MailWindow.default_iconNum

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.mailingListID = attributes.mailingListID
        self.mlsvc = sm.GetService('mailinglists')
        self.groupName = self.mlsvc.GetDisplayName(self.mailingListID)
        self.SetMinSize([350, 460])
        self.SetCaption(localization.GetByLabel('UI/EVEMail/MailingLists/Caption', mailinglistName=self.groupName))
        self.welcomeText = None
        self.sr.tabs = TabGroup(name='tabs', parent=self.content)
        self.sr.membersPanel = Container(name='membersPanel', parent=self.content, align=uiconst.TOALL)
        self.sr.accessPanel = Container(name='accessPanel', parent=self.content, align=uiconst.TOALL)
        self.sr.welcomePanel = Container(name='welcomePanel', parent=self.content, align=uiconst.TOALL)
        tabs = [[localization.GetByLabel('UI/EVEMail/MailingLists/MembersTab'),
          self.sr.membersPanel,
          self,
          'members'], [localization.GetByLabel('UI/EVEMail/MailingLists/AccessTab'),
          self.sr.accessPanel,
          self,
          'access'], [localization.GetByLabel('UI/EVEMail/MailingLists/WelcomeMailTab'),
          self.sr.welcomePanel,
          self,
          'welcome']]
        self.StartupMembersPanel()
        self.StartupAccessPanel()
        self.StartupWelcomePanel()
        self.sr.tabs.Startup(tabs, 'mailinglistSetup_tabs', autoselecttab=1)

    def StartupMembersPanel(self):
        membersPanel = self.sr.membersPanel
        comboOptions = [(localization.GetByLabel('UI/Common/All'), FILTER_ALL),
         (localization.GetByLabel('UI/EVEMail/MailingLists/NormalMembers'), FILTER_MEMBERS),
         (localization.GetByLabel('UI/EVEMail/MailingLists/MutedMembers'), FILTER_MUTED),
         (localization.GetByLabel('UI/Chat/Operators'), FILTER_OPERATORS),
         (localization.GetByLabel('UI/EVEMail/MailingLists/SearchByName'), FILTER_BYNAME)]
        topCont = Container(name='topCont', parent=membersPanel, align=uiconst.TOTOP, pos=(0, 10, 0, 28))
        self.sr.membersPanel.showMembersCombo = Combo(label=localization.GetByLabel('UI/EVEMail/MailingLists/ShowLabel'), parent=topCont, options=comboOptions, name='showMembersCombo', callback=self.OnShowMembersComboChanged, width=100, align=uiconst.TOPLEFT)
        self.sr.membersPanel.searchEdit = SingleLineEditText(label=localization.GetByLabel('UI/PeopleAndPlaces/SearchString'), name='searchEdit', parent=topCont, align=uiconst.TOPLEFT, pos=(115,
         0,
         80,
         EDITHEIGHT), state=uiconst.UI_HIDDEN, isCharCorpOrAllianceField=True)
        self.sr.membersPanel.searchEdit.ShowClearButton(showOnLetterCount=3)
        self.sr.membersPanel.searchEdit.OnReturn = self.UpdateMembersScroll
        self.sr.membersPanel.searchButton = Button(parent=topCont, label=localization.GetByLabel('UI/Common/Buttons/Search'), left=200, func=self.UpdateMembersScroll, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        pagingCont = LayoutGrid(parent=ContainerAutoSize(parent=topCont, align=uiconst.TORIGHT), align=uiconst.CENTER, columns=3, cellSpacing=(4, 0))
        self.sr.pageBackBtn = Button(parent=pagingCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/Icons/23_64_1.png', iconSize=24, hint=localization.GetByLabel('UI/Common/Previous'), func=lambda : self.ChangeMembersPage(-1), args=())
        self.sr.pageCount = eveLabel.EveLabelMedium(parent=pagingCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, text='')
        self.sr.pageFwdBtn = Button(parent=pagingCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/Icons/23_64_2.png', iconSize=24, hint=localization.GetByLabel('UI/Common/Next'), func=lambda : self.ChangeMembersPage(1), args=())
        bottomCont = Container(parent=membersPanel, align=uiconst.TOBOTTOM, pos=(0,
         0,
         100,
         EDITHEIGHT), padding=(0,
         3 * PAD,
         0,
         PAD), state=uiconst.UI_PICKCHILDREN)
        comboOptions = [(localization.GetByLabel('UI/EVEMail/MailingLists/SetRoleMember'), ACTION_SETMEMBER),
         (localization.GetByLabel('UI/EVEMail/MailingLists/SetRoleMuted'), ACTION_SETMUTED),
         (localization.GetByLabel('UI/EVEMail/MailingLists/SetRoleOperator'), ACTION_SETOPERATOR),
         (localization.GetByLabel('UI/EVEMail/MailingLists/Kick'), ACTION_KICK)]
        self.sr.membersPanel.actionCombo = Combo(label=localization.GetByLabel('UI/EVEMail/MailingLists/ApplyToSelected'), parent=bottomCont, options=comboOptions, name='showMembersCombo', width=150, align=uiconst.TOPLEFT)
        self.sr.membersPanel.ApplyBtn = Button(parent=bottomCont, label=localization.GetByLabel('UI/Generic/Apply'), func=self.ApplyActionToMembers, align=uiconst.TOPRIGHT)
        self.sr.membersPanel.ApplyBtn.Disable()
        self.roles = {const.mailingListMemberDefault: localization.GetByLabel('UI/EVEMail/MailingLists/Member'),
         const.mailingListMemberMuted: localization.GetByLabel('UI/EVEMail/MailingLists/MutedMember'),
         const.mailingListMemberOperator: localization.GetByLabel('UI/EVEMail/MailingLists/Operator'),
         const.mailingListMemberOwner: localization.GetByLabel('UI/EVEMail/MailingLists/Owner')}
        self.sr.membersPanel.scroll = eveScroll.Scroll(parent=membersPanel, name='membersScroll', padTop=PAD)
        self.sr.membersPanel.scroll.sr.id = 'membersPanelScroll'
        self.sr.membersPanel.scroll.OnSelectionChange = self.OnMembersScrollSelectionChange

    def OnMembersScrollSelectionChange(self, *args):
        if len(self.sr.membersPanel.scroll.GetSelected()) > 0:
            self.sr.membersPanel.ApplyBtn.Enable()
        else:
            self.sr.membersPanel.ApplyBtn.Disable()

    def OnShowMembersComboChanged(self, comboBox, selString, selVal):
        if selVal == FILTER_BYNAME:
            self.sr.membersPanel.searchEdit.state = uiconst.UI_NORMAL
            self.sr.membersPanel.searchButton.state = uiconst.UI_NORMAL
        else:
            self.sr.membersPanel.searchEdit.state = uiconst.UI_HIDDEN
            self.sr.membersPanel.searchButton.state = uiconst.UI_HIDDEN
            self.UpdateMembersScroll()

    def ChangeMembersPage(self, pageChange, *args):
        self.currPage += pageChange
        if self.numPages <= 1:
            self.sr.pageBackBtn.Disable()
            self.sr.pageFwdBtn.Disable()
        elif self.currPage == 0:
            self.sr.pageBackBtn.Disable()
            self.sr.pageFwdBtn.Enable()
        elif self.currPage == self.numPages - 1:
            self.sr.pageBackBtn.Enable()
            self.sr.pageFwdBtn.Disable()
        else:
            self.sr.pageBackBtn.Enable()
            self.sr.pageFwdBtn.Enable()
        self.PopulateMembersScroll()
        self.sr.pageCount.text = '%s / %s' % (self.currPage + 1, self.numPages)

    def UpdateMembersScroll(self, *args):
        self.members = self.mlsvc.GetMembers(self.mailingListID)
        if not self or self.destroyed:
            return
        self.FilterMembers()
        self.SortMembers()
        self.PageMembers()
        self.PopulateMembersScroll()

    def FilterMembers(self, *args):
        filter = self.sr.membersPanel.showMembersCombo.GetValue()
        self.filteredMembers = []
        if filter == FILTER_ALL:
            for memberID, accessLevel in self.members.iteritems():
                self.filteredMembers.append(utillib.KeyVal(memberID=memberID, accessLevel=accessLevel))

        elif filter == FILTER_MEMBERS:
            for memberID, accessLevel in self.members.iteritems():
                if accessLevel == const.mailingListMemberDefault:
                    self.filteredMembers.append(utillib.KeyVal(memberID=memberID, accessLevel=accessLevel))

        elif filter == FILTER_MUTED:
            for memberID, accessLevel in self.members.iteritems():
                if accessLevel == const.mailingListMemberMuted:
                    self.filteredMembers.append(utillib.KeyVal(memberID=memberID, accessLevel=accessLevel))

        elif filter == FILTER_OPERATORS:
            for memberID, accessLevel in self.members.iteritems():
                if accessLevel == const.mailingListMemberOperator or accessLevel == const.mailingListMemberOwner:
                    self.filteredMembers.append(utillib.KeyVal(memberID=memberID, accessLevel=accessLevel))

        elif filter == FILTER_BYNAME:
            searchStr = self.sr.membersPanel.searchEdit.GetValue().strip().lower()
            for memberID, accessLevel in self.members.iteritems():
                name = cfg.eveowners.Get(memberID).name.strip().lower()
                if name.startswith(searchStr):
                    self.filteredMembers.append(utillib.KeyVal(memberID=memberID, accessLevel=accessLevel))

    def SortMembers(self):
        self.filteredMembers.sort(cmp=self._CompareMembers)

    def _CompareMembers(self, x, y):
        nameX = cfg.eveowners.Get(x.memberID).name.lower()
        nameY = cfg.eveowners.Get(y.memberID).name.lower()
        if nameX < nameY:
            return -1
        elif nameX == nameY:
            return 0
        else:
            return 1

    def PageMembers(self):
        self.currPage = 0
        self.pagedMembers = []
        self.numPages = int(math.ceil(float(len(self.filteredMembers)) / NUMPERPAGE))
        for i in range(self.numPages):
            self.pagedMembers.append(self.filteredMembers[i * NUMPERPAGE:(i + 1) * NUMPERPAGE])

        if self.numPages > 1:
            pages = []
            for i in range(self.numPages):
                pages.append((str(i + 1), i))

        self.ChangeMembersPage(0)

    def PopulateMembersScroll(self, *args):
        scrolllist = []
        self.checkedMembers = []
        if len(self.pagedMembers) == 0:
            page = []
        else:
            page = self.pagedMembers[self.currPage]
        ownerIDs = {m.memberID for m in page}
        cfg.eveowners.Prime(ownerIDs)
        for m in page:
            memberID = m.memberID
            memberInfo = cfg.eveowners.Get(memberID)
            label = '%s<t>%s' % (memberInfo.name, self.roles[m.accessLevel])
            entry = GetFromClass(UserSimple, {'charID': memberID,
             'info': memberInfo,
             'label': label,
             'ownerID': memberID})
            scrolllist.append(entry)

        self.sr.membersPanel.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Generic/NamePerson'), localization.GetByLabel('UI/EVEMail/MailingLists/Role')], customColumnWidths=True, noContentHint=localization.GetByLabel('UI/EVEMail/MailingLists/NoMembersFound'))
        self.sr.membersPanel.ApplyBtn.Disable()

    @staticmethod
    def GetCharMenu(entry, *args):
        return GetMenuService().CharacterMenu(entry.sr.node.charID)

    def ApplyActionToMembers(self, *args):
        action = self.sr.membersPanel.actionCombo.GetValue()
        selectedMembers = self._GetSelectedMembers()
        doClose = False
        if action == ACTION_SETMEMBER:
            if session.charid in selectedMembers:
                ret = eve.Message('MailingListMemberSelfConfirm', {}, uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    return
                doClose = True
            self.mlsvc.SetMembersClear(self.mailingListID, selectedMembers)
        elif action == ACTION_SETMUTED:
            if session.charid in selectedMembers:
                ret = eve.Message('MailingListMuteSelfConfirm', {}, uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    return
                doClose = True
            self.mlsvc.SetMembersMuted(self.mailingListID, selectedMembers)
        elif action == ACTION_SETOPERATOR:
            self.mlsvc.SetMembersOperator(self.mailingListID, selectedMembers)
        elif action == ACTION_KICK:
            self.mlsvc.KickMembers(self.mailingListID, selectedMembers)
            self.UpdateAccessScrollData()
        if doClose:
            self.Close()
        else:
            self.UpdateMembersScroll()

    def _GetSelectedMembers(self):
        selected = []
        for s in self.sr.membersPanel.scroll.GetSelected():
            selected.append(s.ownerID)

        return selected

    def ClearAccessForSelected(self, *args):
        selected = self.sr.blockedScroll.GetSelected() + self.sr.allowedScroll.GetSelected()
        if selected:
            for e in selected:
                self.mlsvc.ClearEntityAccess(self.mailingListID, e.ownerID)

            self.UpdateAccessScrollData()
        else:
            raise UserError('PICKERRORNOTIFY', {'num': 1})

    def AddToBlocked(self, *args):
        self._ModifyAccess(const.mailingListBlocked)

    def AddToAllowed(self, *args):
        self._ModifyAccess(const.mailingListAllowed)

    def _ModifyAccess(self, newAccess):
        ownerID = self.Search(self.sr.blockEdit.GetValue())
        if ownerID is not None:
            self.mlsvc.SetEntityAccess(self.mailingListID, ownerID, newAccess)
            self.UpdateAccessScrollData()

    def OnDropInBlocked(self, dragObj, nodes):
        self._UpdateAccessOnDropNodes(nodes, const.mailingListBlocked)

    def OnDropInAllowed(self, dragObj, nodes):
        self._UpdateAccessOnDropNodes(nodes, const.mailingListAllowed)

    def _UpdateAccessOnDropNodes(self, nodes, newAccess):
        validTypeIDs = evetypes.GetTypeIDsByGroups(ALLOWED_GROUP_IDS)
        ownerIDs = set()
        for node in nodes:
            if (node.charID or node.itemID) and node.__guid__ in AllUserEntries():
                ownerIDs.add(node.charID or node.itemID)
            elif node.itemID and node.typeID and node.typeID in validTypeIDs:
                ownerIDs.add(node.itemID)
            elif getattr(node, '__guid__', None) == 'TextLink':
                itemID = GetItemIDFromTextLink(node, validTypeIDs)
                if itemID:
                    ownerIDs.add(itemID)

        if not ownerIDs:
            return
        cfg.eveowners.Prime(ownerIDs)
        accessByEntityID = {x:newAccess for x in ownerIDs if cfg.eveowners.Get(x).groupID in ALLOWED_GROUP_IDS}
        if not accessByEntityID:
            return
        self.mlsvc.SetEntitiesAccess(self.mailingListID, accessByEntityID)
        self.UpdateAccessScrollData()

    def UpdateBlockedScroll(self):
        self.sr.blockedScroll.Load(contentList=self.scrolllist[const.mailingListBlocked], headers=[localization.GetByLabel('UI/Generic/NamePerson'), localization.GetByLabel('UI/Common/Type')], customColumnWidths=True)

    def UpdateAllowedScroll(self):
        self.sr.allowedScroll.Load(contentList=self.scrolllist[const.mailingListAllowed], headers=[localization.GetByLabel('UI/Generic/NamePerson'), localization.GetByLabel('UI/Common/Type')], customColumnWidths=True)

    def StartupAccessPanel(self):
        accessPanel = self.sr.accessPanel
        topCont = Container(name='topCont', parent=accessPanel, align=uiconst.TOTOP, height=130)
        comboOptions = [(localization.GetByLabel('UI/EVEMail/MailingLists/PrivateAccess'), const.mailingListBlocked), (localization.GetByLabel('UI/EVEMail/MailingLists/PublicAccess'), const.mailingListAllowed)]
        self.sr.accessPanel.defaultAccessCombo = Combo(label=localization.GetByLabel('UI/EVEMail/MailingLists/DefaultAccessLabel'), parent=topCont, options=comboOptions, name='subcriptionAccessCombo', select=self.mlsvc.GetSettings(self.mailingListID).defaultAccess, pos=(0,
         SPACING,
         0,
         0), width=200)
        Button(parent=topCont, label=localization.GetByLabel('UI/Common/Buttons/Apply'), pos=(0, 41, 0, 0), func=self.ApplySettings, align=uiconst.TOPRIGHT)
        roleComboOptions = [(localization.GetByLabel('UI/EVEMail/MailingLists/Normal'), const.mailingListMemberDefault), (localization.GetByLabel('UI/EVEMail/MailingLists/MutedRole'), const.mailingListMemberMuted)]
        self.sr.accessPanel.defaultRoleCombo = Combo(label=localization.GetByLabel('UI/EVEMail/MailingLists/DefaultMemberRole'), parent=topCont, options=roleComboOptions, name='roleCombo', select=self.mlsvc.GetSettings(self.mailingListID).defaultMemberAccess, pos=(0,
         self.sr.accessPanel.defaultAccessCombo.top + self.sr.accessPanel.defaultAccessCombo.height + SPACING,
         0,
         0), width=200)
        Line(parent=topCont, align=uiconst.TOBOTTOM)
        addToBlockCont = Container(name='AddToBlockCont', parent=accessPanel, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0, 0, 0, 22), padding=(0, 20, 0, 0))
        self.sr.blockEdit = SingleLineEditText(label=localization.GetByLabel('UI/EVEMail/MailingLists/EntitySearchLabel'), name='AddToBlockEdit', parent=addToBlockCont, align=uiconst.TOPLEFT, pos=(0, 0, 100, 0), isCharCorpOrAllianceField=True)
        self.sr.blockEdit.ShowClearButton(showOnLetterCount=3)
        b1 = Button(parent=addToBlockCont, label=localization.GetByLabel('UI/EVEMail/MailingLists/Allow'), func=self.AddToAllowed, align=uiconst.CENTERRIGHT)
        Button(parent=addToBlockCont, label=localization.GetByLabel('UI/PeopleAndPlaces/BlockContact'), func=self.AddToBlocked, align=uiconst.CENTERRIGHT, left=b1.width + b1.left + 4)
        self.sr.scrollCont = scrollCont = Container(name='scrollCont', parent=accessPanel, align=uiconst.TOALL)
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/EVEMail/MailingLists/BlockedLabel'), parent=scrollCont, align=uiconst.TOTOP, top=10, state=uiconst.UI_NORMAL)
        self.sr.blockedScroll = eveScroll.Scroll(parent=scrollCont, name='blockedScroll', align=uiconst.TOTOP)
        self.sr.blockedScroll.OnSetFocus = self.BlockedScrollOnSetFocus
        self.sr.blockedScroll.sr.id = 'blockedScroll'
        self.sr.blockedScroll.sr.content.OnDropData = self.OnDropInBlocked
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/EVEMail/MailingLists/AllowedLabel'), parent=scrollCont, align=uiconst.TOTOP, top=10, state=uiconst.UI_NORMAL)
        self.sr.allowedScroll = eveScroll.Scroll(parent=scrollCont, name='allowedScroll', align=uiconst.TOTOP)
        self.sr.allowedScroll.OnSetFocus = self.AllowedScrollOnSetFocus
        self.sr.allowedScroll.sr.id = 'allowedScroll'
        self.sr.allowedScroll.sr.content.OnDropData = self.OnDropInAllowed
        self.UpdateAccessScrollData()
        ButtonGroup(btns=[[localization.GetByLabel('UI/EVEMail/MailingLists/RemoveSelected'),
          self.ClearAccessForSelected,
          None,
          None]], parent=accessPanel, line=False)
        self._OnResize()

    def AllowedScrollOnSetFocus(self):
        self.sr.blockedScroll.DeselectAll()

    def BlockedScrollOnSetFocus(self):
        self.sr.allowedScroll.DeselectAll()

    def UpdateAccessScrollData(self):
        self.scrolllist = {const.mailingListAllowed: [],
         const.mailingListBlocked: []}
        accessList = self.mlsvc.GetSettings(self.mailingListID).access
        cfg.eveowners.Prime(accessList.keys())
        for i, m in enumerate(accessList.iteritems()):
            ownerID, accessLevel = m
            owner = cfg.eveowners.Get(ownerID)
            label = '%s<t>%s' % (owner.name, evetypes.GetGroupNameByGroup(owner.groupID))
            entry = GetFromClass(UserSimple, {'charID': ownerID,
             'info': owner,
             'label': label,
             'ownerID': ownerID})
            self.scrolllist[accessLevel].append(entry)

        self.UpdateAllowedScroll()
        self.UpdateBlockedScroll()

    def ApplySettings(self, *args):
        defaultAccess = self.sr.accessPanel.defaultAccessCombo.GetValue()
        defaultRole = self.sr.accessPanel.defaultRoleCombo.GetValue()
        self.mlsvc.SetDefaultAccess(self.mailingListID, defaultAccess, defaultRole)

    def Search(self, searchStr):
        return searchOld.SearchOwners(searchStr=searchStr, groupIDs=ALLOWED_GROUP_IDS, hideNPC=True, notifyOneMatch=True, searchWndName='AddToBlockSearch')

    def StartupWelcomePanel(self, *args):
        welcomePanel = self.sr.welcomePanel
        self.sr.wekcomeToAllCB = Checkbox(parent=welcomePanel, align=uiconst.TOBOTTOM, padTop=8, text=localization.GetByLabel('UI/EVEMail/MailingLists/SendWelcomeMailToAllCheckbox'), settingsKey='welcomeToAllCB', retval=self.mailingListID, checked=settings.user.ui.Get('welcomeToAllCB_%s' % self.mailingListID, 0), callback=self.OnCheckboxChange)
        self.sr.subjecField = SingleLineEditText(name='subjecField', parent=welcomePanel, align=uiconst.TOTOP, padBottom=8, maxLength=const.mailMaxSubjectSize, label='', hintText=localization.GetByLabel('UI/EVEMail/MailingLists/WelcomeMailSubject'))
        self.sr.welcomeScrollCont = scrollCont = Container(name='scrollCont', parent=welcomePanel, align=uiconst.TOALL)
        self.sr.welcomeEdit = EditPlainText(setvalue='', parent=self.sr.welcomeScrollCont, align=uiconst.TOALL, showattributepanel=1, maxLength=const.mailMaxTaggedBodySize)
        ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/Save'),
          self.SaveWelcomeMail,
          None,
          None]], parent=welcomePanel, padTop=8, idx=0)

    def OnCheckboxChange(self, checkbox, *args):
        value = self.mailingListID or ''
        name = '%s_%s' % (checkbox.name, value)
        settings.user.ui.Set(name, checkbox.checked)

    def UpdateWelcome(self, *args):
        welcomeMail = self.mlsvc.GetWelcomeMail(self.mailingListID)
        if not welcomeMail:
            self.sr.welcomeEdit.SetValue('')
            self.sr.subjecField.SetValue('')
            return
        self.welcomeText = welcomeMail
        mail = welcomeMail[0]
        self.sr.welcomeEdit.SetValue(mail.body)
        self.sr.subjecField.SetValue(mail.title)

    def SaveWelcomeMail(self, *args):
        sendToAll = self.sr.wekcomeToAllCB.GetValue()
        subject = self.sr.subjecField.GetValue()
        body = self.sr.welcomeEdit.GetValue()
        if len(subject) < 1 and len(body) < 1:
            self.mlsvc.ClearWelcomeMail(self.mailingListID)
            return
        if len(subject) < 1:
            raise UserError('NoSubject')
        if sendToAll:
            self.mlsvc.SaveAndSendWelcomeMail(self.mailingListID, subject, body)
        else:
            self.mlsvc.SaveWelcomeMail(self.mailingListID, subject, body)

    def _OnResize(self, *args):
        uthread.new(self.__OnResize)

    def __OnResize(self):
        if self.destroyed or not self.sr.scrollCont:
            return
        aL, aT, aW, aH = self.sr.scrollCont.GetAbsolute()
        newHeight = (aH - 72) / 2
        self.sr.allowedScroll.height = newHeight
        self.sr.blockedScroll.height = newHeight

    def Load(self, key):
        if key == 'members':
            self.UpdateMembersScroll()
        elif key == 'access':
            self.UpdateAllowedScroll()
            self._OnResize()
        elif key == 'welcome':
            if self.welcomeText is None:
                self.UpdateWelcome()
