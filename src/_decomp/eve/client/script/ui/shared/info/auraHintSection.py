#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\auraHintSection.py
import eveui
import localization
from carbonui import Align, TextBody
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor

class AuraHintSection(eveui.Container):
    default_align = Align.TOBOTTOM
    default_height = 32

    def __init__(self, text = None, *args, **kwargs):
        self._text = text if text else localization.GetByLabel('UI/CareerPortal/AuraAssistancePanelTitle')
        super(AuraHintSection, self).__init__(*args, **kwargs)
        self._construct()

    def _construct(self):
        eveui.Frame(name='background_frame', bgParent=self, texturePath='res:/UI/Texture/classes/Button/background_cut_bottom_right.png', color=eveColor.AURA_PURPLE, cornerSize=9, opacity=0.05)
        icon_container = eveui.Container(name='icon_container', parent=self, align=Align.TOLEFT, width=16, padLeft=8)
        Sprite(name='aura_icon', parent=icon_container, align=Align.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/aura/aura_icon_16x16.png', width=16, height=16)
        label_text = self._text
        label_width, _ = TextBody.MeasureTextSize(label_text)
        label_container = eveui.ContainerAutoSize(name='label_container', parent=self, align=Align.TOALL, padTop=6, padLeft=8, padRight=32)
        TextBody(name='title_label', parent=label_container, align=Align.TOLEFT, text=label_text, color=eveColor.AURA_PURPLE, autoFadeSides=16)
