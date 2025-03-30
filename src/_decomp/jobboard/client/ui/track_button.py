#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\track_button.py
import carbonui
from carbonui.control.buttonIcon import ButtonIcon
import eveui
import eveicon
import localization
from jobboard.client import job_board_signals, get_job_board_service

class TrackJobButton(eveui.Button):

    def __init__(self, job, *args, **kwargs):
        self._job = job
        kwargs['func'] = self._on_click
        super(TrackJobButton, self).__init__(*args, **kwargs)
        self._update()
        job_board_signals.on_tracked_jobs_changed.connect(self._update)
        self._job.on_job_updated.connect(self._update)

    def Close(self):
        job_board_signals.on_tracked_jobs_changed.disconnect(self._update)
        if self._job:
            self._job.on_job_updated.disconnect(self._update)
        super(TrackJobButton, self).Close()

    def _update(self):
        if self._job.is_trackable or self._job.is_tracked:
            is_tracked = self._job.is_tracked
            self.icon = eveicon.camera_untrack if is_tracked else eveicon.visibility
            self.label = localization.GetByLabel('UI/Common/Untrack' if is_tracked else 'UI/Common/Track')
            self.variant = carbonui.ButtonVariant.NORMAL if not is_tracked else carbonui.ButtonVariant.GHOST
            self.Show()
        else:
            self.Hide()

    def _on_click(self, *args, **kwargs):
        if self._job.is_trackable or self._job.is_tracked:
            self._job.toggle_tracked_by_player()
        else:
            self.Hide()


class TrackJobIconButton(ButtonIcon):
    default_width = 24
    default_height = 24

    def __init__(self, job, *args, **kwargs):
        self._job = job
        kwargs['func'] = self._on_click
        super(TrackJobIconButton, self).__init__(*args, **kwargs)
        self._update()
        job_board_signals.on_tracked_jobs_changed.connect(self._update)
        self._job.on_job_updated.connect(self._update)

    def Close(self):
        job_board_signals.on_tracked_jobs_changed.disconnect(self._update)
        if self._job:
            self._job.on_job_updated.disconnect(self._update)
        super(TrackJobIconButton, self).Close()

    def _update(self):
        if self._job.is_trackable or self._job.is_tracked:
            is_tracked = self._job.is_tracked
            self.SetTexturePath(eveicon.camera_untrack if is_tracked else eveicon.visibility)
            self.hint = localization.GetByLabel('UI/Common/Untrack' if is_tracked else 'UI/Common/Track')
            self.Show()
        else:
            self.Hide()

    def _on_click(self, *args, **kwargs):
        if self._job.is_trackable or self._job.is_tracked:
            self._job.toggle_tracked_by_player()
        else:
            self.Hide()
