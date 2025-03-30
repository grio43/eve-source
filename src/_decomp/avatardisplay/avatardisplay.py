#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\avatardisplay\avatardisplay.py
from __future__ import absolute_import
import logging
import math
import os
import sys
import time
from brennivin.itertoolsext import first, first_or_default
from eve.common.lib import appConst as const
from eve.common.script.paperDoll.paperDollDefinitions import LOD_SKIN
from eve.common.script.paperDoll.yamlPreloader import LoadYamlFileNicely
from eveexceptions import UserError
from mathext import clamp
from eve.client.script.ui.login.charcreation.ccUtil import GenderIDToPaperDollGender
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation, SceneContainer
from eve.client.script.ui.shared.preview import MergeBoundingBoxes
import charactercreator.const as ccConst
import evegraphics.settings as gfxsettings
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
import carbonui.const as uiconst
from carbonui.uicore import uicore
from charactercreator.client.grading import GetTexLUT, GetLUTIntensity
import blue
import evetypes
import trinity
import uthread
import geo2
import log
from avatardisplay import cmd_avatarwindow
import avatardisplay.avatar_command as ac
from avatardisplay.errors import FailedToPlaybackScene
from fsdBuiltData.common.character import GetAvatarBehaviorRows
AvatarDisplay_Next_CharID = None
Prs_To_CharID_Dict = {}
cache = {}
preparing_scene = False
logger = logging.getLogger()
ARCHETYPES_TO_BLOODLINES = {'aashape': const.bloodlineAmarr,
 'akshape': const.bloodlineKhanid,
 'anshape': const.bloodlineNiKunni,
 'cashape': const.bloodlineAchura,
 'ccshape': const.bloodlineCivire,
 'cdshape': const.bloodlineDeteis,
 'drshape': const.bloodlineDrifter,
 'ggshape': const.bloodlineGallente,
 'gishape': const.bloodlineIntaki,
 'gjmshape': const.bloodlineJinMei,
 'mbshape': const.bloodlineBrutor,
 'msshape': const.bloodlineSebiestor,
 'mvshape': const.bloodlineVherokior}

def PreloadScene(scene_dir, curve_list_yaml = '', per_scene_caching = False):
    uthread.new(AvatarDisplay.PreloadScene, scene_dir, curve_list_yaml=curve_list_yaml, per_scene_caching=per_scene_caching)


def PlaybackScene(scene_dir, parent, anim_strs = None, audio_strs = None, hide = False, per_scene_caching = False, sound_start_time = 0):
    logger.info('avatardisplay:  Scene playback requested: %s', scene_dir)
    AvatarDisplay.PlaybackScene(scene_dir, parent, anim_strs, audio_strs, hide=hide, per_scene_caching=per_scene_caching, sound_start_time=sound_start_time)


def PlaybackCharacterScene(male_scene_dir, female_scene_dir, parent, char_id, anim_strs = None, audio_strs = None, hide = False, per_scene_caching = False, sound_start_time = 0):
    AvatarDisplay.PlaybackCharacterScene(male_scene_dir, female_scene_dir, parent, char_id, anim_strs=anim_strs, audio_strs=audio_strs, hide=hide, per_scene_caching=per_scene_caching, sound_start_time=sound_start_time)


def PlaybackCharacter(charID_str, parent, dna_str = None, anim_str = None, audio_str = None):
    AvatarDisplay.PlaybackCharacter(charID_str, parent, dna_str, anim_str, audio_str)


GSTATE_CACHE = {}
CACHE_GSF = 0
CACHE_READY = 1
CURVE_CACHE = {}
CHARS_LOADING = []

class AvatarDisplay(object):

    @staticmethod
    def ClearAvatarDisplayGlobals():
        global CHARS_LOADING
        global AvatarDisplay_Next_CharID
        global cache
        global Prs_To_CharID_Dict
        global CURVE_CACHE
        global GSTATE_CACHE
        logger.info('avatardisplay: CLEAR AVATARDISPLAY GLOBALS')
        logger.info('avatardisplay: GLOBALS: %s %s %s %s %s %s' % (str(GSTATE_CACHE),
         str(CURVE_CACHE),
         str(CHARS_LOADING),
         str(Prs_To_CharID_Dict),
         str(cache),
         str(AvatarDisplay_Next_CharID)))
        characterSvc = sm.GetService('character')
        GSTATE_CACHE = {}
        CURVE_CACHE = {}
        CHARS_LOADING = []
        Prs_To_CharID_Dict = {}
        for currkey in cache:
            if type(currkey) is int:
                logger.info('avatardisplay: removing character %s' % currkey)
                characterSvc.RemoveCharacter(currkey)

        cache = {}
        AvatarDisplay_Next_CharID = None
        logger.info('avatardisplay: GLOBALS: %s %s %s %s %s %s' % (str(GSTATE_CACHE),
         str(CURVE_CACHE),
         str(CHARS_LOADING),
         str(Prs_To_CharID_Dict),
         str(cache),
         str(AvatarDisplay_Next_CharID)))

    @staticmethod
    def DisplayCharacter(charID_str, dna_str = None, anim_str = None, audio_str = None):
        import time
        wnd = cmd_avatarwindow.MyWindow.Open(windowID='AvatarWindow %d' % time.time())
        AvatarDisplay.PlaybackCharacter(charID_str, wnd.sr.sceneContainer, dna_str, anim_str, audio_str)
        return 'Ok'

    @staticmethod
    def PlaybackCharacter(charID_str, parent, dna_str = None, anim_str = None, audio_str = None):
        avatarcontainer = AvatarPreviewContainer(parent=parent)
        characterSvc = sm.GetService('character')
        charID = AvatarDisplay.FindTempCharID(charID_str)
        if dna_str is None:
            dna = sm.RemoteSvc('paperDollServer').GetPaperDollData(charID)
        else:
            dna = characterSvc.factory.GetDNAFromYamlFile(blue.paths.ResolvePath(dna_str))
        if dna is None:
            raise UserError('CharacterHasNoDNA', {'charID': charID})
        uthread.new(avatarcontainer.PreviewCharacter, charID, dna=dna)
        avatarcontainer.sceneContainer.OrbitParent(0, -60)
        av = None
        while av is None:
            blue.synchro.Yield()
            av = characterSvc.GetSingleCharactersAvatar(charID)

        av.display = False
        doll = None
        while doll is None:
            blue.synchro.Yield()
            doll = characterSvc.GetSingleCharactersDoll(charID)

        while doll.IsBusyUpdating():
            blue.synchro.Yield()

        if anim_str is not None and '.gsf' in anim_str:
            AvatarDisplay.PlaybackSingleAvatarGState(anim_str, audio_str, av)
        elif anim_str is not None and '.gr2' in anim_str:
            AvatarDisplay.PlaybackSingleAvatarGr2(anim_str, audio_str, av)
        else:
            AvatarDisplay.PlaybackSingleAvatarDefaultIdle(audio_str, av)

    @staticmethod
    def PlaybackSingleAvatarDefaultIdle(audio_str, av):
        if 'female' in av.visualModel.geometryResPath.lower():
            gender_name = 'Female'
        else:
            gender_name = 'Male'
        anim_str = 'res:\\Animation\\CharacterCreatorV2\\GState\\CharacterCreator_Gstate_%s_Master.gsf' % gender_name
        AvatarDisplay.PlaybackSingleAvatarGState(anim_str, audio_str, av)

    @staticmethod
    def PlaybackSingleAvatarGr2(anim_str, audio_str, av):
        animation = trinity.Tr2GrannyAnimation()
        animation.resPath = anim_str
        trinity.WaitForResourceLoads()
        baseclip = animation.grannyRes.GetAnimationName(0)
        animation.PlayAnimationEx(baseclip, 0, 0, 1.0)
        if audio_str is not None:
            sm.GetService('audio').SendUIEvent(audio_str)
        av.animationUpdater = animation
        av.display = True

    @staticmethod
    def PlaybackSingleAvatarGState(anim_str, audio_str, av):
        animation = trinity.Tr2GStateAnimation()
        animation.gStateResPath = anim_str
        log.LogNotice('Resetting gStateResPath')
        trinity.WaitForResourceLoads()
        while not animation.IsFullyLoaded():
            blue.synchro.Yield()

        animation.InstantiateCharacter()
        if audio_str is not None:
            sm.GetService('audio').SendUIEvent(audio_str)
        av.animationUpdater = animation
        av.display = True

    @staticmethod
    def FindTempCharID(charID_str):
        global AvatarDisplay_Next_CharID
        charID = 0
        if int(charID_str) == 0:
            if AvatarDisplay_Next_CharID:
                charID = AvatarDisplay_Next_CharID
                AvatarDisplay_Next_CharID += 1
            else:
                charID = 0
                AvatarDisplay_Next_CharID = 1
        return charID

    @staticmethod
    def DisplayPreparedScene(scene_dir, anim_strs = None, audio_strs = None, sound_start_time = 0, sub_char = None):
        wnd = cmd_avatarwindow.MyWindow.Open(windowID='AvatarWindow %d' % time.time())
        wnd.height = 400
        wnd.width = 300
        if sub_char is None:
            PlaybackScene(scene_dir, wnd.sr.sceneContainer, anim_strs, audio_strs, sound_start_time=sound_start_time)
        else:
            PlaybackCharacterScene(scene_dir, scene_dir, wnd.sr.sceneContainer, sub_char)
        return 'Ok'

    @staticmethod
    def PreloadScene(scene_dirs, curve_list_yaml = '', per_scene_caching = False):
        if type(scene_dirs) == str:
            scene_dirs = [scene_dirs]
        dolls = []
        for scene_dir in scene_dirs:
            scene = trinity.Tr2InteriorScene()
            cache[scene_dir] = scene
            anim_strs, audio_strs, background, camera_dict, dna_list, lights, position_list, post, char_ids, saved_curveset_lists, saved_audio_delays = AvatarDisplay.ReadSceneData(scene_dir)
            charSvc = sm.GetService('character')
            if dna_list is not None:
                bloodlineID_list = GetBloodlineIDListFromDNAList(dna_list)
                gender_list = []
                for dna in dna_list:
                    if dna[0] == 'male':
                        gender_list.append(1)
                    else:
                        gender_list.append(0)

                for idx, dna in enumerate(dna_list):
                    if char_ids[idx] in cache or char_ids[idx] in CHARS_LOADING:
                        continue
                    CHARS_LOADING.append(char_ids[idx])
                    try:
                        character = charSvc.AddCharacterToScene(charID=char_ids[idx], scene=scene, gender=GenderIDToPaperDollGender(gender_list[idx]), bloodlineID=bloodlineID_list[idx], dna=dna, lod=LOD_SKIN, updateDoll=False, anim=False)
                        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
                        textureResolution = ccConst.DOLL_VIEWER_TEXTURE_RESOLUTIONS[textureQuality]
                        useFastShader = IsUsingLowQualityCharacters()
                        character.doll.textureResolution = textureResolution
                        character.doll.useFastShader = useFastShader
                        character.Update()
                        character.WaitForUpdate()
                        dolls.append(character.doll)
                        cache[char_ids[idx]] = character
                    except Exception as e:
                        raise e
                    finally:
                        if char_ids[idx] in CHARS_LOADING:
                            CHARS_LOADING.remove(char_ids[idx])

                for idx, anim_str in enumerate(anim_strs):
                    if anim_str is not None and anim_str != 'no_anim':
                        if '.gsf' in anim_str:
                            gender_name = GenderIDToPaperDollGender(gender_list[idx])
                            if per_scene_caching:
                                cacheKey = (anim_str, gender_name.lower(), scene)
                            else:
                                cacheKey = (anim_str, gender_name.lower())
                            if cacheKey not in GSTATE_CACHE:
                                logger.info('avatardisplay: GSTATE_CACHE PRELOAD START %s' % str(GSTATE_CACHE))
                                GSTATE_CACHE[cacheKey] = [trinity.Tr2GStateAnimation(), False]
                                logger.info('avatardisplay: GSTATE_CACHE %s' % str(GSTATE_CACHE))
                                GSTATE_CACHE[cacheKey][CACHE_GSF].gStateResPath = str(anim_str)
                                while not GSTATE_CACHE[cacheKey][CACHE_GSF].IsFullyLoaded():
                                    blue.synchro.Yield()

                                GSTATE_CACHE[cacheKey][CACHE_GSF].InstantiateCharacter()
                                GSTATE_CACHE[cacheKey][CACHE_READY] = True
                                logger.info('avatardisplay: GSTATE_CACHE PRELOAD END %s' % str(GSTATE_CACHE))
                        elif '.gr2' in anim_str:
                            animation = trinity.Tr2GrannyAnimation()
                            animation.resPath = str(anim_str)
                    else:
                        gsf_anim = True
                        animation = trinity.Tr2GStateAnimation()
                        animation.gStateResPath = 'res:\\Animation\\CharacterCreatorV2\\GState\\CharacterCreator_Gstate_%s_Master.gsf' % dna_list[idx][0]
                        log.LogNotice('Resetting gStateResPath')
                        while not animation.IsFullyLoaded():
                            blue.synchro.Yield()

                        animation.InstantiateCharacter()

        if curve_list_yaml:
            curve_path_list = LoadYamlFileNicely(curve_list_yaml)
            for curve_path in curve_path_list:
                curve_res = trinity.Load(curve_path)
                if curve_path not in CURVE_CACHE:
                    CURVE_CACHE[curve_path] = curve_res

        while any(map(lambda doll: doll.IsBusyUpdating(), dolls)):
            blue.synchro.Yield()

        trinity.WaitForResourceLoads()
        blue.synchro.Sleep(100)
        trinity.WaitForResourceLoads()

    @staticmethod
    def PlaybackCharacterScene(male_scene_dir, female_scene_dir, parent, char_id, anim_strs = None, audio_strs = None, hide = False, per_scene_caching = False, sound_start_time = 0):
        dna = sm.RemoteSvc('paperDollServer').GetPaperDollData(char_id)
        dna_list = [dna]
        owner = cfg.eveowners.Get(char_id)
        gender = getattr(owner, 'gender', None)
        if gender is None:
            raise RuntimeError('{0.name} ({0.charID}) does not have a defined gender'.format(owner))
        if gender:
            scene_dir = male_scene_dir
        else:
            scene_dir = female_scene_dir
        AvatarDisplay.PlaybackScene(scene_dir, parent, anim_strs=anim_strs, audio_strs=audio_strs, hide=hide, per_scene_caching=per_scene_caching, sound_start_time=sound_start_time, dna_list=dna_list, gender_list=[gender], sub_char_id=char_id)

    @staticmethod
    def PlaybackScene(scene_dir, parent, anim_strs = None, audio_strs = None, hide = False, per_scene_caching = False, sound_start_time = 0, dna_list = None, gender_list = None, sub_char_id = None):
        parent.avatarscenecontainer = AvatarCommandReceiverContainer(parent=parent, name='avatarscenecontainer')
        anim_strs, audio_strs, background, camera_dict, scene_dna_list, lights, position_list, post, char_ids, saved_curveset_lists, saved_audio_delays = AvatarDisplay.ReadSceneData(scene_dir, anim_strs, audio_strs, sub_char_id=sub_char_id)
        if dna_list is None:
            dna_list = scene_dna_list
        uthread.new(parent.avatarscenecontainer.PreviewPreparedScene, char_ids=char_ids, dna_list=dna_list, position_list=position_list, lights=lights, camera=camera_dict, post=post, background=background, anim_strs=anim_strs, audio_strs=audio_strs, hide=hide, curveset_lists=saved_curveset_lists, audio_delays=saved_audio_delays, per_scene_caching=per_scene_caching, scene_dir=scene_dir, sound_start_time=sound_start_time, gender_list=gender_list, sub_char_id=sub_char_id)

    @staticmethod
    def ReadSceneData(scene_dir, anim_strs = None, audio_strs = None, sub_char_id = None):
        scene_dict = AvatarDisplay.ReadSceneYamlFile(scene_dir, 'scene.yaml')
        bg_dict = AvatarDisplay.ReadSceneYamlFile(scene_dir, 'background.yaml')
        camera_dict = AvatarDisplay.ReadSceneYamlFile(scene_dir, 'camera.yaml')
        background = bg_dict['path']
        width = 1000
        height = width / camera_dict['aspect_ratio']
        character_list = scene_dict['characters']
        dna_list, position_list, saved_anim_strs, saved_audio_strs, char_ids, saved_curveset_lists, saved_audio_delays = AvatarDisplay.ReadSceneCharacterData(character_list, scene_dir, sub_char_id=sub_char_id)
        if not anim_strs:
            anim_strs = saved_anim_strs
        if not audio_strs:
            audio_strs = saved_audio_strs
        lights = AvatarDisplay.ReadSceneLightsData(scene_dir)
        post = AvatarDisplay.ReadScenePostData(scene_dir)
        logger.info('avatardisplay: ReadSceneData complete %s', scene_dir)
        return (anim_strs,
         audio_strs,
         background,
         camera_dict,
         dna_list,
         lights,
         position_list,
         post,
         char_ids,
         saved_curveset_lists,
         saved_audio_delays)

    @staticmethod
    def ReadScenePostData(scene_dir):
        post = None
        post_path = os.path.join(scene_dir, 'post.yaml')
        resolved_post_path = blue.paths.ResolvePath(post_path)
        if resolved_post_path:
            post = LoadYamlFileNicely(post_path)
        return post

    @staticmethod
    def ReadSceneLightsData(scene_dir):
        lights = None
        lights_path = os.path.join(scene_dir, 'lights_client.red')
        resolved_lights_path = blue.paths.ResolvePath(lights_path)
        if resolved_lights_path:
            lights = trinity.Load(lights_path)
        return lights

    @staticmethod
    def ReadSceneCharacterData(character_list, scene_dir, sub_char_id = None):
        dna_list = []
        position_list = []
        saved_anim_strs = []
        saved_curveset_lists = []
        saved_audio_strs = []
        saved_audio_delays = []
        char_ids = []
        for char_idx, scene_char in enumerate(character_list):
            saved_anim_strs.append(scene_char.get('animation_path'))
            char_curveset_list = scene_char.get('curveset', [])
            for idx, curveset in enumerate(char_curveset_list):
                if 'res:' not in curveset:
                    char_curveset_list[idx] = os.path.join(scene_dir, curveset)

            saved_curveset_lists.append(char_curveset_list)
            saved_audio_strs.append(scene_char.get('animation_lipsync_audio'))
            lipsync_audio_delay = scene_char.get('animation_lipsync_audio_delay', '0.0')
            if not lipsync_audio_delay:
                lipsync_audio_delay = '0.0'
            saved_audio_delays.append(float(lipsync_audio_delay))
            if 'res:' not in scene_char['prs_path']:
                prs_path = os.path.join(scene_dir, scene_char['prs_path'])
            else:
                prs_path = scene_char['prs_path']
            if char_idx == 0 and sub_char_id is not None:
                char_ids.append(AvatarDisplay.GetCharID(sub_char_id))
            else:
                char_ids.append(AvatarDisplay.GetCharID(prs_path))
            dna_dict = LoadYamlFileNicely(prs_path)
            dna_list.append(dna_dict)
            position_path = os.path.join(scene_dir, scene_char['position_path'])
            position_dict = LoadYamlFileNicely(position_path)
            position_list.append(position_dict)

        return (dna_list,
         position_list,
         saved_anim_strs,
         saved_audio_strs,
         char_ids,
         saved_curveset_lists,
         saved_audio_delays)

    @staticmethod
    def GetSceneWindowID():
        import time
        timestr = str(int(time.time()))
        windowID = 'AvatarScene' + timestr
        return windowID

    @staticmethod
    def GetNextTempCharID():
        global AvatarDisplay_Next_CharID
        if AvatarDisplay_Next_CharID is None:
            AvatarDisplay_Next_CharID = 1
        char_id = AvatarDisplay_Next_CharID
        AvatarDisplay_Next_CharID += 1
        return char_id

    @staticmethod
    def GetCharID(prs_path):
        if type(prs_path) != str:
            prs_path = str(prs_path)
        prs_file = os.path.basename(prs_path)
        char_id = Prs_To_CharID_Dict.get(prs_file, None)
        if char_id is None:
            char_id = AvatarDisplay.GetNextTempCharID()
            Prs_To_CharID_Dict[prs_file] = char_id
        return char_id

    @staticmethod
    def ReadSceneYamlFile(scene_dir, filename):
        scene_path = os.path.join(scene_dir, filename)
        file_dict = LoadYamlFileNicely(scene_path)
        if not file_dict:
            raise FailedToPlaybackScene(scene_dir, file_missing=filename)
        return file_dict


class AvatarPreviewContainer(Container):
    __notifyevents__ = ['OnGraphicSettingsChanged',
     'OnSetDevice',
     'OnSettingsCloseStarted',
     'OnUIScalingChange']

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        if hasattr(self, 'sceneContainer') and self.sceneContainer.renderJob is not None:
            if hasattr(self.sceneContainer.renderJob, 'GetStep'):
                step = self.sceneContainer.renderJob.GetStep('RENDER_BLEND')
                if step is not None and hasattr(step, 'effect') and step.effect is not None:
                    for param in self.sceneContainer.renderJob.GetStep('RENDER_BLEND').effect.parameters:
                        if param.name == 'Opacity':
                            param.value = value

    @opacity.deleter
    def opacity(self):
        del self._opacity

    def FadeInOpacity(self, target_opacity = 1.0, duration = 1.0):
        self.fade_in_duration = duration
        if hasattr(self.sceneContainer.renderJob, 'enabled'):
            self.sceneContainer.renderJob.enabled = True
        animations.FadeIn(self, target_opacity, self.fade_in_duration)

    def FadeOutOpacity(self, duration = 1.0, timeOffset = 0.0):
        animations.FadeOut(self, duration, timeOffset)
        blue.synchro.SleepWallclock((duration + timeOffset) * 1000)
        if self.sceneContainer.renderJob is not None:
            self.sceneContainer.renderJob.enabled = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.context = None
        self.startLoadingCallback = attributes.get('OnStartLoading', None)
        self.stopLoadingCallback = attributes.get('OnStopLoading', None)
        self.skinController = None
        self.loading = False
        self.ConstructSceneContainer()
        self.sceneContainer.Startup()
        self._opacity = 1.0
        self.fade_in_duration = 1.0
        self.fade_out_duration = 1.0
        self.fade_out_offset = 0.0
        self.reload_thread = None
        self.scene_dir = ''

    def ConstructSceneContainer(self):
        self.sceneContainer = AvatarPreviewSceneContainer(parent=self, align=uiconst.TOALL)

    def Close(self):
        logger.info('avatardisplay: CLOSE AvatarPreviewContainer')
        self.FadeOutOpacity(self.fade_out_duration, self.fade_out_offset)
        super(AvatarPreviewContainer, self).Close()
        self._Cleanup()

    def _OnStartLoading(self):
        if self.startLoadingCallback:
            self.startLoadingCallback(self)
        else:
            self.loading = True

    def _OnStopLoading(self, success):
        if self.stopLoadingCallback:
            self.stopLoadingCallback(self, success)
        else:
            self.loading = False

    def PreviewCharacter(self, charID, dna = None, apparel = None, background = None):
        context = AvatarCharacterSceneContext(charID, dna=dna, apparel=apparel, background=background)
        return self.LoadScene(context)

    def PreviewPreparedScene(self, char_ids = [], dna_list = None, position_list = None, lights = None, camera = None, post = None, background = None, anim_strs = None, audio_strs = None, hide = False, curveset_lists = None, audio_delays = None, per_scene_caching = False, scene_dir = '', sound_start_time = 0, gender_list = None, sub_char_id = None):
        global preparing_scene
        logger.info('avatardisplay: PreviewPreparedScene started for %s' % str(scene_dir))
        while preparing_scene:
            logger.info('avatardisplay: Yielding on preparing_scene: %s' % str(preparing_scene))
            blue.synchro.Yield()

        preparing_scene = True
        try:
            logger.info('avatardisplay: Creating AvatarCharacterPreparedSceneContext for %s' % str(scene_dir))
            context = AvatarCharacterPreparedSceneContext(char_ids=char_ids, dna_list=dna_list, position_list=position_list, lights=lights, camera=camera, post=post, background=background, anim_strs=anim_strs, audio_strs=audio_strs, curveset_lists=curveset_lists, audio_delays=audio_delays, gender_list=gender_list, sub_char_id=sub_char_id)
            logger.info('avatardisplay: LoadScene started for %s' % str(scene_dir))
            scn = self.LoadScene(context, hide=hide, per_scene_caching=per_scene_caching, scene_dir=scene_dir, sound_start_time=sound_start_time)
        except Exception as e:
            raise e
        finally:
            preparing_scene = False

        return scn

    def LoadScene(self, context, force = False, hide = False, per_scene_caching = False, scene_dir = '', sound_start_time = 0):
        if context == self.context and not force:
            logger.info('avatardisplay: Multiple LoadScenes into the same context')
            return False
        if scene_dir:
            self.scene_dir = scene_dir
        success = True
        try:
            self._OnStartLoading()
            self._Cleanup()
            self.context = context
            self.context.LoadScene(self.sceneContainer, hide=hide, per_scene_caching=per_scene_caching, scene_dir=scene_dir, sound_start_time=sound_start_time)
            self.opacity = 0.0
            self.UpdateViewPort()
            logger.info('avatardisplay: Scene loading complete, ready for fade-in')
        except Exception:
            if not self.destroyed:
                log.LogException('Exception raised while loading preview for {context}'.format(context=str(context)))
                sys.exc_clear()
                success = False

        self.FadeInOpacity(target_opacity=1.0, duration=self.fade_in_duration)
        self._OnStopLoading(success)
        return success

    def Reload(self, sound_start_time = 0):
        if self.reload_thread is not None:
            logger.info('avatardisplay: Skipping reload due to reload already pending')
            return
        if uicore.layer.systemmenu.isopen or uicore.layer.charactercreation.isopen:
            logger.info('avatardisplay: Skipping reload due to system menu or character creation being open.')
            return
        if not self.context or not hasattr(self.context, 'character_list'):
            logger.info('avatardisplay: Skipping reload called before context is set up.')
            return
        self.reload_thread = uthread.new(self.Reload_t, sound_start_time=sound_start_time)

    def Reload_t(self, sound_start_time = 0):

        def _cleanup_and_return():
            logger.info('avatardisplay: context destroyed before reload thread active')
            self.reload_thread = None

        blue.synchro.Sleep(30)
        if self.context is None:
            _cleanup_and_return()
        update_list = [ character.doll.IsBusyUpdating() for character in self.context.character_list ]
        while any(update_list):
            blue.synchro.Yield()
            if self.context is None:
                _cleanup_and_return()
            update_list = [ character.doll.IsBusyUpdating() for character in self.context.character_list ]

        if self.sceneContainer.renderJob:
            if hasattr(self.sceneContainer.renderJob, 'SetStartOpacity'):
                self.sceneContainer.renderJob.SetStartOpacity(0.0)
        if self.context:
            self.context.StopAudio()
            self.display = False
            self.context.ResetCharacterLoadLocks()
            self.LoadScene(self.context, force=True, scene_dir=self.scene_dir, sound_start_time=sound_start_time)
            self.isDirty = True
            self.display = True
        self.reload_thread = None

    def _Cleanup(self):
        try:
            preparing_scene = False
            if self.context:
                self.context.StopAudio()
                self.context.Cleanup()
                self.context = None
        except Exception:
            log.LogException('Exception raised during preview container cleanup', severity=log.INFO)
            sys.exc_clear()

    def AnimEntry(self, yaw0 = 1.1 * math.pi, pitch0 = 0.0, yaw1 = 1.25 * math.pi, pitch1 = 0.3, duration = 2.0):
        self.sceneContainer.AnimEntry(yaw0, pitch0, yaw1, pitch1, duration)

    def UpdateViewPort(self):
        if uicore.layer.systemmenu.isopen:
            logger.info('avatardisplay: System menu is open and UpdateViewPort was called')
            return
        if self.sceneContainer:
            self.sceneContainer.UpdateViewPort()

    def OnSetDevice(self):
        if uicore.layer.systemmenu.isopen:
            logger.info('avatardisplay: System menu is open and SetDevice was called')
            return
        self.WaitForDollUpdates()
        logging.info('avatardisplay: Reloading in OnSetDevice')
        self.Reload()

    def WaitForDollUpdates(self):
        while self.context and any([ char.doll.getbusyUpdating() for char in self.context.character_list ]):
            blue.synchro.Yield()

    def OnGraphicSettingsChanged(self, changes):
        if uicore.layer.systemmenu.isopen:
            logger.info('avatardisplay: System menu is open and graphics settings were changed')
            return
        if self.context and any((setting in self.context.relevantSettings for setting in changes)):
            logging.info('avatardisplay: Reloading in OnGraphicsSettingsChanged')
            self.Reload()

    def OnSettingsCloseStarted(self):
        if hasattr(self.context, 'char_ids'):
            for char_id in self.context.char_ids:
                sm.GetService('character').UpdateDoll(char_id)

        self.WaitForDollUpdates()
        logging.info('avatardisplay: Reloading in OnSettingsCloseStarted')
        self.Reload()


class AvatarCommandReceiverContainer(AvatarPreviewContainer):
    AvatarPreviewContainer.__notifyevents__.append('OnAvatarCommand')

    def __init__(self, *args, **kwargs):
        super(AvatarCommandReceiverContainer, self).__init__(*args, **kwargs)
        self.COMMANDS = ['restart', 'play_scene_anim']

    def OnAvatarCommand(self, *args, **kwargs):
        self.process_command(args)

    def process_command(self, args):
        print ('got here', len(args), args[1:])
        if len(args) >= 1:
            curr_command = args[0]
            print curr_command
            if curr_command in self.COMMANDS:
                command_func = getattr(ac, 'avcmd_' + curr_command)
                uthread.new(command_func, self, *args[1:])

    def PlaySceneBehavior(self, behavior_name):
        if self.context is not None:
            self.context.PlaySceneBehavior(behavior_name)


class AvatarPreviewNavigation(SceneContainerBaseNavigation):
    default_cursor = uiconst.UICURSOR_CCALLDIRECTIONS
    default_state = uiconst.UI_NORMAL

    def UpdateCursor(self):
        if uicore.uilib.rightbtn and not uicore.uilib.leftbtn and self.sr.sceneContainer.verticalPanEnabled:
            self.cursor = uiconst.UICURSOR_CCUPDOWN
        else:
            self.cursor = uiconst.UICURSOR_CCALLDIRECTIONS

    def OnMouseDown(self, *args):
        SceneContainerBaseNavigation.OnMouseDown(self, *args)
        self.UpdateCursor()

    def OnMouseUp(self, *args):
        SceneContainerBaseNavigation.OnMouseUp(self, *args)
        self.UpdateCursor()

    def OnMouseMove(self, *args):
        if self.sr.sceneContainer.verticalPanEnabled and uicore.uilib.rightbtn:
            cameraDistance = self.sr.sceneContainer.camera.GetZoomDistance()
            delta = uicore.uilib.dy * 0.0006 * cameraDistance
            y = self.sr.sceneContainer.verticalPan
            self.sr.sceneContainer.verticalPan = y + delta
        else:
            SceneContainerBaseNavigation.OnMouseMove(self, *args)


class AvatarPreviewSceneContainer(SceneContainer):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(AvatarPreviewSceneContainer, self).ApplyAttributes(attributes)
        self._minY = None
        self._maxY = None
        self._opacity = 1.0

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.renderObject.opacity = value

    @opacity.deleter
    def opacity(self):
        del self._opacity

    @property
    def verticalPanLimits(self):
        return (self._minY, self._maxY)

    @verticalPanLimits.setter
    def verticalPanLimits(self, limits):
        if limits is None:
            limits = (None, None)
        minY, maxY = limits
        if minY > maxY:
            minY, maxY = maxY, minY
        self._minY = minY
        self._maxY = maxY

    @property
    def verticalPanEnabled(self):
        return self._minY is not None and self._maxY is not None

    @property
    def verticalPan(self):
        if self.camera:
            return self.camera.atPosition[1]

    @verticalPan.setter
    def verticalPan(self, y):
        if self.verticalPanEnabled:
            y = clamp(y, self._minY, self._maxY)
            x, _, z = self.camera.atPosition
            self.camera.SetAtPosition((x, y, z))

    def Close(self):
        logger.info('avatardisplay: CLOSING AvatarPreviewSceneContainer')
        super(AvatarPreviewSceneContainer, self).Close()


class AvatarSceneContext(object):
    relevantSettings = []

    def LoadScene(self, sceneContainer, hide = False):
        raise NotImplementedError('AvatarSceneContexts must override the LoadScene method')

    def Cleanup(self):
        pass

    def ResetCharacterLoadLocks(self):
        pass


class AvatarCharacterPreparedSceneContext(AvatarSceneContext):
    relevantSettings = [gfxsettings.GFX_CHAR_TEXTURE_QUALITY, gfxsettings.UI_NCC_GREEN_SCREEN, gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION]

    def __init__(self, char_ids, dna_list, position_list, lights, camera, post, background = None, anim_strs = None, audio_strs = None, curveset_lists = None, audio_delays = None, gender_list = None, sub_char_id = None):
        self.char_ids = char_ids
        self.dna_list = dna_list
        self.position_list = position_list
        self.background = background
        self.boundingBox_list = []
        self.character_list = []
        self.lights = lights
        self.camera = camera
        self.post = post
        self.anim_strs = anim_strs
        self.audio_strs = audio_strs
        self.curveset_lists = curveset_lists
        self.audio_delays = audio_delays
        self.audio_playing_ID = 0
        self.audio_playing_event = ''
        self.anim_start_thread = None
        self.minimized = False
        self.lutObject = None
        self.gender_list = gender_list
        self.sub_char_id = sub_char_id
        self.granny_animation_list = None
        self.scene_container = None
        self.behavior_dict = None

    def __eq__(self, other):
        return isinstance(other, AvatarCharacterPreparedSceneContext) and self.dna_list == other.dna_list and self.background == other.background and self.char_ids == other.char_ids and self.position_list == other.position_list and self.lights == other.lights and self.camera == other.camera and self.post == other.post and self.anim_strs == other.anim_strs and self.audio_strs == other.audio_strs and self.curveset_lists == other.curveset_lists and self.audio_delays == other.audio_delays and self.gender_list == other.gender_list and self.sub_char_id == other.sub_char_id

    def LoadScene(self, sceneContainer, hide = False, per_scene_caching = False, scene_dir = '', sound_start_time = 0):
        logger.info('avatardisplay: LoadScene starting %s' % scene_dir)
        if uicore.layer.systemmenu.isopen:
            logger.info('avatardisplay: System menu is open')
            return
        background = self.GetBackground()
        logger.info('avatardisplay: LoadScene bg loaded %s' % scene_dir)
        sceneContainer.PrepareInteriorScene(useShadows=True, backgroundImage=background, startOpacity=0.0)
        logger.info('avatardisplay: LoadScene interior scene prepared %s' % scene_dir)
        sceneContainer.renderJob.enabled = False
        sceneContainer.UpdateAlignment()
        logger.info('avatardisplay: LoadScene UpdateAlignment called %s' % scene_dir)
        for curveSet in sceneContainer.scene.curveSets[:]:
            sceneContainer.scene.curveSets.remove(curveSet)

        if self.lights:
            lightList = sceneContainer.scene.lights[:]
            for light in lightList:
                sceneContainer.scene.RemoveLightSource(light)

            for light in self.lights.lights:
                sceneContainer.scene.AddLightSource(light)

            if self.lights.curveSets:
                for curveSet in self.lights.curveSets:
                    sceneContainer.scene.curveSets.append(curveSet)

        logger.info('avatardisplay: LoadScene Lights added %s' % scene_dir)
        if self.camera:
            sceneContainer.camera.StopUpdateThreads()
            sceneContainer.camera.eyePosition = self.camera['position']
            sceneContainer.camera.atPosition = self.camera['point_of_interest']
            sceneContainer.camera.near_clip = self.camera.get('front_clip', 0.1)
            sceneContainer.camera.far_clip = self.camera.get('back_clip', 300)
            sceneContainer.camera.fov = self.camera.get('field_of_view', 0.3)
            aspect_ratio = self.camera.get('aspect_ratio', 1.778)
            sceneContainer.camera.UpdateViewportSize(aspect_ratio, 1.0)
        logger.info('avatardisplay: LoadScene camera set up %s' % scene_dir)
        avatar_list = []
        granny_animation_list = []
        charSvc = sm.GetService('character')
        if self.dna_list is not None:
            if self.sub_char_id is not None:
                char_id_list = [self.sub_char_id]
            else:
                char_id_list = None
            bloodlineID_list = GetBloodlineIDListFromDNAList(self.dna_list, char_id_list)
            tmp_gender_list = []
            for idx, dna in enumerate(self.dna_list):
                if type(dna) == list:
                    if dna[0] == 'male':
                        tmp_gender_list.append(1)
                    else:
                        tmp_gender_list.append(0)
                else:
                    tmp_gender_list.append(self.gender_list[idx])

            self.character_list = []
            try:
                for idx, dna in enumerate(self.dna_list):
                    while self.char_ids[idx] in CHARS_LOADING:
                        logger.info('avatardisplay: Character loading for %s, yielding' % str(scene_dir))
                        blue.synchro.Yield()

                    CHARS_LOADING.append(self.char_ids[idx])
                    logger.info('avatardisplay: About to add character to scene %s' % str(scene_dir))
                    updateDoll = False
                    if self.sub_char_id is not None:
                        updateDoll = True
                    character = charSvc.AddCharacterToScene(charID=self.char_ids[idx], scene=sceneContainer.scene, gender=GenderIDToPaperDollGender(tmp_gender_list[idx]), bloodlineID=bloodlineID_list[idx], dna=dna, lod=LOD_SKIN, updateDoll=updateDoll, anim=False)
                    if self.char_ids[idx] not in cache:
                        cache[self.char_ids[idx]] = character
                    logger.info('avatardisplay: Character added %s' % str(scene_dir))
                    self.character_list.append(character)
                    pos = self.position_list[idx]
                    av = charSvc.GetSingleCharactersAvatar(self.char_ids[idx])
                    avatar_list.append(av)
                    av.display = False
                    av.translation = pos['translation']
                    av.rotation = pos['rotation']

                for avatar in avatar_list:
                    avatar.display = True

                logger.info('avatardisplay: Characters added %s' % scene_dir)
                textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
                textureResolution = ccConst.DOLL_VIEWER_TEXTURE_RESOLUTIONS[textureQuality]
                useFastShader = IsUsingLowQualityCharacters()
                self.boundingBox_list = []
                for idx, character in enumerate(self.character_list):
                    if textureResolution != character.doll.textureResolution or useFastShader != character.doll.useFastShader:
                        logger.info('TexRes: (%d, %d)' % (character.doll.textureResolution[0], character.doll.textureResolution[1]))
                        character.doll.textureResolution = textureResolution
                        character.doll.useFastShader = useFastShader
                    try:
                        self.boundingBox_list.append(character.visualModel.GetBoundingBoxInLocalSpace())
                    except RuntimeError:
                        self.boundingBox_list.append(((-0.5, -0.5, 0), (0.5, 0.5, 1.5)))

                for character in self.character_list:
                    character.Update()
                    character.WaitForUpdate()

            except Exception as e:
                raise e
            finally:
                self.ResetCharacterLoadLocks()

        if useFastShader:
            sceneContainer.scene.ambientColor = (0.25, 0.25, 0.25)
        if not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
            sceneContainer.scene.dynamics.append(floor)
        logger.info('avatardisplay: LoadScene character quality set %s' % scene_dir)
        if self.post:
            if self.post['lut']:
                self.lutObject = blue.resMan.GetResource(self.post['lut_path'])
                while not self.lutObject.isPrepared:
                    blue.synchro.Yield()

                tex_lut_obj = GetTexLUT(sceneContainer.renderJob)
                if tex_lut_obj is not None:
                    tex_lut_obj.SetResource(self.lutObject)
                    sceneContainer.renderJob.lut_res_path = self.post['lut_path']
                influence_obj = GetLUTIntensity(sceneContainer.renderJob)
                if influence_obj is not None:
                    influence_obj.value = self.post['lut_influence']
        logger.info('avatardisplay: LoadScene Postprocess done %s' % scene_dir)
        for idx, dna in enumerate(self.dna_list):
            av = charSvc.GetSingleCharactersAvatar(self.char_ids[idx])
            if 'female' in av.visualModel.geometryResPath.lower():
                gender_name = 'Female'
            else:
                gender_name = 'Male'
            gsf_anim = False
            animation = None
            if self.anim_strs is not None and self.anim_strs[idx] is not None and self.anim_strs[idx] != 'no_anim':
                if '.gsf' in self.anim_strs[idx]:
                    gsf_anim = True
                    if per_scene_caching:
                        cacheKey = (self.anim_strs[idx], gender_name.lower(), scene_dir)
                    else:
                        cacheKey = (self.anim_strs[idx], gender_name.lower())
                    if cacheKey in GSTATE_CACHE:
                        while not GSTATE_CACHE[cacheKey][CACHE_READY]:
                            blue.synchro.Yield()

                        logger.info('avatardisplay: GSTATE_CACHE HIT %s' % str(GSTATE_CACHE))
                        animation = GSTATE_CACHE[cacheKey][CACHE_GSF]
                        animation.ResetParamsToDefault()
                    else:
                        logger.info('avatardisplay: GSTATE_CACHE MISS %s' % str(GSTATE_CACHE))
                        GSTATE_CACHE[cacheKey] = [trinity.Tr2GStateAnimation(), False]
                        GSTATE_CACHE[cacheKey][CACHE_GSF].gStateResPath = str(self.anim_strs[idx])
                        while not GSTATE_CACHE[cacheKey][CACHE_GSF].IsFullyLoaded():
                            blue.synchro.Yield()

                        GSTATE_CACHE[cacheKey][CACHE_GSF].InstantiateCharacter()
                        animation = GSTATE_CACHE[cacheKey][CACHE_GSF]
                        GSTATE_CACHE[cacheKey][CACHE_READY] = True
                elif '.gr2' in self.anim_strs[idx]:
                    animation = trinity.Tr2GrannyAnimation()
                    animation.resPath = self.anim_strs[idx]
            else:
                gsf_anim = True
                animation = trinity.Tr2GStateAnimation()
                animation.gStateResPath = 'res:\\Animation\\CharacterCreatorV2\\GState\\CharacterCreator_Gstate_%s_Master.gsf' % gender_name
                log.LogNotice('Resetting gStateResPath')
                trinity.WaitForResourceLoads()
                if gsf_anim and animation is not None:
                    while not animation.IsFullyLoaded():
                        blue.synchro.Yield()

                    animation.InstantiateCharacter()
            if animation is not None:
                av.animationUpdater = animation
            logger.info('avatardisplay: LoadScene character animation set up %s' % scene_dir)
            curveset_paths = self.curveset_lists[idx]
            if curveset_paths is not None:
                self.BindCurveList(curveset_paths, av, sceneContainer)
            logger.info('avatardisplay: LoadScene character curves bound %s' % scene_dir)
            if not gsf_anim:
                granny_animation_list.append(animation)
            else:
                granny_animation_list.append(None)

        if self.post:
            if 'transmission_noise' in self.post:
                if self.post['transmission_noise']:
                    sceneContainer.renderJob.PlaceTransmissionEffectInScene(sceneContainer.scene)
        self.granny_animation_list = granny_animation_list
        self.scene_container = sceneContainer
        self.StartAnimation(sceneContainer.scene.curveSets, granny_animation_list, sound_start_time)
        if not hide:
            sceneContainer.renderJob.enabled = True

    def BindCurveList(self, curve_list, avatar, sceneContainer):
        curvesets = []
        for curveset_path in curve_list:
            curveset_metadata_path = curveset_path[:-4] + '_metadata.yaml'
            if curveset_path:
                if curveset_path.lower() in CURVE_CACHE:
                    curveset = CURVE_CACHE[curveset_path.lower()]
                else:
                    curveset = trinity.Load(curveset_path)
                    if curveset_path.lower() not in CURVE_CACHE:
                        CURVE_CACHE[curveset_path.lower()] = curveset
                curvesets.append(curveset)
                curveset_metadata = LoadYamlFileNicely(curveset_metadata_path)
                route = curveset_metadata['parameter_path']
                sceneContainer.scene.curveSets.append(curveset)
                for binding in curveset.bindings:
                    if binding.destinationObject:
                        if route:
                            dest_param = self.GetTargetFromOwnerAndRoute(avatar, route)
                            binding.destinationObject = dest_param
                        else:
                            gsf_param = avatar.animationUpdater.parameters.FindByName(binding.destinationObject.name)
                            binding.destinationObject = gsf_param

        return curvesets

    def LoadBehaviors(self):
        behavior_rows = GetAvatarBehaviorRows()
        self.behavior_dict = {}
        for behavior in behavior_rows:
            self.behavior_dict[behavior.name, behavior.resGender] = behavior

    def PlaySceneBehavior(self, behavior_name, index = '0'):
        if self.scene_container is None:
            return
        if self.behavior_dict is None:
            self.LoadBehaviors()
        charSvc = sm.GetService('character')
        idx = int(index)
        gender = charSvc.GetSingleCharactersMetadata(self.char_ids[idx])['genderID']
        if (behavior_name, gender) in self.behavior_dict:
            log.LogInfo('avatardisplay: playing %s for gender %s' % (behavior_name, gender))
            curve_list = self.behavior_dict[behavior_name, gender].resPathList
            avatar = charSvc.GetSingleCharactersAvatar(self.char_ids[idx])
            self.PlayCurveListOnAvatar(curve_list, avatar, self.scene_container)
        else:
            log.logInfo('avatardisplay: playing nothing, requested behavior not in table %s %s' % (behavior_name, gender))

    def PlayCurveListOnAvatar(self, curve_list, avatar, sceneContainer):
        if self.granny_animation_list is not None:
            curvesets = self.BindCurveList(curve_list, avatar, sceneContainer)
            self.StartAnimation(curvesets, self.granny_animation_list, sound_start_time=0, silence_sound=True)

    def ResetCharacterLoadLocks(self):
        for charid in self.char_ids:
            if charid in CHARS_LOADING:
                CHARS_LOADING.remove(charid)

    def StartAnimation(self, curve_sets, granny_animation_list, sound_start_time = 0, silence_sound = False):
        if self.anim_start_thread:
            return
        self.anim_start_thread = uthread.new(self.StartAnimation_t, curve_sets, granny_animation_list, sound_start_time, silence_sound)

    def IsSupportedVOLanguage(self):
        return session.languageID == 'EN'

    def StartAnimation_t(self, curve_sets, granny_animation_list, sound_start_time = 0, silence_sound = False):
        logger.info('avatardisplay: animation started')
        delay_index = zip(self.audio_delays, range(len(self.audio_delays)))
        delay_index.sort(key=lambda x: x[0])
        curr_offset = 0
        play_sound = False
        curr_time = time.time()
        if not sound_start_time:
            play_sound = True and not silence_sound
            sound_start_time = curr_time
        offset = curr_time - sound_start_time
        if curve_sets:
            for curveSet in curve_sets:
                if 'lipsync' in curveSet.name:
                    if self.IsSupportedVOLanguage():
                        curveSet.PlayFrom(offset)
                    else:
                        curveSet.Stop()
                else:
                    curveSet.PlayFrom(offset)

        for idx in range(len(self.dna_list)):
            if granny_animation_list[idx] is not None:
                animation = granny_animation_list[idx]
                baseclip = animation.grannyRes.GetAnimationName(0)
                animation.PlayAnimationEx(baseclip, 1, 0, 1.0)

        if play_sound:
            for delay, idx in delay_index:
                if self.audio_strs is not None and self.audio_strs[idx] != 'no_audio':
                    self.StartAudio(str(self.audio_strs[idx]), delay - curr_offset)
                    curr_offset = delay

        self.anim_start_thread = None

    def StartAudio(self, audio_str, delay):
        if self.minimized:
            return
        if not self.IsSupportedVOLanguage():
            return
        logger.info('avatardisplay: start audio event=%s delay=%s sec', audio_str, delay)
        blue.synchro.Sleep(delay * 1000)
        self.audio_playing_event = audio_str
        self.audio_playing_ID = sm.GetService('audio').SendUIEventWithCallback(audio_str)
        logger.info('avatardisplay: audio UI event sent %s', audio_str)

    def StopAudio(self):
        self.audio_playing_event = ''
        if self.anim_start_thread:
            logger.info('avatardisplay: killing anim start thread')
            self.anim_start_thread.kill()
        if self.audio_playing_ID > 0:
            sm.GetService('audio').StopUIEvent(self.audio_playing_ID)
            logger.info('avatardisplay: stop audio request sent for %s', self.audio_playing_ID)

    def SetMinimized(self):
        self.minimized = True

    def SetMaximized(self):
        self.minimized = False

    def GetSceneAudioPlayingEvent(self):
        return self.audio_playing_event

    @staticmethod
    def GetTargetFromOwnerAndRoute(owner, route):
        import re
        steps = route.split('.')
        current = owner
        for step in steps:
            if step.lower() == 'owner':
                continue
            if hasattr(current, step):
                current = getattr(current, step)
                continue
            regex = u'(?P<name>^.+)\\[\\"(?P<key>.+)\\"\\]'
            match = re.match(regex, step)
            if match is not None and match.groups():
                name = match.group('name')
                key = match.group('key')
                if hasattr(current, name):
                    tmp = getattr(current, name)
                    if tmp.FindByName(key):
                        current = tmp.FindByName(key)

        return current

    def GetBackground(self):
        background = self.background
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            background = 'res:/UI/Texture/CharacterCreation/backdrops/Background_1001.dds'
        return background

    def SetupCamera(self, sceneContainer):
        if self.boundingBox_list:
            SetupInteriourCamera(sceneContainer, reduce(MergeBoundingBoxes, self.boundingBox_list))
        else:
            SetupInteriourCamera(sceneContainer, ((-0.5, -0.5, 0), (0.5, 0.5, 1.5)))


class AvatarCharacterSceneContext(AvatarSceneContext):
    relevantSettings = [gfxsettings.GFX_CHAR_TEXTURE_QUALITY, gfxsettings.UI_NCC_GREEN_SCREEN, gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION]

    def __init__(self, charID, dna = None, apparel = None, background = None):
        dna = dna or sm.RemoteSvc('paperDollServer').GetPaperDollData(charID)
        if dna is None:
            raise UserError('CharacterHasNoDNA', {'charID': charID})
        self.charID = charID
        self.dna = dna
        self.apparel = apparel or []
        self.background = background
        self.boundingBox = None
        self.character = None

    def __eq__(self, other):
        return isinstance(other, AvatarCharacterSceneContext) and self.charID == other.charID and self.dna == other.dna and self.apparel == other.apparel and self.background == other.background

    def LoadScene(self, sceneContainer, hide = False):
        useFastShader = False
        background = self.GetBackground()
        sceneContainer.PrepareInteriorScene(useShadows=True, backgroundImage=background)
        if self.charID > 65535:
            owner = cfg.eveowners.Get(self.charID)
            charInfo = sm.RemoteSvc('charMgr').GetPublicInfo(self.charID)
            bloodlineID = charInfo.bloodlineID
            gender = getattr(owner, 'gender', None)
            if gender is None:
                raise RuntimeError('{0.name} ({0.charID}) does not have a defined gender'.format(owner))
        else:
            bloodlineID = const.bloodlineGallente
            gender = 0
            if self.dna[0] == 'male':
                gender = 1
        charSvc = sm.GetService('character')
        char_loaded = charSvc.IsSingleCharacterLoaded(self.charID)
        character = charSvc.AddCharacterToScene(charID=self.charID, scene=sceneContainer.scene, gender=GenderIDToPaperDollGender(gender), bloodlineID=bloodlineID, dna=self.dna, lod=LOD_SKIN, updateDoll=not char_loaded, anim=False)
        self.character = character
        if not char_loaded:
            textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
            textureResolution = ccConst.DOLL_VIEWER_TEXTURE_RESOLUTIONS[textureQuality]
            character.doll.textureResolution = textureResolution
            useFastShader = IsUsingLowQualityCharacters()
            character.doll.useFastShader = useFastShader
            for typeID in self.apparel:
                apparel = GetPaperDollResource(typeID, gender=gender)
                if apparel is None:
                    log.LogError('Unable to preview %s (%s) since it has no associated resource' % (evetypes.GetName(typeID), typeID))
                    continue
                charSvc.ApplyTypeToDoll(self.charID, apparel.resPath, doUpdate=False)

            character.Update()
            character.WaitForUpdate()
        try:
            self.boundingBox = character.visualModel.GetBoundingBoxInLocalSpace()
        except RuntimeError:
            self.boundingBox = ((-0.5, -0.5, 0), (0.5, 0.5, 1.5))

        if useFastShader:
            sceneContainer.scene.ambientColor = (0.25, 0.25, 0.25)
        if not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
            sceneContainer.scene.dynamics.append(floor)
        self.SetupCamera(sceneContainer)

    def GetBackground(self):
        background = self.background
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            background = 'res:/UI/Texture/CharacterCreation/backdrops/Background_1001.dds'
        return background

    def SetupCamera(self, sceneContainer):
        SetupInteriourCamera(sceneContainer, self.boundingBox)

    def Cleanup(self):
        pass


def SetupInteriourCamera(sceneContainer, boundingBox):
    p0, p1 = geo2.Vector(boundingBox[0]), geo2.Vector(boundingBox[1])
    center = 0.5 * (p1 - p0) + p0
    camera = sceneContainer.camera
    camera.SetAtPosition(center)
    sceneContainer.verticalPanLimits = (p0.y, p1.y)
    rad = max(geo2.Vec3Length(p0 - p1), 0.3)
    alpha = sceneContainer.fov * 1.5 / 2.0
    maxZoom = min(rad * (1 / math.tan(alpha)), 9.0)
    minZoom = rad + sceneContainer.frontClip
    sceneContainer.SetMinMaxZoom(minZoom, maxZoom)
    camera.SetZoomLinear(0.6)
    camera.kMinPitch = 0.0
    camera.kMaxPitch = math.pi / 2.0
    camera.kOrbitSpeed = 30.0
    camera.farClip = 100.0


def GetPaperDollResource(typeID, gender = None):
    assets = filter(lambda a: a.typeID == typeID, cfg.paperdollResources)
    if len(assets) == 0:
        log.LogWarn('PreviewWnd::PreviewType - No asset matched the typeID {}'.format(typeID))
        return None
    default_asset = first(assets)
    unisex_asset = first_or_default(assets, lambda a: a.resGender is None, default_asset)
    return first_or_default(assets, lambda a: a.resGender == gender, unisex_asset)


def GetBloodlineFromDNA(dna, charID = None):
    if type(dna) == list:
        bloodlineArchetypeString = ''
        for modifier in dna:
            if type(modifier) is dict:
                cat = modifier.get('category', '')
                if cat == 'archetypes':
                    bloodlineArchetypeString = modifier['path'].split('/')[1]

        if bloodlineArchetypeString in ARCHETYPES_TO_BLOODLINES:
            return ARCHETYPES_TO_BLOODLINES[bloodlineArchetypeString]
        else:
            return None
    else:
        charInfo = sm.RemoteSvc('charMgr').GetPublicInfo(charID)
        return charInfo.bloodlineID


def GetBloodlineIDListFromDNAList(dna_list, char_id_list = None):
    bloodlineID_list = []
    for idx, dna in enumerate(dna_list):
        if type(char_id_list) == list:
            char_id = char_id_list[idx]
        else:
            char_id = None
        bloodline = GetBloodlineFromDNA(dna, charID=char_id)
        if bloodline is None:
            bloodline = const.bloodlineGallente
            logging.warning('avatardisplay: No valid archetype in .prs file')
        bloodlineID_list.append(bloodline)

    return bloodlineID_list


def IsUsingLowQualityCharacters():
    return gfxsettings.Get(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION)
