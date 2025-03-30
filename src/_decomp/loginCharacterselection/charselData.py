#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginCharacterselection\charselData.py
from collections import defaultdict
from characterskills import GetSPForLevelRaw
from dogma.const import attributeSkillTimeConstant
from eve.common.script.util.facwarCommon import GetCombatEnemyFactions
from itertoolsext import Bundle
from eve.common.script.sys.idCheckers import IsStation
import dogma.data as dogma_data

class CharacterSelectionData:

    def __init__(self, charRemoteSvc, cfg, localization, stripTags):
        self.charRemoteSvc = charRemoteSvc
        self.cfg = cfg
        self.localization = localization
        self.stripTags = stripTags
        self.details = {}
        self.userDetails = None
        self.FetchCharacterInfoForUserID()

    def FetchCharacterInfoForUserID(self):
        if self.details:
            return None
        self.trainingDetails = (None, None)
        userDetails, self.trainingDetails, characterDetails, wars = self.charRemoteSvc.GetCharacterSelectionData()
        warsByCharacterID = defaultdict(list)
        for eachWar in wars:
            warsByCharacterID[eachWar.characterID].append(eachWar)

        self.userDetails = userDetails[0]
        for row in characterDetails:
            wars = warsByCharacterID[row.characterID]
            character = CharacterSelectionDataForCharacter(row.characterID, row, self.cfg, self.localization, self.stripTags, wars)
            self.details[row.characterID] = character

    def GetCharInfo(self, charID):
        return self.details[charID]

    def GetNumCharacterSlots(self):
        return self.userDetails.characterSlots

    def GetUserName(self):
        return self.userDetails.userName

    def GetUserCreationDate(self):
        return self.userDetails.creationDate

    def GetChars(self):
        chars = [ data.charDetails for data in self.details.itervalues() ]
        chars.sort(key=lambda x: x.logoffDate, reverse=True)
        return chars

    def GetSubscriptionEndTime(self):
        return Bundle(subscriptionEndTime=self.userDetails.subscriptionEndTime, trainingEndTimes=self.trainingDetails)

    def GetMaxServerCharacters(self):
        return int(self.userDetails.maxCharacterSlots)


class CharacterSelectionDataForCharacter:

    def __init__(self, charID, charDetails, cfg, localization, stripTags, wars):
        self.charID = charID
        self.charDetails = charDetails
        self.cfg = cfg
        self.localization = localization
        self.stripTags = stripTags
        self.wars = wars
        factionID = getattr(charDetails, 'factionID', None)
        if factionID:
            try:
                enemies = GetCombatEnemyFactions(factionID)
            except RuntimeError:
                enemies = []

            factionWars = []
            for eachID in enemies:
                warBundle = Bundle(characterID=charID, warID=None, declaredByID=eachID, againstID=factionID, mutual=True, ally=False)
                factionWars.append(warBundle)

            if factionWars:
                self.wars += factionWars
        if charDetails.stationID:
            self.stationID = charDetails.stationID
            if charDetails.solarSystemID:
                self.solarSystemID = charDetails.solarSystemID
            else:
                self.solarSystemID = self.cfg.evelocations.Get(self.stationID).solarSystemID
        elif charDetails.solarSystemID:
            self.stationID = None
            self.solarSystemID = charDetails.solarSystemID
        else:
            self.stationID = None
            self.solarSystemID = None
        if self.solarSystemID:
            self.securityStatus = self.cfg.mapSystemCache[self.solarSystemID].securityStatus
        else:
            self.securityStatus = 0.0

    def GetWalletBalance(self):
        balance = self.charDetails.balance
        return balance

    def GetSkillInfo(self):
        skillPoints = self.charDetails.skillPoints
        return skillPoints

    def GetCorporationInfo(self):
        return (self.charDetails.corporationID, self.charDetails.allianceID)

    def GetUnreaddMailCount(self):
        unreadMailCount = self.charDetails.unreadMailCount
        return unreadMailCount

    def GetCurrentLocationInfo(self):
        if self.securityStatus > 0.0 and self.securityStatus < 0.05:
            securityStatus = 0.05
        else:
            securityStatus = self.securityStatus
        return (self.solarSystemID, securityStatus)

    def GetCurrentStation(self):
        return self.stationID

    def GetCurrentStationAndStationLocation(self):
        if self.stationID is None:
            return
        if not IsStation(self.stationID):
            return {'stationName': self.cfg.evelocations.Get(self.stationID).name,
             'orbitName': '',
             'shortOrbitName': ''}

        def CleanString(locationString):
            locationString = self.stripTags(locationString, stripOnly=['localized'])
            locationString = locationString.replace(self.localization.HIGHLIGHT_IMPORTANT_MARKER, '')
            return locationString

        orbitID = self.cfg.stations.Get(self.stationID).orbitID
        orbitName = self.cfg.evelocations.Get(orbitID).name
        orbitName = CleanString(orbitName)
        solarsystemName = self.cfg.evelocations.Get(self.solarSystemID).name
        solarsystemName = CleanString(solarsystemName)
        shortOrbitName = orbitName.replace(solarsystemName, '').strip()
        moonText = self.localization.GetByLabel('UI/Locations/LocationMoonLong')
        shortOrbitName = shortOrbitName.replace(moonText, '').replace('  ', ' ')
        stationName = self.cfg.evelocations.Get(self.stationID).name
        stationName = CleanString(stationName)
        stationNameWithoutOrbit = stationName.replace(orbitName, '')
        stationNameWithoutOrbit = stationNameWithoutOrbit.strip(' - ')
        stationInfo = {'stationName': stationNameWithoutOrbit,
         'orbitName': orbitName,
         'shortOrbitName': shortOrbitName}
        return stationInfo

    def GetCurrentShip(self):
        return self.charDetails.shipTypeID

    def GetPaperDollState(self):
        return self.charDetails.paperdollState

    def GetFinishedSkills(self):
        return self.charDetails.finishedSkills

    def GetWalletChanged(self):
        return self.charDetails.balanceChange

    def IsCharacterAtWar(self):
        return bool(self.wars)

    def GetCharacterWars(self):
        return self.wars

    def GetSkillInTrainingInfo(self):
        typeID = self.charDetails.skillTypeID
        if typeID is None:
            return self._GetSkillInTrainingInfo()
        toLevel = self.charDetails.toLevel
        return self._GetSkillInTrainingInfo(currentSkill=typeID, level=self.charDetails.toLevel, trainingStartTime=self.charDetails.trainingStartTime, trainingEndTime=self.charDetails.trainingEndTime, queueEndTime=self.charDetails.queueEndTime, finishSP=self._GetSkillPointsWithDefaults(self.charDetails.finishSP, toLevel, typeID), trainedSP=self._GetSkillPointsWithDefaults(self.charDetails.trainedSP, toLevel - 1, typeID), fromSP=self._GetSkillPointsWithDefaults(None, toLevel - 1, typeID))

    def _GetSkillInTrainingInfo(self, currentSkill = None, level = None, trainingStartTime = None, trainingEndTime = None, queueEndTime = None, finishSP = None, trainedSP = None, fromSP = None):
        return {'currentSkill': currentSkill,
         'level': level,
         'trainingStartTime': trainingStartTime,
         'trainingEndTime': trainingEndTime,
         'queueEndTime': queueEndTime,
         'finishSP': finishSP,
         'trainedSP': trainedSP,
         'fromSP': fromSP}

    def _GetSkillPointsWithDefaults(self, value, level, typeID):
        if typeID is None:
            return
        if value is not None:
            return value
        skillTimeConstant = dogma_data.get_type_attribute(typeID, attributeSkillTimeConstant)
        return GetSPForLevelRaw(skillTimeConstant, level)

    def GetDeletePrepareTime(self):
        return self.charDetails.deletePrepareDateTime

    def IsPreparingForDeletion(self):
        return bool(self.charDetails.deletePrepareDateTime)

    def IsUnavailable(self):
        return bool(self.charDetails.lockTypeID)

    def GetCharacterLockType(self):
        return self.charDetails.lockTypeID
