#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\structure_design\license_loading_container.py
import eveicon
from carbonui import uiconst, ButtonVariant, Density, TextAlign
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveCaptionLarge, EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.loadingContainer import LoadingContainer
from localization import GetByLabel

class LicenseLoadingContainer(LoadingContainer):
    BANNER_WIDTH = 1600
    BANNER_HEIGHT = 300

    def __init__(self, *args, **kwargs):
        self._header_container = None
        self._banner = None
        self._state_container = None
        super(LicenseLoadingContainer, self).__init__(*args, **kwargs)

    def _ConstructFailureState(self, failureStateMessage, failureStateSubtext, retryBtnLabel):
        self._construct_header()
        self._construct_failure_state(failureStateMessage, failureStateSubtext, retryBtnLabel)

    def _construct_header(self):
        self._header_container = Container(name='header_container', parent=self._failureStateCont, align=uiconst.TOTOP, height=200, clipChildren=True)
        Button(name='skinr_button', parent=self._header_container, align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Personalization/PaintTool/OpenSKINR'), texturePath='res:/UI/Texture/WindowIcons/paint_tool.png', variant=ButtonVariant.PRIMARY, func=self._on_skinr_button_click, padRight=20, padBottom=20)
        text_container = ContainerAutoSize(name='text_container', parent=self._header_container, align=uiconst.TOTOP, padLeft=20, padTop=20)
        description_container = ContainerAutoSize(name='description_container', parent=text_container, align=uiconst.TOBOTTOM)
        EveLabelMedium(name='cta_description', parent=description_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/TrySKINRDescription'))
        caption_container = ContainerAutoSize(name='caption_container', parent=text_container, align=uiconst.TOBOTTOM, padBottom=10)
        EveCaptionLarge(name='cta_caption', parent=caption_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/TrySKINRTitle'))
        self._banner = Sprite(name='banner', parent=self._header_container, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/StructureDesign/background/skinr_banner.png', state=uiconst.UI_DISABLED)

    def _construct_failure_state(self, failureStateMessage, failureStateSubtext, retryBtnLabel):
        self._state_container = Container(name='state_container', parent=self._failureStateCont, align=uiconst.TOALL)
        self._failureCentralCont = ContainerAutoSize(name='failureCentralCont', parent=self._state_container, align=uiconst.CENTER, padding=(self.failureContPadding,
         self.failureContPadding,
         self.failureContPadding,
         self.failureContPadding))
        if len(failureStateMessage) > 0:
            errorMessage = EveCaptionSmall(name='errorMessage', parent=self._failureCentralCont, align=uiconst.TOTOP, textAlign=TextAlign.CENTER, text=failureStateMessage, color=eveColor.WARNING_ORANGE)
            errorMessage.uppercase = True
        if len(failureStateSubtext) > 0:
            EveLabelLarge(name='errorSubtext', parent=self._failureCentralCont, align=uiconst.TOTOP, textAlign=TextAlign.CENTER, text=failureStateSubtext, top=8 if len(failureStateMessage) > 0 else 0)
        if len(retryBtnLabel) > 0:
            btnCont = ContainerAutoSize(name='btnCont', parent=self._failureCentralCont, align=uiconst.TOTOP, height=32, top=16 if len(failureStateMessage) + len(failureStateSubtext) > 0 else 0)
            Button(name='retryBtn', parent=btnCont, align=uiconst.CENTER, density=Density.NORMAL, label=retryBtnLabel, texturePath=eveicon.refresh, variant=ButtonVariant.GHOST, func=lambda *args: self.LoadContent(self._loadCallback, self._failedCallback))

    def _on_skinr_button_click(self, _buttton):
        uicore.cmd.OpenPaintToolWindow()

    def _OnResize(self, *args):
        super(LicenseLoadingContainer, self)._OnResize(*args)
        if self.destroyed:
            return
        if self._header_container and self._banner:
            scale_ratio = max(1.0, float(self._header_container.displayWidth) / float(self.BANNER_WIDTH))
            self._banner.width = float(self.BANNER_WIDTH) * scale_ratio
            self._banner.height = float(self.BANNER_HEIGHT) * scale_ratio
            header_padding = 8 if uicore.dpiScaling > 1.25 else 0
            self._header_container.padLeft = header_padding
            self._header_container.padRight = header_padding
