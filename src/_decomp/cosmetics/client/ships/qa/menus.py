#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\qa\menus.py
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui.control.contextMenu.menuData import MenuData
from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
from cosmetics.client.shipSkinComponentTradingSvc import get_ship_skin_component_trading_svc
from cosmetics.client.shipSkinDataSvc import get_ship_skin_data_svc
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.client.ships.qa.component_licenses_table import ComponentLicensesTableWindow
from cosmetics.client.ships.qa.settings import is_sequencing_button_always_enabled, should_show_popup_if_skin_name_missing, show_unpublished_components, scene_debug_mode_setting, visualize_shape_ellipsoid
from cosmetics.client.ships.qa.skin_licenses_table import SkinLicensesTableWindow, grant_license_from_design
from cosmetics.client.ships.qa.skin_trading import expire_listing
from cosmetics.client.ships.qa.tier_points import set_current_design_qa_tier_points
from cosmetics.client.liveIconCacheUtils import clear_all_cached_maps, open_cache_directory_in_explorer

def is_qa():
    if not session:
        return False
    return bool(session.role & ROLE_QA)


def add_qa_context_menu(menu_data):
    menu_data.AddSeparator()
    m = MenuData()
    m.AddEntry('Sequencing', subMenuData=add_qa_submenu_for_sequencing())
    m.AddEntry('Bypass popups', subMenuData=add_qa_submenu_for_popups())
    m.AddEntry('Flush Client Service Cache', _flush_client_service_cache)
    m.AddEntry('Component Licenses', ComponentLicensesTableWindow.Open)
    m.AddEntry('SKIN Licenses', SkinLicensesTableWindow.Open)
    m.AddCheckbox('Show unpublished components', show_unpublished_components)
    m.AddCheckbox('3d Scene Debug Mode', scene_debug_mode_setting)
    m.AddCheckbox('Visualize shapeEllipsoid', visualize_shape_ellipsoid)
    m.AddEntry('Clear icon cache', clear_all_cached_maps)
    m.AddEntry('Open icon cache folder', open_cache_directory_in_explorer)
    menu_data.AddEntry(text='QA', subMenuData=m)


def add_qa_submenu_for_sequencing():
    m = MenuData()
    m.AddCheckbox("Enable 'Start Sequencing' despite errors", is_sequencing_button_always_enabled)
    return m


def add_qa_submenu_for_popups():
    m = MenuData()
    m.AddCheckbox("Show 'Skin Name' popup when name is missing", should_show_popup_if_skin_name_missing)
    return m


def _flush_client_service_cache():
    get_ship_skin_component_svc()._populate_cache()
    get_ship_skin_component_trading_svc()._clear_cache()
    get_ship_skin_sequencing_svc()._clear_cache()
    get_ship_skin_license_svc()._clear_cache()
    get_ship_skin_design_svc()._clear_cache()
    get_ship_skin_data_svc()._clear_cache()


def get_qa_menu_for_tier_points():
    if is_qa():
        return [('Set QA Tier Points', set_current_design_qa_tier_points, ())]
    return []


def get_qa_menu_for_design_card(skin_design_id):
    if is_qa():
        return [('QA: Grant License', lambda : grant_license_from_design(skin_design_id, 10), ())]
    return []


def get_qa_menu_for_skin_listing_card(card, skin_listing_id):
    if is_qa():
        return [('QA: Expire...', lambda : expire_listing(card, skin_listing_id), ())]
    return []
