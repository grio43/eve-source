#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crate\fixedcratewindow.py
import uthread2
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from carbonui.window.header.small import SmallWindowHeader
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window
from eve.client.script.ui.crate.controller import FixedCrateStackController
from eve.client.script.ui.crate.view.fixed import FixedView
from eve.client.script.ui.crate.window import Splash, CrateWindowUnderlay
from carbonui.fontconst import STYLE_SMALLTEXT

class StackBadge(Container):

    def ApplyAttributes(self, attributes):
        super(StackBadge, self).ApplyAttributes(attributes)
        self._value = attributes.value
        self._Layout()
        self._Update()

    def SetValue(self, value):
        self._value = value
        self._Update()

    def GetValue(self):
        return self._value

    def _Layout(self):
        self.frame = Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/counterFrame.png', cornerSize=8 if self._value >= 10 else 1, offset=-1, color=eveThemeColor.THEME_FOCUSDARK)
        self.label = Label(parent=self, align=uiconst.CENTER, fontStyle=STYLE_SMALLTEXT, fontsize=10, bold=True, color=Color.WHITE, padLeft=-1, padRight=1)

    def _Update(self):
        self._UpdateLabel()
        self._UpdateSize()

    def _UpdateLabel(self):
        self.label.SetText(FmtAmt(self._value, fmt='sn'))

    def _UpdateSize(self):
        self.width = max(16, self.label.textwidth + 5)
        self.height = max(16, self.label.textheight)


class Stack(Container):

    def ApplyAttributes(self, attributes):
        super(Stack, self).ApplyAttributes(attributes)
        Sprite(parent=self, width=32, height=32, align=uiconst.TORIGHT, texturePath='res:/UI/Texture/classes/ItemPacks/Stack_32.png')
        self.circle = StackBadge(parent=self, value=attributes.size, width=32, height=32, align=uiconst.CENTERLEFT, idx=0)
        padAmount = self.circle.width / 2
        self.circle.padLeft = -padAmount
        self.circle.padRight = padAmount

    def SetValue(self, value):
        self.circle.SetValue(value)


class FixedCrateWindow(Window):
    __guid__ = 'form.CrateRedeemedWindow'
    default_windowID = 'CrateRedeemedWindow'
    default_fixedWidth = 800
    default_fixedHeight = 420
    default_width = 800
    default_height = 420
    default_clipChildren = False
    default_isCollapseable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_isMinimizable = False

    @classmethod
    def Open(cls, *args, **kwargs):
        cls.CloseIfOpen()
        return super(FixedCrateWindow, cls).Open(**kwargs)

    def ApplyAttributes(self, attributes):
        super(FixedCrateWindow, self).ApplyAttributes(attributes)
        crate_stack_list = attributes.crate_stack_list
        self.controller = FixedCrateStackController(crate_stack_list)
        self.view = None
        self.splash = None
        self.Layout()
        self.controller.onOpen.connect(self.OnCrateOpenedOrSkipped)
        self.controller.onSkip.connect(self.OnCrateOpenedOrSkipped)
        self.controller.onFinish.connect(self.Close)
        self.controller.onCrateMultiOpenEnded.connect(self.OnMultiOpenEnded)
        uthread2.start_tasklet(self.AnimEntry)

    def Layout(self, shouldAnimateView = False):
        if self.view:
            self.view.Close()
        self.Flush()
        self.SetCaption(self.controller.caption)
        self._stack = Stack(parent=self.content, size=self.controller.stacksize, align=uiconst.TOPRIGHT, width=32, height=32, top=20, padRight=5, padLeft=-5)
        if self.controller.stacksize <= 1:
            self._stack.Hide()
        if self.splash:
            self.splash.Close()
        self.splash = Splash(parent=self.GetMainArea(), align=uiconst.CENTERLEFT, pos=(120, 0, 1, 1), controller=self.controller)
        self.view = FixedView(parent=self.GetMainArea(), align=uiconst.TOALL, controller=self.controller, shouldAnimateView=shouldAnimateView)

    def Prepare_Header_(self):
        self._SetHeader(SmallWindowHeader(show_caption=False))

    def OnCrateOpen(self):
        if self.controller.stacksize < 1:
            self.Close()
        self.UpdateStackValue()
        self.Layout(shouldAnimateView=True)

    def OnCrateOpenedOrSkipped(self):
        self.OnCrateOpen()

    def OnMultiOpenEnded(self, *args):
        self.UpdateStackValue()

    def UpdateStackValue(self):
        self._stack.SetValue(self.controller.stacksize)

    def AnimEntry(self):
        self.splash.AnimEntry()

    def Prepare_Background_(self):
        self.sr.underlay = CrateWindowUnderlay(parent=self)

    def Close(self, *args, **kwargs):
        self.controller.Close()
        super(FixedCrateWindow, self).Close(*args, **kwargs)
