#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\circleView.py
import math
import carbonui.const as uiconst
import telemetry
import trinity
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorlinetrace import DashedCircle
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.dpi import ScaleDpi
from carbonui.util.various_unsorted import GetWindowAbove
from careergoals.client.signal import on_goal_completed
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.shared.careerPortal.circleView.innerCircles import InnerCircles
from eveexceptions import EatsExceptions
from eveui import Sprite
MAX_CIRCLE_WIDTH = 800
GLOW_WIDTH = 220

class CircleViewContainer(Container):
    default_opacity = 0
    default_height = 800
    default_width = 800
    default_align = uiconst.CENTER

    def __init__(self, initialState, *args, **kwargs):
        super(CircleViewContainer, self).__init__(*args, **kwargs)
        self.initialState = initialState
        self.nodesByID = {}
        self.currentState = None
        self.PrepareUI()
        self.ConnectToSignals()
        self.OnCareerWindowStateChanged(initialState)

    def PrepareUI(self):
        wnd = GetWindowAbove(self)
        w, _ = wnd.GetAbsoluteSize()
        self.width = self.height = min(MAX_CIRCLE_WIDTH, w / 2)
        self.circleView = self.CreateCircleView(width=self.width, height=self.height)

    def CreateCircleView(self, *args, **kwargs):
        raise NotImplementedError

    def Close(self):
        self.DisconnectFromSignals()
        super(CircleViewContainer, self).Close()

    def GetSignals(self):
        return [(careerConst.CAREER_WINDOW_STATE_SETTING.on_change, self.OnCareerWindowStateChanged), (GetWindowAbove(self).on_end_scale, self.OnEndScale)]

    def OnEndScale(self, wnd):
        w, _ = wnd.GetAbsoluteSize()
        self.circleView.width = self.circleView.height = min(MAX_CIRCLE_WIDTH, w / 2)
        self.width = self.height = min(MAX_CIRCLE_WIDTH, w / 2)
        self.circleView.UpdateCircle()

    def OnCareerWindowStateChanged(self, newState, animate = True):
        raise NotImplementedError

    @EatsExceptions('CircleView::ConnectToSignals')
    def ConnectToSignals(self):
        for signal, callback in self.GetSignals():
            signal.connect(callback)

    @EatsExceptions('CircleView::DisconnectFromSignals')
    def DisconnectFromSignals(self):
        for signal, callback in self.GetSignals():
            signal.disconnect(callback)


class CircleView(Transform):
    default_height = 800
    default_width = 800
    default_align = uiconst.CENTER
    default_arc_opacity = 0.8
    default_scalingCenter = (0.5, 0.5)
    innerCircleTexturePath = 'res:/UI/Texture/classes/careerPortal/innerCircles.png'

    def ApplyAttributes(self, attributes):
        super(CircleView, self).ApplyAttributes(attributes)
        self.nodes = []
        self._initialized = False
        self.innerCircles = None
        self.outerCircle = None
        self.nodeParent = Container(name='nodeParent', parent=self, align=uiconst.TOALL)
        self.ConstructInnerCircles()
        self.fill = Sprite(name='fill', parent=self, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/circle_glow.png', state=uiconst.UI_DISABLED, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.5)
        on_goal_completed.connect(self.OnGoalCompleted)

    def Close(self):
        on_goal_completed.disconnect(self.OnGoalCompleted)
        super(CircleView, self).Close()

    def OnGoalCompleted(self, *args):
        if not self.nodes:
            return
        self.UpdateViewColor()

    def ConstructOuterCircle(self, radius):
        prevOpacity = 1
        if self.outerCircle is not None:
            prevOpacity = self.outerCircle.opacity
            self.outerCircle.Close()
        angle, dashSizeFactor, nodeCount = self.GetOuterCircleVariables(radius)
        self.outerCircle = DashedCircle(name='OuterCircle', parent=self, align=uiconst.CENTER, range=math.radians(360), lineWidth=ScaleDpi(2), radius=radius, glowBrightness=0.5, startAngle=angle, dashCount=nodeCount, dashSizeFactor=dashSizeFactor, opacity=prevOpacity)

    def GetOuterCircleVariables(self, radius):
        nodeCount = self._GetNodesCount()
        nodeSize = self.GetNodeSize()
        angle = self._GetAngleOffset() + 0 / float(nodeCount) * 2 * math.pi
        dashSizeFactor = (math.pi * (2 * radius) - nodeCount * nodeSize) / (nodeCount * nodeSize)
        return (angle, dashSizeFactor, nodeCount)

    def ConstructInnerCircles(self):
        if self.innerCircles is not None:
            self.innerCircles.Close()
        self.innerCircles = InnerCircles(parent=self, align=uiconst.CENTER, texturePath=self.innerCircleTexturePath, spriteEffect=trinity.TR2_SFX_MODULATE, state=uiconst.UI_DISABLED)

    def _GetViewColor(self):
        if any((not node.IsCompleted() for node in self.nodes)):
            return eveColor.WHITE
        else:
            return eveColor.LEAFY_GREEN

    def Reset(self):
        self.nodes = []
        self.nodeParent.Flush()

    def AddNode(self, node):
        self.nodes.append(node)
        node.SetParent(self.nodeParent)

    @telemetry.ZONE_METHOD
    def UpdateCircle(self):
        if not self.nodes:
            return
        size = self.width
        nodeSize = self.GetNodeSize()
        diameter = size - nodeSize
        radius = diameter * 0.5
        self.ConstructOuterCircle(radius)
        self.UpdateCircleMask()
        self.innerCircles.pos = (0,
         0,
         diameter - 10,
         diameter - 10)
        fillSize = diameter * 1.33
        self.fill.SetSize(fillSize, fillSize)
        self.UpdateViewColor()
        self.AdjustNodes(size, radius)

    def UpdateViewColor(self):
        viewColor = eveColor.Color(self._GetViewColor())
        self.fill.color = viewColor.SetOpacity(self.fill.opacity).GetRGBA()
        self.outerCircle.color = viewColor.SetOpacity(self.outerCircle.opacity).GetRGBA()

    def UpdateCircleMask(self):
        maskTexturePath = self._GetNodeMask()
        self.innerCircles.SetSecondaryTexturePath(maskTexturePath)
        self.innerCircles.scaleSecondary = self._GetInnerCircleScale()

    def _GetNodeMask(self):
        return 'res:/UI/Texture/classes/careerPortal/nodeMasks/%s_node_mask.png' % len(self.nodes)

    def _GetInnerCircleScale(self):
        if uicore.dpiScaling > 1.25:
            return (0.94, 0.94)
        return (0.91, 0.91)

    @staticmethod
    def _GetFillScale():
        scale = 900 / 730.0
        return (scale, scale)

    def OnAdjustSizeDone(self, radius):
        self.radius = radius

    @telemetry.ZONE_METHOD
    def AdjustNodes(self, size, radius):
        for i, nodeCont in enumerate(self.nodes):
            self.AdjustNode(nodeCont, i, size, radius)

    def AdjustNode(self, node, idx, size, radius, animate = False):
        nodeSize = self.GetNodeSize()
        left, top, angle = self._GetNodeContPositionFromSizeAndRadius(nodeSize, idx, radius)
        node.ResizeComponents(nodeSize, left, top, angle, animate)

    def _GetNodesCount(self):
        return len(self.nodes)

    def _GetNodeAngleMeasure(self, radius):
        if radius <= 0:
            return 0
        else:
            adjustment_radius = 0.5 * self.GetNodeSize() / radius
            try:
                node_angle_measure = 2.0 * math.asin(adjustment_radius)
            except ValueError:
                return 0

            return node_angle_measure

    def _GetArcAngleMeasure(self, nodeAngleMeasure):
        count = float(self._GetNodesCount())
        if count > 0:
            return (2 * math.pi - count * nodeAngleMeasure) / count
        return 2 * math.pi

    def _GetNodeContPositionFromSizeAndRadius(self, nodeSize, i, radius):
        angle = self._GetAngleOffset() + i / float(self._GetNodesCount()) * 2 * math.pi
        left = radius * math.cos(angle) + int(nodeSize / 2 - nodeSize / 2)
        top = radius * math.sin(angle) + int(nodeSize / 2 - nodeSize / 2)
        return (left, top, angle)

    def _GetAngleOffset(self):
        return -math.pi / 2

    def GetNodeSize(self):
        raise NotImplementedError

    def SetArcOpacity(self, opacity, duration, animate = True):
        if animate:
            animations.FadeTo(self.outerCircle, self.outerCircle.opacity, opacity, duration=duration)
        else:
            self.outerCircle.opacity = opacity
