#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\card.py
import carbonui
import carbonui.const as uiconst
import eveui
import math
import trinity
import uthread2
from carbonui import Align
from carbonui.primitives.container import Container
from carbonui.uiconst import PickState
from eve.client.script.ui import eveColor, eveThemeColor
from jobboard.client.ui.solar_system_chip import SolarSystemChip
from jobboard.client.ui.tag_icon import TagIcon
from jobboard.client.ui.track_button import TrackJobIconButton
from jobboard.client.ui.util import get_career_path_bg
from jobboard.client.ui.const import HERO_CARD_MAX_WIDTH
GLOW_IDLE = 0.5
GLOW_HOVER = 1.0
GLOW_MOUSE_DOWN = 2.0
FLAIR_SIZE = 400

class BaseJobCard(eveui.Container):
    default_pickState = PickState.OFF
    default_align = eveui.Align.to_all
    default_pos = (0, 0, 0, 0)
    default_height = 176
    default_width = 300
    isDragObject = True
    OPACITY_IDLE = 0.1
    OPACITY_HOVER = 0.2
    OPACITY_MOUSEDOWN = 0.4

    def __init__(self, controller, show_feature = False, show_as_reward = False, *args, **kwargs):
        kwargs['name'] = u'entry_{}'.format(controller.job_id)
        super(BaseJobCard, self).__init__(*args, **kwargs)
        self.job = controller
        self._show_feature = show_feature
        self._show_as_reward = show_as_reward
        self._solar_system_chip = None
        self._layout()
        self.pickState = PickState.ON
        self.job.on_job_updated.connect(self._on_job_updated)
        uthread2.start_tasklet(self._update_state)

    def Close(self):
        self.job.on_job_updated.disconnect(self._on_job_updated)
        super(BaseJobCard, self).Close()

    def _on_job_updated(self):
        self.Flush()
        self._layout()
        self._update_state()

    def _update_state(self):
        self._update_top_title()
        self._update_left_line_color()
        self._update_hover_frame_color()

    def _layout(self):
        self._left_line = eveui.Line(name='leftLine', parent=self, align=Align.TOLEFT, color=self._left_line_color, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.6, glowBrightness=0.5)
        self.content = Container(name='content', parent=self)
        self.bottom = eveui.Container(name='bottom', parent=self.content, padding=(16, 0, 16, 8), align=Align.TOBOTTOM, height=24)
        self.top_cont = eveui.Container(name='topCont', parent=self.content, align=Align.TOTOP, height=50, padding=(16, 16, 16, 0))
        self.middle = eveui.Container(name='middle', parent=self.content, align=Align.TOALL, padding=16)
        self._construct_top()
        self._construct_middle()
        self._construct_bottom()
        self._construct_underlay()

    def _construct_underlay(self):
        eveui.Frame(name='card_mask_frame', bgParent=self, texturePath='res:/UI/Texture/classes/Opportunities/card_mask.png', cornerSize=16, color=(0, 0, 0, 0.9))
        self._hover_frame = eveui.Frame(name='hover_frame', parent=self, texturePath='res:/UI/Texture/classes/Opportunities/card_mask.png', cornerSize=16, color=self._hover_frame_color, opacity=self.OPACITY_IDLE)

    def _construct_bottom(self):
        self._construct_attention_icons(self.bottom)
        self._track_button_container = eveui.ContainerAutoSize(parent=self.bottom, align=Align.TORIGHT)
        if not self.job.is_tracked:
            self._track_button_container.opacity = 0
            self._track_button_container.DisableAutoSize()
        TrackJobIconButton(parent=self._track_button_container, align=Align.TORIGHT, job=self.job)
        self._actions_container = eveui.ContainerAutoSize(name='bottomButtons', parent=self.bottom, align=Align.TORIGHT, opacity=0.0)
        self._actions_container.DisableAutoSize()
        self._construct_actions(self._actions_container)

    def _construct_attention_icons(self, parent):
        pass

    def _construct_actions(self, parent):
        pass

    def _construct_middle(self):
        carbonui.TextHeader(parent=self.middle, align=Align.TOTOP, maxLines=2, text=self.job.title, bold=True)

    def _construct_top(self):
        self._top_right_container = eveui.ContainerAutoSize(name='top_right_container', parent=self.top_cont, align=Align.TORIGHT)
        self._construct_top_right()
        self._header_row = Container(name='headerRow', parent=self.top_cont, align=Align.TOTOP, height=20)
        title_icon_cont = eveui.ContainerAutoSize(name='iconCont', parent=self._header_row, align=Align.TOLEFT, top=-2, padRight=2)
        title_icon_cont_content = eveui.ContainerAutoSize(name='icon_cont_content', parent=title_icon_cont, align=Align.TOPLEFT, height=TagIcon.default_height)
        self._construct_title_icons(title_icon_cont_content)
        title_cont = Container(name='titleCont', parent=self._header_row, clipChildren=True)
        self.top_title = carbonui.TextBody(name='top_title', parent=title_cont, align=Align.TOPLEFT, color=carbonui.TextColor.SECONDARY, autoFadeSides=16)
        self._construct_solar_system_chip()

    def _construct_top_right(self):
        pass

    def _update_top_title(self):
        self.top_title.text = self._get_top_title()

    def _update_left_line_color(self):
        state_info = self.job.get_state_info()
        if not state_info:
            self._left_line.rgb = self._left_line_color[:3]
            return
        self._left_line.rgb = state_info['color'][:3]

    def _update_hover_frame_color(self):
        state_info = self.job.get_state_info()
        if state_info:
            rgb = state_info['color'][:3]
        else:
            rgb = self._hover_frame_color[:3]
        self._hover_frame.rgb = rgb

    def _construct_title_icons(self, container):
        if self._show_feature:
            title = self.job.feature_tag.title
            icon = self.job.feature_tag.icon
        else:
            title = self.job.career_title
            icon = self.job.career_icon
        tag_icon = TagIcon(parent=container, align=Align.TOLEFT, texturePath=icon, hint=title, pickState=PickState.ON, padRight=4)
        tag_icon.OnClick = self.OnClick

    def _get_top_title(self):
        if self._show_feature:
            return self.job.feature_tag.title or self.job.career_title
        else:
            return self.job.career_title

    def OnColorThemeChanged(self):
        super(BaseJobCard, self).OnColorThemeChanged()
        self._update_left_line_color()
        self._update_hover_frame_color()

    def _construct_solar_system_chip(self):
        solar_system_id = self.job.solar_system_id
        if solar_system_id:
            container = eveui.Container(parent=self.top_cont, align=Align.TOTOP, height=20, padTop=8, clipChildren=True)
            self._solar_system_chip = SolarSystemChip(parent=container, state=eveui.State.disabled, align=Align.TOLEFT, solar_system_id=solar_system_id)

    def OnMouseEnter(self, *args):
        eveui.Sound.entry_hover.play()
        eveui.fade_in(self._hover_frame, end_value=self.OPACITY_HOVER, duration=0.2)
        eveui.animate(self._left_line, 'glowBrightness', GLOW_HOVER, duration=0.2)
        eveui.animation.fade_in(self._actions_container, duration=0.3)
        self._actions_container.ExpandWidth()
        eveui.animation.fade_in(self._track_button_container, duration=0.3)
        self._track_button_container.ExpandWidth()

    def OnMouseExit(self, *args):
        eveui.fade(self._hover_frame, end_value=self.OPACITY_IDLE, duration=0.2)
        eveui.animate(self._left_line, 'glowBrightness', GLOW_IDLE, duration=0.2)
        eveui.animation.fade_out(self._actions_container, duration=0.2)
        self._actions_container.CollapseWidth(duration=0.3)
        if not self.job.is_tracked:
            eveui.animation.fade_out(self._track_button_container, duration=0.2)
            self._track_button_container.CollapseWidth(duration=0.3)

    def OnClick(self, *args):
        eveui.Sound.button_click.play()
        self.job.on_click()

    def OnMouseDown(self, *args):
        eveui.fade(self._hover_frame, end_value=self.OPACITY_MOUSEDOWN, duration=0.2)
        eveui.animate(self._left_line, 'glowBrightness', GLOW_MOUSE_DOWN, duration=0.2)

    def OnMouseUp(self, *args):
        eveui.fade(self._hover_frame, end_value=self.OPACITY_IDLE, duration=0.2)
        eveui.animate(self._left_line, 'glowBrightness', GLOW_IDLE, duration=0.2)

    def GetDragData(self):
        return self.job.get_drag_data()

    def GetMenu(self):
        return self.job.get_menu()

    @property
    def _left_line_color(self):
        return eveThemeColor.THEME_FOCUS

    @property
    def _hover_frame_color(self):
        return eveThemeColor.THEME_FOCUS

    @property
    def _bg_flair_color(self):
        return eveThemeColor.THEME_FOCUSDARK


class JobCard(BaseJobCard):

    def _construct_underlay(self):
        flair_cont = Container(name='flairCont', parent=self, pickState=PickState.OFF, clipChildren=True)
        self._bg_flair = eveui.Sprite(name='bgFlair', parent=flair_cont, texturePath=get_career_path_bg(self.job.career_id), color=self._bg_flair_color, align=Align.TOPLEFT, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, opacity=0.7, pos=(-FLAIR_SIZE / 2 + 25,
         -FLAIR_SIZE / 2 + 25,
         FLAIR_SIZE,
         FLAIR_SIZE))
        super(JobCard, self)._construct_underlay()

    def _construct_bottom(self):
        eveui.Frame(bgParent=self.bottom, texturePath='res:/UI/Texture/classes/Opportunities/card_mask.png', cornerSize=16, color=eveColor.WHITE, opacity=0.05, padding=(-16, -8, -16, -8))
        super(JobCard, self)._construct_bottom()
        self.bottom_content_cont = eveui.Container(name='bottom_content_cont', parent=self.bottom)
        self._construct_bottom_content()

    def _construct_bottom_content(self):
        self._construct_subtitle(self.job.subtitle)

    def _construct_subtitle(self, subtitle):
        if subtitle:
            text_container = eveui.Container(parent=self.bottom_content_cont, align=carbonui.Align.TOALL, clipChildren=True)
            carbonui.TextBody(parent=text_container, align=carbonui.Align.CENTERLEFT, maxLines=1, autoFadeSides=16, text=subtitle)

    def OnColorThemeChanged(self):
        super(JobCard, self).OnColorThemeChanged()
        self._bg_flair.rgb = self._bg_flair_color[:3]

    def OnMouseEnter(self, *args):
        super(JobCard, self).OnMouseEnter(*args)
        eveui.animate(self._bg_flair, 'glowBrightness', 0.3, duration=0.2)
        eveui.animate(self._bg_flair, 'rotation', end_value=self._bg_flair.rotation + 2 * math.pi, duration=80.0, curve_type=eveui.CurveType.linear)

    def OnMouseExit(self, *args):
        super(JobCard, self).OnMouseExit(*args)
        eveui.animate(self._bg_flair, 'glowBrightness', 0.0, duration=0.2)
        eveui.animate(self._bg_flair, 'rotation', end_value=self._bg_flair.rotation + 0.025, duration=0.2)


class JobHeroCard(BaseJobCard):
    default_width = 450
    OPACITY_IDLE = 0.25
    OPACITY_HOVER = 0.05
    OPACITY_MOUSEDOWN = 0.3

    def _construct_underlay(self):
        super(JobHeroCard, self)._construct_underlay()
        gradient_container = Container(name='gradient_container', parent=self, align=eveui.Align.to_all, pickState=PickState.OFF, clipChildren=True)
        bg_container = Container(name='bg_container', parent=self, align=eveui.Align.to_all, pickState=PickState.OFF, clipChildren=True)
        title_width, _ = carbonui.TextHeader.MeasureTextSize(self.job.title, bold=True, maxLines=2)
        eveui.GradientSprite(parent=gradient_container, align=Align.TOLEFT_PROP, width=0.6, minWidth=title_width + 48, rgbData=[(0, (0, 0, 0))], alphaData=[(0, 0.9), (1.0, 0)])
        eveui.Sprite(name='bg_image', parent=bg_container, texturePath=self.job.background_image, textureSecondaryPath='res:/UI/Texture/classes/Opportunities/hero_card_mask.png', align=Align.CENTERRIGHT, width=HERO_CARD_MAX_WIDTH, height=176, spriteEffect=trinity.TR2_SFX_MODULATE)

    def _construct_middle(self):
        subtitle = self.job.subtitle
        if subtitle:
            carbonui.TextBody(parent=self.middle, align=Align.TOTOP, maxLines=1, text=subtitle, padBottom=4)
        super(JobHeroCard, self)._construct_middle()

    @property
    def _hover_frame_color(self):
        return eveColor.BLACK
