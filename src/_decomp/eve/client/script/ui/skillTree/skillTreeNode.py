#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillTree\skillTreeNode.py
import itertools
from collections import defaultdict
import evetypes
from skills.client.skillController import SkillController

class SkillTreeController(SkillController):

    def __init__(self, typeID):
        super(SkillTreeController, self).__init__(typeID)
        self.parentsByLevel = defaultdict(list)
        self.childrenByLevel = defaultdict(list)

    def AddParent(self, parent, level):
        parent.AddChild(self, level)

    def AddChild(self, child, level):
        self.childrenByLevel[level].append(child)
        child.parentsByLevel[level].append(self)

    def PrintChildren(self, depth = 0):
        print '-' * depth + evetypes.GetName(self.GetTypeID())
        for level, children in self.childrenByLevel.iteritems():
            print '\n' + '-' * depth + 'LEVEL %s:' % level
            for child in children:
                child.PrintChildren(depth + 1)

    def GetCategoryAndGroupName(self):
        return evetypes.GetGroupName(self.GetTypeID())

    def IsRoot(self):
        return not self.GetParentsByLevel()

    def IsRootOfGroup(self):
        parents = [ node for node in self.GetParents() if node.GetGroupID() == self.GetGroupID() ]
        return not parents

    def GetParents(self):
        return list(itertools.chain(*self.parentsByLevel.values()))

    def GetParentsByLevel(self):
        return self.parentsByLevel

    def GetChildren(self):
        return list(itertools.chain(*self.childrenByLevel.values()))

    def GetDecendants(self):
        ret = []
        self._GetDecendants(self, ret)
        return ret

    def GetDecendantsTypeIDs(self):
        ret = [ node.GetTypeID() for node in self.GetDecendants() ]
        ret.append(self.GetTypeID())
        return ret

    def _GetDecendants(self, node, ret):
        children = node.GetChildren()
        ret.extend(children)
        for child in children:
            self._GetDecendants(child, ret)

    def GetAncestors(self):
        ret = []
        self._GetAncestors(self, ret)
        return ret

    def _GetAncestors(self, node, ret):
        parents = node.GetParents()
        ret.extend(parents)
        for child in parents:
            self._GetAncestors(child, ret)

    def GetSubtree(self):
        return self.GetAncestors() + [self] + self.GetChildren()

    def GetChildrenByLevel(self):
        return self.childrenByLevel

    def GetDepth(self):
        if not self.parentsByLevel:
            return 0
        return max([ parent.GetDepth() + 1 for parent in self.GetParents() ])
