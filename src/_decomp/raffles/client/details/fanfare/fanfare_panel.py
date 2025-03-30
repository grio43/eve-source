#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\fanfare\fanfare_panel.py
import trinity
import uthread2
import threadutils
import eveui
from raffles.client import sound, texture
from raffles.client.localization import Text
from .controller import FanfareController
from .ticket import Ticket
from .slot_options import SlotOptions
from .owned_tickets import OwnedTickets
from .item_socket import ItemSocket

class FanfarePanel(eveui.Container):
    default_name = 'FanfarePanel'
    default_state = eveui.State.normal
    default_align = eveui.Align.to_all

    def __init__(self, raffle, on_finish, **kwargs):
        super(FanfarePanel, self).__init__(**kwargs)
        self._controller = FanfareController(raffle)
        self._thread = None
        self._video_thread = None
        self._on_finish = on_finish
        self._layout()
        self._thread = uthread2.start_tasklet(self._animate)

    def Close(self):
        eveui.play_sound(sound.fanfare_loop_stop)
        if self._thread:
            self._thread.kill()
            self._thread = None
        if self._video_thread:
            self._video_thread.kill()
            self._video_thread = None
        super(FanfarePanel, self).Close()

    def _animate(self):
        self._video_thread = uthread2.start_tasklet(self._video_intro)
        eveui.play_sound(sound.fanfare_loop_play)
        self.item_socket.reveal()
        self.ticket.reveal()
        uthread2.sleep(1.5)
        self.skip_button.state = eveui.State.normal
        eveui.fade_in(self.skip_button, duration=0.5)
        decrypting_order = self._controller.get_decrypting_order()
        uthread2.sleep(0.5)
        for index in decrypting_order:
            self.item_socket.highlight()
            self.ticket.highlight(index)
            self.options.show_options(index)
            self.item_socket.decrypt()
            self.ticket.decrypt(index)
            self._controller.decrypt(index)
            self.owned_tickets.decrypt(index)
            uthread2.sleep(1)
            self.options.unselect()
            if self._controller.highlighted_ticket_count == 0:
                self._lose()
                return

        self._finish()

    def _lose(self):
        eveui.play_sound(sound.fanfare_show_full_ticket)
        self.ticket.show_all()
        uthread2.sleep(1)
        self._finish()

    def _video_intro(self):
        eveui.play_sound(sound.fanfare_intro)
        self.background_video.SetVideoPath(path=texture.bg_intro, videoLoop=False)
        uthread2.sleep(0.5)
        self.background_loop_video.SetVideoPath(path=texture.bg_loop, videoLoop=True)
        uthread2.sleep(1.5)
        eveui.fade_out(self.background_video, duration=1)

    def _video_outro(self):
        if self._controller.is_winner:
            eveui.play_sound(sound.fanfare_outro_win)
            path = texture.bg_outro_win
        else:
            eveui.play_sound(sound.fanfare_outro_lose)
            path = texture.bg_outro_lose
        self.background_video.opacity = 0
        self.background_video.SetVideoPath(path=path, videoLoop=False)
        eveui.fade_in(self.background_video, duration=0.5, sleep=True)
        self.background_loop_video.Close()

    def _finish(self):
        self._controller.update_winner_seen()
        eveui.play_sound(sound.fanfare_loop_stop)
        self.skip_button.Hide()
        self.owned_tickets.close()
        self.ticket.close()
        self.options.close()
        if self._video_thread:
            self._video_thread.kill()
        self._video_thread = uthread2.start_tasklet(self._video_outro)
        if self._controller.is_winner:
            uthread2.sleep(2)
            self.item_socket.close()
        else:
            self.item_socket.close()
            uthread2.sleep(0.5)
        self._on_finish()
        self.state = eveui.State.disabled
        eveui.fade_out(self, duration=2, sleep=True)
        self.Close()

    def _skip(self, *args):
        if not self._thread:
            return
        self._thread.kill()
        self._thread = None
        self._finish()

    def _layout(self):
        container = eveui.Container(parent=self, align=eveui.Align.to_all)
        self.item_socket = ItemSocket(parent=container, align=eveui.Align.center, top=-92, type_id=self._controller.type_id, item_id=self._controller.item_id, is_copy=self._controller.is_copy)
        self.ticket = Ticket(parent=container, align=eveui.Align.center, top=70, controller=self._controller)
        self.options = SlotOptions(parent=container, align=eveui.Align.center, top=160, controller=self._controller)
        self.owned_tickets = OwnedTickets(parent=container, align=eveui.Align.center_left, controller=self._controller)
        self.skip_button = eveui.Button(parent=container, state=eveui.State.disabled, align=eveui.Align.bottom_right, label=Text.skip(), func=self._skip, opacity=0)
        video_container = eveui.Container(name='videoContainer', parent=self, align=eveui.Align.center, width=1024, height=716, left=2, top=-20)
        self.background_video = eveui.StreamingVideoSprite(name='bgVideo', parent=video_container, state=eveui.State.disabled, align=eveui.Align.to_all, spriteEffect=trinity.TR2_SFX_COPY, disableAudio=True)
        self.background_loop_video = eveui.StreamingVideoSprite(name='bgLoopVideo', parent=video_container, state=eveui.State.disabled, align=eveui.Align.to_all, disableAudio=True, opacity=0)
