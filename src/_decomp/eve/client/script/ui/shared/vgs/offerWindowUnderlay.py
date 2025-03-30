#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\offerWindowUnderlay.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill

class OfferWindowUnderlay(Container):
    default_name = 'underlay'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        super(OfferWindowUnderlay, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        self.backFill = Fill(bgParent=self, color=(0.133, 0.141, 0.149, 0.98))
        self.frame = Fill(bgParent=self, color=(0.4, 0.4, 0.4, 0.8), padding=(-10, -10, -10, -10))

    def AnimEntry(self):
        pass

    def AnimExit(self):
        pass

    def EnableLightBackground(self):
        pass

    def DisableLightBackground(self):
        pass
