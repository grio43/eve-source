#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\dotted_progress.py
import eveui
import threadutils

class DottedProgress(eveui.FlowContainer):
    default_opacity = 0

    def __init__(self, dot_size = 8, wait_time = 0.0, **kwargs):
        kwargs.setdefault('centerContent', True)
        kwargs.setdefault('contentSpacing', (dot_size, 0))
        kwargs.setdefault('height', dot_size)
        kwargs.setdefault('width', dot_size * 9)
        super(DottedProgress, self).__init__(**kwargs)
        self._wait_time = wait_time
        self._sprites = []
        self._active = False
        for _ in range(5):
            self._sprites.append(eveui.Fill(parent=self, align=eveui.Align.no_align, height=dot_size, width=dot_size, opacity=0))

    def Show(self, *args):
        super(DottedProgress, self).Show(*args)
        if self._active:
            return
        self._show()

    @threadutils.threaded
    def _show(self):
        eveui.fade_in(self, duration=0.1, time_offset=self._wait_time, sleep=True)
        self._active = True
        length = len(self._sprites)
        for i in range(length):
            self._animate(self._sprites[i], i / float(length))

    def Hide(self, *args):
        super(DottedProgress, self).Hide(*args)
        if not self._active:
            return
        self._active = False
        eveui.fade_out(self, duration=0.1)
        for sprite in self._sprites:
            sprite.opacity = 0
            eveui.stop_animation(sprite, 'opacity')

    def _animate(self, sprite, time_offset):
        duration = 1
        eveui.fade(sprite, start_value=0, end_value=1, duration=duration, time_offset=time_offset * duration, curve_type=eveui.CurveType.bounce, loops=-1)
