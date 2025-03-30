#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\paginationButtons.py
import eveicon
from carbonui import Align, Density
from carbonui.button import styling
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from localization import GetByLabel
from signals import Signal

class PaginationButtons(ContainerAutoSize):

    def __init__(self, pagination_controller, density = Density.NORMAL, **kw):
        super(PaginationButtons, self).__init__(**kw)
        self.density = density
        self.height = styling.get_height(density)
        self.on_page_selected = Signal('on_page_selected')
        self.pagination_controller = pagination_controller
        self.pagination_controller.on_page_num_changed.connect(self._on_page_num_changed)
        self.first_page_btn = Button(name='first_page_btn', parent=self, align=Align.TOLEFT, func=self.on_first_page_btn, texturePath=eveicon.chevron_left_double, density=self.density, hint=GetByLabel('UI/Common/FirstPage'))
        self.prev_page_btn = Button(name='first_page_btn', parent=self, align=Align.TOLEFT, func=self.on_prev_page_btn, texturePath=eveicon.chevron_left, padLeft=4, density=self.density, hint=GetByLabel('UI/Common/PreviousPage'))
        self.next_page_btn = Button(name='next_page_btn', parent=self, align=Align.TOLEFT, func=self.on_next_page_btn, texturePath=eveicon.chevron_right, padLeft=4, density=self.density, hint=GetByLabel('UI/Common/NextPage'))
        self.update_buttons()

    def _on_page_num_changed(self, page_num):
        self.update_buttons()

    def on_prev_page_btn(self, *args):
        self.on_page_selected(self.pagination_controller.page_num - 1)

    def on_next_page_btn(self, *args):
        self.on_page_selected(self.pagination_controller.page_num + 1)

    def on_first_page_btn(self, *args):
        self.on_page_selected(0)

    def update_buttons(self):
        if self.pagination_controller.page_num > 0:
            self.first_page_btn.Enable()
            self.prev_page_btn.Enable()
        else:
            self.first_page_btn.Disable()
            self.prev_page_btn.Disable()
        if self.pagination_controller.has_next_page():
            self.next_page_btn.Enable()
        else:
            self.next_page_btn.Disable()
