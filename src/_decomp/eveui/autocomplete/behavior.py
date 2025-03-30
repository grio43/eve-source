#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\behavior.py
from carbonui.uicore import uicore
import carbonui.const as uiconst
import proper
import uthread2
from eveui.autocomplete.controller import AutocompleteController
from eveui.autocomplete.suggestion_list import SuggestionScrollList
from eveui.constants import Align
from eveui.keyboard import Key

class AutocompleteBehavior(proper.Observable):

    def __init__(self, fetch_suggestions, render_suggestion, suggestion_limit = None, suggestion_list_class = None, hide_suggestions_on_unfocus = True, show_suggestions_on_focus = False, show_empty_suggestions = False, suggestion_list_min_width = None, suggestion_list_max_width = None, suggestion_list_min_height = None, suggestion_list_max_height = None, **kwargs):
        self.autocomplete_controller = AutocompleteController(fetch_suggestions, suggestion_limit)
        self.__render_suggestion = render_suggestion
        self.__suggestion_list_class = suggestion_list_class or SuggestionScrollList
        self.__hide_suggestions_on_unfocus = hide_suggestions_on_unfocus
        self.__show_suggestions_on_focus = show_suggestions_on_focus
        self.__show_empty_suggestions = show_empty_suggestions
        self.__suggestion_list_min_width = suggestion_list_min_width
        self.__suggestion_list_max_width = suggestion_list_max_width
        self.__suggestion_list_min_height = suggestion_list_min_height
        self.__suggestion_list_max_height = suggestion_list_max_height
        self.__suggestion_list = None
        super(AutocompleteBehavior, self).__init__(**kwargs)
        self.bind(focused=self.__on_focus_changed, text=self.__on_text_changed)
        self.autocomplete_controller.bind(suggestions=self.__on_suggestions_changed)
        self.autocomplete_controller.on_completed.connect(self.__on_completed)

    def on_completed(self, suggestion):
        with self.autocomplete_controller.prevent_fetch():
            self.text = suggestion

    def on_key_down(self, key):
        if key in (Key.up, Key.down):
            self.__open_suggestion_list()
            if not self.autocomplete_controller.suggestions:
                self.__fetch_suggestions(self.text)
            elif key == Key.down:
                self.autocomplete_controller.select_next()
            elif key == Key.up:
                self.autocomplete_controller.select_previous()
        elif key == Key.escape and self.autocomplete_controller.suggestions:
            self.__clear_suggestion_list()
        elif key in (Key.tab, Key.enter) and self.autocomplete_controller.selected_suggestion is not None:
            self.autocomplete_controller.complete()
        else:
            return super(AutocompleteBehavior, self).on_key_down(key)
        return True

    def __on_completed(self, suggestion):
        self.on_completed(suggestion)

    def __on_text_changed(self, *args):
        self.__fetch_suggestions(self.text)
        if self.focused:
            self.__open_suggestion_list()

    def __on_focus_changed(self, _, focused):
        if focused and self.__show_suggestions_on_focus:
            self.autocomplete_controller.clear_suggestion_result()
            self.__fetch_suggestions(self.text)
        elif not focused and self.__hide_suggestions_on_unfocus:
            self.__clear_suggestion_list()

    def __on_suggestions_changed(self, controller, suggestions):
        if len(suggestions) == 0 and not self.__show_empty_suggestions:
            self.__close_suggestion_list()
        elif self.focused and not self.completed_suggestion:
            self.__open_suggestion_list()

    @uthread2.debounce(wait=0.3)
    def __fetch_suggestions(self, query):
        self.autocomplete_controller.fetch_suggestions(query)

    def __close_suggestion_list(self):
        if self.__suggestion_list:
            self.__suggestion_list.Close()
            self.__suggestion_list = None

    def __clear_suggestion_list(self):
        self.autocomplete_controller.clear_suggestion_result()
        self.__close_suggestion_list()

    def __open_suggestion_list(self):
        if self.__suggestion_list is not None:
            return
        left, top, width, height = self.GetAbsolute()
        self.__suggestion_list = self.__suggestion_list_class(parent=uicore.layer.menu, align=Align.top_left, left=left, top=top + height, autocomplete_controller=self.autocomplete_controller, render_suggestion=self.__render_suggestion, min_width=max(self.__suggestion_list_min_width, width), max_width=self.__suggestion_list_max_width, min_height=self.__suggestion_list_min_height, max_height=self.__suggestion_list_max_height)
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self._on_global_mouse_down)

    def Close(self):
        self.autocomplete_controller.close()
        self.__close_suggestion_list()
        super(AutocompleteBehavior, self).Close()

    def _on_global_mouse_down(self, object, *args, **kwargs):
        if object == self or object.IsUnder(uicore.layer.menu):
            return True
        if self.__suggestion_list:
            self.__close_suggestion_list()
