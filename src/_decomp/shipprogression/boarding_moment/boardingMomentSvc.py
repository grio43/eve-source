#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\boardingMomentSvc.py
import os
import blue
import yaml
from carbonui.services.setting import UserSettingBool
from shipprogression.boarding_moment.feature_flags import are_first_time_boarding_moments_enabled
from shipprogression.boarding_moment.settings import first_time_boarding_moments_enabled_by_user
boardingMomentService = None

def GetBoardingMomentService():
    global boardingMomentService
    if not session.userid:
        return
    if boardingMomentService is None:
        boardingMomentService = BoardingMomentService()
    return boardingMomentService


def ResetBoardingMomentService():
    global boardingMomentService
    if boardingMomentService is not None:
        boardingMomentService = None


class BoardingMomentService(object):
    IGNORED_GROUPS = [4]
    __guid__ = 'svc.boardingMomentSvc'
    __notifyevents__ = ['OnSessionReset']

    def __init__(self):
        self._dataHandler = _BoardingMomentDataHandler()
        self._ignore_setting = UserSettingBool('BoardingMoment_Ignore', False)
        self.is_playing = False
        sm.RegisterNotify(self)

    def OnSessionReset(self):
        ResetBoardingMomentService()
        sm.UnregisterNotify(self)

    def HasSeen(self, typeID):
        if not first_time_boarding_moments_enabled_by_user.get():
            return True
        if not are_first_time_boarding_moments_enabled():
            return True
        return self._dataHandler.HasSeen(typeID)

    def HasUnseen(self, typeID):
        return self._dataHandler.HasUnseen(typeID)

    def ShouldPlay(self, typeID):
        if self.HasSeen(typeID):
            return False
        return self.HasUnseen(typeID)

    def SetUnseen(self, typeID):
        if first_time_boarding_moments_enabled_by_user.get():
            self._dataHandler.SetUnseen(typeID)

    def SetSeen(self, typeID):
        self._dataHandler.SetSeen(typeID)

    def Clear(self):
        self._dataHandler.Clear()

    def IsPlaying(self):
        return self.is_playing


class _BoardingMomentDataHandler(object):

    def __init__(self):
        self._path = os.path.join(blue.paths.ResolvePathForWriting(u'cache:/user_%d.boarding.yaml' % session.userid))
        self._boardingEntries = {}
        self._fileCreated = False
        if os.path.exists(self._path):
            self._boardingEntries = self._ReadFile()
            if self._boardingEntries is None or len(self._boardingEntries) == 0:
                self._boardingEntries = {}
        else:
            self._fileCreated = True
            newFile = file(self._path, 'w')
            newFile.close()

    def HasSeen(self, typeID):
        if typeID in self._boardingEntries:
            return self._boardingEntries[typeID]
        return False

    def HasUnseen(self, typeID):
        if typeID in self._boardingEntries:
            return not self._boardingEntries[typeID]
        return False

    def SetUnseen(self, typeID):
        self._boardingEntries[typeID] = False
        self._WriteFile(self._boardingEntries)

    def SetSeen(self, typeID):
        self._boardingEntries[typeID] = True
        self._WriteFile(self._boardingEntries)

    def Clear(self):
        self._boardingEntries = {}
        self._WriteFile(self._boardingEntries)

    def _ReadFile(self, default = None):
        with open(self._path) as openFile:
            data = yaml.load(openFile)
        return data or default

    def _WriteFile(self, data):
        with open(self._path, 'w') as openFile:
            yaml.dump(data, openFile)
