#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\page\stack.py
import functools
import uthread2
from carbonui.primitives.container import Container

class PageStack(Container):
    default_clipChildren = True

    def __init__(self, start_page = None, **kwargs):
        self._pages = []
        super(PageStack, self).__init__(**kwargs)
        if start_page:
            self._pages.append(start_page)
            self._load_page(start_page)
            start_page.show_immediately()

    def push_page(self, page):
        if self._pages:
            current_page = self._pages[-1]
            current_page.disable()
            current_page.on_back.disconnect(self.pop_page)
            current_page.animate_pushed_out(functools.partial(self._unload_page, current_page))
        page.on_back.connect(self.pop_page)
        self._pages.append(page)
        self._load_page(page)
        page.animate_pushed_in(page.enable)

    def pop_page(self):
        current_page = self._pages.pop()
        current_page.disable()
        current_page.on_back.disconnect(self.pop_page)
        current_page.animate_popped_out(functools.partial(self._unload_page, current_page))
        if self._pages:
            page = self._pages[-1]
            if len(self._pages) > 1:
                page.on_back.connect(self.pop_page)
            self._load_page(page)
            page.animate_popped_in(page.enable)

    def _load_page(self, page):
        page.SetParent(self)
        uthread2.start_tasklet(page.load)

    def _unload_page(self, page):
        page.SetParent(None)
        uthread2.start_tasklet(page.unload)
