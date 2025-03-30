#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\world_events\card.py
import eveui
from carbonui import Align
from jobboard.client.ui.card import JobCard
from jobboard.client.ui.list_entry import JobListEntry
from jobboard.client.ui.progress_bar import ProgressGauge
from jobboard.client.ui.time_remaining import TimeRemainingIcon

class WorldEventCard(JobCard):

    def __init__(self, *args, **kwargs):
        self._gauge = None
        super(WorldEventCard, self).__init__(*args, **kwargs)

    def _on_job_updated(self):
        self._update_gauge()
        self._update_state()

    def _construct_top_right(self):
        self._construct_progress(self._top_right_container)

    def _construct_attention_icons(self, parent):
        super(WorldEventCard, self)._construct_attention_icons(parent)
        self._construct_time_remaining(parent)

    def _construct_progress(self, parent):
        if not self.job.has_influence:
            return
        self._gauge = ProgressGauge(parent=parent, align=Align.CENTER, radius=25, bg_opacity=0.6)
        self._update_gauge(animate=False)

    def _construct_time_remaining(self, parent):
        if not self.job.expiration_time:
            return
        time_remaining_icon = TimeRemainingIcon(parent=parent, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag

    def _update_gauge(self, animate = True):
        if self._gauge is None:
            return
        self._gauge.Show()
        self._gauge.set_value(self.job.progress_percentage, animate=animate)


class WorldEventListEntry(JobListEntry):

    def __init__(self, *args, **kwargs):
        self._gauge = None
        super(WorldEventListEntry, self).__init__(*args, **kwargs)

    def _on_job_updated(self):
        self._update_gauge()
        self._update_state()

    def _construct_left_content(self, parent):
        super(WorldEventListEntry, self)._construct_left_content(parent)
        self._construct_progress(parent)

    def _construct_attention_icons(self, parent):
        super(WorldEventListEntry, self)._construct_attention_icons(parent)
        self._construct_time_remaining(parent)

    def _construct_progress(self, parent):
        if not self.job.has_influence:
            return
        gauge_container = eveui.ContainerAutoSize(name='gauge_container', parent=parent, align=eveui.Align.to_right, padRight=8)
        self._gauge = ProgressGauge(parent=gauge_container, align=eveui.Align.center, radius=12, show_label=False)
        self._update_gauge(animate=False)

    def _construct_time_remaining(self, parent):
        if not self.job.expiration_time:
            return
        time_remaining_icon = TimeRemainingIcon(parent=parent, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag

    def _update_gauge(self, animate = True):
        if not self._gauge:
            return
        self._gauge.Show()
        self._gauge.set_value(self.job.progress_percentage, animate=animate)
