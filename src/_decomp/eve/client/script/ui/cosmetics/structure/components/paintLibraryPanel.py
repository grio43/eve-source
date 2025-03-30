#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\paintLibraryPanel.py
import uthread2
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.line import Line
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.cosmetics.structure import const as paintToolConst
from eve.client.script.ui.cosmetics.structure import paintToolSelections
from eve.client.script.ui.cosmetics.structure.components.paintCard import PaintCard, CARD_WIDTH, CARD_HEIGHT
from eve.client.script.ui.util.uix import GetTextHeight
from localization import GetByLabel
from paints.data import dataLoader as paintsDataLoader
CONTENT_SPACING = 8
HEADER_ID_MATTE = 'matte'
HEADER_ID_COATED = 'coated'
HEADER_ID_SATIN = 'satin'

class PaintLibraryPanel(Container):

    def __init__(self, target_slot, **kw):
        self._target_slot_id = None
        self._selected_paint_id = None
        self._paint_cards = {}
        self._name_checkbox = None
        self._loading_thread = None
        self.set_target_slot(target_slot)
        super(PaintLibraryPanel, self).__init__(**kw)
        self._construct_layout()

    def Close(self):
        if self._loading_thread is not None:
            self._loading_thread.kill()
            self._loading_thread = None
        for paint_card in self._paint_cards.itervalues():
            paint_card.on_paint_card_clicked.disconnect(self._on_paint_card_clicked)

        super(PaintLibraryPanel, self).Close()

    def _construct_layout(self):
        top_cont = ContainerAutoSize(parent=self, name='topCont', align=uiconst.TOTOP, padBottom=8, padRight=24)
        self._slot_label = EveLabelLarge(parent=top_cont, name='slotLabel', align=uiconst.TOTOP, padBottom=8, color=eveColor.WHITE)
        Line(parent=top_cont, align=uiconst.TOTOP, color=eveColor.WHITE, opacity=0.1, padBottom=8)
        self._name_checkbox = Checkbox(parent=top_cont, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/PaintLibrary/ShowNames'), checked=settings.user.ui.Get('paintLibraryPanel_showNames', True), callback=self._on_name_checkbox_change, padBottom=8)
        matte_text = GetByLabel('UI/Personalization/PaintTool/PaintLibrary/Finishes/Matte')
        coated_text = GetByLabel('UI/Personalization/PaintTool/PaintLibrary/Finishes/Coated')
        satin_text = GetByLabel('UI/Personalization/PaintTool/PaintLibrary/Finishes/Satin')
        font_size = EveLabelLarge.default_fontsize
        font_style = EveLabelLarge.default_fontStyle
        matte_text_height = GetTextHeight(matte_text, fontsize=font_size, fontStyle=font_style, width=CARD_WIDTH)
        coated_text_height = GetTextHeight(coated_text, fontsize=font_size, fontStyle=font_style, width=CARD_WIDTH)
        satin_text_height = GetTextHeight(satin_text, fontsize=font_size, fontStyle=font_style, width=CARD_WIDTH)
        header_height = max(max(matte_text_height, coated_text_height), satin_text_height)
        self._headers_cont = Container(parent=top_cont, name='headersCont', align=uiconst.TOTOP, height=header_height)
        self._add_header(HEADER_ID_MATTE, matte_text)
        self._add_header(HEADER_ID_COATED, coated_text)
        self._add_header(HEADER_ID_SATIN, satin_text)
        self._scroll_cont = ScrollContainer(parent=self, name='scrollCont')
        self._cards_cont = FlowContainer(name='cardsLibraryCont', parent=self._scroll_cont, align=uiconst.TOTOP, contentSpacing=(CONTENT_SPACING, CONTENT_SPACING), padBottom=8)
        self._loading_thread = uthread2.StartTasklet(self._load_paints_thread)

    def _add_header(self, header_id, label):
        EveLabelLarge(parent=self._headers_cont, name='label_%s' % header_id, align=uiconst.TOLEFT, text=label, width=CARD_WIDTH, padRight=CONTENT_SPACING)

    def _load_paints_thread(self):
        try:
            for i, paint_id in enumerate(self._get_sorted_paints()):
                paint_card = PaintCard(parent=self._cards_cont, name='paint_card_%s' % paint_id, align=uiconst.NOALIGN, paint_id=paint_id, width=CARD_WIDTH, height=CARD_HEIGHT, index=i)
                self._paint_cards[paint_id] = paint_card
                paint_card.on_paint_card_clicked.connect(self._on_paint_card_clicked)

        finally:
            self._loading_thread = None
            self._update_card_names()

    def _get_sorted_paints(self):

        def _get_paint_order(paint_id):
            material_name = paintsDataLoader.get_paint_material_name(paint_id)
            finish = paintsDataLoader.get_paint_finish(paint_id)
            if finish == 'matt':
                return 1
            if finish == 'coated':
                return 2
            if finish == 'satin':
                return 3

        def _sort_hues(val):
            return val['hue_value']

        def _sort_paints(val):
            return val['order']

        paints = paintsDataLoader.get_paint_ids()
        paint_by_hues = []
        for hue_id in paintsDataLoader.get_hue_category_ids():
            paint_by_hues.append({'hue_id': hue_id,
             'hue_value': paintsDataLoader.get_hue_category_hue(hue_id),
             'paints': sorted([ {'paint_id': p,
                        'material_name': paintsDataLoader.get_paint_material_name(p),
                        'finish': paintsDataLoader.get_paint_finish(p),
                        'order': _get_paint_order(p)} for p in paints if paintsDataLoader.get_paint_hue_category(p) == hue_id ], key=_sort_paints)})

        paint_by_hues.sort(key=_sort_hues)
        sorted_paints = []
        for hue_dict in paint_by_hues:
            grouped_paints = {}
            for paint in hue_dict['paints']:
                hsb_suffix = '_'.join(paint['material_name'].split('_')[-3:])
                if hsb_suffix not in grouped_paints:
                    grouped_paints[hsb_suffix] = [paint]
                else:
                    grouped_paints[hsb_suffix].append(paint)

            for group in grouped_paints.values():
                group.sort(key=lambda p: p['order'])
                sorted_paints.extend([ p['paint_id'] for p in group ])

        return sorted_paints

    def set_target_slot(self, slot_id):
        self._target_slot_id = slot_id
        if self._target_slot_id is not None:
            self._selected_paint_id = paintToolSelections.SELECTED_PAINTWORK.get_slot(self._target_slot_id)
            slot_name = GetByLabel(paintToolConst.PAINT_SLOT_NAMES[self._target_slot_id])
            self._slot_label.text = GetByLabel('UI/Personalization/PaintTool/PaintLibrary/PaintSelection', slotName=slot_name)
            if self._selected_paint_id is not None:
                self._scroll_to(self._selected_paint_id)
        else:
            self._selected_paint_id = None
            self._slot_label = ''
        for paint_id, paint_card in self._paint_cards.iteritems():
            paint_card.set_selected(paint_id == self._selected_paint_id)

    def _on_paint_card_clicked(self, paint_id):
        if self._selected_paint_id:
            self._paint_cards[self._selected_paint_id].set_selected(False)
        if paint_id == self._selected_paint_id:
            self._selected_paint_id = None
        else:
            self._selected_paint_id = paint_id
            if self._selected_paint_id:
                self._paint_cards[self._selected_paint_id].set_selected(True)
        paintToolSelections.select_paint_slot(slot_id=self._target_slot_id, paint_id=self._selected_paint_id)

    def _scroll_to(self, paint_id):
        paint_card = self._paint_cards.get(paint_id, None)
        if paint_card:
            scroll_position = float(paint_card.index) / float(len(self._paint_cards))
            if scroll_position < 0.1:
                scroll_position = 0.0
            elif scroll_position > 0.9:
                scroll_position = 1.0
            self._scroll_cont.ScrollToVertical(scroll_position)

    def _update_card_names(self):
        if not self._name_checkbox:
            return
        selected = self._name_checkbox.GetValue()
        settings.user.ui.Set('paintLibraryPanel_showNames', selected)
        for paint_card in self._paint_cards.values():
            paint_card.is_label_visible(selected)

        self._scroll_cont.UpdateAlignment()

    def _on_name_checkbox_change(self, *args):
        self._update_card_names()
        self._scroll_to(self._selected_paint_id)
