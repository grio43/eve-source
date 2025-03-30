#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\corpStructureEntry.py
import eveformat.client
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst, TextColor
from carbonui.control.checkbox import Checkbox
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.cosmetics.structure import const as paintToolConst
from eve.client.script.ui.cosmetics.structure import paintToolSignals, paintToolSelections
from eve.client.script.ui.cosmetics.structure.components.corpStructureStatePanel import CorpStructureStatePanel
from eve.client.script.ui.structure.structureIcon import StructureIcon
from localization import GetByLabel
from structures import UPKEEP_STATE_FULL_POWER
ROW_HEIGHT = 32
STRUCTURE_ICON_SIZE = 16
STRUCTURE_NAME_PADDING = 4
PRICE_ICON_SIZE = 18
PRICE_ICON_PADDING = 8
LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)

class CorpStructureEntry(BaseListEntryCustomColumns):
    default_name = 'corpStructureEntry'

    def __init__(self, *args, **kwargs):
        super(CorpStructureEntry, self).__init__(*args, **kwargs)
        self._structure_data = self.node.controller
        if self._structure_data.is_eligible_for_application():
            self.background_color = tuple(eveColor.MATTE_BLACK[:3]) + (0.25,)
        else:
            self.background_color = tuple(eveColor.WARNING_ORANGE[:3]) + (0.05,)
        self._add_column_select()
        self._add_column_name()
        self._add_column_location()
        self._add_column_type()
        self._add_column_state()
        self._add_column_price()
        paintToolSignals.on_structure_state_loaded.connect(self._on_structure_state_loaded)
        paintToolSignals.on_structure_selection_changed.connect(self._on_structure_selection_changed)

    def Close(self):
        paintToolSignals.on_structure_state_loaded.disconnect(self._on_structure_state_loaded)
        paintToolSignals.on_structure_selection_changed.disconnect(self._on_structure_selection_changed)
        super(CorpStructureEntry, self).Close()

    def Load(self, *args):
        super(CorpStructureEntry, self).Load(*args)
        if not CorpStructureEntry.is_row_enabled(self._structure_data):
            self.node.panel.Disable()
            self._name_label.color = TextColor.DISABLED
            self._location_label.color = TextColor.DISABLED
            self._type_label.color = TextColor.DISABLED
            self._cost_label.color = TextColor.DISABLED

    @staticmethod
    def is_row_enabled(structure_data):
        return structure_data.upkeep_state == UPKEEP_STATE_FULL_POWER and structure_data.is_eligible_for_painting()

    @staticmethod
    def get_column_sort_values(structure_data):
        price = structure_data.get_price_for_duration(paintToolSelections.SELECTED_DURATION)
        return (structure_data.instance_id in paintToolSelections.SELECTED_STRUCTURES,
         _strip_system_name(structure_data.structure_name, structure_data.location_name).lower(),
         structure_data.location_name,
         structure_data.type_name,
         _get_state_sort_order(structure_data),
         price if price is not None else 0)

    @staticmethod
    def get_sort_value(node, _column_id, _sort_direction, idx = None):
        return (node.columnSortValues[idx],) + tuple(node.columnSortValues)

    @staticmethod
    def get_headers():
        return ['',
         GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Common/Location'),
         GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Common/Status'),
         GetByLabel('UI/Common/Cost')]

    def _add_column_select(self):
        column = self.AddColumnContainer()
        self._checkbox = Checkbox(name='checkbox', parent=column, align=uiconst.CENTER, callback=self._on_checkbox_clicked)
        self._checkbox.SetChecked(self._structure_data.instance_id in paintToolSelections.SELECTED_STRUCTURES, report=False)

    def _add_column_name(self):
        column = self.AddColumnContainer()
        column.name = 'column_name'
        column.state = uiconst.UI_NORMAL
        text = _strip_system_name(self._structure_data.structure_name, self._structure_data.location_name)
        content_wrapper = Container(name='content_wrapper', parent=column, align=uiconst.TOALL, hint=text)
        StructureIcon(name='structureIcon_%s' % text.replace('<br>', '_'), parent=content_wrapper, align=uiconst.CENTERLEFT, typeID=self._structure_data.type_id, structureID=self._structure_data.instance_id, pos=(0,
         0,
         STRUCTURE_ICON_SIZE,
         STRUCTURE_ICON_SIZE), state=uiconst.UI_DISABLED)
        self._name_label = EveLabelMedium(name='name_label', parent=content_wrapper, align=uiconst.CENTERLEFT, text=text, left=STRUCTURE_ICON_SIZE + STRUCTURE_NAME_PADDING, autoFadeSides=paintToolConst.LABEL_FADEOUT)

    def _add_column_location(self):
        column = self.AddColumnContainer()
        column.name = 'column_location'
        column.state = uiconst.UI_NORMAL
        text = _get_location_text(self._structure_data)
        content_wrapper = Container(name='content_wrapper', parent=column, align=uiconst.TOALL, hint=text)
        self._location_label = EveLabelMedium(name='location_label', parent=content_wrapper, align=uiconst.CENTERLEFT, text=text, autoFadeSides=paintToolConst.LABEL_FADEOUT)

    def _add_column_type(self):
        column = self.AddColumnContainer()
        column.name = 'column_type'
        column.state = uiconst.UI_NORMAL
        text = self._structure_data.type_name
        content_wrapper = Container(name='content_wrapper', parent=column, align=uiconst.TOALL, hint=text)
        self._type_label = EveLabelMedium(name='type_label', parent=content_wrapper, align=uiconst.CENTERLEFT, text=text, autoFadeSides=paintToolConst.LABEL_FADEOUT)

    def _add_column_state(self):
        column = self.AddColumnContainer()
        column.name = 'column_state'
        column.state = uiconst.UI_NORMAL
        self._state_panel = CorpStructureStatePanel(self._structure_data, parent=column)

    def _add_column_price(self):
        column = self.AddColumnContainer()
        column.name = 'column_price'
        column.state = uiconst.UI_NORMAL
        content_wrapper = Container(name='content_wrapper', parent=column, align=uiconst.TOALL)
        price = self._structure_data.get_price_for_duration(paintToolSelections.SELECTED_DURATION)
        if price is not None:
            icon_cont = Container(parent=content_wrapper, name='iconCont', align=uiconst.TOLEFT, width=PRICE_ICON_SIZE, left=2)
            Sprite(parent=icon_cont, name='icon', align=uiconst.CENTER, width=PRICE_ICON_SIZE, height=PRICE_ICON_SIZE, texturePath='res:/UI/Texture/Icons/evermarks.png')
        text = FmtAmt(price) if price is not None else '-'
        column.hint = text
        self._cost_label = EveLabelMedium(name='cost_label', parent=content_wrapper, align=uiconst.CENTERLEFT, text=text, left=PRICE_ICON_PADDING + PRICE_ICON_SIZE, autoFadeSides=paintToolConst.LABEL_FADEOUT)

    def _on_checkbox_clicked(self, *_args):
        selected = self._checkbox.GetValue()
        if selected:
            paintToolSelections.add_selected_structure(self._structure_data)
        else:
            paintToolSelections.remove_selected_structure(self._structure_data)
        self.sr.node.columnSortValues = CorpStructureEntry.get_column_sort_values(self._structure_data)

    @staticmethod
    def GetColWidths(_node, idx = None):
        widths = []
        if idx is None or idx == 0:
            w = 31
            widths.append(w)
        if idx is None or idx == 1:
            w = 208
            widths.append(w)
        if idx is None or idx == 2:
            w = 91
            widths.append(w)
        if idx is None or idx == 3:
            w = 89
            widths.append(w)
        if idx is None or idx == 4:
            w = 151
            widths.append(w)
        if idx is None or idx == 5:
            w = 116
            widths.append(w)
        return widths

    @classmethod
    def GetDynamicHeight(cls, node, width = None):
        return ROW_HEIGHT

    def _on_structure_state_loaded(self, structure_id):
        if structure_id == self._structure_data.instance_id:
            self.node.columnSortValues = self.get_column_sort_values(self._structure_data)

    def _on_structure_selection_changed(self, modifier, structure_data):
        if modifier == paintToolSignals.SELECTION_MODIFIER_CLEAR_ALL:
            self._checkbox.SetChecked(isChecked=False, report=False)
            return
        if not self._structure_data == structure_data:
            return
        self._checkbox.SetChecked(isChecked=modifier == paintToolSignals.SELECTION_MODIFIER_ADDED, report=False)


def _get_location_text(data):
    return '%s %s' % (eveformat.solar_system_security_status(data.location_id), data.location_name)


def _strip_system_name(name, location_name):
    if name.startswith(location_name):
        name = name.replace('%s - ' % location_name, '')
    return name


def _get_state_sort_order(structure_data):
    if not structure_data.is_eligible_for_painting():
        return -3
    elif structure_data.is_abandoned():
        return -2
    elif structure_data.is_low_power():
        return -1
    elif structure_data.license_id is not None:
        return 0
    elif structure_data.is_ready_for_painting():
        return 1
    else:
        return -10
