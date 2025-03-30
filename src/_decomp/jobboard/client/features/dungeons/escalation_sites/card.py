#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\escalation_sites\card.py
from jobboard.client.features.dungeons.card import DungeonCard, DungeonListEntry
from jobboard.client.ui.time_remaining import TimeRemainingIcon

class EscalationSiteCard(DungeonCard):

    def _construct_attention_icons(self, parent):
        super(EscalationSiteCard, self)._construct_attention_icons(parent)
        self._construct_time_remaining(parent)

    def _construct_time_remaining(self, parent):
        if self.job.is_expired:
            return
        time_remaining_icon = TimeRemainingIcon(parent=parent, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag


class EscalationListEntry(DungeonListEntry):

    def _construct_attention_icons(self, parent):
        super(EscalationListEntry, self)._construct_attention_icons(parent)
        self._construct_time_remaining(parent)

    def _construct_time_remaining(self, parent):
        time_remaining_icon = TimeRemainingIcon(parent=parent, job=self.job, padLeft=4)
        time_remaining_icon.OnClick = self.OnClick
        time_remaining_icon.GetMenu = self.GetMenu
        time_remaining_icon.GetDragData = self.GetDragData
        time_remaining_icon.PrepareDrag = self.PrepareDrag
