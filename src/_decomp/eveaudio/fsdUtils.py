#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\fsdUtils.py
import sys
import evetypes
import logging
from fsdBuiltData.client.musicTriggers import GetMusicTrigger
from fsdBuiltData.common.soundIDs import GetSoundEventName, GetSound
from operations.client.operationscontroller import GetOperationsController
logger = logging.getLogger('eveaudio.fsdUtils')
logger.level = logging.INFO
logger.addHandler(logging.StreamHandler(sys.stdout))

def GetMusicTriggerFromOperation(operationID):
    operation = GetOperationsController().get_operation_by_id(operationID)
    musicTriggerID = getattr(operation, 'musicTrigger', 0)
    musicTrigger = GetMusicTrigger(musicTriggerID)
    return (musicTriggerID, musicTrigger)


def GetMusicTriggerFromConversation(conversationID):
    conversationSvc = sm.GetService('conversationService')
    line = conversationSvc.get_active_conversation_line()
    musicTriggerID = getattr(line, 'music_trigger', 0)
    musicTrigger = GetMusicTrigger(musicTriggerID)
    return (musicTriggerID, musicTrigger)


def GetEventFromSoundID(soundID):
    event = ''
    sound = GetSound(soundID)
    if sound:
        event = GetSoundEventName(soundID, '')
    else:
        logger.error('Sound ID {} is invalid.'.format(soundID))
    return event


def GetSoundUrlForType(slimItem):
    soundUrl = sm.GetService('incursion').GetSoundUrlByKey(slimItem.groupID)
    if soundUrl is None:
        soundID = evetypes.GetSoundID(slimItem.typeID)
        if soundID is not None:
            soundUrl = GetSoundEventName(soundID)
    return soundUrl
