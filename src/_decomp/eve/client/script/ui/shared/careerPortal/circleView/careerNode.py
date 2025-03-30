#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\careerNode.py
import math
import carbonui.const as uiconst
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui.control.button import Button
from carbonui import ButtonFrameType, ButtonVariant, Density
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from careergoals.client.career_goal_svc import get_career_goals_svc
from characterdata import careerpath, careerpathconst
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.donutSegment import DonutSegment
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from eve.client.script.ui.shared.careerPortal import cpSignals, careerConst
from eve.client.script.ui.shared.careerPortal.careerConst import LEVEL_ANIMATION_DURATION
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.careerPointsLabel import CareerPointsLabel
from eve.client.script.ui.shared.careerPortal.circleView.circleNode import CircleNode
from eve.client.script.ui.shared.careerPortal.link.dragData import NodeDragData
from eve.client.script.ui.util.uix import GetTextWidth, GetTextHeight, QtyPopup
from localization import GetByMessageID, GetByLabel
LABEL_CONTAINER_HEIGHT = 30
TEXT_CONT_TOP = 4
GLYPH_ICON_SIZE = 16
ICON_SIZE = 128
BG_PADDING = 180
NODE_MAX_SIZE = 180
ANIM_DURATION = 0.4

class CareerNode(CircleNode):
    default_name = 'CareerNode'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.CENTER
    isInCenter = False

    def GetMenu(self):
        if session and session.role & ROLE_GML:
            menu = [['QA: Complete', self._Debug_CompleteGoal], ['QA: Progress', self._Debug_ProgressGoal]]
            return menu

    def _Debug_CompleteGoal(self):
        get_career_goals_svc().get_goal_data_controller().admin_complete_goal(self.nodeObject.goal.goal_id)

    def _Debug_ProgressGoal(self):
        ret = QtyPopup(minvalue=0, setvalue=1, maxvalue=self.nodeObject.goal.definition.target_value)
        if ret and 'qty' in ret:
            get_career_goals_svc().get_goal_data_controller().admin_progress_goal(self.nodeObject.goal.goal_id, ret['qty'])

    def ApplyAttributes(self, attributes):
        self.nodeObject = attributes.nodeObject
        self.prevPos = None
        super(CareerNode, self).ApplyAttributes(attributes)
        progress, target = self.nodeObject.GetCareerPathProgress()
        self.iconGauge.SetGaugeValue(progress, target)
        self.iconGauge.UpdateGaugeColor(progress >= target)
        self.OnCareerWindowStateChanged(attributes.initialState)

    def GetSignals(self):
        signals = super(CareerNode, self).GetSignals()
        signals.extend([(cpSignals.on_career_node_hover_on, self.OnCareerNodeHoveredOn), (cpSignals.on_career_node_hover_off, self.OnCareerNodeHoveredOff)])
        return signals

    def PrepareUI(self):
        self.iconGauge = IconWithGauge(parent=self, align=uiconst.CENTERTOP, nodeObject=self.nodeObject)
        self.textCont = CardTextCont(name='textCont', parent=self, nodeObject=self.nodeObject)

    def OnGoalUpdated(self, goalID, value):
        if goalID != self.nodeObject.goal.goal_id:
            return
        if careerConst.CAREER_WINDOW_STATE_SETTING.get() != careerConst.CareerWindowState.CAREERS_VIEW and careerConst.SELECTED_CAREER_PATH_SETTING.get() != self.nodeObject.careerPathID:
            self.FadeIn(callback=lambda : self.FadeOut(timeOffset=1.5))
        progress, target = self.nodeObject.GetCareerPathProgress()
        self.iconGauge.SetGaugeValue(progress, target)

    def ResizeComponents(self, nodeSize, left, top, angle, animate = False):
        self.iconGauge.ResizeComponents(nodeSize, animate)
        self.textCont.top = self.iconGauge.height + TEXT_CONT_TOP
        newWidth = max(self.textCont.GetWidth(), self.iconGauge.gauge.width)
        textContHeight = self.textCont.GetHeight()
        newHeight = textContHeight + self.iconGauge.gauge.height + TEXT_CONT_TOP
        newAnchorY = newAnchorX = nodeSize / 2
        top += textContHeight / 2
        if self.IsSelected():
            self._GoToCenter()
        if animate:
            animations.MorphScalar(self, 'width', self.width, newWidth, duration=LEVEL_ANIMATION_DURATION)
            animations.MorphScalar(self, 'height', self.width, newHeight, duration=LEVEL_ANIMATION_DURATION)
            animations.MorphScalar(self, 'left', startVal=self.left, endVal=left, duration=careerConst.LEVEL_ANIMATION_DURATION)
            animations.MorphScalar(self, 'top', startVal=self.top, endVal=top, duration=careerConst.LEVEL_ANIMATION_DURATION)
            animations.MorphScalar(self, 'anchorPointX', self.anchorPointX, newAnchorX, duration=LEVEL_ANIMATION_DURATION)
            animations.MorphScalar(self, 'anchorPointY', self.anchorPointY, newAnchorY, duration=LEVEL_ANIMATION_DURATION)
        else:
            self.top = top
            self.left = left
            self.width = newWidth
            self.height = newHeight
            self.prevPos = (left,
             top,
             newWidth,
             newHeight)
            self.anchorPointY = newAnchorY
            self.anchorPointX = newAnchorY

    def IsSelected(self):
        careerID = careerConst.SELECTED_CAREER_PATH_SETTING.get()
        return careerID == self.nodeObject.careerPathID

    def OnCareerWindowStateChanged(self, state):
        careerID = careerConst.SELECTED_CAREER_PATH_SETTING.get()
        if state == careerConst.CareerWindowState.CAREERS_VIEW:
            self.Show()
            animations.FadeIn(self, duration=ANIM_DURATION)
            animations.Tr2DRotateTo(self, startAngle=self.rotation, endAngle=0)
            self.textCont.Show()
            animations.FadeIn(self.textCont, duration=ANIM_DURATION, callback=self.textCont.careerPointsLabel.Reset)
            if careerID == self.nodeObject.careerPathID:
                self._GoToCircle()
            else:
                self.Enable()
            animations.Tr2DScaleTo(self.iconGauge, startScale=self.iconGauge.scale, endScale=(1.0, 1.0))
        if state in (careerConst.CareerWindowState.ACTIVITIES_VIEW, careerConst.CareerWindowState.GOALS_VIEW):
            animations.Tr2DRotateTo(self, startAngle=self.rotation, endAngle=math.radians(-careerConst.CIRCLE_ROTATION_BY_CAREER[careerID]))
            animations.FadeOut(self.textCont, duration=0.2)
            if self.nodeObject.careerPathID == careerID:
                self._GoToCenter()
            else:
                self.Disable()
                animations.FadeOut(self, duration=ANIM_DURATION, callback=self.Hide)
                animations.Tr2DScaleTo(self.iconGauge, self.iconGauge.scale, (0.8, 0.8))

    def _GoToCircle(self):
        animations.MoveTo(self, self.pos, self.prevPos)
        textContHeight = self.textCont.GetHeight()
        newHeight = textContHeight + self.iconGauge.gauge.height + TEXT_CONT_TOP
        animations.MorphScalar(self, 'height', self.height, newHeight, duration=0.2)
        careerConst.SELECTED_CAREER_PATH_SETTING.set(careerpathconst.career_path_none)
        self.isInCenter = False

    def _GoToCenter(self):
        animations.MoveTo(self, startPos=self.pos, endPos=(0, 0))
        newHeight = self.iconGauge.width or 172
        animations.MorphScalar(self, 'height', self.height, newHeight, duration=0.2)
        animations.Tr2DScaleTo(self.iconGauge, startScale=self.iconGauge.scale, endScale=(1.5, 1.5))
        self.isInCenter = True

    def OnClick(self, *args):
        PlaySound('career_portal_select_profession_play')
        if careerConst.SELECTED_CAREER_PATH_SETTING.get() == self.nodeObject.careerPathID:
            currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
            if currentState == careerConst.CareerWindowState.GOALS_VIEW:
                newState = careerConst.CareerWindowState.ACTIVITIES_VIEW
            else:
                newState = careerConst.CareerWindowState.CAREERS_VIEW
            careerConst.CAREER_WINDOW_STATE_SETTING.set(newState)
        else:
            get_career_portal_controller_svc().select_career(self.nodeObject.careerPathID, self.nodeObject.goal.goal_id)

    def OnMouseEnter(self, *args):
        self.iconGauge.OnMouseEnter(*args)
        if self.IsAnimating():
            return
        PlaySound('career_portal_hover_profession_play')
        cpSignals.on_career_node_hover_on(self.nodeObject.careerPathID)

    def OnMouseExit(self, *args):
        self.iconGauge.OnMouseExit(*args)
        cpSignals.on_career_node_hover_off(self.nodeObject.careerPathID)

    def IsAnimating(self):
        return self.HasAnimation('left') or self.HasAnimation('top')

    def OnCareerNodeHoveredOn(self, careerPathID):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState != careerConst.CareerWindowState.ACTIVITIES_VIEW:
            return
        if careerPathID != self.nodeObject.careerPathID:
            self.Show()
            animations.FadeIn(self, duration=0.2)

    def OnCareerNodeHoveredOff(self, careerPathID):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState != careerConst.CareerWindowState.ACTIVITIES_VIEW:
            return
        if careerPathID != self.nodeObject.careerPathID:
            animations.FadeOut(self, duration=0.2, callback=self.Hide)

    def FadeIn(self, callback = None):
        animations.FadeIn(self, duration=ANIM_DURATION, callback=callback)

    def FadeOut(self, timeOffset = 0.0):
        animations.FadeOut(self, duration=ANIM_DURATION, timeOffset=timeOffset)

    def GetDragData(self):
        if self.nodeObject:
            return NodeDragData(self.nodeObject.careerPathID, None, None, self.nodeObject.careerPathName)


class CardTextCont(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP
    default_align = uiconst.CENTERTOP

    def ApplyAttributes(self, attributes):
        super(CardTextCont, self).ApplyAttributes(attributes)
        self.nodeObject = attributes.nodeObject
        self.careerInfoContainer = ContainerAutoSize(name='careerInfoContainer', parent=self, align=uiconst.TOTOP)
        nameLabelAndInfoContainer = Container(name='nameLabelAndInfoContainer', parent=self.careerInfoContainer, align=uiconst.TOTOP, height=LABEL_CONTAINER_HEIGHT)
        self.careerPathLabel = EveCaptionLarge(parent=nameLabelAndInfoContainer, name='careerPathLabel', align=uiconst.CENTER, state=uiconst.UI_DISABLED, bold=True, singleline=True, text=self.nodeObject.careerPathName)
        self.infoGlyphIcon = InfoGlyphIcon(parent=nameLabelAndInfoContainer, align=uiconst.CENTER)
        pointsContainer = Container(name='pointsContainer', parent=self.careerInfoContainer, align=uiconst.TOTOP, height=20)
        self.careerPointsLabel = CareerPointsLabel(parent=pointsContainer, careerNode=self.nodeObject)
        self.videoButton = Button(parent=Container(name='playButtonContainer', parent=self, align=uiconst.TOTOP, height=24, top=4), name='videoButton', align=uiconst.CENTER, label=GetByLabel('UI/CareerPortal/PlayVideo'), texturePath='res:/UI/Texture/classes/careerPortal/playVideo.png', func=self.PlayVideo, iconSize=GLYPH_ICON_SIZE, density=Density.COMPACT, variant=ButtonVariant.GHOST, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT)
        self.UpdateLabels()
        self.width = self.GetWidth()

    def UpdateLabels(self):
        self.infoGlyphIcon.left = self.careerPathLabel.width / 2 + GLYPH_ICON_SIZE
        self.infoGlyphIcon.hint = GetByLabel(careerConst.CAREER_DESCRIPTIONS.get(self.nodeObject.careerPathID, ''))

    def PlayVideo(self, *args):
        videoPath = careerConst.CAREER_VIDEOS.get(self.nodeObject.careerPathID, None)
        get_career_portal_controller_svc().play_video(videoPath)

    def GetWidth(self):
        careerLabelWidth = GetTextWidth(self.nodeObject.careerPathName, fontsize=self.careerPathLabel.fontsize, bold=True)
        return careerLabelWidth + self.infoGlyphIcon.width + GLYPH_ICON_SIZE + 4

    def GetHeight(self):
        careerLabelHeight = GetTextHeight(self.nodeObject.careerPathName, fontsize=self.careerPathLabel.fontsize, bold=True)
        pointsLabelHeight = GetTextHeight(self.nodeObject.GetCareerPathPointsText())
        totalHeight = careerLabelHeight + pointsLabelHeight + self.videoButton.parent.height + self.videoButton.parent.top * 2
        return totalHeight


class IconWithGauge(Transform):
    default_align = uiconst.CENTERTOP
    default_state = uiconst.UI_DISABLED
    default_bgGaugeOpacity = 0.15
    default_rotationCenter = (0.5, 0.5)
    default_scalingCenter = (0.5, 0.5)

    def ApplyAttributes(self, attributes):
        super(IconWithGauge, self).ApplyAttributes(attributes)
        self.nodeObject = attributes.nodeObject
        texturePath = self.nodeObject.iconTexturePath
        self.isSelected = False
        self.gauge = GaugeCircular(parent=self, name='gauge', align=uiconst.CENTER, lineWidth=4, clockwise=True, showMarker=False, glow=True, glowBrightness=0.5, bgPortion=0.997, idx=0, colorBg=Color(eveColor.CRYO_BLUE).SetBrightness(0.2).GetRGBA(), useMiddleGauge=True)
        self.icon = Sprite(parent=self, name='icon', align=uiconst.CENTER, texturePath=texturePath, state=uiconst.UI_DISABLED, width=ICON_SIZE, height=ICON_SIZE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, idx=1)

    def _SetupBackground(self):
        self.bgCont = Container(name='backgroundContainer', parent=self, align=uiconst.CENTER, bgTexturePath='res:/UI/Texture/classes/careerPortal/careerNodeHoverOff.png', bgOutputMode=uiconst.OUTPUT_COLOR_AND_GLOW, bgSpriteEffect=trinity.TR2_SFX_SOFTLIGHT, opacity=0.5)
        self.bgCont._bgSprite.glowBrightness = 0.3

    def ConstructLine(self, radius, lineWidth):
        return DonutSegment(parent=self, align=uiconst.CENTER, lineWidth=lineWidth, radius=radius, isClockwise=True)

    def ResizeComponents(self, nodeSize, animate):
        if animate:
            self._AnimateToNewSize(nodeSize)
        else:
            iconSize = nodeSize / 1.2
            bgSizeWithPadding = nodeSize * 2.2
            self.icon.SetSize(iconSize, iconSize)
            self.bgCont.SetSize(bgSizeWithPadding, bgSizeWithPadding)
            self.height = self.width = nodeSize
        radius = nodeSize / 2
        self.gauge.SetRadius(radius)

    def _AnimateToNewSize(self, nodeSize):
        animations.MorphScalar(self, 'height', self.height, nodeSize, duration=LEVEL_ANIMATION_DURATION)
        animations.MorphScalar(self, 'width', self.width, nodeSize, duration=LEVEL_ANIMATION_DURATION)
        iconSize = nodeSize / 1.2
        bgSizeWithPadding = nodeSize * 2.2
        animations.MorphScalar(self.icon, 'height', self.icon.height, iconSize, duration=LEVEL_ANIMATION_DURATION)
        animations.MorphScalar(self.icon, 'width', self.icon.width, iconSize, duration=LEVEL_ANIMATION_DURATION)
        animations.MorphScalar(self.bgCont, 'height', self.bgCont.height, bgSizeWithPadding, duration=LEVEL_ANIMATION_DURATION)
        animations.MorphScalar(self.bgCont, 'width', self.bgCont, bgSizeWithPadding, duration=LEVEL_ANIMATION_DURATION)

    def SetGaugeValue(self, value, maxValue):
        isGaugeFull = value >= maxValue
        self.gauge.SetValueWithMiddleGauge(float(value) / float(maxValue), lingerDurationSeconds=1.0, callback=lambda : self.UpdateGaugeColor(isGaugeFull))

    def UpdateGaugeColor(self, full):
        if full:
            animations.MorphScalar(self.gauge.gauge, 'glowBrightness', startVal=self.gauge.glowBrightness, endVal=1.0, curveType=uiconst.ANIM_OVERSHOT5)
            self.gauge.SetColor(eveColor.LEAFY_GREEN, eveColor.LEAFY_GREEN)
        else:
            self.gauge.SetColor(eveColor.CRYO_BLUE, eveColor.CRYO_BLUE)

    def OnMouseEnter(self, *args):
        animations.FadeTo(self.icon, self.icon.opacity, 1.4, duration=careerConst.HOVER_ANIMATION_DURATION)
        animations.FadeIn(self.bgCont, endVal=1.0, duration=careerConst.HOVER_ANIMATION_DURATION)

    def OnMouseExit(self, *args):
        animations.FadeTo(self.icon, self.icon.opacity, 1.0, duration=careerConst.HOVER_ANIMATION_DURATION)
        animations.FadeTo(self.bgCont, startVal=self.bgCont.opacity, endVal=0.5, duration=careerConst.HOVER_ANIMATION_DURATION)


class CareerNodeObject(object):

    def __init__(self, careerPathID):
        self.careerPathID = careerPathID
        self._careerPathName = None
        self.goal = get_career_goals_svc().get_goal_data_controller().get_career_path_goal(self.careerPathID)

    @property
    def iconTexturePath(self):
        return careerConst.ICON_BY_CAREER_ID.get(self.careerPathID, '')

    @property
    def careerPathName(self):
        if self._careerPathName is None:
            careerInfo = careerpath.get_career_path(self.careerPathID)
            self._careerPathName = GetByMessageID(careerInfo.nameID)
        return self._careerPathName

    def GetCareerPathPointsText(self):
        currentPoints = self.goal.progress
        maxPoints = self.goal.definition.target_value
        return GetByLabel('UI/CareerPortal/CareerPointsNumFull', currentPoints=currentPoints, totalPoints=maxPoints)

    def GetCareerPathProgress(self):
        return (self.goal.progress, self.goal.definition.target_value)
