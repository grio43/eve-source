#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\root\__init__.py
import eveui
import threadutils
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.uicore import uicore
from dynamicresources.client.ess.bracket.camera import InFlightCameraReference
from dynamicresources.client.ess.bracket.root.online import Online
from dynamicresources.client.ess.bracket.root.status import Offline
from dynamicresources.client.ess.bracket.state_machine import State, StateMachine
from dynamicresources.client.ess.bracket.transform import EssRootTransformController
from dynamicresources.client.ess.state import EssStatus
from dynamicresources.client.service import get_dynamic_resource_service

class EssBracket(object):
    __notifyevents__ = ('OnWarpActive', 'OnClientEvent_WarpFinished')

    def __init__(self, item_id):
        self._item_id = item_id
        self._closed = False
        self._ess_root = None
        self._camera = None
        self._status_update_token = None
        self._michelle = ServiceManager.Instance().GetService('michelle')
        self._scene_manager = ServiceManager.Instance().GetService('sceneManager')
        self._dynamic_resource_service = get_dynamic_resource_service()
        self._state_machine = StateMachine()
        self._init()

    @property
    def item_id(self):
        return self._item_id

    @property
    def ess_root(self):
        return self._ess_root

    @property
    def camera(self):
        return self._camera

    @property
    def ess_state_provider(self):
        return self._dynamic_resource_service.ess_state_provider

    @property
    def layer(self):
        return uicore.layer.space_ui

    @threadutils.threaded
    def _init(self):
        ball = self._wait_for_ball()
        scene = self._scene_manager.GetRegisteredScene('default')
        self._ess_root = EssRootTransformController(ess_ball=ball, scene=scene)
        self._camera = InFlightCameraReference(self._scene_manager)
        self._on_ess_status_changed()
        ServiceManager.Instance().RegisterNotify(self)

    def _wait_for_ball(self):
        ball = None
        while ball is None:
            if self._closed:
                return
            ball = self._michelle.GetBall(self._item_id)
            if ball is not None:
                break
            eveui.wait_for_next_frame()

        return ball

    def _on_ess_status_changed(self, *_args):
        if self._closed:
            return
        (status, in_range), self._status_update_token = self.ess_state_provider.select(self._on_ess_status_changed, lens=lambda state: (state.status, state.in_range))
        if status == EssStatus.loading or self._michelle.InWarp():
            self._state_machine.move_to(Hidden())
        elif status == EssStatus.offline:
            self._state_machine.move_to(Offline(self))
        elif status == EssStatus.online:
            self._state_machine.move_to(Online(self))

    def close(self):
        if self._status_update_token:
            self._status_update_token.unsubscribe()
        self._state_machine.close()
        ServiceManager.Instance().UnregisterNotify(self)
        self._closed = True

    def OnWarpActive(self, _warp_to_item_id, _warp_to_type_id):
        self._on_ess_status_changed()

    def OnClientEvent_WarpFinished(self, _warp_to_item_id, _warp_to_type_id):
        self._on_ess_status_changed()


class Hidden(State):
    pass


from dynamicresources.client.ess.bracket.debug import __reload_update__
