#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\opportunity.py
from .base import Action

class TrackOpportunity(Action):
    atom_id = 610

    def __init__(self, job_id = None, **kwargs):
        super(TrackOpportunity, self).__init__(**kwargs)
        self.job_id = self.get_atom_parameter_value('job_id', job_id)

    def start(self, **kwargs):
        super(TrackOpportunity, self).start(**kwargs)
        from jobboard.client import get_job_board_service
        job = get_job_board_service().get_job(self.job_id)
        if job:
            job.add_tracked()

    @classmethod
    def get_subtitle(cls, job_id = None, **kwargs):
        return job_id
