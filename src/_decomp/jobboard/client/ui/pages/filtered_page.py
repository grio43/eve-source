#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\pages\filtered_page.py
import carbonui
from carbonui.primitives.cardsContainer import CardsContainer
import eveui
import threadutils
import uthread2
import localization
from jobboard.client import job_board_signals
from jobboard.client.ui.card import JobCard
from jobboard.client.ui.page_filters import PageFilters
from jobboard.client.ui.pages.base_page import BasePage
from jobboard.client.util import get_content_tags_for_jobs, sort_jobs
from jobboard.client.job_board_settings import sort_by_setting, list_view_setting
from jobboard.client.ui.const import CARD_MAX_WIDTH
MAXIMUM_RENDERED_CARDS = 100

class FilteredPage(BasePage):
    _show_as_rewards = False
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, window_controller, **kwargs):
        self._filters_controller = window_controller.page_controller
        self._job_cards = {}
        self._jobs = []
        self._cards_container = None
        self._show_feature = False
        super(FilteredPage, self).__init__(**kwargs)

    @property
    def primary_content_tag_id(self):
        return None

    @property
    def display_as_list(self):
        return list_view_setting.get()

    @property
    def info_tooltip(self):
        return ''

    def _register(self):
        sm.RegisterNotify(self)
        job_board_signals.on_job_added.connect(self._on_job_added)
        job_board_signals.on_job_removed.connect(self._on_job_removed)
        job_board_signals.on_job_state_changed.connect(self._on_job_state_changed)
        sort_by_setting.on_change.connect(self._sort_changed)
        list_view_setting.on_change.connect(self._list_view_changed)
        self._filters_controller.on_filters_changed.connect(self._on_filters_changed)
        super(FilteredPage, self)._register()

    def _unregister(self):
        sm.UnregisterNotify(self)
        job_board_signals.on_job_added.disconnect(self._on_job_added)
        job_board_signals.on_job_removed.disconnect(self._on_job_removed)
        job_board_signals.on_job_state_changed.disconnect(self._on_job_state_changed)
        sort_by_setting.on_change.disconnect(self._sort_changed)
        list_view_setting.on_change.disconnect(self._list_view_changed)
        self._filters_controller.on_filters_changed.disconnect(self._on_filters_changed)
        super(FilteredPage, self)._unregister()

    @eveui.skip_if_destroyed
    def _reconstruct_content(self):
        self._job_cards.clear()
        super(FilteredPage, self)._reconstruct_content()

    def _on_filters_changed(self):
        if self._cards_container:
            self._reconstruct_content()

    @eveui.skip_if_destroyed
    def _sort_changed(self, *args, **kwargs):
        if self._cards_container:
            self._reconstruct_content()

    @eveui.skip_if_destroyed
    def _list_view_changed(self, *args, **kwargs):
        if self._cards_container:
            self._reconstruct_content()

    @eveui.skip_if_destroyed
    def _on_job_state_changed(self, job):
        self._on_job_added(job)

    @eveui.skip_if_destroyed
    def _on_job_added(self, job):
        job_id = job.job_id
        if job_id not in self._job_cards and self._validate_job(job):
            self._no_jobs_container.display = False
            self._jobs.append(job)
            self._construct_job_card(job)
            self._reorder_cards()
            self._update_available_content_tags()
        self._update_job_count()

    @eveui.skip_if_destroyed
    def _on_job_removed(self, job):
        job_id = job.job_id
        if job_id in self._job_cards:
            job_card = self._job_cards.pop(job_id)
            job_card.Close()
            self._jobs.remove(job)
            if not self._job_cards:
                self._no_jobs_container.display = True
        self._update_job_count()

    @uthread2.debounce(0.1)
    def _reorder_cards(self):
        if self.destroyed or not self._cards_container or self._cards_container.destroyed:
            return
        self._jobs = sort_jobs(self._jobs)
        sorted_jobs = self._get_sorted_jobs()
        for index, job in enumerate(sorted_jobs):
            if job.job_id in self._job_cards:
                self._job_cards[job.job_id].SetOrder(index)

    def _get_jobs(self):
        return self._service.get_jobs(filters=self._filters_controller.get_as_dict())

    def _validate_job(self, job):
        return job.check_filters(**self._filters_controller.get_as_dict())

    def _construct_base_containers(self):
        super(FilteredPage, self)._construct_base_containers()
        self._no_jobs_container = eveui.ContainerAutoSize(name='no_jobs_container', parent=self._content_container, align=eveui.Align.to_top, display=False)
        carbonui.TextHeader(name='no_jobs_container_header', parent=self._no_jobs_container, align=eveui.Align.center, text=localization.GetByLabel('UI/Opportunities/NoOpportunitiesFound'))

    def _construct_header(self):
        pass

    def _construct_filters(self):
        self._filters_section = PageFilters(parent=self._filters_container, controller=self._filters_controller, primary_content_tag_id=self.primary_content_tag_id, info_tooltip=self.info_tooltip, padBottom=16)

    def _construct_content(self):
        self._no_jobs_container.display = False
        if self.display_as_list:
            self._cards_container = eveui.ContainerAutoSize(parent=self._content_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        else:
            self._cards_container = CardsContainer(parent=self._content_container, align=eveui.Align.to_top, cardHeight=JobCard.default_height, cardMaxWidth=self.card_max_width, contentSpacing=(16, 16))
        self._jobs = self._get_jobs()
        sorted_jobs = self._get_sorted_jobs()[:MAXIMUM_RENDERED_CARDS]
        self._update_available_content_tags()
        self._update_job_count()
        feature_ids = set()
        for job in sorted_jobs:
            feature_ids.add(job.feature_id)

        if len(feature_ids) > 1:
            self._show_feature = True
        elif len(feature_ids) == 1 and list(feature_ids)[0] not in self._filters_controller.content_tag_ids:
            self._show_feature = True
        else:
            self._show_feature = False
        if sorted_jobs:
            for job in threadutils.be_nice_iter(30, sorted_jobs):
                self._construct_job_card(job)

        else:
            self._no_jobs_container.display = True

    def _update_job_count(self):
        self._filters_section.set_job_count(len(self._jobs))

    def _update_available_content_tags(self):
        self._filters_section.set_available_content_tags(get_content_tags_for_jobs(self._jobs))

    def _get_sorted_jobs(self):
        sort_by = sort_by_setting.get()
        if sort_by == 'name':
            return sorted(self._jobs, key=lambda job: job.title.lower())
        elif sort_by == 'name_reversed':
            return sorted(self._jobs, key=lambda job: job.title.lower(), reverse=True)
        elif sort_by == 'num_jumps':
            return sorted(self._jobs, key=lambda job: job.jumps)
        elif sort_by == 'num_jumps_reversed':
            return sorted(self._jobs, key=lambda job: job.jumps, reverse=True)
        elif sort_by == 'time_remaining':
            return sorted(self._jobs, key=lambda job: (job.expiration_time is None, job.expiration_time))
        elif sort_by == 'time_remaining_reversed':
            return sorted(self._jobs, key=lambda job: (job.expiration_time is None, job.expiration_time), reverse=True)
        else:
            return self._jobs

    def _construct_job_card(self, job):
        list_view = self.display_as_list
        if self._cards_container and not self._cards_container.destroyed and job.job_id not in self._job_cards:
            card = job.construct_entry(list_view=list_view, parent=self._cards_container, show_feature=self._show_feature)
            self._job_cards[job.job_id] = card

    @property
    def card_max_width(self):
        return CARD_MAX_WIDTH
