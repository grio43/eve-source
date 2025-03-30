#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\controller.py
from contextlib import contextmanager
import heapq
import proper
import signals
import threadutils
import uthread2

class AutocompleteController(proper.Observable):
    __stop_consume_thread_message = object()

    def __init__(self, fetch_suggestions, suggestion_limit = None, **kwargs):
        self.suggestion_limit = suggestion_limit
        self.__fetch_suggestions = fetch_suggestions
        self.__fetch_result_queue = uthread2.queue_channel()
        self.__fetch_suppressed = 0
        self.__fetching_query = None
        super(AutocompleteController, self).__init__(**kwargs)
        self.on_completed = signals.Signal(signalName='on_completed')
        self.on_closed = signals.Signal(signalName='on_closed')
        self.on_fetch_start = signals.Signal(signalName='on_fetch_start')
        self.on_fetch_end = signals.Signal(signalName='on_fetch_end')
        self.__start_consume_thread()

    @property
    def is_fetch_suppressed(self):
        return self.__fetch_suppressed > 0

    @proper.alias
    def selected_suggestion(self):
        if self.suggestions and self._selected_index is not None:
            return self.suggestions[self._selected_index]

    @selected_suggestion.setter
    def selected_suggestion(self, suggestion):
        if self.suggestions is None:
            return
        self._selected_index = self.suggestions.index(suggestion)

    @proper.alias
    def suggestions(self):
        if self.suggestion_result is not None:
            return self.suggestion_result.suggestions
        else:
            return []

    @proper.ty(default=None)
    def suggestion_result(self):
        pass

    @proper.alias
    def query(self):
        if self.suggestion_result:
            return self.suggestion_result.query

    def complete(self):
        if self.selected_suggestion is not None:
            self.on_completed(self.selected_suggestion)
            self.clear_suggestion_result()

    def cancel_fetch_maybe(self):
        if self.__fetch_suggestions_thread.kill_thread_maybe():
            query = self.__fetching_query
            self.__fetching_query = None
            self.on_fetch_end(query)

    def wait_for_fetch(self):
        while self.__fetching_query:
            self.__fetch_suggestions_thread.join()

    def clear_suggestion_result(self):
        self.cancel_fetch_maybe()
        self.suggestion_result = None

    def close(self):
        self.cancel_fetch_maybe()
        self.__fetch_result_queue.send(self.__stop_consume_thread_message)
        self.on_closed()
        self.on_completed.clear()
        self.on_closed.clear()
        self.on_fetch_start.clear()
        self.on_fetch_end.clear()
        self.unbind_all()

    def fetch_suggestions(self, query):
        if not self.is_fetch_suppressed:
            self.__fetching_query = query
            self.__fetch_suggestions_thread(query)
            self.on_fetch_start(query)

    @contextmanager
    def prevent_fetch(self):
        self.__fetch_suppressed += 1
        try:
            yield
        finally:
            self.__fetch_suppressed -= 1

    def select_next(self):
        if not self.suggestions:
            return
        self._selected_index = min(self._selected_index + 1, len(self.suggestions) - 1)

    def select_previous(self):
        if not self.suggestions:
            return
        self._selected_index = max(self._selected_index - 1, 0)

    @proper.ty(default=None)
    def _selected_index(self):
        pass

    @threadutils.highlander_threaded
    def __fetch_suggestions_thread(self, query):
        heap = []
        heap_snapshot = None
        suggestion_iter = self.__fetch_suggestions(query)
        if suggestion_iter is None:
            suggestion_iter = iter([])
        for i, suggestion in enumerate(suggestion_iter):
            if self.suggestion_limit and len(heap) >= self.suggestion_limit:
                heapq.heappushpop(heap, suggestion)
            else:
                heapq.heappush(heap, suggestion)
            if (i + 1) % 200 == 0 and heap != heap_snapshot:
                heap_snapshot = heap[:]
                self.__send_suggestion_result(heap_snapshot, query)
            threadutils.BeNice(5)

        self.__send_suggestion_result(heap, query)
        self.__fetching_query = None
        self.on_fetch_end(query)

    def __send_suggestion_result(self, heap, query):
        suggestions = list(reversed([ heapq.heappop(heap)[1] for _ in range(len(heap)) ]))
        result = SuggestionSearchResult(suggestions, query)
        self.__fetch_result_queue.send(result)
        uthread2.Yield()

    @threadutils.threaded
    def __start_consume_thread(self):
        while True:
            result = self.__fetch_result_queue.receive()
            if result is self.__stop_consume_thread_message:
                return
            self.suggestion_result = result

    @suggestion_result.after_change
    def __update_selected(self, suggestion_result):
        if suggestion_result is not None and suggestion_result.suggestions:
            self._selected_index = 0
        else:
            self._selected_index = None


class SuggestionSearchResult(object):

    def __init__(self, suggestions, query):
        self.suggestions = tuple(suggestions)
        self.query = query

    def __hash__(self):
        return hash((self.query, self.suggestions))

    def __eq__(self, other):
        return isinstance(other, SuggestionSearchResult) and self.suggestions == other.suggestions and self.query == other.query

    def __ne__(self, other):
        return not self == other
