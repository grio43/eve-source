#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\fanfare\picker.py
import eveui
import uthread2

class Picker(eveui.Container):

    def __init__(self, **kwargs):
        super(Picker, self).__init__(**kwargs)
        self._lock_height = self.height
        self._move_height = self.height + 8
        self._layout()

    def move_to(self, left, duration = 0.5):
        if self.height != self._move_height:
            self.unlock()
            uthread2.sleep(0.5)
        eveui.animate(self, 'left', end_value=left, duration=duration)
        uthread2.sleep(duration + 0.1)

    def unlock(self):
        eveui.animate(self, 'height', end_value=self._move_height, duration=0.3)

    def lock_in(self):
        eveui.animate(self, 'height', end_value=self._lock_height, duration=0.1, sleep=True)

    def _layout(self):
        eveui.Line(parent=self, align=eveui.Align.to_top_no_push, color=(0.7, 0.86, 1.0))
        eveui.Line(parent=self, align=eveui.Align.to_bottom_no_push, color=(0.7, 0.86, 1.0))
