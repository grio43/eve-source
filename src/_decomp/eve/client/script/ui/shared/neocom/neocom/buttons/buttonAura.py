#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonAura.py
from carbonui import const as uiconst
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonWindow import ButtonWindow
from eve.client.script.ui.shared.neocom.neocom.neocomUtil import IsBlinkingEnabled

class ButtonAura(ButtonWindow):

    def ApplyAttributes(self, attributes):
        super(ButtonAura, self).ApplyAttributes(attributes)
        if IsBlinkingEnabled():
            self.btnData.SetBlinkingOn()

    def ConstructActiveFrame(self):
        self.activeFrame = Frame(bgParent=self, name='hoverFill', texturePath='res:/UI/Texture/classes/Neocom/buttonActive.png', cornerSize=5, state=uiconst.UI_HIDDEN, color=eveColor.PRIMARY_BLUE)

    def ConstructBlinkSprite(self):
        self.blinkSprite = Sprite(bgParent=self, name='blinkSprite', texturePath='res:/UI/Texture/classes/Neocom/buttonBlink.png', state=uiconst.UI_HIDDEN, color=eveColor.PRIMARY_BLUE)

    def ConstructIcon(self):
        self.iconTransform = Transform(name='iconTransform', parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5), padding=4)
        self.icon = GlowSprite(parent=self.iconTransform, name='icon', state=uiconst.UI_DISABLED, align=uiconst.TOALL, iconOpacity=1.0, iconClass=Sprite, glowColor=eveColor.CRYO_BLUE)
