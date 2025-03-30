#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\pages\base_page.py
import uthread2
import eveui
from carbonui import Align
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from carbonui.util.various_unsorted import GetWindowAbove
from jobboard.client import get_job_board_service, job_board_signals

class BasePage(eveui.Container):
    default_align = eveui.Align.to_all

    def __init__(self, **kwargs):
        super(BasePage, self).__init__(**kwargs)
        self._init_services()
        self._is_dirty = False
        self._layout()
        self._register()

    def _init_services(self):
        self._service = get_job_board_service()

    def Close(self):
        self._unregister()
        super(BasePage, self).Close()

    def _register(self):
        job_board_signals.on_job_window_maximized.connect(self._on_window_maximized)

    def _unregister(self):
        job_board_signals.on_job_window_maximized.disconnect(self._on_window_maximized)

    def OnSessionChanged(self, _is_remote, _session, change):
        if 'solarsystemid2' in change:
            self._is_dirty = True
            self._try_reconstruct()

    def _on_window_maximized(self):
        self._try_reconstruct()

    def _try_reconstruct(self):
        if not self._is_dirty:
            return
        if self.IsVisible():
            self._is_dirty = False
            self._reconstruct_content()

    @eveui.skip_if_destroyed
    def _reconstruct_content(self):
        self._content_container.Flush()
        uthread2.start_tasklet(self._construct_content)

    def _layout(self):
        self._construct_base_containers()
        self._construct_header()
        self._construct_filters()
        uthread2.start_tasklet(self._construct_content)

    def _construct_filters(self):
        pass

    def _construct_base_containers(self):
        self._main_container = eveui.Container(name='main_container', parent=self, align=eveui.Align.to_all)
        self._scroll_container = eveui.ScrollContainer(name='scroll_container', parent=self._main_container, align=eveui.Align.to_all)
        self._header_container = eveui.ContainerAutoSize(name='header_container', parent=self._scroll_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        self._filters_container = eveui.ContainerAutoSize(name='filters_container', parent=self._scroll_container, align=Align.TOTOP_STICKY, alignMode=Align.TOTOP_STICKY)
        self._filters_container_bg = BlurredSceneUnderlay(bgParent=self._filters_container, display=False)
        self._content_container = eveui.ContainerAutoSize(name='content_container', parent=self._scroll_container, align=Align.TOTOP)

    def _construct_header(self):
        raise NotImplementedError

    def _construct_content(self):
        raise NotImplementedError

    def on_faded_in(self, light_background_enabled):
        if light_background_enabled:
            self._filters_container_bg.EnableLightBackground(animate=False)
        else:
            self._filters_container_bg.DisableLightBackground(animate=False)
        self._filters_container_bg.display = True
