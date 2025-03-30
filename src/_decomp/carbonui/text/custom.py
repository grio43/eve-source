#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\text\custom.py
import trinity
from carbonui.control.label import LabelCore
from carbonui.text.color import TextColor
from carbonui.text.const import FontSizePreset

class TextCustom(LabelCore):
    default_name = 'TextCustom'
    default_fontsize = FontSizePreset.BODY
    default_color = TextColor.NORMAL
    default_shadowOffset = (1, 1)
    default_shadowSpriteEffect = trinity.TR2_SFX_FONT
    default_shadowColor = (0.0, 0.0, 0.0, 0.6)
