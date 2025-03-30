#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\corpStructureSelector.py
import evetypes
from carbonui import const as uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.cosmetics.structure import const as paintToolConst
from eve.client.script.ui.cosmetics.structure import paintToolSelections, paintToolSignals
from eve.client.script.ui.cosmetics.structure.components.corpCheckoutPanel import CorpCheckoutPanel
from eve.client.script.ui.cosmetics.structure.components.corpStructureList import CorpStructureList
from eve.client.script.ui.cosmetics.structure.corpStructureFilters import set_structure_type_filter, set_structure_text_filter
from localization import GetByLabel

class CorpStructureSelector(Container):

    def __init__(self, **kw):
        super(CorpStructureSelector, self).__init__(**kw)
        set_structure_type_filter(None, notify=False)
        set_structure_text_filter('', notify=False)
        self._construct_layout()
        paintToolSignals.on_structure_selection_changed.connect(self._on_structure_selection_changed)
        paintToolSignals.on_application_list_loaded.connect(self._on_application_list_loaded)

    def Close(self):
        paintToolSignals.on_structure_selection_changed.disconnect(self._on_structure_selection_changed)
        paintToolSignals.on_structure_selection_changed.disconnect(self._on_application_list_loaded)
        super(CorpStructureSelector, self).Close()

    def set_prices(self, catalogue):
        self._list.update_prices(catalogue)

    def update(self):
        self._corp_checkout_panel.update()
        self._list.reload()

    def _construct_layout(self):
        label_cont = ContainerAutoSize(parent=self, name='topLabelCont', align=uiconst.TOTOP)
        EveCaptionSmall(parent=label_cont, name='topLabel', align=uiconst.CENTERTOP, text=GetByLabel('UI/Personalization/PaintTool/SelectStructures'), padTop=24, padBottom=24, width=paintToolConst.get_design_application_page_width())
        self._construct_checkout_panel()
        self._construct_filters()
        self._construct_list()

    def _construct_checkout_panel(self):
        self._corp_checkout_panel = CorpCheckoutPanel(parent=self, align=uiconst.TOBOTTOM, padBottom=70)

    def _construct_filters(self):
        filters_cont = Container(parent=self, name='filtersCont', align=uiconst.TOTOP, height=32, padBottom=32)
        options = [(GetByLabel('UI/Personalization/PaintTool/StructureTypeFilterShowAll'), None)]
        options.extend([ (evetypes.GetName(x), x) for x in PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS ])
        checkbox_container = ContainerAutoSize(name='checkbox_container', parent=filters_cont, align=uiconst.TOLEFT)
        self._select_all_checkbox = Checkbox(name='select_all_checkbox', parent=checkbox_container, align=uiconst.CENTERLEFT, callback=self._on_select_all_toggle, text=GetByLabel('UI/Common/SelectAll'), hint=GetByLabel('UI/Personalization/PaintTool/SelectAll'))
        self._structure_type_combo = Combo(parent=filters_cont, align=uiconst.TOLEFT, maxVisibleEntries=len(PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS), options=options, callback=self._on_structure_combo_select, nothingSelectedText=GetByLabel('UI/Personalization/PaintTool/StructureTypeFilterNoSelection'), padLeft=20)
        self._text_filter = QuickFilterEdit(parent=filters_cont, align=uiconst.TOLEFT, width=183, padLeft=20, callback=self._on_text_filter)

    def _construct_list(self):
        Line(parent=self, align=uiconst.TOBOTTOM, color=tuple(eveColor.WHITE[:3]) + (0.3,), weight=2, padBottom=16)
        self._list = CorpStructureList(parent=self, name='scroll', align=uiconst.TOALL, padBottom=9)

    def _update_select_all_check_box(self):
        displayed_structures = self._list.displayed_corp_structures
        if len(displayed_structures) == 0:
            self._select_checkbox(False, enabled=False)
            return
        has_eligible_structures = False
        for structure_data in displayed_structures:
            if structure_data.is_eligible_for_application():
                has_eligible_structures = True
                break

        if not has_eligible_structures:
            self._select_checkbox(False, enabled=False)
            return
        for structure_data in displayed_structures:
            if not structure_data.is_eligible_for_application():
                continue
            if structure_data.instance_id not in paintToolSelections.SELECTED_STRUCTURES:
                self._select_checkbox(False)
                return
            self._select_checkbox(True)

    def _select_checkbox(self, value, enabled = True):
        self._select_all_checkbox.SetChecked(isChecked=value, report=False)
        self._select_all_checkbox.enabled = enabled

    def _on_select_all_toggle(self, checkbox):
        is_selected = checkbox.GetValue()
        paintToolSignals.on_structure_select_all_toggle(is_selected)

    def _on_structure_combo_select(self, _combo, _key, value):
        set_structure_type_filter(value)

    def _on_text_filter(self, *args):
        set_structure_text_filter(self._text_filter.GetValue().lower())

    def _on_structure_selection_changed(self, modifier, structure_data):
        self._update_select_all_check_box()

    def _on_application_list_loaded(self):
        self._update_select_all_check_box()
