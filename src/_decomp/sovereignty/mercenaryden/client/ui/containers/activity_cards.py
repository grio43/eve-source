#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\activity_cards.py
from carbonui import Align
from characterdata.careerpathconst import career_path_enforcer
from eveicon import hourglass as hourglass_icon
from eve.client.script.ui.control.timer import CountdownTimer
from jobboard.client.features.mercenary_tactical_operations.card_section_vertical import MTOFeatureCardSectionVertical
from jobboard.client.job_board_signals import on_job_added, on_job_removed, on_job_completed
from jobboard.client.ui.base_list_entry import ListEntryWithText
from localization import GetByLabel
from signals.signalUtil import ConnectSignals, DisconnectSignals

class ActivityCards(MTOFeatureCardSectionVertical):
    LABEL_PATH_NEXT_ACTIVITY = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/NextActivityTimer'
    MSECS_BETWEEN_NEXT_AVAILABLE_UPDATES = 500

    def __init__(self, controller, show_feature = True, show_solar_system = False, hide_empty = True, *args, **kwargs):
        self._controller = controller
        self._next_generation = None
        self._entry_with_timer = None
        self._timer = CountdownTimer(fetch_timestamp_to_countdown_to=self._controller.get_next_activity_generation, max_fetching_attempts=5)
        super(ActivityCards, self).__init__(show_feature, show_solar_system, hide_empty, *args, **kwargs)
        self._connect_signals()

    def Close(self):
        self._timer.stop_timer()
        self._disconnect_signals()
        super(ActivityCards, self).Close()

    def _connect_signals(self):
        self._signals_and_callbacks = [(on_job_added, self._on_jobs_changed),
         (on_job_removed, self._on_jobs_changed),
         (on_job_completed, self._on_jobs_changed),
         (self._timer.on_updated, self._on_next_available_timer_updated)]
        ConnectSignals(self._signals_and_callbacks)

    def _disconnect_signals(self):
        self._signals_and_callbacks = []
        DisconnectSignals(self._signals_and_callbacks)

    def _fetch_jobs(self):
        all_available_jobs = self._fetch_all_jobs()
        mercenary_den_id = self._controller.item_id
        available_jobs_for_my_mercenary_den = [ job for job in all_available_jobs if job.den_id == mercenary_den_id ]
        return available_jobs_for_my_mercenary_den[:10]

    def _construct_cards(self):
        for job in self._jobs_by_id.values():
            job.construct_list_entry(parent=self._cards_container, align=Align.TOTOP, show_feature=self._show_feature, show_solar_system=self._show_solar_system)

        self._entry_with_timer = ListEntryWithText(name='entry_with_timer_to_next_available', parent=self._cards_container, align=Align.TOTOP, icon=hourglass_icon, career_id=career_path_enforcer, display=False)
        self._timer.start_timer()

    def _on_jobs_changed(self, *args, **kwargs):
        if self._entry_with_timer:
            self._entry_with_timer.display = self._should_display_next_available_timer()

    def _on_next_available_timer_updated(self, text):
        if text:
            self._entry_with_timer.text = GetByLabel(labelNameAndPath=self.LABEL_PATH_NEXT_ACTIVITY, time_left=text)
        self._entry_with_timer.display = self._should_display_next_available_timer()

    def _should_display_next_available_timer(self):
        if not self._entry_with_timer or not self._entry_with_timer.text:
            return False
        if len(self._jobs_by_id) >= self._controller.get_activity_limit():
            return False
        return True
