#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\page\select.py
import functools
import logging
import datetime
import carbonui.control.button
import datetimeutils
import localization
import signals
import threadutils
import uthread2
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control import buttons, eveLabel, eveLoadingWheel, itemIcon
from homestation.client import text
from homestation.client.error import handle_change_home_station_validation_error
from homestation.client.prompt import prompt_set_home_station_remotely
from homestation.client.ui import info_card
from homestation.client.ui.const import BIG_BUTTON_HEIGHT, PAGE_WIDTH_MAX, Padding, TextColor
from homestation.client.ui.header import Header
from homestation.client.ui.page.base import Page
from homestation.client.ui.tooltip import load_error_tooltip
from homestation.validation import ChangeHomeStationValidationError
log = logging.getLogger(__name__)

class StateError(Exception):
    pass


class State(object):
    initial = 0
    loading = 1
    ready = 2
    selecting = 3
    error = 4
    done = 5


class PageController(object):

    def __init__(self, home_station_service):
        self._state = State.initial
        self._home_station_service = home_station_service
        self._candidates = None
        self._error = None
        self.on_loading = signals.Signal()
        self.on_ready = signals.Signal()
        self.on_error = signals.Signal()
        self.on_selecting = signals.Signal()
        self.on_done = signals.Signal()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if self._state == state:
            raise StateError()
        if self._state == State.error:
            self._error = None
        self._state = state
        if state == State.loading:
            self.on_loading()
        elif state == State.ready:
            self.on_ready()
        elif state == State.error:
            self.on_error()
        elif state == State.selecting:
            self.on_selecting()
        elif state == State.done:
            self.on_done()
        else:
            raise StateError()

    @property
    def candidates(self):
        if self.state != State.ready:
            raise StateError()
        return self._candidates

    @property
    def error(self):
        if self.state != State.error:
            raise StateError()
        return self._error

    @property
    def next_remote_change_time(self):
        return self._home_station_service.get_next_remote_change_time()

    @property
    def on_home_station_changed(self):
        return self._home_station_service.on_home_station_changed

    def load(self):
        if self.state not in (State.initial, State.ready, State.error):
            raise StateError()
        self.state = State.loading
        try:
            result = self._home_station_service.get_home_station_candidates()
            self._candidates = result.candidates
            result.token.on_invalidated.connect(self._on_candidates_invalidated)
        except Exception as error:
            log.exception('Failed to load SelectHomeStationPageController')
            self._error = error
            self.state = State.error
        else:
            self.state = State.ready

    def select(self, candidate):
        if self._state != State.ready:
            raise StateError()
        allow_remote = False
        if candidate.is_remote:
            allow_remote = prompt_set_home_station_remotely()
            if not allow_remote:
                return
        self.state = State.selecting
        try:
            self._home_station_service.set_home_station(candidate.id, allow_remote)
        except ChangeHomeStationValidationError as error:
            handle_change_home_station_validation_error(error)
        finally:
            self.state = State.done

    def _on_candidates_invalidated(self):
        if self.state in (State.loading, State.ready):
            uthread2.start_tasklet(self.load)


class SelectHomeStationPage(Page):

    def __init__(self, home_station_service):
        super(SelectHomeStationPage, self).__init__()
        self.controller = PageController(home_station_service)
        self.candidate_entries = []
        self.scroll = None
        self.main_cont = None
        self.bottom_cont = None
        self.spinner_cont = None
        self.error_cont = None
        self.current_station_cont = None
        self.school_station_cont = None
        self.office_candidates_cont = None

    def load(self):
        self.layout()
        self.controller.on_loading.connect(self.on_loading)
        self.controller.on_ready.connect(self.on_ready)
        self.controller.on_error.connect(self.on_error)
        self.controller.on_selecting.connect(self.on_selecting)
        self.controller.on_done.connect(self.on_done)
        self.controller.load()

    def on_loading(self):
        self.show_spinner()

    def on_ready(self):
        self.hide_spinner()
        self.update_candidates()

    def on_error(self):
        self.hide_spinner()
        self.show_error()

    def on_selecting(self):
        self.bottom_cont.Disable()
        animations.FadeOut(self.bottom_cont, duration=0.3)
        self.show_spinner()
        animations.FadeOut(self.main_cont, duration=0.3, callback=self.main_cont.Flush, sleep=True)

    def on_done(self):
        self.hide_spinner()
        self.go_back()

    def unload(self):
        self.spinner_cont = None
        self.error_cont = None
        self.controller.on_loading.disconnect(self.on_loading)
        self.controller.on_ready.disconnect(self.on_ready)
        self.controller.on_error.disconnect(self.on_error)
        self.controller.on_selecting.disconnect(self.on_selecting)
        self.controller.on_done.disconnect(self.on_done)
        super(SelectHomeStationPage, self).unload()

    def show_spinner(self):
        if self.spinner_cont is None:
            self.spinner_cont = Container(parent=self, align=uiconst.TOALL, idx=0)
            eveLoadingWheel.LoadingWheel(parent=self.spinner_cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.main_cont.state = uiconst.UI_DISABLED
        animations.FadeTo(self.main_cont, startVal=self.main_cont.opacity, endVal=0.2, duration=0.3, timeOffset=0.3)
        animations.FadeIn(self.spinner_cont, duration=0.3, timeOffset=0.3)

    def hide_spinner(self):
        self.main_cont.state = uiconst.UI_PICKCHILDREN
        animations.FadeIn(self.main_cont, duration=0.3)
        animations.FadeOut(self.spinner_cont, duration=0.3)

    def show_error(self):
        info_card.InfoCard(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.wide, severity=info_card.Severity.error, text=text.error_loading_home_station_candidates(), idx=1)

    def layout(self):
        self.bottom_cont = ContainerAutoSize(parent=self, align=uiconst.TOBOTTOM, padding=Padding.wide)
        carbonui.control.button.Button(parent=self.bottom_cont, align=uiconst.CENTER, fixedheight=BIG_BUTTON_HEIGHT, label=text.action_cancel(), func=self.go_back, args=())
        self.scroll = ScrollContainer(parent=self, align=uiconst.TOALL)
        self.main_cont = ContainerAutoSize(parent=self.scroll, align=uiconst.CENTERTOP, alignMode=uiconst.TOTOP, top=Padding.wide, opacity=0.0, width=PAGE_WIDTH_MAX)
        eveLabel.EveCaptionLarge(parent=self.main_cont, align=uiconst.TOTOP, text=text.header_change_home_station())
        Header(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.section, text=text.header_current_station())
        self.current_station_cont = CandidatesList(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.normal, spacing=Padding.normal, no_content_hint=text.no_content_hint_current_station())
        Header(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.section, text=text.header_school_station(), hint=text.hint_school_station_header())
        self.school_station_cont = CandidatesList(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.normal, spacing=Padding.normal, no_content_hint=text.no_content_hint_school_station())
        Header(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.wide * 2, text=text.header_corporation_offices(), hint=text.hint_corporation_offices_header())
        RemoteChangeInfoCard(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.normal, get_next_remote_change_time=lambda : self.controller.next_remote_change_time, on_home_station_changed=self.controller.on_home_station_changed)
        self.office_candidates_cont = CandidatesList(parent=self.main_cont, align=uiconst.TOTOP, top=Padding.normal, spacing=Padding.normal, no_content_hint=text.no_content_hint_corporation_offices())

    def update_candidates(self):
        while self.candidate_entries:
            self.candidate_entries.pop().Close()

        localized_cmp = localization.util.GetSortFunc(localization.util.GetLanguageID())
        loc_key = functools.cmp_to_key(localized_cmp)
        sorted_candidates = sorted(self.controller.candidates, key=lambda candidate: loc_key(candidate.name))
        for candidate in sorted_candidates:
            parents = []
            if candidate.is_current_station:
                parents.append(self.current_station_cont)
            if candidate.is_school_hq:
                parents.append(self.school_station_cont)
            if candidate.is_remote:
                parents.append(self.office_candidates_cont)
            for parent in parents:
                self.candidate_entries.append(StationCandidateEntry(parent=parent, align=uiconst.TOTOP, page_controller=self.controller, candidate=candidate))


class RemoteChangeInfoCard(info_card.InfoCard):

    def __init__(self, get_next_remote_change_time, on_home_station_changed, **kwargs):
        super(RemoteChangeInfoCard, self).__init__(severity=info_card.Severity.info, state=uiconst.UI_HIDDEN, **kwargs)
        self._get_next_remote_change_time = get_next_remote_change_time
        self._on_home_station_changed = on_home_station_changed
        self.load()
        self._on_home_station_changed.connect(self.load)

    @threadutils.highlander_threaded
    def load(self):
        while not self.destroyed:
            next_remote_change_time = self._get_next_remote_change_time()
            if next_remote_change_time is None:
                self.display = False
                return
            self.display = True
            delta = next_remote_change_time - datetime.datetime.utcnow()
            if delta.total_seconds() <= 0:
                self.display = False
                return
            if delta.total_seconds() <= 1:
                self.text = text.remote_change_cooldown_info_card(timestamp=text.just_a_moment())
            else:
                filetime_delta = datetimeutils.timedelta_to_filetime_delta(delta)
                timestamp = localization.formatters.FormatTimeIntervalWritten(filetime_delta, showFrom='day', showTo='second')
                self.text = text.remote_change_cooldown_info_card(timestamp=timestamp)
            uthread2.sleep(1.0)


class CandidatesList(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP

    def __init__(self, spacing = 0, no_content_hint = None, **kwargs):
        super(CandidatesList, self).__init__(**kwargs)
        self._spacing = spacing
        self._no_content_hint = no_content_hint
        self._no_content_hint_label = None
        self._update_no_content_hint()

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, spacing):
        if spacing != self._spacing:
            self._spacing = spacing
            self._update_spacing()

    def _update_no_content_hint(self):
        if len(self.children) == 0:
            self._no_content_hint_label = eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, text=self._no_content_hint, color=TextColor.secondary)
        elif len(self.children) > 1 and self._no_content_hint_label is not None:
            label = self._no_content_hint_label
            self._no_content_hint_label = None
            label.Close()

    def _update_spacing(self):
        for i, child in enumerate(self.children):
            if i > 0:
                child.padTop = self._spacing

    def _AppendChildRO(self, child):
        super(CandidatesList, self)._AppendChildRO(child)
        self._update_no_content_hint()
        self._update_spacing()

    def _InsertChildRO(self, idx, child):
        super(CandidatesList, self)._InsertChildRO(idx, child)
        self._update_no_content_hint()
        self._update_spacing()

    def _RemoveChildRO(self, child):
        super(CandidatesList, self)._RemoveChildRO(child)
        self._update_no_content_hint()
        self._update_spacing()


class StationCandidateEntry(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP
    default_minHeight = BIG_BUTTON_HEIGHT
    icon_size = default_minHeight

    def __init__(self, page_controller, candidate, **kwargs):
        super(StationCandidateEntry, self).__init__(**kwargs)
        self.page_controller = page_controller
        self.candidate = candidate
        self.layout()

    def layout(self):
        icon_cont = ContainerAutoSize(parent=self, align=uiconst.TOLEFT, padRight=Padding.normal)
        itemIcon.ItemIcon(parent=icon_cont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=self.icon_size, height=self.icon_size, typeID=self.candidate.type_id, showOmegaOverlay=False)
        button_cont = ContainerAutoSize(parent=self, align=uiconst.TORIGHT, padLeft=Padding.normal)
        SelectHomeStationButton(parent=button_cont, align=uiconst.TOPLEFT, page_controller=self.page_controller, candidate=self.candidate)
        eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=self.candidate.link)
        eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, text=text.solar_system_trace(self.candidate.solar_system_id), color=TextColor.secondary)


class SelectHomeStationButton(carbonui.control.button.Button):
    default_fixedheight = BIG_BUTTON_HEIGHT

    def __init__(self, page_controller, candidate, **kwargs):
        self.page_controller = page_controller
        self.candidate = candidate
        super(SelectHomeStationButton, self).__init__(label=text.action_set_home_station(), func=self.page_controller.select, args=(self.candidate,), **kwargs)
        if self.candidate.errors:
            self.Disable()

    def LoadTooltipPanel(self, panel, parent):
        errors = [ text.describe_change_home_station_validation_error(error) for error in self.candidate.errors ]
        load_error_tooltip(panel, errors)
