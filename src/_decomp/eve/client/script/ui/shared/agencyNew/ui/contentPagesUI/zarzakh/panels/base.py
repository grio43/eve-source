#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\zarzakh\panels\base.py
from carbonui.primitives.container import Container

class BasePanel(Container):

    def __init__(self, *args, **kwargs):
        super(BasePanel, self).__init__(*args, **kwargs)

    def get_searchable_strings(self):
        return []
