#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\field.py
import eveicon
from contextlib import contextmanager
import proper
import threadutils
import uthread2
import weakness
from eveui.animation import animate, fade_in, fade_out
from eveui.audio import Sound
from eveui.autocomplete.behavior import AutocompleteBehavior
from eveui.autocomplete.suggestion_entry import LargeSuggestionEntry
from eveui.button.icon import ButtonIcon
from eveui.constants import Align
from eveui.decorators import lazy
from eveui.external import Container, ContainerAutoSize
from eveui.input.text_field import TextField
from eveui.progress.dots import DottedProgress

class ProgressBehavior(object):

    def __init__(self, *args, **kwargs):
        super(ProgressBehavior, self).__init__(*args, **kwargs)
        self.autocomplete_controller.on_fetch_start.connect(self.__on_fetch_start)
        self.autocomplete_controller.on_fetch_end.connect(self.__on_fetch_end)

    @lazy
    def __progress_indicator(self):
        container = ContainerAutoSize(parent=self.trailing_container, align=Align.to_right, left=8, opacity=0.0)
        DottedProgress(parent=container, align=Align.center, dot_size=3, dot_count=3)
        return container

    def __on_fetch_start(self, query):
        if not self.__progress_indicator.isAutoSizeEnabled:
            self.__progress_indicator.EnableAutoSize()
        fade_in(self.__progress_indicator, duration=0.5)

    def __on_fetch_end(self, query):
        self.__progress_indicator.DisableAutoSize()
        animate(self.__progress_indicator, 'width', end_value=0, duration=0.2)
        fade_out(self.__progress_indicator, duration=0.2, on_complete=self.__progress_indicator.Close)


class ClearBehavior(object):
    clear_button_size = 16
    clear_button_margin = 0

    def __init__(self, *args, **kwargs):
        super(ClearBehavior, self).__init__(*args, **kwargs)

    @lazy
    def __clear_button(self):
        button_container = Container(parent=self.trailing_container, align=Align.to_right, left=8, opacity=0.0)
        ButtonIcon(parent=button_container, align=Align.center, size=self.clear_button_size, texture_path=eveicon.close, on_click=self.clear, opacity=0.5)
        return button_container

    def show_clear_button(self):
        fade_in(self.__clear_button, duration=0.2)
        animate(self.__clear_button, 'width', end_value=self.clear_button_size + self.clear_button_margin * 2, duration=0.2)

    def hide_clear_button(self):
        fade_out(self.__clear_button, duration=0.2)
        animate(self.__clear_button, 'width', end_value=0, duration=0.2, on_complete=self.__clear_button.Close)


class AutocompleteField(ClearBehavior, ProgressBehavior, AutocompleteBehavior, TextField):
    suggestion_icon_size = 16
    suggestion_icon_margin = 2

    def __init__(self, provider, get_suggestion_text = None, completed_suggestion = None, suggestion_limit = 30, suggestion_list_class = None, **kwargs):
        try:
            iter(provider)
        except TypeError:
            provider = [provider]

        self.__providers = provider
        self.__suggestion_icon = None
        self.__text_update_suppressed = False
        self._get_suggestion_text = get_suggestion_text
        super(AutocompleteField, self).__init__(fetch_suggestions=weakness.WeakMethod(self.__fetch_suggestions), render_suggestion=weakness.WeakMethod(self.__render_suggestion), completed_suggestion=completed_suggestion, suggestion_limit=suggestion_limit, suggestion_list_class=suggestion_list_class, text=self.__get_suggestion_name(completed_suggestion), **kwargs)
        self.__layout()
        self.bind(focused=self.__on_focused_changed, text=self.__on_text_changed, completed_suggestion=self.__on_completed_suggestion_changed)

    @proper.ty(default=None)
    def completed_suggestion(self):
        pass

    def clear(self):
        with self.autocomplete_controller.prevent_fetch():
            self.controller.clear_text()
        self.completed_suggestion = None

    def complete(self, suggestion):
        if suggestion == self.completed_suggestion:
            return
        self.completed_suggestion = suggestion

    def on_completed(self, suggestion):
        Sound.entry_select.play()
        self.complete(suggestion)

    def __fetch_suggestions(self, query):
        previous_suggestions = set(self.autocomplete_controller.suggestions)
        for s in fetch_from_providers(self.__providers, query, previous_suggestions):
            yield s

    def __render_suggestion(self, autocomplete_controller, suggestion, query):
        return LargeSuggestionEntry(get_suggestion_text=self.__get_suggestion_text, autocomplete_controller=autocomplete_controller, suggestion=suggestion, query=query)

    def __render_suggestion_icon(self, suggestion, size):
        return suggestion.render_icon(size)

    def __get_suggestion_text(self, suggestion):
        if suggestion is None:
            return u''
        if self._get_suggestion_text:
            return self._get_suggestion_text(suggestion)
        return suggestion.text

    def __get_suggestion_name(self, suggestion):
        if suggestion is None:
            return u''
        if self._get_suggestion_text:
            return self._get_suggestion_text(suggestion)
        return suggestion.name

    def __on_focused_changed(self, *args):
        if self.completed_suggestion is not None:
            self.controller.select_all()
        else:
            self.clear()

    def __on_completed_suggestion_changed(self, *args):
        self.__update_completed_suggestion()

    def __update_completed_suggestion(self):
        if self.completed_suggestion is None:
            if not self.__text_update_suppressed:
                with self.autocomplete_controller.prevent_fetch():
                    self.controller.clear_text()
            self.__hide__suggestion_icon()
            self.hide_clear_button()
        else:
            if not self.__text_update_suppressed:
                with self.autocomplete_controller.prevent_fetch():
                    self.controller.replace_text(self.__get_suggestion_name(self.completed_suggestion))
            self.__show_suggestion_icon()
            self.show_clear_button()

    def __on_text_changed(self, *args):
        if self.completed_suggestion is not None and not self.autocomplete_controller.is_fetch_suppressed:
            with self.__prevent_text_update():
                self.completed_suggestion = None

    @contextmanager
    def __prevent_text_update(self):
        self.__text_update_suppressed = True
        try:
            yield
        finally:
            self.__text_update_suppressed = False

    def __layout(self):
        if self.completed_suggestion is not None:
            self.__show_suggestion_icon(should_animate=False)
            self.show_clear_button()

    @lazy
    def __suggestion_icon_container(self):
        return Container(parent=self.leading_container, align=Align.to_left, left=8, opacity=0.0)

    def __show_suggestion_icon(self, should_animate = True):
        if self.__suggestion_icon:
            self.__suggestion_icon.Close()
        icon = self.__render_suggestion_icon(self.completed_suggestion, self.suggestion_icon_size)
        if icon is None:
            return
        container = self.__suggestion_icon_container
        end_width = self.suggestion_icon_size + self.suggestion_icon_margin * 2
        if should_animate:
            fade_in(container, duration=0.08)
            animate(container, 'width', end_value=end_width, duration=0.1)
        else:
            container.opacity = 1
            container.width = end_width
        self.__suggestion_icon = icon
        self.__suggestion_icon.align = Align.center
        self.__suggestion_icon.SetParent(container)

    def __hide__suggestion_icon(self):
        fade_out(self.__suggestion_icon_container, duration=0.08)
        animate(self.__suggestion_icon_container, 'width', end_value=0, duration=0.1, on_complete=self.__suggestion_icon_container.Close)


thread_done_message = object()

def fetch_from_providers(providers, query, previous_suggestions):
    channel = uthread2.queue_channel()
    threads = []
    try:
        for provider in providers:
            threads.append(start_fetch_thread(provider, channel, query, previous_suggestions))

        done_count = 0
        while done_count < len(threads):
            result = channel.receive()
            if result is thread_done_message:
                done_count += 1
            else:
                yield result

    finally:
        for thread in threads:
            thread.kill()


@threadutils.threaded
def start_fetch_thread(provider, channel, query, previous_suggestions):
    try:
        suggestions = provider(query, previous_suggestions)
        for suggestion in suggestions:
            channel.send(suggestion)
            threadutils.be_nice(5)

    finally:
        channel.send(thread_done_message)
