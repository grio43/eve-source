#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\headerButton.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect

@Component(ButtonEffect())

class HeaderButton(Container):
    default_width = 16
    default_height = 16
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onClick = attributes.onClick
        Sprite(parent=self, texturePath=attributes.texturePath, width=self.width, height=self.height, align=uiconst.CENTER, state=uiconst.UI_DISABLED, color=(0.8, 0.8, 0.8, 1.0))

    def OnClick(self):
        if not self.disabled:
            self.onClick()
