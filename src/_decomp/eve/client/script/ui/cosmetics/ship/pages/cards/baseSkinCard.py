#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\baseSkinCard.py
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Align, TextAlign, TextBody, TextColor, uiconst, SpriteEffect, PickState
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from cosmetics.client.liveIconRenderer import LiveIconSprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.cosmetics.ship.pages.cards import cardConst
from eve.client.script.ui.cosmetics.ship.pages.cards.cardConst import CardOutline
from signals import Signal

class SkinCard(Container):
    default_state = uiconst.UI_NORMAL
    default_width = cardConst.card_width
    default_height = cardConst.card_height
    ship_glow = True
    ANIM_DURATION = 0.2
    GLOW_AMOUNT = 0.4
    ICON_SIZE = 128

    def __init__(self, *args, **kwargs):
        super(SkinCard, self).__init__(*args, **kwargs)
        self._is_selected = False
        self.is_hovered = False
        self.live_rendered_icon = None
        self.finished_loading = False
        self.on_click = Signal('on_click')
        self._update_live_icon_thread = None
        self._update_thread = None
        self.construct_layout()
        self.update_live_icon_threaded()
        self.update_threaded()
        self.name_label.text = self.get_skin_name()

    def Close(self):
        try:
            self.kill_threads()
        finally:
            super(SkinCard, self).Close()

    def kill_threads(self):
        self.kill_update_live_icon_thread()
        self.kill_update_thread()

    def kill_update_live_icon_thread(self):
        if self._update_live_icon_thread is not None:
            self._update_live_icon_thread.kill()
            self._update_live_icon_thread = None

    def kill_update_thread(self):
        if self._update_thread is not None:
            self._update_thread.kill()
            self._update_thread = None

    def construct_layout(self):
        self.construct_content_container()
        self.construct_outline()
        self.construct_stack_lines()
        self.construct_stack_number()
        self.construct_label()
        self.construct_highlight()
        self.construct_top_line()
        self.construct_tier_indicator()
        self.construct_loading_indicator()
        self.construct_live_rendered_icon_container()
        self.construct_live_rendered_icon_sprite()

    def construct_loading_indicator(self):
        self.loading_indicator = LoadingWheel(parent=self, align=uiconst.CENTER, display=True, idx=0)

    def on_live_rendered_icon_initialized(self):
        self.finished_loading = True
        self.loading_indicator.Hide()
        animations.FadeIn(self.live_rendered_icon)
        self.live_rendered_icon.on_rendered.disconnect(self.on_live_rendered_icon_initialized)

    def on_loading_sprite_fadeout_complete(self):
        self.loading_indicator.display = False

    def get_live_rendered_icon_skin_design(self):
        return None

    def construct_stack_lines(self):
        self.stack_lines_container = Container(name='stack_lines_container', parent=self, align=Align.TOTOP, opacity=0.5, height=6, display=False, padTop=-6)
        Fill(parent=self.stack_lines_container, align=Align.CENTERBOTTOM, color=self.stack_lines_color, opacity=0.5, pos=(0, 2, 150, 1))
        Fill(parent=self.stack_lines_container, align=Align.CENTERBOTTOM, color=self.stack_lines_color, opacity=0.3, pos=(0, 5, 134, 1))

    @property
    def stack_lines_color(self):
        return eveColor.WHITE

    def construct_content_container(self):
        self.content = Container(name='content', parent=self, align=Align.TOALL)

    def construct_stack_number(self):
        self.stack_numbers_container = ContainerAutoSize(name='stack_numbers_container', parent=self.content, align=Align.BOTTOMRIGHT, alignMode=Align.CENTER, display=False, top=36, minHeight=34, minWidth=38)
        self.stack_numbers_label = TextBody(name='stack_numbers_label', parent=self.stack_numbers_container, align=Align.CENTER, textAlign=Align.CENTER, padding=(16, 0, 8, 0))
        StretchSpriteHorizontal(name='stack_numbers_line', parent=self.stack_numbers_container, align=Align.TOALL, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/stack/corner_line.png', color=eveColor.WHITE, opacity=0.02, leftEdgeSize=8, rightEdgeSize=20)
        StretchSpriteHorizontal(name='stack_numbers_background', parent=self.stack_numbers_container, align=Align.TOALL, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/stack/corner_fill.png', color=eveColor.COAL_BLACK, leftEdgeSize=27, rightEdgeSize=11)

    def get_background_texture(self):
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/background.png'

    def get_mask_texture(self):
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/mask.png'

    def construct_live_rendered_icon_container(self):
        self.icon_container = Container(name='icon_container', parent=self.content, align=Align.CENTERTOP, width=168, height=198)
        Sprite(bgParent=self.icon_container, spriteEffect=SpriteEffect.MODULATE, textureSecondaryPath=self.get_background_texture(), texturePath=self.get_mask_texture())

    def construct_live_rendered_icon_sprite(self):
        self.live_rendered_icon = LiveIconSprite(name='live_rendered_icon', parent=self.icon_container, align=Align.TOALL, opacity=0.0, pickState=PickState.OFF, viewportWidth=self.icon_container.width, viewportHeight=self.icon_container.height, bg_texture_path=self.get_background_texture(), mask_texture_path=self.get_mask_texture(), glow=self.ship_glow)
        self.finished_loading = False
        self.live_rendered_icon.on_rendered.connect(self.on_live_rendered_icon_initialized)

    def construct_tier_indicator(self):
        self.tier_label = TextBody(name='tier_label', parent=self.content, align=Align.TOTOP_NOPUSH, textAlign=TextAlign.CENTER, text=self.get_skin_tier_text(), color=self.get_skin_tier_text_color(), shadowOffset=(0, 0), bold=True, padTop=6)
        if not self.show_tier_background():
            return
        self.tier_container = Container(name='tier_container', parent=self.content, align=Align.TOTOP_NOPUSH, opacity=0.5, width=self.default_width, height=29)
        self.tier_background = Sprite(name='tier_background', parent=self.tier_container, align=Align.TOTOP_NOPUSH, state=uiconst.UI_DISABLED, texturePath=self.get_skin_tier_texture(), outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=self.default_width, height=29)

    def show_tier_background(self):
        return True

    def get_skin_tier_level(self):
        return 1

    def get_skin_tier_text(self):
        return '{tier}'.format(tier=self.get_skin_tier_level())

    def get_skin_tier_text_color(self):
        return eveColor.BLACK

    def get_skin_tier_texture(self):
        tier_level = self.get_skin_tier_level()
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/tier/tier_{level}.png'.format(level=tier_level)

    def construct_top_line(self):
        self.top_left_corner = Sprite(name='top_left_corner', parent=self.content, align=Align.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/top_corner.png', outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=8, height=1)
        self.top_right_corner = Sprite(name='top_right_corner', parent=self.content, align=Align.TOPRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/top_corner.png', outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=8, height=1)
        self.top_line_container = Container(name='top_line_container', parent=self.content, align=Align.TOTOP_NOPUSH, opacity=0.5, width=self.default_width, height=1)
        self.top_line = Sprite(name='top_line', parent=self.top_line_container, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/top_line.png', outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=self.default_width, height=1)

    def construct_outline(self):
        self.outline = Sprite(name='outline', parent=self.content, state=uiconst.UI_DISABLED, texturePath=self.get_outline_texture(), color=self.get_outline_color(), outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=168, height=197, opacity=0.0)

    def get_outline_color(self):
        return eveColor.FOCUS_BLUE

    def get_outline_texture(self):
        return CardOutline.DEFAULT

    def construct_highlight(self):
        self.highlight_container = Container(name='highlight_container', parent=self.content, align=Align.TOBOTTOM_NOPUSH, opacity=0.0, height=4)
        self.highlight_bottom = Sprite(name='highlight_bottom', parent=self.highlight_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/highlight_bottom.png', outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=48, height=4)

    @property
    def highlight_offset(self):
        return 13

    def construct_label(self):
        self.name_label_container = Container(name='name_label_container', parent=self.content, align=Align.TOBOTTOM, width=self.default_width, height=18, padLeft=10, padRight=10, top=6)
        self.name_label = TextBody(name='name_label', parent=self.name_label_container, align=Align.CENTERLEFT, color=TextColor.SECONDARY, maxLines=1, autoFadeSides=16)

    def get_skin_name(self):
        return ''

    def update_live_icon_threaded(self):
        self.kill_update_live_icon_thread()
        self._update_live_icon_thread = uthread2.start_tasklet(self.update_live_icon)

    def update_live_icon(self):
        if self.destroyed:
            return
        self.live_rendered_icon.apply_skin_design(self.get_live_rendered_icon_skin_design())

    def update_threaded(self):
        self.kill_update_thread()
        self._update_thread = uthread2.start_tasklet(self.update)

    def update(self):
        if self.destroyed:
            return
        self.state = uiconst.UI_DISABLED
        self.update_stack_lines()
        self.update_stack_numbers()
        self.update_top_line()
        self.update_outline()
        self.update_highlight()
        self.update_tier_indicator()
        self.update_label()
        self.state = uiconst.UI_NORMAL

    def update_stack_lines(self):
        self.stack_lines_container.display = False

    def update_stack_numbers(self):
        self.stack_numbers_container.display = False

    def update_top_line(self):
        target_color = self.get_top_line_color()
        animations.SpColorMorphTo(self.top_line, self.top_line.GetRGBA(), target_color, self.ANIM_DURATION)
        self.update_line_corners()
        animations.FadeTo(self.top_line_container, self.top_line_container.opacity, self.get_top_line_opacity(), self.ANIM_DURATION)

    def get_top_line_opacity(self):
        if self.is_hovered or self.is_selected:
            return 1.0
        return 0.5

    def update_outline(self):
        if self.is_selected:
            target_opacity = 0.6
        elif self.is_hovered:
            target_opacity = 0.2
        else:
            target_opacity = 0.0
        animations.FadeTo(self.outline, self.outline.opacity, target_opacity, self.ANIM_DURATION)

    def update_line_corners(self):
        target_color = self.get_top_line_corner_color()
        animations.SpColorMorphTo(self.top_left_corner, self.top_left_corner.GetRGBA(), target_color, self.ANIM_DURATION)
        animations.SpColorMorphTo(self.top_right_corner, self.top_right_corner.GetRGBA(), target_color, self.ANIM_DURATION)

    def get_top_line_color(self):
        if self.is_selected:
            return eveColor.CRYO_BLUE
        return eveColor.WHITE

    def get_top_line_corner_color(self):
        if self.is_selected:
            return eveColor.CRYO_BLUE
        return eveColor.WHITE

    def get_highlight_color(self):
        return eveColor.WHITE

    def update_highlight(self):
        self.highlight_container.top = self.highlight_offset
        self.highlight_bottom.color = self.get_highlight_color()
        animations.FadeTo(self.highlight_container, self.highlight_container.opacity, self.get_highlight_opacity(), self.ANIM_DURATION)

    def get_highlight_opacity(self):
        if self.is_selected:
            return 1.0
        return 0.0

    def update_tier_indicator(self):
        if not self.show_tier_background():
            return
        if hasattr(self, 'tier_container'):
            target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
            animations.FadeTo(self.tier_container, self.tier_container.opacity, target_opacity, self.ANIM_DURATION)

    def update_label(self):
        color = self.get_label_color()
        animations.SpColorMorphTo(self.name_label, self.name_label.GetRGBA(), color, self.ANIM_DURATION)

    def get_label_color(self):
        color = TextColor.HIGHLIGHT if self.is_selected or self.is_hovered else TextColor.SECONDARY
        return color

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value):
        if self._is_selected == value:
            return
        self._is_selected = value
        if value:
            self._on_selected()
        else:
            self._on_deselected()
        self.update_threaded()

    def _on_selected(self):
        pass

    def _on_deselected(self):
        pass

    def OnMouseEnter(self, *args):
        self.is_hovered = True
        PlaySound('nanocoating_button_hover_play')
        self.update_threaded()

    def OnMouseExit(self, *args):
        self.is_hovered = False
        self.update_threaded()

    def OnClick(self, *args):
        self.is_selected = not self.is_selected
        self.on_click(self)


class BlankSkinCard(Container):
    default_width = cardConst.card_width
    default_height = cardConst.card_height

    def __init__(self, *args, **kwargs):
        super(BlankSkinCard, self).__init__(*args, **kwargs)
        self.construct_layout()

    def construct_layout(self):
        self.bg_sprite = Sprite(name='bg_sprite', parent=self, align=Align.CENTERTOP, texturePath=self.get_background_texture(), width=self.default_width, height=self.default_height)

    def get_background_texture(self):
        return 'res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/blank.png'
