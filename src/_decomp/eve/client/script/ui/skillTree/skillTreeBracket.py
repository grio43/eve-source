#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillTree\skillTreeBracket.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import TextColor, uiconst
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.bracket import Bracket
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.skillTree.skillTreeConst import ALL_GROUPS
import math
STEP_ANGLE = 0.4
STEP_Y = 1000
STEP_Z = 2000

class SkillTreeBracket(Bracket):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    isDragObject = True
    default_width = 200
    default_height = 60

    def ApplyAttributes(self, attributes):
        super(SkillTreeBracket, self).ApplyAttributes(attributes)
        self.skillQueueService = sm.GetService('skillqueue')
        self.skillService = sm.GetService('skills')
        self.graphParent = None
        self.graphChildren = []
        self.angle = 0.0
        self.controller = attributes.controller
        self.onDoubleClick = attributes.onDoubleClick
        self.onMouseEnter = attributes.onMouseEnter
        self.onMouseExit = attributes.onMouseExit
        certificateID = attributes.certificateID
        certificateLevel = attributes.certificateLevel
        requiredLevel = self.controller.GetCertificateRequiredSkillLevel(certificateID, certificateLevel)
        self.currGroupID = attributes.currGroupID
        self.mainCont = Container(name='mainCont', parent=self, padding=(10, 10, 10, 2))
        self.ConstructLabel(requiredLevel)
        self.skillBar = SkillBar(parent=self.mainCont, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED, skillID=self.controller.typeID, requiredLevel=requiredLevel, padTop=4)
        self.timeLabel = None
        self.bg = Container(name='bg', bgParent=self)
        PanelUnderlay(bgParent=self.bg, opacity=0.85)
        Fill(bgParent=self.bg, color=eveColor.SMOKE_BLUE if self.controller.IsRoot() else eveColor.BLACK, opacity=0.05)
        self.SetNormal()

    def ConstructLabel(self, requiredLevel):
        color = TextColor.NORMAL if self.controller.IsInjected() else TextColor.DISABLED
        if requiredLevel:
            text = self.controller.GetRequiredSkillNameAndLevelComparedToTrainedLevel(requiredLevel)
        else:
            text = '%s (%sx)' % (self.controller.GetName(), int(self.controller.GetRank()))
        if not self.IsInCurrentGroup():
            text += '\n<color=red>%s</color>' % self.controller.GetCategoryAndGroupName()
        self.label = EveLabelMedium(parent=self.mainCont, align=uiconst.TOTOP, text=text, color=color, autoFadeSides=10)

    def IsInCurrentGroup(self):
        return self.currGroupID in (ALL_GROUPS, self.controller.GetGroupID())

    def IsRoot(self):
        if self.currGroupID == ALL_GROUPS:
            return self.controller.IsRoot()
        else:
            return self.controller.IsRootOfGroup()

    def GetMenu(self):
        return self.controller.GetMenu()

    def GetDragData(self):
        return self.controller.GetDragData()

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        if self.onMouseEnter:
            self.onMouseEnter(self)

    def OnMouseExit(self):
        if self.onMouseExit:
            self.onMouseExit(self)

    def OnMouseDown(self, *args):
        super(SkillTreeBracket, self).OnMouseDown(*args)
        uicore.uilib.tooltipHandler.CloseTooltip()

    def OnDblClick(self):
        sm.GetService('info').ShowInfo(self.controller.GetTypeID())

    def SetNormal(self):
        if self.IsRoot() and self.currGroupID != ALL_GROUPS:
            self.width = 200
            self.height = 60
        else:
            self.width = self.height = 20
        self.bg.opacity = 1.0

    def SetEmphasized(self):
        self.bg.opacity = 1.0
        self.width = 200
        self.height = 60

    def SetDeemphasized(self):
        self.bg.opacity = 0.1
        self.width = self.height = 20

    def AddToGraph(self, graphParent, i, j, k):
        self.graphParent = graphParent
        if graphParent:
            graphParent.graphChildren.append(self)
        self.graphPos = (i, j, k)

    def SetRadialPos(self, radius, angle):
        self.radius = radius
        self.angle = angle

    def GetXYZ(self):
        _, j, k = self.graphPos
        self.angle = self._GetAngle(k)
        parX, _, parZ = self.GetParXYZPosition()
        x = parX + STEP_Z * math.cos(self.angle)
        y = j * STEP_Y
        z = parZ + STEP_Z * math.sin(self.angle)
        return (x, y, z)

    def _GetAngle(self, k):
        angle = self.GetBaseAngle()
        numSiblings = len(self.GetSiblings())
        i = self.GetSiblings().index(self)
        if numSiblings == 1:
            pass
        elif k == 1:
            angleStep = 2 * math.pi / numSiblings
            angle += i * angleStep
        else:
            angleStep = math.pi / 2 / (numSiblings - 1)
            angle += (i - (numSiblings - 1) / 2.0) * angleStep
        return angle

    def GetParXYZPosition(self):
        if self.graphParent:
            return self.graphParent.GetXYZPosition()
        else:
            return (0, 0, 0)

    def GetXYZPosition(self):
        return self.projectBracket.trackPosition

    def GetBaseAngle(self):
        if self.graphParent:
            return self.graphParent.angle
        else:
            return 0.0

    def UpdateBracketPosition(self):
        self.projectBracket.trackPosition = self.GetXYZ()
        for graphChild in self.graphChildren:
            graphChild.UpdateBracketPosition()

    def GetSiblings(self):
        if self.graphParent:
            return self.graphParent.graphChildren
        else:
            return [self]

    def GetHint(self):
        return repr(self.graphPos)
