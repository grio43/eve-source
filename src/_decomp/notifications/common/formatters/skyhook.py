#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\skyhook.py
from eve.common.script.sys.idCheckers import IsFaction
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import blue
SOLAR_SYSTEM_ID = 'solarsystemID'
ITEM_ID = 'itemID'
TYPEID = 'typeID'
PLANET_ID = 'planetID'
SKYHOOK_SHOW_INFO_DATA = 'skyhookShowInfoData'
PLANET_SHOW_INFO_DATA = 'planetShowInfoData'
SHOW_INFO = 'showinfo'
CORPID_SCOPE = 1000107
CHARID_SCOPECEO = 3004341
TEST_ALLIANCE_ID = 99000025
LINK_STARTED_LABELS = [('UI/OrbitalSkyhook/Notifications/LinkStartedFirstHeader', 'UI/OrbitalSkyhook/Notifications/LinkStartedFirstBody'), ('UI/OrbitalSkyhook/Notifications/LinkStartedSecondHeader', 'UI/OrbitalSkyhook/Notifications/LinkStartedSecondBody'), ('UI/OrbitalSkyhook/Notifications/LinkStartedThirdHeader', 'UI/OrbitalSkyhook/Notifications/LinkStartedThirdBody')]

class SkyhookLinkStarted(BaseNotificationFormatter):

    def Format(self, notification):
        from evelink.client import location_link
        headerLabel, bodyLabel = LINK_STARTED_LABELS[notification.data['reminderNumber']]
        notification.subject = GetByLabel(headerLabel)
        bodyText = GetByLabel(bodyLabel, planetName=location_link(notification.data['planetID']), characterID=notification.data['characterID'], linkTime=notification.data['linkTime'], remainingMinutes=notification.data['remainingMinutes'])
        notification.body = bodyText
        notification.subtext = bodyText


class BaseSkyhookNotificationFormatter(BaseNotificationFormatter):

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)
        self.localization = self.GetLocalizationImpl(localizationImpl)

    @staticmethod
    def GetBaseData(itemID, typeID, solarSystemID, planetID):
        celestial = cfg.mapSolarSystemContentCache.celestials[planetID]
        planetTypeID = celestial.typeID
        skyhookShowInfoData = (SHOW_INFO, typeID, itemID)
        planetShowInfoData = (SHOW_INFO, planetTypeID, planetID)
        data = {ITEM_ID: itemID,
         SKYHOOK_SHOW_INFO_DATA: skyhookShowInfoData,
         PLANET_ID: planetID,
         PLANET_SHOW_INFO_DATA: planetShowInfoData,
         SOLAR_SYSTEM_ID: solarSystemID,
         TYPEID: typeID}
        return data

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)

    def _FormatSubject(self, data, notification):
        notification.subject = self.localization.GetByLabel(self.subjectLabel, **data)

    def _FormatBody(self, data, notification):
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def GetBaseSampleArgs():
        sampleArgs = (1016094240451L, 81080, 30004797, 40313559)
        return sampleArgs


class SkyhookTheftVulnerabilityStarted(BaseSkyhookNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjSkyhookTheftVulnerabilityStarted'
    bodyLabel = 'Notifications/Structures/bodySkyhookTheftVulnerabilityStarted'

    @staticmethod
    def MakeData(itemID, typeID, solarSystemID, planetID):
        data = BaseSkyhookNotificationFormatter.GetBaseData(itemID, typeID, solarSystemID, planetID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseSkyhookNotificationFormatter.GetBaseSampleArgs()
        return SkyhookTheftVulnerabilityStarted.MakeData(*sampleArgs)

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)

    def _FormatSubject(self, data, notification):
        notification.subject = self.localization.GetByLabel(self.subjectLabel, **data)

    def _FormatBody(self, data, notification):
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)


class SkyhookOnline(BaseSkyhookNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjSkyhookOnline'
    bodyLabel = 'Notifications/Structures/bodySkyhookOnline'

    @staticmethod
    def MakeData(itemID, typeID, solarSystemID, planetID):
        data = BaseSkyhookNotificationFormatter.GetBaseData(itemID, typeID, solarSystemID, planetID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseSkyhookNotificationFormatter.GetBaseSampleArgs()
        return SkyhookOnline.MakeData(*sampleArgs)


class SkyhookLostShield(BaseSkyhookNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjSkyhookLostShield'
    bodyLabel = 'Notifications/Structures/bodySkyhookLostShield'

    @staticmethod
    def MakeData(itemID, typeID, solarSystemID, planetID, reinforcedTimestamp, vulnerableTime):
        data = BaseSkyhookNotificationFormatter.GetBaseData(itemID, typeID, solarSystemID, planetID)
        data['timeLeft'] = long(reinforcedTimestamp - blue.os.GetWallclockTime())
        data['timestamp'] = reinforcedTimestamp
        data['vulnerableTime'] = vulnerableTime
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseSkyhookNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (blue.os.GetWallclockTime() + 5 * const.HOUR + 37 * const.MIN, 3 * const.HOUR + 13 * const.MIN)
        return SkyhookLostShield.MakeData(*sampleArgs)


class SkyhookUnderAttack(BaseSkyhookNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjSkyhookUnderAttack'
    bodyLabel = 'Notifications/Structures/bodySkyhookUnderAttack'
    bodyLabelWithoutAlliance = 'Notifications/Structures/bodySkyhookUnderAttackWithoutAlliance'

    @staticmethod
    def MakeData(itemID, typeID, solarSystemID, planetID, shield, armor, hull, isActive, aggressorID, aggressorCorpID, aggressorAllianceID = None):
        data = BaseSkyhookNotificationFormatter.GetBaseData(itemID, typeID, solarSystemID, planetID)
        aggressorCorpName = cfg.eveowners.Get(aggressorCorpID).name
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, aggressorCorpID)
        data['shieldPercentage'] = 100 * shield
        data['armorPercentage'] = 100 * armor
        data['hullPercentage'] = 100 * hull
        data['isActive'] = isActive
        data['charID'] = aggressorID
        data['corpName'] = aggressorCorpName
        data['corpLinkData'] = ownerCorpLinkData
        data['allianceID'] = aggressorAllianceID
        if aggressorAllianceID:
            data['allianceName'] = cfg.eveowners.Get(aggressorAllianceID).name
            if IsFaction(aggressorAllianceID):
                data['allianceLinkData'] = (SHOW_INFO, const.typeFaction, aggressorAllianceID)
            else:
                data['allianceLinkData'] = (SHOW_INFO, const.typeAlliance, aggressorAllianceID)
        return data

    def _FormatBody(self, data, notification):
        if data['allianceID']:
            bodyLabel = self.bodyLabel
        else:
            bodyLabel = self.bodyLabelWithoutAlliance
        if data['armorPercentage'] == 100 and not data['isActive']:
            warningText = GetByLabel('Notifications/Structures/warningSkyhookUnderAttack')
        else:
            warningText = ''
        data['warningText'] = warningText
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseSkyhookNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (0.3,
         0.4,
         0.5,
         CHARID_SCOPECEO,
         CORPID_SCOPE)
        if variant == 0:
            return SkyhookUnderAttack.MakeData(*sampleArgs)
        else:
            sampleArgs += (TEST_ALLIANCE_ID,)
            return SkyhookUnderAttack.MakeData(*sampleArgs)


class SkyhookDestroyed(BaseSkyhookNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjSkyhookDestroyed'
    bodyLabel = 'Notifications/Structures/bodySkyhookDestroyed'

    @staticmethod
    def MakeData(itemID, typeID, solarSystemID, planetID):
        data = BaseSkyhookNotificationFormatter.GetBaseData(itemID, typeID, solarSystemID, planetID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseSkyhookNotificationFormatter.GetBaseSampleArgs()
        return SkyhookDestroyed.MakeData(*sampleArgs)


class SkyhookDeployed(BaseSkyhookNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjSkyhookDeployed'
    bodyLabel = 'Notifications/Structures/bodySkyhookDeployed'

    @staticmethod
    def MakeData(itemID, typeID, solarSystemID, planetID, corpID, timeLeft):
        data = BaseSkyhookNotificationFormatter.GetBaseData(itemID, typeID, solarSystemID, planetID)
        ownerCorpName = cfg.eveowners.Get(corpID).name
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, corpID)
        data['ownerCorpName'] = ownerCorpName
        data['ownerCorpLinkData'] = ownerCorpLinkData
        data['timeLeft'] = timeLeft
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseSkyhookNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (1000107, 5 * const.HOUR)
        return SkyhookDestroyed.MakeData(*sampleArgs)
