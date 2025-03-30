#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\link_with_ship\in_space_link_ui.py
import eveui
import threadutils
import uthread2
from spacecomponents.client.ui.link_with_ship.link_ui_container import LinkUIContainer
from spacecomponents.client.ui.link_with_ship.state.ready import Ready
from analysisbeacon.client.state import StateMachine
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.uicore import uicore
from dynamicresources.client.ess.bracket.camera import InFlightCameraReference
from spacecomponents.common.components.linkWithShip import LINKSTATE_COMPLETED
from spacecomponents.client.ui.rootTransformController import RootTransformController

class InSpaceLinkUI:

    def __init__(self, item_id, initiate_link_function, space_component, type_id, owner_id):
        self.space_component = space_component
        self._item_id = item_id
        self._type_id = type_id
        self._owner_id = owner_id
        self._closed = False
        self._status_update_token = None
        self._michelle = ServiceManager.Instance().GetService('michelle')
        self._scene_manager = ServiceManager.Instance().GetService('sceneManager')
        self._camera = InFlightCameraReference(self._scene_manager)
        self._state_machine = StateMachine()
        self._ui = None
        self._camera_facing_ui = None
        self.initiate_link_function = initiate_link_function
        self._init()

    @threadutils.threaded
    def _init(self):
        ball = self._wait_for_ball()
        scene = self._scene_manager.GetRegisteredScene('default', allowBlocking=True)
        self._root = RootTransformController(ball=ball, scene=scene)
        self._camera_facing_ui = LinkUIContainer(parent=uicore.layer.space_ui, ball=ball, camera=self._camera, scene=scene, transform=self._root)
        if self.space_component.GetLinkState() is not None:
            self.initial_ui_setup(self.space_component.GetLinkState())

    def initial_ui_setup(self, state):
        if state != LINKSTATE_COMPLETED:
            uthread2.start_tasklet(self._state_machine.move_to, Ready(self._camera_facing_ui, self._item_id, self.initiate_link_function, self.space_component.attributes.characterEnergyCost, self.space_component.attributes.linkDuration, state, self._type_id, self._owner_id))

    def set_link_state(self, link_state):
        if self._state_machine.state:
            if link_state != LINKSTATE_COMPLETED:
                uthread2.start_tasklet(self._state_machine.state.enable)
            else:
                uthread2.start_tasklet(self._state_machine.state.exit)

    def set_can_link(self, tooltip, busy):
        if self._state_machine.state:
            uthread2.start_tasklet(self._state_machine.state.updateLinkButton, tooltip, busy)

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

    def remove_from_space(self):
        self._closed = True

        def clean_up():
            if self._state_machine.state:
                self._state_machine.state.exit()
            eveui.wait_for_next_frame()
            self._camera_facing_ui.remove_from_space()

        uthread2.start_tasklet(clean_up)
