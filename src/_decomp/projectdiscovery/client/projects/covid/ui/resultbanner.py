#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\resultbanner.py
from carbon.common.script.sys.serviceManager import ServiceManager
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from carbonui.fontconst import STYLE_SMALLTEXT
from localization import GetByLabel
from projectdiscovery.client.projects.covid.sounds import Sounds
from uthread2 import call_after_wallclocktime_delay
HEIGHT = 64
PADDING_SIDE = 30
FONTSIZE_TEXT = 48
LEADING_TEXT = 4
TEXTURES_FOLDER = 'res:/UI/Texture/classes/ProjectDiscovery/covid/'
LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Results/'
FADE_OUT_DELAY = 3.0
FADE_OUT_DURATION = 0.5

class ResultType(object):
    PASSED = 0
    FAILED = 1
    UNKNOWN = 2


LABEL_PATH_BY_RESULT_TYPE = {ResultType.PASSED: LABELS_FOLDER + 'Passed',
 ResultType.FAILED: LABELS_FOLDER + 'Failed',
 ResultType.UNKNOWN: LABELS_FOLDER + 'Submitted'}
COLOR_TEXT_BY_RESULT_TYPE = {ResultType.PASSED: (0.2, 0.74, 0.95, 1.0),
 ResultType.FAILED: (0.97, 0.09, 0.13, 1.0),
 ResultType.UNKNOWN: (0.2, 0.74, 0.95, 1.0)}
BACKGROUND_TEXTURE_PATH_BY_RESULT_TYPE = {ResultType.PASSED: TEXTURES_FOLDER + 'banner.png',
 ResultType.FAILED: TEXTURES_FOLDER + 'banner_red.png',
 ResultType.UNKNOWN: TEXTURES_FOLDER + 'banner.png'}
SOUND_BY_RESULT_TYPE = {ResultType.PASSED: Sounds.RESULTS_SUCCESS,
 ResultType.FAILED: Sounds.RESULTS_FAILURE,
 ResultType.UNKNOWN: Sounds.RESULTS_SUCCESS}

class ResultBanner(Container):

    def ApplyAttributes(self, attributes):
        super(ResultBanner, self).ApplyAttributes(attributes)
        sm = ServiceManager.Instance()
        self.audio = sm.GetService('audio')
        self.content = Container(name='banner_container', parent=self, align=uiconst.CENTER, height=HEIGHT)
        self.label = Label(name='banner_label', parent=self.content, align=uiconst.CENTER, fontsize=FONTSIZE_TEXT, fontStyle=STYLE_SMALLTEXT, bold=True, letterspace=LEADING_TEXT)
        self.background_sprite = Sprite(name='banner_background', parent=self.content, align=uiconst.TOALL)

    def _OnResize(self):
        self.content.width = self.width - 2 * PADDING_SIDE

    def _get_result_type(self, result):
        is_solved = result.get('isSolved', False) and 'score' in result
        if is_solved:
            score = result['score']
            if score >= 0.5:
                return ResultType.PASSED
            return ResultType.FAILED
        return ResultType.UNKNOWN

    def load_result(self, result, result_type = None):
        self.StopAnimations()
        self.Hide()
        self.opacity = 0.0
        if not result:
            return
        result_type = self._get_result_type(result) if result_type is None else result_type
        label_path = LABEL_PATH_BY_RESULT_TYPE[result_type]
        self.label.SetText(GetByLabel(label_path).upper())
        label_color = COLOR_TEXT_BY_RESULT_TYPE[result_type]
        self.label.SetTextColor(label_color)
        texture_path = BACKGROUND_TEXTURE_PATH_BY_RESULT_TYPE[result_type]
        self.background_sprite.SetTexturePath(texture_path)
        sound = SOUND_BY_RESULT_TYPE[result_type]
        self.audio.SendUIEvent(sound)
        self.Show()
        self.opacity = 1.0
        call_after_wallclocktime_delay(self.fade_out, FADE_OUT_DELAY)

    def fade_out(self):
        animations.FadeOut(self, FADE_OUT_DURATION)
