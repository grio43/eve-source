#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\page_filters.py
import carbonui
from carbonui.button.menu import MenuButton
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.buttonIcon import ButtonIcon
import eveicon
import eveui
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from jobboard.client import get_primary_feature_tags
from jobboard.client.ui.chip import Chip, ContentTagChip
from jobboard.client.util import sort_content_tags
from jobboard.client.job_board_settings import sort_by_setting, list_view_setting
from metadata import get_content_tags_as_objects
import localization

class PageFilters(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top

    def __init__(self, controller, primary_content_tag_id = None, info_tooltip = '', *args, **kwargs):
        super(PageFilters, self).__init__(*args, **kwargs)
        self._controller = controller
        self._available_content_tags = {}
        self._primary_content_tag_id = primary_content_tag_id
        self._filters_shown = settings.char.ui.Get('opportunitiesFiltersExpanded', False)
        self._info_tooltip = info_tooltip
        self._layout()
        self._list_view_setting_changed()
        list_view_setting.on_change.connect(self._list_view_setting_changed)

    def Close(self):
        list_view_setting.on_change.disconnect(self._list_view_setting_changed)
        super(PageFilters, self).Close()

    def set_job_count(self, count):
        self._label.text = localization.GetByLabel('UI/Opportunities/OpportunitiesAmount', amount=count)

    def set_available_content_tags(self, content_tags):
        current_content_tag_ids = self._controller.content_tag_ids
        available_content_tags = {tag_id:tag for tag_id, tag in content_tags.iteritems() if tag_id not in current_content_tag_ids}
        self._available_content_tags = available_content_tags
        self._update_filter_chips()

    def _list_view_setting_changed(self, *args, **kwargs):
        self._view_button.SetTexturePath(eveicon.grid_view if list_view_setting.get() else eveicon.details_view)

    def _update_filter_chips(self):
        self._filter_chips_container.Flush()
        for keyword in self._controller.keywords:
            Chip(parent=self._filter_chips_container, value=keyword, label=keyword, selected=True, on_click=self._remove_keyword)

        primary_feature_tags = get_primary_feature_tags()
        content_tags = get_content_tags_as_objects(self._controller.content_tag_ids)
        for content_tag in content_tags.itervalues():
            if content_tag.id == self._primary_content_tag_id:
                continue
            ContentTagChip(parent=self._filter_chips_container, selected=True, on_click=self._toggle_content_tag, content_tag=content_tag, show_icon=content_tag.id in primary_feature_tags)

        if self._filters_shown:
            sorted_content_tags = sort_content_tags(self._available_content_tags.values(), important_tags=primary_feature_tags)
            for content_tag in sorted_content_tags:
                ContentTagChip(parent=self._filter_chips_container, on_click=self._toggle_content_tag, content_tag=content_tag, show_icon=content_tag.id in primary_feature_tags)

        self._filter_chips_container.display = bool(self._filter_chips_container.children)
        self._filters_button.texturePath = eveicon.caret_up if self._filters_shown else eveicon.caret_down

    def _toggle_content_tag(self, value):
        if value in self._controller.content_tag_ids:
            self._controller.remove_content_tag(value)
        else:
            self._controller.add_content_tag(value)

    def _remove_keyword(self, value):
        self._controller.remove_keyword(value)

    def _layout(self):
        content_container = eveui.Container(name='content_container', parent=self, align=eveui.Align.to_top, height=24)
        self._view_button = ButtonIcon(parent=content_container, align=eveui.Align.to_right, texturePath=eveicon.details_view, func=self._toggle_list_view)
        self._sort_button = MenuButton(parent=content_container, align=eveui.Align.to_right, label=localization.GetByLabel('UI/Common/SortBy'), texturePath=eveicon.bars_sort_ascending, variant=carbonui.ButtonVariant.GHOST, density=carbonui.Density.COMPACT, get_menu_func=self._get_sort_menu, padLeft=8)
        self._filters_button = eveui.Button(parent=content_container, align=eveui.Align.to_right, label=localization.GetByLabel('UI/Generic/Filters'), texturePath=eveicon.caret_down, func=self._toggle_filters, variant=carbonui.ButtonVariant.GHOST, density=carbonui.Density.COMPACT, padLeft=8)
        self._search_field = eveui.SingleLineEditText(parent=content_container, align=eveui.Align.to_right, width=125, hintText=localization.GetByLabel('UI/Common/Search'), OnReturn=self._search_submitted, icon=eveicon.search)
        self._search_field.GetSuggestions = self._get_search_suggestions
        self._search_field.OnHistoryClick = self._search_submitted
        label_container = eveui.Container(parent=content_container, align=eveui.Align.to_all, clipChildren=True)
        self._label = carbonui.TextHeader(parent=label_container, align=eveui.Align.to_left, maxLines=1, autoFadeSides=16)
        info_tooltip = self._info_tooltip
        if info_tooltip:
            icon_container = eveui.Container(parent=label_container, align=eveui.Align.to_left, width=16, left=8)
            eveui.Sprite(parent=icon_container, state=eveui.State.normal, align=eveui.Align.center, height=16, width=16, texturePath=eveicon.info, color=carbonui.TextColor.NORMAL, hint=info_tooltip)
        self._filter_chips_container = eveui.FlowContainer(name='filter_chips_container', parent=self, align=eveui.Align.to_top, contentSpacing=(8, 8), padTop=8)

    def _toggle_list_view(self, *args, **kwargs):
        list_view_setting.toggle()

    def _toggle_filters(self, *args, **kwargs):
        self._filters_shown = not self._filters_shown
        settings.char.ui.Set('opportunitiesFiltersExpanded', self._filters_shown)
        self._update_filter_chips()

    def _search_submitted(self, *args, **kwargs):
        available_tags = {tag.title:tag.id for tag in self._available_content_tags.values()}
        if self._search_field.text in available_tags:
            self._controller.add_content_tag(available_tags[self._search_field.text])
        else:
            self._controller.add_keyword(self._search_field.text)
        self._search_field.Clear()

    def _clear_filters(self, *args, **kwargs):
        self._controller.clear()

    def _get_search_suggestions(self):
        return [ tag.title for tag in self._available_content_tags.values() ]

    def _get_sort_menu(self):
        m = MenuData()
        m.AddCaption(self.hint)
        m.AddRadioButton(localization.GetByLabel('UI/Opportunities/DefaultSortName'), 'relevance', sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(localization.GetByLabel('UI/Common/Name'), 'name', sort_by_setting)
        m.AddRadioButton(localization.GetByLabel('UI/Inventory/NameReversed'), 'name_reversed', sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(localization.GetByLabel('UI/Corporations/Goals/NumJumps'), 'num_jumps', sort_by_setting)
        m.AddRadioButton(localization.GetByLabel('UI/Corporations/Goals/NumJumpsReversed'), 'num_jumps_reversed', sort_by_setting)
        m.AddSeparator()
        m.AddRadioButton(localization.GetByLabel('UI/Common/TimeRemainingFilter'), 'time_remaining', sort_by_setting)
        m.AddRadioButton(localization.GetByLabel('UI/Common/TimeRemainingReversedFilter'), 'time_remaining_reversed', sort_by_setting)
        return m
