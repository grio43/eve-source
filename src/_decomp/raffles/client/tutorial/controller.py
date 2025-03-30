#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\controller.py
import proper
import signals

class TutorialController(proper.Observable):

    def __init__(self, pages, **kwargs):
        self._pages = pages
        super(TutorialController, self).__init__(**kwargs)
        self.on_closed = signals.Signal(signalName='on_closed')

    @property
    def page_count(self):
        return len(self._pages)

    @proper.ty(default=0)
    def current_page_index(self):
        pass

    @proper.alias
    def current_page(self):
        return self._pages[self.current_page_index]

    @current_page_index.validator
    def __validate_current_page_index(self, current_page_index):
        if len(self._pages) <= current_page_index < 0:
            raise ValueError('current page index out of range')
        return current_page_index

    @proper.alias
    def is_on_last_page(self):
        return self.current_page_index == len(self._pages) - 1

    def next_page(self):
        if self.is_on_last_page:
            self.on_closed()
        else:
            self.current_page_index += 1
