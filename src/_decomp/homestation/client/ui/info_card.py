#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\info_card.py
import math
import chroma
from carbonui import uiconst
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel
from homestation.client.ui.const import Padding, Color
from homestation.client.ui.vertical_centered_container import VerticalCenteredContainer

class Severity(object):
    info = 0
    warning = 1
    error = 2


ICON_BY_SEVERITY = {Severity.info: None,
 Severity.warning: 'res:/UI/Texture/classes/agency/iconExclamation.png',
 Severity.error: 'res:/UI/Texture/classes/agency/iconExclamation.png'}
COLOR_BY_SEVERITY = {Severity.info: Color.info,
 Severity.warning: Color.warning,
 Severity.error: Color.error}

class InfoCard(VerticalCenteredContainer):
    icon_size = 24
    default_alignMode = uiconst.TOTOP
    default_minHeight = icon_size + 2 * Padding.normal

    def __init__(self, text = None, severity = Severity.info, **kwargs):
        self._text = text
        self._severity = severity
        self._label = None
        super(InfoCard, self).__init__(**kwargs)
        self.layout()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if self._text != text:
            self._text = text
            self._label.SetText(text)

    @property
    def _color(self):
        return COLOR_BY_SEVERITY[self._severity]

    @property
    def _icon(self):
        return ICON_BY_SEVERITY[self._severity]

    def layout(self):
        with self.auto_size_disabled():
            Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, rotation=math.pi, color=chroma.Color.from_any(self._color).with_brightness(0.1).rgb, opacity=0.9)
            Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, color=self._color)
            if self._icon:
                Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=Padding.normal, left=Padding.normal, width=self.icon_size, height=self.icon_size, texturePath=self._icon, color=self._color)
            left_offset = self.icon_size + Padding.normal if self._icon else 0
            self._label = eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padding=(Padding.normal + left_offset,
             Padding.normal,
             Padding.normal,
             Padding.normal), text=self._text, color=self._color)
