#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\mercenaryDen.py
from eve.common.script.sys.idCheckers import IsFaction, IsCorporation, IsAlliance
from evelink import Link, format_show_info_url
from gametime import GetWallclockTime, HOUR, MIN
from inventorycommon.const import ownerDeathlessCustodians, ownerUnknown, typeCorporation, typeFaction, typeAlliance
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
ITEM_ID = 'itemID'
TYPEID = 'typeID'
SOLAR_SYSTEM_ID = 'solarsystemID'
PLANET_ID = 'planetID'
MERCENARY_DEN_SHOW_INFO_DATA = 'mercenaryDenShowInfoData'
PLANET_SHOW_INFO_DATA = 'planetShowInfoData'
SHOW_INFO = 'showinfo'
TIMESTAMP_ENTERED = 'timestampEntered'
TIMESTAMP_EXITED = 'timestampExited'
AGGRESSOR_CHARACTER_ID = 'aggressorCharacterID'
AGGRESSOR_CORPORATION_NAME = 'aggressorCorporationName'
AGGRESSOR_ALLIANCE_NAME = 'aggressorAllianceName'
SHIELD_PERC = 'shieldPercentage'
ARMOR_PERC = 'armorPercentage'
HULL_PERC = 'hullPercentage'
WARNING_TEXT = 'warningText'
CORPID_SCOPE = 1000107
CHARID_SCOPECEO = 3004341

class BaseMercenaryDenNotificationFormatter(BaseNotificationFormatter):

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)
        self.localization = self.GetLocalizationImpl(localizationImpl)

    @staticmethod
    def GetBaseData(itemID, typeID, solarSystemID, planetID):
        celestial = cfg.mapSolarSystemContentCache.celestials[planetID]
        planetTypeID = celestial.typeID
        data = {ITEM_ID: itemID,
         TYPEID: typeID,
         SOLAR_SYSTEM_ID: solarSystemID,
         PLANET_ID: planetID,
         MERCENARY_DEN_SHOW_INFO_DATA: (SHOW_INFO, typeID, itemID),
         PLANET_SHOW_INFO_DATA: (SHOW_INFO, planetTypeID, planetID)}
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
        sampleArgs = (1000000269694L, 85230, 30004943, 40313086)
        return sampleArgs

    @staticmethod
    def GetSampleSender():
        return ownerDeathlessCustodians

    @staticmethod
    def _GetCorporationName(corporationID):
        if corporationID is None or not IsCorporation(corporationID):
            return cfg.eveowners.Get(ownerUnknown).name
        return unicode(Link(url=format_show_info_url(typeCorporation, corporationID), text=cfg.eveowners.Get(corporationID).name))

    @staticmethod
    def _GetAllianceName(allianceID):
        if allianceID is None:
            return cfg.eveowners.Get(ownerUnknown).name
        elif IsAlliance(allianceID):
            return unicode(Link(url=format_show_info_url(typeAlliance, allianceID), text=cfg.eveowners.Get(allianceID).name))
        elif IsFaction(allianceID):
            return unicode(Link(url=format_show_info_url(typeFaction, allianceID), text=cfg.eveowners.Get(allianceID).name))
        else:
            return cfg.eveowners.Get(ownerUnknown).name


class MercenaryDenReinforced(BaseMercenaryDenNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMercenaryDenReinforced'
    bodyLabel = 'Notifications/Structures/bodyMercenaryDenReinforced'

    @staticmethod
    def MakeData(itemID, typeID, solarSystemID, planetID, timestampEntered, timestampExited, aggressorCharacterID, aggressorCorporationID, aggressorAllianceID):
        data = BaseMercenaryDenNotificationFormatter.GetBaseData(itemID, typeID, solarSystemID, planetID)
        data[TIMESTAMP_ENTERED] = timestampEntered
        data[TIMESTAMP_EXITED] = timestampExited
        data[AGGRESSOR_CHARACTER_ID] = aggressorCharacterID or ownerUnknown
        data[AGGRESSOR_CORPORATION_NAME] = MercenaryDenReinforced._GetCorporationName(aggressorCorporationID)
        data[AGGRESSOR_ALLIANCE_NAME] = MercenaryDenReinforced._GetAllianceName(aggressorAllianceID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseMercenaryDenNotificationFormatter.GetBaseSampleArgs()
        timestampEntered = GetWallclockTime()
        timestampExited = timestampEntered + 1 * HOUR + 15 * MIN
        aggressorCharacterID = 90000001
        aggressorCorporationID = 98000001
        aggressorAllianceID = 99000001
        sampleArgs += (timestampEntered,
         timestampExited,
         aggressorCharacterID,
         aggressorCorporationID,
         aggressorAllianceID)
        return MercenaryDenReinforced.MakeData(*sampleArgs)


class MercenaryDenAttacked(BaseMercenaryDenNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMercenaryDenAttacked'
    bodyLabel = 'Notifications/Structures/bodyMercenaryDenAttacked'

    @staticmethod
    def MakeData(itemID, typeID, solarSystemID, planetID, shield, armor, hull, aggressorID, aggressorCorpID, aggressorAllianceID = None):
        data = BaseMercenaryDenNotificationFormatter.GetBaseData(itemID, typeID, solarSystemID, planetID)
        data[SHIELD_PERC] = 100 * shield
        data[ARMOR_PERC] = 100 * armor
        data[HULL_PERC] = 100 * hull
        data[AGGRESSOR_CHARACTER_ID] = aggressorID
        data[AGGRESSOR_CORPORATION_NAME] = MercenaryDenAttacked._GetCorporationName(aggressorCorpID)
        data[AGGRESSOR_ALLIANCE_NAME] = MercenaryDenAttacked._GetAllianceName(aggressorAllianceID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseMercenaryDenNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (0.3,
         0.4,
         0.5,
         CHARID_SCOPECEO,
         CORPID_SCOPE)
        return MercenaryDenAttacked.MakeData(*sampleArgs)


class MercenaryDenNewMTO(BaseNotificationFormatter):

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self)
        self.localization = self.GetLocalizationImpl(localizationImpl)

    def Format(self, notification):
        data = notification.data
        mto_job_link = data['job_link']
        solar_system_id = data['solar_system_id']
        notification.subject = self.localization.GetByLabel('UI/MercenaryDens/Notifications/NewMTOAvailableSubject')
        notification.body = self.localization.GetByLabel('UI/MercenaryDens/Notifications/NewMTOAvailableText', job_link=mto_job_link, solar_system_id=solar_system_id)
        notification.subtext = self.localization.GetByLabel('UI/MercenaryDens/Notifications/NewMTOAvailableText', job_link=mto_job_link, solar_system_id=solar_system_id)

    @staticmethod
    def MakeSampleData(variant = 0):
        return {'pirateFactionID': 500011,
         'solar_system_id': 30002093}
