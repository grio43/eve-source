#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\reserve_bank\timer.py
from __future__ import division
import datetime
import math
import datetimeutils
import eveui
import gametime
import localization
import mathext
import threadutils
import trinity
import uthread2
from carbonui import uiconst
from carbonui.primitives.vectorlinetrace import DashedCircle
from carbonui.uianimations import animations
from eve.client.script.ui.control.donutSegment import DonutSegment
from dynamicresources.client import color
from dynamicresources.client.ess.bracket.space_container import EssSpaceContainer
from dynamicresources.client.ess.bracket.timer_indicator import TimerIndicator
from dynamicresources.client.service import get_dynamic_resource_service

class ReserveBankTimer(object):

    def __init__(self, camera, ess_root_transform, offset_y = 0.0, scale = 1.0):
        self._camera = camera
        self._root_transform = ess_root_transform
        self._offset_y = offset_y
        self._scale = scale
        self._y_transform = trinity.EveTransform()
        self._y_transform.name = 'reserve_bank_timer'
        self._y_transform.translation = (0, self._offset_y, 0)
        self._root_transform.children.append(self._y_transform)
        self._space_cont = EssSpaceContainer(transform=self._y_transform, width=1024, height=1024, scale=scale)
        self._timer_indicator_transform = trinity.EveTransform()
        self._y_transform.children.append(self._timer_indicator_transform)
        self._timer_indicator = TimerIndicator(name='reserve_bank_timer_indicator', transform=self._timer_indicator_transform, width=512, height=512, scale=scale / 2.0, color=color.reserve_bank.rgba, on_update=self._on_timer_indicator_update, visible=False)
        service = get_dynamic_resource_service()
        reserve_bank_state = service.ess_state_provider.state.reserve_bank
        pulses_total = reserve_bank_state.pulses_total
        dash_size_factor = mathext.lerp(20.0, 10.0, mathext.clamp(pulses_total / 45.0, 0.0, 1.0))
        self._timer = DashedCircle(parent=self._space_cont.content, align=uiconst.CENTER, radius=464, lineWidth=48, dashCount=pulses_total, startAngle=0, range=math.pi * 2, startColor=color.reserve_bank.rgba, endColor=color.reserve_bank.rgba, dashSizeFactor=dash_size_factor, end=0.0, smoothScale=8)
        DashedCircle(parent=self._space_cont.content, align=uiconst.CENTER, radius=464, lineWidth=48, dashCount=pulses_total, startAngle=0, range=math.pi * 2, startColor=color.neutral.with_alpha(0.5).rgba, endColor=color.neutral.with_alpha(0.5).rgba, dashSizeFactor=dash_size_factor, smoothScale=8)
        self._payment_timer = DonutSegment(parent=self._space_cont.content, align=uiconst.CENTER, colorEnd=color.neutral.rgba, colorStart=color.neutral.rgba, lineWidth=8, startAngle=mathext.pi, radius=511, isClockwise=True)
        DonutSegment(parent=self._space_cont.content, align=uiconst.CENTER, colorEnd=color.neutral.with_alpha(0.5).rgba, colorStart=color.neutral.with_alpha(0.5).rgba, lineWidth=8, startAngle=mathext.pi, radius=511, isClockwise=True)
        self._start_timer_update_loop()

    def close(self):
        self._space_cont.Close()
        self._timer_indicator.Close()
        self._root_transform.children.fremove(self._y_transform)

    def play_enter_animation(self):
        animations.MorphScalar(self._space_cont, 'offset_y', startVal=-1000, endVal=0, duration=0.7, curveType=uiconst.ANIM_SMOOTH)
        animations.FadeTo(self._space_cont.content, startVal=0.0, endVal=1.0, duration=0.4, timeOffset=0.3)
        self._timer_indicator.show(time_offset=0.7)

    def play_exit_animation(self, sleep = False):
        self._timer_indicator.hide()
        animations.BlinkOut(self._space_cont, sleep=sleep)

    def play_pulse_animation(self, pulses_remaining, pulses_total, sleep = False):
        timer_progress = (pulses_remaining + 1) / pulses_total - 1.0 / pulses_total * 0.5
        center_angle = mathext.lerp(0, 360, timer_progress)
        total_gap_sweep = 360.0 / (self._timer.dashSizeFactor + 1.0)
        dash_sweep = (360.0 - total_gap_sweep) / pulses_total
        dash = DashedCircle(parent=self._space_cont.content, align=uiconst.CENTER, radius=464, lineWidth=48, dashCount=1, startAngle=math.radians(center_angle - dash_sweep / 2.0) - math.pi, range=math.radians(dash_sweep), startColor=color.white.rgba, endColor=color.white.rgba, dashSizeFactor=self._timer.dashSizeFactor, idx=0, opacity=0.0)
        animations.FadeOut(self._payment_timer, duration=0.3)

        def move_indicator():
            self._update_timer_indicator(pulses_remaining, pulses_total)
            self._timer_indicator.opacity = 0.0
            animations.FadeIn(self._timer_indicator, duration=0.2, timeOffset=0.8)

        animations.FadeOut(self._timer_indicator, duration=0.2, callback=move_indicator)
        animations.BlinkIn(dash, duration=0.2, sleep=True)
        animations.MorphScalar(self._payment_timer, 'end', startVal=1.0, endVal=self._pulse_progress_at(gametime.now_sim() + datetime.timedelta(seconds=0.5)), duration=0.8)
        animations.BlinkIn(self._payment_timer, duration=0.2)
        self._timer.end = pulses_remaining / pulses_total
        animations.FadeOut(dash, duration=0.5, sleep=sleep, callback=dash.Close)
        if sleep:
            uthread2.sleep(0.3)

    @threadutils.threaded
    def _start_timer_update_loop(self):
        service = get_dynamic_resource_service()
        reserve_bank_state = service.ess_state_provider.state.reserve_bank
        previous_pulses_remaining = reserve_bank_state.pulses_remaining
        pulses_total = reserve_bank_state.pulses_total
        while not self._timer.destroyed:
            reserve_bank_state = service.ess_state_provider.state.reserve_bank
            pulses_remaining = reserve_bank_state.pulses_remaining
            if not pulses_remaining:
                eveui.wait_for_next_frame()
                continue
            if previous_pulses_remaining != pulses_remaining:
                self.play_pulse_animation(pulses_remaining, reserve_bank_state.pulses_total, sleep=True)
                previous_pulses_remaining = pulses_remaining
            self._timer.end = pulses_remaining / pulses_total
            self._payment_timer.end = self._pulse_progress
            self._update_timer_indicator(pulses_remaining, pulses_total)
            eveui.wait_for_next_frame()

    def _update_timer_indicator(self, pulses_remaining, pulses_total):
        timer_progress = pulses_remaining / pulses_total
        total_gap_sweep = 360.0 / (self._timer.dashSizeFactor + 1.0)
        half_gap = total_gap_sweep / pulses_total / 2.0
        angle = math.radians(mathext.lerp(0, 360, timer_progress) - half_gap)
        radius = 0.905
        self._timer_indicator_transform.translation = (-mathext.cos(angle) * radius * self._scale / 2.0, 0, -mathext.sin(angle) * radius * self._scale / 2.0)
        distance = self._camera.distance_from_transform(self._timer_indicator_transform)
        distance_fraction = max(distance - 10000.0, 0.0) / 100000.0
        scale = mathext.lerp(self._scale / 2.0, self._scale + 18000.0, distance_fraction)
        self._timer_indicator.scale = scale
        self._timer_indicator.opacity = self._space_cont.content.opacity

    @property
    def _pulse_remaining_time(self):
        return self._pulse_remaining_time_at(gametime.now_sim())

    def _pulse_remaining_time_at(self, time):
        service = get_dynamic_resource_service()
        reserve_bank_state = service.ess_state_provider.state.reserve_bank
        pulses_remaining = reserve_bank_state.pulses_remaining
        if not pulses_remaining:
            return datetime.timedelta(seconds=0)
        pulse_interval = service.ess_settings.reserve_bank_pulse_interval
        last_pulse_start = reserve_bank_state.last_pulse_start
        remaining = last_pulse_start - time + pulse_interval
        if remaining.total_seconds() < 0:
            remaining = datetime.timedelta(seconds=0)
        return remaining

    @property
    def _pulse_progress(self):
        return self._pulse_progress_at(gametime.now_sim())

    def _pulse_progress_at(self, time):
        service = get_dynamic_resource_service()
        pulse_interval = service.ess_settings.reserve_bank_pulse_interval
        return self._pulse_remaining_time_at(time).total_seconds() / pulse_interval.total_seconds()

    @property
    def _total_remaining_time(self):
        service = get_dynamic_resource_service()
        reserve_bank_state = service.ess_state_provider.state.reserve_bank
        pulses_remaining = reserve_bank_state.pulses_remaining
        if not pulses_remaining:
            return datetime.timedelta(seconds=0)
        pulse_interval = service.ess_settings.reserve_bank_pulse_interval
        remaining = (pulses_remaining - 1) * pulse_interval + self._pulse_remaining_time
        if remaining.total_seconds() < 0:
            remaining = datetime.timedelta(seconds=0)
        return remaining

    def _on_timer_indicator_update(self, indicator):
        remaining = self._total_remaining_time
        filetime_remaining = datetimeutils.timedelta_to_filetime_delta(remaining)
        text = localization.formatters.FormatTimeIntervalShort(filetime_remaining, showFrom='minute')
        indicator.set_text(text)
        if remaining.total_seconds() <= 0.0:
            indicator.hide()


from dynamicresources.client.ess.bracket.debug import __reload_update__
