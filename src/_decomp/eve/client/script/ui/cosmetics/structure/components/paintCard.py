#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\paintCard.py
import carbonui
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.frame import Frame
from carbonui.primitives.fill import Fill
from localization import GetByMessageID
from signals import Signal
from carbonui import const as uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui import eveColor
from paints.data import dataLoader as paintsDataLoader
from carbonui.uianimations import animations
from eve.client.script.ui.cosmetics.structure import const as paintToolConst
CARD_HEIGHT = 101
CARD_WIDTH = 80
CARD_PAINT_WIDTH = CARD_WIDTH
CARD_PAINT_HEIGHT = 64
CARD_PAINT_ICON_SIZE = 64
SELECTED_FRAME_OPACITY = 1.0
UNSELECTED_FRAME_OPACITY = 0.0
SELECTED_FRAME_BRIGHTNESS = 0.5
UNSELECTED_FRAME_BRIGHTNESS = 0.0

class PaintCard(Container):
    on_paint_card_clicked = Signal()

    def __init__(self, paint_id, index, **kw):
        super(PaintCard, self).__init__(**kw)
        self._selected = False
        self._paint_id = paint_id
        self._name_nabel = None
        self.index = index
        self._construct_layout()

    def _construct_layout(self):
        center_cont = Container(name='centerCont', parent=self, align=uiconst.TOTOP, height=64)
        self._name_nabel = carbonui.TextDetail(name='nameLabel', parent=self, align=uiconst.TOTOP, padTop=5, padBottom=6, text=GetByMessageID(paintsDataLoader.get_paint_brand_name_id(self._paint_id)), maxFontSize=13)
        btn = ButtonIcon(name='iconBtn', parent=center_cont, align=uiconst.TORIGHT_NOPUSH, func=self._on_clicked, width=CARD_PAINT_ICON_SIZE, height=CARD_PAINT_ICON_SIZE, iconSize=CARD_PAINT_ICON_SIZE, texturePath=paintToolConst.get_paint_icon(self._paint_id))
        btn.SetIconColor(eveColor.WHITE)
        Fill(name='bgFill', parent=center_cont, align=uiconst.CENTER, width=CARD_PAINT_WIDTH, height=CARD_PAINT_HEIGHT, color=eveColor.WHITE, opacity=0.1)
        self._frame = Frame(parent=center_cont, name='frame', align=uiconst.TOALL, frameConst=uiconst.FRAME_BORDER2_CORNER0, color=eveColor.PRIMARY_BLUE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=UNSELECTED_FRAME_BRIGHTNESS, opacity=UNSELECTED_FRAME_OPACITY)

    def OnMouseEnter(self, *args):
        super(PaintCard, self).OnMouseEnter(*args)
        if not self._selected:
            self._show_frame(True)

    def OnMouseExit(self, *args):
        super(PaintCard, self).OnMouseExit(*args)
        if not self._selected:
            self._show_frame(False)

    def set_selected(self, selected):
        self._selected = selected
        self._show_frame(selected)

    def _show_frame(self, show):
        target_opacity = SELECTED_FRAME_OPACITY if show else UNSELECTED_FRAME_OPACITY
        target_glow_brightness = SELECTED_FRAME_BRIGHTNESS if show else UNSELECTED_FRAME_BRIGHTNESS
        animations.MorphScalar(self._frame, 'glowBrightness', startVal=self._frame.glowBrightness, endVal=target_glow_brightness, duration=0.25)
        animations.FadeTo(self._frame, startVal=self._frame.opacity, endVal=target_opacity, duration=0.25)

    def _on_clicked(self, *args):
        self.on_paint_card_clicked(self._paint_id)
        PlaySound('nanocoating_button_select_color_play')

    def is_label_visible(self, value):
        self._name_nabel.state = uiconst.UI_PICKCHILDREN if value else uiconst.UI_HIDDEN
        self.height = CARD_HEIGHT if value else CARD_PAINT_HEIGHT
