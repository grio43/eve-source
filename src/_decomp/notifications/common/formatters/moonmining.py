#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\moonmining.py
import evetypes
from carbon.common.script.util.linkUtil import GetShowInfoLink
import inventorycommon.const as invConst
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

def GetOreText(data, getByLabelFunc):
    oreVolumeByTypeID = data.get('oreVolumeByType', None)
    if oreVolumeByTypeID is None:
        return ''
    textListTuple = []
    for oreTypeID, volume in oreVolumeByTypeID.iteritems():
        oreName = evetypes.GetName(oreTypeID)
        typeLink = GetShowInfoLink(oreTypeID, oreName)
        oreText = getByLabelFunc('Notifications/Structures/OreTypeAndVolume', typeLink=typeLink, volume=volume)
        textListTuple.append((oreName, oreText))

    textList = [ item[1] for item in sorted(textListTuple, key=lambda x: x[0]) ]
    text = '<br>'.join(textList)
    return text


class BaseMoonminingNotificationFormatter(BaseNotificationFormatter):

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)
        self.localization = self.GetLocalizationImpl(localizationImpl)

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)

    def _FormatSubject(self, data, notification):
        notification.subject = self.localization.GetByLabel(self.subjectLabel, **data)

    def _FormatBody(self, data, notification):
        oreText = GetOreText(data, self.localization.GetByLabel)
        data['oreComp'] = oreText
        self.AddLinksToData(data)
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)

    @staticmethod
    def AddLinksToData(data):
        solarSystemID = data['solarSystemID']
        solarSystemName = cfg.evelocations.Get(solarSystemID).name
        data['solarSystemLink'] = GetShowInfoLink(invConst.typeSolarSystem, solarSystemName, solarSystemID)
        moonID = data['moonID']
        moonName = cfg.evelocations.Get(moonID).name
        data['moonLink'] = GetShowInfoLink(invConst.typeMoon, moonName, moonID)

    @staticmethod
    def GetBaseData(structureID, structureName, structureTypeID, solarSystemID, moonID):
        structureLink = GetShowInfoLink(structureTypeID, structureName, structureID)
        data = {'structureLink': structureLink,
         'structureID': structureID,
         'structureName': structureName,
         'structureTypeID': structureTypeID,
         'solarSystemID': solarSystemID,
         'moonID': moonID}
        return data


class MoonminingExtractionStartedNotificationFormatter(BaseMoonminingNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMoonminingExtractionStarted'
    bodyLabel = 'Notifications/Structures/bodyMoonminingExtractionStarted'

    @staticmethod
    def MakeData(structureID, structureName, structureTypeID, solarSystemID, moonID, startedBy, readyTime, autoTime, oreVolumeByType):
        data = BaseMoonminingNotificationFormatter.GetBaseData(structureID, structureName, structureTypeID, solarSystemID, moonID)
        charInfo = cfg.eveowners.Get(startedBy)
        startedByLink = GetShowInfoLink(charInfo.typeID, charInfo.name, startedBy)
        data.update({'startedByLink': startedByLink,
         'startedBy': startedBy,
         'readyTime': readyTime,
         'autoTime': autoTime,
         'oreVolumeByType': oreVolumeByType})
        return data


class MoonminingExtractionCancelledNotificationFormatter(BaseMoonminingNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMoonminingExtractionCancelled'
    bodyLabel = 'Notifications/Structures/bodyMoonminingExtractionCancelled'
    bodyLabelUnknown = 'Notifications/Structures/bodyMoonminingExtractionCancelledByUnknown'

    def _FormatBody(self, data, notification):
        if data['cancelledBy'] is None:
            bodyLabel = self.bodyLabelUnknown
        else:
            bodyLabel = self.bodyLabel
        self.AddLinksToData(data)
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeData(structureID, structureName, structureTypeID, solarSystemID, moonID, cancelledBy):
        data = BaseMoonminingNotificationFormatter.GetBaseData(structureID, structureName, structureTypeID, solarSystemID, moonID)
        if cancelledBy:
            charInfo = cfg.eveowners.Get(cancelledBy)
            cancelledByLink = GetShowInfoLink(charInfo.typeID, charInfo.name, cancelledBy)
        else:
            cancelledByLink = ''
        data.update({'cancelledBy': cancelledBy,
         'cancelledByLink': cancelledByLink})
        return data


class MoonminingExtractionFinishedNotificationFormatter(BaseMoonminingNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMoonminingChunkReady'
    bodyLabel = 'Notifications/Structures/bodyMoonminingChunkReady'

    @staticmethod
    def MakeData(structureID, structureName, structureTypeID, solarSystemID, moonID, autoTime, oreVolumeByType):
        data = BaseMoonminingNotificationFormatter.GetBaseData(structureID, structureName, structureTypeID, solarSystemID, moonID)
        data.update({'autoTime': autoTime,
         'oreVolumeByType': oreVolumeByType})
        return data


class MoonminingLaserFiredNotificationFormatter(BaseMoonminingNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMoonminingLaserFired'
    bodyLabel = 'Notifications/Structures/bodyMoonminingLaserFired'

    @staticmethod
    def MakeData(structureID, structureName, structureTypeID, solarSystemID, moonID, firedBy, oreVolumeByType):
        data = BaseMoonminingNotificationFormatter.GetBaseData(structureID, structureName, structureTypeID, solarSystemID, moonID)
        charInfo = cfg.eveowners.Get(firedBy)
        firedByLink = GetShowInfoLink(charInfo.typeID, charInfo.name, firedBy)
        data.update({'firedByLink': firedByLink,
         'firedBy': firedBy,
         'oreVolumeByType': oreVolumeByType})
        return data


class MoonminingAutomaticFractureNotificationFormatter(BaseMoonminingNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMoonminingChunkAutomaticFracture'
    bodyLabel = 'Notifications/Structures/bodyMoonminingChunkAutomaticFracture'

    @staticmethod
    def MakeData(structureID, structureName, structureTypeID, solarSystemID, moonID, oreVolumeByType):
        data = BaseMoonminingNotificationFormatter.GetBaseData(structureID, structureName, structureTypeID, solarSystemID, moonID)
        data.update({'oreVolumeByType': oreVolumeByType})
        return data
