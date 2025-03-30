#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\cosmeticLicenseErrorScreen.py
from carbonui import Density, TextAlign, uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium
from carbonui.control.button import Button

class CosmeticLicenseErrorScreen(Container):

    def ApplyAttributes(self, attributes):
        super(CosmeticLicenseErrorScreen, self).ApplyAttributes(attributes)
        self._CreateLayout()

    def _CreateLayout(self):
        self.centralCont = ContainerAutoSize(name='centralCont', parent=self, align=uiconst.CENTER, padding=(16, 0, 16, 0))
        self.errorMessage = EveCaptionLarge(name='errorMessage', parent=self.centralCont, align=uiconst.TOTOP, textAlign=TextAlign.CENTER)
        self.errorSubtext = EveLabelMedium(name='errorSubtext', parent=self.centralCont, align=uiconst.TOTOP, textAlign=TextAlign.CENTER, state=uiconst.UI_NORMAL, padTop=5)
        btnCont = Container(name='btnCont', parent=self.centralCont, align=uiconst.TOTOP, height=32, padTop=32)
        self.actionBtn = Button(name='actionBtn', parent=btnCont, align=uiconst.CENTER, density=Density.EXPANDED)
        Fill(name='blackFill', parent=self, color=eveColor.BLACK)

    def AdjustWidth(self, width):
        self.centralCont.width = width

    def ShowScreen(self, errorMsg, errorSubtext, buttonText, buttonCallback):
        animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.25)
        self.errorMessage.text = errorMsg
        self.errorSubtext.text = errorSubtext
        self.actionBtn.label = buttonText
        self.actionBtn.OnClick = buttonCallback
        self.Enable()

    def CloseScreen(self, animate):
        if animate:
            animations.FadeTo(self, startVal=self.opacity, endVal=0.0, duration=0.25)
        else:
            self.opacity = 0.0
        self.Disable()
