#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\const.py
import eveicon
from eve.client.script.ui import eveThemeColor
from itertoolsext.Enum import Enum
from cosmetics.common.ships.skins.static_data.component_category import ComponentCategory
from cosmetics.common.ships.skins.static_data.slot_name import SlotID
from eve.common.lib import appConst
COMPONENT_CATEGORY_NAMES = {ComponentCategory.MATERIAL: 'UI/Personalization/ShipSkins/DesignComponents/Categories/Nanocoating',
 ComponentCategory.PATTERN: 'UI/Personalization/ShipSkins/DesignComponents/Categories/Pattern',
 ComponentCategory.METALLIC: 'UI/Personalization/ShipSkins/DesignComponents/Categories/Metallic'}
SLOT_ICONS = {SlotID.PRIMARY_NANOCOATING: eveicon.primary_area,
 SlotID.SECONDARY_NANOCOATING: eveicon.secondary_area,
 SlotID.TERTIARY_NANOCOATING: eveicon.details,
 SlotID.TECH_AREA: eveicon.tech_area,
 SlotID.PATTERN: eveicon.patterns,
 SlotID.PATTERN_MATERIAL: eveicon.primary_area,
 SlotID.SECONDARY_PATTERN: eveicon.patterns,
 SlotID.SECONDARY_PATTERN_MATERIAL: eveicon.primary_area}
SEQUENCE_BINDER_ICONS_BY_MATERIAL_TYPE = {appConst.typeAlignment: eveicon.alignment,
 appConst.typeFermionic: eveicon.fermionic,
 appConst.typeKerr: eveicon.kerr}
SEQUENCE_BINDER_NAMES_BY_MATERIAL_TYPE = {appConst.typeAlignment: 'UI/Personalization/ShipSkins/SKINR/Studio/Alignment',
 appConst.typeFermionic: 'UI/Personalization/ShipSkins/SKINR/Studio/Fermionic',
 appConst.typeKerr: 'UI/Personalization/ShipSkins/SKINR/Studio/Kerr'}
PANEL_BG_COLOR = eveThemeColor.THEME_TINT
PANEL_BG_OPACITY = 0.95
ANIM_DURATION_MEDIUM = 0.6
ANIM_DURATION_LONG = 1.2
ANIM_DURATION_EXTRA_LONG = 2.4

@Enum

class SkinrPage:
    STUDIO = 1
    STUDIO_DESIGNER = 2
    STUDIO_SEQUENCING = 3
    STORE = 4
    STORE_SKINS = 5
    STORE_COMPONENTS = 6
    COLLECTION = 7
    COLLECTION_SKINS = 8
    COLLECTION_COMPONENTS = 9
    STUDIO_SAVED_DESIGNS = 10


CHILD_PAGES_BY_PARENT_PAGE = {SkinrPage.STUDIO: (SkinrPage.STUDIO_DESIGNER, SkinrPage.STUDIO_SEQUENCING),
 SkinrPage.STORE: (SkinrPage.STORE_COMPONENTS, SkinrPage.STORE_SKINS),
 SkinrPage.COLLECTION: (SkinrPage.COLLECTION_SKINS, SkinrPage.COLLECTION_COMPONENTS)}
PARENT_PAGE_BY_CHILD_PAGE = {}
for parent_page_id, children in CHILD_PAGES_BY_PARENT_PAGE.items():
    for page_id in children:
        PARENT_PAGE_BY_CHILD_PAGE[page_id] = parent_page_id
