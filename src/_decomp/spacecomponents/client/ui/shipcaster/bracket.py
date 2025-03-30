#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\shipcaster\bracket.py
import threadutils
from spacecomponents.client.ui.baseBracket import BaseBracket
from spacecomponents.client.ui.rootTransformController import RootTransformController
from spacecomponents.client.ui.shipcaster.shipcasterStates import Online
from carbon.common.script.sys.serviceManager import ServiceManager
from dynamicresources.client.ess.bracket.camera import InFlightCameraReference
from dynamicresources.client.ess.bracket.state_machine import State

class ShipcasterBracket(BaseBracket):
    __notifyevents__ = ('OnWarpActive', 'OnClientEvent_WarpFinished')

    def __init__(self, item_id, type_id):
        super(ShipcasterBracket, self).__init__(item_id, type_id)
        self._init()

    @threadutils.threaded
    def _init(self):
        ball = self._wait_for_ball()
        scene = self._scene_manager.GetRegisteredScene('default')
        self._root = RootTransformController(ball=ball, scene=scene)
        self._camera = InFlightCameraReference(self._scene_manager)
        self._on_shipcaster_status_changed()
        ServiceManager.Instance().RegisterNotify(self)

    def _on_shipcaster_status_changed(self, *_args):
        if self._closed:
            return
        if self._michelle.InWarp():
            self._state_machine.move_to(Hidden())
        else:
            self._state_machine.move_to(Online(self))

    def OnWarpActive(self, _warp_to_item_id, _warp_to_type_id):
        self._on_shipcaster_status_changed()

    def OnClientEvent_WarpFinished(self, _warp_to_item_id, _warp_to_type_id):
        self._on_shipcaster_status_changed()


class Hidden(State):
    pass
