#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\side_navigation.py
import eveicon
import localization
import uthread2
from carbonui import Align, TextColor
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.sideNavigation import SideNavigation, SideNavigationEntry, SideNavigationSettingsEntry
from jobboard.client import get_job_board_service, job_board_signals, get_primary_feature_tags
from jobboard.client.job_board_settings import get_display_feature_setting
from metadata.common import get_content_tags_as_objects, ContentTags, get_content_tags
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst

class JobBoardSideNavigation(SideNavigation):

    def __init__(self, controller, is_expanded_func, **kwargs):
        super(JobBoardSideNavigation, self).__init__(is_expanded_func, **kwargs)
        self._controller = controller
        self._update_counters()
        self._register()

    def Close(self):
        self._unregister()
        super(JobBoardSideNavigation, self).Close()

    def _register(self):
        job_board_signals.on_content_tag_count_updated.connect(self._on_content_tag_count_updated)
        job_board_signals.on_job_provider_state_changed.connect(self._on_job_provider_state_changed)
        self._controller.on_page_change.connect(self._on_page_change)

    def _unregister(self):
        job_board_signals.on_content_tag_count_updated.disconnect(self._on_content_tag_count_updated)
        job_board_signals.on_job_provider_state_changed.disconnect(self._on_job_provider_state_changed)
        self._controller.on_page_change.disconnect(self._on_page_change)

    def _on_page_change(self, page_id, **kwargs):
        content_tag_id = self._controller.page_controller.primary_content_tag_id
        self.set_entry_selected(content_tag_id)

    @uthread2.debounce(0.2)
    def _on_content_tag_count_updated(self):
        self._update_counters()

    def _on_job_provider_state_changed(self, provider):
        feature_tag = provider.feature_tag
        if feature_tag and feature_tag.id in self._entries:
            self._entries[feature_tag.id].force_hidden(not get_display_feature_setting(feature_tag.id).get())

    def _update_counters(self):
        service = get_job_board_service()
        jobs = service.get_available_jobs()
        self._entries[None].set_value(len(jobs))
        for content_tag_id, entry in self._entries.items():
            if not content_tag_id:
                continue
            entry.set_value(service.get_content_tag_count(content_tag_id))

    def _construct_footer(self):
        entry = JobBoardSettingsEntry(parent=self._footer, padTop=8, is_always_expanded_setting=self.is_always_expanded_setting, on_hover=self._on_entry_hover)
        self._connect_to_expand(entry)

    def _construct_body(self):
        label = localization.GetByLabel('UI/Opportunities/SectionFeatures')
        self.add_header(label)
        self.add_entry(entry_id=None, icon=eveicon.house, text=localization.GetByLabel('UI/Common/All'), on_click=lambda *args: self._controller.open_home_page())
        for content_tag in get_primary_feature_tags().values():
            self._construct_entry(content_tag, hide_empty=True, force_hidden=not get_display_feature_setting(content_tag.id))

        self.add_header(localization.GetByLabel('UI/Opportunities/SectionCareerPaths'))
        career_content_tags = get_content_tags_as_objects([ContentTags.career_path_soldier_of_fortune,
         ContentTags.career_path_enforcer,
         ContentTags.career_path_explorer,
         ContentTags.career_path_industrialist])
        for content_tag in sorted(career_content_tags.values(), key=lambda ct: ct.title):
            self._construct_entry(content_tag)

        self.add_header(localization.GetByLabel('UI/Opportunities/SectionOther'))
        other_content_tags = get_content_tags_as_objects(get_content_tags())
        for content_tag in sorted(other_content_tags.values(), key=lambda ct: ct.title):
            if content_tag.id in self._entries:
                continue
            self._construct_secondary_entry(content_tag)

    def _construct_entry(self, content_tag, hide_icon = False, hide_empty = False, force_hidden = False):
        entry_id = content_tag.id
        icon = content_tag.icon or eveicon.show_info if not hide_icon else None
        text = content_tag.title
        on_click = lambda *args: self._controller.open_browse_page(entry_id)
        self.add_entry(entry_id, text, on_click, icon, hide_empty, force_hidden)

    def _construct_secondary_entry(self, content_tag):
        entry = SecondaryContentTagEntry(name='{}_page_entry'.format(content_tag.id), parent=self._body, icon=eveicon.tag, text=content_tag.title, hide_empty=True, on_click=lambda *args: self._controller.open_browse_page(content_tag.id), on_hover=self._on_entry_hover)
        entry_id = content_tag.id
        self._entries[entry_id] = entry
        self._connect_to_expand(entry)


class SecondaryContentTagEntry(SideNavigationEntry):

    def _update_display_state(self):
        super(SecondaryContentTagEntry, self)._update_display_state()
        self._icon_container.display = self.selected

    def on_expanded_changed(self, expanded, animate = True):
        super(SecondaryContentTagEntry, self).on_expanded_changed(expanded, animate)
        if not expanded and not self.selected:
            self.display = False
        else:
            self._update_display_state()


class JobBoardSettingsEntry(SideNavigationSettingsEntry):

    def _layout(self):
        super(JobBoardSettingsEntry, self)._layout()
        self._settings_button = MenuButtonIcon(parent=self, align=Align.TOLEFT, texturePath=eveicon.settings, hint=localization.GetByLabel('UI/Common/Settings'), opacity=TextColor.NORMAL.opacity, get_menu_func=self._get_settings_menu, uniqueUiName=pConst.UNIQUE_NAME_OPPORTUNITY_FILTERS)

    def _get_settings_menu(self):
        menu = MenuData()
        menu.AddCaption(localization.GetByLabel('UI/Opportunities/DisplayFeatureSettingHeader'))
        for content_tag in get_primary_feature_tags().values():
            menu.AddCheckbox(content_tag.title, setting=get_display_feature_setting(content_tag.id))

        return menu
