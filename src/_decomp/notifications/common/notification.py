#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\notification.py


class Notification(object):
    NORMAL_NOTIFICATION = 1
    CONTACT_NOTIFICATION = 2
    SKILL_NOTIFICATION = 3
    CONTACT_LOGGED_ON = 2001
    CONTACT_LOGGED_OFF = 2002
    SKILL_NOTIFICATION_EMPTYQUEUE = 1002
    SKILL_NOTIFICATION_NORMAL = 1000
    SHIP_CORP_COSMETIC_LICENSE_ACQUIRED = 6001
    SHIP_ALLIANCE_COSMETIC_LICENSE_ACQUIRED = 6002

    def __init__(self, notificationID, typeID, senderID, receiverID, processed, created, data, subtext = None):
        self.notificationID = notificationID
        self.typeID = typeID
        self.senderID = senderID
        self.receiverID = receiverID
        self.processed = processed
        self.created = created
        self.data = data
        self.deleted = False
        self.groupID = -1
        self.subject = ''
        self.body = ''
        self.metaType = self.NORMAL_NOTIFICATION
        self.callback = None
        self.callbackArgs = None
        self.showStanding = False
        self.subtext = subtext

    def __str__(self):
        ret = '%s object %d of type %d' % (self.__class__.__name__, self.notificationID, self.typeID)
        if self.subject:
            ret += ' - subject: %s' % self.subject
        if self.body:
            ret += ' - body: %s' % self.body
        ret += ' - data: %s' % self.data
        return ret

    __repr__ = __str__

    def makeSimple(self):
        return SimpleNotification(subject=self.subject, created=self.created, notificationID=self.notificationID, notificationTypeID=self.typeID, senderID=self.senderID)

    @staticmethod
    def FromDTO(notification):
        return Notification(notificationID=notification.notificationID, typeID=notification.typeID, senderID=notification.senderID, receiverID=notification.receiverID, processed=notification.processed, created=notification.created, data=notification.data)

    @staticmethod
    def MakeContactLoggedOnNotification(contactCharID, currentCharID, created, subject, labelText = None):
        return Notification.MakeContactNotification(contactCharID, currentCharID, created, typeID=Notification.CONTACT_LOGGED_ON, title=subject, labelText=labelText)

    @staticmethod
    def MakeContactLoggedOffNotification(contactCharID, currentCharID, created, subject, labelText = None):
        return Notification.MakeContactNotification(contactCharID, currentCharID, created, typeID=Notification.CONTACT_LOGGED_OFF, title=subject, labelText=labelText)

    @staticmethod
    def MakeContactNotification(contactCharID, currentCharID, created, typeID, title, labelText = None):
        contactNotification = Notification(notificationID=-1, typeID=typeID, senderID=contactCharID, receiverID=currentCharID, processed=0, created=created, data={}, subtext=labelText)
        contactNotification.subject = title
        contactNotification.showStanding = True
        contactNotification.metaType = Notification.CONTACT_NOTIFICATION
        return contactNotification

    @staticmethod
    def MakeSkillNotification(header, text, created, callBack = None, callbackargs = None, notificationType = SKILL_NOTIFICATION_NORMAL):
        notification = Notification(notificationID=-1, typeID=notificationType, senderID=session.charid, receiverID=session.charid, processed=0, created=created, data={'callbackargs': callbackargs})
        notification.subject = header
        notification.body = text
        return notification

    @staticmethod
    def MakeShipCosmeticLicenseAcquiredNotification(notificationType, header, body, createdTime, callback):
        notification = Notification(notificationID=-1, typeID=notificationType, senderID=session.charid, receiverID=session.charid, processed=0, created=createdTime, data={})
        notification.callback = callback
        notification.subject = header
        notification.subtext = body
        return notification

    def copy(self):
        notification = Notification.FromDTO(self)
        notification.deleted = self.deleted
        notification.subject = self.subject
        notification.body = self.body
        notification.metaType = self.metaType
        return notification


class SimpleNotification(object):

    def __init__(self, subject, created, notificationID, notificationTypeID, senderID = 0, body = ''):
        self.subject = subject
        self.created = created
        self.notificationID = notificationID
        self.typeID = notificationTypeID
        self.senderID = senderID
        self.metaType = Notification.NORMAL_NOTIFICATION
        self.body = body
        self.callback = None
        self.callbackArgs = None
        self.showStanding = False
        self.subtext = None
