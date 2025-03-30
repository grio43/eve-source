#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\kiringPaymentProvider.py
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from kiring.client.apigateway import PAY_THROUGH_ALIPAY_WEBSITE, PAY_THROUGH_SCANNING_WEIXIN_QR_CODE, PAY_THROUGH_SCANNING_ALIPAY_QR_CODE

class ProviderElement(Container):
    default_width = 100
    default_height = 50
    PROVIDER_TEXTURE = 'res:/UI/Texture/Vgs/Hot.png'
    PROVIDER_TEXT = 'Mystery payment method'

    def ApplyAttributes(self, attributes):
        super(ProviderElement, self).ApplyAttributes(attributes)
        Sprite(parent=self, width=32, height=32, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath=self.PROVIDER_TEXTURE)
        EveLabelMedium(parent=self, text=self.PROVIDER_TEXT, align=uiconst.CENTERBOTTOM)


class AliPayWebsiteProviderElement(ProviderElement):
    PROVIDER_TEXTURE = 'res:/UI/Texture/Vgs/AliPay_Logo.png'
    PROVIDER_TEXT = localization.GetByLabel('UI/VirtualGoodsStore/Kiring/Alipay')


class AliPayQrCodeProviderElement(ProviderElement):
    PROVIDER_TEXTURE = 'res:/UI/Texture/Vgs/AliPay_Logo.png'
    PROVIDER_TEXT = localization.GetByLabel('UI/VirtualGoodsStore/Kiring/AlipayQR')


class WeixinQrCodeProviderElement(ProviderElement):
    PROVIDER_TEXTURE = 'res:/UI/Texture/Vgs/WeChatPay_Logo.png'
    PROVIDER_TEXT = localization.GetByLabel('UI/VirtualGoodsStore/Kiring/WeixinQR')


PROVIDER_TO_ELEMENT = {PAY_THROUGH_ALIPAY_WEBSITE: AliPayWebsiteProviderElement,
 PAY_THROUGH_SCANNING_ALIPAY_QR_CODE: AliPayQrCodeProviderElement,
 PAY_THROUGH_SCANNING_WEIXIN_QR_CODE: WeixinQrCodeProviderElement}

def get_element_for_payment_provider(provider):
    return PROVIDER_TO_ELEMENT.get(provider, None)
