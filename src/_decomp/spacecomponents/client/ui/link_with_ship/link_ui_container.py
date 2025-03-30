#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\link_with_ship\link_ui_container.py
import math
import weakref
import trinity
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from carbonui.primitives.container import Container
from dynamicresources.client.ess.bracket.panel import BracketPanel, get_absolute_bounds
from spacecomponents.client.ui.rootTransformController import PanelTransformController

class LinkUIContainer(BracketPanel):

    def __init__(self, parent, ball, camera, scene, transform):
        self._transform = transform
        self._scene_ref = weakref.ref(scene)
        self.run_camera_update_loop = True
        self._camera = camera
        self.is_showing = True
        self._linking_transform = PanelTransformController(root=self._transform, camera=camera)
        super(LinkUIContainer, self).__init__(name='beacon_camera_facing_ui_cont', transform=self._linking_transform.transform, layer=parent, camera=camera, collapse_at_camera_distance=100000.0, clipping_dead_zone=50, collapsed=True)
        self._ui = Transform(name='link_button_thether_ui_base', width=100, height=30, alignMode=uiconst.CENTERBOTTOM)
        self.button_cont = ContainerAutoSize(name='link_button_content_base', align=uiconst.TOPLEFT, alignMode=uiconst.TOPLEFT, width=100, height=30, state=uiconst.UI_PICKCHILDREN, left=-20 if self.is_collapsed else 0, opacity=0.0 if self.is_collapsed else 1.0)
        self.tracker.add(self.button_cont, offset=(111, 8), anchor=(0.0, 0.0))
        self.tracker.add(self._ui, offset=(-9, 8), anchor=(0.0, 0.0))

    def remove_from_space(self):
        self.run_camera_update_loop = False
        scene = self._scene_ref()
        self.tracker.remove(self._ui)
        self.tracker.remove(self.button_cont)
        if scene is not None:
            scene.uiObjects.fremove(self._transform)

    @property
    def content_bounds(self):
        return get_absolute_bounds(self._ui)

    def expand(self):
        pass

    def collapse(self, lock = False):
        pass
