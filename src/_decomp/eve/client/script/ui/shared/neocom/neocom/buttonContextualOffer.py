#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttonContextualOffer.py
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton

class ButtonContextualOffer(BaseNeocomButton):

    def ApplyAttributes(self, attributes):
        super(ButtonContextualOffer, self).ApplyAttributes(attributes)

    def LoadTooltipPanel(self, panel, owner):
        panel.LoadGeneric1ColumnTemplate()
        panel.AddLabelMedium(text=self.btnData.label, wrapWidth=220)
