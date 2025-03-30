#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\paintSlot.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.vectorarc import VectorArc
from signals import Signal
from carbonui import const as uiconst
from carbonui.uianimations import animations
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
import eve.client.script.ui.cosmetics.structure.paintToolSelections as paintToolSelections
from eve.client.script.ui.cosmetics.structure import const as paintToolConst
from localization import GetByLabel, GetByMessageID
from paints.data import dataLoader as paintsDataLoader
SLOT_SIZE = 64
SELECTED_INDICATOR_WIDTH = 4
SELECTED_INDICATOR_HEIGHT = 8
SELECTED_INDICATOR_PADDING = 4
SELECTED_COLOR = eveColor.CRYO_BLUE
HOVER_ON_EMPTY_COLOR = tuple(eveColor.WHITE[:3]) + (0.6,)
FILLED_COLOR = eveColor.LEAFY_GREEN
EMPTY_COLOR = tuple(eveColor.WHITE[:3]) + (0.1,)

class PaintSlot(Container):
    default_state = uiconst.UI_NORMAL
    on_paint_slot_clicked = Signal()

    def __init__(self, slot_id, **kwargs):
        super(PaintSlot, self).__init__(**kwargs)
        self.hint = GetByLabel(paintToolConst.PAINT_SLOT_NAMES[slot_id])
        self.slot_id = slot_id
        self._paint_id = None
        self._hovered = False
        self._selected = False
        self._construct_layout()
        self.update_selected_paint()
        self.set_selected(False, animate=False)

    def _construct_layout(self):
        selected_indicator_cont = Container(parent=self, name='selectedIndicatorCont', align=uiconst.TORIGHT, width=SELECTED_INDICATOR_WIDTH, padLeft=SELECTED_INDICATOR_PADDING, padRight=SELECTED_INDICATOR_PADDING)
        self._selected_indicator = Sprite(parent=selected_indicator_cont, align=uiconst.CENTER, width=SELECTED_INDICATOR_WIDTH, height=SELECTED_INDICATOR_HEIGHT, texturePath='res:/UI/Texture/classes/paintTool/paintSlots/selection_arrow.png')
        btn_cont = Container(parent=self, name='btnCont')
        self._circle = VectorArc(name='circle', parent=btn_cont, align=uiconst.CENTER, radius=0.5 * SLOT_SIZE, lineWidth=1, fill=False, glowBrightness=0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW)
        Sprite(name='iconSprite', parent=btn_cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=32, height=32, texturePath='res:/UI/Texture/classes/paintTool/paintSlots/%s.png' % self.slot_id)
        self._color_sprite = Sprite(name='colorSprite', parent=btn_cont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=56, height=56, texturePath='res:/UI/Texture/classes/paintTool/paintSlots/bg_white.png')

    def OnClick(self, *args):
        self.on_paint_slot_clicked(self.slot_id)
        PlaySound(paintToolConst.PAINT_SLOT_CLICK_SOUND_EVENTS[self.slot_id])

    def OnMouseEnter(self, *args):
        self._hovered = True
        self._update_circle()
        PlaySound('nanocoating_button_hover_play')

    def OnMouseExit(self, *args):
        self._hovered = False
        self._update_circle()

    def _update_icon(self):
        if self._paint_id is not None:
            target_color = paintsDataLoader.get_material_rgba(self._paint_id)
            target_opacity = 0.5
        else:
            target_color = eveColor.BLACK
            target_opacity = 0.2
        animations.SpColorMorphTo(self._color_sprite, self._color_sprite.GetRGBA(), target_color, 0.25)
        animations.FadeTo(self._color_sprite, self._color_sprite.opacity, target_opacity, 0.25)

    def _update_circle(self):
        target_brightness = 1.0 if self._hovered else 0.7
        if self._selected:
            target_color = SELECTED_COLOR
        elif self._paint_id:
            target_color = SELECTED_COLOR
        elif self._hovered:
            target_color = HOVER_ON_EMPTY_COLOR
        else:
            target_color = EMPTY_COLOR
        animations.MorphScalar(self._circle, 'glowBrightness', self._circle.glowBrightness, target_brightness, duration=0.25)
        animations.SpColorMorphTo(self._circle, self._circle.GetRGBA(), target_color, 0.25)

    def _update_selected_indicator(self, animate = True):
        target_opacity = 1.0 if self._selected else 0.0
        if not animate:
            self._selected_indicator.opacity = target_opacity
        else:
            animations.FadeTo(self._selected_indicator, self._selected_indicator.opacity, target_opacity, duration=0.25)

    def _update_hint(self):
        if self._paint_id is not None:
            self.hint = GetByMessageID(paintsDataLoader.get_paint_brand_name_id(self._paint_id))
        else:
            self.hint = GetByLabel(paintToolConst.PAINT_SLOT_NAMES[self.slot_id])

    def set_selected(self, selected, animate = True):
        self._selected = selected
        self._update_selected_indicator(animate=animate)
        self._update_circle()

    def update_selected_paint(self):
        self._paint_id = paintToolSelections.SELECTED_PAINTWORK.get_slot(self.slot_id)
        self._update_icon()
        self._update_circle()
        self._update_hint()
