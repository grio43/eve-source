#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\evolution_progression.py
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui import Align, TextColor, TextDetail, PickState
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from gametime import HOUR, SEC
from localization import GetByLabel
from mathext import clamp
SIZE_SMALL_CIRCLE = 24
SIZE_BIG_CIRCLE = 48

class EvolutionStageContainer(Container):
    STAGE_NUMBER_COLOR_HIGHLIGHT = TextColor.HIGHLIGHT
    STAGE_NUMBER_COLOR_NO_HIGHLIGHT = TextColor.SECONDARY
    LINE_WIDTH_SMALL_CIRCULAR_GAUGE_DEFAULT = 2.0
    LINE_WIDTH_SMALL_CIRCULAR_GAUGE_NO_ACTIVE_AND_NO_PROGRESS = 1.0
    LINE_WIDTH_BIG_CIRCULAR_GAUGE = 2.0
    COLOR_CIRCULAR_GAUGE_START = eveThemeColor.THEME_FOCUS
    COLOR_CIRCULAR_GAUGE_END = eveThemeColor.THEME_FOCUS
    COLOR_CIRCULAR_GAUGE_BACKGROUND_DEFAULT = eveColor.GUNMETAL_GREY
    COLOR_CIRCULAR_GAUGE_BACKGROUND_NO_ACTIVE_AND_NO_PROGRESS = eveColor.MATTE_BLACK
    COLOR_COMPLETED_CIRCLE = eveThemeColor.THEME_FOCUS
    OPACITY_COMPLETED_CIRCLE_DEFAULT = 1.0
    OPACITY_COMPLETED_CIRCLE_HOVERED = 0.5
    TEXTURE_CIRCLE = 'res:/UI/Texture/Classes/Gauge/circle.png'
    default_width = SIZE_SMALL_CIRCLE
    default_height = SIZE_SMALL_CIRCLE

    def __init__(self, stage, is_active, progress_ratio, progress_numbers, hint, on_size_changed, *args, **kwargs):
        super(EvolutionStageContainer, self).__init__(*args, **kwargs)
        self.stage = stage
        self.progress_ratio = progress_ratio
        self.progress_numbers = progress_numbers
        self.is_active = is_active
        self.is_started = FloatCloseEnough(progress_ratio, 0.0)
        self.is_completed = FloatCloseEnough(progress_ratio, 1.0)
        self.hint = hint
        self._on_size_changed = on_size_changed
        self._construct_stage_number()
        self._construct_progress_numbers()
        self._construct_stage_gauge()
        self._construct_completed_circle()

    def _construct_stage_number(self):
        should_highlight = self.is_active or not self.is_started
        self._stage_number = TextDetail(name=u'stage_number_%s' % self.stage, parent=self, align=Align.CENTER, color=self.STAGE_NUMBER_COLOR_HIGHLIGHT if should_highlight else self.STAGE_NUMBER_COLOR_NO_HIGHLIGHT, text=u'%s' % self.stage, display=self._get_stage_number_display(is_hovered=False))

    def _construct_progress_numbers(self):
        progress_numbers_container = ContainerAutoSize(name=u'progress_numbers_container_%s' % self.stage, parent=self, align=Align.HORIZONTALLY_CENTERED, width=SIZE_BIG_CIRCLE, clipChildren=True, alignMode=Align.TOTOP)
        self._progress_numbers_text = TextDetail(name='progress_numbers_text', parent=progress_numbers_container, align=Align.CENTER, pickState=PickState.OFF, display=self._get_progress_numbers_display(is_hovered=False), maxWidth=progress_numbers_container.width, text=self.progress_numbers)

    def _construct_stage_gauge(self):
        if self.is_active or not self.is_started:
            small_line_width = self.LINE_WIDTH_SMALL_CIRCULAR_GAUGE_DEFAULT
            color_bg = self.COLOR_CIRCULAR_GAUGE_BACKGROUND_DEFAULT
        else:
            small_line_width = self.LINE_WIDTH_SMALL_CIRCULAR_GAUGE_NO_ACTIVE_AND_NO_PROGRESS
            color_bg = self.COLOR_CIRCULAR_GAUGE_BACKGROUND_NO_ACTIVE_AND_NO_PROGRESS
        self._stage_gauge_small = GaugeCircular(name=u'stage_gauge_small_%s' % self.stage, parent=self, align=Align.CENTER, showMarker=False, radius=SIZE_SMALL_CIRCLE / 2, lineWidth=small_line_width, colorStart=self.COLOR_CIRCULAR_GAUGE_START, colorEnd=self.COLOR_CIRCULAR_GAUGE_END, colorBg=color_bg, pickState=PickState.OFF, display=self._get_small_stage_gauge_display(is_hovered=False))
        self._stage_gauge_small.SetValue(self.progress_ratio, animate=False)
        self._stage_gauge_big = GaugeCircular(name=u'stage_gauge_big_%s' % self.stage, parent=self, align=Align.CENTER, showMarker=False, radius=SIZE_BIG_CIRCLE / 2, lineWidth=self.LINE_WIDTH_BIG_CIRCULAR_GAUGE, colorStart=self.COLOR_CIRCULAR_GAUGE_START, colorEnd=self.COLOR_CIRCULAR_GAUGE_END, colorBg=color_bg, pickState=PickState.OFF, display=self._get_big_stage_gauge_display(is_hovered=False))
        self._stage_gauge_big.SetValue(self.progress_ratio, animate=False)

    def _construct_completed_circle(self):
        self._completed_circle = Sprite(name=u'completed_circle_%s' % self.stage, parent=self, align=Align.TOALL, texturePath=self.TEXTURE_CIRCLE, pickState=PickState.OFF, display=self.is_completed, color=self.COLOR_COMPLETED_CIRCLE, opacity=self._get_completed_circle_opacity(is_hovered=False))

    def _get_stage_number_display(self, is_hovered):
        if is_hovered:
            return False
        return True

    def _get_progress_numbers_display(self, is_hovered):
        if is_hovered:
            return True
        return False

    def _get_small_stage_gauge_display(self, is_hovered):
        if is_hovered:
            return False
        if self.is_completed:
            return False
        return True

    def _get_big_stage_gauge_display(self, is_hovered):
        if is_hovered:
            return True
        return False

    def _get_completed_circle_opacity(self, is_hovered):
        if is_hovered:
            return self.OPACITY_COMPLETED_CIRCLE_HOVERED
        return self.OPACITY_COMPLETED_CIRCLE_DEFAULT

    def OnMouseEnter(self, *args):
        super(EvolutionStageContainer, self).OnMouseEnter(*args)
        self.width = SIZE_BIG_CIRCLE
        self.height = SIZE_BIG_CIRCLE
        self._stage_number.display = self._get_stage_number_display(is_hovered=True)
        self._progress_numbers_text.display = self._get_progress_numbers_display(is_hovered=True)
        self._stage_gauge_small.display = self._get_small_stage_gauge_display(is_hovered=True)
        self._stage_gauge_big.display = self._get_big_stage_gauge_display(is_hovered=True)
        self._completed_circle.opacity = self._get_completed_circle_opacity(is_hovered=True)
        self._on_size_changed(is_hovered=True)

    def OnMouseExit(self, *args):
        super(EvolutionStageContainer, self).OnMouseExit(*args)
        self.width = SIZE_SMALL_CIRCLE
        self.height = SIZE_SMALL_CIRCLE
        self._stage_number.display = self._get_stage_number_display(is_hovered=False)
        self._progress_numbers_text.display = self._get_progress_numbers_display(is_hovered=False)
        self._stage_gauge_small.display = self._get_small_stage_gauge_display(is_hovered=False)
        self._stage_gauge_big.display = self._get_big_stage_gauge_display(is_hovered=False)
        self._completed_circle.opacity = self._get_completed_circle_opacity(is_hovered=False)
        self._on_size_changed(is_hovered=False)


class BaseEvolutionProgressionContainer(Container):
    LABEL_PATH_LEVEL_PROGRESS = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/LevelProgress'
    PADDING_BETWEEN_CIRCLES = 13
    MIN_PADDING_BETWEEN_CIRCLES_ON_HOVER = 4

    def __init__(self, *args, **kwargs):
        self._stage_containers = []
        self.padding_between_circles_on_hover = self.PADDING_BETWEEN_CIRCLES
        super(BaseEvolutionProgressionContainer, self).__init__(*args, **kwargs)

    def clear(self):
        self._stage_containers = []
        self.Flush()

    def load(self, controller):
        self.clear()
        current_level = self._get_current_level(controller)
        stages_and_level_bands = self._get_stages_and_level_bands(controller)
        self._update_width(stages_and_level_bands)
        content = Container(name='content_container', parent=self, align=Align.TOTOP, height=SIZE_BIG_CIRCLE)
        for stage in sorted(stages_and_level_bands.keys(), reverse=True):
            lower, upper = stages_and_level_bands[stage]
            level_delta = current_level - lower
            progress_delta = upper - lower
            if lower <= current_level < upper:
                is_active = True
                progress_ratio = self._get_progress_ratio(current_level, lower, upper)
                progress_numbers = self._get_progress_numbers(level_delta, progress_delta)
            elif current_level < lower:
                is_active = False
                progress_ratio = 0.0
                progress_numbers = self._get_progress_numbers(0, progress_delta)
            else:
                is_active = False
                progress_ratio = 1.0
                progress_numbers = self._get_progress_numbers(progress_delta, progress_delta)
            stage_container = EvolutionStageContainer(name='evolution_stage_container_%s' % stage, parent=content, align=Align.CENTERRIGHT, stage=stage, is_active=is_active, progress_ratio=progress_ratio, progress_numbers=progress_numbers, pickState=PickState.ON, hint=self._get_hint(controller, stage, progress_numbers), on_size_changed=self._on_stage_container_size_changed)
            self._stage_containers.append(stage_container)

        self._update_positions(is_hovered=False)

    def _on_stage_container_size_changed(self, is_hovered):
        self._update_positions(is_hovered)

    def _update_positions(self, is_hovered):
        padding = self.padding_between_circles_on_hover if is_hovered else self.PADDING_BETWEEN_CIRCLES
        left = 0
        for stage_container in self._stage_containers:
            stage_container.left = left
            left += stage_container.width + padding

    def _update_width(self, stages_and_level_bands):
        num_stages = len(stages_and_level_bands)
        default_width = SIZE_SMALL_CIRCLE * num_stages + self.PADDING_BETWEEN_CIRCLES * (num_stages - 1)
        self.padding_between_circles_on_hover = max(self.MIN_PADDING_BETWEEN_CIRCLES_ON_HOVER, (default_width - SIZE_BIG_CIRCLE - SIZE_SMALL_CIRCLE * (num_stages - 1)) / (num_stages - 1))
        hovered_width = SIZE_BIG_CIRCLE + (SIZE_SMALL_CIRCLE + self.padding_between_circles_on_hover) * (num_stages - 1)
        self.width = max(default_width, hovered_width)

    def _get_progress_numbers(self, level, level_upper):
        if None in (level, level_upper):
            return ''
        return GetByLabel(self.LABEL_PATH_LEVEL_PROGRESS, current_level=level, level_upper_band=level_upper)

    def _get_progress_ratio(self, level, level_lower, level_upper):
        if None in (level, level_lower, level_upper) or level_upper <= level_lower:
            return 0.0
        elif level >= level_upper:
            return 1.0
        elif level <= level_lower:
            return 0.0
        else:
            return clamp(value=float(level - level_lower) / (level_upper - level_lower), low=0.0, high=1.0)

    def _get_current_level(self, controller):
        raise NotImplementedError('Must implement _get_level in derived class')

    def _get_stages_and_level_bands(self, controller):
        raise NotImplementedError('Must implement _get_stages_and_level_bands in derived class')

    def _get_hint(self, controller, stage, progress_numbers):
        raise NotImplementedError('Must implement _get_hint in derived class')


class DevelopmentProgressionContainer(BaseEvolutionProgressionContainer):
    LABEL_PATH_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/DevelopmentProgressTooltip'
    LABEL_PATH_VALUE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/DevelopmentValue'
    LABEL_PATH_INFOMORPH_RATE_DATA = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/InfomorphGenerationRateData'

    def _get_current_level(self, controller):
        level = controller.get_current_development_level()
        level_lower, level_upper = controller.get_current_development_level_bands()
        level = clamp(level, level_lower, level_upper)
        max_level = controller.get_maximum_development_level()
        if controller.is_development_maxed_out():
            level = max_level
        return level

    def _get_stages_and_level_bands(self, controller):
        return controller.get_development_stages_and_level_bands()

    def _get_hint(self, controller, stage, progress_numbers):
        lower, upper = controller.get_infomorph_generation_rates_per_second(stage + 1)
        rate = GetByLabel(self.LABEL_PATH_INFOMORPH_RATE_DATA, lower=int(lower * HOUR / SEC), upper=int(upper * HOUR / SEC))
        return GetByLabel(self.LABEL_PATH_TOOLTIP, development_value=GetByLabel(self.LABEL_PATH_VALUE, level=stage), development_progress=progress_numbers, rate=rate)


class AnarchyProgressionContainer(BaseEvolutionProgressionContainer):
    LABEL_PATH_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/AnarchyProgressTooltip'
    LABEL_PATH_VALUE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/AnarchyValue'
    LABEL_PATH_PERCENTAGE = 'UI/Common/Formatting/Percentage'

    def _get_current_level(self, controller):
        level = controller.get_current_anarchy_level()
        level_lower, level_upper = controller.get_current_anarchy_level_bands()
        level = clamp(level, level_lower, level_upper)
        max_level = controller.get_maximum_anarchy_level()
        if controller.is_anarchy_maxed_out():
            level = max_level
        return level

    def _get_stages_and_level_bands(self, controller):
        return controller.get_anarchy_stages_and_level_bands()

    def _get_hint(self, controller, stage, progress_numbers):
        return GetByLabel(self.LABEL_PATH_TOOLTIP, anarchy_value=GetByLabel(self.LABEL_PATH_VALUE, level=stage), anarchy_progress=progress_numbers, workforce_cost=GetByLabel(self.LABEL_PATH_PERCENTAGE, percentage=controller.get_workforce_cost_as_percentage(stage + 1)))
