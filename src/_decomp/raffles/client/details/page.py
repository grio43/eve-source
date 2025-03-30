#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\page.py
import eveui
import threadutils
from raffles.common.errors import RafflesError
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.widget.banner_background import BannerBackground
from raffles.client.widget.dotted_progress import DottedProgress
from .active_panel import ActivePanel
from .finished_panel import FinishedPanel

class DetailsPage(eveui.Container):
    default_name = 'RafflesDetailsPage'

    def __init__(self, window_controller, raffle_id, background_layer, **kwargs):
        super(DetailsPage, self).__init__(**kwargs)
        self._controller = window_controller.details_page_controller
        self._navigation = window_controller.navigation_controller
        self._raffle = None
        self._background_layer = background_layer
        self.finished_panel = None
        self._get_raffle(raffle_id)
        self._navigation.current_page_title = Text.page_title_details()
        self._update_banner_image()

    def _update_banner_image(self):
        eveui.Sprite(parent=self._background_layer, align=eveui.Align.center_top, texturePath=texture.background_triangles, width=1024, height=716, opacity=0.2)

    @threadutils.threaded
    def _get_raffle(self, raffle_id):
        self.loading_indicator.Show()
        try:
            self._raffle = self._controller.get_raffle(raffle_id)
        except RafflesError as error:
            self._show_error()
        else:
            self._layout()
            self._raffle.subscribe()
            self._raffle.on_status_changed.connect(self._update_layout)
        finally:
            self.loading_indicator.Hide()

    def Close(self):
        super(DetailsPage, self).Close()
        if self._raffle:
            self._raffle.unsubscribe()
            self._raffle.on_status_changed.disconnect(self._update_layout)

    def _handle_back(self, *args, **kwargs):
        self._navigation.on_back()

    def _update_layout(self, *args, **kwargs):
        self.Flush()
        self._layout()

    @eveui.lazy
    def loading_indicator(self):
        return DottedProgress(parent=self, align=eveui.Align.center, wait_time=0.3)

    def _layout(self):
        BannerBackground(parent=self._background_layer)
        if self._raffle.winner_id:
            FinishedPanel(parent=self, raffle=self._raffle, navigation=self._navigation, controller=self._controller)
        else:
            ActivePanel(parent=self, raffle=self._raffle)

    def _show_error(self):
        self.error_message_label = eveui.EveCaptionSmall(name='errorMessage', parent=self, align=eveui.Align.center, opacity=1, text=Text.not_found_error())
