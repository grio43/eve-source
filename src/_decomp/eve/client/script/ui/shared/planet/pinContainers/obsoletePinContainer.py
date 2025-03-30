#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\obsoletePinContainer.py
from eve.client.script.ui.shared.planet.pinContainers.BasePinContainer import BasePinContainer
from eve.client.script.ui.shared.planet import planetCommon

class ObsoletePinContainer(BasePinContainer):
    panelIDs = [planetCommon.PANEL_DECOMMISSION]
