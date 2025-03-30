#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\war.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.common.script.util.notificationUtil import ParamWarOwners, CreateItemInfoLink
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
from carbon.common.script.util.format import FmtDate

class WarInvalidateMsg(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarConcordInvalidates'
    bodyLabel = 'Notifications/bodyWarConcordInvalidates'
    bodyLabelNoStarted = 'Notifications/bodyWarConcordInvalidatesNotStarted'

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data.update(notification.data)
        notification.subject = GetByLabel(self.subjectLabel, **data)
        bodyLabel = self.bodyLabel
        if data.get('timeStarted', None):
            if notification.created < data['timeStarted']:
                bodyLabel = self.bodyLabelNoStarted
        notification.body = GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001}


class WarHQRemovedFromSpace(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarHqRemoved'
    bodyLabel = 'Notifications/bodyWarWarHqRemoved'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data['declaredDate'] = FmtDate(notification.data['timeDeclared'])
        data['warHQ'] = notification.data['warHQ']
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001,
         'timeDeclared': 132023206828876106L,
         'warHQ': 'A War HQ'}


class WarMutualWarInviteSent(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarMutualWarInviteSent'
    bodyLabel = 'Notifications/bodyWarMutualWarInviteSent'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        expireTimeStamp = notification.data['expireTimeStamp']
        expireDate = FmtDate(expireTimeStamp, 'ln')
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, expireDate=expireDate, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001,
         'expireTimeStamp': 132023206828876106L}


class WarMutualWarInviteRejected(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarMutualWarInviteRejected'
    bodyLabel = 'Notifications/bodyWarMutualWarInviteRejected'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001}


class WarMutualWarInviteAccepted(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarMutualWarInviteAccepted'
    bodyLabel = 'Notifications/bodyWarMutualWarInviteAccepted'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data['time'] = notification.data['time']
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001,
         'time': 132023206828876106L}


class WarAdopted(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarAdopted'
    bodyLabel = 'Notifications/bodyWarAdopted'
    allyText = 'Notifications/WarAdoptedAllyText'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data['allianceName'] = CreateItemInfoLink(notification.data['allianceID'])
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)
        if notification.data.get('isAlly', False):
            notification.body += '<br><br>%s' % GetByLabel('Notifications/WarAdoptedAllyText', **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001,
         'allianceID': 99000002}


class MutualWarExpired(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjMutualWarExpired'
    bodyLabel = 'Notifications/bodyMutualWarExpired'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data['numDays'] = notification.data['numDays']
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001,
         'numDays': 5}


class WarInherited(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarInherited'
    bodyLabel = 'Notifications/bodyWarInherited'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data['allianceName'] = CreateItemInfoLink(notification.data['allianceID'])
        data['quitterName'] = CreateItemInfoLink(notification.data['quitterID'])
        data['opponentName'] = CreateItemInfoLink(notification.data['opponentID'])
        data['allyText'] = notification.data.get('allyText') or ''
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001,
         'allianceID': 99000002,
         'quitterID': 98000003,
         'opponentID': 98000004}


class WarAllyInherited(WarInherited):
    allyText = 'Notifications/WarAllyInherited'

    def Format(self, notification):
        notification.data['allianceName'] = CreateItemInfoLink(notification.data['allianceID'])
        notification.data['allyText'] = GetByLabel(self.allyText, **notification.data)
        super(WarAllyInherited, self).Format(notification)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001,
         'allianceID': 99000002,
         'quitterID': 98000003,
         'opponentID': 98000004}


class MutualWarRetracted(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarRetracts'
    bodyLabel = 'Notifications/bodyWarRetract'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)


class ConcordRetractsWar(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarConcordRetracts'
    bodyLabel = 'Notifications/bodyWarConcordRetracts'
    signOff = 'Notifications/bodyConcordSignOff'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data['endDate'] = notification.data['endDate']
        data['signOff'] = GetByLabel(self.signOff)
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)


class WarInvalid(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarConcordRetracts'
    bodyLabel = 'Notifications/bodyWarInvalid'
    signOff = 'Notifications/bodyConcordSignOff'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data['endDate'] = notification.data['endDate']
        data['signOff'] = GetByLabel(self.signOff)
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)


class WarEndedHqSystemSecurityDropMsg(BaseNotificationFormatter):
    subjectLabel = 'Notifications/subjWarEndedHqSystemSecurityDrop'
    bodyLabel = 'Notifications/bodyWarEndedHqSystemSecurityDrop'
    signOff = 'Notifications/bodyConcordSignOff'

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        data = ParamWarOwners(notification)
        data.update(notification.data)
        data['signOff'] = GetByLabel(self.signOff)
        hqInfo = notification.data['warHQ_IdType']
        hqItemID, hqTypeID = hqInfo
        hqItemName = notification.data['warHQ']
        notification.data['warHQ'] = GetShowInfoLink(hqTypeID, hqItemName, hqItemID)
        notification.subject = GetByLabel(self.subjectLabel, **data)
        notification.body = GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'againstID': 98000001,
         'declaredByID': 99000001,
         'endDate': 132261482400000000L,
         'warHQ': 'Edmalbrurdus - Montague War HQ',
         'warHQ_IdType': (1000000157608L, 35832)}
