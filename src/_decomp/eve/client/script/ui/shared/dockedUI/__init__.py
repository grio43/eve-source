#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\__init__.py
from eve.common.script.sys.eveCfg import IsDockedInStructure

def ReloadLobbyWnd():
    from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
    LobbyWnd.CloseIfOpen()
    OpenLobbyWnd()


def OpenLobbyWnd():
    from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
    if session.stationid:
        from eve.client.script.ui.shared.dockedUI.controllers.stationController import StationController
        LobbyWnd.OpenBehindFullscreenViews(controller=StationController(itemID=session.stationid))
    elif IsDockedInStructure():
        from eve.client.script.ui.shared.dockedUI.controllers.structureController import StructureController
        LobbyWnd.OpenBehindFullscreenViews(controller=StructureController(itemID=session.structureid))
