#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\location.py
from .base import Event

class AbyssalRoomChanged(Event):
    atom_id = 624
    __notifyevents__ = ['OnAbyssalLocationEntered', 'OnAbyssalLocationExited']

    def OnAbyssalLocationEntered(self, client_data):
        self.invoke()

    def OnAbyssalLocationExited(self):
        self.invoke()


class AbyssalContentFinished(Event):
    atom_id = 629
    __notifyevents__ = ['OnAbyssalContentFinished']

    def OnAbyssalContentFinished(self, *args, **kwargs):
        self.invoke()


class DeathZoneStateUpdated(Event):
    atom_id = 634
    __notifyevents__ = ['OnDeathzoneStateUpdate']

    def OnDeathzoneStateUpdate(self, *args, **kwargs):
        self.invoke()


class InsurgencyStateChanged(Event):
    atom_id = 638
    __notifyevents__ = ['OnInsurgencyCampaignStartedForLocation_Local', 'OnInsurgencyCampaignEndingForLocation_Local']

    def OnInsurgencyCampaignStartedForLocation_Local(self, campaignSnapshot):
        self.invoke()

    def OnInsurgencyCampaignEndingForLocation_Local(self):
        self.invoke()


class CorruptionValueChanged(Event):
    atom_id = 639
    __notifyevents__ = ['OnCorruptionValueChanged_Local']

    def OnCorruptionValueChanged_Local(self, systemID, data):
        self.invoke()


class SupressionValueChanged(Event):
    atom_id = 640
    __notifyevents__ = ['OnSuppressionValueChanged_Local']

    def OnSuppressionValueChanged_Local(self, systemID, data):
        self.invoke()
