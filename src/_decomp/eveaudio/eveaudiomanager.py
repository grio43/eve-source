#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\eveaudiomanager.py
import sys
import audio2
import eveaudio
import logging
from audio2.audiomanager import AudioManager
from fsdBuiltData.common.wwiseEvents import WwiseEvents
from fsdBuiltData.common.wwiseSoundBanks import WwiseSoundBanks
from fsdBuiltData.common.wwiseWemFileIDs import WwiseWemFileIDs
from eveaudio import EVE_COMMON_BANKS
from eveaudio.audactionrecords import AudActionRecordTupleToInstance
from eveaudio.utils import Singleton
from weakness import WeakMethod
LANGUAGE_ID_TO_BANK = {'en': 'English(US)',
 'de': 'German',
 'ru': 'Russian',
 'ja': 'Japanese',
 'zh': 'Chinese',
 'fr': 'French(France)',
 'ko': 'Korean',
 'es': 'Spanish'}
logger = logging.getLogger(__name__)

def GetAudioManager():
    if not eveaudio.g_audioManager:
        raise ValueError('No instance of EveAudioManager has been created! You must call eveaudio.eveaudiomanager.CreateAudioManager before using GetAudioManager!', None, sys.exc_info()[2])
    return eveaudio.g_audioManager


def CreateAudioManager(baseSoundbankPath, languageID, applicationName):
    if not eveaudio.g_audioManager:
        eveaudio.g_audioManager = EveAudioManager(baseSoundbankPath, languageID, applicationName)
    return eveaudio.g_audioManager


class EveAudioManager(AudioManager):

    def __init__(self, baseSoundbankPath, languageID, applicationName):
        languageDirectory = self.GetLanguageDirectoryPath(languageID)
        super(EveAudioManager, self).__init__(baseSoundbankPath, languageDirectory, applicationName)
        self.wwiseEventsMetadata = WwiseEvents()
        self.wwiseSoundBanksMetadata = WwiseSoundBanks()
        self.wwiseWemMetadata = WwiseWemFileIDs()
        self.Initialize()

    def Initialize(self):
        audioMetadata = {'Events': self.wwiseEventsMetadata.GenerateReverseLookup(),
         'SoundBanks': self.wwiseSoundBanksMetadata.TransformToDict(),
         'WemFileIDs': self.wwiseWemMetadata.TransformToDict()}
        return super(EveAudioManager, self).Initialize(audioMetadata, defaultSoundBanks=EVE_COMMON_BANKS)

    def GetLanguageDirectoryPath(self, languageID):
        filepath = ''
        try:
            filepath = LANGUAGE_ID_TO_BANK[languageID.lower()]
        except KeyError:
            raise ValueError('Unknown language ID {} passed in!'.format(languageID), None, sys.exc_info()[2])

        return filepath

    def ReloadSoundBanks(self):
        self.Initialize()
        return super(EveAudioManager, self).ReloadSoundBanks()

    def SetDebugLogCallback(self, callback):
        self.manager.log = audio2.AudActionLogCB()
        self.manager.log.RegisterCallback(self._ProcessAndForwardAudActionRecord)
        self.debugLogCallback = WeakMethod(callback)

    def StopDebugLogging(self):
        self.manager.log = None

    def _ProcessAndForwardAudActionRecord(self, actionRecord):
        if self.debugLogCallback and self.debugLogCallback.self_ref() is not None:
            self.debugLogCallback(AudActionRecordTupleToInstance(actionRecord))
