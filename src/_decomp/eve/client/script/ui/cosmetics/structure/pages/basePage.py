#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\pages\basePage.py
import eve.client.script.ui.cosmetics.structure.paintToolSelections as paintToolSelections
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui import const as uiconst

class BasePage(Container):
    default_opacity = 0.0

    def __init__(self, page_id, **kw):
        super(BasePage, self).__init__(**kw)
        self._page_id = page_id
        self._construct_layout()
        paintToolSelections.SELECTED_PAGE.on_change.connect(self._on_selected_page_changed)
        self._on_selected_page_changed(paintToolSelections.SELECTED_PAGE.get())

    def Close(self):
        super(BasePage, self).Close()
        paintToolSelections.SELECTED_PAGE.on_change.disconnect(self._on_selected_page_changed)

    def _construct_layout(self):
        raise NotImplementedError

    def _open_page(self):
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, self.opacity, 1.0, 0.25)

    def _close_page(self):
        self.state = uiconst.UI_DISABLED
        animations.FadeTo(self, self.opacity, 0.0, 0.25)

    def _on_selected_page_changed(self, page_id):
        if self._page_id == page_id:
            self._open_page()
        if self._page_id != page_id:
            self._close_page()
