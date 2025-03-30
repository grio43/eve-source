#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\const.py
import chroma
from carbonui import TextColor

class Color(object):
    base = chroma.Color.from_hex('#5CCBCB').rgb
    warning = chroma.Color.from_hex('#FFA64D').rgb
    error = chroma.Color.from_hex('#c1272d').rgb
    text_normal = TextColor.NORMAL
    text_secondary = TextColor.SECONDARY
    white = chroma.Color.from_hex('#FFFFFF').rgb
