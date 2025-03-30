#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\vgsGiftFormatters.py
import logging
import evetypes
import localization
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import redeem
logger = logging.getLogger(__name__)
try:
    from evelink.client import character_link, type_link
except ImportError:

    def character_link(char_id):
        return cfg.eveowners.Get(char_id).name


    def type_link(type_id):
        return evetypes.GetName(type_id)


class VgsGiftItemReceived(BaseNotificationFormatter):

    def Format(self, notification):
        message = notification.data['message']
        offer_id = notification.data['offerID']
        sender = character_link(notification.data['senderCharID'])
        has_item = False
        try:
            offer_object = sm.GetService('vgsService').GetStore().GetOffer(offer_id)
            products = offer_object.productQuantities.values()
            offer_name = ''
            for product in products:
                type_id = product.typeId
                offer_quantity = notification.data['quantity']
                quantity = product.quantity * offer_quantity if product.quantity >= offer_quantity else offer_quantity
                if type_id == 0:
                    offer_name += localization.GetByLabel('UI/VirtualGoodsStore/ItemNameAndQuantity', itemName=product.name, quantity=product.quantity) + '\n'
                else:
                    has_item = True
                    offer_name += u'%s (%dx)\n' % (type_link(type_id), quantity)

        except Exception:
            offer_name = localization.GetByLabel('Notifications/GiftingOfferNotFound')

        notification.subject = localization.GetByLabel('Notifications/GiftingSubject')
        notification.subtext = localization.GetByLabel('Notifications/GiftingSubtext', senderName=sender)
        notification.body = localization.GetByLabel('Notifications/GiftingMessageBody', senderName=sender, offerName=offer_name)
        if message:
            notification.body += '\n%s' % localization.GetByLabel('Notifications/GiftingCustomMessage', message=message)
        if has_item:
            notification.body += '\n' + localization.GetByLabel('Notifications/GiftingRedeemText', redeemingLink=redeem.format_open_redeem_queue_url())
        return notification
