#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\browse\page.py
import math
import random
import time
from carbonui.uianimations import animations
import eveui
import threadutils
import trinity
import uthread2
from raffles.client import sound, texture
from raffles.client.localization import Text
from raffles.client.raffle_card import RaffleCard
from raffles.client.constants import RAFFLES_PER_PAGE
from raffles.client.widget.banner_background import BannerBackground
from raffles.client.widget.dotted_progress import DottedProgress
from raffles.common.errors import RafflesError
from .banner import Banner
from .filter import Filter
FETCH_TIMEOUT = 4.5
TIME_BETWEEN_CARDS = 0.05

class BrowsePage(eveui.Container):
    default_name = 'BrowseRafflesPage'

    def __init__(self, window_controller, background_layer, type_id = None, **kwargs):
        super(BrowsePage, self).__init__(**kwargs)
        self._controller = window_controller.browse_page_controller
        self._navigation = window_controller.navigation_controller
        self._raffles_thread = None
        self._raffle_count = 0
        self._background_layer = background_layer
        self._navigation.current_page_title = Text.page_title_browse()
        if type_id:
            self._controller.filters.reset_filter()
            if type_id == -1:
                self._controller.filters.type_id = None
            else:
                self._controller.filters.type_id = type_id
        self._layout()

    def Close(self):
        if self._raffles_thread:
            self._raffles_thread.kill()
        super(BrowsePage, self).Close()

    def _on_card_filter(self, type_id = None, group_id = None, solar_system_id = None):
        if type_id:
            self._controller.filters.type_id = type_id
        elif group_id:
            self._controller.filters.group_id = group_id
        elif solar_system_id:
            self._controller.filters.solar_system_id = solar_system_id

    def _layout(self):
        BannerBackground(parent=self._background_layer)
        Banner(parent=self)
        body_container = eveui.Container(parent=self, padTop=24)
        self._construct_top(body_container)
        self.loading_indicator = DottedProgress(parent=body_container, align=eveui.Align.center, wait_time=0.7)
        self.error_message_label = eveui.EveCaptionSmall(name='errorMessage', parent=body_container, align=eveui.Align.center, opacity=0)
        self._construct_cards(body_container)

    def _construct_top(self, container):
        self.refresh_button = eveui.Button(name='refreshButton', parent=container, align=eveui.Align.top_right, texturePath=texture.refresh_icon, label=Text.refresh(), func=self._refresh_raffles_handler)
        self.filter = Filter(parent=container, controller=self._controller.filters, on_apply=self._apply_filter_handler, padRight=self.refresh_button.width)

    @threadutils.threaded
    def _construct_cards(self, parent):
        container = eveui.GridContainer(name='cardsContainer', parent=parent, align=eveui.Align.to_top, height=420, padding=(-8, 40, -8, 24))
        container.columns = 4
        container.lines = 3
        self._cards = []
        for _ in range(RAFFLES_PER_PAGE):
            eveui.wait_for_next_frame()
            self._cards.append(RaffleCard(navigation=self._navigation, on_filter=self._on_card_filter, parent=container, padding=8))

        self._get_raffles(from_refresh=False)

    @eveui.skip_if_destroyed
    def _get_raffles(self, from_refresh = True):
        if self._raffles_thread:
            self._raffles_thread.kill()
        self._raffles_thread = uthread2.start_tasklet(self._get_raffles_thread, from_refresh)

    def _get_raffles_thread(self, from_refresh):
        self.error_message_label.opacity = 0
        self.refresh_button.Disable()
        self.loading_indicator.Show()
        fade_out_time = 0
        if self._raffle_count > 0:
            eveui.play_sound(sound.browse_hide_raffles)
            for i in range(RAFFLES_PER_PAGE):
                self._cards[i].turn_off(time_offset=i // 4 * 0.15)

            fade_out_time = time.time() + 0.7
        try:
            result = self._controller.get_raffles(from_refresh)
        except RafflesError as error:
            self._get_failed(Text.unknown_error())
        else:
            self._raffle_count = len(result)
            if self._raffle_count == 0:
                self._get_failed(Text.no_raffles_found_error())
            else:
                sleep_time = fade_out_time - time.time()
                if sleep_time > 0:
                    uthread2.sleep(sleep_time)
                if from_refresh:
                    eveui.play_sound(sound.browse_show_raffles)
                for i, raffle in enumerate(result):
                    self._cards[i].turn_on(raffle, time_offset=i // 4 * 0.05)

        finally:
            self.loading_indicator.Hide()
            uthread2.sleep(0.7)
            self.refresh_button.Enable()

    def _get_failed(self, message):
        eveui.play_sound(sound.browse_no_raffles)
        self.error_message_label.text = message
        self.error_message_label.opacity = 1

    @threadutils.throttled(1)
    def _apply_filter_handler(self, *args, **kwargs):
        self._get_raffles()

    def _refresh_raffles_handler(self, *args, **kwargs):
        self._get_raffles()
