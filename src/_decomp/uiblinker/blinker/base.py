#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\blinker\base.py
import abc
import eveui
import threadutils
import trinity
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite

class Blinker(Container):
    __metaclass__ = abc.ABCMeta

    @staticmethod
    @abc.abstractmethod
    def create_for(element, parent):
        pass

    @abc.abstractmethod
    def update_blink_area(self, element):
        pass

    @abc.abstractmethod
    def layout(self, parent):
        pass

    @abc.abstractmethod
    def animate_blink_pulse(self):
        pass

    def __init__(self, parent = None, align = uiconst.TOPLEFT, left = 0, top = 0, width = 0, height = 0):
        self._blink_tasklet = None
        self._obscured = False
        self._obscured_cont = None
        super(Blinker, self).__init__(parent=parent, align=align, left=left, top=top, width=width, height=height)
        self._content = Container(parent=self, align=uiconst.TOALL)
        self.layout(parent=self._content)

    @property
    def blinking(self):
        return self._blink_tasklet is not None

    @property
    def obscured(self):
        return self._obscured

    @obscured.setter
    def obscured(self, value):
        if self._obscured != value:
            self._obscured = value
            self._update_obscured()

    def start(self):
        if self._blink_tasklet is None:
            if self.obscured:
                eveui.fade_in(self._obscured_cont, duration=0.5)
            else:
                eveui.fade_in(self._content, duration=0.5)
            self._blink_tasklet = uthread2.start_tasklet(self._do_blink_loop)

    def stop(self, wait = False):
        if self._blink_tasklet is not None:
            self._blink_tasklet.kill()
            self._blink_tasklet = None
            eveui.fade_out(self._content, duration=0.2)
            if self._obscured:
                eveui.fade_out(self._obscured_cont, duration=0.2)
            if wait:
                uthread2.sleep(0.2)

    @threadutils.threaded
    def close(self):
        self.stop(wait=True)
        self.Close()

    def _do_blink_loop(self):
        while not self.destroyed:
            self.animate_blink_pulse()
            eveui.wait_for_next_frame()

    def _prepare_obscured(self):
        if self._obscured_cont is None:
            self._obscured_cont = Container(parent=self, align=uiconst.TOALL, opacity=0.0)
            flare = Sprite(parent=self._obscured_cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/uiblinker/flare.png', width=547, height=442, blendMode=trinity.TR2_SBM_ADD)
            eveui.fade(flare, start_value=0.1, end_value=0.4, duration=2.0, curve_type=eveui.CurveType.wave, loops=-1)

    def _update_obscured(self):
        if self._obscured:
            self._prepare_obscured()
            if self.blinking:
                eveui.fade_out(self._content, duration=0.1)
            eveui.fade_in(self._obscured_cont, duration=1.0)
        else:
            eveui.fade_out(self._obscured_cont, duration=0.2)
            if self.blinking:
                eveui.fade_in(self._content, duration=0.1)
