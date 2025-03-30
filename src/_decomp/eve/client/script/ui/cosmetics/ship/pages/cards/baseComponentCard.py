#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\baseComponentCard.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Align, TextBody, TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.cosmetics.ship.controls.rarityIndicator import RarityIndicator
from eve.client.script.ui.cosmetics.ship.pages.cards import cardConst
from signals import Signal

class ComponentCard(Container):
    default_state = uiconst.UI_NORMAL
    default_width = cardConst.card_width
    default_height = cardConst.card_height
    ANIM_DURATION = 0.2
    GLOW_AMOUNT = 0.4
    RARITY_ICON_SIZE = 32
    USAGE_ICON_SIZE = 36
    CORNER_ICON_OFFSET = 12

    def __init__(self, *args, **kwargs):
        super(ComponentCard, self).__init__(*args, **kwargs)
        self._is_selected = False
        self.is_hovered = False
        self.on_click = Signal('on_click')
        self.construct_layout()

    def construct_layout(self):
        self.construct_label()
        self.construct_highlight()
        self.construct_top_line()
        self.construct_rarity_indicator()
        self.construct_usage_indicator()
        self.construct_icon()
        self.construct_background()
        self.update()

    def construct_background(self):
        self.background_sprite = Sprite(name='background_sprite', parent=self, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, texturePath=self.get_background_texture(), color=eveColor.SMOKE_BLUE, opacity=0.2, width=self.default_width, height=self.default_height)
        self.hover_sprite = Sprite(name='hover_sprite', parent=self, align=Align.CENTERTOP, state=uiconst.UI_DISABLED, texturePath=self.get_background_texture(), color=eveColor.SMOKE_BLUE, opacity=0.0, width=self.default_width, height=self.default_height)

    def get_background_texture(self):
        return None

    def construct_icon(self):
        self.icon_container = ContainerAutoSize(name='icon_container', parent=self, align=Align.CENTER, top=-23)

    def construct_rarity_indicator(self):
        self.rarity_indicator = RarityIndicator(name='rarity_indicator', parent=self, align=Align.TOPLEFT, rarity=self.get_rarity(), opacity=0.5, top=self.CORNER_ICON_OFFSET, left=self.CORNER_ICON_OFFSET)

    def get_rarity(self):
        return None

    def construct_usage_indicator(self):
        pass

    def has_unlimited_uses(self):
        return False

    def get_uses_remaining(self):
        return None

    def construct_top_line(self):
        self.top_left_corner = Sprite(name='top_left_corner', parent=self, align=Align.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/top_corner.png', outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=8, height=1)
        self.top_right_corner = Sprite(name='top_right_corner', parent=self, align=Align.TOPRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/top_corner.png', outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=8, height=1)
        self.top_line_container = Container(name='top_line_container', parent=self, align=Align.TOTOP_NOPUSH, opacity=0.5, width=self.default_width, height=1)
        self.top_line = Sprite(name='top_line', parent=self.top_line_container, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/top_line.png', outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, color=eveColor.WHITE, width=self.default_width, height=1)

    def construct_highlight(self):
        self.highlight_container = Container(name='highlight_container', parent=self, align=Align.TOBOTTOM_NOPUSH, opacity=0.0, height=4, top=8)
        self.highlight_bottom = Sprite(name='highlight_bottom', parent=self.highlight_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/cards/skin_design/highlight_bottom.png', outputMode=uiconst.OutputMode.COLOR_AND_GLOW, glowBrightness=self.GLOW_AMOUNT, width=48, height=4)

    def construct_label(self):
        self.name_label_container = Container(name='name_label_container', parent=self, align=Align.TOBOTTOM, width=self.default_width, height=18, padLeft=10, padRight=10, top=10)
        self.name_label = TextBody(name='name_label', parent=self.name_label_container, align=Align.CENTERLEFT, text=self.get_component_name(), color=TextColor.SECONDARY, maxLines=1, autoFadeSides=16)

    def get_component_name(self):
        return ''

    def update(self):
        self.update_hover_sprite()
        self.update_top_line()
        self.update_highlight()
        self.update_rarity_indicator()
        self.update_label()

    def update_hover_sprite(self):
        target_opacity = 0.4 if self.is_selected or self.is_hovered else 0.0
        animations.FadeTo(self.hover_sprite, self.hover_sprite.opacity, target_opacity, self.ANIM_DURATION)

    def update_top_line(self):
        target_color = self.get_top_line_color()
        animations.SpColorMorphTo(self.top_line, self.top_line.GetRGBA(), target_color, self.ANIM_DURATION)
        animations.SpColorMorphTo(self.top_left_corner, self.top_left_corner.GetRGBA(), target_color, self.ANIM_DURATION)
        animations.SpColorMorphTo(self.top_right_corner, self.top_right_corner.GetRGBA(), target_color, self.ANIM_DURATION)
        animations.FadeTo(self.top_line_container, self.top_line_container.opacity, self.get_top_line_opacity(), self.ANIM_DURATION)

    def update_highlight(self):
        self.highlight_bottom.color = self.get_highlight_color()
        animations.FadeTo(self.highlight_container, self.highlight_container.opacity, self.get_highlight_opacity(), self.ANIM_DURATION)

    def get_top_line_color(self):
        if self.is_selected:
            return eveColor.CRYO_BLUE
        return eveColor.WHITE

    def get_top_line_opacity(self):
        if self.is_hovered or self.is_selected:
            return 1.0
        return 0.5

    def get_highlight_color(self):
        return eveColor.CRYO_BLUE

    def get_highlight_opacity(self):
        if self.is_selected:
            return 1.0
        return 0.0

    def update_rarity_indicator(self):
        target_opacity = 1.0 if self.is_hovered or self.is_selected else 0.5
        animations.FadeTo(self.rarity_indicator, self.rarity_indicator.opacity, target_opacity, self.ANIM_DURATION)

    def update_label(self):
        target_color = TextColor.HIGHLIGHT if self.is_selected or self.is_hovered else TextColor.SECONDARY
        animations.SpColorMorphTo(self.name_label, self.name_label.GetRGBA(), target_color, self.ANIM_DURATION)

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
        self.update()

    def _on_selected(self):
        pass

    def _on_deselected(self):
        pass

    def OnMouseEnter(self, *args):
        self.is_hovered = True
        PlaySound('nanocoating_button_hover_play')
        self.update()

    def OnMouseExit(self, *args):
        self.is_hovered = False
        self.update()

    def OnClick(self, *args):
        self.is_selected = not self.is_selected
        self.on_click(self)


class BlankComponentCard(Container):
    default_width = cardConst.card_width
    default_height = cardConst.card_height

    def __init__(self, *args, **kwargs):
        super(BlankComponentCard, self).__init__(*args, **kwargs)
        self.construct_layout()

    def construct_layout(self):
        self.bg_sprite = Sprite(name='bg_sprite', parent=self, align=Align.CENTERTOP, texturePath=self.get_background_texture(), width=self.default_width, height=self.default_height)

    def get_background_texture(self):
        return None
