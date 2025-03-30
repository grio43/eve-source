#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\panel.py
import carbonui
import eveui
import threadutils
import uthread2
from raffles.client import texture
from raffles.client.tutorial.page_counter import PageCounter

class TutorialPanel(eveui.Container):
    default_width = 260
    default_height = 400

    def __init__(self, tutorial_controller, **kwargs):
        self.controller = tutorial_controller
        self._current_page = (self.controller.current_page_index, self.controller.current_page)
        self._current_animation = None
        self._is_updating_page = False
        self._is_page_update_pending = False
        super(TutorialPanel, self).__init__(**kwargs)
        self._layout()
        self.controller.bind(current_page=self._on_current_page)

    @threadutils.threaded
    def _update_current_page(self):
        if self._is_updating_page:
            self._is_page_update_pending = True
            return
        self._is_page_update_pending = False
        self._is_updating_page = True
        try:
            going_forward = True
            if self._current_page is not None:
                current_page_index, current_page = self._current_page
                self._kill_current_animation()
                if current_page_index == self.controller.current_page_index - 1:
                    if current_page.exit_animation is not None:
                        self._play_animation(current_page.exit_animation)
                    else:
                        self._play_animation(self._go_forward_exit_animation)
                elif current_page_index < self.controller.current_page_index:
                    self._play_animation(self._go_forward_exit_animation)
                else:
                    going_forward = False
                    self._play_animation(self._go_back_exit_animation)
            self.button.Disable()
            self._animate_hide_text(forward=going_forward)
            self._animate_hide_button(forward=going_forward)
            uthread2.sleep(0.2)
            page = self.controller.current_page
            self._current_page = (self.controller.current_page_index, page)
            self.caption_label.SetText(page.caption)
            self.text_label.SetText(page.text)
            self.button.SetLabel(page.button_label)
            self._wait_for_current_animation()
            self._animate_show_text(forward=going_forward)
            self._animate_show_button(forward=going_forward)
            uthread2.sleep(0.15)
            self.button.Enable()
            self._play_animation(page.enter_animation)
        finally:
            self._is_updating_page = False

        if self._is_page_update_pending:
            self._update_current_page()

    def _kill_current_animation(self):
        if self._current_animation:
            self._current_animation.kill()

    def _wait_for_current_animation(self):
        if self._current_animation:
            self._current_animation.get()

    def _play_animation(self, animation):
        if self._current_animation:
            self._current_animation.kill()
        self._current_animation = uthread2.start_tasklet(self._play_animation_thread, animation)

    def _play_animation_thread(self, animation):
        try:
            animation(self.top_cont)
        finally:
            self._current_animation = None

    def _go_back_exit_animation(self, container):
        for child in container.children:
            eveui.animate(child, 'left', end_value=child.left + 10, duration=0.2)
            eveui.fade_out(child, duration=child.opacity * 0.2, on_complete=child.Close)

        uthread2.sleep(0.2)

    def _go_forward_exit_animation(self, container):
        for child in container.children:
            eveui.animate(child, 'left', end_value=child.left - 10, duration=0.2)
            eveui.fade_out(child, duration=child.opacity * 0.2, on_complete=child.Close)

        uthread2.sleep(0.2)

    def _animate_hide_text(self, forward = True):
        end_value = -10 if forward else 10
        eveui.animate(self.caption_label, 'left', end_value=end_value, duration=0.15)
        eveui.animate(self.text_label, 'left', end_value=end_value, duration=0.15)
        eveui.fade_out(self.main_cont, duration=0.15)

    def _animate_show_text(self, forward = True):
        start_value = 10 if forward else -10
        eveui.animate(self.caption_label, 'left', start_value=start_value, end_value=0, duration=0.25)
        eveui.animate(self.text_label, 'left', start_value=start_value, end_value=0, duration=0.25)
        eveui.fade_in(self.main_cont, duration=0.25)

    def _animate_hide_button(self, forward = True):
        eveui.fade_out(self.button, duration=0.15)

    def _animate_show_button(self, forward = True):
        eveui.fade_in(self.button, duration=0.25)

    def _on_current_page(self, controller, current_page):
        self._update_current_page()

    def _layout(self):
        eveui.Frame(bgParent=self, texturePath=texture.panel_1_corner, cornerSize=9, color=(0.1, 0.1, 0.1), opacity=0.95)
        self.header_cont = eveui.Container(parent=self, align=eveui.Align.to_top, height=12, padding=(8, 8, 8, 0))
        self.page_counter = PageCounter(parent=self.header_cont, align=eveui.Align.center, tutorial_controller=self.controller)
        eveui.ButtonIcon(parent=self.header_cont, align=eveui.Align.center_right, texture_path='res:/UI/Texture/Shared/DarkStyle/windowClose.png', size=12, on_click=self.controller.on_closed, color=(0.4, 0.4, 0.4))
        self.top_cont = eveui.Container(parent=self, align=eveui.Align.to_top, height=160, padding=(8, 8, 8, 0), clipChildren=True)
        self.footer_cont = eveui.Container(parent=self, align=eveui.Align.to_bottom, height=48)
        self.main_cont = eveui.Container(parent=self, align=eveui.Align.to_all, padding=(24, 8, 24, 0))
        self.button = eveui.Button(parent=self.footer_cont, align=eveui.Align.center, label=self.controller.current_page.button_label, func=self.controller.next_page, args=())
        self.caption_label = carbonui.TextHeader(name='caption_label', parent=self.main_cont, align=eveui.Align.to_top, text=self.controller.current_page.caption, padBottom=8)
        self.text_label = carbonui.TextBody(name='text_label', parent=self.main_cont, align=eveui.Align.to_top, text=self.controller.current_page.text, maxFontSize=15)
        self._play_animation(self.controller.current_page.enter_animation)
