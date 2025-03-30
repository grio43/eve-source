#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsFilterSettings.py
import localization
from carbonui.control.contextMenu.menuData import MenuData
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel import standingsConst
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingsConst import SORTED_BY_STANDING_DESCENDING, SORTED_ALPHABETICALLY, SORTED_BY_STANDING_ASCENDING, SORTED_BY_RECENTLY_CHANGED, SORTED_BY_ID, STANDING_SORT_SETTING
from localization import GetByLabel

def get_menu():
    menuData = MenuData()
    menuData.AddCaption(localization.GetByLabel('UI/Standings/SortingHeader'))
    for label, value in standingsConst.SORT_BY_OPTIONS:
        menuData.AddRadioButton(GetByLabel(label), value, STANDING_SORT_SETTING)

    return menuData


def get_nodes_sorted(nodes):
    value = STANDING_SORT_SETTING.get()
    if value == standingsConst.SORTED_BY_STANDING_ASCENDING:
        return sort_by_standing(False, nodes)
    elif value == standingsConst.SORTED_BY_STANDING_DESCENDING:
        return sort_by_standing(True, nodes)
    elif value == standingsConst.SORTED_ALPHABETICALLY:
        return sort_alphabetically(nodes)
    elif value == standingsConst.SORTED_BY_RECENTLY_CHANGED:
        return sort_by_recently_changed(nodes)
    else:
        return sort_by_id(nodes)


def sort_by_id(nodes):
    return _get_nodes_sorted(key=lambda entry: entry.standingData.GetOwnerID2(), nodes=nodes)


def sort_by_standing(descending, nodes):
    return _get_nodes_sorted(key=lambda entry: entry.standingData.GetStanding2To1(), reverse=descending, nodes=nodes)


def sort_alphabetically(nodes):
    return _get_nodes_sorted(key=lambda entry: entry.standingData.GetOwner2Name(), nodes=nodes)


def sort_by_recently_changed(nodes):
    return _get_nodes_sorted(key=lambda entry: _is_entry_read(entry), nodes=nodes)


def _is_entry_read(entry):
    if entry.panel:
        return entry.panel.isRead


def _get_nodes_sorted(key, reverse = False, nodes = None):
    groups = []
    for group in nodes:
        if group.entries:
            group.entries = sorted(group.entries, key=key, reverse=reverse)
            groups.append(group)

    return groups
