#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\const.py
import evetypes
from cosmetics.common.structures.const import StructurePaintSlot
from paints.data.const import PAINT_RARITY_COMMON, PAINT_RARITY_UNCOMMON, PAINT_RARITY_RARE
from structures import UPKEEP_STATE_FULL_POWER, UPKEEP_STATE_LOW_POWER, UPKEEP_STATE_ABANDONED
STRUCTURE_SELECTION_PAGE_ID = 0
DESIGN_CREATION_PAGE_ID = 1
DESIGN_APPLICATION_PAGE_ID = 2
SUMMARY_PAGE_ID = 3
WINDOW_MIN_SIZE = (1030, 650)
LABEL_FADEOUT = 25

def get_structure_icon(type_id):
    return 'res:/UI/Texture/classes/paintTool/structureIcons/%s_512_tr.png' % evetypes.GetGraphicID(type_id)


def get_structure_glow_texture(type_id):
    return 'res:/UI/Texture/classes/paintTool/structureIcons/glows/%s_512_tr.png' % evetypes.GetGraphicID(type_id)


def get_paint_icon(paint_id):
    return 'res:/UI/Texture/classes/paintTool/paintIcons/%s.png' % paint_id


PAINT_RARITY_NAMES = {PAINT_RARITY_COMMON: 'UI/Personalization/Paints/Rarity/Common',
 PAINT_RARITY_UNCOMMON: 'UI/Personalization/Paints/Rarity/Uncommon',
 PAINT_RARITY_RARE: 'UI/Personalization/Paints/Rarity/Rare'}
PAINT_SLOT_NAMES = {StructurePaintSlot.PRIMARY: 'UI/Personalization/Slots/Primary',
 StructurePaintSlot.SECONDARY: 'UI/Personalization/Slots/Secondary',
 StructurePaintSlot.DETAILING: 'UI/Personalization/Slots/Detailing'}
PAINT_SLOT_CLICK_SOUND_EVENTS = {StructurePaintSlot.PRIMARY: 'nanocoating_button_push_primary_play',
 StructurePaintSlot.SECONDARY: 'nanocoating_button_push_secondary_play',
 StructurePaintSlot.DETAILING: 'nanocoating_button_push_detailing_play'}
UPKEEP_STATE_NAMES = {UPKEEP_STATE_FULL_POWER: 'UI/Personalization/PaintTool/StructureStates/FullPower',
 UPKEEP_STATE_LOW_POWER: 'UI/Personalization/PaintTool/StructureStates/LowPower',
 UPKEEP_STATE_ABANDONED: 'UI/Personalization/PaintTool/StructureStates/Abandoned'}
_DESIGN_APPLICATION_PAGE_FIXED_SECTION_WIDTH = 688

def get_design_application_page_width():
    return _DESIGN_APPLICATION_PAGE_FIXED_SECTION_WIDTH
