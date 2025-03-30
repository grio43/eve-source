#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\UI\bracketBorderWindow.py
import math
import trinity
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipDescriptionWrapper
from carbonui.control.window import Window
from carbonui.control.buttonIcon import ButtonIcon
from uthread2 import StartTasklet
SPRITE_OPACITY = 0.2
IMG_HEIGHT = 400
MOUSE_ENTER_EXIT_DURATION = 0.3

class BracketBorderWindow(Window):
    default_name = 'BracketBorderWindow'
    default_fixedWidth = 950
    default_fixedHeight = 550
    default_isLightBackgroundConfigurable = False
    default_isMinimizable = False
    default_isCollapseable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_border_opacity = 0.35
    default_background_image = None
    default_on_open_callback = None
    default_on_close_callback = None
    mainContentWidth = 770
    mainContentHeight = 415
    bracketWidth = 910
    bracketHeadWidth = 260
    innerContWidth = 892
    innerContHeight = 500
    bottomBracketOffset = 46
    openingDurationSec = 0.3
    openingDuration2Sec = 0.3
    closingDurationSec = 0.28
    closingDuration2Sec = 0.28
    fadeOutDurationSec = 0.1
    fadeInDurationSec = 0.3

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.borderOpacity = attributes.get('borderOpacity', self.default_border_opacity)
        self.backgroundImage = attributes.get('backgroundImage', self.default_background_image)
        self.onOpenCallback = attributes.get('onOpenCallback', self.default_on_open_callback)
        self.onCloseCallback = attributes.get('onCloseCallback', self.default_on_close_callback)
        self.sr.headerParent.Hide()
        self.HideBackground()
        self.outerCont = Container(name='outerCont', parent=self.sr.main, state=uiconst.UI_PICKCHILDREN, opacity=1, padding=2, clipChildren=True)
        self.innerCont = Container(name='innerCont', parent=self.outerCont, align=uiconst.CENTERTOP, height=self.innerContHeight, width=self.innerContWidth, opacity=0, bgColor=(0, 0, 0, 0.5))
        self.frameCont = Container(name='contentCont', parent=self.innerCont, align=uiconst.CENTER, width=self.mainContentWidth, height=self.mainContentHeight)
        self.ConstructBracketFrame()
        self.ConstructContent()
        self.ConstructInnerFrame()
        self._AnimEnter()
        if callable(self.onOpenCallback):
            StartTasklet(self.onOpenCallback)

    def ConstructContent(self):
        pass

    def ConstructBracketFrame(self):
        self.topBracketContainer = Container(name='topBracketCont', parent=self.outerCont, align=uiconst.CENTERTOP, width=self.bracketWidth, height=7, opacity=self.borderOpacity, idx=0)
        self.topBracketTail = StretchSpriteHorizontal(name='topSpriteBracket', parent=self.topBracketContainer, align=uiconst.CENTERTOP, width=self.bracketWidth, height=7, leftEdgeSize=16, rightEdgeSize=16, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/bracketTails_Window.png')
        self.topBracketHead = StretchSpriteHorizontal(name='topSpriteHead', parent=self.topBracketContainer, align=uiconst.CENTERTOP, width=self.bracketHeadWidth, height=5, leftEdgeSize=16, rightEdgeSize=16, top=1, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/bracketHead_Window.png')
        self.bottomBracketContainer = Container(name='bottomBracketCont', parent=self.outerCont, align=uiconst.CENTERBOTTOM, width=self.bracketWidth, height=7, top=self.bottomBracketOffset, opacity=self.borderOpacity, idx=0)
        self.bottomBracketTail = StretchSpriteHorizontal(name='bottomSpriteBracket', parent=self.bottomBracketContainer, align=uiconst.CENTERBOTTOM, width=self.bracketWidth, height=7, leftEdgeSize=16, rightEdgeSize=16, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/bracketTails_Window.png', rotation=math.pi)
        self.bottomBracketHead = StretchSpriteHorizontal(name='bottomSpriteHead', parent=self.bottomBracketContainer, align=uiconst.CENTERBOTTOM, width=self.bracketHeadWidth, height=5, leftEdgeSize=16, rightEdgeSize=16, top=1, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/bracketHead_Window.png', rotation=math.pi)

    def ConstructInnerFrame(self):
        mainSpriteWidth = self.mainContentWidth
        mainSpriteHeight = self.mainContentHeight
        self.bannerSprite = Sprite(name='bannerSprite', parent=self.frameCont, align=uiconst.CENTERTOP, width=mainSpriteWidth, height=mainSpriteHeight, texturePath=self.backgroundImage, textureSecondaryPath='res:/UI/Texture/Shared/BracketBorderWindow/mask_Window770.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        self.bannerVideoSprite = StreamingVideoSprite(name='bannerVideoSprite', parent=self.frameCont, state=uiconst.UI_HIDDEN, align=uiconst.CENTERTOP, width=mainSpriteWidth, height=mainSpriteHeight, textureSecondaryPath='res:/UI/Texture/Shared/BracketBorderWindow/mask_Window770.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        self.frameSprite = Frame(name='frameSprite', parent=self.frameCont, align=uiconst.CENTERTOP, width=mainSpriteWidth, height=mainSpriteHeight, opacity=SPRITE_OPACITY, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/frame_Window.png', cornerSize=10, idx=0)
        self.closeButtonCont = Container(name='closeButtonContainer', parent=self.innerCont, align=uiconst.TOPRIGHT, height=100, width=75, idx=0)
        self.closeButton = ButtonIcon(name='closeOfferButton', parent=self.closeButtonCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/Icons/x_close14.png', iconSize=14, func=self.CloseButtonClicked, text=localization.GetByLabel('UI/Common/Buttons/Close'))
        self.closeButton.tooltipPanelClassInfo = TooltipDescriptionWrapper(localization.GetByLabel('UI/Common/Buttons/Close'))

    def CloseButtonClicked(self):
        self._AnimExit()
        if callable(self.onCloseCallback):
            self.onCloseCallback()

    def SetBackgroundImage(self, image = None):
        if image is not None:
            self.bannerSprite.SetTexturePath(image)

    def DeferredClose(self):
        self.CloseByUser()

    def _AnimExit(self):
        animations.FadeOut(obj=self.innerCont, duration=self.closingDurationSec)
        animations.MoveTo(obj=self.topBracketContainer, startPos=(0, 0), endPos=(0, self.height / 2 - 8), duration=self.closingDuration2Sec, timeOffset=self.closingDurationSec)
        animations.MoveTo(obj=self.bottomBracketContainer, startPos=(0, self.bottomBracketOffset), endPos=(0, self.height / 2 - 8), duration=self.closingDuration2Sec, timeOffset=self.closingDurationSec)
        animations.FadeOut(obj=self.topBracketContainer, duration=self.fadeOutDurationSec, timeOffset=self.closingDurationSec + self.closingDuration2Sec)
        animations.FadeOut(obj=self.bottomBracketContainer, duration=self.fadeOutDurationSec, timeOffset=self.closingDurationSec + self.closingDuration2Sec, callback=self.DeferredClose)

    def _AnimEnter(self):
        animations.FadeIn(obj=self.topBracketContainer, endVal=SPRITE_OPACITY, duration=self.openingDurationSec)
        animations.FadeIn(obj=self.bottomBracketContainer, endVal=SPRITE_OPACITY, duration=self.openingDurationSec)
        animations.MoveTo(obj=self.topBracketContainer, startPos=(0, self.height / 2 - 8), endPos=(0, 0), duration=self.openingDuration2Sec, timeOffset=self.openingDurationSec)
        animations.MoveTo(obj=self.bottomBracketContainer, startPos=(0, self.height / 2 - 8), endPos=(0, self.bottomBracketOffset), duration=self.openingDuration2Sec, timeOffset=self.openingDurationSec)
        animations.FadeIn(obj=self.innerCont, duration=self.fadeInDurationSec, timeOffset=self.openingDurationSec + self.openingDuration2Sec, callback=self.PostAnimEnter)

    def PostAnimEnter(self):
        pass
