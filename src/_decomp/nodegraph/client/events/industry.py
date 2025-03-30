#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\industry.py
from __future__ import absolute_import
import uthread2
from .base import Event

class IndustryJobChanged(Event):
    atom_id = 516
    __notifyevents__ = ['OnIndustryJobClient']

    def OnIndustryJobClient(self, jobID = None, status = None, **kwargs):
        if not self._validate(status):
            return
        job_info = sm.GetService('industrySvc').GetJobByID(jobID, useCached=True)
        self.invoke(job_id=jobID, blueprint_type_id=job_info.blueprintTypeID, product_type_id=job_info.productTypeID)

    def _validate(self, status):
        return True


class IndustryJobInstalled(IndustryJobChanged):
    atom_id = 507

    def _validate(self, status):
        from industry.const import STATUS_INSTALLED
        return status == STATUS_INSTALLED


class IndustryJobReady(IndustryJobChanged):
    atom_id = 508

    def _validate(self, status):
        from industry.const import STATUS_READY
        return status == STATUS_READY


class SelectedIndustryJobChanged(Event):
    atom_id = 509
    __notifyevents__ = ['OnSelectedIndustryJobChanged']

    def OnSelectedIndustryJobChanged(self, jobData):
        if jobData:
            self._invoke(jobData)

    @uthread2.debounce(0.1)
    def _invoke(self, job_data):
        self.invoke(job_id=job_data.jobID, blueprint_id=job_data.blueprintID, blueprint_type_id=job_data.blueprint.blueprintTypeID, activity_id=job_data.activityID, runs=job_data.runs)


class ReprocessingMaterialsChanged(Event):
    atom_id = 505
    __notifyevents__ = ['OnReprocessingMaterialsChanged']

    def OnReprocessingMaterialsChanged(self, *args, **kwargs):
        self.invoke()
