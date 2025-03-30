#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillTree\skillTreeMapView.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.skillTree.skillTreeConst import ALL_GROUPS
LINE_COLOR = eveThemeColor.THEME_FOCUS
from eve.client.script.ui.shared.mapView import mapViewUtil
from eve.client.script.ui.shared.mapView.mapView import MapView
from eve.client.script.ui.skillTree.skillTreeDataProvider import GetSkillTreeDataProvider
from eve.client.script.ui.skillTree.skillTreeBracket import SkillTreeBracket
from eve.client.script.ui.skillTree.skillGroupSelectionCont import SkillGroupSelectionCont
LINE_WIDTH = 3.0
OPACITY_LINE_UNIMPORTANT = 0.05
OPACITY_LINE_IDLE = 0.5
OPACITY_LINE_HOVER = 1.0

class SkillTreeMapView(MapView):

    def ApplyAttributes(self, attributes):
        super(SkillTreeMapView, self).ApplyAttributes(attributes)
        self.currCategoryID = None
        self.currGroupID = None
        self.skillTreeDataProvider = GetSkillTreeDataProvider()
        self.bracketsByTypeID = {}
        self.linesByTypeID = {}
        self.groupSelectionCont = SkillGroupSelectionCont(parent=self, align=uiconst.TOLEFT, width=300, idx=0)
        self.groupSelectionCont.onSkillGroupSelected.connect(self.OnSkillGroupSelected)
        self.bracketCont = Container(name='bracketCont', parent=self.infoLayer)

    def ConstructLineSet(self):
        self.lineSet = mapViewUtil.CreateLineSet()
        self.lineSet.name = 'SkillLines'
        self.scene.objects.append(self.lineSet)

    def OnSkillGroupSelected(self, groupID):
        self.RedrawTree(groupID)

    def _ConstructScene(self, interestID, zoomToItem, mapFilterID):
        self.sceneContainer.Startup()
        self.camera.SetUpdateCallback(self.OnCameraUpdate)
        self.ConstructStarDataTexture()
        self.ConstructMapScene()
        self.ConstructLineSet()
        self.constructSceneThread = None
        self.camera.LookAtPoint((0, 0, 0))
        self.constructSceneThread = None

    def RedrawTree(self, groupID):
        self.currGroupID = groupID
        self.bracketCont.Flush()
        self.bracketsByTypeID = {}
        self.linesByTypeID = {}
        self.ConstructSkillNodes()
        self.ConstructLines()

    def ConstructSkillNodes(self):
        rootSkills = self.GetRootSkills()
        for i, skill in enumerate(rootSkills):
            self._ConstructSkillNodesRecursive(skill, 0, i, 0)

        for skill in rootSkills:
            bracket = self.bracketsByTypeID.get(skill.GetTypeID())
            bracket.UpdateBracketPosition()

    def _ConstructSkillNodesRecursive(self, skill, i, j, k, graphParent = None):
        if not self.NeedsConstructing(skill):
            return
        graphParent = self._ConstructSkillNode(skill, graphParent, i, j, k)
        k += 1
        children = self._GetChildrenForConstruction(skill)
        i = 0
        for child in children:
            if self.NeedsConstructing(child):
                self._ConstructSkillNodesRecursive(child, i, j, k, graphParent=graphParent)
                i += 1

    def _GetChildrenForConstruction(self, skill):
        children = skill.GetChildren()
        children = sorted(children, key=lambda node: sorted(node.GetDecendantsTypeIDs()))
        children = [ child for child in children if self.NeedsConstructing(child) ]
        return children

    def NeedsConstructing(self, child):
        return child.GetTypeID() not in self.bracketsByTypeID and self.IsInCurrentGroup(child)

    def _ConstructSkillNode(self, skill, graphParent, i, j, k):
        bracket = SkillTreeBracket(parent=self.bracketCont, curveSet=self.sceneContainer.bracketCurveSet, controller=skill, isInCurrGroup=self.IsInCurrentGroup(skill), currGroupID=self.currGroupID, onMouseEnter=self.OnNodeContMouseEnter, onMouseExit=self.OnNodeContMouseExit, idx=0)
        bracket.AddToGraph(graphParent, i, j, k)
        self.bracketsByTypeID[bracket.controller.GetTypeID()] = bracket
        return bracket

    def _GetSkillHorizontalSortKey(self, skill):
        numChildren = len([ child for child in skill.GetChildren() if self.IsInCurrentGroup(child) ])
        parentTypeIDs = sorted([ parent.GetTypeID() for parent in skill.GetParents() ])
        return (numChildren, parentTypeIDs)

    def IsInCurrentGroup(self, skill):
        return self.currGroupID in (ALL_GROUPS, skill.GetGroupID())

    def OnNodeContMouseExit(self, bracket):
        self._FadeAllLines(OPACITY_LINE_IDLE)
        for bracket in self.bracketsByTypeID.values():
            bracket.SetNormal()

    def OnNodeContMouseEnter(self, bracket):
        self._FadeAllLines(OPACITY_LINE_UNIMPORTANT)
        lineIDs = self._GetLineIDsForSubtree(bracket)
        for lineID in lineIDs:
            self._FadeLine(lineID, OPACITY_LINE_HOVER)

        self.lineSet.SubmitChanges()
        subtree = bracket.controller.GetSubtree()
        for b in self.bracketsByTypeID.values():
            if b.controller not in subtree:
                b.SetDeemphasized()
            else:
                b.SetEmphasized()

    def _GetLineIDsForSubtree(self, bracket):
        typeIDs = [ n.GetTypeID() for n in bracket.controller.GetSubtree() ]
        lines = set()
        for typeID1 in typeIDs:
            for typeID2 in typeIDs:
                lineID = self.GetLineID(typeID1, typeID2)
                if lineID is not None:
                    lines.add(lineID)

        return lines

    def _FadeAllLines(self, opacity):
        for lineID in self.GetAllLineIDs():
            self._FadeLine(lineID, opacity)

        self.lineSet.SubmitChanges()

    def _FadeLine(self, lineID, opacity):
        self.lineSet.ChangeLineColor(lineID, Color(*LINE_COLOR).SetOpacity(0.0).GetRGBA(), Color(*LINE_COLOR).SetOpacity(opacity).GetRGBA())

    def ConstructLines(self):
        self.lineSet.ClearLines()
        for nodeCont in self.bracketsByTypeID.values():
            for level, childNodes in nodeCont.controller.GetChildrenByLevel().iteritems():
                for childNode in childNodes:
                    childNodeCont = self.bracketsByTypeID.get(childNode.GetTypeID(), None)
                    if not childNodeCont:
                        continue
                    self._ConstructLine(nodeCont, childNodeCont, level)

        self.lineSet.SubmitChanges()

    def _ConstructLine(self, parNodeCont, childNodeCont, level):
        startPos = parNodeCont.projectBracket.trackPosition
        endPos = childNodeCont.projectBracket.trackPosition
        lineID = self.lineSet.AddStraightLine(startPos, Color(*LINE_COLOR).SetOpacity(0.0).GetRGBA(), endPos, LINE_COLOR, LINE_WIDTH)
        childTypeID = childNodeCont.controller.GetTypeID()
        parTypeID = parNodeCont.controller.GetTypeID()
        self.linesByTypeID[tuple(sorted((childTypeID, parTypeID)))] = lineID

    def GetLineID(self, typeID1, typeID2):
        return self.linesByTypeID.get(tuple(sorted((typeID1, typeID2))), None)

    def GetAllLineIDs(self):
        return self.linesByTypeID.values()

    def GetRootSkills(self):
        if self.currGroupID == ALL_GROUPS:
            skills = self.skillTreeDataProvider.GetAllSkills()
            skills = sorted(skills, key=lambda node: node.IsRoot())
            return [ skill for skill in skills if skill.IsRoot() ]
        else:
            skills = self.skillTreeDataProvider.GetSkillsByGroupID(self.currGroupID)
            skills = sorted(skills, key=lambda node: node.IsRoot())
            return [ skill for skill in skills if skill.IsRootOfGroup() ]
