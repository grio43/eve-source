#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\ui\uipointer.py
import carbonui.const as uiconst
from carbonui.primitives.base import ScaleDpiF
from carbonui.primitives.blurredbackgroundsprite import BlurredBackgroundSprite
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from math import pi
from signals.signal import Signal
from trinity import TR2_SFX_COPY, TR2_SFX_COLOROVERLAY, TR2_SBM_BLEND, TR2_SBM_ADD, TR2_SBM_ADDX2
from uihighlighting.ui.uipointertext import PointerTextContainer
import uthread
UIPOINTER_WIDTH = 276
UIPOINTER_HEIGHT = 36
CONTENT_CONTAINER_PADDING = 10
POINTER_ARROW_WIDTH = 24
POINTER_ARROW_HEIGHT = 32
ARROW_V_OFFSET = 1
ARROW_H_OFFSET = 4
BRACKET_LOOP_VIDEO = 'res:/UI/Texture/classes/HighlightTool/HighlightRing_Loop.webm'
POINTER_ARROW_VIDEO = 'res:/UI/Texture/classes/HighlightTool/HighlightArrow_Loop.webm'
POINTER_ARROW_TEXTURE = 'res:/UI/Texture/classes/HighlightTool/highlightBoxArrow.png'
POINTER_ARROW_COLOR = (172 / 255.0,
 213 / 255.0,
 241 / 255.0,
 1.0)
POINTER_ARROW_GLOW_WIDTH = 36
POINTER_ARROW_GLOW_HEIGHT = 28
POINTER_ARROW_GLOW_TEXTURE = 'res:/UI/Texture/classes/HighlightTool/highlightBoxArrowGlow.png'
POINTER_ARROW_GLOW_COLOR = (0 / 255.0,
 86 / 255.0,
 141 / 255.0,
 1.0)
POINTER_SIDE_BAR_WIDTH = 36
POINTER_SIDE_BAR_HEIGHT = 3
POINTER_SIDE_BAR_TEXTURE = 'res:/UI/Texture/classes/ConversationUI/sideDecoration.png'
POINTER_SIDE_BAR_COLOR = (172 / 255.0,
 213 / 255.0,
 241 / 255.0,
 1.0)
POINTER_SIDE_BAR_GLOW_WIDTH = 56
POINTER_SIDE_BAR_GLOW_HEIGHT = 23
POINTER_SIDE_BAR_TEXTURE_GLOW = 'res:/UI/Texture/classes/ConversationUI/sideDecorationGlow.png'
POINTER_SIDE_BAR_GLOW_COLOR = (0 / 255.0,
 86 / 255.0,
 141 / 255.0,
 1.0)
FRAME_TEXTURE = 'res:/UI/Texture/classes/HighlightTool/highlightBox.png'
FRAME_CORNER_SIZE = 2
BACKGROUND_BLUR_COLOR = (1.0,
 1.0,
 1.0,
 0.9)
BACKGROUND_GLOW_FRAME_TEXTURE = 'res:/UI/Texture/classes/ConversationUI/auraWindowGlow.png'
BACKGROUND_GLOW_FRAME_CORNER_SIZE = 32
BACKGROUND_GLOW_FRAME_OUTER_PADDING = 16
DEFAULT_USE_ARROW_POINTER = False
DEFAULT_USE_SIDE_BAR = True
DEFAULT_USE_BLINK = True
OPACITY_DEFAULT = 1.0
OPACITY_MOUSE_OVER = 0.5
OPACITY_FADE_DURATION_SEC = 0.5

class BaseUiPointer(Container):

    def ApplyAttributes(self, attributes):
        self.pointToElement = attributes.get('pointToElement')
        super(BaseUiPointer, self).ApplyAttributes(attributes)

    def UpdatePointToElement(self, pointToElement):
        self.pointToElement = pointToElement

    def ConstructContent(self):
        raise NotImplementedError('Must implement ConstructContent in derived class of BaseUiPointer')


class UiPointer(BaseUiPointer):

    def ApplyAttributes(self, attributes):
        super(UiPointer, self).ApplyAttributes(attributes)
        basicData = attributes.basicData
        self.text = getattr(basicData, 'uiPointerText', attributes.get('text', None))
        self.title = getattr(basicData, 'uiPointerTitle', attributes.get('title', None))
        self.texturePath = getattr(basicData, 'texturePath', None)
        self.textureSize = getattr(basicData, 'textureSize', None)
        self.iconColor = getattr(basicData, 'iconColor', None)
        self.useArrowPointer = attributes.get('useArrowPointer', DEFAULT_USE_ARROW_POINTER)
        self.pointDirections = attributes.get('pointDirections', (0, 0, 0))
        self.arrowPositionModifier = attributes.get('arrowPositionModifier', 0)
        self.blinkSprite = None
        self.transform = Transform(parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5))
        self.innerCont = Container(parent=self.transform, align=uiconst.TOALL, name='innerCont')
        self.contentCont = Container(parent=self.innerCont, align=uiconst.TOLEFT, name='contentCont', width=0, height=0, padding=CONTENT_CONTAINER_PADDING, opacity=0.0)
        self.onOpacityChanged = Signal(signalName='onOpacityChanged')

    def ConstructContent(self):
        self._ConstructMainContent()
        self.CorrectSize()
        if self.useArrowPointer:
            self.AddArrow()
        self.AddSideBar()
        self.AddFrameAndBackgroundGlow()
        self.AddBlinkFill()
        self.AddBlinkSprite()
        self.AnimEntry()

    def _ConstructMainContent(self):
        self.textContainer = PointerTextContainer(parent=self.contentCont, align=uiconst.TOLEFT, name='textContainer', width=self.GetTextWidth(), height=0, title=self.title, text=self.text, texturePath=self.texturePath, iconSize=self.textureSize, iconColor=self.iconColor)

    def OnMouseEnter(self, *args):
        self.SetPointerOpacity(OPACITY_MOUSE_OVER)

    def OnMouseExit(self, *args):
        self.SetPointerOpacity(OPACITY_DEFAULT)

    def SetPointerOpacity(self, opacity):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=opacity, duration=OPACITY_FADE_DURATION_SEC)
        self.onOpacityChanged(opacity)

    def GetTextWidth(self):
        textWidth = self.width - self.contentCont.padLeft - self.contentCont.padRight
        return textWidth

    def CorrectSize(self, contentWidth = None, contentHeight = None):
        self.contentCont.width = contentWidth or self.textContainer.width
        self.contentCont.height = contentHeight or self.textContainer.height
        arrowWidth = 0
        arrowHeight = 0
        if self.useArrowPointer:
            pointUp, pointDown, pointLeft = self.pointDirections
            if pointUp or pointDown:
                arrowHeight = POINTER_ARROW_HEIGHT
            else:
                arrowWidth = POINTER_ARROW_WIDTH
        self.width = self.contentCont.width + self.contentCont.padLeft + self.contentCont.padRight + arrowWidth
        self.height = max(UIPOINTER_HEIGHT, self.contentCont.height + self.contentCont.padTop + self.contentCont.padBottom + arrowHeight)

    def AddArrow(self):
        upDownLeft = self.width / 2 - POINTER_ARROW_WIDTH / 2 - ARROW_H_OFFSET + self.arrowPositionModifier
        leftRightTop = self.height / 2 - POINTER_ARROW_HEIGHT / 2 + ARROW_V_OFFSET + self.arrowPositionModifier
        pointUp, pointDown, pointLeft = self.pointDirections
        arrowSpriteWidth = POINTER_ARROW_WIDTH
        arrowSpriteHeight = POINTER_ARROW_HEIGHT
        arrowGlowSpriteWidth = POINTER_ARROW_GLOW_WIDTH
        arrowGlowSpriteHeight = POINTER_ARROW_GLOW_HEIGHT
        arrowSpriteTop = arrowSpriteLeft = 0
        arrowSpriteRotation = 0
        arrowGlowSpriteTop = 0
        arrowGlowSpriteLeft = 0
        if pointUp or pointDown:
            arrowSpriteLeft = upDownLeft
            arrowSpriteWidth = POINTER_ARROW_HEIGHT
            arrowSpriteHeight = POINTER_ARROW_WIDTH
            if pointUp:
                arrowSpriteRotation = pi / 2
                arrowSpriteTop = 0
                self.innerCont.padTop = arrowSpriteHeight
                arrowGlowSpriteTop = arrowSpriteTop + arrowSpriteHeight / 2
                arrowGlowSpriteLeft = arrowSpriteLeft + arrowSpriteWidth / 2 - arrowGlowSpriteWidth / 2
            elif pointDown:
                arrowSpriteRotation = -pi / 2
                arrowSpriteTop = self.height - arrowSpriteHeight
                self.innerCont.padBottom = arrowSpriteHeight
                arrowGlowSpriteTop = arrowSpriteTop - arrowSpriteHeight / 2
                arrowGlowSpriteLeft = arrowSpriteLeft + arrowSpriteWidth / 2 - arrowGlowSpriteWidth / 2
        else:
            arrowSpriteTop = leftRightTop
            arrowGlowSpriteWidth = POINTER_ARROW_GLOW_HEIGHT
            arrowGlowSpriteHeight = POINTER_ARROW_GLOW_WIDTH
            if pointLeft:
                arrowSpriteRotation = pi
                arrowSpriteLeft = 0
                self.innerCont.padLeft = arrowSpriteWidth
                arrowGlowSpriteTop = arrowSpriteTop + arrowSpriteHeight / 2 - arrowGlowSpriteHeight / 2
                arrowGlowSpriteLeft = arrowSpriteLeft + arrowSpriteWidth / 2
            else:
                arrowSpriteRotation = 0
                arrowSpriteLeft = self.width - arrowSpriteWidth
                self.innerCont.padRight = arrowSpriteWidth
                arrowGlowSpriteTop = arrowSpriteTop + arrowSpriteHeight / 2 - arrowGlowSpriteHeight / 2
                arrowGlowSpriteLeft = arrowSpriteLeft - arrowSpriteWidth / 2
        self.arrowSprite = StreamingVideoSprite(name='arrowSprite', parent=self.transform, videoPath=POINTER_ARROW_VIDEO, width=arrowSpriteWidth, height=arrowSpriteHeight, align=uiconst.TOPLEFT, top=arrowSpriteTop, left=arrowSpriteLeft, state=uiconst.UI_DISABLED, color=POINTER_ARROW_COLOR, blendMode=TR2_SBM_ADD, spriteEffect=TR2_SFX_COLOROVERLAY, videoLoop=True, disableAudio=True)
        self.arrowSprite.Pause()
        self.arrowSprite.rotation = arrowSpriteRotation
        self.arrowSprite.OnVideoFinished = self._PlayLoop()
        arrowGlowSprite = Sprite(parent=self.transform, name='arrowGlowSprite', texturePath=POINTER_ARROW_GLOW_TEXTURE, width=arrowGlowSpriteWidth, height=arrowGlowSpriteHeight, align=uiconst.ANCH_TOPLEFT, top=arrowGlowSpriteTop, left=arrowGlowSpriteLeft, rotation=arrowSpriteRotation, blendMode=TR2_SBM_ADD, color=POINTER_ARROW_GLOW_COLOR)
        r, g, b, a = POINTER_ARROW_GLOW_COLOR
        uicore.animations.SpColorMorphTo(arrowGlowSprite, startColor=(r,
         g,
         b,
         1.5), endColor=(r,
         g,
         b,
         0.5), duration=1.5, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def _PlayLoop(self):
        self.arrowSprite.opacity = 1.0
        self.arrowSprite.Play()

    def AddSideBar(self):
        if not DEFAULT_USE_SIDE_BAR:
            return
        sideBarSpriteRotation = pi / 2.0
        Sprite(name='sideBarSprite', parent=self.innerCont, texturePath=POINTER_SIDE_BAR_TEXTURE, top=1, width=POINTER_SIDE_BAR_WIDTH, height=POINTER_SIDE_BAR_HEIGHT, align=uiconst.CENTERTOP, rotation=sideBarSpriteRotation, state=uiconst.UI_DISABLED, color=POINTER_SIDE_BAR_COLOR, blendMode=TR2_SBM_ADD)
        Sprite(name='sideBarSpriteGlow', parent=self.innerCont, texturePath=POINTER_SIDE_BAR_TEXTURE_GLOW, top=1, width=POINTER_SIDE_BAR_GLOW_WIDTH, height=POINTER_SIDE_BAR_GLOW_HEIGHT, align=uiconst.CENTERTOP, rotation=sideBarSpriteRotation, blendMode=TR2_SBM_ADD, color=POINTER_SIDE_BAR_GLOW_COLOR)

    def AddFrameAndBackgroundGlow(self):
        self.backgroundAndFrameContainer = Container(parent=self.transform, align=uiconst.TOALL, name='backgroundAndFrameContainer', padding=self.innerCont.padding)
        backgroundContainer = Container(parent=self.backgroundAndFrameContainer, align=uiconst.TOALL, name='backgroundContainer', padding=-BACKGROUND_GLOW_FRAME_OUTER_PADDING)
        cornerSize = int(ScaleDpiF(BACKGROUND_GLOW_FRAME_CORNER_SIZE))
        Frame(bgParent=backgroundContainer, name='backgroundGlowFrame', align=uiconst.TOALL, texturePath=BACKGROUND_GLOW_FRAME_TEXTURE, cornerSize=cornerSize, blendMode=TR2_SBM_ADD)
        frameContainer = Container(parent=self.backgroundAndFrameContainer, align=uiconst.TOALL, name='frameContainer')
        Frame(bgParent=frameContainer, name='highlightBox', texturePath=FRAME_TEXTURE, cornerSize=FRAME_CORNER_SIZE)
        BlurredBackgroundSprite(bgParent=frameContainer, name='backgroundBlur', color=BACKGROUND_BLUR_COLOR, width=frameContainer.width, height=frameContainer.height)

    def AddBlinkFill(self):
        if not DEFAULT_USE_BLINK:
            return
        self.blinkFill = Fill(bgParent=self.innerCont, name='blinkFill', state=uiconst.UI_DISABLED, blendMode=TR2_SBM_ADD, color=(1, 1, 1, 0))

    def AddBlinkSprite(self):
        if not DEFAULT_USE_BLINK:
            return
        self.blinkSprite = Sprite(bgParent=self.innerCont, name='blinkSprite', texturePath='res:/UI/Texture/classes/Neocom/buttonDown.png', state=uiconst.UI_DISABLED, blendMode=TR2_SBM_ADD, color=(1, 1, 1, 0))

    def AnimEntry(self):
        uthread.new(self._AnimEntry)

    def _AnimEntry(self):
        uicore.animations.Tr2DScaleTo(obj=self.transform, startScale=(1.0, 0.0), endScale=(1.0, 1.0), duration=0.1)
        if self.blinkFill and self.blinkSprite:
            uicore.animations.FadeTo(obj=self.blinkFill, startVal=0.75, endVal=0.0, duration=0.1, timeOffset=0.0, loops=2, sleep=True)
            uicore.animations.SpColorMorphTo(obj=self.blinkFill, startColor=self.blinkFill.GetRGBA(), endColor=(0, 0, 0, 0), duration=0.1)
        animations.FadeTo(self.contentCont, 0.0, 1.0, duration=0.3, timeOffset=0.1, sleep=True)
        self.blinkSprite.opacity = 0.5
        uicore.animations.SpSwoopBlink(self.blinkSprite, rotation=pi - 0.5, duration=3.0, loops=uiconst.ANIM_REPEAT, timeOffset=1.0)


class CustomUiPointer(UiPointer):
    default_name = 'CustomUiPointer'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(CustomUiPointer, self).ApplyAttributes(attributes)
        self._content = attributes.highlightContent
        self.textContainer = None
        self.pickState = uiconst.TR2_SPS_ON

    def _ConstructMainContent(self):
        if self._content:
            self.textContainer = self._content
            self.textContainer.SetParent(self.contentCont)

    def OnMouseEnter(self, *args):
        pass

    def OnMouseExit(self, *args):
        pass

    def Close(self):
        if self.textContainer:
            self.textContainer.SetParent(None)
        super(CustomUiPointer, self).Close()


class UiPointerData(object):

    def __init__(self, uiPointerElement, pointToElement, considerations, oldPointLeft, oldPointUp, oldPointDown, basicData):
        self.uiPointerElement = uiPointerElement
        self.pointToElement = pointToElement
        self.considerations = considerations
        self.oldPointLeft = oldPointLeft
        self.oldPointUp = oldPointUp
        self.oldPointDown = oldPointDown
        self.basicData = basicData


class PointerBasicData(object):

    def __init__(self, pointToID, defaultDirection, **kwargs):
        self.pointToID = pointToID
        self.defaultDirection = defaultDirection
        self.uiPointerTitle = None
        self.uiPointerText = None
        self.offset = 0
        self.audioSetting = False
        self.shouldPrioritizeVisible = False
        self.texturePath = None
        self.textureSize = None
        self.iconColor = None
        self.highlightContent = None
        self.showEvenOffscreen = False
        self.uiClass = None
        self.pointerIDx = -1
        self.__dict__.update(kwargs)
