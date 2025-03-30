#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\pages\browse_page.py
from .filtered_page import FilteredPage

class BrowsePage(FilteredPage):

    def _get_jobs(self):
        return self._service.get_available_jobs(filters=self._filters_controller.get_as_dict())

    def _validate_job(self, job):
        return job.is_available_in_browse and super(BrowsePage, self)._validate_job(job)
