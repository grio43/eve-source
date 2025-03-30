#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\circleNode.py
import math
import carbonui.const as uiconst
from carbonui import fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from careergoals.client.signal import on_goal_progress_changed, on_goal_completed
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.shared.careerPortal import careerConst
from eveexceptions import ExceptionEater
from signals.signalUtil import ChangeSignalConnect

class CircleNode(Transform):
    isDragObject = True

    def ApplyAttributes(self, attributes):
        super(CircleNode, self).ApplyAttributes(attributes)
        self.anchorPointX = self.width * 0.5
        self.anchorPointY = self.height * 0.5
        self.PrepareUI()
        self.ConnectSignals()

    def PrepareUI(self):
        raise NotImplementedError

    def ConnectSignals(self):
        for signal, func in self.GetSignals():
            signal.connect(func)

    def DisconnectSignals(self):
        for signal, func in self.GetSignals():
            signal.disconnect(func)

    def Close(self):
        self.DisconnectSignals()
        super(CircleNode, self).Close()

    def GetSignals(self):
        return [(on_goal_progress_changed, self.OnGoalUpdated), (on_goal_completed, self.OnGoalCompleted), (careerConst.CAREER_WINDOW_STATE_SETTING.on_change, self.OnCareerWindowStateChanged)]

    def OnCareerWindowStateChanged(self, state):
        pass

    def OnGoalUpdated(self, goalID, value):
        pass

    def OnGoalCompleted(self, goalID):
        pass

    def ResizeComponents(self, contSize, left, top, angle, animate = False):
        pass

    def UpdateAnchorPointsAndSize(self, contSize):
        raise NotImplementedError


TEXT_PADDING = 12

class CircleNodeWithText(CircleNode):
    default_state = uiconst.UI_NORMAL
    default_height = 150
    default_width = 150
    default_align = uiconst.CENTER

    def PrepareUI(self):
        self.textCont = NodeTextCont(name='textCont', parent=self, align=uiconst.CENTERTOP)
        self.iconCont = Container(name='iconCont', parent=self, align=uiconst.TOALL)
        self.ConstructFrame()
        self.ConstructIcon()

    def ConstructIcon(self):
        self.bgSprite = Sprite(name='bgSprite', parent=self.iconCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/circleView/nodeBg.png', state=uiconst.UI_DISABLED, opacity=0)

    def ConstructFrame(self):
        self.frame = Sprite(name='frameSprite', parent=self.iconCont, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/careerPortal/circleView/nodeFrame.png', state=uiconst.UI_DISABLED, opacity=1.0)

    def GetNameLabel(self):
        raise NotImplementedError

    def GetProgressLabel(self):
        raise NotImplementedError

    def IsCompleted(self):
        raise NotImplementedError

    def OnClick(self, *args):
        raise NotImplementedError

    def ResizeComponents(self, contSize, left, top, angle, animate = False):
        self.UpdateAnchorPointsAndSize(contSize)
        self.UpdateTextPos(angle)
        if animate:
            animations.MorphScalar(self, 'top', startVal=self.top, endVal=top, duration=careerConst.LEVEL_ANIMATION_DURATION)
            animations.MorphScalar(self, 'left', startVal=self.left, endVal=left, duration=careerConst.LEVEL_ANIMATION_DURATION)
        else:
            self.top = top
            self.left = left

    def UpdateAnchorPointsAndSize(self, contSize):
        self.height = self.width = contSize
        self.bgSprite.SetSize(self.width, self.height)
        self.anchorPointX = contSize / 2
        self.anchorPointY = contSize / 2

    def UpdateNode(self):
        self.textCont.UpdateLabels(self.GetNameLabel(), self.GetProgressLabel())
        if self.IsCompleted():
            self.SetCompletedState()
        else:
            self.SetNormalState()

    def OnMouseEnter(self, *args):
        self.SetHoverState()

    def OnMouseExit(self, *args):
        self.SetNormalState()

    def SetNormalState(self):
        if self.IsCompleted():
            return
        self.textCont.nameLabel.color = eveColor.WHITE
        self.textCont.progressLabel.color = eveColor.WHITE

    def SetHoverState(self):
        pass

    def SetCompletedState(self):
        self.textCont.nameLabel.color = eveColor.LEAFY_GREEN
        self.textCont.progressLabel.color = eveColor.LEAFY_GREEN

    def UpdateTextPos(self, angle):
        angleDegrees = math.degrees(angle + 0.5 * math.pi) % 360
        textAlign = uiconst.CENTER
        contAlign = uiconst.CENTERBOTTOM
        top = left = 0
        textWidth = self.textCont.GetWidth()
        textHeight = self.textCont.GetHeight()
        if 0 <= angleDegrees < 30 or 330 <= angleDegrees < 360:
            contAlign = uiconst.CENTERTOP
            top = -textHeight - 8
        elif 150 <= angleDegrees < 210:
            contAlign = uiconst.CENTERBOTTOM
            top = -textHeight - 8
        elif 30 <= angleDegrees < 150:
            textAlign = uiconst.CENTERLEFT
            contAlign = uiconst.CENTERRIGHT
            left = -textWidth - TEXT_PADDING
        elif 210 <= angleDegrees < 330:
            textAlign = uiconst.CENTERRIGHT
            contAlign = uiconst.CENTERLEFT
            left = -textWidth - TEXT_PADDING
        self.textCont.nameLabel.SetAlign(textAlign)
        self.textCont.progressLabel.SetAlign(textAlign)
        self.textCont.SetAlign(contAlign)
        self.textCont.SetPosition(left, top)


class NodeTextCont(ContainerAutoSize):
    nameLabelClass = EveLabelMedium
    progressLabelClass = EveLabelSmall

    def ApplyAttributes(self, attributes):
        super(NodeTextCont, self).ApplyAttributes(attributes)
        self.nameLabel = self.nameLabelClass(parent=ContainerAutoSize(parent=self, align=uiconst.TOTOP), name='nameLabel', align=uiconst.CENTER, bold=True)
        self.progressLabel = self.progressLabelClass(parent=ContainerAutoSize(parent=self, align=uiconst.TOTOP), name='progressLabel', align=uiconst.CENTER)

    def GetWidth(self):
        w, _ = self.nameLabel.MeasureTextSize(self.nameLabel.text)
        return w

    def GetHeight(self):
        _, nameHeight = self.nameLabel.MeasureTextSize(self.nameLabel.text)
        _, progressHeight = self.progressLabel.MeasureTextSize(self.progressLabel.text)
        return nameHeight + progressHeight

    def UpdateLabels(self, name, progress):
        self.nameLabel.text = name
        self.progressLabel.text = progress
        self.width = self.GetWidth()
