#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\towGameSvc.py
import signals
from carbon.common.script.sys.service import Service

class TowGameSvc(Service):
    __guid__ = 'svc.towGameSvc'
    __startupdependencies__ = []

    def __init__(self):
        super(TowGameSvc, self).__init__()
        self.SIGNAL_OnTowGameAdded = signals.Signal(signalName='OnTowGameAdded')
        self.SIGNAL_OnTowGameRemoved = signals.Signal(signalName='OnTowGameRemoved')
        self.SIGNAL_OnTowGameUpdated = signals.Signal(signalName='OnTowGameNewScore')
        self.currentTowGameSnapshot = None

    def AddTowGame(self, itemID, winThreshold, scoreByFactionID):
        self.currentTowGameSnapshot = TowGameSnapshot(itemID, winThreshold, scoreByFactionID)
        self.SIGNAL_OnTowGameAdded(self.currentTowGameSnapshot)

    def UpdateTowGame(self, scoreByFactionID):
        if self.currentTowGameSnapshot is not None:
            self.currentTowGameSnapshot._scoreByFactionID = scoreByFactionID
        self.SIGNAL_OnTowGameUpdated(self.currentTowGameSnapshot)

    def RemoveTowGame(self):
        self.currentTowGameSnapshot = None
        self.SIGNAL_OnTowGameRemoved()

    def GetCurrentTowGame(self):
        return self.currentTowGameSnapshot


class TowGameSnapshot(object):

    def __init__(self, towGameObjectiveItemID, winThreshold, scoreByFactionID):
        self._scoreByFactionID = scoreByFactionID
        self._winThreshold = winThreshold
        self._towGameObjectiveItemID = towGameObjectiveItemID

    @property
    def scoreByFactionID(self):
        return self._scoreByFactionID

    @property
    def winThreshold(self):
        return self._winThreshold

    @property
    def towGameObjectiveItemID(self):
        return self._towGameObjectiveItemID
