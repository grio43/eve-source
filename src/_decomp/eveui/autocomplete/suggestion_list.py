#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\suggestion_list.py
import threadutils
import uthread2
from eveui.constants import Align
from eveui.decorators import skip_if_destroyed
from eveui.external import Fill, ScrollContainer

def optional(value, default):
    if value is not None:
        return value
    return default


class SuggestionScrollList(ScrollContainer):
    default_min_width = 0
    default_max_width = 360
    default_min_height = 0
    default_max_height = 240

    def __init__(self, autocomplete_controller, render_suggestion, min_height = None, max_height = None, min_width = None, max_width = None, **kwargs):
        self.min_height = optional(min_height, self.default_min_height)
        self.max_height = optional(max_height, self.default_max_height)
        self.min_width = optional(min_width, self.default_min_width)
        self.max_width = optional(max_width, self.default_max_width)
        self._controller = autocomplete_controller
        self._render_suggestion = render_suggestion
        self._entries = {}
        self._is_updating = False
        super(SuggestionScrollList, self).__init__(**kwargs)
        self._layout()
        self._update_suggestions()
        self._controller.bind(suggestion_result=self._update_suggestions, selected_suggestion=self._update_selected_suggestion)
        self._controller.on_fetch_start.connect(self._update_query)

    def _layout(self):
        Fill(bgParent=self, color=(0.1, 0.1, 0.1, 1.0))

    def _update_query(self, query):
        if self._is_updating:
            self._is_dirty = True
            return
        for suggestion, entry in self._entries.items():
            entry.query = query

    def _update_suggestions(self, *args):
        self._is_dirty = True
        if not self._is_updating:
            self._is_updating = True
            self._update_suggestions_thread()

    @threadutils.threaded
    def _update_suggestions_thread(self):
        try:
            while self._is_dirty:
                self._is_dirty = False
                self._update_suggestions_inner()

        finally:
            self._is_updating = False

        self._scroll_to_selected()

    @skip_if_destroyed
    def _update_suggestions_inner(self):
        self.mainCont.DisableAutoSize()
        new_entries = {}
        suggestions = self._controller.suggestions
        query = self._controller.query
        for suggestion, entry in self._entries.iteritems():
            if suggestion not in suggestions:
                entry.SetParent(None)
                uthread2.start_tasklet(entry.Close)
            else:
                entry.query = query
                new_entries[suggestion] = entry

        for index, suggestion in enumerate(suggestions):
            threadutils.BeNice(5)
            entry = self._entries.get(suggestion, None)
            if entry is None:
                entry = self._add_suggestion_entry(index=index, autocomplete_controller=self._controller, suggestion=suggestion, query=query)
                new_entries[suggestion] = entry
            elif not entry.destroyed and entry.GetOrder() != index:
                entry.SetOrder(index)

        self._entries = new_entries
        self.mainCont.EnableAutoSize()

    def _update_selected_suggestion(self, autocomplete_controller, selected_suggestion):
        self._scroll_to_selected()

    @skip_if_destroyed
    def _scroll_to_selected(self):
        if self._is_updating:
            return
        if self._controller.selected_suggestion is None:
            return
        selected_entry = self._entries.get(self._controller.selected_suggestion, None)
        if selected_entry is not None:
            self.ScrollToRevealChildVertical(selected_entry)

    def _add_suggestion_entry(self, index, autocomplete_controller, suggestion, query):
        entry = self._render_suggestion(autocomplete_controller=autocomplete_controller, suggestion=suggestion, query=query)
        entry.align = Align.to_top
        entry.SetParent(self, idx=index)
        return entry

    def _OnMainContSizeChange(self, width, height):
        super(SuggestionScrollList, self)._OnMainContSizeChange(width, height)
        self.height = max(self.min_height, min(height, self.max_height))
        self.width = max(self.min_width, min(width, self.max_width))
