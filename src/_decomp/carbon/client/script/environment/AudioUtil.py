#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\client\script\environment\AudioUtil.py


def CheckAudioFileForEnglish(audioPath):
    if settings.user.ui.Get('forceEnglishVoice', False):
        audioPath = audioPath[:-3] + 'EN.' + audioPath[-3:]
    return audioPath


def PlaySound(audioPath):
    sm.GetService('audio').SendUIEvent(audioPath)


def SetSoundParameter(rtpcName, value):
    sm.GetService('audio').SetUIRTPC(rtpcName, value)
