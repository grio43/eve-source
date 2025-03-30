#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\pages\structureSelectionPage.py
import evetypes
import math
from carbonui import uiconst, ButtonVariant, TextColor, TextAlign
from carbonui.control.button import Button
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.dpi import ReverseScaleDpi
from carbon.client.script.environment.AudioUtil import PlaySound
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium, EveLabelLarge
from eve.client.script.ui.cosmetics.structure import const as paintToolConst
from eve.client.script.ui.cosmetics.structure import paintToolSelections
from eve.client.script.ui.cosmetics.structure.pages.basePage import BasePage
from localization import GetByLabel

class StructureCard(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_width = 115

    def __init__(self, type_id, icon_texture_path, glow_texture_path, callback = None, **kwargs):
        super(StructureCard, self).__init__(**kwargs)
        self._type_id = type_id
        self._icon_texture_path = icon_texture_path
        self._glow_texture_path = glow_texture_path
        self._callback = callback
        self._sprite_container = None
        self._selection_sprite = None
        self._name_label = None
        self._construct_layout()

    def _construct_layout(self):
        sprite_size = self.width
        self._sprite_container = Container(name='sprite_container', parent=self, align=uiconst.TOTOP, width=sprite_size, height=sprite_size)
        Sprite(name='icon_sprite', parent=self._sprite_container, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self._icon_texture_path)
        self._selection_sprite = Sprite(name='selection_sprite', parent=self._sprite_container, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath=self._glow_texture_path, opacity=0.0, color=eveColor.CRYO_BLUE)
        self._name_label = EveLabelLarge(name='name_label', parent=self, text=evetypes.GetName(self._type_id), textAlign=TextAlign.CENTER, align=uiconst.TOTOP)

    def _OnResize(self, *args):
        super(StructureCard, self)._OnResize(*args)
        sprite_size = ReverseScaleDpi(self.displayWidth)
        self._sprite_container.width = sprite_size
        self._sprite_container.height = sprite_size

    def OnClick(self, *args):
        super(StructureCard, self).OnClick(*args)
        self.select()
        PlaySound('nanocoating_hover_structure_play')
        if self._callback:
            self._callback(self, self._type_id)

    @property
    def type_id(self):
        return self._type_id

    def select(self):
        animations.FadeTo(self._selection_sprite, self._selection_sprite.opacity, 1.0, duration=0.2)
        animations.SpColorMorphTo(self._name_label, self._name_label.GetRGBA(), eveColor.CRYO_BLUE, 0.2)

    def deselect(self):
        animations.FadeTo(self._selection_sprite, self._selection_sprite.opacity, 0.0, duration=0.2)
        animations.SpColorMorphTo(self._name_label, self._name_label.GetRGBA(), TextColor.NORMAL, 0.2)


class StructureSelectionPage(BasePage):

    def __init__(self, **kwargs):
        self._structure_cards = []
        self._card_columns = 4
        self._card_spacing_x = 20
        self._card_spacing_y = 20
        self._label_area_prop_height = 0.12
        self._button_area_prop_height = self._label_area_prop_height
        self._label_container = None
        self._structure_grid = None
        self._select_button = None
        super(StructureSelectionPage, self).__init__(**kwargs)
        paintToolSelections.SELECTED_STRUCTURE_TYPE.on_change.connect(self._on_structure_selection_changed)

    def Close(self):
        super(StructureSelectionPage, self).Close()
        paintToolSelections.SELECTED_STRUCTURE_TYPE.on_change.disconnect(self._on_structure_selection_changed)

    def _construct_layout(self):
        self._construct_description_labels()
        self._construct_button_area()
        self._construct_structure_grid()

    def _construct_description_labels(self):
        label_area_container = Container(name='label_area_container', parent=self, align=uiconst.TOTOP_PROP, height=self._label_area_prop_height)
        self._label_container = ContainerAutoSize(name='label_container', parent=label_area_container, align=uiconst.CENTER)
        EveCaptionLarge(name='description_main_label', parent=self._label_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/SelectStructureCaption'), textAlign=TextAlign.CENTER)
        EveLabelMedium(name='description_sub_label', parent=self._label_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/SelectStructureInfo'), textAlign=TextAlign.CENTER)
        self._update_label_sizes()

    def _construct_button_area(self):
        button_area_container = Container(name='button_area_container', parent=self, align=uiconst.TOBOTTOM_PROP, height=self._button_area_prop_height)
        self._select_button = Button(name='select_button', parent=button_area_container, align=uiconst.CENTERBOTTOM, label=GetByLabel('UI/Personalization/PaintTool/StartDesigning'), variant=ButtonVariant.PRIMARY, func=self._on_select_button_clicked, enabled=False, padBottom=30)

    def _construct_structure_grid(self):
        grid_container = Container(name='grid_container', parent=self, align=uiconst.TOALL)
        self._structure_grid = FlowContainer(name='structure_grid', parent=grid_container, align=uiconst.CENTER, centerContent=True)
        for type_id in PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS:
            card = StructureCard(name='structure_card', parent=self._structure_grid, align=uiconst.NOALIGN, type_id=type_id, icon_texture_path=paintToolConst.get_structure_icon(type_id), glow_texture_path=paintToolConst.get_structure_glow_texture(type_id), callback=self._on_structure_card_select)
            self._structure_cards.append(card)

        self._update_grid_size()

    def _on_structure_card_select(self, _card, type_id):
        paintToolSelections.SELECTED_STRUCTURE_TYPE.set(type_id)
        self._select_button.enabled = True

    @staticmethod
    def _on_next_button_clicked(_button):
        paintToolSelections.SELECTED_PAGE.set(paintToolConst.DESIGN_CREATION_PAGE_ID)

    @staticmethod
    def _on_select_button_clicked(_button):
        paintToolSelections.SELECTED_PAGE.set(paintToolConst.DESIGN_CREATION_PAGE_ID)
        PlaySound('nanocoating_button_start_designing_play')

    def _on_structure_selection_changed(self, type_id):
        for card in self._structure_cards:
            if card.type_id == type_id:
                card.select()
            else:
                card.deselect()

    def _OnResize(self, *args):
        super(StructureSelectionPage, self)._OnResize(*args)
        self._update_label_sizes()
        self._update_grid_size()

    def _update_label_sizes(self):
        self._label_container.width = self.displayWidth

    def _update_grid_size(self):
        if self._structure_grid is None:
            return
        window_min_width, window_min_height = paintToolConst.WINDOW_MIN_SIZE
        if self.displayWidth > self.displayHeight:
            ratio = float(self.displayHeight) / float(window_min_height)
        else:
            ratio = float(self.displayWidth) / float(window_min_height)
        card_size = math.floor(ReverseScaleDpi(StructureCard.default_width) * ratio)
        card_spacing_x = math.floor(ReverseScaleDpi(self._card_spacing_x) * ratio)
        card_spacing_y = math.floor(ReverseScaleDpi(self._card_spacing_y) * ratio)
        for card in self._structure_cards:
            card.width = card_size

        self._structure_grid.contentSpacing = (card_spacing_x, card_spacing_y)
        self._structure_grid.width = card_size * self._card_columns + card_spacing_x * self._card_columns
