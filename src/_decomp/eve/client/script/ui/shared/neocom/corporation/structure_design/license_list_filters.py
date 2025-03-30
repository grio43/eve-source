#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\structure_design\license_list_filters.py
import eveicon
import evetypes
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.cosmetics.structure import licenseSignals
from localization import GetByLabel

class LicenseListFilters(Container):

    def __init__(self, type_filter, text_filter, *args, **kwargs):
        super(LicenseListFilters, self).__init__(*args, **kwargs)
        self._construct_layout(type_filter, text_filter)

    def _construct_layout(self, type_filter, text_filter):
        options = [(GetByLabel('UI/Personalization/PaintTool/StructureTypeFilterShowAll'), None)]
        options.extend([ (evetypes.GetName(x), x) for x in PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS ])
        self._structure_type_combo = Combo(parent=self, align=uiconst.TOLEFT, maxVisibleEntries=len(PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS), options=options, callback=self._on_structure_combo_select, nothingSelectedText=GetByLabel('UI/Personalization/PaintTool/StructureTypeFilterNoSelection'))
        if type_filter is not None:
            self._structure_type_combo.SetValue(type_filter)
        self._text_filter = QuickFilterEdit(parent=self, align=uiconst.TOALL, padLeft=20, callback=self._on_text_filter_edited, padRight=30)
        if text_filter is not None:
            self._text_filter.SetValue(text_filter, docallback=False)
        ButtonIcon(parent=self, name='reload_button', align=uiconst.TORIGHT, width=30, height=30, texturePath=eveicon.refresh, iconSize=16, func=self._on_reload_button_clicked, hint=GetByLabel('UI/Personalization/PaintTool/ReloadLicenses'))

    @property
    def is_type_filter_enabled(self):
        return self.structure_type_id is not None

    @property
    def structure_type_id(self):
        return self._structure_type_combo.GetValue()

    @property
    def is_text_filter_enabled(self):
        return self.search_text is not None and self.search_text != ''

    @property
    def search_text(self):
        return self._text_filter.GetValue()

    def _on_structure_combo_select(self, _combo, _key, value):
        licenseSignals.on_structure_filter_changed(value)

    def _on_text_filter_edited(self):
        licenseSignals.on_text_filter_changed(self._text_filter.GetValue())

    def _on_reload_button_clicked(self, *args):
        licenseSignals.on_reload_licenses_requested()
