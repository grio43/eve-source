#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\atoms\getters\evetype.py
import evetypes
from .base import GetterAtom

class GetEveTypeInfo(GetterAtom):
    atom_id = 581

    def __init__(self, type_id = None, group_id = None):
        self.type_id = type_id
        self.group_id = group_id

    def get_values(self, **kwargs):
        if self.type_id:
            group_id = evetypes.GetGroupID(self.type_id)
        elif self.group_id:
            group_id = self.group_id
        else:
            return {}
        return {'group_id': group_id,
         'category_id': evetypes.GetCategoryIDByGroup(group_id)}


class GetTypeList(GetterAtom):
    atom_id = 186

    def __init__(self, type_list_id = None, **kwargs):
        self.type_list_id = type_list_id

    def get_values(self):
        return {'type_ids': evetypes.GetTypeIDsByListID(self.type_list_id)}

    @classmethod
    def get_subtitle(cls, type_list_id = None, **kwargs):
        return str(type_list_id)
