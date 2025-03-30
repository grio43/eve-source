#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\scene.py
import logging
import trinity
import geo2
from appConst import AU
from fsdBuiltData.common.graphicIDs import GetAlbedoColor
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from .base import Action
logger = logging.getLogger(__name__)

def get_scene_manager():
    return sm.GetService('sceneManager')


def get_default_scene():
    return get_scene_manager().GetRegisteredScene('default')


def get_ballpark():
    return sm.GetService('michelle').GetBallpark()


class SetLensFlare(Action):
    atom_id = 180

    def __init__(self, graphic_id = None, direction = None, **kwargs):
        super(SetLensFlare, self).__init__(**kwargs)
        self.graphic_id = graphic_id
        self.direction = self._resolve_direction(direction)
        self.lens_flare = None

    def _resolve_direction(self, direction):
        direction = self.get_atom_parameter_value('direction', direction)
        if not (hasattr(direction, '__len__') and len(direction) == 3):
            direction = self.get_atom_parameter_value('direction', None)
        return direction

    def start(self, **kwargs):
        super(SetLensFlare, self).start(**kwargs)
        self.load_lens_flare()

    def load_lens_flare(self):
        graphic_file = GetGraphicFile(int(self.graphic_id))
        self.lens_flare = trinity.Load(graphic_file)
        if self.lens_flare is None:
            return
        scene = get_default_scene()
        if scene is None:
            return
        ballpark = get_ballpark()
        position = self.get_lens_flare_position(ballpark)
        lens_flare_ball = ballpark.AddClientSideBall(position)
        scene = get_default_scene()
        self.clear_lens_flares(scene)
        self.disable_sun_model(scene)
        self.add_lens_flare_to_scene(lens_flare_ball, scene)

    def disable_sun_model(self, scene):
        model = getattr(scene.sunBall, 'model', None)
        if model:
            model.display = False

    def add_lens_flare_to_scene(self, lens_flare_ball, scene):
        self.lens_flare.translationCurve = lens_flare_ball
        scene.lensflares.append(self.lens_flare)
        scene.sunBall = lens_flare_ball
        albedo_color = GetAlbedoColor(self.graphic_id)
        if albedo_color is not None:
            sun_color = tuple(albedo_color)
            scene.sunDiffuseColor = sun_color

    def get_lens_flare_position(self, ballpark):
        player_ball = ballpark.GetBall(ballpark.ego)
        player_pos = (player_ball.x, player_ball.y, player_ball.z)
        direction_normalized = geo2.Vec3NormalizeD(self.direction)
        vector_to_lens_flare = geo2.Vec3ScaleD(direction_normalized, 1000 * AU)
        position = geo2.Vec3AddD(player_pos, vector_to_lens_flare)
        return position

    def clear_lens_flares(self, scene):
        old_flares = [ lens_flare for lens_flare in scene.lensflares ]
        for lens_flare in old_flares:
            scene.lensflares.fremove(lens_flare)

    @classmethod
    def get_subtitle(cls, graphic_id = None, **kwargs):
        return u'Graphic ID: {}'.format(graphic_id)


class SetNebula(Action):
    atom_id = 181

    def __init__(self, graphic_id = None, **kwargs):
        super(SetNebula, self).__init__(**kwargs)
        self.graphic_id = graphic_id

    def start(self, **kwargs):
        super(SetNebula, self).start(**kwargs)
        try:
            res_path = GetGraphicFile(self.graphic_id)
            get_scene_manager().ReplaceNebulaFromResPath(res_path)
        except AttributeError:
            logger.info('Tried replacing nebula, but could not access the scene')

    @classmethod
    def get_subtitle(cls, graphic_id = None, **kwargs):
        return u'Graphic ID: {}'.format(graphic_id)
