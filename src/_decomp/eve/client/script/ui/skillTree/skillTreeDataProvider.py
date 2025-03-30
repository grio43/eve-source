#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillTree\skillTreeDataProvider.py
from collections import defaultdict
import evetypes
import inventorycommon.const as invconst
from eve.client.script.ui.skillTree.skillTreeNode import SkillTreeController
from evetypes.skills import get_dogma_required_skills

class SkillTreeDataProvider(object):

    def __init__(self):
        self.skillByTypeID = {}
        self.skillsByGroupID = defaultdict(list)
        self._ConstructNodes()
        self._InitializeData()

    def _ConstructNodes(self):
        type_ids = evetypes.GetTypeIDsByCategory(invconst.categorySkill)
        for type_id in type_ids:
            if not evetypes.IsPublished(type_id):
                continue
            skillTreeController = SkillTreeController(type_id)
            self.skillByTypeID[type_id] = skillTreeController

    def _InitializeData(self):
        for node in self.skillByTypeID.values():
            self._AddNodeToParent(node)
            self.skillsByGroupID[node.GetGroupID()].append(node)

    def _AddNodeToParent(self, skill_node):
        requiredSkillsByLevel = get_dogma_required_skills(skill_node.GetTypeID())
        for parentTypeID, level in requiredSkillsByLevel.iteritems():
            parent = self.skillByTypeID[parentTypeID]
            skill_node.AddParent(parent, level)

    def GetNode(self, type_id):
        return self.skillByTypeID.get(type_id, None)

    def GetSkillGroups(self):
        return self.skillsByGroupID.keys()

    def GetSkillsByGroupID(self, skill_group_id):
        return self.skillsByGroupID[skill_group_id]

    def GetAllSkills(self):
        return self.skillByTypeID.values()

    def GetSkillsByDepth(self):
        skillsByDepth = defaultdict(set)
        for skill in self.GetAllSkills():
            skillsByDepth[skill.GetDepth()].add(skill)

        return skillsByDepth

    def GetRootSkills(self):
        return self.GetSkillsByDepth()[0]


_skillTreeDataProvider = None

def GetSkillTreeDataProvider():
    global _skillTreeDataProvider
    _skillTreeDataProvider = None
    if _skillTreeDataProvider is None:
        _skillTreeDataProvider = SkillTreeDataProvider()
    return _skillTreeDataProvider
