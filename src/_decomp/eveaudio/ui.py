#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\ui.py
import audio2
import evetypes
import logging
from eveaudio.auraQueueManager import AuraQueueManager
from eveaudio.const import AURA_MESSAGES, USER_ERROR_KEY_TO_EVENT
from eveaudio.utils import Singleton
from fsdBuiltData.common.soundIDs import GetSoundEventName
logger = logging.getLogger('eveaudio.ui')

class UIAudioManager(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.eventCallbackSubscriptions = []
        self.audioEmitter = audio2.GetUIPlayer()
        self.auraQueueManager = AuraQueueManager(self.SendUIEventWithCallback)
        self.audioEmitter.eventSenderCallback = self.CallbackFromEventSender
        self.SubscribeToEventCallback(self.auraQueueManager.QueueCallbackHandler)

    def GetUIEmitter(self):
        return self.audioEmitter

    def CallbackFromEventSender(self, event):
        for callbackFunction in self.eventCallbackSubscriptions:
            callbackFunction(event)

    def SubscribeToEventCallback(self, callbackFunc):
        if not self._IsCallbackInSubscriptionList(callbackFunc):
            self.eventCallbackSubscriptions.append(callbackFunc)

    def _IsCallbackInSubscriptionList(self, callbackFunc):
        return callbackFunc in self.eventCallbackSubscriptions

    def UnsubscribeFromEventCallback(self, callbackFunc):
        if self._IsCallbackInSubscriptionList(callbackFunc):
            self.eventCallbackSubscriptions.remove(callbackFunc)

    def SendUIEventWithCallback(self, event):
        return self.audioEmitter.SendEventWithCallback(unicode(event))

    def SendUIEvent(self, event):
        event = event
        return self.audioEmitter.SendEvent(event)

    def SendUIEventByTypeID(self, typeID):
        soundID = evetypes.GetSoundID(typeID)
        if not soundID:
            logger.exception('No soundID assigned to typeID: %s' % typeID)
            return
        eventName = GetSoundEventName(soundID)
        if not eventName:
            logger.exception('No Wwise event name assigned to soundID: %s' % soundID)
            return
        return self.SendUIEvent('ui_' + eventName)

    def StopUIEvent(self, playingID):
        self.audioEmitter.StopSound(playingID, 100)

    def PostDialogueEvent(self, event):
        return self.audioEmitter.PostDialogueEvent(event)

    def SeekOnEventPercent(self, playingID, percentToSeek):
        self.audioEmitter.SeekOnEventPercent(playingID, percentToSeek)

    def SeekOnEventMs(self, playingID, msToSeek):
        self.audioEmitter.SeekOnEventMs(playingID, msToSeek)

    def GetDialoguePlayPosition(self, playingID):
        return self.audioEmitter.GetEventPlayPosition(playingID)

    def SetUIRTPC(self, rtpcName, value):
        self.audioEmitter.SetRTPC(rtpcName, value)

    def SendAudioMessage(self, msg, userErrorKey = None):
        audioMsg = ''
        if userErrorKey and userErrorKey in USER_ERROR_KEY_TO_EVENT.keys():
            audioMsg = USER_ERROR_KEY_TO_EVENT[userErrorKey]
        elif isinstance(msg, str):
            audioMsg = msg
        elif hasattr(msg, 'audio'):
            if msg.audio:
                audioMsg = msg.audio
        if not audioMsg:
            return
        audioMsg = audioMsg
        if audioMsg in AURA_MESSAGES:
            self.auraQueueManager.AddMessage(audioMsg)
        else:
            self.SendUIEvent(audioMsg)
