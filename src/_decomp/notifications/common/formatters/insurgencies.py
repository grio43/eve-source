#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\insurgencies.py
import eve.common.lib.appConst as appConst
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
from pirateinsurgency.const import CAMPAIGN_STATE_ANTIPIRATE_WIN, CAMPAIGN_STATE_NO_WINNER

class InsurgencyStarting(BaseNotificationFormatter):

    def Format(self, notification):
        pirateFaction = cfg.eveowners.Get(notification.data['pirateFactionID']).name
        location = cfg.evelocations.Get(notification.data['originSolarsystemID']).locationName
        notification.subject = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyStartingHeader')
        notification.subtext = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyStartingText', pirateFaction=pirateFaction, location=location)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'pirateFactionID': 500011,
         'originSolarsystemID': 30002093}


class InsurgencyStarted(BaseNotificationFormatter):

    def Format(self, notification):
        pirateFaction = cfg.eveowners.Get(notification.data['pirateFactionID']).name
        notification.subject = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyStartedHeader', pirateFaction=pirateFaction)
        notification.subtext = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyStartedText')

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'pirateFactionID': 500011}


class InsurgencyEndedPiratesWin(BaseNotificationFormatter):
    NOTIFICATION_BODY = {appConst.factionAngelCartel: 'UI/PirateInsurgencies/Notifications/InsurgencyEndedAngelCartel',
     appConst.factionGuristasPirates: 'UI/PirateInsurgencies/Notifications/InsurgencyEndedGuristas'}

    def Format(self, notification):
        pirateFaction = cfg.eveowners.Get(notification.data['pirateFactionID']).name
        notification.subject = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyEndedHeader', pirateFaction=pirateFaction)
        notification.subtext = GetByLabel(self.NOTIFICATION_BODY[notification.data['pirateFactionID']])

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'pirateFactionID': 500011}


class InsurgencyEndedAntiPiratesWin(BaseNotificationFormatter):

    def Format(self, notification):
        pirateFaction = cfg.eveowners.Get(notification.data['pirateFactionID']).name
        notification.subject = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyEndedHeader', pirateFaction=pirateFaction)
        notification.subtext = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyEndedAntiPirates')

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'pirateFactionID': 500011}


class InsurgencyEndedNoOneWins(BaseNotificationFormatter):

    def Format(self, notification):
        pirateFaction = cfg.eveowners.Get(notification.data['pirateFactionID']).name
        notification.subject = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyEndedHeader', pirateFaction=pirateFaction)
        notification.subtext = GetByLabel('UI/PirateInsurgencies/Notifications/InsurgencyEndedNoWinner')

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'pirateFactionID': 500011}


class InsurgencyStage5Corruption(BaseNotificationFormatter):

    def Format(self, notification):
        solarSystemName = cfg.evelocations.Get(notification.data['solarSystemID']).locationName
        pirateFaction = cfg.eveowners.Get(notification.data['pirateFactionID']).name
        numberOfCorruptedSystems = notification.data['numberOfCorruptedSystems']
        totalNumberOfSystems = notification.data['totalNumberOfSystems']
        notification.subject = GetByLabel('UI/PirateInsurgencies/Notifications/MaxCorruptionHeader', location=solarSystemName)
        notification.subtext = GetByLabel('UI/PirateInsurgencies/Notifications/MaxCorruptionText', pirateFaction=pirateFaction, number=numberOfCorruptedSystems, total=totalNumberOfSystems)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'solarSystemID': 30002093,
         'pirateFactionID': 500011,
         'numberOfCorruptedSystems': 2,
         'totalNumberOfSystems': 5}


class InsurgencyStage5Suppression(BaseNotificationFormatter):

    def Format(self, notification):
        solarSystemName = cfg.evelocations.Get(notification.data['solarSystemID']).locationName
        numberOfSuppressedSystems = notification.data['numberOfSuppressedSystems']
        totalNumberOfSystems = notification.data['totalNumberOfSystems']
        notification.subject = GetByLabel('UI/PirateInsurgencies/Notifications/MaxSuppressionHeader', location=solarSystemName)
        notification.subtext = GetByLabel('UI/PirateInsurgencies/Notifications/MaxSuppressionText', number=numberOfSuppressedSystems, total=totalNumberOfSystems)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'solarSystemID': 30002093,
         'numberOfSuppressedSystems': 3,
         'totalNumberOfSystems': 5}
