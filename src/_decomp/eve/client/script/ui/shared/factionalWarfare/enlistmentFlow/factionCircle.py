#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\factionCircle.py
import math
from carbonui.uianimations import animations
from carbonui import const as uiconst, TextBody, TextAlign
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorlinetrace import DashedCircle
from carbonui.util.dpi import ScaleDpi
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.careerPortal.circleView.circleView import CircleView
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.backBtn import BackBtnFaction
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentConst import NODE_SIZE
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentUtil import GetFactionIcon, GetFactionColor
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.warzoneGaugeCont import WarzoneGaugeCont
from eve.common.script.util.facwarCommon import IsCombatEnemyFaction
WARZONE_GAUGE_SIZE = 61

class EnlistmentCircleView(CircleView):

    def ApplyAttributes(self, attributes):
        self.extraCircle = None
        self.enlistmentController = attributes.enlistmentController
        super(EnlistmentCircleView, self).ApplyAttributes(attributes)
        self.ConstructBackBtn()

    def ConstructBackBtn(self):
        nodeSize = self.GetNodeSize()
        self.backBtn = BackBtnFaction(parent=self, align=uiconst.CENTERRIGHT, pos=(0,
         0,
         nodeSize,
         nodeSize), idx=0, enlistmentController=self.enlistmentController)

    def LoadNodes(self, factionIDs):
        self.Reset()
        for factionID in factionIDs:
            node = FactionCircleNode(factionID=factionID, enlistmentController=self.enlistmentController)
            self.AddNode(node)

        self.UpdateCircle()

    def UpdateFaction(self, animate = True):
        self.UpdateViewColor()
        for node in self.nodes:
            node.factionPickerIcon.UpdateFrame()

        selectedFactionID = self.enlistmentController.selectedFactionID
        if selectedFactionID:
            if animate:
                animations.FadeOut(self.nodeParent, callback=self.nodeParent.Hide, duration=0.3)
            else:
                self.nodeParent.display = False
            self.backBtn.display = True
        else:
            self.nodeParent.opacity = 1.0
            self.nodeParent.display = True
            self.backBtn.display = False

    def ConstructOuterCircle(self, radius):
        pass

    def GetNodeSize(self):
        return ScaleDpi(NODE_SIZE)

    def _GetViewColor(self):
        factionID = self.enlistmentController.selectedFactionID or self.enlistmentController.hoveredFactionID
        if factionID:
            viewColor = GetFactionColor(factionID) or eveColor.WHITE
        else:
            viewColor = eveColor.WHITE
        return eveColor.Color(viewColor)

    def UpdateViewColor(self):
        viewColor = self._GetViewColor()
        self.fill.color = viewColor.SetOpacity(self.fill.opacity).GetRGBA()

    def MovingFinished(self):
        self.UpdateViewColor()


class EnlistmentCenterCont(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.CENTER
    default_width = 200
    default_height = 200
    default_pickRadius = 200
    centerText = ''

    def ApplyAttributes(self, attributes):
        super(EnlistmentCenterCont, self).ApplyAttributes(attributes)
        self.enlistmentController = attributes.enlistmentController
        gaugeRadius = WARZONE_GAUGE_SIZE + 8
        self.warzoneGaugeCont = WarzoneGaugeCont(parent=self, pos=(0,
         0,
         2 * gaugeRadius,
         2 * gaugeRadius), gaugeRadius=gaugeRadius, idx=0, showScore=False)
        self.centerIcon = Sprite(parent=self, align=uiconst.CENTER, texturePath='res:/ui/Texture/classes/frontlines/factionalwarfare_icon.png', pos=(0, 0, 64, 64))
        self.centerLabel = TextBody(parent=self, width=200, align=uiconst.CENTER, textAlign=TextAlign.CENTER)
        self.centerLabel.Hide()

    def OnMouseEnter(self, *args):
        if self.enlistmentController.isMovingCircle:
            return
        self.centerIcon.Hide()
        self.centerLabel.Show()

    def OnMouseExit(self, *args):
        self.centerIcon.Show()
        self.centerLabel.Hide()

    def ShowFaction(self, factionID):
        self.warzoneGaugeCont.ShowFaction(factionID)

    def LoadCenterText(self, text):
        self.centerLabel.text = text

    def LoadCenterIcon(self, texturePath):
        self.centerIcon.texturePath = texturePath


class BaseCircleNode(Transform):
    isDragObject = True
    default_align = uiconst.CENTER

    def ApplyAttributes(self, attributes):
        super(BaseCircleNode, self).ApplyAttributes(attributes)
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
        super(BaseCircleNode, self).Close()

    def GetSignals(self):
        return []

    def ResizeComponents(self, contSize, left, top, angle, animate = False):
        pass

    def UpdateAnchorPointsAndSize(self, contSize):
        raise NotImplementedError


class FactionCircleNode(BaseCircleNode):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.factionID = attributes.factionID
        self.enlistmentController = attributes.enlistmentController
        self.angle = 0
        super(FactionCircleNode, self).ApplyAttributes(attributes)

    def PrepareUI(self):
        self.iconCont = Container(name='iconCont', parent=self, align=uiconst.TOALL)
        self.ConstructFrame()
        self.ConstructIcon()

    def ConstructIcon(self):
        self.bgSprite = Sprite(name='bgSprite', parent=self.iconCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/Classes/Enlistment/circle/darkCircle.png', state=uiconst.UI_DISABLED, opacity=1.0)
        self.factionPickerIcon = FactionPickerIcon(parent=self.iconCont, enlistmentController=self.enlistmentController, idx=0, factionID=self.factionID, align=uiconst.TOALL)

    def ConstructFrame(self):
        self.frame = Sprite(name='frameSprite', parent=self.iconCont, align=uiconst.TOALL, texturePath='', state=uiconst.UI_DISABLED, opacity=0.0)

    def ResizeComponents(self, nodeSize, left, top, angle, animate = False):
        self.top = top
        self.left = left
        self.width = nodeSize
        self.height = nodeSize
        self.angle = angle
        self.UpdateIconSize(nodeSize)

    def UpdateIconSize(self, nodeSize):
        self.factionPickerIcon.UpdateIconSize(nodeSize)
        self.bgSprite.SetSize(2 * nodeSize, 2 * nodeSize)

    def OnMouseEnter(self, *args):
        if self.enlistmentController.isMovingCircle:
            return
        self.enlistmentController.on_mouse_enter(self.factionID)
        self.factionPickerIcon.TryShowFrame()

    def OnMouseExit(self, *args):
        if self.enlistmentController.isMovingCircle:
            return
        self.enlistmentController.on_mouse_exit(self.factionID)
        self.factionPickerIcon.TryHideFrame()

    def OnClick(self, *args):
        self.enlistmentController.on_node_clicked(self.factionID)
        self.factionPickerIcon.UpdateFrame()

    def ChangeFrameDisplay(self, show = True):
        if show:
            self.frame.Show()
        else:
            self.frame.Hide()


class FactionPickerIcon(Transform):
    default_align = uiconst.CENTER

    def ApplyAttributes(self, attributes):
        self.enlistmentController = attributes.enlistmentController
        super(FactionPickerIcon, self).ApplyAttributes(attributes)
        self.factionID = attributes.factionID
        texturePath = GetFactionIcon(self.factionID)
        textureColor = GetFactionColor(self.factionID) or eveColor.WHITE
        self.factionIcon = Sprite(name='factionIcon', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 0, 0), texturePath=texturePath, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0)
        self.mouseOverFrame = Sprite(name='mouseOverFrame', parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/Classes/Enlistment/hoverCircle.png', state=uiconst.UI_DISABLED, opacity=1.0, color=textureColor, padding=-4)
        self.mouseOverFrame.Hide()
        self.enemeyFrame = Sprite(name='enemeyFrame', parent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/Classes/Enlistment/hoverCircle.png', state=uiconst.UI_DISABLED, opacity=0.5, color=textureColor)
        self.enemeyFrame.Hide()

    def UpdateIconSize(self, nodeSize):
        iconSize = nodeSize / 1.2
        self.factionIcon.SetSize(iconSize, iconSize)

    def TryShowFrame(self):
        self.mouseOverFrame.Show()
        self.mouseOverFrame.opacity = 1.0

    def TryHideFrame(self):
        if self.factionID not in (self.enlistmentController.hoveredFactionID, self.enlistmentController.selectedFactionID):
            self.mouseOverFrame.Hide()

    def UpdateFrame(self):
        isFactionIsHighlighted = bool(self.enlistmentController.hoveredFactionID or self.enlistmentController.selectedFactionID)
        self.opacity = 1.0
        if self.factionID in (self.enlistmentController.hoveredFactionID, self.enlistmentController.selectedFactionID):
            self.mouseOverFrame.Show()
            self.mouseOverFrame.opacity = 1.0
        elif IsCombatEnemyFaction(self.factionID, self.enlistmentController.hoveredFactionID) or IsCombatEnemyFaction(self.factionID, self.enlistmentController.hoveredFactionID):
            self.mouseOverFrame.Show()
            self.mouseOverFrame.opacity = 0.5
        else:
            self.mouseOverFrame.Hide()
            if isFactionIsHighlighted:
                self.opacity = 0.3
