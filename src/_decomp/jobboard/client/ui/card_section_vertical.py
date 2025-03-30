#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\card_section_vertical.py
from carbonui import Align, PickState, TextHeader
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from collections import OrderedDict
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eveui.animation import animate, fade
from jobboard.client import get_job_board_service, job_board_signals
from localization import GetByLabel
from mathext import clamp
from uthread2 import debounce

class BaseVerticalJobCardSection(ContainerAutoSize):
    default_align = Align.TOTOP
    default_alignMode = Align.TOTOP
    default_pickState = PickState.ON
    default_clipChildren = True

    def __init__(self, show_feature = False, show_solar_system = True, hide_empty = True, *args, **kwargs):
        super(BaseVerticalJobCardSection, self).__init__(*args, **kwargs)
        self._jobs_by_id = OrderedDict()
        self._show_feature = show_feature
        self._show_solar_system = show_solar_system
        self._service = get_job_board_service()
        self._hide_empty = hide_empty
        self._scroll_position = 0
        self._cards_container = None
        self._layout()
        self._register()
        self._refresh()

    @debounce(0.1)
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
        super(BaseVerticalJobCardSection, self).Close()

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
        animate(self._cards_container, 'padLeft', position, duration=0.5)

    def UpdateAlignment(self, *args, **kwargs):
        self._update_scroll()
        return super(BaseVerticalJobCardSection, self).UpdateAlignment(*args, **kwargs)

    @property
    def _max_scroll_position(self):
        return max(0, len(self._cards_container.children) - 1)

    @debounce(0.1)
    def _update_scroll(self):
        self._scroll(0)

    def _layout(self):
        self._construct_cards_container()
        loading_wheel = LoadingWheel(parent=self._cards_container, align=Align.CENTER, width=64, height=64, opacity=0)
        fade(loading_wheel, 0, 1, duration=2, time_offset=0)

    def _construct_cards_container(self):
        if self._cards_container and not self._cards_container.destroyed:
            self._cards_container.Close()
        self._cards_container = ContainerAutoSize(parent=self, align=Align.TOTOP, alignMode=Align.TOTOP)

    def _construct_cards(self):
        for job in self._jobs_by_id.values():
            job.construct_list_entry(parent=self._cards_container, align=Align.TOTOP, show_feature=self._show_feature, show_solar_system=self._show_solar_system)

        if not self._jobs_by_id:
            if self._hide_empty:
                self.Hide()
            else:
                self._construct_fallback()
                self.Show()
        else:
            self.Show()

    def _construct_fallback(self):
        TextHeader(parent=self._cards_container, align=Align.CENTER, text=GetByLabel('UI/Opportunities/NoOpportunitiesFound'))


class FeatureCardSectionVertical(BaseVerticalJobCardSection):
    default_align = Align.TOTOP
    default_alignMode = Align.TOTOP
    default_pickState = PickState.ON
    default_clipChildren = True

    def __init__(self, show_feature = False, show_solar_system = True, hide_empty = True, provider = None, *args, **kwargs):
        self._provider = provider
        super(FeatureCardSectionVertical, self).__init__(show_feature, show_solar_system, hide_empty, *args, **kwargs)

    def _register(self):
        super(FeatureCardSectionVertical, self)._register()
        job_board_signals.on_job_provider_state_changed.connect(self._on_job_provider_state_changed)

    def _unregister(self):
        super(FeatureCardSectionVertical, self)._unregister()
        job_board_signals.on_job_provider_state_changed.disconnect(self._on_job_provider_state_changed)

    @property
    def _provider_id(self):
        if self._provider:
            return self._provider.PROVIDER_ID

    def _should_refresh(self):
        if not super(FeatureCardSectionVertical, self)._should_refresh():
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
        super(FeatureCardSectionVertical, self)._on_job_added(job)
