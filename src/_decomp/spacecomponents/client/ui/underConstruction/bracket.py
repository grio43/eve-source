#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\underConstruction\bracket.py
from carbon.common.script.sys.serviceManager import ServiceManager
import threadutils
from spacecomponents.client.ui.baseBracket import BaseBracket
from dynamicresources.client.ess.bracket.state_machine import State
from spacecomponents.client.ui.underConstruction.underConstructionStates import Online

class UnderContructionBracket(BaseBracket):
    __notifyevents__ = ('OnLoadScene', 'OnWarpActive', 'OnClientEvent_WarpFinished')

    def __init__(self, item_id, type_id):
        super(UnderContructionBracket, self).__init__(item_id, type_id)
        self._init()

    @threadutils.threaded
    def _init(self):
        super(UnderContructionBracket, self)._init()
        ServiceManager.Instance().RegisterNotify(self)
        self._on_status_changed()

    def OnLoadScene(self, scene, key):
        self._on_status_changed()

    def OnWarpActive(self, _warp_to_item_id, _warp_to_type_id):
        self._on_status_changed()

    def OnClientEvent_WarpFinished(self, _warp_to_item_id, _warp_to_type_id):
        self._on_status_changed()

    def _on_status_changed(self, *_args):
        if self._closed:
            return
        if self._michelle.InWarp() or not self._michelle.GetBallpark():
            self._state_machine.move_to(Hidden())
        else:
            self._state_machine.move_to(Online(self))


class Hidden(State):
    pass
