#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\decorative\menuUnderlay.py
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.util.color import Color

class MenuUnderlay(Container):

    def __init__(self, **kwargs):
        super(MenuUnderlay, self).__init__(**kwargs)
        Frame(bgParent=self, opacity=0.1)
        BlurredSceneUnderlay(bgParent=self, isInFocus=True, color=Color.HextoRGBA('#ff0b0a12'))
