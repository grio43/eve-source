#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\skybox.py
import logging
import uthread2
import trinity
from carbonui.uicore import uicore
from carbonui.primitives.fill import Fill
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from spacecomponents.common.components.component import Component
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
logger = logging.getLogger(__name__)

class Skybox(Component):

    def __init__(self, item_id, type_id, attributes, component_registry):
        Component.__init__(self, item_id, type_id, attributes, component_registry)
        self.graphicID = attributes.graphicID
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self._on_added_to_space)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self._on_removed_from_space)
        logger.debug('adding Skybox component to item=%s of type=%s', item_id, type_id)

    def _on_added_to_space(self, slimItem):
        uthread2.start_tasklet(self.TransitionFadeToNebula)

    def _on_removed_from_space(self):
        scene_manager = sm.GetService('sceneManager')
        scene = scene_manager.GetActiveScene()
        new_scene = trinity.Load(GetGraphicFile(self.graphicID))
        if scene.envMapResPath == new_scene.envMapResPath:
            uthread2.start_tasklet(self.TransitionFadeToScene, scene_manager)

    def TransitionFadeToNebula(self):
        fader = Fill(parent=uicore.layer.inflight)
        fader.SetRGBA(0, 0, 0, 0)
        uicore.animations.FadeIn(fader, sleep=True)
        scene_manager = sm.GetService('sceneManager')
        res_path = GetGraphicFile(self.graphicID)
        try:
            scene_manager.ReplaceNebulaFromResPath(res_path)
        except AttributeError:
            logger.info('Tried replacing nebula, but could not access the scene')
        finally:
            uicore.animations.FadeOut(fader, sleep=True)

    def TransitionFadeToScene(self, scene_manager):
        fader = Fill(parent=uicore.layer.inflight)
        fader.SetRGBA(0, 0, 0, 0)
        uicore.animations.FadeIn(fader, sleep=True)
        resPath = scene_manager.GetScene()
        try:
            scene_manager.ReplaceNebulaFromResPath(resPath)
        except AttributeError:
            logger.info('Tried replacing nebula, but could not access the scene')
        finally:
            uicore.animations.FadeOut(fader, sleep=True)
