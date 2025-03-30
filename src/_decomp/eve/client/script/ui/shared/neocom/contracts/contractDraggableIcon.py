#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\contractDraggableIcon.py
from carbonui.primitives.container import Container
from utillib import KeyVal

class ContractDraggableIcon(Container):
    __guid__ = 'xtriui.ContractDraggableIcon'
    isDragObject = True

    def Startup(self, contract, contractTitle):
        self.contract = contract
        self.contractTitle = contractTitle

    def GetDragData(self, *args):
        entry = KeyVal()
        entry.solarSystemID = self.contract.startSolarSystemID
        entry.contractID = self.contract.contractID
        entry.name = self.contractTitle
        entry.__guid__ = 'listentry.ContractEntry'
        return [entry]
