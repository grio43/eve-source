#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\audio2\audiomanager.py
import audio2
INIT_BANK = 'Init.bnk'

class AudioManager(object):

    def __init__(self, baseSoundbankPath, languageDirectory, applicationName):
        self.defaultSoundBanks = []
        self.manager = audio2.GetOrCreateManager()
        self.settings = self._CreateAudioSettings(baseSoundbankPath, languageDirectory, applicationName)
        self.staticDataRepository = audio2.GetStaticDataRepository()
        self.banksWaitingToLoad = set()
        self.enabled = False
        self.manager.UpdateSettings(self.settings)

    def AddAndLoadDefaultSoundBank(self, soundBankName):
        if soundBankName not in self.defaultSoundBanks:
            self.defaultSoundBanks.append(soundBankName)
            self.LoadSoundBank(soundBankName)

    def Disable(self):
        self.banksWaitingToLoad = set(self.GetLoadedSoundBanks())
        self.manager.Disable()
        self.enabled = False

    def DisableSoundPrioritization(self):
        self.manager.DisableAudioCulling()

    def Enable(self, soundBanksToLoad = []):
        self.manager.Enable(self.defaultSoundBanks + soundBanksToLoad + list(self.banksWaitingToLoad))
        audio2.GetListener()
        self.enabled = True
        self.banksWaitingToLoad = set()

    def EnableSoundPrioritization(self):
        self.manager.EnableAudioCulling()

    def GetAudioEmitter(self, emitterID):
        return self.manager.GetAudioEmitter(emitterID)

    def GetLoadedSoundBanks(self):
        return self.manager.GetLoadedSoundBanks()

    def GetSoundPrioritizationEnabled(self):
        return self.manager.audioCullingEnabled

    def Initialize(self, audioMetadata, defaultSoundBanks = []):
        self.defaultSoundBanks = defaultSoundBanks
        self.staticDataRepository.Initialize(audioMetadata)

    def LoadSoundBank(self, bankName):
        if not self.enabled:
            self.banksWaitingToLoad.add(bankName)
        else:
            self.manager.LoadBank(bankName)

    def LoadSoundBanks(self, banksToLoad):
        for bank in banksToLoad:
            self.LoadSoundBank(bank)

    def ReloadSoundBanks(self):
        banksBeforeReload = self.manager.GetLoadedSoundBanks()
        self.Disable()
        self.Enable(soundBanksToLoad=banksBeforeReload)

    def RemoveAndUnloadDefaultSoundBank(self, soundBankName):
        if soundBankName in self.defaultSoundBanks:
            self.defaultSoundBanks.remove(soundBankName)
            self.UnloadSoundBank(soundBankName)

    def SetGlobalRTPC(self, rtpcName, value):
        return self.manager.SetGlobalRTPC(rtpcName, value)

    def SetState(self, stateGroup, stateName):
        return self.manager.SetState(stateGroup, stateName)

    def StopAllPlayingSounds(self):
        self.manager.StopAll()

    def SwapSoundBanks(self, banksToLoad):
        if self.enabled:
            loadedBanks = set(self.GetLoadedSoundBanks())
        else:
            loadedBanks = self.banksWaitingToLoad
        excludedBanks = set(self.defaultSoundBanks).union(set(banksToLoad))
        banksToUnload = loadedBanks.difference(excludedBanks)
        banksToLoad = set(banksToLoad).difference(loadedBanks)
        self.LoadSoundBanks(banksToLoad)
        self.UnloadSoundBanks(banksToUnload)

    def UnloadSoundBanks(self, soundBanksToUnload):
        for soundBank in soundBanksToUnload:
            self.UnloadSoundBank(soundBank)

    def UnloadSoundBank(self, bankName):
        if bankName not in self.defaultSoundBanks and bankName != INIT_BANK:
            if not self.enabled:
                if bankName in self.banksWaitingToLoad:
                    self.banksWaitingToLoad.remove(bankName)
            self.manager.UnloadBank(bankName)

    def _CreateAudioSettings(self, baseSoundbankPath, language, applicationName):
        settings = audio2.AudSettings()
        settings.applicationName = applicationName
        settings.baseSoundbankPath = baseSoundbankPath
        settings.soundbankLanguage = language
        return settings
