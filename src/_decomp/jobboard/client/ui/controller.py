#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\controller.py
import signals
import uthread2
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
import localization
from jobboard.client import get_job_board_service, get_primary_feature_tags
from .pages.active_page import ActivePage
from .pages.details_page import DetailsPage
from .pages.browse_page import BrowsePage
from .pages.home_page import HomePage
from .pages.unclaimed_rewards_page import UnclaimedRewardsPage
from .pages.tag_pages import get_content_tag_page

class WindowController(object):

    def __init__(self, **kwargs):
        self.on_page_change = signals.Signal(signalName='on_page_change')
        self._page_controllers = {'home': HomePageController(),
         'browse': BrowsePageController(),
         'active': ActivePageController(),
         'details': DetailsPageController(),
         'feature': FeaturePageController(),
         'unclaimed_rewards': UnclaimedRewardsPageController()}
        self._page_id = 'home'
        self._last_browse_args = (None, None)
        self._history = HistoryBuffer()
        self._history.Append((self._page_id, {}))
        super(WindowController, self).__init__(**kwargs)

    @property
    def page_id(self):
        return self._page_id

    @property
    def page_controller(self):
        return self.get_page_controller(self.page_id)

    def get_page_controller(self, page_id):
        return self._page_controllers.get(page_id, None)

    @property
    def history_label(self):
        return self.page_controller.history_label

    @property
    def is_back_available(self):
        return self._history.IsBackEnabled()

    @property
    def is_forward_available(self):
        return self._history.IsForwardEnabled()

    def close(self):
        pass

    def open_page(self, page_id = None, job_id = None, **kwargs):
        if job_id:
            self._open_details_page(job_id)
        elif page_id == 'browse':
            self.open_browse_page(content_tag_id=kwargs.get('content_tag_id'), keyword=kwargs.get('keyword'))
        elif page_id == 'active':
            self._open_active_page()
        elif page_id == 'home':
            self.open_home_page()
        elif page_id:
            self._change_page(page_id, **kwargs)
        else:
            page_from_cache = settings.char.ui.Get('opportunities_selected_page', None)
            if page_from_cache:
                self._change_page(**page_from_cache)
            else:
                self.open_browse_page()

    def open_browse_page(self, content_tag_id = None, keyword = None):
        if not content_tag_id and not keyword:
            content_tag_id, keyword = self._last_browse_args
            if not content_tag_id and not keyword or content_tag_id and content_tag_id == self.page_controller.primary_content_tag_id:
                self.open_home_page()
                return
        if content_tag_id in get_primary_feature_tags():
            self._change_page('feature', content_tag_id=content_tag_id)
        else:
            self._change_page('browse', content_tag_id=content_tag_id, keyword=keyword)
        self._last_browse_args = (content_tag_id, keyword)

    def open_home_page(self):
        self._last_browse_args = (None, None)
        self._change_page('home')

    def _open_active_page(self):
        self._change_page('active')

    def _open_details_page(self, job_id):
        self._change_page('details', job_id=job_id)

    def go_forward(self):
        if not self.is_forward_available:
            return
        page_id, kwargs = self._history.GoForward()
        self._change_page(page_id, append_history=False, **kwargs)

    def go_back(self):
        if not self.is_back_available:
            return
        page_id, kwargs = self._history.GoBack()
        self._change_page(page_id, append_history=False, **kwargs)

    def _change_page(self, page_id, append_history = True, **kwargs):
        self._page_id = page_id
        self.get_page_controller(page_id).set_page_arguments(**kwargs)
        if append_history:
            self._history.Append((page_id, kwargs))
        selected_page_setting = {'page_id': page_id}
        selected_page_setting.update(kwargs)
        settings.char.ui.Set('opportunities_selected_page', selected_page_setting)
        self.on_page_change(page_id)


class FilteredPageController(object):

    def __init__(self, filter_setting_key = None):
        self.on_filters_changed = signals.Signal(signalName='on_filters_changed')
        self._filter_setting_key = None
        self.keywords = None
        self.content_tag_ids = None
        self.search = ''
        self._update_filter_setting_key(filter_setting_key)

    def construct_page(self, window_controller, **kwargs):
        pass

    @property
    def window_tab_id(self):
        return None

    @property
    def primary_content_tag_id(self):
        return None

    def set_page_arguments(self, **kwargs):
        pass

    @property
    def history_label(self):
        return ''

    def has_filters(self):
        return bool(self.search) or bool(self.keywords) or bool(self.content_tag_ids)

    def get_as_dict(self):
        keywords = set(self.keywords)
        if self.search:
            keywords.add(self.search)
        return {'content_tag_ids': self.content_tag_ids[:],
         'keywords': keywords}

    def set_filters(self, search = '', keywords = None, content_tag_ids = None, send_signal = True, **kwargs):
        self.set_search(search, send_signal=send_signal)
        self.set_keywords(keywords, send_signal=send_signal)
        self.set_content_tags(content_tag_ids, send_signal=send_signal)
        if not send_signal:
            self._save_settings()

    def set_search(self, value, send_signal = True):
        if self.search != value:
            self.search = value
            if send_signal and self.search not in self.keywords:
                self._signal()

    def set_keywords(self, keywords, send_signal = True):
        keywords_set = set(keywords or [])
        if self.keywords != keywords_set:
            self.keywords = keywords_set
            if send_signal:
                self._signal()

    def add_keyword(self, value, send_signal = True):
        if value not in self.keywords:
            self.keywords.add(value)
            if send_signal:
                self._signal()

    def remove_keyword(self, value):
        if value in self.keywords:
            self.keywords.discard(value)
            self._signal()

    def set_content_tags(self, content_tag_ids, send_signal = True):
        content_tags = list(content_tag_ids or [])
        if self.content_tag_ids != content_tags:
            self.content_tag_ids = content_tags
            if send_signal:
                self._signal()

    def add_content_tag(self, content_tag_id, send_signal = True):
        if content_tag_id not in self.content_tag_ids:
            self.content_tag_ids.append(content_tag_id)
            if send_signal:
                self._signal()

    def remove_content_tag(self, content_tag_id, send_signal = True):
        if content_tag_id in self.content_tag_ids:
            self.content_tag_ids.remove(content_tag_id)
            if send_signal:
                self._signal()

    def clear(self, send_signal = True):
        self.search = ''
        self.keywords.clear()
        self.content_tag_ids = []
        if send_signal:
            self._signal()

    @uthread2.debounce(0.1)
    def _signal(self):
        self._save_settings()
        self.on_filters_changed()

    def _save_settings(self):
        settings.char.ui.Set(self._filter_setting_key, self.get_as_dict())

    def _update_filter_setting_key(self, filter_setting_key):
        if self._filter_setting_key == filter_setting_key:
            return
        self._filter_setting_key = filter_setting_key
        filters_in_settings = settings.char.ui.Get(self._filter_setting_key, {})
        self.keywords = set(filters_in_settings.get('keywords', []))
        self.content_tag_ids = list(filters_in_settings.get('content_tag_ids', []))


class HomePageController(object):

    def construct_page(self, window_controller, **kwargs):
        return HomePage(window_controller=window_controller, **kwargs)

    @property
    def window_tab_id(self):
        return 'browse'

    def set_page_arguments(self, **kwargs):
        pass

    @property
    def primary_content_tag_id(self):
        return None

    @property
    def content_tag_ids(self):
        return None

    @property
    def history_label(self):
        return localization.GetByLabel('UI/Opportunities/PageHistoryLabelBrowse')

    def add_content_tag(self, content_tag_id):
        get_job_board_service().open_browse_page(content_tag_id)

    def add_keyword(self, keyword):
        get_job_board_service().open_browse_page(keyword=keyword)


class BrowsePageController(FilteredPageController):

    def __init__(self):
        self._primary_content_tag_id = None
        super(BrowsePageController, self).__init__(filter_setting_key='opportunities_browse_page_filter')

    @property
    def window_tab_id(self):
        return 'browse'

    @property
    def primary_content_tag_id(self):
        if self.content_tag_ids:
            return self.content_tag_ids[0]

    def construct_page(self, window_controller, **kwargs):
        return BrowsePage(window_controller=window_controller, **kwargs)

    def set_page_arguments(self, content_tag_id = None, keyword = None):
        if content_tag_id and content_tag_id == self.primary_content_tag_id:
            return
        self._primary_content_tag_id = content_tag_id
        content_tag_ids = [content_tag_id] if content_tag_id else []
        keywords = [keyword] if keyword else []
        self.set_filters(content_tag_ids=content_tag_ids, keywords=keywords)

    @property
    def history_label(self):
        return localization.GetByLabel('UI/Opportunities/PageHistoryLabelBrowse')

    @uthread2.debounce(0.1)
    def _signal(self):
        if not self.content_tag_ids and not self.keywords:
            get_job_board_service().open_home_page()
        else:
            self._save_settings()
            self.on_filters_changed()


class ActivePageController(FilteredPageController):

    def __init__(self):
        super(ActivePageController, self).__init__(filter_setting_key='opportunities_active_page_filter')

    @property
    def window_tab_id(self):
        return 'active'

    def construct_page(self, window_controller, **kwargs):
        return ActivePage(window_controller=window_controller, **kwargs)

    @property
    def history_label(self):
        return localization.GetByLabel('UI/Opportunities/PageHistoryLabelActive')


class UnclaimedRewardsPageController(FilteredPageController):

    def __init__(self):
        super(UnclaimedRewardsPageController, self).__init__(filter_setting_key='opportunities_unclaimed_rewards_page_filter')

    @property
    def window_tab_id(self):
        return 'unclaimed_rewards'

    def construct_page(self, window_controller, **kwargs):
        return UnclaimedRewardsPage(window_controller=window_controller, **kwargs)

    @property
    def history_label(self):
        return localization.GetByLabel('UI/Opportunities/PageHistoryLabelUnclaimedRewards')


class FeaturePageController(FilteredPageController):

    def construct_page(self, window_controller, **kwargs):
        content_tag_id = self.primary_content_tag_id
        page_class = get_content_tag_page(content_tag_id)
        return page_class(window_controller=window_controller, content_tag_id=content_tag_id, **kwargs)

    @property
    def window_tab_id(self):
        return 'browse'

    @property
    def primary_content_tag_id(self):
        if self.content_tag_ids:
            return self.content_tag_ids[0]

    def set_page_arguments(self, content_tag_id, **kwargs):
        self._update_filter_setting_key('opportunities_{}_filter'.format(content_tag_id))
        if not self.content_tag_ids:
            self.add_content_tag(content_tag_id, send_signal=False)
        elif self.primary_content_tag_id != content_tag_id:
            if content_tag_id in self.content_tag_ids:
                self.content_tag_ids.remove(content_tag_id)
            self.content_tag_ids.insert(0, content_tag_id)

    @property
    def history_label(self):
        return localization.GetByLabel('UI/Opportunities/PageHistoryLabelBrowse')


class DetailsPageController(object):

    def __init__(self):
        self.job_id = None

    @property
    def window_tab_id(self):
        return None

    def construct_page(self, window_controller, **kwargs):
        return DetailsPage(job_id=self.job_id, **kwargs)

    @property
    def primary_content_tag_id(self):
        job = get_job_board_service().get_job(job_id=self.job_id, wait=False)
        if job:
            return job.feature_id

    def set_page_arguments(self, job_id, **kwargs):
        self.job_id = job_id

    @property
    def history_label(self):
        return localization.GetByLabel('UI/Opportunities/PageHistoryLabelDetails')
