#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\skins\live_data\paginationController.py
import math
from signals import Signal

class BasePaginationController(object):
    num_per_page = None
    _page_num = 0

    def __init__(self):
        self.on_page_num_changed = Signal('on_page_num_changed')

    @property
    def page_num(self):
        return self._page_num

    @page_num.setter
    def page_num(self, value):
        self._page_num = value
        self.on_page_num_changed(value)

    @property
    def initialized(self):
        raise NotImplementedError

    def get_page(self, page_num):
        raise NotImplementedError

    def has_next_page(self):
        raise NotImplementedError

    def has_prev_page(self):
        raise NotImplementedError

    def is_num_pages_known(self):
        raise NotImplementedError

    def has_more_than_one_page(self):
        raise NotImplementedError

    def reset(self, *args, **kwargs):
        raise NotImplementedError

    def clear(self, *args, **kwargs):
        raise NotImplementedError


class PaginationController(BasePaginationController):
    num_pages = 0

    def clear(self, entries, num_per_page = None):
        self.reset(entries, num_per_page)
        self.page_num = 0

    def reset(self, entries, num_per_page = None):
        self.entries = entries
        self.num_per_page = num_per_page
        if num_per_page is None:
            self.num_pages = 1
            self.num_per_page = len(self.entries)
        else:
            self.num_pages = int(math.ceil(len(entries) / float(num_per_page)))

    def get_page(self, page_num):
        if not self.entries:
            return []
        self._validate_page_exists(page_num)
        self.page_num = page_num
        return self._get_page_entries(page_num)

    def _get_page_entries(self, page_num):
        idx_first = page_num * self.num_per_page
        idx_last = (page_num + 1) * self.num_per_page
        return self.entries[idx_first:idx_last]

    def _validate_page_exists(self, page_num):
        max_page_num = max(0, self.num_pages - 1)
        if page_num > max_page_num:
            raise ValueError('Trying to get page number {} when there are only {}'.format(page_num, max_page_num))

    def is_num_pages_known(self):
        return True

    def has_more_than_one_page(self):
        return self.num_pages > 1

    def has_next_page(self):
        return self.page_num < self.num_pages - 1

    def has_prev_page(self):
        return self.page_num > 0

    @property
    def initialized(self):
        return self.page_num is not None
