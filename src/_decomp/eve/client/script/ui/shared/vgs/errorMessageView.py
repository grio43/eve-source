#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\errorMessageView.py
import localization
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.vgs.label import VgsLabelLarge

class ErrorMessageView(Container):

    def ApplyAttributes(self, attributes):
        super(ErrorMessageView, self).ApplyAttributes(attributes)
        message = attributes.message
        VgsLabelLarge(parent=self, align=uiconst.CENTER, width=460, text='<center>%s</center>' % localization.GetByLabel(message))
