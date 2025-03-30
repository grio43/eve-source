#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\addressBookWindow.py
import carbonui.const as uiconst
import eve.client.script.ui.util.searchUtil as searchUtil
import eveicon
import localization
import locks
import threadutils
import uthread
import utillib
from carbonui.control.button import Button
from carbonui import ButtonVariant
from carbonui.control.combo import Combo
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import CharSettingEnum
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.button.menu import MenuButtonIcon
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.shared.neocom.addressBook.contactsConst import TAB_AGENTS, TAB_BOOKMARKS, TAB_CONTACTS, TAB_SEARCH
from eve.client.script.ui.shared.neocom.addressBook.contactsForm import ContactsForm
from eve.client.script.ui.shared.userentry import AgentEntry
from eve.common.script.search.const import ResultType, MatchBy
DEFAULT_SEARCH_STYLE = MatchBy.partial_terms
grplst = [[localization.GetByLabel('UI/Common/Any'), -1],
 [localization.GetByLabel('UI/Agents/Agent'), ResultType.agent],
 [localization.GetByLabel('UI/Common/Character'), ResultType.character],
 [localization.GetByLabel('UI/Common/Corporation'), ResultType.corporation],
 [localization.GetByLabel('UI/Common/Alliance'), ResultType.alliance],
 [localization.GetByLabel('UI/Common/Faction'), ResultType.faction],
 [localization.GetByLabel('UI/Common/LocationTypes/Station'), ResultType.station],
 [localization.GetByLabel('UI/Common/LocationTypes/Structures'), ResultType.structure_with_inlined_data],
 [localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'), ResultType.solar_system],
 [localization.GetByLabel('UI/Common/LocationTypes/Constellation'), ResultType.constellation],
 [localization.GetByLabel('UI/Common/LocationTypes/Region'), ResultType.region]]

class AddressBookWindow(Window):
    default_width = 600
    default_height = 500
    default_minSize = (320, 307)
    default_windowID = 'addressbook'
    default_captionLabelPath = 'UI/PeopleAndPlaces/WindowTitle'
    default_descriptionLabelPath = 'Tooltips/Neocom/Contacts_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/peopleandplaces.png'

    def ApplyAttributes(self, attributes):
        super(AddressBookWindow, self).ApplyAttributes(attributes)
        self.inited = 0
        self.tabGroup = self.header.tab_group
        self.scroll = eveScroll.Scroll(parent=self.sr.main)
        self.contactsPanel = ContactsForm(name='contactsform', parent=self.sr.main, contactType=TAB_CONTACTS)
        self.searchPanel = SearchPanel(parent=self.content, align=uiconst.TOALL)
        self.agentsBtnGroup = ContainerAutoSize(parent=self.content, align=uiconst.TOBOTTOM, idx=0, padTop=8)
        Button(parent=self.agentsBtnGroup, align=uiconst.CENTERLEFT, label=localization.GetByLabel('UI/PeopleAndPlaces/CreateFolder'), texturePath=eveicon.add_folder, func=lambda : self.AddGroup('agentgroups'), args=(), variant=ButtonVariant.GHOST)
        self.scroll.sr.content.OnDropData = self.OnDropData
        idx = settings.user.tabgroups.Get('addressbookpanel', None)
        if idx is None:
            settings.user.tabgroups.Set('addressbookpanel', 4)
        self.ConstructTabs()
        self.inited = 1

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def ConstructTabs(self):
        self.tabGroup.AddTab(localization.GetByLabel('UI/PeopleAndPlaces/Contacts'), self.contactsPanel, self, tabID=TAB_CONTACTS)
        self.tabGroup.AddTab(localization.GetByLabel('UI/PeopleAndPlaces/Agents'), self.scroll, self, tabID=TAB_AGENTS)
        self.tabGroup.AddTab(label=localization.GetByLabel('UI/Common/Search'), panel=self.searchPanel, code=self, tabID=TAB_SEARCH)
        self.tabGroup.AutoSelect()
        self.tabGroup.sr.Get('%s_tab' % localization.GetByLabel('UI/PeopleAndPlaces/Agents'), None).OnTabDropData = self.DropInAgents
        self.tabGroup.sr.Get('%s_tab' % localization.GetByLabel('UI/PeopleAndPlaces/Contacts'), None).OnTabDropData = self.DropInPersonalContact

    def ConstructSearchPanel(self):
        searchPanel = Container(name='topParent', parent=self.sr.main, align=uiconst.TOTOP, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=searchPanel, state=uiconst.UI_DISABLED, pos=(0, -3, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        searchTypeCombo = Combo(label=localization.GetByLabel('UI/Common/SearchType'), parent=searchPanel, options=grplst, name='addressBookComboSearchType', select=settings.user.ui.Get('ppSearchGroup', -1), width=86, left=74, top=20, callback=self.ChangeSearchGroup)
        self.searchEdit = SingleLineEditText(name='search', parent=searchPanel, maxLength=100, left=searchTypeCombo.left + searchTypeCombo.width + 6, top=searchTypeCombo.top, width=86, label=localization.GetByLabel('UI/PeopleAndPlaces/SearchString'))
        Button(parent=searchPanel, label=localization.GetByLabel('UI/Common/Buttons/Search'), pos=(self.searchEdit.left + self.searchEdit.width + 2,
         self.searchEdit.top,
         0,
         0), func=self.Search, btn_default=1)
        self.searchByCombo = Combo(label=localization.GetByLabel('UI/Common/SearchBy'), parent=searchPanel, options=searchUtil.GetSearchByChoices(), name='addressBookComboSearchBy', select=settings.user.ui.Get('ppSearchBy', DEFAULT_SEARCH_STYLE), width=233, left=75, top=self.searchEdit.top + self.searchEdit.height + 2, labelleft=searchTypeCombo.left + searchTypeCombo.width + 6 - 75, callback=self.ChangeSearchBy)
        searchPanel.height = max(52, self.searchByCombo.top + self.searchByCombo.height)

    def DropInAgents(self, *args):
        sm.GetService('addressbook').DropInAgents(*args)

    def DropInPersonalContact(self, *args):
        sm.GetService('addressbook').DropInPersonalContact(*args)

    def DropInBuddyGroup(self, *args):
        sm.GetService('addressbook').DropInBuddyGroup(*args)

    def OnDropData(self, dragObj, nodes):
        self.ShowLoad()
        try:
            visibletab = self.tabGroup.GetSelectedTab()
            if visibletab and hasattr(visibletab, 'OnTabDropData'):
                visibletab.OnTabDropData(dragObj, nodes)
        finally:
            if self is not None and not self.destroyed and self.inited:
                self.HideLoad()

    def AddGroup(self, listID, *args):
        uicore.registry.AddListGroup(listID)
        self.RefreshWindow()

    def RefreshWindow(self):
        if not self.destroyed and self.inited:
            self.tabGroup.ReloadVisible()

    def ChangeSearchGroup(self, entry, header, value, *args):
        settings.user.ui.Set('ppSearchGroup', value)

    def ChangeSearchBy(self, entry, header, value, *args):
        settings.user.ui.Set('ppSearchBy', value)

    def Search(self, *args):
        groupID = settings.user.ui.Get('ppSearchGroup', -1)
        if groupID == -1:
            groupIDList = [ResultType.agent,
             ResultType.character,
             ResultType.corporation,
             ResultType.alliance,
             ResultType.faction,
             ResultType.station,
             ResultType.solar_system,
             ResultType.constellation,
             ResultType.region,
             ResultType.structure_with_inlined_data]
        else:
            groupIDList = [groupID]
        exactSearch = settings.user.ui.Get('ppSearchBy', DEFAULT_SEARCH_STYLE)
        searchUtil.GetResultsInNewWindow(self.searchEdit.GetValue().strip(), groupIDList, searchBy=exactSearch, searchWndName='addressBookSearch')

    def Load(self, args):
        uthread.Lock(self, 'load')
        try:
            self.agentsBtnGroup.state = uiconst.UI_HIDDEN
            self.scroll.sr.iconMargin = 0
            self.scroll.sr.id = '%sAddressBookScroll' % args
            self.scroll.sr.ignoreTabTrimming = 1
            if args == TAB_AGENTS:
                self.ShowAgents()
            elif args == TAB_BOOKMARKS:
                self.ShowPlacesNew()
            self.lastTab = args
        finally:
            uthread.UnLock(self, 'load')

    def ShowAgents(self):
        self.agentsBtnGroup.state = uiconst.UI_PICKCHILDREN
        all_agents_group = uicore.registry.GetListGroup(('agentgroups', 'all'))
        uicore.registry.GetLockedGroup(listID='agentgroups', listgroupName='all', label=localization.GetByLabel('UI/PeopleAndPlaces/AllAgents'), openState=all_agents_group.get('open', True))
        scrollData = self._GetAgentScrollData()
        scrolllist = []
        for s in scrollData:
            scrolllist.append((s.sortBy.lower(), GetFromClass(ListGroup, {'GetSubContent': self.GetAgentsSubContent,
              'DropData': self.DropInBuddyGroup,
              'RefreshScroll': self.RefreshWindow,
              'label': s.label,
              'id': s.id,
              'groupItems': s.groupItems,
              'headers': [localization.GetByLabel('UI/Common/Name')],
              'iconMargin': 18,
              'showlen': 1,
              'state': s.state,
              'npc': True,
              'allowCopy': 1,
              'showicon': s.logo,
              'allowGuids': AllUserEntries()})))

        self.scroll.sr.iconMargin = 18
        scrolllist = SortListOfTuples(scrolllist)
        self.scroll.Load(contentList=scrolllist, fixedEntryHeight=None, headers=[localization.GetByLabel('UI/Common/Name')], scrolltotop=not getattr(self, 'personalshown', 0), noContentHint=localization.GetByLabel('UI/PeopleAndPlaces/NoAgents'))
        setattr(self, 'personalshown', 1)
        if not self.destroyed:
            self.HideLoad()

    def _GetAgentScrollData(self):
        agents = sm.GetService('addressbook').GetAgents()
        scrollData = []
        groups = uicore.registry.GetListGroups('agentgroups')
        for g in groups.iteritems():
            key = g[0]
            data = utillib.KeyVal(g[1])
            if key == 'all':
                data.sortBy = ['  1', '  2'][key == 'allcorps']
                data.groupItems = agents
            else:
                data.sortBy = data.label
                data.state = None
                data.groupItems = filter(lambda charID: charID in agents, data.groupItems)
            data.logo = 'res:/UI/Texture/WindowIcons/agent.png'
            scrollData.append(data)

        return scrollData

    def ShowPlacesNew(self):
        self.bookmarksPanel.Setup()

    def GetAgentsSubContent(self, nodedata, newitems = 0):
        if not len(nodedata.groupItems):
            return []
        charsToPrime = []
        for charID in nodedata.groupItems:
            charsToPrime.append(charID)

        cfg.eveowners.Prime(charsToPrime)
        agents = sm.GetService('addressbook').GetAgents()
        scrolllist = []
        for charID in nodedata.groupItems:
            if charID in agents:
                scrolllist.append(GetFromClass(AgentEntry, {'listGroupID': nodedata.id,
                 'charID': charID,
                 'info': cfg.eveowners.Get(charID)}))

        scrolllist = localization.util.Sort(scrolllist, key=lambda x: x['info'].ownerName)
        return scrolllist


class SearchType(object):
    all = 0
    character = 1
    corporation = 2
    alliance = 3
    agent = 4
    faction = 5
    _RESULT_TYPE_BY_SEARCH_TYPE = {character: ResultType.character,
     corporation: ResultType.corporation,
     alliance: ResultType.alliance,
     agent: ResultType.agent,
     faction: ResultType.faction}
    _DISPLAY_NAME_BY_SEARCH_TYPE = {all: localization.GetByLabel('UI/Common/Any'),
     character: localization.GetByLabel('UI/Common/Character'),
     corporation: localization.GetByLabel('UI/Common/Corporation'),
     alliance: localization.GetByLabel('UI/Common/Alliance'),
     agent: localization.GetByLabel('UI/Agents/Agent'),
     faction: localization.GetByLabel('UI/Common/Faction')}

    @classmethod
    def as_result_type_list(cls, search_type):
        if search_type == cls.all:
            return [ResultType.character,
             ResultType.corporation,
             ResultType.alliance,
             ResultType.agent,
             ResultType.faction]
        else:
            return [cls._RESULT_TYPE_BY_SEARCH_TYPE[search_type]]

    @classmethod
    def display_name(cls, search_type):
        return cls._DISPLAY_NAME_BY_SEARCH_TYPE[search_type]

    @classmethod
    def iter(cls):
        for name in dir(cls):
            if name.startswith('_'):
                continue
            value = getattr(cls, name)
            if isinstance(value, int):
                yield value


SORT_KEY_BY_SEARCH_TYPE = {SearchType.all: 0,
 SearchType.character: 1,
 SearchType.agent: 2,
 SearchType.corporation: 3,
 SearchType.alliance: 4,
 SearchType.faction: 5}
search_type_setting = CharSettingEnum(settings_key='contacts_window_search_type', default_value=SearchType.all, options=frozenset(SearchType.iter()))
search_by_setting = CharSettingEnum(settings_key='contacts_window_search_by', default_value=MatchBy.partial_terms, options=frozenset((value for _, value in searchUtil.SEARCHBY_OPTIONS)))

class SearchPanel(Container):

    def __init__(self, parent, align):
        self._loaded = False
        self._search_input = None
        self._results_scroll = None
        self._search_lock = locks.Lock()
        super(SearchPanel, self).__init__(parent=parent, align=align)

    def load(self):
        self._loaded = True
        search_cont = Container(parent=self, align=uiconst.TOTOP, height=32, padBottom=16)
        MenuButtonIcon(parent=ContainerAutoSize(parent=search_cont, align=uiconst.TORIGHT, padLeft=8), align=uiconst.CENTER, get_menu_func=self._get_search_settings_menu, texturePath=eveicon.tune, hint=localization.GetByLabel('UI/Common/Settings'))
        self._search_input = SingleLineEditText(parent=search_cont, align=uiconst.TOALL, hintText='Search', OnReturn=self._search)
        self._results_scroll = Scroll(parent=self, align=uiconst.TOALL, pushContent=True)
        search_type_setting.on_change.connect(self._on_search_type_setting_changed)
        search_by_setting.on_change.connect(self._on_search_by_setting_changed)

    def _on_search_type_setting_changed(self, value):
        self._search()

    def _on_search_by_setting_changed(self, value):
        self._search()

    @threadutils.highlander_threaded
    def _search(self):
        with self._search_lock:
            self._results_scroll.ShowLoading()
            try:
                search_string = self._search_input.GetValue().strip()
                if not search_string:
                    return
                scroll_entry_list = searchUtil.GetResultsScrollList(searchStr=search_string, groupIDList=SearchType.as_result_type_list(search_type_setting.get()), searchBy=search_by_setting.get())
                self._results_scroll.LoadContent(contentList=scroll_entry_list, noContentHint='No results')
            finally:
                self._results_scroll.HideLoading()

    @staticmethod
    def _get_search_settings_menu():
        menu = MenuData()
        menu.AddCaption(localization.GetByLabel('UI/Common/SearchType'))
        for search_type in sorted(SearchType.iter(), key=lambda x: SORT_KEY_BY_SEARCH_TYPE[x]):
            menu.AddRadioButton(text=SearchType.display_name(search_type), value=search_type, setting=search_type_setting)

        menu.AddCaption(localization.GetByLabel('UI/Common/SearchBy'))
        for text, search_by in searchUtil.SEARCHBY_OPTIONS:
            menu.AddRadioButton(text=text, value=search_by, setting=search_by_setting)

        return menu

    def OnTabSelect(self):
        if not self._loaded:
            self.load()
