#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\warningContainer.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium

class WarningContainer(ContainerAutoSize):
    default_name = 'WarningContainer'
    default_height = 40
    default_width = 390
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(WarningContainer, self).ApplyAttributes(attributes)
        text = attributes.text
        color = attributes.color
        Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=9, color=color, opacity=0.15)
        Sprite(name='cornerSprite', parent=self, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, color=color, opacity=0.5, state=uiconst.UI_DISABLED)
        Sprite(name='warningIcon', parent=self, align=uiconst.CENTERLEFT, width=32, height=32, left=10, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', color=color, state=uiconst.UI_DISABLED)
        self.label = EveLabelMedium(name='warningLabel', parent=self, align=uiconst.TOTOP, padding=(52, 8, 8, 8), text=text, color=color, state=uiconst.UI_NORMAL)

    def SetText(self, text):
        self.label.SetText(text)
