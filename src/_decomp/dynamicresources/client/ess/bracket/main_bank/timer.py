#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\main_bank\timer.py
from __future__ import division
import math
import chroma
import datetimeutils
import eveui
import localization
import mathext
import trinity
import uthread2
from carbonui import uiconst
from carbonui.uianimations import animations
from dynamicresources.client import color
from dynamicresources.client.ess.bracket.space_container import EssSpaceContainer
from dynamicresources.client.ess.bracket.timer_indicator import TimerIndicator
from dynamicresources.client.service import get_dynamic_resource_service
from eve.client.script.ui.control.gaugeCircular import GaugeCircular

class HackingTimer(object):
    dash_size_factor = 20.0

    def __init__(self, camera, ess_root_transform, link_state, radius, line_width, offset_y = 0.0, scale = 1.0):
        self._link_state = link_state
        self._radius = radius
        self._line_width = line_width
        self._offset_y = offset_y
        self._root_transform = ess_root_transform
        self._scale = scale
        self._camera = camera
        self._y_transform = trinity.EveTransform()
        self._y_transform.name = 'main_bank_timer'
        self._y_transform.translation = (0, self._offset_y, 0)
        self._root_transform.children.append(self._y_transform)
        self._space_cont = EssSpaceContainer(transform=self._y_transform, width=(self._radius + self._line_width) * 2, height=(self._radius + self._line_width) * 2, scale=scale)
        self._indicator_transform = trinity.EveTransform()
        self._y_transform.children.append(self._indicator_transform)
        self._indicator = TimerIndicator(name='main_bank_timer_indicator', transform=self._indicator_transform, width=512, height=512, scale=scale / 2.0, color=color.main_bank.rgba, on_update=self._on_timer_indicator_update, visible=False)
        self._timer = GaugeCircular(parent=self._space_cont.content, align=uiconst.CENTER, radius=self._radius, lineWidth=self._line_width, colorEnd=color.main_bank.rgba, colorStart=color.main_bank.rgba, showMarker=False, startAngle=math.pi, colorBg=chroma.Color.from_any(color.neutral).with_alpha(0.5).rgba)
        uthread2.start_tasklet(self._timer_update_loop)
        uthread2.start_tasklet(self._timer_blink_loop)

    @property
    def link_state(self):
        service = get_dynamic_resource_service()
        provider = service.ess_state_provider
        if provider.state.main_bank.link is not None:
            self._link_state = provider.state.main_bank.link
        return self._link_state

    @property
    def dash_count(self):
        return int(mathext.ceil(self.link_state.duration.total_seconds() / 60.0))

    def play_enter_animation(self):
        animations.MorphScalar(self._space_cont, 'offset_y', startVal=-1000, endVal=0, duration=0.7, curveType=uiconst.ANIM_SMOOTH)
        animations.FadeTo(self._space_cont, startVal=0.0, endVal=1.0, duration=0.4, timeOffset=0.3)
        self._indicator.show(time_offset=0.7)

    def play_exit_animation(self, sleep = False):
        self._indicator.hide()
        animations.BlinkOut(self._space_cont, sleep=sleep)

    def close(self):
        self._space_cont.Close()
        self._indicator.Close()
        self._root_transform.children.fremove(self._y_transform)

    def _timer_update_loop(self):
        while not self._timer.destroyed:
            eveui.wait_for_next_frame()
            progress = self.link_state.remaining.total_seconds() / self.link_state.duration.total_seconds()
            self._timer.value = progress
            angle = math.radians(mathext.lerp(0, 360, progress))
            radius = self._radius / (self._radius + self._line_width)
            self._indicator_transform.translation = (-mathext.cos(angle) * radius * self._scale / 2.0, 0, -mathext.sin(angle) * radius * self._scale / 2.0)
            distance = self._camera.distance_from_transform(self._indicator_transform)
            distance_fraction = max(distance - 10000.0, 0.0) / 100000.0
            self._indicator.scale = mathext.lerp(self._scale / 2.0, self._scale + 18000.0, distance_fraction)
            self._indicator.opacity = self._space_cont.content.opacity

    def _timer_blink_loop(self):
        while not self._timer.destroyed:
            if self.link_state is None:
                eveui.wait_for_next_frame()
                continue
            progress = 1.0 - self.link_state.remaining.total_seconds() / self.link_state.duration.total_seconds()
            if progress > 0.75:
                t = (progress - 0.75) / 0.25
                duration = mathext.lerp(1.0, 0.2, t)
                animations.FadeTo(self._timer, startVal=1.0, endVal=0.3, duration=duration, curveType=uiconst.ANIM_WAVE, sleep=True)
            else:
                eveui.wait_for_next_frame()

    def _on_timer_indicator_update(self, indicator):
        remaining = self.link_state.remaining
        filetime_remaining = datetimeutils.timedelta_to_filetime_delta(remaining)
        text = localization.formatters.FormatTimeIntervalShort(filetime_remaining, showFrom='minute')
        indicator.set_text(text)
        if remaining.total_seconds() <= 0.0:
            indicator.hide()


from dynamicresources.client.ess.bracket.debug import __reload_update__
