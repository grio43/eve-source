#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\tabWithTag.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.control.tab import Tab
TAG_PADDING_LEFT = 2
TAG_PADDING_RIGHT = 2
TAG_SIZE = 8
TAG_COLOR = (0.97, 0.09, 0.13)
TAG_TEXTURE_PATH = 'res:/UI/Texture/Shared/smallDot.png'

class TabWithTag(Tab):

    def UpdateShouldShowTag(self, value):
        self.Blink(value)

    def ClearTag(self):
        self.Blink(False)
