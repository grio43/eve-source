#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\baseBracket.py
import threadutils
from dynamicresources.client.ess.bracket.camera import InFlightCameraReference
import eveui
from dynamicresources.client.ess.bracket.state_machine import StateMachine
from carbonui.uicore import uicore
from carbon.common.script.sys.serviceManager import ServiceManager
from spacecomponents.client.ui.rootTransformController import RootTransformController

class BaseBracket(object):

    def __init__(self, item_id, type_id):
        self._item_id = item_id
        self._type_id = type_id
        self._closed = False
        self._root = None
        self._camera = None
        self._michelle = ServiceManager.Instance().GetService('michelle')
        self._scene_manager = ServiceManager.Instance().GetService('sceneManager')
        self._state_machine = StateMachine()

    @property
    def item_id(self):
        return self._item_id

    @property
    def type_id(self):
        return self._type_id

    @property
    def root(self):
        return self._root

    @property
    def camera(self):
        return self._camera

    @property
    def layer(self):
        return uicore.layer.space_ui

    @threadutils.threaded
    def _init(self):
        ball = self._wait_for_ball()
        scene = self._scene_manager.GetRegisteredScene('default')
        self._root = RootTransformController(ball=ball, scene=scene)
        self._camera = InFlightCameraReference(self._scene_manager)
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

    def close(self):
        self._state_machine.close()
        ServiceManager.Instance().UnregisterNotify(self)
        self._closed = True
