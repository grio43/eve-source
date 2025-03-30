#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\card_section.py
import carbonui
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.base import ReverseScaleDpi
from collections import OrderedDict
import eveicon
import eveui
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
import localization
from mathext import clamp
import uthread2
from jobboard.client import get_job_board_service, job_board_signals
from jobboard.client.ui.card import JobCard

class BaseHorizontalJobCardSection(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_state = eveui.State.normal
    default_clipChildren = True

    def __init__(self, title, icon = None, show_feature = False, hide_empty = True, *args, **kwargs):
        super(BaseHorizontalJobCardSection, self).__init__(*args, **kwargs)
        self._title = title
        self._icon = icon
        self._jobs_by_id = OrderedDict()
        self._show_feature = show_feature
        self._service = get_job_board_service()
        self._hide_empty = hide_empty
        self._scroll_position = 0
        self._cards_container = None
        self._layout()
        self._register()
        self._refresh()

    @uthread2.debounce(0.1)
    def _refresh(self):
        if not self._should_refresh():
            return
        jobs = self._fetch_jobs()
        self._set_jobs(jobs)

    def _should_refresh(self):
        return not self.destroyed

    def _fetch_jobs(self):
        return []

    def Close(self):
        self._unregister()
        super(BaseHorizontalJobCardSection, self).Close()

    def _register(self):
        job_board_signals.on_job_added.connect(self._on_job_added)
        job_board_signals.on_job_removed.connect(self._on_job_removed)

    def _unregister(self):
        job_board_signals.on_job_added.disconnect(self._on_job_added)
        job_board_signals.on_job_removed.disconnect(self._on_job_removed)

    def _on_job_added(self, job):
        job_id = job.job_id
        if job_id not in self._jobs_by_id:
            self._refresh()

    def _on_job_removed(self, job):
        job_id = job.job_id
        if job_id in self._jobs_by_id:
            self._refresh()

    def _set_jobs(self, jobs):
        self._jobs_by_id = OrderedDict()
        for job in jobs:
            self._jobs_by_id[job.job_id] = job

        self._reconstruct_cards()

    def _reconstruct_cards(self):
        self._construct_cards_container()
        self._construct_cards()

    def _scroll_left(self):
        self._scroll(-1)

    def _scroll_right(self):
        self._scroll(1)

    def _scroll(self, direction):
        max_scroll_position = self._max_scroll_position
        self._scroll_position = clamp(self._scroll_position + direction, 0, max_scroll_position)
        if not self._jobs_by_id or not self._cards_container.children:
            position = 0
        else:
            position = -ReverseScaleDpi(self._cards_container.children[self._scroll_position].displayX)
        eveui.animate(self._cards_container, 'padLeft', position, duration=0.5)
        if self._scroll_position == 0:
            self._navigation.left_button.Disable()
        else:
            self._navigation.left_button.Enable()
        if self._scroll_position == max_scroll_position:
            self._navigation.right_button.Disable()
        else:
            self._navigation.right_button.Enable()

    def UpdateAlignment(self, *args, **kwargs):
        self._update_navigation()
        return super(BaseHorizontalJobCardSection, self).UpdateAlignment(*args, **kwargs)

    @property
    def _max_scroll_position(self):
        return max(0, len(self._cards_container.children) - 1)

    @uthread2.debounce(0.1)
    def _update_navigation(self):
        cards_container_width = self._cards_container.width
        container_width = self.GetAbsoluteSize()[0]
        if cards_container_width <= container_width:
            self._navigation.Hide()
        else:
            self._navigation.Show()
        self._scroll(0)

    def _layout(self):
        top_container = eveui.Container(parent=self, align=eveui.Align.to_top, height=28, padBottom=8)
        self._construct_top_container(top_container)
        self._construct_cards_container()
        loading_wheel = LoadingWheel(parent=self._cards_container, align=eveui.Align.center, width=64, height=64, opacity=0)
        eveui.fade(loading_wheel, 0, 1, duration=2, time_offset=0)

    def _construct_cards_container(self):
        if self._cards_container and not self._cards_container.destroyed:
            self._cards_container.Close()
        self._cards_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, alignMode=eveui.Align.to_left, height=JobCard.default_height)

    def _construct_cards(self):
        for job in self._jobs_by_id.values():
            job.construct_card(parent=self._cards_container, align=eveui.Align.to_left, padRight=16, show_feature=self._show_feature)

        if not self._jobs_by_id:
            if self._hide_empty:
                self.Hide()
            else:
                self._construct_fallback()
                self.Show()
        else:
            self.Show()

    def _construct_fallback(self):
        carbonui.TextHeader(parent=self._cards_container, align=eveui.Align.center, text=localization.GetByLabel('UI/Opportunities/NoOpportunitiesFound'))

    def _construct_top_container(self, parent):
        self._navigation = CategoryNavigation(parent=parent, align=eveui.Align.to_right, padLeft=8, on_left=self._scroll_left, on_right=self._scroll_right)
        if self._icon:
            icon_container = eveui.Container(parent=parent, align=eveui.Align.to_left, width=16, padRight=8)
            eveui.Sprite(parent=icon_container, align=eveui.Align.center_left, texturePath=self._icon, height=16, width=16, color=carbonui.TextColor.NORMAL)
        label_container = eveui.ContainerAutoSize(parent=parent, align=eveui.Align.to_left, alignMode=eveui.Align.center_left)
        self._title_label = carbonui.TextHeader(parent=label_container, align=eveui.Align.center_left, maxLines=1, text=self._title)


class FeatureCardSection(BaseHorizontalJobCardSection):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_state = eveui.State.normal
    default_clipChildren = True

    def __init__(self, title, icon = None, view_all_callback = None, show_feature = False, hide_empty = True, provider = None, *args, **kwargs):
        self._view_all_callback = view_all_callback
        self._provider = provider
        super(FeatureCardSection, self).__init__(title=title, icon=icon, show_feature=show_feature, hide_empty=hide_empty, *args, **kwargs)

    def _register(self):
        super(FeatureCardSection, self)._register()
        job_board_signals.on_job_provider_state_changed.connect(self._on_job_provider_state_changed)

    def _unregister(self):
        super(FeatureCardSection, self)._unregister()
        job_board_signals.on_job_provider_state_changed.disconnect(self._on_job_provider_state_changed)

    @property
    def _provider_id(self):
        if self._provider:
            return self._provider.PROVIDER_ID

    def _should_refresh(self):
        if not super(FeatureCardSection, self)._should_refresh():
            return False
        elif self._provider.is_hidden:
            self.display = False
            return False
        else:
            return True

    def _fetch_jobs(self):
        return self._service.get_available_jobs(provider_id=self._provider_id)[:10]

    def _on_job_provider_state_changed(self, provider):
        if self._provider_id == provider.PROVIDER_ID:
            self._refresh()

    def _on_job_added(self, job):
        if self._provider_id and self._provider_id != job.provider_id:
            return
        super(FeatureCardSection, self)._on_job_added(job)

    def _construct_cards(self):
        super(FeatureCardSection, self)._construct_cards()
        if self._view_all_callback:
            self._view_all_container.state = eveui.State.normal if len(self._jobs_by_id) else eveui.State.hidden

    def _construct_top_container(self, parent):
        if self._view_all_callback:
            self._view_all_container = eveui.ContainerAutoSize(parent=parent, align=eveui.Align.to_right, padLeft=8, state=eveui.State.hidden)
            eveui.Button(parent=self._view_all_container, state=eveui.State.normal, align=eveui.Align.center_right, variant=carbonui.ButtonVariant.GHOST, density=carbonui.Density.COMPACT, label=localization.GetByLabel('UI/Generic/ViewAll'), func=self._on_view_all_clicked)
        super(FeatureCardSection, self)._construct_top_container(parent)

    def _on_view_all_clicked(self, *args, **kwargs):
        self._view_all_callback()


class RelatedJobCardSection(BaseHorizontalJobCardSection):

    def __init__(self, job, *args, **kwargs):
        self._job = job
        self._job_relevance_profile = self._job.get_relevance_profile()
        super(RelatedJobCardSection, self).__init__(*args, **kwargs)

    def _fetch_jobs(self):
        jobs = self._service.get_related_jobs(self._job_relevance_profile)[:11]
        try:
            jobs.remove(self._job)
        except:
            pass

        return jobs

    def _on_job_added(self, job):
        if not job.is_available_in_browse:
            return
        score = self._job_relevance_profile.calculate_relevance_score(job.content_tag_ids, job.solar_system_id)
        if score == 0:
            return
        super(RelatedJobCardSection, self)._on_job_added(job)


class CategoryNavigation(eveui.Container):
    default_width = 40

    def __init__(self, on_left, on_right, *args, **kwargs):
        super(CategoryNavigation, self).__init__(*args, **kwargs)
        self._on_left = on_left
        self._on_right = on_right
        self._layout()

    def _layout(self):
        self.left_button = ButtonIcon(parent=self, align=eveui.Align.center_left, width=16, iconSize=16, texturePath=eveicon.caret_left, func=self._click_left)
        self.right_button = ButtonIcon(parent=self, align=eveui.Align.center_right, width=16, iconSize=16, texturePath=eveicon.caret_right, func=self._click_right)

    def _click_left(self, *args, **kwargs):
        self._on_left()

    def _click_right(self, *args, **kwargs):
        self._on_right()
