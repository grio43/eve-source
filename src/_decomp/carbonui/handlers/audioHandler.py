#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\handlers\audioHandler.py
__author__ = 'fridrik'

class AudioHandler(object):

    def StopSoundLoop(self, *args, **kwds):
        print 'Unhandled audio.StopSoundLoop', args, kwds

    def GetAudioBus(self, *args, **kwds):
        print 'Unhandled audio.GetAudioBus', args, kwds
        return (None, None)

    def Activate(self, *args, **kwds):
        print 'Unhandled audio.Activate', args, kwds

    def Deactivate(self, *args, **kwds):
        print 'Unhandled audio.Deactivate', args, kwds
