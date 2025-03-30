#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\agency.py
from .base import Condition

class AgencyContentGroupExpanded(Condition):
    atom_id = 217

    def __init__(self, content_group = None, **kwargs):
        super(AgencyContentGroupExpanded, self).__init__(**kwargs)
        self.content_group = content_group

    def validate(self, **kwargs):
        return sm.GetService('agencyNew').IsContentGroupOpenedByName(self.content_group)

    @classmethod
    def get_subtitle(cls, content_group = '', **kwargs):
        return content_group
