#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\ccSvc.py
import carbon.common.lib.telemetry as telemetry
import paperdoll
from carbon.common.script.sys.service import Service
from carbon.common.script.util.commonutils import StripTags
from characterdata.schools import get_school
from eve.client.script.ui.login.intromovie.introcontroller import IntroController
from eve.common.script.sys.dbrow import LookupConstValue
from inventorycommon.const import categoryApparel, containerHangar, flagHangar, flagWardrobe
import localization
from loginCharacterselection.charselData import CharacterSelectionData
import uthread
import launchdarkly

class CCSvc(Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.cc'
    __dependencies__ = ['invCache']

    def Run(self, *args, **kwargs):
        super(CCSvc, self).Run(*args, **kwargs)
        LookupConstValue('', '')
        self.chars = None
        self.characterSelectionData = None
        self.charCreationInfo = None
        self.bloodlineDataByRaceID, self.bloodlineDataByID = (None, None)
        self.dollState = None
        self.availableTypeIDs = None
        self.introController = IntroController()

    def GetCharacterSelectionData(self, force = 0):
        if self.characterSelectionData is None or force:
            self.characterSelectionData = CharacterSelectionData(sm.RemoteSvc('charUnboundMgr'), cfg, localization, StripTags)
            self.PrimeCharacterDetails(self.characterSelectionData.GetChars())
        return self.characterSelectionData

    def ClearCharacterSelectionData(self):
        self.characterSelectionData = None

    def PrimeCharacterDetails(self, characterDetails):
        primeOwners = set()
        primeLocations = set()
        primeTickers = set()
        for character in characterDetails:
            primeOwners.add(character.characterID)
            primeOwners.add(character.corporationID)
            if character.allianceID:
                primeOwners.add(character.allianceID)
            if character.stationID is not None:
                primeLocations.add(character.stationID)
            primeTickers.add(character.corporationID)

        cfg.eveowners.Prime(primeOwners)
        cfg.corptickernames.Prime(primeTickers)
        if len(primeLocations):
            cfg.evelocations.Prime(primeLocations)

    def GetCharactersToSelect(self, force = 0):
        return self.GetCharacterSelectionData(force).GetChars()

    def GoBack(self, *args):
        sm.GetService('viewState').ActivateView('charsel')

    def CreateCharacterWithDoll(self, charactername, bloodlineID, genderID, ancestryID, charInfo, portraitInfo, schoolID, raceID, *args):
        self.LogInfo('charInfo:', charInfo)
        charID = sm.RemoteSvc('charUnboundMgr').CreateCharacterWithDoll(charactername, raceID, bloodlineID, genderID, ancestryID, charInfo, portraitInfo, schoolID)
        self.ClearCharacterSelectionData()
        return charID

    def UpdateExistingCharacterFull(self, charID, dollInfo, portraitInfo, dollExists, flush = False):
        sm.RemoteSvc('paperDollServer').UpdateExistingCharacterFull(charID, dollInfo, portraitInfo, dollExists, flush=flush)
        sm.GetService('paperdoll').ClearCurrentPaperDollData()
        sm.GetService('objectCaching').InvalidateCachedMethodCall('paperDollServer', 'GetPaperDollData', charID)
        self.GetCharacterSelectionData(force=1)

    def UpdateExistingCharacterLimited(self, charID, dollInfo, portraitInfo, dollExists):
        dollData = dollInfo.copy()
        dollData.sculpts = []
        self.LogInfo('UpdateExistingCharacterLimited', charID)
        sm.RemoteSvc('paperDollServer').UpdateExistingCharacterLimited(charID, dollData, portraitInfo, dollExists)
        sm.GetService('paperdoll').ClearCurrentPaperDollData()
        sm.GetService('objectCaching').InvalidateCachedMethodCall('paperDollServer', 'GetPaperDollData', charID)
        self.GetCharacterSelectionData(force=1)

    def UpdateExistingCharacterBloodline(self, charID, bloodlineID, refreshCharData = False):
        sm.RemoteSvc('charUnboundMgr').UpdateCharacterBloodline(charID, bloodlineID)
        if refreshCharData:
            sm.GetService('paperdoll').ClearCurrentPaperDollData()
            sm.GetService('objectCaching').InvalidateCachedMethodCall('paperDollServer', 'GetPaperDollData', charID)
            self.GetCharacterSelectionData(force=1)
        session.SetAttributes({'bloodlineID': bloodlineID})

    @telemetry.ZONE_METHOD
    def GetPortraitData(self, charID):
        data, _ = sm.RemoteSvc('paperDollServer').GetPaperDollPortraitDataFor(charID)
        if len(data):
            return data[0]

    def StoreCurrentDollState(self, state, *args):
        self.dollState = state

    def NoExistingCustomization(self, *arags):
        return self.dollState == paperdoll.State.no_existing_customization

    def ClearMyAvailabelTypeIDs(self, *args):
        self.availableTypeIDs = None

    def GetMyApparel(self):
        if getattr(self, 'availableTypeIDs', None) is not None:
            return self.availableTypeIDs
        availableTypeIDs = set()
        if session.stationid or session.structureid:
            try:
                inv = self.invCache.GetInventory(containerHangar)
                availableTypeIDs.update({i.typeID for i in inv.List(flagHangar) if i.categoryID == categoryApparel})
                inv = self.invCache.GetInventoryFromId(session.charid)
                availableTypeIDs.update({i.typeID for i in inv.List() if i.flagID == flagWardrobe})
            except Exception as e:
                self.LogException(e)

        self.availableTypeIDs = availableTypeIDs
        return self.availableTypeIDs

    def GetSchoolAndSchoolCorpInfoForChar(self, charID):
        charInfo = sm.RemoteSvc('charMgr').GetPublicInfo(charID)
        schoolInfo = get_school(charInfo.schoolID)
        schoolCorpInfo = sm.GetService('corp').GetCorporation(schoolInfo.corporationID)
        return (schoolInfo, schoolCorpInfo)

    def _LoadGame(self, characterID, skipTutorial):
        sm.GetService('sessionMgr').PerformSessionChange(sessionChangeReason='charcreation', func=sm.RemoteSvc('charUnboundMgr').SelectCharacterID, charID=characterID, secondChoiceID=None, skipTutorial=skipTutorial)
        launchdarkly.get_client().character_select(session.userid, characterID, session.languageID)

    def FinishCharacterCreation(self, characterID, skipTutorial):
        uthread.new(self.introController.play_intro, characterID, skipTutorial)
        self._LoadGame(characterID, skipTutorial)

    def IsIntroPlaying(self):
        return self.introController.is_intro_playing

    def IsGameLoaded(self):
        return self.introController.is_game_loaded and not self.introController.is_intro_playing

    def StopIntro(self):
        self.introController.stop_intro()
