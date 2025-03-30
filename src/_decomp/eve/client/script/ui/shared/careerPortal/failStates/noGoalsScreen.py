#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\failStates\noGoalsScreen.py
from carbonui import Align, TextAlign
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import CaptionLabel
from localization import GetByLabel
from signals import Signal

class NoGoalsScreen(Container):
    default_bgColor = (0, 0, 0, 0.45)

    def __init__(self, *args, **kwargs):
        super(NoGoalsScreen, self).__init__(*args, **kwargs)
        self.on_retry = Signal('on_retry')
        self.construct_layout()

    def construct_layout(self):
        label_container = ContainerAutoSize(name='label_container', parent=self, align=Align.CENTER, width=500)
        CaptionLabel(name='synchronization_failed_label', parent=label_container, align=Align.TOTOP, text=GetByLabel('UI/CareerPortal/AIRSynchronizationFailed'), textAlign=TextAlign.CENTER, uppercase=True, fontSize=24)
        CaptionLabel(name='try_again_label', parent=label_container, align=Align.TOTOP, text=GetByLabel('UI/CareerPortal/TryAgainLater'), textAlign=TextAlign.CENTER, fontsize=14)
        button_container = ContainerAutoSize(name='button_container', parent=label_container, align=Align.TOTOP, top=16)
        Button(name='retry_button', parent=button_container, align=Align.CENTER, label=GetByLabel('UI/CareerPortal/Synchronize'), texturePath='res:/UI/Texture/classes/Treatments/recycleIcon.png', func=self.on_retry_button_click)

    def on_retry_button_click(self, *args):
        self.on_retry(self)
