#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\ui\colorfilterbutton.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.control.buttonIcon import ButtonIcon
from signals import Signal
import trinity

class ColorFilterButton(ButtonIcon):

    def ApplyAttributes(self, attributes):
        super(ColorFilterButton, self).ApplyAttributes(attributes)
        self._is_on = attributes.get('isOn', True)
        self._color = attributes.get('color', (1, 1, 1, 1))
        self.setup_layout()

    def setup_layout(self):
        self._color_sprite = Sprite(name='ColorSprite', parent=self, align=uiconst.TOALL, color=self._color, texturePath='res:/UI/Texture/classes/ProjectDiscovery/transitColor.png')
        self._color_sprite.pickState = uiconst.TR2_SPS_OFF
        self._selected_sprite = Sprite(name='selectedSprite', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/transitColorSelected.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, opacity=1 if self._is_on else 0)
        self._selected_sprite.pickState = uiconst.TR2_SPS_OFF

    def UpdateAlignment(self, *args, **kwargs):
        budget = super(ColorFilterButton, self).UpdateAlignment(*args, **kwargs)
        self.icon.SetSize(self.width, self.height)
        return budget

    def OnClick(self, *args):
        if self.enabled:
            self._is_on = not self._is_on
            self._selected_sprite.opacity = 1 if self._is_on else 0
            sm.ScatterEvent('OnExoPlanetsColorToggle', self._is_on)
        super(ColorFilterButton, self).OnClick(*args)

    def toggle_state(self):
        return self._is_on

    @property
    def toggled(self):
        return self._is_on
