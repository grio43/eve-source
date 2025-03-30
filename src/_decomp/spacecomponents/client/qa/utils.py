#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\qa\utils.py
import blue
from carbonui.control.contextMenu.menuData import MenuData
from spacecomponents.client.factory import COMPONENTS as CLIENT_COMPONENTS
from spacecomponents.common.data import get_space_component_names_for_type

def get_qa_menu(item_id, type_id):
    return ('GM: Space Components', ('isDynamic', get_list_of_space_components_in_item, (item_id, type_id)))


def get_list_of_space_components_in_item(item_id, type_id):
    menu_data = MenuData()
    ballpark = sm.GetService('michelle').GetBallpark()
    if not ballpark:
        menu_data.AddEntry('Unavailable, ballpark not loaded', isEnabled=False)
        return menu_data
    submenu_by_component_name = _get_component_submenus(ballpark, item_id, type_id)
    if not submenu_by_component_name:
        menu_data.AddEntry('None', isEnabled=False)
        return menu_data
    for component_name in sorted(submenu_by_component_name.keys()):
        submenu = submenu_by_component_name[component_name]
        if submenu:
            menu_data.AddEntry(text=component_name, subMenuData=submenu)
        else:
            menu_data.AddEntry(text=component_name, func=lambda c = component_name: blue.pyos.SetClipboardData(c))

    return menu_data


def _get_component_submenus(ballpark, item_id, type_id):
    submenu_by_component_name = {}
    component_names = get_space_component_names_for_type(type_id)
    if not component_names:
        return submenu_by_component_name
    try:
        component_instances = ballpark.componentRegistry.GetComponentsByItemID(item_id)
    except KeyError:
        return submenu_by_component_name

    for component_name in component_names:
        if component_name in CLIENT_COMPONENTS:
            try:
                submenu = component_instances[component_name].GetGMMenu()
            except (AttributeError, KeyError):
                submenu = None

        else:
            component_name = '%s (server only)' % component_name
            submenu = None
        submenu_by_component_name[component_name] = submenu

    return submenu_by_component_name
