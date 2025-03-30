#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\plexDonation.py
import localization
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import logging
logger = logging.getLogger(__name__)
DAYS_FOR_ONE_PLEX = 30

class OmegaTimeDonationReceivedFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = localization.GetByLabel('Notifications/NotificationNames/GameTimeDonation')
        logger.debug(notification.data)
        quantity = notification.data.get('quantity', 1) * DAYS_FOR_ONE_PLEX
        sender = LinkifyOwner(notification.data['senderCharID'])
        subtext = localization.GetByLabel('Notifications/Plex/PlexReceived', charactername=sender, quantity=quantity)
        notification.subtext = subtext
        is_message_in_data = 'message' in notification.data
        message_ = '\n\n%s' % localization.GetByLabel('Notifications/GiftingCustomMessage', message=notification.data['message'] if is_message_in_data else '')
        notification.body = subtext + message_ if is_message_in_data and notification.data['message'] else subtext
        return notification


class PlexDonationSentFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = localization.GetByLabel('Notifications/NotificationNames/PlexDonation')
        sender = LinkifyOwner(notification.data['receiverCharID'])
        body = localization.GetByLabel('Notifications/Plex/PlexDonated', charactername=sender)
        notification.subtext = body
        notification.body = body
        return notification


class OmegaTimeAddedFormatter(BaseNotificationFormatter):

    def Format(self, notification):
        notification.subject = localization.GetByLabel('Notifications/NotificationNames/GameTimeAdded')
        subtext = localization.GetByLabel('Notifications/Plex/GameTimeAddedsubtext')
        notification.subtext = subtext
        return notification


def LinkifyOwner(ownerID):
    owner = cfg.eveowners.Get(ownerID)
    return u'<a href="showinfo:{typeID}//{itemID}">{itemName}</a>'.format(typeID=owner.typeID, itemID=ownerID, itemName=owner.name)
