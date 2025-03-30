#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\paintToolSelections.py
from collections import OrderedDict
from carbonui.services.setting import CharSettingEnum
from cosmetics.common.structures.const import PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS
from eve.client.script.ui.cosmetics.structure.const import STRUCTURE_SELECTION_PAGE_ID, DESIGN_CREATION_PAGE_ID, DESIGN_APPLICATION_PAGE_ID, SUMMARY_PAGE_ID
import eve.client.script.ui.cosmetics.structure.paintToolSignals as paintToolSignals
from inventorycommon import const as invconst
from cosmetics.common.structures.fitting import StructurePaintwork
SELECTED_STRUCTURE_TYPE = CharSettingEnum('paintTool_selectedStructure', invconst.typeCitadelAstrahus, PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS)
SELECTED_PAGE = CharSettingEnum('paintTool_selectedPage', STRUCTURE_SELECTION_PAGE_ID, [STRUCTURE_SELECTION_PAGE_ID,
 DESIGN_CREATION_PAGE_ID,
 DESIGN_APPLICATION_PAGE_ID,
 SUMMARY_PAGE_ID])
SELECTED_PAINTWORK = StructurePaintwork()

def select_paint_slot(slot_id, paint_id):
    if SELECTED_PAINTWORK.get_slot(slot_index=slot_id) == paint_id:
        return
    SELECTED_PAINTWORK.set_slot(slot_index=slot_id, slot_value=paint_id)
    paintToolSignals.on_paintwork_selection_changed(slot_id, paint_id)


SELECTED_STRUCTURES = OrderedDict()

def clear_all_selected_structures():
    global SELECTED_STRUCTURES
    SELECTED_STRUCTURES = OrderedDict()
    paintToolSignals.on_structure_selection_changed(paintToolSignals.SELECTION_MODIFIER_CLEAR_ALL, None)


def add_selected_structure(structure_data):
    structure_id = structure_data.instance_id
    if structure_id and structure_id not in SELECTED_STRUCTURES:
        SELECTED_STRUCTURES[structure_id] = structure_data
        paintToolSignals.on_structure_selection_changed(paintToolSignals.SELECTION_MODIFIER_ADDED, structure_data)


def remove_selected_structure(structure_data):
    structure_id = structure_data.instance_id
    if structure_id and structure_id in SELECTED_STRUCTURES:
        SELECTED_STRUCTURES.pop(structure_id)
        paintToolSignals.on_structure_selection_changed(paintToolSignals.SELECTION_MODIFIER_REMOVED, structure_data)


SELECTED_DURATION = 0

def set_selected_duration(value):
    global SELECTED_DURATION
    SELECTED_DURATION = value
    paintToolSignals.on_duration_selection_changed()
