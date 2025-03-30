#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\infoContAttribute.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold
from carbonui.control.section import SubSectionAutoSize

class InfoContAttribute(SubSectionAutoSize):
    default_name = 'InfoContAttribute'

    def ApplyAttributes(self, attributes):
        super(InfoContAttribute, self).ApplyAttributes(attributes)
        self.label = EveLabelMediumBold(name='enemyLabel', parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)

    def UpdateText(self, text):
        self.label.text = text
