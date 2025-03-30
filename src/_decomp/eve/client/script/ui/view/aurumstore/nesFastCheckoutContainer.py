#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\nesFastCheckoutContainer.py
import carbonui.const as uiconst
import uthread2
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import ExitButton
from fastcheckout.client.fastCheckoutStoreView import FastCheckoutStoreView
from fastcheckout.const import FULL_WINDOW_WIDTH, FULL_WINDOW_HEIGHT
TEXT_PADDING = 10
FRAME_WIDTH = 10
FRAME_COLOR = (1.0, 1.0, 1.0, 0.25)
EXIT_BUTTON_PADDING = 4

class NesFastCheckoutContainer(Container):
    default_name = 'NesFastCheckoutContainer'
    default_state = uiconst.UI_PICKCHILDREN
    frameColor = Color.GRAY9
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        super(NesFastCheckoutContainer, self).ApplyAttributes(attributes)
        self.logContext = attributes.get('logContext', None)
        self.construct_layout()

    def construct_layout(self):
        main_container = Container(parent=self, align=uiconst.CENTER, width=FULL_WINDOW_WIDTH, height=FULL_WINDOW_HEIGHT - 50)
        FastCheckoutStoreView(name='NesFastCheckoutStoreView', parent=main_container, align=uiconst.TOALL, logContext=self.logContext, openedFromNES=True)
        Fill(bgParent=main_container, color=FRAME_COLOR, padding=[-FRAME_WIDTH] * 4, fillCenter=True)
        ExitButton(parent=main_container, align=uiconst.TOPRIGHT, onClick=self.CloseAurumStoreView, top=EXIT_BUTTON_PADDING, left=EXIT_BUTTON_PADDING, idx=0)

    def CloseAurumStoreView(self):
        uthread2.StartTasklet(sm.GetService('fastCheckoutClientService').close_fast_checkout_nes)
