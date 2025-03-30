#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\corporation_goals\info_panel_entry.py
from jobboard.client.ui.info_panel_entry import JobInfoPanelEntry

class CorporationJobInfoPanelEntry(JobInfoPanelEntry):

    @property
    def _participation_limit(self):
        return getattr(self.job, 'participation_limit', None)

    @property
    def _personal_progress(self):
        return getattr(self.job, 'personal_progress', 0)

    @property
    def _progress_percentage(self):
        participation_limit = self._participation_limit
        if not participation_limit:
            return super(CorporationJobInfoPanelEntry, self)._progress_percentage
        return float(self._personal_progress) / participation_limit
