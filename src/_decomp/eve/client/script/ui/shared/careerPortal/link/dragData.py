#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\link\dragData.py
from carbonui.control.dragdrop.dragdata.basedragdata import BaseDragData
from eve.client.script.ui.shared.careerPortal.link.link import node_link

class NodeDragData(BaseDragData):

    def __init__(self, careerID, activityID, goalID, name):
        super(NodeDragData, self).__init__()
        self.careerID = careerID
        self.activityID = activityID
        self.goalID = goalID
        self.name = name

    def GetIconTexturePath(self):
        return 'res:/ui/texture/classes/careerPortal/link_icon.png'

    def get_link(self):
        return node_link(self.careerID, self.activityID, self.goalID, self.name)
