#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\contactsForm.py
import math
import eveicon
from carbonui import AxisAlignment, uiconst
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.util.various_unsorted import NiceFilter, SortListOfTuples
from carbonui.control.checkbox import Checkbox
from eve.client.script.parklife import states
from eve.client.script.ui.control.entries.space import Space
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.neocom.addressBook import contactsConst
from eve.client.script.ui.shared.neocom.addressBook.contactsConst import TAB_ALLIANCECONTACTS, TAB_CONTACTS, TAB_CORPCONTACTS
from eve.client.script.ui.shared.neocom.addressBook.manageLabels import ManageLabels
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.shared.neocom.evemail import MailLabelEntry
from eve.client.script.ui.shared.stateFlag import FlagIconWithState
from eve.common.lib import appConst as const
import localization
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.common.script.sys import idCheckers
from menu import MenuLabel
from bannedwords.client import bannedwords
CONTACTGROUPID_TO_STATEID = {const.contactHighStanding: states.flagStandingHigh,
 const.contactGoodStanding: states.flagStandingGood,
 const.contactNeutralStanding: states.flagStandingNeutral,
 const.contactBadStanding: states.flagStandingBad,
 const.contactHorribleStanding: states.flagStandingHorrible}

class ContactListGroup(ListGroup):

    def _ConstructIcon(self):
        self.sr.icon = FlagIconWithState(parent=self, pos=(4, 0, 12, 12), state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)

    def _LoadIconState(self):
        flagID = CONTACTGROUPID_TO_STATEID[self.sr.node.groupID]
        self.sr.icon.SetFlagID(flagID)

    def _LoadIconLeft(self):
        self.sr.icon.left = 6

    def _LoadLabelLeft(self):
        self.sr.label.left = 26


class ContactsForm(Container):
    default_contactType = TAB_CONTACTS
    __notifyevents__ = ['OnContactChange',
     'OnUnblockContact',
     'OnNotificationsRefresh',
     'OnMessageChanged',
     'OnMyLabelsChanged',
     'OnEditLabel',
     'OnSetAllianceStanding',
     'OnSetCorpStanding']

    def ApplyAttributes(self, attributes):
        super(ContactsForm, self).ApplyAttributes(attributes)
        self.contactType = attributes.get('contactType', self.default_contactType)
        self.startPos = 0
        self.group = None
        self.isInitialized = False

    def Load(self, *args):
        self.LoadPanel()

    def LoadPanel(self):
        if self.isInitialized:
            return
        self.isInitialized = True
        self.mainCont = Container(name='mainCont', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.ConstructPaginationCont()
        systemStatsCont = DragResizeCont(name='systemStatsCont', settingsID='contactsListSplit1', parent=self.mainCont, align=uiconst.TOLEFT_PROP if self.contactType == TAB_CONTACTS else uiconst.TORIGHT_PROP, minSize=0.1, maxSize=0.5, defaultSize=0.33)
        self.leftCont = Container(name='leftCont', parent=systemStatsCont.mainCont)
        self.ConstructSearchAndLabelsBtn()
        self.ConstructNavigationScroll()
        self.ConstructScroll()
        self.LoadContactsForm()
        sm.RegisterNotify(self)

    def ConstructPaginationCont(self):
        self.paginationCont = ContainerAutoSize(name='paginationCont', parent=self.mainCont, idx=0, align=uiconst.TOBOTTOM, height=24)
        self.contactFwdBtn = ButtonIcon(parent=self.paginationCont, align=uiconst.TORIGHT, width=self.paginationCont.height, state=uiconst.UI_NORMAL, texturePath=eveicon.navigate_forward, iconSize=16, hint=localization.GetByLabel('UI/Common/Next'), func=self.OnFwdBtn)
        self.contactBackBtn = ButtonIcon(parent=self.paginationCont, align=uiconst.TORIGHT, width=self.paginationCont.height, state=uiconst.UI_NORMAL, texturePath=eveicon.navigate_back, iconSize=16, hint=localization.GetByLabel('UI/Common/Previous'), func=self.OnBackBtn)
        self.pageCount = eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=self.paginationCont, align=uiconst.TORIGHT, padRight=4), state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)

    def OnFwdBtn(self):
        self.BrowseContacts(1)

    def OnBackBtn(self):
        self.BrowseContacts(-1)

    def ConstructScroll(self):
        self.scroll = eveScroll.Scroll(name='rightScroll', parent=self.mainCont, padding=(0, 8, 0, 0))
        self.scroll.sr.ignoreTabTrimming = 1
        self.scroll.multiSelect = 1
        self.scroll.sr.content.OnDropData = self.OnContactDropData
        self.scroll.sr.id = self.contactType

    def ConstructNavigationScroll(self):
        self.leftScroll = eveScroll.Scroll(name='leftScroll', parent=self.leftCont)
        self.leftScroll.multiSelect = 0
        self.leftScroll.sr.content.OnDropData = self.OnContactDropData

    def ConstructSearchAndLabelsBtn(self):
        topCont = FlowContainer(name='topCont', align=uiconst.TOTOP, parent=self.mainCont, height=HEIGHT_NORMAL, contentAlignment=AxisAlignment.END, contentSpacing=(16, 8))
        checkboxCont = ContainerAutoSize(name='checkboxCon', parent=topCont, height=HEIGHT_NORMAL)
        self.onlinecheck = Checkbox(text=localization.GetByLabel('UI/PeopleAndPlaces/OnlineOnly'), parent=checkboxCont, settingsKey='onlinebuddyonly', checked=settings.user.ui.Get('onlinebuddyonly', 0), callback=self.CheckBoxChange, align=uiconst.TORIGHT, padTop=4, wrapLabel=False)
        self.quickFilter = QuickFilterEdit(parent=topCont, isCharCorpOrAllianceField=True, callback=self.LoadContactsForm, width=120)

    def _OnClose(self):
        sm.UnregisterNotify(self)

    def LoadLeftSide(self):
        scrolllist = self.GetStaticLabelsGroups()
        scrolllist.insert(1, GetFromClass(Space, {'height': 16}))
        scrolllist.append(GetFromClass(Space, {'height': 16}))
        scrolllist.append(GetFromClass(LabelListGroup, {'GetSubContent': self.GetLabelsSubContent,
         'MenuFunction': self.LabelGroupMenu,
         'label': localization.GetByLabel('UI/PeopleAndPlaces/Labels'),
         'cleanLabel': localization.GetByLabel('UI/PeopleAndPlaces/Labels'),
         'id': ('contacts', 'Labels', localization.GetByLabel('UI/PeopleAndPlaces/Labels')),
         'state': 'locked',
         'BlockOpenWindow': 1,
         'showicon': eveicon.tag,
         'showlen': 0,
         'groupName': 'labels',
         'groupItems': [],
         'updateOnToggle': 0,
         'manage_labels_callback': self.ManageLabels}))
        self.leftScroll.Load(contentList=scrolllist)
        lastViewedID = self._GetLastViewedID()
        for entry in self.leftScroll.GetNodes():
            groupID = entry.groupID
            if groupID is None:
                continue
            if groupID == lastViewedID:
                panel = entry.panel
                if panel is not None:
                    panel.OnClick()
                    return

        if len(self.leftScroll.GetNodes()) > 0:
            entry = self.leftScroll.GetNodes()[0]
            panel = entry.panel
            if panel is not None:
                panel.OnClick()

    def GetStandingNameShort(self, standing):
        if standing == const.contactHighStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingExcellent')
        if standing == const.contactGoodStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingGood')
        if standing == const.contactNeutralStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingNeutral')
        if standing == const.contactBadStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingBad')
        if standing == const.contactHorribleStanding:
            return localization.GetByLabel('UI/PeopleAndPlaces/StandingTerrible')

    def GetLabelsSubContent(self, items):
        scrolllist = []
        myLabels = sm.GetService('addressbook').GetContactLabels(self.contactType)
        for each in myLabels.itervalues():
            if getattr(each, 'static', 0):
                continue
            entryItem = self.CreateLabelEntry(each)
            scrolllist.append((each.name.lower(), entryItem))

        scrolllist = SortListOfTuples(scrolllist)
        scrolllist.insert(0, GetFromClass(MailLabelEntry, {'cleanLabel': localization.GetByLabel('UI/PeopleAndPlaces/NoLabel'),
         'label': '%s [%s]' % (localization.GetByLabel('UI/PeopleAndPlaces/NoLabel'), self.GetContactsLabelCount(-1)),
         'sublevel': 1,
         'currentView': -1,
         'OnClick': self.LoadGroupFromEntry,
         'groupID': -1}))
        return scrolllist

    def CreateLabelEntry(self, labelEntry):
        count = self.GetContactsLabelCount(labelEntry.labelID)
        return GetFromClass(MailLabelEntry, {'cleanLabel': labelEntry.name,
         'label': '%s [%s]' % (labelEntry.name, count),
         'sublevel': 1,
         'currentView': labelEntry.labelID,
         'OnClick': self.LoadGroupFromEntry,
         'GetMenu': self.GetLabelMenu,
         'OnDropData': self.OnGroupDropData,
         'groupID': labelEntry.labelID})

    def GetLabelMenu(self, entry):
        labelID = entry.sr.node.currentView
        m = []
        if sm.GetService('addressbook').ShowLabelMenuAndManageBtn(self.contactType):
            m.append((MenuLabel('UI/PeopleAndPlaces/LabelsRename'), sm.GetService('addressbook').RenameContactLabelFromUI, (labelID,)))
            m.append(None)
            m.append((MenuLabel('UI/PeopleAndPlaces/LabelsDelete'), sm.GetService('addressbook').DeleteContactLabelFromUI, (labelID, entry.sr.node.label)))
        return m

    def ManageLabels(self, *args):
        configName = '%s%s' % ('ManageLabels', self.contactType)
        ManageLabels.Open(windowID=configName, labelType=self.contactType)

    def GetStaticLabelsGroups(self):
        scrolllist = []
        labelList = [(localization.GetByLabel('UI/PeopleAndPlaces/AllContacts'), const.contactAll),
         (localization.GetByLabel('UI/PeopleAndPlaces/ExcellentStanding'), const.contactHighStanding),
         (localization.GetByLabel('UI/PeopleAndPlaces/GoodStanding'), const.contactGoodStanding),
         (localization.GetByLabel('UI/PeopleAndPlaces/NeutralStanding'), const.contactNeutralStanding),
         (localization.GetByLabel('UI/PeopleAndPlaces/BadStanding'), const.contactBadStanding),
         (localization.GetByLabel('UI/PeopleAndPlaces/TerribleStanding'), const.contactHorribleStanding)]
        if self.contactType == TAB_CONTACTS:
            labelList.append((localization.GetByLabel('UI/PeopleAndPlaces/Watchlist'), const.contactWatchlist))
            labelList.append((localization.GetByLabel('UI/PeopleAndPlaces/Blocked'), const.contactBlocked))
            labelList.insert(0, (localization.GetByLabel('UI/PeopleAndPlaces/Notifications'), const.contactNotifications))
        for label, groupID in labelList:
            entry = self.GetGroupEntry(groupID, label, selected=groupID == self._GetLastViewedID())
            scrolllist.append(entry)

        if self.contactType == TAB_CONTACTS:
            scrolllist.insert(-1, GetFromClass(Space, {'height': 16}))
        return scrolllist

    def _GetLastViewedID(self):
        if self.contactType == TAB_CONTACTS:
            lastViewedID = settings.char.ui.Get('contacts_lastselected', None)
        elif self.contactType == TAB_CORPCONTACTS:
            lastViewedID = settings.char.ui.Get('corpcontacts_lastselected', None)
        elif self.contactType == 'alliancecontact':
            lastViewedID = settings.char.ui.Get('alliancecontacts_lastselected', None)
        return lastViewedID

    def GetGroupEntry(self, groupID, label, selected = 0):
        cls = ContactListGroup if groupID in CONTACTGROUPID_TO_STATEID else ListGroup
        return GetFromClass(cls, {'GetSubContent': self.GetLeftGroups,
         'label': label,
         'cleanLabel': label,
         'id': ('contact', groupID),
         'state': 'locked',
         'BlockOpenWindow': 0,
         'disableToggle': 1,
         'expandable': 0,
         'showicon': 'hide',
         'iconID': contactsConst.iconByContactType.get(groupID, None),
         'showlen': 1,
         'groupItems': self.GetContactsCount(groupID),
         'hideNoItem': 1,
         'hideExpander': 1,
         'hideExpanderLine': 1,
         'selectGroup': 1,
         'isSelected': selected,
         'groupID': groupID,
         'OnClick': self.LoadGroupFromEntry})

    def LoadContactsForm(self, *args):
        if self.contactType == TAB_CONTACTS:
            self.onlinecheck.state = uiconst.UI_NORMAL
        else:
            self.onlinecheck.state = uiconst.UI_HIDDEN
        self.LoadData()
        self.LoadLeftSide()

    def UpdateTopContHeight(self):
        if self.contactType == TAB_CONTACTS:
            self.topCont.height = 45
        elif sm.GetService('addressbook').ShowLabelMenuAndManageBtn(self.contactType):
            self.topCont.height = 38
        else:
            self.topCont.height = 32

    def CheckInGroup(self, groupID, relationshipID):
        if groupID == const.contactHighStanding:
            if relationshipID > const.contactGoodStanding:
                return True
        elif groupID == const.contactGoodStanding:
            if relationshipID > const.contactNeutralStanding and relationshipID <= const.contactGoodStanding:
                return True
        elif groupID == const.contactNeutralStanding:
            if relationshipID == const.contactNeutralStanding:
                return True
        elif groupID == const.contactBadStanding:
            if relationshipID < const.contactNeutralStanding and relationshipID >= const.contactBadStanding:
                return True
        elif groupID == const.contactHorribleStanding:
            if relationshipID < const.contactBadStanding:
                return True
        return False

    def CheckHasLabel(self, labelID, labelMask):
        if not labelMask and labelID == -1:
            return True
        elif labelMask & labelID == labelID:
            return True
        else:
            return False

    def LoadGroupFromEntry(self, entry, *args):
        group = entry.sr.node
        self.blockedSelected = False
        if self.group != group.groupID:
            self.startPos = 0
            self.group = group.groupID
        if group.groupID == const.contactBlocked:
            self.blockedSelected = True
        self.LoadGroupFromNode(group)

    def CheckIfAgent(self, contactID):
        if sm.GetService('agents').IsAgent(contactID):
            return True
        if idCheckers.IsNPC(contactID) and idCheckers.IsCharacter(contactID):
            return True

    def GetContactsLabelCount(self, labelID):
        contactList = []
        for contact in self.contacts:
            if self.CheckHasLabel(labelID, contact.labelMask):
                contactList.append(contact.contactID)

        count = len(contactList)
        return count

    def GetContactsCount(self, groupID):
        contactList = []
        if groupID == const.contactBlocked:
            for blocked in self.blocked:
                contactList.append(blocked.contactID)

        elif groupID == const.contactNotifications:
            for notification in self.notifications:
                contactList.append(notification.notificationID)

        else:
            for contact in self.contacts:
                if groupID == const.contactAll:
                    contactList.append(contact.contactID)
                elif groupID == const.contactWatchlist:
                    if contact.inWatchlist:
                        contactList.append(contact.contactID)
                elif groupID == const.contactHighStanding:
                    if contact.relationshipID > const.contactGoodStanding:
                        contactList.append(contact.contactID)
                elif groupID == const.contactGoodStanding:
                    if contact.relationshipID > const.contactNeutralStanding and contact.relationshipID <= const.contactGoodStanding:
                        contactList.append(contact.contactID)
                elif groupID == const.contactNeutralStanding:
                    if contact.relationshipID == const.contactNeutralStanding:
                        contactList.append(contact.contactID)
                elif groupID == const.contactBadStanding:
                    if contact.relationshipID < const.contactNeutralStanding and contact.relationshipID >= const.contactBadStanding:
                        contactList.append(contact.contactID)
                elif groupID == const.contactHorribleStanding:
                    if contact.relationshipID < const.contactBadStanding:
                        contactList.append(contact.contactID)

        return contactList

    def GetLabelName(self, labelID, *args):
        labels = sm.GetService('addressbook').GetContactLabels(self.contactType).values()
        if labelID == -1:
            return localization.GetByLabel('UI/PeopleAndPlaces/NoLabel')
        for label in labels:
            if labelID == label.labelID:
                return label.name

    def GetScrolllist(self, data):
        scrolllist = []
        noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoContacts')
        onlineOnly = False
        headers = True
        reverse = False
        if self.contactType == TAB_CONTACTS:
            settings.char.ui.Set('contacts_lastselected', data.groupID)
            onlineOnly = settings.user.ui.Get('onlinebuddyonly', 0)
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoContacts')
        elif self.contactType == TAB_CORPCONTACTS:
            settings.char.ui.Set('corpcontacts_lastselected', data.groupID)
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoCorpContacts')
        elif self.contactType == 'alliancecontact':
            settings.char.ui.Set('alliancecontacts_lastselected', data.groupID)
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoAllianceContacts')
        if data.groupID == const.contactWatchlist:
            self.scroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID) and idCheckers.IsCharacter(contact.contactID) and contact.inWatchlist:
                    entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                    if entryTuple is not None:
                        scrolllist.append(entryTuple)

            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoneOnWatchlist')
        elif data.groupID == const.contactBlocked:
            self.scroll.multiSelect = 1
            for blocked in self.blocked:
                if blocked.contactID > 0 and not self.CheckIfAgent(blocked.contactID):
                    entryTuple = sm.GetService('addressbook').GetContactEntry(data, blocked, onlineOnly, contactType=self.contactType)
                    if entryTuple is not None:
                        scrolllist.append(entryTuple)

            if sm.GetService('account').GetDefaultContactCost() == -1:
                noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/UnknownBlocked')
            else:
                noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoneBlockedYet')
        elif data.groupID == const.contactAll:
            self.scroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID):
                    entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                    if entryTuple is not None:
                        scrolllist.append(entryTuple)

        elif data.groupID == const.contactNotifications:
            self.scroll.multiSelect = 0
            for notification in self.notifications:
                scrolllist.append(sm.GetService('addressbook').GetNotifications(notification))

            headers = False
            reverse = True
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoNotifications')
        elif data.groupID in (const.contactGoodStanding,
         const.contactHighStanding,
         const.contactNeutralStanding,
         const.contactBadStanding,
         const.contactHorribleStanding):
            self.scroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID):
                    if self.CheckInGroup(data.groupID, contact.relationshipID):
                        entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                        if entryTuple is not None:
                            scrolllist.append(entryTuple)

            standingText = self.GetStandingNameShort(data.groupID)
            if self.contactType == TAB_CONTACTS:
                noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoContactsStanding', standingText=standingText)
            elif self.contactType == TAB_CORPCONTACTS:
                noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoCorpContactsStanding', standingText=standingText)
            elif self.contactType == TAB_ALLIANCECONTACTS:
                noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoAllianceContactsStanding', standingText=standingText)
        else:
            self.scroll.multiSelect = 1
            for contact in self.contacts:
                if not self.CheckIfAgent(contact.contactID):
                    if self.CheckHasLabel(data.groupID, contact.labelMask):
                        entryTuple = sm.GetService('addressbook').GetContactEntry(data, contact, onlineOnly, contactType=self.contactType, contactLevel=contact.relationshipID, labelMask=contact.labelMask)
                        if entryTuple is not None:
                            scrolllist.append(entryTuple)

            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoContactsLabel', standingText=self.GetLabelName(data.groupID))
        if onlineOnly:
            noContentHint = localization.GetByLabel('UI/PeopleAndPlaces/NoOnlineContact')
        if len(self.quickFilter.GetValue()):
            noContentHint = localization.GetByLabel('UI/Common/NothingFound')
        totalNum = len(scrolllist)
        for entryTuple in scrolllist:
            entryTuple[1]['showChatBubble'] = True

        scrolllist = SortListOfTuples(scrolllist, reverse)
        scrolllist = scrolllist[self.startPos:self.startPos + const.maxContactsPerPage]
        return (scrolllist,
         noContentHint,
         totalNum,
         headers)

    def LoadGroupFromNode(self, data, *args):
        if self.contactType == TAB_ALLIANCECONTACTS and session.allianceid is None:
            self.scroll.Load(fixedEntryHeight=19, contentList=[], noContentHint=localization.GetByLabel('UI/PeopleAndPlaces/OwnerNotInAnyAlliance', corpName=cfg.eveowners.Get(session.corpid).ownerName))
            return
        scrolllist, noContentHint, totalNum, displayHeaders = self.GetScrolllist(data)
        if displayHeaders:
            headers = [localization.GetByLabel('UI/Common/Name')]
        else:
            headers = []
        self.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=noContentHint)
        self.UpdatePaginationCont(totalNum or 0)

    def CheckBoxChange(self, checkbox, *args):
        settings.user.ui.Set(checkbox.GetSettingsKey(), checkbox.checked)
        self.LoadContactsForm()

    def GetLeftGroups(self, data, *args):
        scrolllist = self.GetScrolllist(data)[0]
        return scrolllist

    def LabelGroupMenu(self, node, *args):
        return [(MenuLabel('UI/PeopleAndPlaces/ManageLabels'), self.ManageLabels)]

    def LoadData(self, *args):
        self.contacts = []
        self.blocked = []
        self.notifications = []
        allContacts = sm.GetService('addressbook').GetContacts()
        if self.contactType == TAB_CONTACTS:
            self.contacts = allContacts.contacts.values()
            self.blocked = allContacts.blocked.values()
            self.notifications = sm.GetService('notificationSvc').GetFormattedNotifications(const.groupContacts)
        elif self.contactType == TAB_CORPCONTACTS:
            self.contacts = allContacts.corpContacts.values()
        elif self.contactType == TAB_ALLIANCECONTACTS:
            self.contacts = allContacts.allianceContacts.values()
        filter = self.quickFilter.GetValue()
        if len(filter):
            bannedwords.check_search_words_allowed(filter)
            self.blocked = NiceFilter(self.quickFilter.QuickFilter, self.blocked)
            self.contacts = NiceFilter(self.quickFilter.QuickFilter, self.contacts)

    def BrowseContacts(self, backforth, *args):
        pos = max(0, self.startPos + const.maxContactsPerPage * backforth)
        self.startPos = pos
        self.LoadContactsForm()

    def UpdatePaginationCont(self, totalNum):
        btnDisplayed = 0
        if self.startPos == 0:
            self.contactBackBtn.Disable()
        else:
            self.contactBackBtn.Enable()
            btnDisplayed = 1
        if self.startPos + const.maxContactsPerPage >= totalNum:
            self.contactFwdBtn.Disable()
        else:
            self.contactFwdBtn.Enable()
            btnDisplayed = 1
        self.paginationCont.display = btnDisplayed
        if btnDisplayed:
            self.UpdatePageCountLabel(totalNum)

    def UpdatePageCountLabel(self, totalNum):
        numPages = int(math.ceil(totalNum / float(const.maxContactsPerPage)))
        currentPage = self.startPos / const.maxContactsPerPage + 1
        self.pageCount.text = '%s/%s' % (currentPage, numPages)

    def OnContactDropData(self, dragObj, nodes):
        if self.contactType == TAB_CONTACTS and settings.char.ui.Get('contacts_lastselected', None) == const.contactBlocked:
            sm.GetService('addressbook').DropInBlocked(nodes)
        else:
            sm.GetService('addressbook').DropInPersonal(nodes, self.contactType)

    def ReloadData(self):
        self.LoadData()
        self.LoadLeftSide()
        if len(self.scroll.GetNodes()) < 1:
            self.BrowseContacts(-1)

    def OnNotificationsRefresh(self):
        if self.contactType == TAB_CONTACTS and settings.char.ui.Get('contacts_lastselected', None) == const.contactNotifications:
            self.ReloadData()

    def OnMessageChanged(self, type, messageIDs, what):
        if type == const.mailTypeNotifications and what == 'deleted':
            if self.contactType == TAB_CONTACTS and settings.char.ui.Get('contacts_lastselected', None) == const.contactNotifications:
                self.ReloadData()

    def OnContactChange(self, contactIDs, contactType = None):
        if contactType == self.contactType:
            self.ReloadData()

    def OnSetAllianceStanding(self, *args):
        if self.contactType == TAB_ALLIANCECONTACTS:
            self.ReloadData()

    def OnSetCorpStanding(self, *args):
        if self.contactType == TAB_CORPCONTACTS:
            self.ReloadData()

    def OnMyLabelsChanged(self, contactType, labelID):
        if contactType == self.contactType:
            self.LoadLeftSide()

    def OnEditLabel(self, contactIDs, contactType):
        if contactType == self.contactType:
            self.ReloadData()

    def OnUnblockContact(self, contactID):
        if self.contactType == TAB_CONTACTS:
            self.ReloadData()

    def OnGroupDropData(self, groupID, nodes, *args):
        what, labelID, labelName = groupID
        contactIDs = []
        for node in nodes:
            contactIDs.append(node.itemID)

        if len(contactIDs):
            sm.StartService('addressbook').AssignLabelFromWnd(contactIDs, labelID, labelName)


class LabelListGroup(ListGroup):
    _manage_labels_button = None

    def Startup(self, *etc):
        super(LabelListGroup, self).Startup(*etc)
        self._manage_labels_button = ButtonIcon(parent=self, align=uiconst.CENTERRIGHT, width=24, height=24, iconSize=16, texturePath=eveicon.settings, func=None, hint=localization.GetByLabel('UI/PeopleAndPlaces/ManageLabels'))

    def Load(self, node):
        super(LabelListGroup, self).Load(node)
        manage_labels_callback = node.get('manage_labels_callback', None)
        if manage_labels_callback:
            self._manage_labels_button.func = manage_labels_callback
