#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\warningContainer.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium

class WarningContainer(ContainerAutoSize):
    default_textAlignment = uiconst.CENTERLEFT
    default_minHeight = 43
    default_warningColor = (247 / 255.0, 147 / 255.0, 30 / 255.0)
    default_warningBackgroundColor = (247 / 255.0, 147 / 255.0, 30 / 255.0)
    default_warningOpacity = 0.2

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        text = attributes.text
        textAlignment = attributes.get('textAlignment', self.default_textAlignment)
        warningColor = attributes.get('warningColor', self.default_warningColor)
        warningBackgroundColor = attributes.get('warningBackgroundColor', self.default_warningBackgroundColor)
        warningOpacity = attributes.get('warningOpacity', self.default_warningOpacity)
        self.alignMode = textAlignment
        Sprite(name='warningSprite', parent=self, texturePath='res:/UI/Texture/classes/Warning/warningIconSmall.png', pos=(8, 9, 20, 20), align=uiconst.TOPLEFT, color=warningColor)
        self.warningLabel = EveLabelMedium(parent=self, text=text, align=textAlignment, top=-1)
        if textAlignment in uiconst.PUSHALIGNMENTS:
            self.warningLabel.padLeft = 37
            self.warningLabel.padTop = self.warningLabel.padBottom = self.warningLabel.padRight = 11
        else:
            self.warningLabel.left = 37
            self.warningLabel.padRight = 18
        Sprite(name='cornerSprite', parent=self, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/Warning/warningTriangle.png', pos=(0, 0, 8, 8), color=warningColor)
        Frame(bgParent=self, texturePath='res:/UI/Texture/classes/Warning/solidFrame_12corner.png', cornerSize=12, color=warningBackgroundColor, opacity=warningOpacity)

    @property
    def text(self):
        return self.warningLabel.text

    @text.setter
    def text(self, value):
        self.warningLabel.text = value
