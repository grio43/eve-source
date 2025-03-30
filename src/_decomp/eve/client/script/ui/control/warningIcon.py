#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\warningIcon.py
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uiconst import OutputMode
from eve.client.script.ui import eveColor

class WarningIcon(Container):
    default_width = 16
    default_height = 16

    def __init__(self, **kw):
        super(WarningIcon, self).__init__(**kw)
        Sprite(bgParent=self, texturePath='res:/UI/Texture/classes/Menu/Icons/exclamationMark.png')
        Sprite(bgParent=self, texturePath='res:/UI/Texture/classes/Menu/Icons/triangleBG.png', color=eveColor.HOT_RED, outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.5)
