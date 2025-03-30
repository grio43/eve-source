#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\pages\designCreationPage.py
import evetypes
from carbonui import AxisAlignment
from carbonui import const as uiconst, ButtonVariant
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS, StructurePaintSlot, SLOT_ORDER
from eve.client.script.ui.cosmetics.structure import const as paintToolConst
import eve.client.script.ui.cosmetics.structure.paintToolSelections as paintToolSelections
from eve.client.script.ui.cosmetics.structure.components.paintLibraryPanel import PaintLibraryPanel
from eve.client.script.ui.cosmetics.structure.components import paintSlot
from eve.client.script.ui.cosmetics.structure.components.structureSelector import StructureNameSelector
from eve.client.script.ui.cosmetics.structure.components.navigationButtons import BackButton
from eve.client.script.ui.cosmetics.structure.paintToolSignals import on_paintwork_selection_changed
from eve.client.script.ui.cosmetics.structure.components.previewScene import PreviewPanel
from eve.client.script.ui.cosmetics.structure.pages.basePage import BasePage
from localization import GetByLabel
CAROUSEL_CONT_HEIGHT = 100
SLOT_PADDING = 22
RIGHT_SIDE_WIDTH = 306

class DesignCreationPage(BasePage):

    def __init__(self, **kw):
        self._slots = {}
        self._selected_slot = None
        paintToolSelections.SELECTED_PAINTWORK.clear()
        super(DesignCreationPage, self).__init__(**kw)
        on_paintwork_selection_changed.connect(self._on_paint_selection_changed)
        paintToolSelections.SELECTED_STRUCTURE_TYPE.on_change.connect(self._on_structure_selection_changed)
        self._on_structure_selection_changed(paintToolSelections.SELECTED_STRUCTURE_TYPE.get())
        self._select_slot(StructurePaintSlot.PRIMARY)
        self._update_apply_button()

    def Close(self):
        super(DesignCreationPage, self).Close()
        for slot_cont in self._slots.itervalues():
            slot_cont.on_paint_slot_clicked.disconnect(self._on_paint_slot_clicked)

        on_paintwork_selection_changed.disconnect(self._on_paint_selection_changed)
        paintToolSelections.SELECTED_STRUCTURE_TYPE.on_change.disconnect(self._on_structure_selection_changed)

    def _open_page(self):
        self._live_preview.display = True
        super(DesignCreationPage, self)._open_page()

    def _close_page(self):
        self._live_preview.display = False
        super(DesignCreationPage, self)._close_page()

    def _construct_layout(self):
        Fill(bgParent=self, name='bgFill', color=(0.0, 0.0, 0.0, 0.4), align=uiconst.TORIGHT, width=RIGHT_SIDE_WIDTH)
        self._right_side_cont = Container(parent=self, name='rightSideCont', align=uiconst.TORIGHT, width=RIGHT_SIDE_WIDTH, padTop=37, padBottom=54)
        self._create_nav_button()
        self._create_apply_button()
        self._create_paint_library()
        self._create_paint_slots()
        self._create_structure_carousel()
        self._create_live_preview()

    def _create_paint_library(self):
        self._paint_library = PaintLibraryPanel(parent=self._right_side_cont, name='paintLibrary', align=uiconst.TOALL, padRight=2, padLeft=24, padBottom=26, target_slot=self._selected_slot)

    def _create_nav_button(self):
        BackButton(name='back_button', parent=self, align=uiconst.TOPLEFT, left=23, top=23, onClick=self._on_back_clicked)

    def _create_apply_button(self):
        self._apply_button = Button(parent=self._right_side_cont, name='applyButton', align=uiconst.TOBOTTOM, height=40, label=GetByLabel('UI/Personalization/PaintTool/PaintLibrary/Apply'), variant=ButtonVariant.PRIMARY, func=self._on_next_clicked, padLeft=24, padRight=24)

    def _create_structure_carousel(self):
        structure_carousel_cont = Container(parent=self, name='structureCarouselCont', align=uiconst.TOBOTTOM_NOPUSH, height=CAROUSEL_CONT_HEIGHT)
        self._structure_selector = StructureNameSelector(name='structureNameSelector', parent=structure_carousel_cont, options=[ (evetypes.GetName(idx), idx) for idx in PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS ], contentAlignment=AxisAlignment.CENTER, contentSpacing=(4, 4), centerContent=True, callback=self._on_structure_select)

    def _create_paint_slots(self):
        paint_slots_cont = Container(parent=self, name='paintSlotsCont', align=uiconst.TORIGHT_NOPUSH, width=paintSlot.SLOT_SIZE + paintSlot.SELECTED_INDICATOR_WIDTH + 2 * paintSlot.SELECTED_INDICATOR_PADDING)
        center_cont = ContainerAutoSize(parent=paint_slots_cont, name='centerCont', align=uiconst.CENTER, width=paintSlot.SLOT_SIZE + paintSlot.SELECTED_INDICATOR_WIDTH + 2 * paintSlot.SELECTED_INDICATOR_PADDING)
        for i, slot_id in enumerate(SLOT_ORDER):
            paint_slot = paintSlot.PaintSlot(name='paintSlot_%s' % slot_id, parent=center_cont, align=uiconst.TOTOP, height=paintSlot.SLOT_SIZE, slot_id=slot_id, padTop=SLOT_PADDING if i > 0 else 0)
            paint_slot.on_paint_slot_clicked.connect(self._on_paint_slot_clicked)
            self._slots[slot_id] = paint_slot

    def _create_live_preview(self):
        self._live_preview = PreviewPanel(name='preview_panel', parent=self)
        self._live_preview.display = False

    def _on_paint_slot_clicked(self, slot_id):
        self._select_slot(slot_id)

    def _select_slot(self, selected_slot_id):
        for slot_id, slot in self._slots.iteritems():
            self._slots[slot_id].set_selected(slot_id == selected_slot_id)

        self._selected_slot = selected_slot_id
        self._paint_library.set_target_slot(self._selected_slot)

    def _update_apply_button(self):
        self._apply_button.enabled = any([ x is not None for x in paintToolSelections.SELECTED_PAINTWORK.get_slot_values() ])

    @staticmethod
    def _on_structure_select(_combo, _key, value):
        paintToolSelections.SELECTED_STRUCTURE_TYPE.set(value)

    def _on_structure_selection_changed(self, type_id):
        self._structure_selector.select_by_value(type_id, notify=False)

    def _on_paint_selection_changed(self, _slot_id, _paint_id):
        if _slot_id in self._slots:
            self._slots[_slot_id].update_selected_paint()
        self._live_preview.update(self._structure_selector.get_value(), fit_in_view=False)
        self._update_apply_button()

    @staticmethod
    def _on_back_clicked():
        paintToolSelections.SELECTED_PAGE.set(paintToolConst.STRUCTURE_SELECTION_PAGE_ID)

    @staticmethod
    def _on_next_clicked(_btn):
        paintToolSelections.SELECTED_PAGE.set(paintToolConst.DESIGN_APPLICATION_PAGE_ID)
