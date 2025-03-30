#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\ownerSearch.py
import copy
import types
import localization
import utillib
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.user import SearchedUser
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.util import searchOld, searchUtil
from eve.common.script.search.const import MatchBy
from eve.common.script.sys import idCheckers
from eve.common.lib import appConst as const

class OwnerSearchWindow(Window):
    __guid__ = 'form.OwnerSearchWindow'
    __notifyevents__ = ['OnContactChange',
     'OnContactNoLongerContact',
     'OnSearcedUserRemoved',
     'OnSearcedUserAdded']
    default_windowID = 'ownerSearchWindow'
    default_minSize = (250, 250)
    default_width = 300
    default_height = 400
    default_isMinimizable = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        actionBtns = attributes.actionBtns or []
        caption = attributes.caption or ''
        inpt = attributes.input or ''
        showContactList = attributes.get('showContactList', False)
        extraIconHintFlag = attributes.extraIconHintFlag or None
        configname = attributes.configname or ''
        multiSelect = attributes.get('multiSelect', True)
        ownerGroups = attributes.get('ownerGroups', [const.groupCharacter])
        self.contactsLoaded = 0
        self.SetCaption(caption)
        self.showContactList = showContactList
        self.extraIconHintFlag = extraIconHintFlag
        self.configname = configname
        self.ownerGroups = ownerGroups
        self.sr.hintCont = Container(name='hintCont', parent=self.sr.main, align=uiconst.TOTOP, pos=(0, 0, 0, 16), state=uiconst.UI_HIDDEN)
        searchParent = self.sr.main
        if showContactList:
            self.sr.searchCont = Container(name='searchCont', parent=self.sr.main, align=uiconst.TOALL)
            self.sr.scroll = eveScroll.Scroll(name='searchScroll', parent=self.sr.searchCont, multiSelect=multiSelect)
            self.sr.scroll.OnSelectionChange = self.RefreshSelection
            self.sr.contactsScroll = eveScroll.Scroll(name='contactsScroll', parent=self.sr.main, multiSelect=multiSelect)
            self.sr.contactsScroll.OnSelectionChange = self.RefreshSelection
            self.sr.tabs = TabGroup(name='tabs', parent=self.sr.main, tabs=[[localization.GetByLabel('UI/Mail/Search'),
              self.sr.searchCont,
              self,
              'search'], [localization.GetByLabel('UI/Mail/AllContacts'),
              self.sr.contactsScroll,
              self,
              'contacts']], groupID='calenderEvent_tabs', autoselecttab=1, idx=0)
            searchParent = self.sr.searchCont
        else:
            self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, multiSelect=multiSelect)
            self.sr.scroll.OnSelectionChange = self.RefreshSelection
        self.currentScroll = self.sr.scroll
        searchCont = Container(name='searchCont', parent=searchParent, align=uiconst.TOTOP, idx=0, height=40)
        searchByCont = Container(name='searchByCont', parent=searchParent, align=uiconst.TOTOP, idx=0, height=40)
        searchBtnCont = Container(name='searchBtnCont', parent=searchCont, align=uiconst.TORIGHT, height=40)
        inputCont = Container(name='inputCont', parent=searchCont, align=uiconst.TOALL)
        self.sr.searchBy = Combo(label=localization.GetByLabel('UI/Common/SearchBy'), parent=searchByCont, options=searchUtil.GetSearchByChoices(), name='ownerSearchSearchBy', select=settings.user.ui.Get('ownersSearchBy', MatchBy.partial_terms), width=170, labelleft=65, callback=self.ChangeSearchBy)
        self.sr.inpt = inpt = SingleLineEditText(name='input', parent=inputCont, maxLength=50, label='', setvalue=inpt, align=uiconst.TOTOP, isCharacterField=True)
        self.sr.searchBtn = Button(parent=searchBtnCont, label=localization.GetByLabel('UI/Mail/Search'), func=self.Search, btn_default=1, padLeft=8)
        searchBtnCont.width = self.sr.searchBtn.width
        btns = []
        self.dblClickFunc = None
        for each in actionBtns:
            text, func, dblClickFunc = each
            btns.append([text,
             func,
             lambda : self.GetSelectedInCurrentScroll(),
             None])
            if dblClickFunc:
                self.dblClickFunc = func

        self.sr.btns = ButtonGroup(btns=btns, parent=self.sr.main, idx=0)
        self.sr.btns.state = uiconst.UI_HIDDEN
        self.sr.scroll.Load(contentList=[], headers=[], noContentHint=localization.GetByLabel('UI/Common/TypeInSearch'))

    def ChangeSearchBy(self, entry, header, value, *args):
        settings.user.ui.Set('ownersSearchBy', value)

    def GetSelectedInCurrentScroll(self, *args):
        return self.currentScroll.GetSelected()

    def Load(self, key, *args):
        if not self or self.destroyed:
            return
        if key == 'contacts':
            if not self.contactsLoaded:
                self.LoadContacts()
                self.contactsLoaded = 1
            self.currentScroll = self.sr.contactsScroll
        elif key == 'search':
            self.currentScroll = self.sr.scroll
        self.RefreshSelection()

    def RefreshSelection(self, *args):
        sel = self.currentScroll.GetSelected()
        if len(sel) < 1:
            self.sr.btns.state = uiconst.UI_HIDDEN
            return
        self.sr.btns.state = uiconst.UI_PICKCHILDREN

    def DblClickEntry(self, entry, ignoreConfirm = False, *args):
        if ignoreConfirm or entry.confirmOnDblClick:
            self.currentScroll.SelectNode(entry.sr.node)
            if self.dblClickFunc is not None:
                apply(self.dblClickFunc, (self.currentScroll.GetSelected,))

    def ClickEntry(self, *args):
        self.RefreshSelection()

    def ExtraMenuFunction(self, *args):
        return []

    def Search(self, *args):
        inpt = self.sr.inpt.GetValue()
        if inpt.strip() == '':
            self.sr.scroll.Load(contentList=[], headers=[], noContentHint=localization.GetByLabel('UI/Common/TypeInSearch'))
            return
        hint = ''
        searchBy = settings.user.ui.Get('ownersSearchBy', MatchBy.partial_terms)
        lst = []
        for groupID in self.ownerGroups:
            lst += searchOld.Search(inpt, groupID, getWindow=0, hideNPC=1, notifyOneMatch=1, modal=0, getError=1, exact=searchBy)

        if len(lst) >= 500:
            hint = localization.GetByLabel('UI/Mail/25OrMoreFound', name=inpt)
        try:
            scrolllist = self.GetUserEntries(lst)
            extraEntries = self.GetExtraSearchEntries(inpt, searchBy)
            scrolllist = extraEntries + scrolllist
            noContentHint = localization.GetByLabel('UI/Market/NothingFoundWithSearch', search=inpt)
            self.sr.scroll.Load(contentList=scrolllist, headers=[], noContentHint=noContentHint)
            self.SetHint(hint)
            self.RefreshSelection()
        except:
            if not self or self.destroyed:
                return
            raise

    def GetExtraSearchEntries(self, searchString, searchBy):
        return []

    def GetUserEntries(self, lst):
        scrolllist = []
        for info in lst:
            if type(info) in [types.StringType, types.UnicodeType]:
                continue
            entryTuple = self.GetUserEntryTuple(info[1])
            scrolllist.append(entryTuple)

        scrolllist = SortListOfTuples(scrolllist)
        return scrolllist

    def SetHint(self, hint):
        hp = self.sr.hintCont
        hp.Flush()
        if hint:
            t = eveLabel.EveLabelMedium(text=hint, parent=hp, top=-3, align=uiconst.CENTER, width=self.minsize[0] - 32, state=uiconst.UI_DISABLED)
            hp.state = uiconst.UI_DISABLED
            hp.height = t.height + 4
        else:
            hp.state = uiconst.UI_HIDDEN

    def LoadContacts(self, *args):
        allContacts = sm.GetService('addressbook').GetContacts()
        contacts = allContacts.contacts.values()
        scrolllist = []
        for contact in contacts:
            if idCheckers.IsNPC(contact.contactID):
                continue
            if cfg.eveowners.Get(contact.contactID).groupID not in self.ownerGroups:
                continue
            entryTuple = self.GetUserEntryTuple(contact.contactID, contact)
            scrolllist.append(entryTuple)

        scrolllist = SortListOfTuples(scrolllist)
        self.sr.contactsScroll.Load(contentList=scrolllist, headers=[], noContentHint=localization.GetByLabel('UI/AddressBook/NoContacts'))

    def GetUserEntryTuple(self, ownerID, contact = None, *args):
        if contact is None:
            contact = utillib.KeyVal(contactID=ownerID)
        extraIconHintFlag = copy.copy(self.extraIconHintFlag)
        if extraIconHintFlag and self.IsAdded(ownerID):
            extraIconHintFlag[-1] = True
        extraInfo = utillib.KeyVal(extraIconHintFlag=extraIconHintFlag, wndConfigname=self.configname)
        entryTuple = sm.GetService('addressbook').GetContactEntry(None, contact, dblClick=self.DblClickContact, menuFunction=self.ExtraMenuFunction, extraInfo=extraInfo, listentryType=SearchedUser)
        return entryTuple

    def IsAdded(self, contactID, *args):
        return False

    def DblClickContact(self, entry, *args):
        self.DblClickEntry(entry, ignoreConfirm=True)

    def OnContactChange(self, contactIDs, contactType):
        if contactType == 'contact':
            self.ReloadContactList()

    def OnContactNoLongerContact(self, ownerID):
        self.ReloadContactList()

    def ReloadContactList(self, *args):
        if self.showContactList and self.contactsLoaded:
            self.LoadContacts()

    def OnSearcedUserAdded(self, ownerID, configname, *args):
        self.MarkEntriesAddedOrRemoved(configname, [ownerID], isAdded=1)

    def OnSearcedUserRemoved(self, ownerIDs, configname, *args):
        self.MarkEntriesAddedOrRemoved(configname, ownerIDs, isAdded=0)

    def MarkEntriesAddedOrRemoved(self, configname, ownerIDs, isAdded = 0, *args):
        if self.configname != configname:
            return
        if len(ownerIDs) < 1:
            return
        scrolls = []
        for scrollName in ['scroll', 'contactsScroll']:
            scroll = self.sr.Get(scrollName, None)
            if scroll is not None:
                scrolls.append(scroll)

        for scroll in scrolls:
            ids = ownerIDs[:]
            for entry in scroll.GetNodes():
                if entry.charID in ids:
                    ids.remove(entry.charID)
                    entry.isAdded = isAdded
                    if entry.panel:
                        entry.panel.SearcedUserAddedOrRemoved(entry.isAdded)
                    if len(ids) < 1:
                        break
