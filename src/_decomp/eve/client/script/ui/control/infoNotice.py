#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\infoNotice.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium

class InfoNotice(ContainerAutoSize):
    default_labelText = ''

    def ApplyAttributes(self, attributes):
        super(InfoNotice, self).ApplyAttributes(attributes)
        self._labelText = None
        self.ConstructLayout()
        self.labelText = attributes.get('labelText', self.default_labelText)

    def ConstructLayout(self):
        self.cornerTagWrapper = Container(name='cornerTagWrapper', parent=self, align=uiconst.TOTOP, width=10, height=10)
        self.cornerTag = Sprite(name='cornerTag', parent=self.cornerTagWrapper, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Shared/notice/notice_corner.png', width=10, height=10, color=eveColor.CRYO_BLUE)
        Fill(bgParent=self, color=eveColor.SMOKE_BLUE, opacity=0.2)
        self.noticeLabel = EveLabelMedium(name='noticeLabel', parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=self.labelText, maxLines=2, color=eveColor.PLATINUM_GREY, padding=(24, 1, 24, 11))

    @property
    def labelText(self):
        return self._labelText

    @labelText.setter
    def labelText(self, value):
        self._labelText = value
        self.noticeLabel.text = self._labelText
