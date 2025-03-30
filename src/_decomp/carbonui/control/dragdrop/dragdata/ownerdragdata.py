#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\dragdrop\dragdata\ownerdragdata.py
import logging
import evelink.client
from carbonui.control.dragdrop.dragdata.basedragdata import BaseDragData
from eve.common.script.sys import idCheckers
logger = logging.getLogger(__name__)

class OwnerDragData(BaseDragData):

    def __init__(self, owner_id):
        super(OwnerDragData, self).__init__()
        self.owner_id = owner_id

    def GetIconTexturePath(self):
        if idCheckers.IsAlliance(self.owner_id):
            return sm.GetService('photo').GetAllianceLogo(self.owner_id, 64)
        else:
            return sm.GetService('photo').GetPortrait(self.owner_id, 64)

    def get_link(self):
        return evelink.owner_link(self.owner_id)

    def get_owner_id(self):
        return self.owner_id
