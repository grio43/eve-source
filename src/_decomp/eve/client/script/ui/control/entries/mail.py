#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\mail.py
from eve.client.script.ui.control.entries.generic import Generic

class CorpAllianceEntry(Generic):
    __guid__ = 'listentry.CorpAllianceEntry'
    isDragObject = True

    def GetDragData(self, *args):
        return [self.sr.node]
