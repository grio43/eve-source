#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\mercenary_tactical_operations\card.py
from carbonui import Align
from jobboard.client.ui.card import JobCard
from jobboard.client.ui.list_entry import JobListEntry
from jobboard.client.ui.time_remaining import TimeRemainingIcon

class MTOCard(JobCard):

    def _construct_attention_icons(self, parent):
        self._construct_time_remaining(parent)

    def _construct_time_remaining(self, parent):
        if self.job.is_expired or self.job.is_completed:
            return
        time_remaining_icon = TimeRemainingIcon(name='time_remaining_icon', parent=parent, align=Align.TORIGHT, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag


class MTOListEntry(JobListEntry):
    pass
