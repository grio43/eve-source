#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\common\formatters\structures.py
from __future__ import absolute_import
import gametime
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.common.script.sys.idCheckers import IsFaction, IsPlayerCorporation, IsKnownSpaceSystem, IsWormholeSystem, IsTriglavianSystem
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
import evetypes
import blue
from structures import NO_REINFORCEMENT_WEEKDAY
from structures.types import IsFlexStructure
from timeDateHelpers.weekdays import GetLabelPathForWeekday
from uthread import SEC
SOLAR_SYSTEM_ID = 'solarsystemID'
STRUCTURE_ID = 'structureID'
STRUCTURE_TYPEID = 'structureTypeID'
STRUCURE_SHOW_INFO_DATA = 'structureShowInfoData'
SHOW_INFO = 'showinfo'
CORPID_SCOPE = 1000107
CHARID_SCOPECEO = 3004341
TEST_ALLIANCE_ID = 99000025

class BaseStructureNotificationFormatter(BaseNotificationFormatter):

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)
        self.localization = self.GetLocalizationImpl(localizationImpl)

    @staticmethod
    def GetBaseData(structureID, structureTypeID, solarSystemID):
        showInfoData = (SHOW_INFO, structureTypeID, structureID)
        data = {STRUCTURE_ID: structureID,
         STRUCURE_SHOW_INFO_DATA: showInfoData,
         SOLAR_SYSTEM_ID: solarSystemID,
         STRUCTURE_TYPEID: structureTypeID}
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
        sampleArgs = (1016094240451L, 35834, 30004797)
        return sampleArgs


class StructureFuelAlert(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureFuelAlert'
    bodyLabel = 'Notifications/Structures/bodyStructureFuelAlert'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, listOfTypesAndQty):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['listOfTypesAndQty'] = listOfTypesAndQty
        return data

    def _FormatBody(self, data, notification):
        listOfTypesAndQty = data['listOfTypesAndQty']
        typesAndQtyText = self._GetTextForTypes(listOfTypesAndQty)
        data['typesAndQtyText'] = typesAndQtyText
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)

    def _GetTextForTypes(self, listOfTypesAndQty):
        textList = [ self.localization.GetByLabel('Notifications/Structures/QtyAndType', qty=x[0], typeID=x[1]) for x in listOfTypesAndQty ]
        return '<br>'.join(textList)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += ([(1, 1230), (5000000, 638)],)
        return StructureFuelAlert.MakeData(*sampleArgs)


class StructureAnchoring(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureAnchoring'
    bodyLabel = 'Notifications/Structures/bodyStructureAnchoring'
    bodyLabelFlex = 'Notifications/Structures/bodyStructureAnchoringFlex'

    def _FormatBody(self, data, notification):
        structureTypeID = data.get(STRUCTURE_TYPEID)
        if structureTypeID and IsFlexStructure(structureTypeID):
            bodyLabel = self.bodyLabelFlex
        else:
            bodyLabel = self.bodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, corpID, anchoringTimestamp, vulnerableTime):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        ownerCorpName = cfg.eveowners.Get(corpID).name
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, corpID)
        data['ownerCorpName'] = ownerCorpName
        data['ownerCorpLinkData'] = ownerCorpLinkData
        data['timeLeft'] = long(max(0, anchoringTimestamp - blue.os.GetWallclockTime()))
        data['vulnerableTime'] = vulnerableTime
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (1000107, blue.os.GetWallclockTime() + 5 * const.HOUR, 37 * const.MIN)
        return StructureAnchoring.MakeData(*sampleArgs)


class StructureUnanchoring(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureUnanchoring'
    bodyLabel = 'Notifications/Structures/bodyStructureUnanchoring'
    bodyLabelFlex = 'Notifications/Structures/bodyStructureUnanchoringFlex'

    def _FormatBody(self, data, notification):
        structureTypeID = data.get(STRUCTURE_TYPEID)
        if structureTypeID and IsFlexStructure(structureTypeID):
            bodyLabel = self.bodyLabelFlex
        else:
            bodyLabel = self.bodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, corpID, anchoringTimestamp):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        ownerCorpName = cfg.eveowners.Get(corpID).name
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, corpID)
        data['ownerCorpName'] = ownerCorpName
        data['ownerCorpLinkData'] = ownerCorpLinkData
        data['timeLeft'] = long(max(0, anchoringTimestamp - blue.os.GetWallclockTime()))
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (1000107, blue.os.GetWallclockTime() + 5 * const.HOUR)
        return StructureUnanchoring.MakeData(*sampleArgs)


class StructureUnderAttack(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureUnderAttack'
    bodyLabel = 'Notifications/Structures/bodyStructureUnderAttack'
    bodyLabelWithoutAlliance = 'Notifications/Structures/bodyStructureUnderAttackWithoutAlliance'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, shield, armor, hull, aggressorID, aggressorCorpID, aggressorAllianceID = None):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        aggressorCorpName = cfg.eveowners.Get(aggressorCorpID).name
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, aggressorCorpID)
        data['shieldPercentage'] = 100 * shield
        data['armorPercentage'] = 100 * armor
        data['hullPercentage'] = 100 * hull
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
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (0.3,
         0.4,
         0.5,
         CHARID_SCOPECEO,
         CORPID_SCOPE)
        if variant == 0:
            return StructureUnderAttack.MakeData(*sampleArgs)
        else:
            sampleArgs += (TEST_ALLIANCE_ID,)
            return StructureUnderAttack.MakeData(*sampleArgs)


class StructureOnline(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureOnline'
    subjectLabelRequireDeed = 'Notifications/Structures/subjStructureOnlineRequireDeed'
    bodyLabel = 'Notifications/Structures/bodyStructureOnline'
    bodyLabelRequireDeed = 'Notifications/Structures/bodyStructureOnlineRequireDeed'
    bodyLabelFlex = 'Notifications/Structures/bodyStructureOnlineFlex'

    def _FormatSubject(self, data, notification):
        if data.get('requiresDeedTypeID', None):
            subjectLabel = self.subjectLabelRequireDeed
        else:
            subjectLabel = self.subjectLabel
        notification.subject = self.localization.GetByLabel(subjectLabel, **data)

    def _FormatBody(self, data, notification):
        structureTypeID = data.get(STRUCTURE_TYPEID)
        if structureTypeID and IsFlexStructure(structureTypeID):
            bodyLabel = self.bodyLabelFlex
        else:
            requiresDeedTypeID = data.get('requiresDeedTypeID', None)
            if requiresDeedTypeID:
                bodyLabel = self.bodyLabelRequireDeed
            else:
                bodyLabel = self.bodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, requiresDeedTypeID = None):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        if requiresDeedTypeID:
            data['requiresDeedTypeID'] = requiresDeedTypeID
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        return StructureOnline.MakeData(*sampleArgs)


class StructureLostShield(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureLostShield'
    oldbodyLabel = 'Notifications/Structures/oldbodyStructureLostShield'
    bodyLabel = 'Notifications/Structures/bodyStructureLostShield'

    def _FormatBody(self, data, notification):
        if 'timestamp' in data:
            bodyLabel = self.bodyLabel
        else:
            bodyLabel = self.oldbodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, reinforcedTimestamp, vulnerableTime):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['timeLeft'] = long(reinforcedTimestamp - blue.os.GetWallclockTime())
        data['timestamp'] = reinforcedTimestamp
        data['vulnerableTime'] = vulnerableTime
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (blue.os.GetWallclockTime() + 5 * const.HOUR + 37 * const.MIN, 3 * const.HOUR + 13 * const.MIN)
        return StructureLostShield.MakeData(*sampleArgs)


class StructureLostArmor(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureLostArmor'
    oldbodyLabel = 'Notifications/Structures/oldbodyStructureLostArmor'
    bodyLabel = 'Notifications/Structures/bodyStructureLostArmor'

    def _FormatBody(self, data, notification):
        if 'timestamp' in data:
            bodyLabel = self.bodyLabel
        else:
            bodyLabel = self.oldbodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, reinforcedTimestamp, vulnerableTime):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['timeLeft'] = long(reinforcedTimestamp - blue.os.GetWallclockTime())
        data['timestamp'] = reinforcedTimestamp
        data['vulnerableTime'] = vulnerableTime
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (blue.os.GetWallclockTime() + 5 * const.HOUR + 37 * const.MIN, 3 * const.HOUR + 13 * const.MIN)
        return StructureLostArmor.MakeData(*sampleArgs)


class StructureDestroyed(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureDestroyed'
    bodyLabel = 'Notifications/Structures/bodyStructureDestroyed'
    bodyLabelWh = 'Notifications/Structures/bodyStructureDestroyedWormhole'
    bodyLabelWithoutItemText = 'Notifications/Structures/bodyStructureDestroyedNoItemText'
    bodyLabelAbandoned = 'Notifications/Structures/bodyStructureDestroyedAbandoned'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, ownerCorpID, isAbandoned = False):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        ownerCorpLinkData = (SHOW_INFO, const.typeCorporation, ownerCorpID)
        data['ownerCorpName'] = cfg.eveowners.Get(ownerCorpID).name
        data['ownerCorpLinkData'] = ownerCorpLinkData
        data['isAbandoned'] = isAbandoned
        return data

    def _FormatBody(self, data, notification):
        solarSystemID = data.get(SOLAR_SYSTEM_ID, None)
        structureTypeID = data.get(STRUCTURE_TYPEID)
        if structureTypeID and IsFlexStructure(structureTypeID):
            bodyLabel = self.bodyLabelWithoutItemText
        elif data.get('isAbandoned', False):
            bodyLabel = self.bodyLabelAbandoned
        elif IsTriglavianSystem(solarSystemID):
            bodyLabel = self.bodyLabelWh
        elif IsKnownSpaceSystem(solarSystemID):
            bodyLabel = self.bodyLabel
        elif IsWormholeSystem(solarSystemID):
            bodyLabel = self.bodyLabelWh
        else:
            bodyLabel = self.bodyLabelWithoutItemText
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (CORPID_SCOPE, False)
        return StructureDestroyed.MakeData(*sampleArgs)


class StructureOwnershipTransferred(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/subjOwnershipTransferred'
    bodyLabel = 'Notifications/bodyOwnershipTransferred'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, newOwnerCorpID, oldOwnerCorpID, charID):
        data = {'structureID': structureID,
         'structureTypeID': structureTypeID,
         'solarSystemID': solarSystemID,
         'newOwnerCorpID': newOwnerCorpID,
         'oldOwnerCorpID': oldOwnerCorpID,
         'charID': charID,
         'structureName': cfg.evelocations.Get(structureID).name}
        return data

    def _FormatSubject(self, data, notification):
        dataToDisplay = self._GetDataToUseForDisplay(data)
        notification.subject = self.localization.GetByLabel(self.subjectLabel, **dataToDisplay)

    def _FormatBody(self, data, notification):
        dataToDisplay = self._GetDataToUseForDisplay(data)
        notification.body = self.localization.GetByLabel(self.bodyLabel, **dataToDisplay)

    def _GetDataToUseForDisplay(self, data):
        if data.get('structureID', None):
            structureID = data['structureID']
            structureTypeID = data['structureTypeID']
            structureLinkData = ('showinfo', structureTypeID, structureID)
            newOwnerCorpID = data['newOwnerCorpID']
            toCorporationLinkData = ('showinfo', const.typeCorporation, newOwnerCorpID)
            oldOwnerCorpID = data['oldOwnerCorpID']
            fromCorporationLinkData = ('showinfo', const.typeCorporation, oldOwnerCorpID)
            solarSystemID = data['solarSystemID']
            solarSystemLinkData = ('showinfo', const.typeSolarSystem, solarSystemID)
            charID = data['charID']
            characterLinkData = ('showinfo', cfg.eveowners.Get(charID).typeID, charID)
        else:
            structureLinkData = data['structureLinkData']
            structureID = structureLinkData[2]
            structureTypeID = structureLinkData[1]
            solarSystemLinkData = data['solarSystemLinkData']
            solarSystemID = solarSystemLinkData[2]
            toCorporationLinkData = data['toCorporationLinkData']
            newOwnerCorpID = toCorporationLinkData[2]
            fromCorporationLinkData = data['fromCorporationLinkData']
            oldOwnerCorpID = fromCorporationLinkData[2]
            characterLinkData = data['characterLinkData']
            charID = characterLinkData[2]
        structureName = data.get('structureName', None)
        if not structureName:
            try:
                structureName = cfg.evelocations.Get(structureID).name
            except KeyError:
                pass

        if not structureName:
            structureName = evetypes.GetName(structureTypeID)
        dataToDisplay = {'structureName': structureName,
         'toCorporationName': cfg.eveowners.Get(newOwnerCorpID).ownerName,
         'fromCorporationName': cfg.eveowners.Get(oldOwnerCorpID).ownerName,
         'solarSystemName': cfg.evelocations.Get(solarSystemID).name,
         'characterName': cfg.eveowners.Get(charID).ownerName,
         'structureLinkData': structureLinkData,
         'toCorporationLinkData': toCorporationLinkData,
         'fromCorporationLinkData': fromCorporationLinkData,
         'solarSystemLinkData': solarSystemLinkData,
         'characterLinkData': characterLinkData}
        return dataToDisplay

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (CORPID_SCOPE, CHARID_SCOPECEO, CORPID_SCOPE)
        return StructureOwnershipTransferred.MakeData(*sampleArgs)


class StructureItemsMovedToSafety(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjAssetsMovedToSafety'
    bodyLabel = 'Notifications/Structures/bodyAssetsMovedToSafety'
    subjectLabelCorp = 'Notifications/Structures/subjAssetsMovedToSafetyCorp'
    bodyLabelCorp = 'Notifications/Structures/bodyAssetsMovedToSafetyCorp'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, isCorpOwned, assetSafetyDurationMinimum, assetSafetyDurationFull, newStationID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['assetSafetyDurationMinimum'] = assetSafetyDurationMinimum
        data['assetSafetyMinimumTimestamp'] = blue.os.GetWallclockTime() + assetSafetyDurationMinimum
        data['assetSafetyDurationFull'] = assetSafetyDurationFull
        data['assetSafetyFullTimestamp'] = blue.os.GetWallclockTime() + assetSafetyDurationFull
        data['isCorpOwned'] = isCorpOwned
        _, structureLink = _GetSolarsystemAndStructureLinks(data)
        data['structureLink'] = structureLink
        data['newStationID'] = newStationID
        return data

    def _FormatSubject(self, data, notification):
        if data.get('isCorpOwned', False):
            subjectLabel = self.subjectLabelCorp
        else:
            subjectLabel = self.subjectLabel
        notification.subject = self.localization.GetByLabel(subjectLabel, **data)

    def _FormatBody(self, data, notification):
        if data.get('isCorpOwned', False):
            bodyLabel = self.bodyLabelCorp
        else:
            bodyLabel = self.bodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (3 * const.DAY, 20 * const.DAY, 60009655)
        return StructureItemsMovedToSafety.MakeData(*sampleArgs)


class StructureItemsNeedAttention(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjItemsNeedAttention'
    bodyLabel = 'Notifications/Structures/bodyItemsNeedAttention'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        return StructureItemsNeedAttention.MakeData(*sampleArgs)


class StructureMarketOrdersCancelled(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjMarketOrdersCancelled'
    bodyLabel = 'Notifications/Structures/bodyMarketOrdersCancelled'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        return StructureItemsNeedAttention.MakeData(*sampleArgs)


class StructureCloneDestruction(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/subjCloneJumpImplantDestruction'
    bodyLabel = 'Notifications/bodyCloneJumpImplantDestruction'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, newOwnerCorpID, oldOwnerCorpID, charID):
        data = {'structureName': cfg.evelocations.Get(structureID).name or evetypes.GetName(structureTypeID),
         'structureLinkData': ('showinfo', structureTypeID, structureID),
         'toCorporationName': cfg.eveowners.Get(newOwnerCorpID).ownerName,
         'toCorporationLinkData': ('showinfo', const.typeCorporation, newOwnerCorpID),
         'fromCorporationName': cfg.eveowners.Get(oldOwnerCorpID).ownerName,
         'fromCorporationLinkData': ('showinfo', const.typeCorporation, oldOwnerCorpID),
         'solarSystemName': cfg.evelocations.Get(solarSystemID).name,
         'solarSystemLinkData': ('showinfo', const.typeSolarSystem, solarSystemID),
         'characterName': cfg.eveowners.Get(charID).ownerName,
         'characterLinkData': ('showinfo', cfg.eveowners.Get(charID).typeID, charID)}
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (CORPID_SCOPE, CHARID_SCOPECEO, CORPID_SCOPE)
        return StructureOwnershipTransferred.MakeData(*sampleArgs)


class StructureCloneMoved(BaseStructureNotificationFormatter):
    pass


class StructureLostDockingAccess(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjLostDockingAccess'
    bodyLabel = 'Notifications/Structures/bodyLostDockingAccess'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        return StructureLostDockingAccess.MakeData(*sampleArgs)


class StructureOfficeRental(BaseStructureNotificationFormatter):
    pass


class StructureOfficeLeaseExpiration(BaseStructureNotificationFormatter):
    pass


class StructureOfficeRental(BaseStructureNotificationFormatter):
    pass


class StructureServicesOffline(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureServicesOffline'
    bodyLabel = 'Notifications/Structures/bodyStructureServicesOffline'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, listOfServiceModuleIDs):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['listOfServiceModuleIDs'] = listOfServiceModuleIDs
        return data

    def _FormatBody(self, data, notification):
        text = self._GetTextForTypes(data['listOfServiceModuleIDs'])
        data['listOfServices'] = text
        notification.body = self.localization.GetByLabel(self.bodyLabel, **data)

    def _GetTextForTypes(self, listOfServiceModuleIDs):
        textList = [ self.localization.GetByLabel('Notifications/Structures/TypeLabel', typeID=x) for x in listOfServiceModuleIDs ]
        return '<br>'.join(textList)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += ([35892],)
        return StructureServicesOffline.MakeData(*sampleArgs)


class StructureItemsDelivered(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjItemsDelieveredAtStructure'
    bodyLabel = 'Notifications/Structures/bodyItemsDelieveredAtStructure'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, charID, listOfTypesAndQty):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['listOfTypesAndQty'] = listOfTypesAndQty
        data['charID'] = charID
        return data

    def _FormatBody(self, data, notification):
        listOfTypesAndQty = data['listOfTypesAndQty']
        typesAndQtyText = self._GetTextForTypes(listOfTypesAndQty)
        data['typesAndQtyText'] = typesAndQtyText
        try:
            bodyText = self.localization.GetByLabel(self.bodyLabel, **data)
        except KeyError:
            bodyText = self.localization.GetByLabel('Notifications/Structures/UnableToFormatNotification')

        notification.body = bodyText

    def _GetTextForTypes(self, listOfTypesAndQty):
        textList = [ self.localization.GetByLabel('Notifications/Structures/QtyAndType', qty=x[0], typeID=x[1]) for x in listOfTypesAndQty ]
        return '<br>'.join(textList)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (CHARID_SCOPECEO, [(1, 1230), (5000000, 638)])
        return StructureItemsDelivered.MakeData(*sampleArgs)


class StructureCourierContractDestinationChanged(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjCourierContractDestinationChanged'
    bodyLabel = 'Notifications/Structures/bodyCourierContractDestinationChanged'

    @staticmethod
    def MakeData(newStationID, newStationTypeID, newSolarSystemID, oldSolarSystemID, contractName, contractID):
        data = {}
        data['newStationID'] = newStationID
        data['newLocationData'] = (SHOW_INFO, newStationTypeID, newStationID)
        data['oldSolarSystemID'] = oldSolarSystemID
        data['oldSolarSystemDataLink'] = (SHOW_INFO, const.typeSolarSystem, oldSolarSystemID)
        data['contractData'] = ('contract', newSolarSystemID, contractID)
        data['contractName'] = contractName
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        return StructureCourierContractDestinationChanged.MakeData(60014740, 57, 30002634, 30003147, 'testContract', 235)


class StructureWentLowPower(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureWentLowPower'
    bodyLabel = 'Notifications/Structures/bodyStructureWentLowPower'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        return BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)

    def _FormatSubject(self, data, notification):
        _, structureLink = _GetSolarsystemAndStructureLinks(data)
        notification.subject = self.localization.GetByLabel(self.subjectLabel, structureLink=structureLink, **data)

    def _FormatBody(self, data, notification):
        solarSystemLink, structureLink = _GetSolarsystemAndStructureLinks(data)
        try:
            bodyText = self.localization.GetByLabel(self.bodyLabel, structureLink=structureLink, solarsystemLink=solarSystemLink, **data)
        except KeyError:
            bodyText = self.localization.GetByLabel('Notifications/Structures/UnableToFormatNotification')

        notification.body = bodyText

    @staticmethod
    def MakeSampleData(variant = 0):
        return BaseStructureNotificationFormatter.GetBaseSampleArgs()


class StructureWentHighPower(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureWentHighPower'
    bodyLabel = 'Notifications/Structures/bodyStructureWentHighPower'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID):
        return BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)

    def _FormatSubject(self, data, notification):
        _, structureLink = _GetSolarsystemAndStructureLinks(data)
        notification.subject = self.localization.GetByLabel(self.subjectLabel, structureLink=structureLink, **data)

    def _FormatBody(self, data, notification):
        solarSystemLink, structureLink = _GetSolarsystemAndStructureLinks(data)
        try:
            bodyText = self.localization.GetByLabel(self.bodyLabel, structureLink=structureLink, solarsystemLink=solarSystemLink, **data)
        except KeyError:
            bodyText = self.localization.GetByLabel('Notifications/Structures/UnableToFormatNotification')

        notification.body = bodyText

    @staticmethod
    def MakeSampleData(variant = 0):
        return BaseStructureNotificationFormatter.GetBaseSampleArgs()


class StructuresReinforcementChanged(BaseNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructuresReinforcementChanged'
    bodyLabel = 'Notifications/Structures/bodyStructuresReinforcementChanged'
    bodyLabelNoWeekday = 'Notifications/Structures/bodyStructuresReinforcementChangedNoWeekday'

    def __init__(self, localizationImpl = None):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)
        self.localization = self.GetLocalizationImpl(localizationImpl)

    def Format(self, notification):
        data = notification.data
        self._FormatSubject(data, notification)
        self._FormatBody(data, notification)

    @staticmethod
    def MakeData(numStructures, allStructureInfo, weekday, hour, timestamp):
        return {'numStructures': numStructures,
         'allStructureInfo': allStructureInfo,
         'weekday': weekday,
         'hour': hour,
         'timestamp': timestamp}

    def _FormatSubject(self, data, notification):
        numStructures = data['numStructures']
        notification.subject = self.localization.GetByLabel(self.subjectLabel, numStructures=numStructures)

    def _FormatBody(self, data, notification):
        linksSorted = sorted([ (name.lower(), GetShowInfoLink(typeID, name, itemID)) for itemID, name, typeID in data['allStructureInfo'] ])
        linksSorted = [ item[1] for item in linksSorted ]
        linksText = '<br>'.join(linksSorted)
        weekDay = data['weekday']
        if weekDay == NO_REINFORCEMENT_WEEKDAY:
            dayText = ''
            bodyLabel = self.bodyLabelNoWeekday
        else:
            dayText = self.localization.GetByLabel(GetLabelPathForWeekday(weekDay))
            bodyLabel = self.bodyLabel
        hourText = '%.2d:00' % data['hour']
        bodyText = self.localization.GetByLabel(bodyLabel, listOfStructureLinks=linksText, weekday=dayText, reinforcementHour=hourText, timestamp=data['timestamp'])
        notification.body = bodyText

    @staticmethod
    def MakeSampleData(variant = 0):
        allStructureInfo = [(1, 'my Keepstar', 35834), (1, 'my fortizarrrr', 35833)]
        return StructuresReinforcementChanged.MakeData(2, allStructureInfo, 4, 14, gametime.GetWallclockTime())


class StructureIndustryJobsInteruptedBase(BaseStructureNotificationFormatter):
    subjectLabel = ''
    bodyLabel = ''
    subjectLabelCorp = ''
    bodyLabelCorp = ''

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, isCorpOwned):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['isCorpOwned'] = isCorpOwned
        _, structureLink = _GetSolarsystemAndStructureLinks(data)
        data['structureLink'] = structureLink
        return data

    def _FormatSubject(self, data, notification):
        if data.get('isCorpOwned', False):
            subjectLabel = self.subjectLabelCorp
        else:
            subjectLabel = self.subjectLabel
        notification.subject = self.localization.GetByLabel(subjectLabel, **data)

    def _FormatBody(self, data, notification):
        if data.get('isCorpOwned', False):
            bodyLabel = self.bodyLabelCorp
        else:
            bodyLabel = self.bodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (True,)
        return StructureItemsMovedToSafety.MakeData(*sampleArgs)


class StructureIndustryJobsPaused(StructureIndustryJobsInteruptedBase):
    subjectLabel = 'Notifications/Structures/subjStructureJobsPaused'
    bodyLabel = 'Notifications/Structures/bodyStructureJobsPaused'
    subjectLabelCorp = 'Notifications/Structures/subjStructureJobsPausedCorp'
    bodyLabelCorp = 'Notifications/Structures/bodyStructureJobsPausedCorp'


class StructureIndustryJobsCancelled(StructureIndustryJobsInteruptedBase):
    subjectLabel = 'Notifications/Structures/subjStructureJobsCancelled'
    bodyLabel = 'Notifications/Structures/bodyStructureJobsCancelled'
    subjectLabelCorp = 'Notifications/Structures/subjStructureJobsCancelledCorp'
    bodyLabelCorp = 'Notifications/Structures/bodyStructureJobsCancelledCorp'


class StructureImpendingAbandonmentAssetsAtRisk(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureImpendingAbandonmentAssetsAtRisk'
    bodyLabel = 'Notifications/Structures/bodyStructureImpendingAbandonmentAssetsAtRisk'
    subjectLabelCorp = 'Notifications/Structures/subjStructureImpendingAbandonmentAssetsAtRisk_Corp'
    bodyLabelCorp = 'Notifications/Structures/bodyStructureImpendingAbandonmentAssetsAtRisk_Corp'

    @staticmethod
    def MakeData(structureID, structureTypeID, solarSystemID, isCorpOwned, daysUntilAbandon):
        data = BaseStructureNotificationFormatter.GetBaseData(structureID, structureTypeID, solarSystemID)
        data['isCorpOwned'] = isCorpOwned
        data['daysUntilAbandon'] = daysUntilAbandon
        _, structureLink = _GetSolarsystemAndStructureLinks(data)
        data['structureLink'] = structureLink
        return data

    @staticmethod
    def MakeSampleData(variant = 0):
        sampleArgs = BaseStructureNotificationFormatter.GetBaseSampleArgs()
        sampleArgs += (False, 4)
        return StructureImpendingAbandonmentAssetsAtRisk.MakeData(*sampleArgs)

    def _FormatSubject(self, data, notification):
        if data.get('isCorpOwned', False):
            subjectLabel = self.subjectLabelCorp
        else:
            subjectLabel = self.subjectLabel
        notification.subject = self.localization.GetByLabel(subjectLabel, **data)

    def _FormatBody(self, data, notification):
        if data.get('isCorpOwned', False):
            bodyLabel = self.bodyLabelCorp
        else:
            bodyLabel = self.bodyLabel
        notification.body = self.localization.GetByLabel(bodyLabel, **data)


class StructurePaintPurchased(BaseNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructurePaintPurchased'
    bodyLabel = 'Notifications/Structures/bodyStructurePaintPurchased'

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel=self.subjectLabel, bodyLabel=self.bodyLabel)

    def Format(self, notification):
        characterID = notification.data['purchasedByCharacterID']
        structureIDs = notification.data['structureIDs']
        lpAmount = notification.data['lpAmount']
        durationSeconds = notification.data['durationSeconds']
        issuedAt = notification.data['issuedAt']
        numStructures = len(structureIDs)
        bodyMsgData = {'numStructures': numStructures,
         'lpAmount': lpAmount,
         'duration': durationSeconds * SEC,
         'issuedAt': issuedAt,
         'characterName': cfg.eveowners.Get(characterID).ownerName,
         'characterLinkData': ('showinfo', cfg.eveowners.Get(characterID).typeID, characterID)}
        notification.subject = GetByLabel(self.subjectLabel, numStructures=numStructures)
        notification.body = GetByLabel(self.bodyLabel, **bodyMsgData)

    @staticmethod
    def MakeData(characterID, structureIDs, lpAmount, durationSeconds, issuedAt):
        return {'purchasedByCharacterID': characterID,
         'structureIDs': structureIDs,
         'lpAmount': lpAmount,
         'durationSeconds': durationSeconds,
         'issuedAt': issuedAt}


class StructureLowReagentsAlert(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureMagmaticGasAlert'
    bodyLabel = 'Notifications/Structures/bodyStructureMagmaticGasAlert'


class StructureNoReagentsAlert(BaseStructureNotificationFormatter):
    subjectLabel = 'Notifications/Structures/subjStructureMagmaticGasDepleted'
    bodyLabel = 'Notifications/Structures/bodyStructureMagmaticGasDepleted'


def _GetSolarsystemAndStructureLinks(data):
    structureName = _GetLocationName(data[STRUCTURE_ID], '<someStructure>')
    structureLink = GetShowInfoLink(data[STRUCTURE_TYPEID], structureName, data[STRUCTURE_ID])
    locationID = data[SOLAR_SYSTEM_ID]
    solarsystemName = _GetLocationName(locationID, '<someLocation>')
    solarSystemLink = GetShowInfoLink(const.typeSolarSystem, solarsystemName, locationID)
    return (solarSystemLink, structureLink)


def _GetLocationName(locationID, fallback):
    try:
        locationName = cfg.evelocations.Get(locationID).name
    except KeyError:
        locationName = fallback

    return locationName
