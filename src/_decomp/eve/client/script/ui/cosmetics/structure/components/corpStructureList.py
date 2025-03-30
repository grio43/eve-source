#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\corpStructureList.py
from carbonui import const as uiconst
from carbonui.control.scroll import Scroll
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from cosmetics.client.structures import fittingSignals
from cosmetics.common.structures.exceptions import StructureTypeNotEligibleError
from eve.client.script.ui.control.scrollUtil import TabFinder
from eve.client.script.ui.cosmetics.structure import const as paintToolConst
from eve.client.script.ui.cosmetics.structure import paintToolSelections, paintToolSignals
from eve.client.script.ui.cosmetics.structure.components.corpStructureEntry import CorpStructureEntry
from eve.client.script.ui.cosmetics.structure.corpStructureData import CorpStructureData
from eve.client.script.ui.cosmetics.structure.corpStructureFilters import get_filters
from localization import GetByLabel

class CorpStructureList(Container):
    __notifyevents__ = ['OnUIScalingChange']

    def __init__(self, **kw):
        super(CorpStructureList, self).__init__(**kw)
        self._catalogue = None
        self._corp_structures = {}
        self._displayed_corp_structures = []
        self._structure_states_loading = []
        self._build_structure_dict()
        self._construct_layout()
        paintToolSignals.on_structure_filters_changed.connect(self._on_structure_filters_changed)
        paintToolSignals.on_duration_selection_changed.connect(self._on_duration_selection_changed)
        paintToolSignals.on_structure_state_loaded.connect(self._on_structure_state_loaded)
        paintToolSignals.on_structure_select_all_toggle.connect(self._on_structure_select_all_toggle)
        fittingSignals.on_structure_cosmetic_state_changed.connect(self._on_cosmetic_state_changed)

    def Close(self):
        paintToolSignals.on_structure_filters_changed.disconnect(self._on_structure_filters_changed)
        paintToolSignals.on_duration_selection_changed.disconnect(self._on_duration_selection_changed)
        paintToolSignals.on_structure_state_loaded.disconnect(self._on_structure_state_loaded)
        paintToolSignals.on_structure_select_all_toggle.disconnect(self._on_structure_select_all_toggle)
        fittingSignals.on_structure_cosmetic_state_changed.disconnect(self._on_cosmetic_state_changed)
        super(CorpStructureList, self).Close()

    def OnUIScalingChange(self, *_args):
        self._load()

    def reload(self):
        self._load()

    def update_prices(self, catalogue):
        self._catalogue = catalogue
        for structure_data in self._corp_structures.itervalues():
            try:
                structure_data.price_per_duration = catalogue.get_prices_for_structure_type_id(structure_data.type_id)
            except StructureTypeNotEligibleError:
                structure_data.price_per_duration = {}

        self._load()

    def _build_structure_dict(self):
        corp_structures = sm.GetService('structureDirectory').GetCorporationStructures()
        ids_to_prime = corp_structures.keys()
        cfg.evelocations.Prime(ids_to_prime)
        self._corp_structures = {}
        for structure_id, structure in corp_structures.iteritems():
            self._corp_structures[structure_id] = CorpStructureData(structure_id, structure['typeID'], structure['upkeepState'], structure['solarSystemID'])

    def _get_filtered_and_sorted_list(self):
        self._displayed_corp_structures = []
        self._structure_states_loading = []
        corp_structures = self._corp_structures.values()
        type_filter, text_filter = get_filters()
        scroll_list = []
        for corp_structure in corp_structures:
            if type_filter is not None and corp_structure.type_id != type_filter:
                continue
            if text_filter != '' and text_filter not in corp_structure.structure_name.lower() and text_filter not in corp_structure.location_name.lower():
                continue
            node = Bunch(controller=corp_structure, decoClass=CorpStructureEntry, columnSortValues=CorpStructureEntry.get_column_sort_values(corp_structure), charIndex=corp_structure.structure_name, GetSortValue=CorpStructureEntry.get_sort_value)
            scroll_list.append(node)
            self._displayed_corp_structures.append(corp_structure)
            self._structure_states_loading.append(corp_structure.instance_id)

        return (scroll_list, False)

    @property
    def displayed_corp_structures(self):
        return self._displayed_corp_structures

    def _construct_layout(self):
        self._scroll = Scroll(parent=self, name='scroll', align=uiconst.TOALL, minWidth=paintToolConst.get_design_application_page_width(), rowPadding=6)
        self._scroll.GetTabStops = self._get_tab_stops

    def _get_tab_stops(self, headertabs, idx = None):
        return TabFinder().GetTabStops(self._scroll.sr.nodes, headertabs, CorpStructureEntry, idx=idx)

    def _load(self):
        sort_by = self._scroll.GetSortBy()
        reverse_sort = self._scroll.GetSortDirection()
        self._scroll.ShowLoading()
        structure_list, something_filtered_out = self._get_filtered_and_sorted_list()
        if something_filtered_out:
            no_content_hint = GetByLabel('UI/Structures/Browser/NoStructuresFoundWithFilters')
        else:
            no_content_hint = GetByLabel('UI/Structures/Browser/NoStructuresFound')
        self._scroll.LoadContent(contentList=structure_list, headers=CorpStructureEntry.get_headers(), noContentHint=GetByLabel('UI/Structures/Browser/NoStructuresFound'))
        if not sort_by:
            sort_by = GetByLabel('UI/Common/Name')
        self._scroll.Sort(by=sort_by, reversesort=reverse_sort)
        self._scroll.HideLoading()
        headers = self._scroll.GetHeadersChildren()
        if len(headers) > 0:
            children_objects = headers._childrenObjects
            if len(children_objects) > 0:
                children_objects[0].state = uiconst.UI_DISABLED
        paintToolSignals.on_application_list_loaded()

    def _on_structure_filters_changed(self):
        self._load()

    def _on_duration_selection_changed(self):
        self._load()

    def _on_structure_state_loaded(self, structure_id):
        if structure_id in self._structure_states_loading:
            self._structure_states_loading.remove(structure_id)
        if len(self._structure_states_loading) == 0:
            sort_by = self._scroll.GetSortBy()
            reverse_sort = self._scroll.GetSortDirection()
            self._scroll.Sort(by=sort_by, reversesort=reverse_sort)

    def _on_structure_select_all_toggle(self, is_selected):
        corp_structures = self._corp_structures.values()
        for structure_data in corp_structures:
            if structure_data in self._displayed_corp_structures:
                if is_selected:
                    if structure_data.is_eligible_for_application():
                        paintToolSelections.add_selected_structure(structure_data)
                else:
                    paintToolSelections.remove_selected_structure(structure_data)

    def _on_cosmetic_state_changed(self, structure_id, _paintwork):
        for structure_data in self._displayed_corp_structures:
            if structure_id == structure_data.instance_id:
                self._load()
                break
