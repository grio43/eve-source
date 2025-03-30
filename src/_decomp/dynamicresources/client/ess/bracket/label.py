#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\label.py
import trinity
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel

class InSpaceLabel(ContainerAutoSize):
    label_class = None

    def __init__(self, parent, align, text = None, top = 0, left = 0, color = None):
        super(InSpaceLabel, self).__init__(parent=parent, align=align, alignMode=uiconst.TOPLEFT, top=top, left=left)
        self._label = self.label_class(parent=self, align=uiconst.TOPLEFT, text=text, bold=False, color=color or (1.0, 1.0, 1.0))
        self._shadow = self.label_class(parent=self, align=uiconst.TOPLEFT, top=1, text=text, bold=False, color=(0.0, 0.0, 0.0))
        self._shadow.renderObject.spriteEffect = trinity.TR2_SFX_BLUR

    @property
    def text(self):
        return self._label.GetText()

    @text.setter
    def text(self, text):
        self._label.text = text
        self._shadow.text = text

    @property
    def mainLabel(self):
        return self._label


class Header(InSpaceLabel):
    label_class = eveLabel.EveCaptionLarge


class Notification(InSpaceLabel):
    label_class = eveLabel.EveHeaderLarge


class MediumInSpaceLabel(InSpaceLabel):
    label_class = eveLabel.EveLabelMedium


from dynamicresources.client.ess.bracket.debug import __reload_update__
