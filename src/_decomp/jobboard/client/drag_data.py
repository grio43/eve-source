#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\drag_data.py
from jobboard.client.link import get_job_link

class JobDragData(object):

    def __init__(self, job):
        self._job = job

    def get_link(self):
        return get_job_link(self._job)

    def LoadIcon(self, icon, dad, iconSize):
        icon.LoadIcon('res:/ui/Texture/WindowIcons/opportunities.png')
