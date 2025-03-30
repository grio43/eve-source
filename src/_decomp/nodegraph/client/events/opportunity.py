#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\opportunity.py
from .base import Event

class OpportunityViewed(Event):
    atom_id = 603

    def _register(self):
        from jobboard.client.job_board_signals import on_job_viewed
        on_job_viewed.connect(self._on_job_viewed)

    def _unregister(self):
        from jobboard.client.job_board_signals import on_job_viewed
        on_job_viewed.disconnect(self._on_job_viewed)

    def _on_job_viewed(self, job_id):
        self.invoke(job_id=job_id)

    @classmethod
    def get_subtitle(cls, job_id = None, **kwargs):
        return job_id
