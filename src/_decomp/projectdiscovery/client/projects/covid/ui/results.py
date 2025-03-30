#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\results.py
from carbon.common.script.sys.serviceManager import ServiceManager
from carbon.common.script.util.format import FmtAmt
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.moreIcon import DescriptionIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from carbonui.fontconst import STYLE_HEADER
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from localization import GetByLabel
from localization.util import IsSessionLanguageConcise
import log
from projectdiscovery.client.projects.covid.sounds import Sounds
from projectdiscovery.client.projects.covid.ui.containerwithcorners import ContainerWithCorners
SMALL_GAUGE_SIZE = 56
BIG_GAUGE_SIZE = 188
PADDING_GAUGES_TO_LABELS = 38
PADDING_BETWEEN_SMALL_GAUGES = 11
PADDING_SMALL_GAUGE_TO_LABEL = 12
PADDING_BETWEEN_LABELS_BIG_GAUGE = -10
GRADING_LABEL_HEIGHT = 48
PADDING_GRADING_TO_XP_LABEL = 20
PADDING_BETWEEN_PROGRESS_LABELS = 10
PADDING_ICON_TO_LABEL = 12
PADDING_CONTAINER_TO_LABEL = 24
PADDING_CONTAINER_TO_INFO_ICON = 45
PROGRESS_LABEL_WIDTH = 322
PROGRESS_LABEL_HEIGHT = 64
GAUGES_CONTAINER_HEIGHT = BIG_GAUGE_SIZE
TOTAL_WIDTH = PROGRESS_LABEL_WIDTH
GAUGE_ANIMATION_DURATION = 1.0
SMALL_GAUGE_LINE_WIDTH = 8.0
BIG_GAUGE_LINE_WIDTH = 8.0
PERFECT_VALUE = 0.7
PAR_VALUE = 0.5
FONTSIZE_SMALL_GAUGE_LABEL = 14
FONTSIZE_SMALL_GAUGE_DESCRIPTION = 14
FONTSIZE_BIG_GAUGE_LABEL = 60
FONTSIZE_BIG_GAUGE_DESCRIPTION = 18
FONTSIZE_GRADING_LABEL = 24
FONTSIZE_PROGRESS_LABEL = 18
COLOR_BACKGROUND_GAUGE = (0.2, 0.74, 0.95, 0.2)
COLOR_BACKGROUND_PROGRESS_LABEL = (0.05, 0.18, 0.24, 0.6)
COLOR_BACKGROUND_PROGRESS_ICON = (1.0, 1.0, 1.0, 0.9)
COLOR_TEXT = (0.2, 0.74, 0.95, 1.0)
TEXTURE_PATH_XP_ICON = 'res:/UI/Texture/classes/ProjectDiscovery/covid/xp.png'
TEXTURE_PATH_ISK_ICON = 'res:/UI/Texture/classes/ProjectDiscovery/covid/isk.png'
TEXTURE_PATH_1ST_ICON = 'res:/UI/Texture/classes/ProjectDiscovery/covid/1st.png'
HIGH_SCORE_GAUGE_NAME = 'high_score'
PAR_GAUGE_NAME = 'par'
AVERAGE_GAUGE_NAME = 'average'
SMALL_GAUGES = [HIGH_SCORE_GAUGE_NAME, PAR_GAUGE_NAME, AVERAGE_GAUGE_NAME]
LABELS_FOLDER = 'UI/ProjectDiscovery/Covid/Results/'
LABEL_PATH_ACCURACY = LABELS_FOLDER + 'Accuracy'
LABEL_PATH_FIRST_REVIEWER = LABELS_FOLDER + 'FirstReviewer'
LABEL_PATH_THANKS = LABELS_FOLDER + 'Thanks'
GRADING_BY_SCORE = {90: LABELS_FOLDER + 'Grade90',
 70: LABELS_FOLDER + 'Grade70',
 50: LABELS_FOLDER + 'Grade50',
 40: LABELS_FOLDER + 'Grade40',
 0: LABELS_FOLDER + 'Grade0'}
TEXTURES_FOLDER = 'res:/UI/Texture/classes/ProjectDiscovery/covid/'
GRADE_BACKGROUND_TEXTURE_BY_SCORE = {50: TEXTURES_FOLDER + 'banner.png',
 0: TEXTURES_FOLDER + 'banner_red.png'}
LABEL_PATH_SMALL_GAUGE_DESCRIPTION = {HIGH_SCORE_GAUGE_NAME: LABELS_FOLDER + 'HighScore',
 PAR_GAUGE_NAME: LABELS_FOLDER + 'ParScore',
 AVERAGE_GAUGE_NAME: LABELS_FOLDER + 'AverageScore'}

class Statistics(ContainerAutoSize):
    default_width = TOTAL_WIDTH
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        super(Statistics, self).ApplyAttributes(attributes)
        sm = ServiceManager.Instance()
        self.audio = sm.GetService('audio')
        self._build_score_gauges()
        self._build_progress_labels()

    def _build_score_gauges(self):
        self.gauges_container = Container(name='gauges_container', parent=self, align=uiconst.TOTOP, height=BIG_GAUGE_SIZE)
        self._build_small_gauges()
        self._build_big_gauge()

    def _build_small_gauges(self):
        self.small_gauges = {}
        self.small_gauge_labels = {}
        self.small_gauge_descriptions = {}
        small_gauges_container = Container(name='small_gauges_container', parent=self.gauges_container, align=uiconst.TOLEFT, width=TOTAL_WIDTH - BIG_GAUGE_SIZE)
        for gauge_order, gauge_name in enumerate(SMALL_GAUGES):
            self._build_small_gauge(small_gauges_container, gauge_order, gauge_name)

    def _build_small_gauge(self, parent, order, name):
        padding = PADDING_BETWEEN_SMALL_GAUGES if order == 1 else 0
        small_gauge_and_description_container = Container(name='small_gauge_and_description_container_%s_%s' % (order, name), parent=parent, align=uiconst.TOTOP, height=SMALL_GAUGE_SIZE, padTop=padding, padBottom=padding)
        small_gauge_container = ContainerWithCorners(name='small_gauge_container_%s_%s' % (order, name), parent=small_gauge_and_description_container, align=uiconst.TOLEFT, width=SMALL_GAUGE_SIZE)
        self.small_gauges[name] = GaugeCircular(name='small_gauge_%s_%s' % (order, name), parent=small_gauge_container, align=uiconst.TOLEFT, width=SMALL_GAUGE_SIZE, radius=SMALL_GAUGE_SIZE / 2, showMarker=False, state=uiconst.UI_HIDDEN, colorBg=COLOR_BACKGROUND_GAUGE, lineWidth=SMALL_GAUGE_LINE_WIDTH)
        self.small_gauge_labels[name] = Label(name='small_gauge_label_%s_%s' % (order, name), parent=small_gauge_container, align=uiconst.CENTER, fontsize=FONTSIZE_SMALL_GAUGE_LABEL, color=COLOR_TEXT)
        self.small_gauge_descriptions[name] = Label(name='small_gauge_description_%s_%s' % (order, name), parent=small_gauge_and_description_container, align=uiconst.CENTERLEFT, padLeft=SMALL_GAUGE_SIZE + PADDING_SMALL_GAUGE_TO_LABEL, fontsize=FONTSIZE_SMALL_GAUGE_DESCRIPTION)

    def _build_big_gauge(self):
        big_gauge_container = ContainerWithCorners(name='big_gauge_container', parent=self.gauges_container, align=uiconst.TOLEFT, width=BIG_GAUGE_SIZE, shouldShowLeftCorners=False)
        self.big_gauge = GaugeCircular(name='big_gauge', parent=big_gauge_container, align=uiconst.TOTOP, height=BIG_GAUGE_SIZE, radius=BIG_GAUGE_SIZE / 2, showMarker=False, lineWidth=BIG_GAUGE_LINE_WIDTH, state=uiconst.UI_HIDDEN, colorBg=COLOR_BACKGROUND_GAUGE)
        self.big_gauge_label = Label(name='big_gauge_label', parent=big_gauge_container, align=uiconst.CENTERTOP, fontsize=FONTSIZE_BIG_GAUGE_LABEL, fontStyle=STYLE_HEADER)
        self.big_gauge_description = Label(name='big_gauge_description', parent=big_gauge_container, align=uiconst.CENTERTOP, fontsize=FONTSIZE_BIG_GAUGE_DESCRIPTION, color=COLOR_TEXT)

    def _build_progress_labels(self):
        self.labels_container = Container(name='labels_container', parent=self, align=uiconst.TOTOP)
        self._build_grading_label()
        self._build_first_label()
        self._build_xp_label()
        self._build_isk_label()
        self._build_thanks_label()

    def _build_grading_label(self):
        self.grading_label_container = ContainerWithCorners(name='grading_label_container', parent=self.labels_container, align=uiconst.TOTOP, height=GRADING_LABEL_HEIGHT, padBottom=PADDING_GRADING_TO_XP_LABEL)
        self.grading_label = Label(name='grading_label', parent=self.grading_label_container, align=uiconst.CENTER, fontsize=FONTSIZE_GRADING_LABEL)
        self.grading_label_background = Sprite(name='grading_label_background', parent=self.grading_label_container, align=uiconst.TOALL)

    def _build_first_label(self):
        self.first_label_container = Container(name='first_label_container', parent=self.labels_container, align=uiconst.TOTOP, height=PROGRESS_LABEL_HEIGHT, padBottom=PADDING_BETWEEN_PROGRESS_LABELS)
        first_icon_width = PROGRESS_LABEL_HEIGHT
        container_width = PROGRESS_LABEL_WIDTH - first_icon_width - PADDING_ICON_TO_LABEL
        text_width = container_width - 2 * PADDING_CONTAINER_TO_LABEL
        Sprite(name='first_icon', parent=self.first_label_container, align=uiconst.TOLEFT, width=first_icon_width, texturePath=TEXTURE_PATH_1ST_ICON, bgColor=COLOR_BACKGROUND_PROGRESS_ICON)
        first_container = ContainerWithCorners(name='first_container', parent=self.first_label_container, align=uiconst.TOLEFT, width=container_width, bgColor=COLOR_BACKGROUND_PROGRESS_LABEL, padLeft=PADDING_ICON_TO_LABEL)
        self.first_label = Label(name='first_label', parent=first_container, align=uiconst.CENTERLEFT, fontsize=FONTSIZE_PROGRESS_LABEL, padLeft=PADDING_CONTAINER_TO_LABEL, width=text_width)

    def _build_xp_label(self):
        self.xp_label_container = Container(name='xp_label_container', parent=self.labels_container, align=uiconst.TOTOP, height=PROGRESS_LABEL_HEIGHT)
        xp_icon_width = PROGRESS_LABEL_HEIGHT
        Sprite(name='xp_icon', parent=self.xp_label_container, align=uiconst.TOLEFT, width=xp_icon_width, texturePath=TEXTURE_PATH_XP_ICON, bgColor=COLOR_BACKGROUND_PROGRESS_ICON)
        xp_container = ContainerWithCorners(name='xp_container', parent=self.xp_label_container, align=uiconst.TOLEFT, width=PROGRESS_LABEL_WIDTH - xp_icon_width - PADDING_ICON_TO_LABEL, bgColor=COLOR_BACKGROUND_PROGRESS_LABEL, padLeft=PADDING_ICON_TO_LABEL)
        self.xp_label = Label(name='xp_label', parent=xp_container, align=uiconst.CENTERLEFT, fontsize=FONTSIZE_PROGRESS_LABEL, padLeft=PADDING_CONTAINER_TO_LABEL, bold=True)
        self.xp_info_icon = DescriptionIcon(parent=xp_container, align=uiconst.CENTERLEFT, left=PADDING_CONTAINER_TO_INFO_ICON, state=uiconst.UI_HIDDEN)

    def _build_isk_label(self):
        self.isk_label_container = Container(name='isk_label_container', parent=self.labels_container, align=uiconst.TOTOP, height=PROGRESS_LABEL_HEIGHT, padTop=PADDING_BETWEEN_PROGRESS_LABELS)
        isk_icon_width = PROGRESS_LABEL_HEIGHT
        Sprite(name='isk_icon', parent=self.isk_label_container, align=uiconst.TOLEFT, width=isk_icon_width, texturePath=TEXTURE_PATH_ISK_ICON, bgColor=COLOR_BACKGROUND_PROGRESS_ICON)
        isk_container = ContainerWithCorners(name='isk_container', parent=self.isk_label_container, align=uiconst.TOLEFT, width=PROGRESS_LABEL_WIDTH - isk_icon_width - PADDING_ICON_TO_LABEL, bgColor=COLOR_BACKGROUND_PROGRESS_LABEL, padLeft=PADDING_ICON_TO_LABEL)
        self.isk_label = Label(name='isk_label', parent=isk_container, align=uiconst.CENTERLEFT, fontsize=FONTSIZE_PROGRESS_LABEL, padLeft=PADDING_CONTAINER_TO_LABEL, bold=True)

    def _build_thanks_label(self):
        self.thanks_label_container = ContainerWithCorners(name='thanks_label_container', parent=self.labels_container, align=uiconst.TOTOP, height=PROGRESS_LABEL_HEIGHT, bgColor=COLOR_BACKGROUND_PROGRESS_LABEL, padTop=PADDING_BETWEEN_PROGRESS_LABELS)
        self.thanks_label = Label(name='thanks_label', parent=self.thanks_label_container, align=uiconst.CENTERLEFT, fontsize=FONTSIZE_PROGRESS_LABEL, padLeft=PADDING_CONTAINER_TO_LABEL, width=PROGRESS_LABEL_WIDTH - 2 * PADDING_CONTAINER_TO_LABEL)

    def _load_small_gauge(self, gauge_name, value):
        self.small_gauges[gauge_name].SetValue(value, animate=False)
        percent_value = GetByLabel('UI/Common/Percentage', percentage=int(value * 100))
        self.small_gauge_labels[gauge_name].SetText(percent_value)
        self.small_gauge_descriptions[gauge_name].SetText(GetByLabel(LABEL_PATH_SMALL_GAUGE_DESCRIPTION[gauge_name]))
        self.small_gauges[gauge_name].Show()
        self.gauges_container.Show()

    def _load_big_gauge(self, value):
        self.big_gauge.SetValueAndMarkerTimed(value, GAUGE_ANIMATION_DURATION)
        percent_value = GetByLabel('UI/Common/Percentage', percentage=int(value * 100))
        self.big_gauge_label.SetText(percent_value)
        self.big_gauge_description.SetText(GetByLabel(LABEL_PATH_ACCURACY))
        label_height = self.big_gauge_label.height
        description_height = self.big_gauge_description.height
        padding = 0 if IsSessionLanguageConcise() else PADDING_BETWEEN_LABELS_BIG_GAUGE
        total_text_height = label_height + description_height + padding
        self.big_gauge_label.top = (BIG_GAUGE_SIZE - total_text_height) / 2
        self.big_gauge_description.top = self.big_gauge_label.top + label_height + padding
        self.gauges_container.height = BIG_GAUGE_SIZE
        self.big_gauge.Show()
        self.gauges_container.Show()
        self.audio.SendUIEvent(Sounds.CALCULATE)

    def _load_grade(self, score):
        text = self._get_grade_label_path(score)
        background_texture = self._get_grade_background_texture(score)
        self.grading_label.SetText(GetByLabel(text))
        self.grading_label_background.SetTexturePath(background_texture)
        self.labels_container.height = self.labels_container.height + GRADING_LABEL_HEIGHT + PADDING_GRADING_TO_XP_LABEL
        self.grading_label_container.Show()

    def _load_first(self):
        self.first_label.SetText(GetByLabel(LABEL_PATH_FIRST_REVIEWER))
        self.labels_container.height = self.labels_container.height + PROGRESS_LABEL_HEIGHT + PADDING_BETWEEN_PROGRESS_LABELS
        self.first_label_container.Show()

    def _load_xp(self, xp, is_bonus):
        text = self._get_xp_text(xp, is_bonus)
        self.xp_label.SetText(text)
        self.labels_container.height = self.labels_container.height + PROGRESS_LABEL_HEIGHT
        self.xp_label_container.Show()

    def _load_isk(self, isk):
        text = FmtAmt(isk)
        self.isk_label.SetText(text)
        self.labels_container.height = self.labels_container.height + PROGRESS_LABEL_HEIGHT + PADDING_BETWEEN_PROGRESS_LABELS
        self.isk_label_container.Show()

    def _load_thanks(self):
        self.thanks_label.SetText(GetByLabel(LABEL_PATH_THANKS))
        self.labels_container.height = self.labels_container.height + PROGRESS_LABEL_HEIGHT + PADDING_BETWEEN_PROGRESS_LABELS
        self.thanks_label_container.Show()

    def _hide_gauges(self):
        self.gauges_container.Hide()
        self.gauges_container.height = 0
        gauges = [self.big_gauge] + [ self.small_gauges[name] for name in SMALL_GAUGES ]
        for gauge in gauges:
            gauge.Hide()

        labels = [self.big_gauge_label] + [ self.small_gauge_labels[name] for name in SMALL_GAUGES ]
        descriptions = [self.big_gauge_description] + [ self.small_gauge_descriptions[name] for name in SMALL_GAUGES ]
        for label in labels + descriptions:
            label.SetText('')

    def _hide_labels(self):
        self.labels_container.height = 0
        self.grading_label_container.Hide()
        self.first_label_container.Hide()
        self.xp_label_container.Hide()
        self.isk_label_container.Hide()
        self.thanks_label_container.Hide()

    def _get_grade_label_path(self, score):
        for min_score in reversed(sorted(GRADING_BY_SCORE.keys())):
            if score * 100 >= min_score:
                return GRADING_BY_SCORE[min_score]

        return GRADING_BY_SCORE[0]

    def _get_grade_background_texture(self, score):
        for min_score in reversed(sorted(GRADE_BACKGROUND_TEXTURE_BY_SCORE.keys())):
            if score * 100 >= min_score:
                return GRADE_BACKGROUND_TEXTURE_BY_SCORE[min_score]

        return GRADE_BACKGROUND_TEXTURE_BY_SCORE[0]

    def _get_xp_text(self, xp, is_bonus):
        if is_bonus:
            if xp % 2:
                text = FmtAmt(amount=float(xp) / 2, showFraction=1)
            else:
                text = FmtAmt(amount=int(xp / 2), showFraction=0)
        else:
            text = FmtAmt(amount=int(xp), showFraction=0)
        if is_bonus and xp > 0:
            text += u'<color=%s> x 2</color>' % Color(*COLOR_TEXT).GetHex()
        return text

    def _reset(self):
        self.Hide()
        self._hide_gauges()
        self._hide_labels()

    def load_result(self, result, show_labels = True):
        self._reset()
        if not result:
            return
        is_solved = result.get('isSolved', False)
        is_first_classification = result.get('classificationCount', None) == 0
        if is_solved:
            score = result['score']
            high_score = self._get_high_score(result)
            average_score = self._get_average_score(result)
            is_high_score = score > high_score
            if is_high_score:
                high_score = score
            self._load_big_gauge(score)
            self._load_small_gauge(HIGH_SCORE_GAUGE_NAME, high_score)
            self._load_small_gauge(PAR_GAUGE_NAME, 0.5)
            self._load_small_gauge(AVERAGE_GAUGE_NAME, average_score)
            if show_labels:
                self._load_grade(score)
        if not is_solved and is_first_classification and show_labels:
            self._load_first()
        if show_labels and 'XP_Reward' in result:
            xp = result['XP_Reward']
            is_bonus = result.get('gotBonusXP', False)
            self._load_xp(xp, is_bonus)
        if show_labels and 'ISK_Reward' in result:
            isk = result['ISK_Reward']
            self._load_isk(isk)
        if show_labels and not is_solved:
            self._load_thanks()
        try:
            if show_labels and 'requiredSkillPoints' in result:
                skill_points = result['requiredSkillPoints'][0]
                self.xp_info_icon.SetState(uiconst.UI_NORMAL)
                self.xp_info_icon.tooltipPanelClassInfo = SimpleTextTooltip(text=GetByLabel('UI/ProjectDiscovery/NotEnoughSkillPointsError', skillPoints=skill_points))
        except Exception as exc:
            log.LogException('Error displaying required SP to gain XP in Project Discovery: %s' % exc)

        padding = 0 if self.gauges_container.IsHidden() else PADDING_GAUGES_TO_LABELS
        self.labels_container.padTop = padding
        self.SetState(uiconst.UI_NORMAL)

    def _get_high_score(self, result):
        try:
            return result['task']['votes']['highScore']
        except KeyError:
            return 0

    def _get_average_score(self, result):
        try:
            return result['task']['votes']['avgScore']
        except KeyError:
            return 0

    def get_gauges_height(self):
        return self.gauges_container.height

    def get_content_height(self):
        content_height = 0
        if not self.gauges_container.IsHidden():
            content_height += self.gauges_container.height
        if not self.labels_container.IsHidden():
            content_height += self.labels_container.padTop + self.labels_container.height
        return content_height
