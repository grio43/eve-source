#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\rootTransformController.py
import weakref
import geo2
import trinity

class RootTransformController(object):

    def __init__(self, ball, scene):
        self._scene_ref = weakref.ref(scene)
        self.transform = trinity.EveRootTransform()
        self.transform.translationCurve = ball
        scene.uiObjects.append(self.transform)

    def __del__(self):
        scene = self._scene_ref()
        if scene is not None:
            scene.uiObjects.fremove(self.transform)

    @property
    def world_position(self):
        _, _, position = geo2.MatrixDecompose(self.transform.worldTransform)
        return position


class PanelTransformController(object):

    def __init__(self, root, camera, offset_y = 0.0):
        self.root = root
        self.camera = camera
        self.offset_y = offset_y
        self._closed = False
        self.transform = trinity.EveTransform()
        self.transform.translation = (0, self.offset_y, 0)
        self.root.transform.children.append(self.transform)

    def __del__(self):
        if not self._closed:
            self.close()

    def close(self):
        if not self._closed:
            self._closed = True
            self.root.transform.children.fremove(self.transform)
            self.root = None
