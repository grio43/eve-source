#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\conditions\evetype.py
import evetypes
from .base import ConditionAtom

class InTypeList(ConditionAtom):
    atom_id = 582

    def __init__(self, type_list_id = None, type_id = None, group_id = None, category_id = None, **kwargs):
        super(InTypeList, self).__init__(**kwargs)
        self.type_list_id = type_list_id
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id

    def validate(self, **kwargs):
        if not self.type_list_id:
            return False
        if self.type_id:
            return self.type_id in evetypes.GetTypeIDsByListID(self.type_list_id)
        type_list = evetypes.GetTypeList(self.type_list_id)
        if self.group_id:
            return self.group_id in type_list.includedGroupIDs
        if self.category_id:
            return self.category_id in type_list.includedCategoryIDs
