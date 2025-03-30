#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\browse\controller.py
import random
from raffles.client.constants import RAFFLES_PER_PAGE
from raffles.client.tutorial import show_history_tab_hint
from .filter_controller import FilterController

class BrowsePageController(object):

    def __init__(self, storage):
        self._storage = storage
        self.filters = FilterController()
        self._browsing_page = 0
        self._browsing_raffles = []
        self._storage.on_raffle_joined.connect(self._on_raffle_joined)

    @property
    def page_number(self):
        return self._browsing_page

    @page_number.setter
    def page_number(self, page_number):
        self._browsing_page = page_number

    def get_raffles(self, from_refresh):
        if not self.filters.has_changes and self._browsing_raffles:
            if from_refresh:
                self._check_expired()
                self._browsing_page += 1
            start_index = self._browsing_page * RAFFLES_PER_PAGE
            end_index = start_index + RAFFLES_PER_PAGE
            result = self._browsing_raffles[start_index:end_index]
            show_cached = result and (self._browsing_page == 0 or len(result) == RAFFLES_PER_PAGE)
            if show_cached:
                return result
        self._clear_raffles()
        filters, constraints = self.filters.get()
        self._browsing_page = 0
        grab = sm.GetService('raffleSvc').grab(filters, constraints)
        for raffle_data in grab:
            raffle = self._storage.update_raffle(raffle_data)
            self._browsing_raffles.append(raffle)

        random.shuffle(self._browsing_raffles)
        self._sort()
        result = self._browsing_raffles[:12]
        return result

    def _sort(self):
        start_index = 0
        result = []
        while start_index < len(self._browsing_raffles):
            result.append(sorted(self._browsing_raffles[start_index:start_index + 12], key=lambda x: x.ticket_price, reverse=True))
            start_index = start_index + 12

        self._browsing_raffles = [ item for sublist in result for item in sublist ]

    def _check_expired(self):
        for raffle in self._browsing_raffles[:]:
            if raffle.is_expired:
                self._browsing_raffles.remove(raffle)
                if not raffle.is_involved:
                    self._storage.remove_raffle(raffle)

    def _clear_raffles(self):
        for raffle in self._browsing_raffles:
            if not raffle.is_involved:
                self._storage.remove_raffle(raffle)

        self._browsing_raffles = []

    def _on_raffle_joined(self, raffle):
        show_history_tab_hint()
