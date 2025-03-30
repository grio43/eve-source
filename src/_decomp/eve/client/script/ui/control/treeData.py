#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\treeData.py
import collections
from signals import Signal

class TreeData(object):

    def __init__(self, label = None, parent = None, children = None, icon = None, isRemovable = False, settings = None, nodeID = None, **kw):
        self._label = label
        self._children = children or []
        if isinstance(self._children, tuple):
            self._children = list(self._children)
        self._parent = parent
        if parent:
            parent.AddChild(self)
        for child in self._children:
            child._parent = self

        self._kw = kw
        self._node_id = nodeID
        self._icon = icon
        self._isRemovable = isRemovable
        self._settings = settings
        self._is_selected = False
        self._is_expanded = False
        self._ConstructSignals()

    def _ConstructSignals(self):
        self.on_created = Signal('on_created')
        self.on_destroyed = Signal('on_destroyed')
        self.on_click = Signal('on_click')
        self.on_dbl_click = Signal('on_dbl_click')
        self.on_mouse_down = Signal('on_mouse_down')
        self.on_mouse_up = Signal('on_mouse_up')
        self.on_mouse_enter = Signal('on_mouse_enter')
        self.on_mouse_exit = Signal('on_mouse_exit')
        self.on_drop_data = Signal('on_drop_data')
        self.on_drag_enter = Signal('on_drag_enter')
        self.on_drag_exit = Signal('on_drag_exit')
        self.on_selected = Signal('on_selected')
        self.on_deselected = Signal('on_deselected')
        self.on_descendant_selected = Signal('on_descendant_selected')
        self.on_descendant_deselected = Signal('on_descendant_deselected')
        self.on_expanded = Signal('on_expanded')
        self.on_collapsed = Signal('on_collapsed')
        self.on_click.connect(self._trigger_root_node_on_click)
        self.on_dbl_click.connect(self._trigger_root_node_on_dbl_click)
        self.on_selected.connect(self._trigger_root_node_on_selected)
        self.on_deselected.connect(self._trigger_root_node_on_deselected)
        self.on_expanded.connect(self._trigger_root_node_on_expanded)
        self.on_collapsed.connect(self._trigger_root_node_on_collapsed)

    def _trigger_root_node_on_click(self, node):
        if not self.IsRoot():
            self.GetRootNode().on_click(node)

    def _trigger_root_node_on_dbl_click(self, node):
        if not self.IsRoot():
            self.GetRootNode().on_dbl_click(node)

    def _trigger_root_node_on_selected(self, node, animate = True):
        if not self.IsRoot():
            self.parent._on_descendant_selected(node, animate)

    def _on_descendant_selected(self, node, animate):
        if self.IsRoot():
            self.on_selected(node, animate)
        else:
            self.parent._on_descendant_selected(node, animate)
        self.on_descendant_selected(node, animate)

    def _trigger_root_node_on_deselected(self, node, animate = True):
        if not self.IsRoot():
            self.parent._on_descendant_deselected(node, animate)

    def _on_descendant_deselected(self, node, animate):
        if self.IsRoot():
            self.on_deselected(node, animate)
        else:
            self.parent._on_descendant_deselected(node, animate)
        self.on_descendant_deselected(node, animate)

    def _trigger_root_node_on_expanded(self, node, animate = True):
        if not self.IsRoot():
            self.GetRootNode().on_expanded(node, animate)

    def _trigger_root_node_on_collapsed(self, node, animate = True):
        if not self.IsRoot():
            self.GetRootNode().on_collapsed(node, animate)

    def GetSettings(self):
        return self._settings

    settings = property(GetSettings)

    def GetParent(self):
        return self._parent

    parent = property(GetParent)

    def IsRoot(self):
        return not self.parent

    def IsLeaf(self):
        return not self.GetChildren()

    def GetRootNode(self):
        if not self.parent:
            return self
        return self.parent.GetRootNode()

    def GetLabel(self):
        return self._label or ''

    def GetIcon(self):
        return self._icon

    def GetMenu(self):
        return []

    def GetHint(self):
        return None

    def GetTooltipPointer(self):
        return None

    def GetID(self):
        if self._node_id is not None:
            return self._node_id
        else:
            return (self._label, tuple(self._kw.keys()))

    def GetChildren(self):
        return self._children

    children = property(GetChildren)

    def AddChild(self, child):
        if child not in self._children:
            self._children.append(child)
            child._parent = self

    def AddNode(self, label = None, children = None, icon = None, isRemovable = False, settings = None, nodeID = None, **kw):
        treeData = TreeData(label=label, parent=self, children=children, icon=icon, isRemovable=isRemovable, settings=settings, nodeID=nodeID, **kw)
        self.AddChild(treeData)
        return treeData

    def RemoveChild(self, child):
        if child in self._children:
            self._children.remove(child)

    def GetChildByID(self, dataID, recursive = True):
        if dataID == self.GetID():
            return self
        if self.IsForceCollapsed():
            return None
        children = self.GetChildren()
        for child in children:
            if child.GetID() == dataID:
                return child

        for child in children:
            ret = child.GetChildByID(dataID)
            if ret:
                return ret

    def GetSelected(self):
        return self._GetSelected([])

    def _GetSelected(self, ret):
        if self.IsSelected():
            ret.append(self)
        for child in self._children:
            child._GetSelected(ret)

        return ret

    def IsDraggable(self):
        return False

    def HasChildren(self):
        return bool(self._children)

    def IsRemovable(self):
        return self._isRemovable

    def IsForceCollapsed(self):
        return False

    def GetPathToDescendant(self, dataID, forceGetChildren = False):
        if self.GetID() == dataID:
            return [self]
        if self.HasChildren():
            if not forceGetChildren and self.IsForceCollapsed():
                return None
            for child in self.GetChildren():
                found = child.GetPathToDescendant(dataID, forceGetChildren)
                if found:
                    return [self] + found

    def GetAncestors(self):
        parent = self.GetParent()
        if parent:
            ancestors = parent.GetAncestors()
            ancestors.append(parent)
            return ancestors
        else:
            return []

    def IsAncestor(self, node):
        return node in self.GetAncestors()

    def GetDescendants(self, forceGetChildren = False):
        ret = collections.OrderedDict()
        if self.HasChildren():
            if not forceGetChildren and self.IsForceCollapsed():
                return {}
            for child in self.GetChildren():
                ret[child.GetID()] = child
                ret.update(child.GetDescendants())

        return ret

    def IsDescendantOf(self, invID):
        parent = self.GetParent()
        if not parent:
            return False
        if invID == parent.GetID():
            return True
        return parent.IsDescendantOf(invID)

    def IsSelectable(self):
        return True

    def SetSelected(self, animate = True):
        if not self.IsSelectable():
            return
        was_selected = self._is_selected
        self._is_selected = True
        if not was_selected:
            self.on_selected(self, animate)

    def SetDeselected(self, animate = True):
        was_selected = self._is_selected
        self._is_selected = False
        if was_selected:
            self.on_deselected(self, animate)

    def IsSelected(self):
        return self._is_selected

    def SetExpanded(self, animate = True):
        was_expaned = self._is_expanded
        self._is_expanded = True
        if not was_expaned:
            self.on_expanded(self, animate)

    def SetCollapsed(self, animate = True):
        was_expaned = self._is_expanded
        self._is_expanded = False
        if was_expaned:
            self.on_collapsed(self, animate)

    def IsExpanded(self):
        return self._is_expanded

    def ToggleExpanded(self, animate = True):
        if self.IsExpanded():
            self.SetCollapsed(animate)
        else:
            self.SetExpanded(animate)

    def IsAnyDescendantSelected(self):
        if self.IsForceCollapsed():
            return False
        for child in self.GetChildren():
            if child.IsSelected() or child.IsAnyDescendantSelected():
                return True

        return False

    def DeselectAll(self, animate = True):
        self.SetDeselected(animate)
        for child in self.GetChildren():
            child.DeselectAll(animate)
