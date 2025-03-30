#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\navigationButtons.py
import eveicon
from carbonui import const as uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.util.uix import GetTextWidth
from localization import GetByLabel

class BackButton(ContainerAutoSize):
    default_height = 24
    default_state = uiconst.UI_NORMAL

    def __init__(self, onClick = None, *args, **kwargs):
        super(BackButton, self).__init__(*args, **kwargs)
        self._icon = None
        self._on_click_callback = onClick
        self._construct_layout()

    def _construct_layout(self):
        self._icon = ButtonIcon(name='icon', parent=self, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, width=24, height=24, iconSize=16, texturePath=eveicon.navigate_back)
        label_text = GetByLabel('UI/Commands/Back')
        label_width = GetTextWidth(label_text, fontsize=EveLabelLarge.default_fontsize, fontStyle=EveLabelLarge.default_fontStyle)
        label_container = Container(name='label_container', parent=self, align=uiconst.TOLEFT, height=self.height, width=label_width)
        EveLabelLarge(name='label', parent=label_container, align=uiconst.CENTERLEFT, text=label_text)

    def OnMouseEnter(self, *args):
        if self._icon:
            uicore.animations.MorphScalar(self._icon.icon, 'glowBrightness', self._icon.icon.glowBrightness, self._icon.GLOWAMOUNT_MOUSEHOVER, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        if self._icon:
            uicore.animations.MorphScalar(self._icon.icon, 'glowBrightness', self._icon.icon.glowBrightness, self._icon.GLOWAMOUNT_IDLE, duration=uiconst.TIME_ENTRY)

    def OnClick(self, *args):
        if self._on_click_callback:
            self._on_click_callback(*args)
