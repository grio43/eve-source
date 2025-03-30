#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\history\controller.py
import logging
import signals
import threadutils
from raffles.client.character_stats import CharacterStats
from raffles.client.util import station_name
from raffles.common.errors import RafflesError
from .filter_controller import FilterController
logger = logging.getLogger(__name__)

class HistoryPageController(object):

    def __init__(self, storage):
        self._storage = storage
        self.filters = FilterController()
        self.filters.on_change.connect(self._filters_changed)
        self.filters.on_sorting_changed.connect(self._sorting_changed)
        self._my_raffles = set()
        self._sorted_raffles = []
        self._filtered_raffles = []
        self.on_raffles_changed = signals.Signal(signalName='on_raffles_changed')
        self.stats = CharacterStats()
        self.stats.start_fetch()
        self.fetching_raffles = True
        self._fetch_history()

    @threadutils.threaded
    def _fetch_history(self):
        try:
            raffle_history = sm.GetService('raffleSvc').get_history()
        except RafflesError:
            logger.exception('Failed to fetch HyperNet history')
            self.fetching_raffles = False
            self.on_raffles_changed()
        else:
            self.fetching_raffles = False
            for raffle_data in raffle_history:
                raffle = self._storage.update_raffle(raffle_data)
                self._my_raffles.add(raffle)

            self.stats.update_active(self._my_raffles)
            self._sort_raffles()
            self._apply_filter()
        finally:
            self._storage.on_raffle_joined.connect(self._raffle_joined)
            self._storage.on_raffle_created.connect(self._raffle_created)
            self._storage.on_raffle_finished.connect(self._raffle_finished)

    def _raffle_joined(self, raffle):
        self.stats.raffle_joined(raffle)
        self._add_raffle(raffle)

    def _raffle_created(self, raffle):
        self.stats.raffle_created(raffle)
        self._add_raffle(raffle)

    def _raffle_finished(self, raffle):
        self.stats.raffle_finished(raffle)

    def _add_raffle(self, raffle):
        if raffle not in self._my_raffles and raffle.is_involved:
            self._my_raffles.add(raffle)
            self._sort_raffles()
            self._apply_filter()

    def page_open(self):
        self._sort_raffles()
        self._apply_filter()

    @property
    def filtered_raffles(self):
        return self._filtered_raffles

    @property
    def filtered_count(self):
        return len(self._filtered_raffles)

    @property
    def total_count(self):
        return len(self._my_raffles)

    def _filters_changed(self):
        self._apply_filter()

    def _sorting_changed(self):
        self._sort_raffles()
        self._apply_filter()

    @threadutils.threaded
    def _apply_filter(self):
        self._filtered_raffles = [ raffle for raffle in self._sorted_raffles if self._filter_raffle(raffle) ]
        self.on_raffles_changed()

    def _filter_raffle(self, raffle):
        if not self.filters.get_setting('show_joined') and not raffle.is_raffle_owner:
            return False
        if not self.filters.get_setting('show_created') and raffle.is_raffle_owner:
            return False
        if not self.filters.get_setting('show_active') and not raffle.is_finished:
            return False
        if not self.filters.get_setting('show_finished') and raffle.is_finished:
            return False
        if not self.filters.get_setting('show_public') and not raffle.is_private:
            return False
        if not self.filters.get_setting('show_private') and raffle.is_private:
            return False
        if self.filters.item_suggestion:
            if self.filters.type_id and raffle.type_id != self.filters.type_id:
                return False
            if self.filters.group_id and raffle.group_id != self.filters.group_id:
                return False
            if self.filters.category_id and raffle.category_id != self.filters.category_id:
                return False
            if self.filters.is_blueprint and self.filters.blueprint_type:
                copy = self.filters.blueprint_type == 2
                return copy == raffle.is_blueprint_copy
        if self.filters.solar_system_id and raffle.solar_system_id != self.filters.solar_system_id:
            return False
        if self.filters.meta_group_id and raffle.meta_group_id != self.filters.meta_group_id:
            return False
        if self.filters.has_setting_changes('min_ticket_price') and self.filters.get_setting('min_ticket_price') > raffle.ticket_price:
            return False
        if self.filters.has_setting_changes('max_ticket_price') and self.filters.get_setting('max_ticket_price') < raffle.ticket_price:
            return False
        if self.filters.has_setting_changes('min_ticket_count') and self.filters.get_setting('min_ticket_count') > raffle.ticket_count:
            return False
        if self.filters.has_setting_changes('max_ticket_count') and self.filters.get_setting('max_ticket_count') < raffle.ticket_count:
            return False
        return True

    def _sort_raffles(self):
        sorting, reverse = self.filters.sorting
        if sorting:
            self._sorted_raffles = sorted(self._my_raffles, key=lambda raffle: getattr(raffle, sorting), reverse=reverse)
        else:
            finished_raffles = []
            active_raffles = []
            interaction_raffles = []
            for raffle in self._my_raffles:
                if raffle.is_finished:
                    if raffle.requires_interaction:
                        interaction_raffles.append(raffle)
                    else:
                        finished_raffles.append(raffle)
                else:
                    active_raffles.append(raffle)

            interaction_raffles.sort(key=lambda raffle: raffle.item_name, reverse=reverse)
            active_raffles.sort(key=lambda raffle: raffle.item_name, reverse=reverse)
            finished_raffles.sort(key=lambda raffle: raffle.end_time, reverse=not reverse)
            self._sorted_raffles = interaction_raffles + active_raffles + finished_raffles


def _check_search_filter(raffle, search):
    if search in raffle.item_name.lower():
        return True
    if search in station_name(raffle.location_id).lower():
        return True
