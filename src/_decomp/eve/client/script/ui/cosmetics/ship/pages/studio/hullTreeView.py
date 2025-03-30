#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\hullTreeView.py
import logging
import sys
import evetypes
import localization
import shipgroup
import uthread2
from carbonui import uiconst, TextColor, Align, SpriteEffect
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from cosmetics.common.ships.skins.static_data.slot_configuration import is_skinnable_ship
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.treeData import TreeData
from eve.client.script.ui.control.treeViewEntry import TreeViewEntry, TreeViewEntryShip
from eve.client.script.ui.shared.shipTree import shipTreeConst
from eve.common.script.sys.idCheckers import IsShipType
from eveui.autocomplete import ItemTypeProvider
from localization import GetByMessageID, GetByLabel
from signals import Signal
log = logging.getLogger(__name__)

def get_tree_view_entry_class(node):
    if isinstance(node, ShipTreeData):
        return HullTreeViewEntryShip
    else:
        return ShipGroupTreeViewEntry


class HullTreeView(ScrollContainer):
    default_alignMode = Align.TOTOP

    def __init__(self, **kw):
        super(HullTreeView, self).__init__(**kw)
        self.faction_id = None
        self.root_node = None
        self.search_provider = ItemTypeProvider(type_filter=IsShipType)
        self.reconstruct_thread = None
        self.loading_wheel = LoadingWheel(parent=self, align=Align.CENTERTOP, top=32, state=uiconst.UI_DISABLED, opacity=0.0)
        self.tree_view_cont = ContainerAutoSize(parent=self, align=Align.TOTOP)
        self.on_hull_type_selected = Signal('on_hull_type_selected')

    def apply_search_query(self, query):
        self.reconstruct_tree_view(query)

    def set_faction(self, faction_id, selected_type_id = None):
        if faction_id == shipTreeConst.ANY_FACTION:
            faction_id = None
        self.faction_id = faction_id
        if self.reconstruct_thread:
            self.reconstruct_thread.kill()
        self.reconstruct_thread = uthread2.start_tasklet(self.reconstruct_tree_view, None, selected_type_id)

    def reconstruct_tree_view(self, search_query = None, selected_type_id = None):
        self.tree_view_cont.opacity = 0.0
        animations.FadeIn(self.loading_wheel, duration=0.3, timeOffset=0.1)
        try:
            self.root_node = TreeData()
            self._construct_tree_data(search_query)
            self._reconstruct_tree_entries()
            self._set_selected_node(selected_type_id)
            self.root_node.on_click.connect(self.on_node_clicked)
            self.root_node.on_selected.connect(self.on_node_selected)
            self.root_node.on_deselected.connect(self.on_node_deselected)
        finally:
            animations.FadeIn(self.tree_view_cont, duration=0.3)
            animations.FadeOut(self.loading_wheel, duration=0.1)

    def _set_selected_node(self, selected_type_id):
        if selected_type_id:
            selected_node = self.root_node.GetChildByID(selected_type_id)
            if selected_node:
                selected_node.SetSelected(animate=False)

    def _construct_tree_data(self, search_query):
        if search_query:
            type_ids = self.get_search_result_type_ids(search_query)
            for type_id in type_ids:
                self.root_node.AddChild(ShipTreeData(evetypes.GetName(type_id), nodeID=type_id))

        else:
            for ship_group_id in self.get_top_level_ship_group_ids_sorted():
                if ship_group_id:
                    self._add_ship_group_to_tree(ship_group_id, self.root_node)

    def get_search_result_type_ids(self, search_query):
        suggestions = list(self.search_provider(query=search_query, previous_suggestions=[]))
        type_ids = [ suggestion.type_id for _, suggestion in suggestions ]
        return type_ids

    def _reconstruct_tree_entries(self):
        self.tree_view_cont.Flush()
        for node in self.root_node.children:
            cls = get_tree_view_entry_class(node)
            cls(parent=self.tree_view_cont, data=node, level=0)

        self._update_no_content_hint()

    def _update_no_content_hint(self):
        if self.root_node.children:
            no_content_hint = None
        else:
            no_content_hint = GetByLabel('UI/Wallet/WalletWindow/SearchNoResults')
        self.ShowNoContentHint(no_content_hint)

    def get_top_level_ship_group_ids_sorted(self):

        def get_sort_key(group_id):
            if group_id in shipgroup.GROUPS_BY_SIZE:
                return shipgroup.GROUPS_BY_SIZE.index(group_id)
            else:
                return sys.maxint

        group_ids = shipgroup.get_ship_group_ids(faction_id=self.faction_id)
        return sorted(group_ids, key=get_sort_key)

    def on_node_selected(self, node, *args):
        self.on_hull_type_selected(node.GetID())

    def on_node_deselected(self, *args):
        self.on_hull_type_selected(None)

    def _add_ship_group_to_tree(self, ship_group_id, parent_node):
        name_id = cfg.infoBubbleGroups[ship_group_id]['nameID']
        type_ids = shipgroup.get_type_ids(ship_group_id, self.faction_id)
        sub_group_ids = shipgroup.get_ship_group_ids(ship_group_id, self.faction_id)
        if not type_ids and not sub_group_ids:
            return
        node = ShipGroupTreeData(label=localization.GetByMessageID(name_id), nodeID=ship_group_id)
        parent_node.AddChild(node)
        for type_id in type_ids:
            node.AddChild(ShipTreeData(evetypes.GetName(type_id), nodeID=type_id))

        for sub_group_id in sub_group_ids:
            self._add_ship_group_to_tree(sub_group_id, node)

    def on_node_clicked(self, node):
        if isinstance(node, ShipTreeData):
            if node.IsSelected():
                node.SetDeselected()
            else:
                node.GetRootNode().DeselectAll()
                node.SetSelected()
        else:
            node.ToggleExpanded()


class ShipTreeData(TreeData):

    def __eq__(self, other):
        return self.GetID() == other.GetID()

    def is_skinnable(self):
        return is_skinnable_ship(self.GetID())

    def GetHint(self):
        if not self.is_skinnable():
            return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ShipNotSkinnableTooltip')

    def IsSelectable(self):
        return is_skinnable_ship(self.GetID())


class ShipGroupTreeData(TreeData):

    def GetHint(self):
        return GetByMessageID(cfg.infoBubbleGroups.get(self.GetID())['descriptionID'])

    def GetIcon(self):
        return cfg.infoBubbleGroups.get(self.GetID())['iconSmall']


class ShipGroupTreeViewEntry(TreeViewEntry):
    default_height = 32
    default_iconColor = TextColor.NORMAL
    default_settingsID = 'ShipGroupTreeViewEntry'

    def GetTreeViewEntryClassByTreeData(self, node):
        return get_tree_view_entry_class(node)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def GetTooltipPosition(self):
        l, t, w, h = self.GetAbsolute()
        return (l,
         t,
         w,
         self.default_height)

    def GetIconSize(self):
        return 16


class HullTreeViewEntryShip(TreeViewEntryShip):

    def ApplyAttributes(self, attributes):
        super(HullTreeViewEntryShip, self).ApplyAttributes(attributes)
        if not self.data.is_skinnable():
            self.icon.icon.spriteEffect = SpriteEffect.COLOROVERLAY
            self.icon.icon.saturation = 0.0
            self.icon.opacity = 0.5
            self.SetAccessability(canAccess=False)

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def OnClick(self, *args):
        if not self.data.is_skinnable():
            return
        super(HullTreeViewEntryShip, self).OnClick(*args)
