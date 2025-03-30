#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crate\window.py
import carbonui.fontconst
import localization
import log
import trinity
import uthread
from carbonui import const as uiconst, TextBody
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util import color
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveStyleLabel
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import FillThemeColored, FrameThemeColored, GradientThemeColored
from eve.client.script.ui.crate.button import CrateButton
from eve.client.script.ui.crate.controller import CreateController
from eve.client.script.ui.crate.view import CreateView

def getColorUIHighlight(alpha = 1.0):
    elementColor = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
    return color.GetColor(elementColor, alpha=alpha)


class CrateWindow(Window):
    __guid__ = 'form.CrateWindow'
    default_fixedWidth = 800
    default_fixedHeight = 420
    default_width = 800
    default_height = 420
    default_windowID = 'CrateWindow'
    default_clipChildren = False
    default_isCollapseable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_isMinimizable = False

    @classmethod
    def Open(cls, *args, **kwargs):
        wnd = cls.GetIfOpen()
        if not wnd:
            return super(CrateWindow, cls).Open(*args, **kwargs)
        if not wnd.controller.isOpening:
            wnd.Close()
            return super(CrateWindow, cls).Open(*args, **kwargs)
        wnd.Maximize()
        return wnd

    def ApplyAttributes(self, attributes):
        super(CrateWindow, self).ApplyAttributes(attributes)
        typeID = attributes.typeID
        itemID = attributes.itemID
        stacksize = attributes.stacksize
        self.controller = CreateController(typeID, itemID, stacksize)
        self.view = None
        self.Layout()
        self.controller.onOpen.connect(self.OnCrateOpen)
        self.controller.onFinish.connect(self.Close)
        uthread.new(self.AnimEntry)

    def Layout(self):
        self.sr.headerParent.Hide()
        self.SetCaption(self.controller.caption)
        self.splash = Splash(parent=self.GetMainArea(), align=uiconst.CENTERLEFT, pos=(120, 0, 1, 1), controller=self.controller)
        CrateDetailView(parent=self.GetMainArea(), align=uiconst.TOALL, padding=(380, 36, 24, 24), controller=self.controller)

    def OnCrateOpen(self):
        if self.view:
            animations.FadeOut(self.view, duration=0.2, callback=self.view.Close)
        self.view = CreateView(parent=self.GetMainArea(), align=uiconst.TOALL, controller=self.controller, shouldAnimateView=True)

    def AnimEntry(self):
        self.splash.AnimEntry()

    def Prepare_Background_(self):
        self.sr.underlay = CrateWindowUnderlay(parent=self)

    def Close(self, *args, **kwargs):
        self.controller.Close()
        super(CrateWindow, self).Close(*args, **kwargs)


class CrateWindowUnderlay(Container):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(CrateWindowUnderlay, self).ApplyAttributes(attributes)
        self.frame = FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, texturePath='res:/UI/Texture/classes/ItemPacks/windowFrame.png', cornerSize=10, fillCenter=False, opacity=0.5)
        self.outerGlow = FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, texturePath='res:/UI/Texture/classes/ItemPacks/boxGlow.png', cornerSize=5, offset=-2, opacity=0.0)
        self.underlay = GradientThemeColored(bgParent=self, padding=(1, 1, 1, 1), rgbData=[(0, (0.5, 0.5, 0.5))], alphaData=[(0, 0.0), (0.4, 0.9), (0.6, 1.0)], rotation=0)
        GradientThemeColored(parent=self, align=uiconst.TOTOP, height=1, alphaData=[(0, 0.0), (0.4, 0.08), (0.6, 0.1)], rotation=0, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        GradientThemeColored(parent=self, align=uiconst.TOBOTTOM, height=1, alphaData=[(0, 0.0), (0.4, 0.08), (0.6, 0.1)], rotation=0, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        FillThemeColored(parent=self, align=uiconst.TORIGHT, width=1, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.1)

    def AnimEntry(self):
        animations.FadeTo(self.frame, startVal=self.frame.opacity, endVal=1.0, duration=0.4, curveType=uiconst.ANIM_OVERSHOT3)
        animations.FadeTo(self.outerGlow, startVal=self.outerGlow.opacity, endVal=0.25, duration=0.4, curveType=uiconst.ANIM_OVERSHOT2)
        animations.FadeTo(self.underlay, startVal=self.underlay.opacity, endVal=1.0, duration=0.3, curveType=uiconst.ANIM_LINEAR)

    def AnimExit(self):
        animations.FadeTo(self.frame, startVal=self.frame.opacity, endVal=0.5, duration=0.6)
        animations.FadeTo(self.outerGlow, startVal=self.outerGlow.opacity, endVal=0.0, duration=0.6)
        animations.FadeTo(self.underlay, startVal=self.underlay.opacity, endVal=0.85, duration=0.3, curveType=uiconst.ANIM_LINEAR)

    def EnableLightBackground(self):
        pass

    def DisableLightBackground(self):
        pass


class Splash(Container):

    def ApplyAttributes(self, attributes):
        super(Splash, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.flare = None
        self.Layout()
        self.controller.onOpen.connect(self.OnCrateOpen)

    def _NotifyOfFailedTextureLoad(self, sprite):
        trinity.WaitForResourceLoads()
        if not sprite.texture.atlasTexture or not sprite.texture.atlasTexture.IsGood():
            log.LogError('Failed to load crate static splash image from path:', sprite.texture.resPath)

    def Layout(self):
        if self.controller.staticSplash:
            staticSplashSprite = Sprite(parent=self, align=uiconst.TOPLEFT, left=-int(self.controller.staticSplash.width / 2.0), top=-int(self.controller.staticSplash.height / 2.0), texturePath=self.controller.staticSplash.resPath, width=self.controller.staticSplash.width, height=self.controller.staticSplash.height, color=self.controller.staticSplash.color or (1.0, 1.0, 1.0))
            uthread.new(self._NotifyOfFailedTextureLoad, staticSplashSprite)
        if self.controller.animatedSplash:
            try:
                self.flare = StreamingVideoSprite(parent=self, align=uiconst.TOPLEFT, left=-int(self.controller.animatedSplash.width / 2.0), top=-int(self.controller.animatedSplash.height / 2.0), width=self.controller.animatedSplash.width, height=self.controller.animatedSplash.height, videoPath=self.controller.animatedSplash.resPath, videoLoop=True, blendMode=trinity.TR2_SBM_ADD, spriteEffect=trinity.TR2_SFX_COPY, color=self.controller.animatedSplash.color or getColorUIHighlight(), disableAudio=True)
            except RuntimeError:
                log.LogError('Failed to load crate animated splash from path:', self.controller.animatedSplash.resPath)

    def AnimEntry(self):
        if self.flare:
            animations.FadeTo(self.flare, endVal=self.flare.opacity, duration=2.0)

    def OnCrateOpen(self):
        if self.flare:
            animations.FadeOut(self.flare)


class CrateDetailView(Container):

    def ApplyAttributes(self, attributes):
        super(CrateDetailView, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.Layout()
        self.controller.onOpen.connect(self.OnCrateOpenedOrSkipped)
        self.controller.onSkip.connect(self.OnCrateOpenedOrSkipped)

    def _ConstructTitle(self):
        self.title = Transform(parent=self, align=uiconst.TOTOP, height=40, width=400)
        titleLabelWidth, titleLabelHeight = TitleLabel.MeasureTextSize(self.controller.caption)
        titleLabelClass = TitleLabel
        if titleLabelHeight > self.title.height or titleLabelWidth > self.title.width:
            titleLabelClass = SmallerTitleLabel
        titleLabel = titleLabelClass(parent=self.title, align=uiconst.TOPLEFT, padBottom=12, width=420, text=self.controller.caption)
        self.title.height = titleLabel.height

    def Layout(self):
        buttonCont = Container(parent=self, align=uiconst.TOBOTTOM, height=30)
        self._ConstructTitle()
        self.textScroll = ScrollContainer(parent=self, align=uiconst.TOTOP, padBottom=8, height=400)
        TextBody(parent=self.textScroll, align=uiconst.TOTOP, text=self.controller.description)
        self.button = CrateButton(parent=buttonCont, align=uiconst.CENTER, label=localization.GetByLabel('UI/Crate/InitHacking'), func=self.OpenCrate)

    def OpenCrate(self, button):
        button.disabled = True
        try:
            self.controller.OpenCrate()
        except Exception:
            button.disabled = False
            log.LogException()

    def OnCrateOpenedOrSkipped(self):
        self.Disable()
        self.controller.onOpen.disconnect(self.OnCrateOpenedOrSkipped)
        self.controller.onSkip.disconnect(self.OnCrateOpenedOrSkipped)
        animations.MorphScalar(self.title, 'top', endVal=-24, timeOffset=0.25)
        animations.MorphVector2(self.title, 'scale', startVal=(1.0, 1.0), endVal=(0.8, 0.8), timeOffset=0.25)
        animations.FadeOut(self.textScroll, duration=0.5)
        animations.FadeOut(self.button, duration=0.5)


class TitleLabel(EveStyleLabel):
    default_fontsize = 30
    default_bold = True
    default_fontStyle = carbonui.fontconst.STYLE_HEADER
    default_shadowOffset = (0, 1)


class SmallerTitleLabel(EveStyleLabel):
    default_fontsize = 20
    default_bold = True
    default_fontStyle = carbonui.fontconst.STYLE_HEADER
    default_shadowOffset = (0, 1)


def center(text):
    return u'<center>{}</center>'.format(text)


def __SakeReloadHook():
    try:
        instance = CrateWindow.GetIfOpen()
        if instance:
            CrateWindow.Reload(instance)
    except Exception:
        log.LogException()
