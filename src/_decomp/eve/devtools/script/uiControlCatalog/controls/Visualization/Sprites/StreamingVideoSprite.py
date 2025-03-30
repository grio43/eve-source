#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Visualization\Sprites\StreamingVideoSprite.py
import carbonui.const as uiconst
from carbonui.primitives.sprite import StreamingVideoSprite
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = 'Basic'
    description = StreamingVideoSprite.__doc__

    def sample_code(self, parent):
        from carbonui.primitives.sprite import StreamingVideoSprite
        StreamingVideoSprite(parent=parent, videoPath='res:/video/charactercreation/amarr.webm', videoLoop=True, align=uiconst.TOPLEFT, width=300, height=169)


class Sample2(Sample):
    name = 'With color'
    description = 'Video sprite can use all the same blend modes and effects as a normal Sprite can'

    def sample_code(self, parent):
        from carbonui.primitives.sprite import StreamingVideoSprite
        StreamingVideoSprite(parent=parent, videoPath='res:/video/charactercreation/amarr.webm', videoLoop=True, align=uiconst.TOPLEFT, width=300, height=169, color=(0, 0, 1, 1))


class Sample3(Sample):
    name = 'With alpha blending'

    def sample_code(self, parent):
        from carbonui.primitives.sprite import StreamingVideoSprite
        from carbonui.uiconst import SpriteEffect
        StreamingVideoSprite(parent=parent, videoPath='res:/video/hacking/bgLoop_alpha.webm', videoLoop=True, align=uiconst.TOPLEFT, width=600, height=420, spriteEffect=SpriteEffect.COPY)
