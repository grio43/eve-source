#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\locations\search.py
import eveicon
import localization
import locks
import threadutils
from carbonui import uiconst
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import CharSettingEnum
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.button.menu import MenuButtonIcon
from eve.client.script.ui.util import searchUtil
from eve.common.script.search.const import MatchBy, ResultType

class SearchType(object):
    all = 0
    station = 1
    solar_system = 2
    constellation = 3
    region = 4
    structure = 5
    _RESULT_TYPE_BY_SEARCH_TYPE = {station: ResultType.station,
     solar_system: ResultType.solar_system,
     constellation: ResultType.constellation,
     region: ResultType.region,
     structure: ResultType.structure_with_inlined_data}
    _DISPLAY_NAME_BY_SEARCH_TYPE = {all: localization.GetByLabel('UI/Common/Any'),
     station: localization.GetByLabel('UI/Common/LocationTypes/Station'),
     solar_system: localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
     constellation: localization.GetByLabel('UI/Common/LocationTypes/Constellation'),
     region: localization.GetByLabel('UI/Common/LocationTypes/Region'),
     structure: localization.GetByLabel('UI/Common/LocationTypes/Structures')}

    @classmethod
    def as_result_type_list(cls, search_type):
        if search_type == cls.all:
            return [ResultType.station,
             ResultType.solar_system,
             ResultType.constellation,
             ResultType.region,
             ResultType.structure_with_inlined_data]
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
 SearchType.solar_system: 1,
 SearchType.constellation: 2,
 SearchType.region: 3,
 SearchType.station: 4,
 SearchType.structure: 5}
search_type_setting = CharSettingEnum(settings_key='locations_window_search_type', default_value=SearchType.all, options=frozenset(SearchType.iter()))
search_by_setting = CharSettingEnum(settings_key='locations_window_search_by', default_value=MatchBy.partial_terms, options=frozenset((value for _, value in searchUtil.SEARCHBY_OPTIONS)))

class LocationSearchPanel(Container):

    def __init__(self, parent, align):
        self._loaded = False
        self._search_input = None
        self._results_scroll = None
        self._search_lock = locks.Lock()
        super(LocationSearchPanel, self).__init__(parent=parent, align=align)

    def load(self):
        self._loaded = True
        search_cont = Container(parent=self, align=uiconst.TOTOP, height=32, padBottom=16)
        MenuButtonIcon(parent=ContainerAutoSize(parent=search_cont, align=uiconst.TORIGHT, padLeft=8), align=uiconst.CENTER, get_menu_func=self._get_search_settings_menu, texturePath=eveicon.tune, hint=localization.GetByLabel('UI/Common/Settings'))
        self._search_input = SingleLineEditText(parent=search_cont, align=uiconst.TOALL, hintText=localization.GetByLabel('UI/Common/Search'), OnReturn=self._search)
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
