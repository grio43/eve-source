#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\type_browser.py
import eveformat
import eveicon
import evetypes
import threadutils
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import TextColor, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.dragdrop.dragdata import TypeDragData
from carbonui.control.scroll import Scroll
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import _BaseSetting, _CharSettingMixin, CharSettingBool
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.button.menu import MenuButtonIcon
from eve.client.script.ui.util import uix
from eve.common.script.sys import eveCfg
from eveui.autocomplete import get_highlighted_string, ItemTypeProvider
from inventorycommon.const import categoryShip, categoryStructure
from inventorycommon.util import IsShipFittable

class SortBy(object):
    NAME = 1
    TYPE_ID = 2
    BEST_MATCH = 3
    _ALL = (NAME, TYPE_ID, BEST_MATCH)
    _NAME_BY_VALUE = {NAME: 'NAME',
     TYPE_ID: 'TYPE_ID',
     BEST_MATCH: 'BEST_MATCH'}

    @classmethod
    def all(cls):
        return cls._ALL

    @classmethod
    def iter(cls):
        return iter(cls._ALL)

    @classmethod
    def get_name(cls, value):
        return cls._NAME_BY_VALUE[value]


class SortDirection(object):
    ASCENDING = 1
    DESCENDING = 2
    _ALL = (ASCENDING, DESCENDING)
    _NAME_BY_VALUE = {ASCENDING: 'ASCENDING',
     DESCENDING: 'DESCENDING'}

    @classmethod
    def all(cls):
        return cls._ALL

    @classmethod
    def iter(cls):
        return iter(cls._ALL)

    @classmethod
    def get_name(cls, value):
        return cls._NAME_BY_VALUE[value]


class SortSetting(_CharSettingMixin, _BaseSetting):

    def _validate(self, value):
        return isinstance(value, tuple) and len(value) == 2 and value[0] in SortBy.all() and value[1] in SortDirection.all()


fuzzy_search_setting = CharSettingBool(settings_key='type_browser_fuzzy_search', default_value=True)
show_unpublished_types_setting = CharSettingBool(settings_key='type_browser_show_unpublished_types', default_value=True)
sort_setting = SortSetting(settings_key='type_browser_sort', default_value=(SortBy.BEST_MATCH, SortDirection.ASCENDING))
ENTRY_COUNT_MAX = 100

class TypeBrowser(Window):
    default_caption = 'Type Browser'
    default_windowID = 'type_browser'
    default_width = 580
    default_height = 700
    default_minSize = (480, 200)
    _search_field = None
    _results_scroll = None
    _current_search_parameters = None
    _cancellation_token = None
    _searching = False

    def __init__(self, **kwargs):
        super(TypeBrowser, self).__init__(**kwargs)
        self._layout()
        fuzzy_search_setting.on_change.connect(self._on_fuzzy_search_setting_changed)
        show_unpublished_types_setting.on_change.connect(self._on_show_unpublished_types_setting_changed)
        sort_setting.on_change.connect(self._on_sort_setting_changed)
        self._trigger_search()

    def _layout(self):
        top_cont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padBottom=16)
        MenuButtonIcon(parent=ContainerAutoSize(parent=top_cont, align=uiconst.TORIGHT, padLeft=8), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.bars_sort_ascending, get_menu_func=self._get_sort_menu, hint='Sort by')
        MenuButtonIcon(parent=ContainerAutoSize(parent=top_cont, align=uiconst.TORIGHT, padLeft=8), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.tune, get_menu_func=self._get_options_menu, hint='Search options')
        self._search_field = SingleLineEditText(parent=top_cont, align=uiconst.TOTOP, hintText='Search', OnChange=self._on_search_field_text_changed)
        self._search_field.ShowClearButton(icon=eveicon.close, hint='Clear')
        self._results_scroll = Scroll(parent=self.content, align=uiconst.TOALL, rowPadding=1)

    @staticmethod
    def _get_options_menu():
        menu = MenuData()
        menu.AddCheckbox(text='Fuzzy Search', setting=fuzzy_search_setting)
        menu.AddCheckbox(text='Show unpublished types', setting=show_unpublished_types_setting)
        return menu

    @staticmethod
    def _get_sort_menu():
        menu = MenuData()
        menu.AddRadioButton(text='Best match', setting=sort_setting, value=(SortBy.BEST_MATCH, SortDirection.ASCENDING))
        menu.AddSeparator()
        menu.AddRadioButton(text='Name', setting=sort_setting, value=(SortBy.NAME, SortDirection.ASCENDING))
        menu.AddRadioButton(text='Name (reversed)', setting=sort_setting, value=(SortBy.NAME, SortDirection.DESCENDING))
        menu.AddSeparator()
        menu.AddRadioButton(text='Type ID', setting=sort_setting, value=(SortBy.TYPE_ID, SortDirection.ASCENDING))
        menu.AddRadioButton(text='Type ID (reversed)', setting=sort_setting, value=(SortBy.TYPE_ID, SortDirection.DESCENDING))
        return menu

    def _on_search_field_text_changed(self, text):
        self._trigger_search()

    def _on_fuzzy_search_setting_changed(self, value):
        self._trigger_search()

    def _on_show_unpublished_types_setting_changed(self, value):
        self._trigger_search()

    def _on_sort_setting_changed(self, value):
        self._trigger_search()

    def _get_search_parameters(self):
        sort_by, sort_direction = sort_setting.get()
        return SearchParameters(query=self._search_field.GetText(), fuzzy=fuzzy_search_setting.is_enabled(), show_unpublished_types=show_unpublished_types_setting.get(), sort_by=sort_by, sort_direction=sort_direction)

    def _trigger_search(self):
        search_parameters = self._get_search_parameters()
        if self._current_search_parameters == search_parameters:
            return
        self._current_search_parameters = search_parameters
        if self._cancellation_token:
            self._cancellation_token.cancel()
        if not self._searching:
            self._searching = True
            self._results_scroll.ShowLoading()
            self._start_search_loop()

    @threadutils.threaded
    def _start_search_loop(self):
        try:
            parameters = None
            while parameters != self._current_search_parameters:
                parameters = self._current_search_parameters
                self._cancellation_token = CancellationToken()
                if parameters.query:
                    entries = self._get_search_result_entries(search_parameters=parameters, cancellation_token=self._cancellation_token)
                else:
                    entries = get_category_entries(search_parameters=parameters)
                if entries is None or self._cancellation_token.cancelled:
                    continue
                scroll_to_top = bool(parameters.query)
                self._results_scroll.LoadContent(contentList=entries, noContentHint='No results for "{}"'.format(parameters.query), scrolltotop=scroll_to_top)

        finally:
            self._searching = False
            self._results_scroll.HideLoading()

    def _get_search_result_entries(self, search_parameters, cancellation_token):
        try:
            type_id = int(search_parameters.query)
        except ValueError:
            pass
        else:
            if type_id in evetypes.GetTypes():
                return [GetFromClass(TypeEntry, {'label': get_type_entry_label(type_id, evetypes.GetName(type_id)),
                  'type_id': type_id})]

        if search_parameters.fuzzy:
            query = search_parameters.query
            score_function = None
            matcher = None

            def suggestion_key_func(x):
                return -x[0]

        else:
            query = search_parameters.query.lower()

            def score_function(search_query, text):
                index = text.lower().find(search_query.lower())
                if index >= 0:
                    return index

            def matcher(search_query, text):
                index = score_function(search_query, text)
                if index >= 0:
                    return [(index, index + len(search_query))]

            def suggestion_key_func(x):
                return x[0]

        provider = ItemTypeProvider(score_function=score_function, include_unpublished=search_parameters.show_unpublished_types)
        suggestions = list(provider(query=query, previous_suggestions=[]))
        if cancellation_token.cancelled:
            return
        suggestion_count_total = len(suggestions)
        suggestions = sorted(suggestions, key=suggestion_key_func)
        if suggestion_count_total > ENTRY_COUNT_MAX:
            suggestions = suggestions[:ENTRY_COUNT_MAX]
        if search_parameters.sort_by == SortBy.TYPE_ID:

            def key_func(x):
                return x[1].type_id

        elif search_parameters.sort_by == SortBy.BEST_MATCH:
            if search_parameters.fuzzy:

                def key_func(x):
                    return -x[0]

            else:

                def key_func(x):
                    return x[0]

        else:

            def key_func(x):
                return x[1].name.lower()

        reverse = search_parameters.sort_direction == SortDirection.DESCENDING
        suggestions = sorted(suggestions, key=key_func, reverse=reverse)
        entries = [ GetFromClass(TypeEntry, {'label': get_highlighted_string(text=get_type_entry_label(suggestion[1].type_id, suggestion[1].name), query=search_parameters.query, matcher=matcher),
         'type_id': suggestion[1].type_id}) for suggestion in suggestions ]
        if suggestion_count_total > ENTRY_COUNT_MAX:
            entries.append(GetFromClass(Generic, {'label': eveformat.color('+{} more ...'.format(suggestion_count_total - ENTRY_COUNT_MAX), TextColor.SECONDARY)}))
        return entries


def get_category_entries(search_parameters):
    categories = sorted([ (category_id, evetypes.GetCategoryNameByCategory(category_id)) for category_id in evetypes.IterateCategories() if show_unpublished_types_setting.is_enabled() or evetypes.IsCategoryPublishedByCategory(category_id) ], key=lambda x: x[1].lower())
    return [ GetFromClass(ListGroup, {'id': (name, category_id),
     'label': get_category_entry_label(category_id, name),
     'showlen': False,
     'sublevel': 0,
     'BlockOpenWindow': True,
     'state': 'locked',
     'GetSubContent': lambda node, _category_id = category_id: get_group_entries_by_category(_category_id, search_parameters),
     'MenuFunction': get_category_menu}) for category_id, name in categories ]


def get_category_entry_label(category_id, name):
    text = u'{} {}'.format(name, eveformat.color(u'[Category ID: {}]'.format(category_id), TextColor.SECONDARY))
    if not evetypes.IsCategoryPublishedByCategory(category_id):
        text += u' {}'.format(eveformat.color('unpublished', eveColor.WARNING_ORANGE))
    return text


def get_category_menu(node, *args):
    menu = MenuData()
    menu.AddSeparator()
    category_id = node.id[1]
    menu.AddEntry(text='Create all types in this category in my inventory (SHIFT + click to select quantity)', func=lambda : create_item_types_in_category(category_id))
    return menu


def get_group_entries_by_category(category_id, search_parameters):
    groups = sorted([ (group_id, evetypes.GetGroupNameByGroup(group_id)) for group_id in evetypes.GetGroupIDsByCategory(category_id) if show_unpublished_types_setting.is_enabled() or evetypes.IsGroupPublishedByGroup(group_id) ], key=lambda x: x[1].lower())
    return [ GetFromClass(ListGroup, {'id': (name, group_id),
     'label': get_group_entry_label(group_id, name),
     'showlen': False,
     'sublevel': 1,
     'BlockOpenWindow': True,
     'state': 'locked',
     'GetSubContent': lambda node, _group_id = group_id: get_type_entries_by_group(_group_id, search_parameters),
     'MenuFunction': get_group_menu}) for group_id, name in groups ]


def get_group_entry_label(group_id, name):
    text = u'{} {}'.format(name, eveformat.color(u'[Group ID: {}]'.format(group_id), TextColor.SECONDARY))
    if not evetypes.IsGroupPublishedByGroup(group_id):
        text += u' {}'.format(eveformat.color('unpublished', eveColor.WARNING_ORANGE))
    return text


def get_group_menu(node, *args):
    menu = MenuData()
    menu.AddSeparator()
    group_id = node.id[1]
    menu.AddEntry(text='Create all types in this group in my inventory (SHIFT + click to select quantity)', func=lambda : create_item_types_in_group(group_id))
    return menu


def get_type_entries_by_group(group_id, search_parameters):
    if search_parameters.sort_by == SortBy.TYPE_ID:

        def key_func(x):
            return x[0]

    else:

        def key_func(x):
            return x[1].lower()

    reverse = search_parameters.sort_direction == SortDirection.DESCENDING
    types = sorted([ (type_id, evetypes.GetName(type_id)) for type_id in evetypes.GetTypeIDsByGroup(group_id) if show_unpublished_types_setting.is_enabled() or evetypes.IsPublished(type_id) ], key=key_func, reverse=reverse)
    return [ GetFromClass(TypeEntry, {'label': get_type_entry_label(type_id, name),
     'type_id': type_id,
     'sublevel': 2,
     'show_secondary_text': False}) for type_id, name in types ]


def get_type_entry_label(type_id, name):
    text = u'{} {}'.format(name, eveformat.color(u'[Type ID: {}]'.format(type_id), TextColor.SECONDARY))
    if not evetypes.IsPublished(type_id):
        text += u' {}'.format(eveformat.color('unpublished', eveColor.WARNING_ORANGE))
    return text


class SlimTypeEntry(Generic):
    isDragObject = True

    @classmethod
    def GetCopyData(cls, node):
        return evetypes.GetName(node.typeID)

    def GetDragData(self):
        return [TypeDragData(self.sr.node.typeID)]


class TypeEntry(SE_BaseClassCore):
    isDragObject = True
    _icon_cont = None
    _icon = None
    _primary_label = None
    _secondary_label = None

    def Startup(self, *args):
        self._icon_cont = Container(parent=self, align=uiconst.TOLEFT, width=32, padRight=4)
        self._info_icon = InfoIcon(parent=Container(parent=self, align=uiconst.TORIGHT, width=24), align=uiconst.CENTER)
        self._action_cont = ContainerAutoSize(parent=self, align=uiconst.TORIGHT)
        self._secondary_label = eveLabel.EveLabelSmall(parent=Container(parent=self, align=uiconst.TOBOTTOM_PROP, height=0.5), align=uiconst.TOTOP, color=TextColor.SECONDARY)
        self._primary_label = eveLabel.EveLabelMedium(parent=Container(parent=self, align=uiconst.TOALL), align=uiconst.BOTTOMLEFT, autoFadeSides=8)

    def Load(self, node):
        self.sr.node = node
        type_id = node.type_id
        self._load_icon(type_id)
        sub_level = node.get('sublevel', 0)
        self._icon_cont.left = sub_level * 16 + (8 if sub_level > 0 else 0)
        self._info_icon.SetTypeID(type_id)
        self._primary_label.text = node.label
        if node.get('show_secondary_text', True):
            self._secondary_label.parent.display = True
            self._primary_label.align = uiconst.BOTTOMLEFT
            self._secondary_label.text = self._get_secondary_text(type_id)
        else:
            self._secondary_label.parent.display = False
            self._primary_label.align = uiconst.CENTERLEFT
        self._action_cont.Flush()
        ButtonIcon(parent=ContainerAutoSize(parent=self._action_cont, align=uiconst.TORIGHT), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.load, hint='Create this type in my inventory<br><br>Shift+Click: Choose quantity', func=lambda : create_item_type(type_id))
        if can_spawn(type_id):
            enabled = eveCfg.InSpace()
            hint = 'Spawn this type in space<br><br>Shift+Click: Choose quantity'
            if not enabled:
                hint += '<br><br>' + eveformat.color("Unable to spawn types. You're not in space.", TextColor.WARNING)
            spawn_button = ButtonIcon(parent=ContainerAutoSize(parent=self._action_cont, align=uiconst.TORIGHT), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.assemble_ship, hint=hint, func=lambda : spawn_item_type(type_id))
            if not enabled:
                spawn_button.Disable()
        if can_fit(type_id):
            ButtonIcon(parent=ContainerAutoSize(parent=self._action_cont, align=uiconst.TORIGHT), align=uiconst.CENTER, width=24, height=24, iconSize=16, texturePath=eveicon.fitting, hint='Fit this to my ship<br><br>Shift+Click: Choose quantity', func=lambda : fit_item_type(type_id))

    @staticmethod
    def _get_secondary_text(type_id):
        category = evetypes.GetCategoryName(type_id)
        group = evetypes.GetGroupName(type_id)
        return u'{} > {}'.format(category, group)

    def _load_icon(self, type_id):
        if self._icon is None:
            self._icon = ItemIcon(parent=self._icon_cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=32, height=32, typeID=type_id)
        else:
            self._icon.SetTypeID(type_id)

    def GetHeight(self, *args):
        return 32

    def GetMenu(self):
        menu_service = ServiceManager.Instance().GetService('menu')
        return menu_service.GetMenuFromItemIDTypeID(typeID=self.sr.node.type_id, itemID=None)

    @classmethod
    def GetCopyData(cls, node):
        return evetypes.GetName(node.type_id)

    def GetDragData(self):
        return [TypeDragData(self.sr.node.type_id)]


def create_item_type(type_id):
    quantity = 1
    if uicore.uilib.Key(uiconst.VK_SHIFT):
        quantity = choose_quantity(hint='How many {} should we create?'.format(evetypes.GetName(type_id)))
        if quantity is None:
            return
    slash_service = ServiceManager.Instance().GetService('slash')
    return slash_service.SlashCmd('/create {} {}'.format(type_id, quantity))


def create_item_types_in_category(category_id):
    _create_many_types(type_ids=evetypes.GetTypeIDsByCategory(category_id), quantity_prompt_hint='How many of each item type in the {} category should we create?'.format(evetypes.GetCategoryNameByCategory(category_id)))


def create_item_types_in_group(group_id):
    _create_many_types(type_ids=evetypes.GetTypeIDsByGroup(group_id), quantity_prompt_hint='How many of each item type in the {} group should we create?'.format(evetypes.GetGroupNameByGroup(group_id)))


def _create_many_types(type_ids, quantity_prompt_hint):
    quantity = 1
    if uicore.uilib.Key(uiconst.VK_SHIFT):
        quantity = choose_quantity(hint=quantity_prompt_hint)
        if quantity is None:
            return
    slash_service = ServiceManager.Instance().GetService('slash')
    for type_id in type_ids:
        slash_service.SlashCmd('/create {} {}'.format(type_id, quantity))


def can_spawn(type_id):
    category_id = evetypes.GetCategoryID(type_id)
    return is_in_space() and category_id in (categoryShip, categoryStructure)


def is_in_space():
    return session.solarsystemid


def spawn_item_type(type_id):
    quantity = 1
    if uicore.uilib.Key(uiconst.VK_SHIFT):
        quantity = choose_quantity(hint='How many {} should we create?'.format(evetypes.GetName(type_id)))
        if quantity is None:
            return
    slash_service = ServiceManager.Instance().GetService('slash')
    if quantity > 1:
        return slash_service.SlashCmd('/spawnN {} 250 {}'.format(quantity, type_id))
    else:
        return slash_service.SlashCmd('/spawn {}'.format(type_id))


def can_fit(type_id):
    return IsShipFittable(evetypes.GetCategoryID(type_id))


def fit_item_type(type_id):
    quantity = 1
    if uicore.uilib.Key(uiconst.VK_SHIFT):
        quantity = choose_quantity(hint='How many {} would you like to fit to your ship?'.format(evetypes.GetName(type_id)))
        if quantity is None:
            return
    slash_service = ServiceManager.Instance().GetService('slash')
    if quantity > 1:
        return slash_service.SlashCmd('/loop {} /fit me {}'.format(quantity, type_id))
    else:
        return slash_service.SlashCmd('/fit me {}'.format(type_id))


def choose_quantity(hint, min_value = 1, max_value = None):
    result = uix.QtyPopup(minvalue=min_value, maxvalue=max_value, caption='Choose quantity', hint=hint, label=None)
    if result:
        return result['qty']
    else:
        return


class SearchParameters(object):

    def __init__(self, query, fuzzy, show_unpublished_types, sort_by, sort_direction):
        self.query = query
        self.fuzzy = fuzzy
        self.show_unpublished_types = show_unpublished_types
        self.sort_by = sort_by
        self.sort_direction = sort_direction

    def __eq__(self, other):
        return isinstance(other, SearchParameters) and self.query == other.query and self.fuzzy == other.fuzzy and self.show_unpublished_types == other.show_unpublished_types and self.sort_by == other.sort_by and self.sort_direction == other.sort_direction

    def __repr__(self):
        return u'SearchParameters(query={!r}, fuzzy={!r}, show_unpublished_types={!r}, sort_by=SortBy.{}, sort_direction=SortBy{})'.format(self.query, self.fuzzy, self.show_unpublished_types, self.sort_by, self.sort_direction)


class CancellationToken(object):
    _cancelled = False

    @property
    def cancelled(self):
        return self._cancelled

    def cancel(self):
        self._cancelled = True
