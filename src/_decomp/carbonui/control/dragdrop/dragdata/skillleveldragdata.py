#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\dragdrop\dragdata\skillleveldragdata.py
from carbonui.control.dragdrop.dragdata.typedragdata import TypeDragData

class SkillLevelDragData(TypeDragData):

    def __init__(self, typeID, level):
        super(SkillLevelDragData, self).__init__(typeID)
        self.level = level
