#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\storageIcon.py
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.shared.planet import planetCommon

class StorageIcon(Icon):

    def ApplyAttributes(self, attributes):
        Icon.ApplyAttributes(self, attributes)
        self.amount = attributes.amount

    def LoadTooltipPanel(self, tooltipPanel, *args):
        planetCommon.LoadProductTooltipPanel(tooltipPanel, self.typeID, self.amount)

    def GetMenu(self, *args):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)

    def OnDblClick(self):
        sm.GetService('info').ShowInfo(self.typeID)
