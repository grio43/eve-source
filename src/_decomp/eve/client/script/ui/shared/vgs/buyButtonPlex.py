#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\buyButtonPlex.py
import localization
from eve.client.script.ui.control.eveLabel import EveHeaderMedium
from eve.client.script.ui.shared.vgs.buttonCore import ButtonCore
from eve.client.script.ui.shared.vgs.const import COLOR_PLEX

class BuyButtonPlex(ButtonCore):
    default_name = 'BuyButtonPlex'
    default_color = COLOR_PLEX
    default_padding = (8, 4, 8, 4)
    default_labelClass = EveHeaderMedium
    default_labelShadow = True
    default_labelShadowColor = (0.0, 0.0, 0.0, 0.4)
    default_labelTop = 1
    default_logContext = 'None'
    default_text = localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyPlex')

    def ApplyAttributes(self, attributes):
        if attributes.get('onClick', None) is None:
            attributes.onClick = self.OpenFastCheckout
        super(BuyButtonPlex, self).ApplyAttributes(attributes)
        self.logContext = attributes.get('logContext', self.default_logContext)

    def OpenFastCheckout(self):
        sm.GetService('cmd').CmdBuyPlex(logContext=self.logContext)
