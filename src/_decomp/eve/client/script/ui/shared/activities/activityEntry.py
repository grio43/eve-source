#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\activities\activityEntry.py
import math
from carbonui.fontconst import STYLE_SMALLTEXT
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.util.color import Color
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMediumBold, EveStyleLabel
from eve.client.script.ui.shared.activities.activitiesUIConst import OPACITY_SELECTED, OPACITY_HOVER, ACTIVITY_ENTRY_HEIGHT, SCROLL_WIDTH, BADGE_COLOR, DEFAULT_DIAMETER, SCROLL_ELEMENT_INTRODUCE_WIDTH, SCROLL_ELEMENT_INTRODUCE_HEIGHT, SCROLL_ELEMENT_INTRODUCE_BOTTOM_PADDING, SCROLL_ELEMENT_INTRODUCE_RIGHT_PADDING, SCROLL_ELEMENT_TITLE_WIDTH, SCROLL_ELEMENT_TITLE_HEIGHT, SCROLL_ELEMENT_TITLE_TOP_PADDING, SCROLL_ELEMENT_ICON_PARENT_WIDTH, SCROLL_ELEMENT_ICON_WIDTH, SCROLL_ELEMENT_ICON_HEIGHT, SCROLL_ELEMENT_INTRODUCE_DISPLAY_WIDTH

class CountdownLabelBold(EveStyleLabel):
    __guid__ = 'uicontrols.CountdownLabelBold'
    default_name = 'EveLabelSmallBold'
    default_fontStyle = STYLE_SMALLTEXT
    default_fontsize = 8
    default_bold = True


class ActivityEntry(ContainerAutoSize):
    default_name = 'activityEntry'
    contentType = None
    default_state = uiconst.UI_NORMAL
    hasTimer = False
    isDragObject = True
    default_scalingCenter = (0.5, 0.5)
    default_opacity = 0.0
    default_minHeight = ACTIVITY_ENTRY_HEIGHT
    default_width = SCROLL_WIDTH
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(ActivityEntry, self).ApplyAttributes(attributes)
        self.isSelected = False
        self.ConstructData(attributes)
        self.ConstructBackground()
        self.ConstructIconContainer()
        self.ConstructMainContainer()
        self.ConstructBottomCont()
        self.ConstructIcon()
        self.ConstructContent()
        self.SetContent()
        self.ConstructRedDot()
        self.ConstructCountdown()
        self.AfterAllInitialize()

    def AfterAllInitialize(self):
        value = self.data.GetTimeLeftText()
        redDotOpacity = 1 if self.data.IsUnseen() else 0
        textOpacity = 0
        if value is not None:
            self.label.SetText(value)
            redDotOpacity = 0
            textOpacity = 1
        self._ShowText(textOpacity)
        self._ShowRedDot(redDotOpacity)

    def ConstructData(self, attributes):
        self.data = attributes.data
        self.activityID = self.data.GetID()
        self.service = sm.GetService('activities')

    def ConstructBackground(self):
        self.backgroundContainer = Container(name='backgroundContainer', bgParent=self, opacity=0.1)
        self.cornerTriangle = Sprite(name='cornerTriSmall', parent=self, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, opacity=0.3)
        StretchSpriteHorizontal(name='contentCardTop', parent=self.backgroundContainer, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', height=11, leftEdgeSize=9)
        StretchSpriteHorizontal(name='contentCardBot', parent=self.backgroundContainer, align=uiconst.TOBOTTOM_NOPUSH, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', height=11, rotation=math.pi, leftEdgeSize=9)
        self.strokeFrame = Frame(name='strokeFrame', parent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Stroke.png', opacity=0.1, cornerSize=9)
        self.selectedFill = Frame(name='selected', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', color=Color.WHITE, opacity=0.0, cornerSize=9)
        self.hoverFill = Frame(name='selected', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', color=Color.WHITE, opacity=0.0, cornerSize=9)
        Frame(name='bgFill', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', color=Color.BLACK, opacity=0.9, cornerSize=9)

    def ConstructIconContainer(self):
        leftCont = Container(name='iconCont', parent=self, align=uiconst.TOLEFT, width=SCROLL_ELEMENT_ICON_PARENT_WIDTH)
        self.iconCont = Container(name='iconCont', parent=leftCont, align=uiconst.CENTER, pos=(0,
         0,
         SCROLL_ELEMENT_ICON_WIDTH,
         SCROLL_ELEMENT_ICON_HEIGHT))

    def ConstructMainContainer(self):
        self.mainCont = Container(name='mainCont', parent=self, align=uiconst.TOTOP, width=SCROLL_ELEMENT_TITLE_WIDTH, height=SCROLL_ELEMENT_TITLE_HEIGHT, padTop=SCROLL_ELEMENT_TITLE_TOP_PADDING, clipChildren=True)

    def ConstructBottomCont(self):
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOBOTTOM, width=SCROLL_ELEMENT_INTRODUCE_WIDTH, height=SCROLL_ELEMENT_INTRODUCE_HEIGHT, padRight=SCROLL_ELEMENT_INTRODUCE_RIGHT_PADDING, padBottom=SCROLL_ELEMENT_INTRODUCE_BOTTOM_PADDING)
        Frame(bgParent=self.bottomCont, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=(0, 0, 0, 0.25))

    def ConstructIcon(self):
        iconSize = SCROLL_ELEMENT_ICON_WIDTH
        Sprite(name='icon', parent=self.iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0,
         0,
         iconSize,
         iconSize), texturePath=self.data.GetIconPath())

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructBottomLabel()

    def ConstructTitleLabel(self):
        self.titleLabel = EveLabelMediumBold(name='titleLabel', parent=self.mainCont, maxLines=1, width=SCROLL_ELEMENT_TITLE_WIDTH, left=4, align=uiconst.CENTERLEFT, color=(1, 1, 1, 1), state=uiconst.UI_NORMAL)
        self.titleLabel.OnClick = self.OnClick

    def ConstructBottomLabel(self):
        self.bottomLabel = EveLabelSmall(parent=self.bottomCont, width=SCROLL_ELEMENT_INTRODUCE_DISPLAY_WIDTH, name='bottomLabel', align=uiconst.CENTERLEFT, maxLines=1, padLeft=4)

    def SetContent(self):
        self.titleLabel.SetText(self.data.GetName())
        self.bottomLabel.SetText(self.data.GetIntroduce())

    def ConstructRedDot(self):
        self.badgeContainer = Container(name='badgeContainer', parent=self, padRight=8, padTop=8, align=uiconst.TOPRIGHT, width=DEFAULT_DIAMETER, height=DEFAULT_DIAMETER, opacity=0)
        self.frame = Frame(name='badgeFrame', bgParent=self.badgeContainer, texturePath='res:/UI/Texture/Shared/counterFrame.png', cornerSize=0, color=BADGE_COLOR)

    def ConstructCountdown(self):
        self.textContainer = Container(name='textContainer', parent=self, align=uiconst.TOPRIGHT, width=58, height=14, opacity=1, bgColor=BADGE_COLOR, idx=0)
        self.label = CountdownLabelBold(parent=self.textContainer, top=-1, align=uiconst.CENTER, color=Color.WHITE)

    def Select(self):
        self.isSelected = True
        animations.StopAllAnimations(self.selectedFill)
        animations.StopAllAnimations(self.cornerTriangle)
        animations.FadeTo(self.selectedFill, self.selectedFill.opacity, OPACITY_SELECTED, duration=0.4)
        animations.FadeTo(self.cornerTriangle, self.cornerTriangle.opacity, 1.0, duration=0.4)

    def Deselect(self):
        self.isSelected = False
        animations.StopAllAnimations(self.selectedFill)
        animations.StopAllAnimations(self.cornerTriangle)
        animations.FadeTo(self.selectedFill, self.selectedFill.opacity, 0.0, duration=0.4)
        animations.FadeTo(self.cornerTriangle, self.cornerTriangle.opacity, 0.3, duration=0.4)

    def OnMouseEnter(self, *args):
        sm.GetService('audio').SendUIEvent(uiconst.SOUND_ENTRY_HOVER)
        animations.StopAllAnimations(self.hoverFill)
        animations.FadeTo(self.hoverFill, self.hoverFill.opacity, OPACITY_HOVER, duration=0.1)

    def OnMouseExit(self, *args):
        animations.StopAllAnimations(self.hoverFill)
        animations.FadeTo(self.hoverFill, self.hoverFill.opacity, 0.0, duration=0.2)

    def AnimEnter(self, offsetIdx = 0):
        timeOffset = 0.05 * offsetIdx
        duration = 0.3
        animations.StopAllAnimations(self)
        animations.Tr2DScaleTo(self, (0.9, 0.9), (1.0, 1.0), duration=duration, timeOffset=timeOffset)
        animations.FadeIn(self, duration=2 * duration, timeOffset=timeOffset)

    def OnClick(self, *args):
        sm.GetService('audio').SendUIEvent('agency_window5_play')
        sm.GetService('audio').SendUIEvent(uiconst.SOUND_ENTRY_SELECT)
        self.OnEntrySelected(*args)

    def GetActivity(self):
        return self.data

    def _ShowRedDot(self, opacity = 1):
        self.badgeContainer.opacity = opacity

    def _ShowText(self, opacity = 1):
        self.textContainer.opacity = opacity

    def OnEntrySelected(self, *args):
        self.service.SelectActivity(self.activityID)
        self._ShowRedDot(0)
