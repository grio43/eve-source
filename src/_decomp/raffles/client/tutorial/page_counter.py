#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\page_counter.py
import eveui
import proper

class PageCounter(proper.Observable, eveui.ContainerAutoSize):

    def __init__(self, tutorial_controller, **kwargs):
        self.controller = tutorial_controller
        self._pips = []
        super(PageCounter, self).__init__(**kwargs)
        self._layout()

    def _layout(self):
        for i in range(self.controller.page_count):
            pip = Pip(parent=self, align=eveui.Align.top_left, left=i * 16, tutorial_controller=self.controller, page_index=i)
            self._pips.append(pip)


class Pip(eveui.compatibility.CarbonEventHandler, eveui.Fill):
    default_state = eveui.State.normal
    default_width = 5
    default_height = 5

    def __init__(self, tutorial_controller, page_index, **kwargs):
        self.controller = tutorial_controller
        self.page_index = page_index
        kwargs['color'] = self._get_color()
        super(Pip, self).__init__(**kwargs)
        self.controller.bind(current_page_index=self._on_current_page_index)

    def on_click(self, click_count):
        self.controller.current_page_index = self.page_index

    def _on_current_page_index(self, controller, page_index):
        color = self._get_color()
        eveui.animate(self, 'color', end_value=color, duration=0.3)

    def _get_color(self):
        if self.page_index == self.controller.current_page_index:
            return (0.6, 0.6, 0.6)
        else:
            return (0.2, 0.2, 0.2)
