#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\debug\window.py
import contextlib
import datetime
import uuid
from collections import OrderedDict
import datetimeutils
import eveformat
import evelink.client
import eveui
import gametime
import localization
import signals
import uthread2
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from dynamicresources.client.ess.state import EssStateProvider, EssStatus, MainBankLink, MainBankLinkResult
from dynamicresources.client.service import get_dynamic_resource_service

class DebugEssStateProvider(EssStateProvider):

    def __init__(self, provider):
        if isinstance(provider, DebugEssStateProvider):
            raise RuntimeError('Double wrapping!')
        self._suppress_state_update = False
        super(DebugEssStateProvider, self).__init__(provider.state)
        self._real_provider = provider
        self._next_token_id = provider._next_token_id
        self._subscribers = provider._subscribers
        provider._subscribers = OrderedDict()
        self._need_fetch = provider._need_fetch
        self.on_fetch_request = provider.on_fetch_request
        provider.on_fetch_request = signals.Signal()
        self._overrides = {}
        self.history = [self._state]
        self.on_override_changed = signals.Signal()

    @EssStateProvider.state.setter
    def state(self, state):
        if self._real_provider is None:
            raise RuntimeError('Provider has been released')
        if state != self._real_provider.state:
            self.history.append(state)
        self._real_provider.state = state
        old_state = self._state
        self._state = self._override_state(state)
        self.notify_subscribers(old_state, self._state)

    def evolve(self, *args, **kwargs):
        self.state = self._real_provider.state.evolve(*args, **kwargs)

    def _override_state(self, state):
        if '__state__' in self._overrides:
            state = self._overrides['__state__']
        return state.evolve(status=self._overrides.get('status', state.status), in_range=self._overrides.get('in_range', state.in_range), main_bank=state.main_bank.evolve(balance=self._overrides.get('main_bank.balance', state.main_bank.balance), link=self._overrides.get('main_bank.link', state.main_bank.link), link_result=self._overrides.get('main_bank.link_result', state.main_bank.link_result)), reserve_bank=state.reserve_bank.evolve(balance=self._overrides.get('reserve_bank.balance', state.reserve_bank.balance), pulses_total=self._overrides.get('reserve_bank.pulses_total', state.reserve_bank.pulses_total), pulses_remaining=self._overrides.get('reserve_bank.pulses_remaining', state.reserve_bank.pulses_remaining), last_pulse_start=self._overrides.get('reserve_bank.last_pulse_start', state.reserve_bank.last_pulse_start), link_count=self._overrides.get('reserve_bank.link_count', state.reserve_bank.link_count), linked=self._overrides.get('reserve_bank.linked', state.reserve_bank.linked)))

    def release_provider(self):
        provider = self._real_provider
        self._real_provider = None
        provider._next_token_id = self._next_token_id
        provider._subscribers = self._subscribers
        self._subscribers = OrderedDict()
        provider._need_fetch = self._need_fetch
        provider.on_fetch_request = self.on_fetch_request
        self.on_fetch_request = signals.Signal()
        if self.state != provider.state:
            provider.notify_subscribers(self.state, provider.state)
        return provider

    @contextlib.contextmanager
    def atomic_override(self):
        old_suppress = self._suppress_state_update
        self._suppress_state_update = True
        old_overrides = self._overrides.copy()
        try:
            yield
        finally:
            self._suppress_state_update = old_suppress

        self._update_state(old_overrides)

    def set_override(self, path, value):
        old_overrides = self._overrides.copy()
        self._overrides[path] = value
        self._update_state(old_overrides)

    def has_override(self, path):
        return path in self._overrides

    def clear_override(self, path):
        old_overrides = self._overrides.copy()
        del self._overrides[path]
        self._update_state(old_overrides)

    def _update_state(self, old_overrides):
        if self._real_provider is None:
            raise RuntimeError('Provider has been released')
        if self._suppress_state_update:
            return
        old_state = self._state
        self._state = self._override_state(self._real_provider.state)
        self.notify_subscribers(old_state, self._state)
        if old_overrides != self._overrides:
            self.on_override_changed()


class EssStateProviderOverride(object):

    def __init__(self, service):
        self._service = service
        self._wrapper = DebugEssStateProvider(service.ess_state_provider)
        service._ess_state_provider = self._wrapper

    def __del__(self):
        self._service._ess_state_provider = self._wrapper.release_provider()


class EssDebugWindow(Window):
    default_name = 'EssDebugWindow'
    default_windowID = 'ess_debug_window'
    default_caption = 'ESS Debug Window'
    default_width = 300
    default_height = 400
    default_minSize = (default_width, default_height)
    default_left = '__center__'
    default_top = '__center__'

    def __init__(self, **kwargs):
        super(EssDebugWindow, self).__init__(**kwargs)
        self._state_update_token = None
        self._paused = False
        self._state_index = 0
        self._service = get_dynamic_resource_service()
        self._ess_state_provider_override = EssStateProviderOverride(self._service)
        self._is_reserve_bank_lock_overridden = False
        self._on_state_update()
        self.state_provider.on_override_changed.connect(self._redraw)

    @property
    def ess_state(self):
        return self.state_provider.state

    @property
    def state_provider(self):
        provider = self._service.ess_state_provider
        if not isinstance(provider, DebugEssStateProvider):
            raise RuntimeError('EssStateProvider not wrapped')
        return provider

    def Close(self, setClosed = False, *args, **kwargs):
        self._state_update_token = None
        if hasattr(self, '_ess_state_provider_override'):
            del self._ess_state_provider_override
        super(EssDebugWindow, self).Close(setClosed, *args, **kwargs)

    def _on_state_update(self, state = None):
        _, self._state_update_token = self.state_provider.watch(self._on_state_update)
        self._redraw()

    def _pause(self):
        self._paused = True
        self._state_index = len(self.state_provider.history) - 1
        self.state_provider.set_override('__state__', self.state_provider.history[self._state_index])

    def _resume(self):
        self._paused = False
        self.state_provider.clear_override('__state__')

    def _next_history(self):
        if self._state_index < len(self.state_provider.history) - 1:
            self._state_index += 1
            self.state_provider.set_override('__state__', self.state_provider.history[self._state_index])

    def _previous_history(self):
        if self._state_index > 0:
            self._state_index -= 1
            self.state_provider.set_override('__state__', self.state_provider.history[self._state_index])

    def _redraw(self):
        if self.destroyed:
            return
        self.GetMainArea().Flush()
        main = Container(parent=self.GetMainArea(), align=uiconst.TOALL, padding=12)
        change_color = eveColor.CRYO_BLUE
        history_cont = Container(parent=Container(parent=self.GetMainArea(), align=uiconst.TOBOTTOM, height=52, padding=(2, 0, 2, 2), bgColor=(0.0, 0.0, 0.0, 0.3)), align=uiconst.TOALL, padding=(16, 8, 16, 8))
        if not self._paused:
            Button(parent=history_cont, align=uiconst.CENTERLEFT, minHeight=32, sidePadding=16, label='PAUSE', func=self._pause, args=())
            eveLabel.EveLabelMedium(parent=history_cont, align=uiconst.CENTERRIGHT, text='{} updates'.format(len(self.state_provider.history)))
        else:
            Fill(parent=history_cont.parent, align=uiconst.TOLEFT_NOPUSH, width=3, color=change_color)
            Button(parent=history_cont, align=uiconst.CENTERLEFT, minHeight=32, sidePadding=16, label='RESUME', func=self._resume, args=())
            grid = LayoutGrid(parent=history_cont, align=uiconst.CENTERRIGHT, columns=3, cellSpacing=8)
            prev_button = Button(parent=grid, align=uiconst.CENTER, label='PREVIOUS', func=self._previous_history, args=())
            if self._state_index == 0:
                prev_button.Disable()
            eveLabel.EveLabelMedium(parent=grid, align=uiconst.CENTER, text='{} / {}'.format(self._state_index + 1, len(self.state_provider.history)))
            next_button = Button(parent=grid, align=uiconst.CENTER, label='NEXT', func=self._next_history, args=())
            if self._state_index >= len(self.state_provider.history) - 1:
                next_button.Disable()
        left_pad = 21
        value_color = eveColor.BLACK
        state_cont = ContainerAutoSize(parent=main, align=uiconst.TOTOP)

        def field(parent, checked, callback):
            wrap = ContainerAutoSize(parent=parent, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padBottom=8)
            Fill(parent=wrap, align=uiconst.TOLEFT_NOPUSH, left=-10, width=3, color=change_color if checked else (0.2, 0.2, 0.2))
            Checkbox(parent=ContainerAutoSize(parent=wrap, align=uiconst.TOLEFT, minHeight=16), align=uiconst.CENTERTOP, top=1, checked=checked, callback=callback, hint='clear override' if checked else 'override')
            return wrap

        is_status_overridden = self.state_provider.has_override('status')
        status_field = field(parent=state_cont, checked=is_status_overridden, callback=self._on_status_override)
        if is_status_overridden:
            status_cont = LayoutGrid(parent=status_field, align=uiconst.TOTOP, columns=2)
            eveLabel.EveLabelMedium(parent=status_cont, align=uiconst.CENTER, text='The ESS is')
            Combo(parent=status_cont, align=uiconst.CENTER, left=4, options=map(lambda s: (s.name, s), iter(EssStatus)), callback=self._on_status, select=self.ess_state.status)
        else:
            eveLabel.EveLabelMedium(parent=status_field, align=uiconst.TOTOP, text='The ESS is {}'.format(eveformat.bold(eveformat.color(self.ess_state.status.name, value_color))))
        is_range_overridden = self.state_provider.has_override('in_range')
        range_field = field(parent=state_cont, checked=is_range_overridden, callback=self._on_range_override)
        if not is_range_overridden:
            eveLabel.EveLabelMedium(parent=range_field, align=uiconst.TOTOP, text='You are {}'.format(eveformat.bold(eveformat.color('in range' if self.ess_state.in_range else 'out of range', value_color))))
        else:
            range_cont = LayoutGrid(parent=range_field, align=uiconst.TOTOP, columns=2)
            eveLabel.EveLabelMedium(parent=range_cont, align=uiconst.CENTER, text='You are')
            Combo(parent=range_cont, align=uiconst.CENTER, left=4, options=[('in range', True), ('out of range', False)], callback=self._on_range, select=self.ess_state.in_range)
        eveLabel.EveCaptionSmall(parent=state_cont, align=uiconst.TOTOP, text='MAIN BANK', padding=(left_pad,
         16,
         0,
         0))
        eveLabel.EveLabelMedium(parent=state_cont, align=uiconst.TOTOP, text='The balance is {}'.format(eveformat.color(eveformat.isk(self.ess_state.main_bank.balance), value_color)), padding=(left_pad,
         4,
         0,
         16))
        is_link_overridden = self.state_provider.has_override('main_bank.link')
        link_field = field(parent=state_cont, checked=is_link_overridden, callback=self._on_link_override)
        if not self.ess_state.main_bank.link:
            eveLabel.EveLabelMedium(parent=link_field, align=uiconst.TOTOP, text='No one is currently hacking')
        else:
            eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=link_field, align=uiconst.TOTOP), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, text='{} is hacking'.format(eveformat.color(evelink.character_link(self.ess_state.main_bank.link.character_id), value_color)))
            timer_label = eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=link_field, align=uiconst.TOTOP, padding=(0, 4, 0, 4)), align=uiconst.TOTOP)

            def update_time(label, state):
                link = state.main_bank.link
                while not label.destroyed:
                    remaining = link.end - gametime.now_sim()
                    if remaining.total_seconds() > 0:
                        text = '{} remaining'.format(eveformat.color(format_delta_time(remaining), value_color))
                    else:
                        text = 'Completion pending ...'
                    label.SetText(text)
                    eveui.wait_for_next_frame()

            uthread2.start_tasklet(update_time, timer_label, self.ess_state)
            if is_link_overridden:
                button_cont = FlowContainer(parent=ContainerAutoSize(parent=link_field, align=uiconst.TOTOP, padTop=4), align=uiconst.TOTOP, contentSpacing=(4, 4))
                Button(parent=button_cont, align=uiconst.NOALIGN, label='UNLINK', minHeight=32, sidePadding=16, func=self._fail_hack, args=())
                Button(parent=button_cont, align=uiconst.NOALIGN, label='COMPLETE', minHeight=32, sidePadding=16, func=self._succeed_hack, args=())
                Button(parent=button_cont, align=uiconst.NOALIGN, label='+1m', minHeight=32, sidePadding=16, func=self._advance_hack, args=(datetime.timedelta(minutes=1),))
                Button(parent=button_cont, align=uiconst.NOALIGN, label='-1m', minHeight=32, sidePadding=16, func=self._advance_hack, args=(datetime.timedelta(minutes=-1),))
        if not self.ess_state.main_bank.link and self.ess_state.main_bank.link_result:
            link_result = self.ess_state.main_bank.link_result
            character = evelink.character_link(link_result.character_id)
            if link_result.successful:
                text = '{} completed a hack'.format(character)
            else:
                text = '{} disconnected'.format(character)
            eveLabel.EveLabelMedium(parent=link_field, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padding=(0, 4, 0, 4), text=text)
        if is_link_overridden and not self.ess_state.main_bank.link:
            button_cont = FlowContainer(parent=ContainerAutoSize(parent=link_field, align=uiconst.TOTOP, padTop=4), align=uiconst.TOTOP, contentSpacing=(4, 4))
            Button(parent=button_cont, align=uiconst.NOALIGN, label='LINK', func=self._fake_hack, args=())
            Button(parent=button_cont, align=uiconst.NOALIGN, label='LINK (10s)', func=self._fake_hack, args=datetime.timedelta(seconds=10))
        eveLabel.EveCaptionSmall(parent=state_cont, align=uiconst.TOTOP, text='Reserve bank', padding=(left_pad,
         16,
         0,
         0))
        eveLabel.EveLabelMedium(parent=state_cont, align=uiconst.TOTOP, text='The balance is {}'.format(eveformat.color(eveformat.isk(self.ess_state.reserve_bank.balance), value_color)), padding=(left_pad,
         4,
         0,
         4))
        lock_field = field(parent=state_cont, checked=self._is_reserve_bank_lock_overridden, callback=self._on_reserve_bank_lock_override)
        if self.ess_state.reserve_bank.locked:
            eveLabel.EveLabelMedium(parent=lock_field, align=uiconst.TOTOP, text='The bank is {}'.format(eveformat.color('LOCKED', value_color)))
            if self._is_reserve_bank_lock_overridden:
                button_cont = FlowContainer(parent=ContainerAutoSize(parent=lock_field, align=uiconst.TOTOP, padTop=4), align=uiconst.TOTOP, contentSpacing=(4, 4))
                Button(parent=button_cont, align=uiconst.NOALIGN, label='UNLOCK (15m)', func=self._unlock_reserve_bank, args=(15,))
                Button(parent=button_cont, align=uiconst.NOALIGN, label='UNLOCK (45m)', func=self._unlock_reserve_bank, args=(45,))
        else:
            eveLabel.EveLabelMedium(parent=lock_field, align=uiconst.TOTOP, text='{} of {} pulses remaining'.format(eveformat.color(self.ess_state.reserve_bank.pulses_remaining, value_color), eveformat.color(self.ess_state.reserve_bank.pulses_total, value_color)))
            last_pulse_start_label = eveLabel.EveLabelMedium(parent=lock_field, align=uiconst.TOTOP)

            def update_last_pulse_start_label():
                while not last_pulse_start_label.destroyed:
                    last_pulse_start_label.text = 'Pulse started {} ago'.format(eveformat.color(format_delta_time(gametime.now_sim() - self.ess_state.reserve_bank.last_pulse_start), value_color))
                    eveui.wait_for_next_frame()

            uthread2.start_tasklet(update_last_pulse_start_label)
            if self._is_reserve_bank_lock_overridden:
                grid = LayoutGrid(parent=lock_field, align=uiconst.TOTOP, top=4, columns=4, cellSpacing=4)
                decrease_button = Button(parent=grid, fixedwidth=18, label='-', func=self._remove_reserve_bank_link, args=())
                link_count = self.ess_state.reserve_bank.link_count
                linked = self.ess_state.reserve_bank.linked
                if link_count == 0 or link_count == 1 and linked:
                    decrease_button.Disable()
                eveLabel.EveLabelMedium(parent=grid, text=eveformat.color(self.ess_state.reserve_bank.link_count, value_color))
                Button(parent=grid, fixedwidth=18, label='+', func=self._add_reserve_bank_link, args=())
                eveLabel.EveLabelMedium(parent=grid, text='active links')
            else:
                eveLabel.EveLabelMedium(parent=lock_field, align=uiconst.TOTOP, text='{} active links'.format(eveformat.color(self.ess_state.reserve_bank.link_count, value_color)))
            eveLabel.EveLabelMedium(parent=lock_field, align=uiconst.TOTOP, top=4, text='You are {}'.format(eveformat.color('linked' if self.ess_state.reserve_bank.linked else 'not linked', value_color)))
            if self._is_reserve_bank_lock_overridden:
                button_cont = FlowContainer(parent=ContainerAutoSize(parent=lock_field, align=uiconst.TOTOP, padTop=8), align=uiconst.TOTOP, contentSpacing=(4, 4))
                if self.ess_state.reserve_bank.linked:
                    Button(parent=button_cont, align=uiconst.NOALIGN, label='UNLINK', func=self._unlink_from_reserve_bank, args=())
                else:
                    Button(parent=button_cont, align=uiconst.NOALIGN, label='LINK', func=self._link_to_reserve_bank, args=())
                if self.ess_state.reserve_bank.pulses_remaining > 0:
                    Button(parent=button_cont, align=uiconst.NOALIGN, label='PULSE', func=self._pulse_reserve_bank, args=())
                    Button(parent=button_cont, align=uiconst.NOALIGN, label='FINISH', func=self._lock_reserve_bank, args=())

    def _on_status_override(self, checkbox):
        override = bool(checkbox.GetValue())
        if override:
            self.state_provider.set_override('status', self.ess_state.status)
        else:
            self.state_provider.clear_override('status')

    def _on_status(self, combo, key, value):
        self.state_provider.set_override('status', value)

    def _on_range_override(self, checkbox):
        override = bool(checkbox.GetValue())
        if override:
            self.state_provider.set_override('in_range', self.ess_state.in_range)
        else:
            self.state_provider.clear_override('in_range')

    def _on_range(self, combo, key, value):
        self.state_provider.set_override('in_range', value)

    def _on_link_override(self, checkbox):
        override = bool(checkbox.GetValue())
        if override:
            with self.state_provider.atomic_override():
                self.state_provider.set_override('main_bank.link', self.ess_state.main_bank.link)
                self.state_provider.set_override('main_bank.link_result', self.ess_state.main_bank.link_result)
        else:
            with self.state_provider.atomic_override():
                self.state_provider.clear_override('main_bank.link')
                self.state_provider.clear_override('main_bank.link_result')

    def _fake_hack(self, duration = None):
        if duration is None:
            duration = datetime.timedelta(minutes=6)
        start = gametime.now_sim()
        end = start + duration
        self.state_provider.set_override('main_bank.link', MainBankLink(uuid.uuid4(), session.charid, start, end))

    def _fail_hack(self):
        self._finish_hack(successful=False)

    def _succeed_hack(self):
        self._finish_hack(successful=True)

    def _finish_hack(self, successful):
        if self.ess_state.main_bank.link is None:
            return
        link = self.ess_state.main_bank.link
        with self.state_provider.atomic_override():
            self.state_provider.set_override('main_bank.link', None)
            self.state_provider.set_override('main_bank.link_result', MainBankLinkResult(link_id=self.ess_state.main_bank.link.link_id, character_id=link.character_id, successful=successful))

    def _advance_hack(self, delta):
        if self.ess_state.main_bank.link is None:
            return
        link = self.ess_state.main_bank.link
        self.state_provider.set_override('main_bank.link', link.evolve(start=link.start - delta, end=link.end - delta))

    def _on_reserve_bank_lock_override(self, checkbox):
        override = bool(checkbox.GetValue())
        if override:
            self._is_reserve_bank_lock_overridden = True
            with self.state_provider.atomic_override():
                self.state_provider.set_override('reserve_bank.pulses_total', self.state_provider.state.reserve_bank.pulses_total)
                self.state_provider.set_override('reserve_bank.pulses_remaining', self.state_provider.state.reserve_bank.pulses_remaining)
                self.state_provider.set_override('reserve_bank.link_count', self.state_provider.state.reserve_bank.link_count)
                self.state_provider.set_override('reserve_bank.last_pulse_start', self.state_provider.state.reserve_bank.last_pulse_start)
                self.state_provider.set_override('reserve_bank.linked', False)
        else:
            self._is_reserve_bank_lock_overridden = False
            with self.state_provider.atomic_override():
                self.state_provider.clear_override('reserve_bank.pulses_total')
                self.state_provider.clear_override('reserve_bank.pulses_remaining')
                self.state_provider.clear_override('reserve_bank.link_count')
                self.state_provider.clear_override('reserve_bank.last_pulse_start')
                self.state_provider.clear_override('reserve_bank.linked')

    def _unlock_reserve_bank(self, pulses):
        with self.state_provider.atomic_override():
            self.state_provider.set_override('reserve_bank.pulses_total', pulses)
            self.state_provider.set_override('reserve_bank.pulses_remaining', pulses)
            self.state_provider.set_override('reserve_bank.link_count', 0)
            self.state_provider.set_override('reserve_bank.last_pulse_start', gametime.now_sim())

    def _lock_reserve_bank(self):
        with self.state_provider.atomic_override():
            self.state_provider.set_override('reserve_bank.pulses_total', 0)
            self.state_provider.set_override('reserve_bank.pulses_remaining', 0)
            self.state_provider.set_override('reserve_bank.link_count', 0)
            self.state_provider.set_override('reserve_bank.last_pulse_start', None)
            self.state_provider.set_override('reserve_bank.linked', False)

    def _pulse_reserve_bank(self):
        with self.state_provider.atomic_override():
            self.state_provider.set_override('reserve_bank.pulses_remaining', self.state_provider.state.reserve_bank.pulses_remaining - 1)
            self.state_provider.set_override('reserve_bank.last_pulse_start', gametime.now_sim())

    def _add_reserve_bank_link(self):
        self.state_provider.set_override('reserve_bank.link_count', self.state_provider.state.reserve_bank.link_count + 1)

    def _remove_reserve_bank_link(self):
        self.state_provider.set_override('reserve_bank.link_count', self.state_provider.state.reserve_bank.link_count - 1)

    def _link_to_reserve_bank(self):
        with self.state_provider.atomic_override():
            self._add_reserve_bank_link()
            self.state_provider.set_override('reserve_bank.linked', True)

    def _unlink_from_reserve_bank(self):
        with self.state_provider.atomic_override():
            self._remove_reserve_bank_link()
            self.state_provider.set_override('reserve_bank.linked', False)


def format_delta_time(delta_time):
    return localization.formatters.FormatTimeIntervalShortWritten(datetimeutils.timedelta_to_filetime_delta(delta_time), showFrom='hour', showTo='second')


def __reload_update__(old_namespace):
    window = EssDebugWindow.GetIfOpen()
    if window:
        window.Close()
        EssDebugWindow.Open()
