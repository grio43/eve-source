#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\assembleModularShip.py
from collections import defaultdict
import evetypes
import localization
import uthread
import utillib
from carbonui import uiconst
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listwindow import ListWindow
from eve.client.script.ui.control import eveLabel
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg
from eve.common.script.sys.eveCfg import IsControllingStructure
from inventorycommon.const import numVisibleSubsystems
from inventorycommon.util import IsSubsystemFlagVisible

def prompt_assemble_modular_ship(ship):
    wnd = AssembleShip.Open(windowID='assemble_modular_ship_dialog', ship=ship)
    wnd.show_window_controls = False
    wnd.MakeUnstackable()
    if wnd.ShowModal() == 1:
        return wnd.result
    else:
        return None


class AssembleShip(ListWindow):
    __guid__ = 'form.AssembleShip'
    __nonpersistvars__ = []
    default_ship = None
    default_groupIDs = None
    default_isPreview = None
    ship_doc = 'Ship'
    groupIDs_doc = 'Group IDs'
    isPreview_doc = 'Is preview'
    result = None

    def ApplyAttributes(self, attributes):
        ListWindow.ApplyAttributes(self, attributes)
        ship = attributes.ship
        groupIDs = attributes.groupIDs
        isPreview = attributes.isPreview
        self.ship = ship
        self.groupIDs = groupIDs
        self.scope = uiconst.SCOPE_INGAME
        self.isPreview = isPreview
        self.SetCaption(localization.GetByLabel('UI/Station/PickSubSystems'))
        self.startSubSystems = {}
        if not self.isPreview:
            self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Submit, cancelFunc=self.Cancel)
        self.invalidateOpenState = 1
        self.scroll.state = uiconst.UI_NORMAL
        self.scroll.SelectAll = self.SelectAll
        self.subSystems = {}
        self.SetMinSize([300, 400])
        self.selectedSubSystemsByFlag = {}
        self.LoadScrollList()
        self.UpdateHint()
        setselected = attributes.setselected
        if setselected is not None:
            self.SetSelected(setselected)

    def SelectAll(self, *args):
        pass

    def UpdateShip(self, ship, selectedSubSystems = None):
        self.ship = ship
        self.startSubSystems = selectedSubSystems or {}
        self.LoadScrollList()

    def SetSelected(self, subSystems = None):
        self.startSubSystems = subSystems or {}
        self.LoadScrollList()

    def GetSubSystemsByGroup(self):
        godma = sm.StartService('godma')
        if self.isPreview:
            subSystemsByGroupID = defaultdict(list)
            for groupID in evetypes.GetGroupIDsByCategory(const.categorySubSystem):
                for typeID in evetypes.GetTypeIDsByGroup(groupID):
                    if not evetypes.IsPublished(typeID):
                        continue
                    if godma.GetTypeAttribute(typeID, const.attributeFitsToShipType) != self.ship.typeID:
                        continue
                    if not IsSubsystemFlagVisible(int(godma.GetTypeAttribute(typeID, const.attributeSubSystemSlot))):
                        continue
                    subSystemsByGroupID[groupID].append((typeID, typeID))

        else:
            if not (eveCfg.IsDocked() or IsControllingStructure()):
                return
            inv = sm.GetService('invCache').GetInventory(const.containerHangar)
            subSystemsByGroupID = defaultdict(list)
            for item in inv.List(const.flagHangar):
                if item.categoryID != const.categorySubSystem:
                    continue
                if godma.GetTypeAttribute(item.typeID, const.attributeFitsToShipType) != self.ship.typeID:
                    continue
                if not IsSubsystemFlagVisible(int(godma.GetTypeAttribute(item.typeID, const.attributeSubSystemSlot))):
                    continue
                subSystemsByGroupID[item.groupID].append((item.typeID, item.itemID))

        return subSystemsByGroupID

    def LoadScrollList(self):
        scrolllist = []
        subSystemsByGroupID = self.GetSubSystemsByGroup()
        godma = sm.GetService('godma')
        for groupID in evetypes.GetGroupIDsByCategory(const.categorySubSystem):
            if self.groupIDs is not None and groupID in self.groupIDs:
                continue
            scrolllist.append(GetFromClass(Header, {'label': evetypes.GetGroupNameByGroup(groupID)}))
            types = []
            typeIDs = []
            if groupID in subSystemsByGroupID:
                for subSystemTypeID, subSystemItemID in subSystemsByGroupID[groupID]:
                    if subSystemTypeID not in typeIDs:
                        types.append((subSystemTypeID, evetypes.GetName(subSystemTypeID), subSystemItemID))
                        typeIDs.append(subSystemTypeID)

            types.sort()
            first = True
            for typeID, typeName, itemID in types:
                data = utillib.KeyVal()
                data.typeID = typeID
                data.label = typeName
                data.showinfo = 1
                data.itemID = itemID
                data.OnClick = self.ClickEntry
                if groupID in self.startSubSystems and typeID == self.startSubSystems[groupID] or not self.startSubSystems and first:
                    data.isSelected = 1
                else:
                    data.isSelected = 0
                if data.isSelected:
                    slotFlag = int(godma.GetTypeAttribute(typeID, const.attributeSubSystemSlot))
                    self.subSystems[slotFlag] = itemID
                    self.selectedSubSystemsByFlag[slotFlag] = itemID
                first = False
                scrolllist.append(GetFromClass(AssembleShipEntry, data))

        self.UpdateHint()
        self.scroll.Load(contentList=scrolllist, scrolltotop=0)

    def getSubSystems(self):
        subSystems = {}
        for s in self.subSystems.values():
            subSystems[evetypes.GetGroupID(s)] = s

        return subSystems

    def ClickEntry(self, entry, *args):
        slotFlag = int(sm.services['godma'].GetTypeAttribute(entry.typeID, const.attributeSubSystemSlot))
        node = None
        if slotFlag in self.selectedSubSystemsByFlag:
            oldItemID = self.selectedSubSystemsByFlag[slotFlag]
            for node in self.scroll.GetNodes():
                if not node.itemID:
                    continue
                if node.itemID == oldItemID:
                    break

            if node is not None:
                node.isSelected = False
            content = self.scroll.sr.content
            for child in content.children:
                if getattr(child, 'itemID', None) == node.itemID:
                    child.HiliteMe(uiconst.UI_HIDDEN)

        node = self.GetNode(entry)
        if node is None:
            return
        self.selectedSubSystemsByFlag[slotFlag] = entry.itemID
        entry.HiliteMe(uiconst.UI_DISABLED)
        node = self.GetNode(entry)
        if node is not None:
            node.isSelected = True
        self.subSystems[slotFlag] = entry.itemID
        self.UpdateHint()
        if self.isPreview:
            sm.GetService('preview').PreviewType(self.ship.typeID, self.getSubSystems(), animate=False)

    def GetNode(self, entry):
        for node in self.scroll.GetNodes():
            if not node.itemID:
                continue
            if node.itemID == entry.itemID:
                return node

    def Error(self, *args):
        pass

    def UpdateHint(self):
        ep = self.GetChild('errorParent')
        if self.groupIDs is None:
            groupIDs = []
        else:
            groupIDs = self.groupIDs
        lenGroupIDs = 0
        if self.groupIDs is not None:
            lenGroupIDs = len(self.groupIDs)
        if len(self.subSystems) + lenGroupIDs != numVisibleSubsystems:
            t = eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Station/SelectFiveSubsystems'), top=-3, parent=ep, width=self.minsize[0] - 32, state=uiconst.UI_DISABLED, color=(1.0, 0.0, 0.0, 1.0), align=uiconst.CENTER)
            ep.state = uiconst.UI_DISABLED
            ep.height = t.height + 8
        else:
            ep.state = uiconst.UI_HIDDEN

    def Refresh(self):
        self.groupIDs = None
        self.subSystems = {}
        self.LoadScrollList()

    def Submit(self, *args):
        lenGroupIDs = 0
        if self.groupIDs is not None:
            lenGroupIDs = len(self.groupIDs)
        hangarContents = {i.itemID for i in sm.GetService('invCache').GetInventory(const.containerHangar).List(const.flagHangar)}
        subSystems = set(self.subSystems.values())
        if subSystems & hangarContents != subSystems:
            self.Refresh()
        if len(self.subSystems) != numVisibleSubsystems - lenGroupIDs:
            self.Refresh()
            return
        self.result = self.subSystems.values()
        self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)


class AssembleShipEntry(Generic):
    __guid__ = 'listentry.AssembleShipEntry'

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.sr.selectedEntry = Fill(parent=self, padTop=1, padBottom=1, color=(0.0, 1.0, 0.0, 0.25))
        self.sr.selectedEntry.state = uiconst.UI_HIDDEN

    def Load(self, node):
        Generic.Load(self, node)
        if node.Get('isSelected', False):
            self.sr.selectedEntry.state = uiconst.UI_DISABLED
        else:
            self.sr.selectedEntry.state = uiconst.UI_HIDDEN

    def GetMenu(self, *args):
        return []

    def HiliteMe(self, state):
        self.sr.selectedEntry.state = state
        self.selected = state == uiconst.UI_DISABLED
