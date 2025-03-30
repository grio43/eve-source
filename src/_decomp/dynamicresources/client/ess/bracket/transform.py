#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\transform.py
import weakref
import codereload
import enum
import eveui
import geo2
import threadutils
import trinity

class EssRootTransformController(object):

    def __init__(self, ess_ball, scene):
        self._scene_ref = weakref.ref(scene)
        self.transform = trinity.EveRootTransform()
        self.transform.translationCurve = ess_ball
        scene.uiObjects.append(self.transform)

    def __del__(self):
        scene = self._scene_ref()
        if scene is not None:
            scene.uiObjects.fremove(self.transform)

    @property
    def world_position(self):
        _, _, position = geo2.MatrixDecompose(self.transform.worldTransform)
        return position


@codereload.reloadable_enum

class BankTransformSide(enum.IntEnum):
    left = 1
    right = 2


class BankPanelTransformController(object):

    def __init__(self, root, camera, side = None, offset_y = 0.0, radius = 0.0):
        self.root = root
        self.camera = camera
        self.offset_y = offset_y
        self.radius = radius
        self.side = BankTransformSide(side) if side is not None else None
        self._closed = False
        self.transform = trinity.EveTransform()
        self.root.transform.children.append(self.transform)
        self._start_update_loop()

    def __del__(self):
        if not self._closed:
            self.close()

    def close(self):
        if not self._closed:
            self._closed = True
            self.root.transform.children.fremove(self.transform)
            self.root = None

    @threadutils.threaded
    def _start_update_loop(self):
        while not self._closed:
            if self.side is None:
                tangent = (0, 0, 0)
            elif self.side == BankTransformSide.left:
                tangent = self.camera.left
            elif self.side == BankTransformSide.right:
                tangent = self.camera.right
            else:
                raise RuntimeError('Unknown side {!r}'.format(self.side))
            self.transform.translation = geo2.Vec3Add((0, self.offset_y, 0), geo2.Vec3Scale(tangent, self.radius))
            eveui.wait_for_next_frame()
