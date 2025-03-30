#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\orbitalMaterialUI.py
import eveformat
import evelink.client
import utillib
from carbon.common.script.net.moniker import Moniker
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.window import Window
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uianimations import animations
import inventorycommon.typeHelpers
import localization
from collections import defaultdict
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from typematerials.data import get_type_materials_by_id
ICONWIDTH = 74
ICONHEIGHT = 154
ICONPADDING = 4

class OrbitalMaterialUI(Window):
    __guid__ = 'form.OrbitalMaterialUI'
    __notifyevents__ = ['OnItemChange']
    default_windowID = 'OrbitalMaterialUI'
    default_captionLabelPath = 'UI/UpgradeWindow/UpgradeHold'
    scope = uiconst.SCOPE_INFLIGHT

    def ApplyAttributes(self, attributes):
        super(OrbitalMaterialUI, self).ApplyAttributes(attributes)
        self.orbitalID = attributes.orbitalID
        self.hasCapacity = 1
        self.MakeUnResizeable()
        self.Startup(attributes.orbitalID, const.flagSpecializedMaterialBay)
        self.CheckCanUpgrade()

    def Startup(self, itemID, locationFlag):
        sm.RegisterNotify(self)
        self.itemID = itemID
        self.typeID = sm.GetService('invCache').GetInventoryFromId(itemID).GetItem().typeID
        self.locationFlag = locationFlag
        self.AddLayoutNew()

    def AddLayoutNew(self):
        self.main_container = ContainerAutoSize(parent=self.content, align=uiconst.TOPLEFT, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        self.sr.iconContainer = LayoutGrid(name='iconContainer', parent=self.main_container, align=uiconst.TOPLEFT, columns=4, cellSpacing=(8, 8))
        self.sr.iconContainer.OnDropData = self.OnDropData
        self.sr.iconContainer.OnDragEnter = self.OnDragEnter
        self.sr.iconContainer.OnDragExit = self.OnDragExit
        self.PopulateIcons()
        self.transferBtn = Button(align=uiconst.CENTER, label=localization.GetByLabel('UI/UpgradeWindow/StartUpgrade'), func=self.InitiateUpgrade, args=(), enabled=self._can_upgrade())
        self.sr.iconContainer.AddCell(self.transferBtn, colSpan=self.sr.iconContainer.columns)

    def _on_main_cont_size_changed(self):
        width, height = self.GetWindowSizeForContentSize(height=self.main_container.height, width=self.main_container.width)
        self.SetMinSize(size=(width, height), refresh=True)

    def AddLayout(self):
        pad = const.defaultPadding
        self.sr.footer = Container(name='footer', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 25), padding=(pad,
         pad,
         pad,
         pad))
        self.sr.iconContainer = Container(name='iconContainer', parent=self.sr.main, align=uiconst.TOALL, padding=(pad + 5,
         pad + 5,
         0,
         0), columns=4)
        self.sr.iconContainer.OnDropData = self.OnDropData
        self.sr.iconContainer.OnDragEnter = self.OnDragEnter
        self.sr.iconContainer.OnDragExit = self.OnDragExit
        btns = [(localization.GetByLabel('UI/UpgradeWindow/StartUpgrade'),
          self.InitiateUpgrade,
          (),
          None)]
        self.buttons = btns = ButtonGroup(btns=btns, parent=self.sr.footer)
        self.transferBtn = btns.buttons[0]

    def PopulateIcons(self):
        qtyByTypeID = defaultdict(lambda : utillib.KeyVal(qty=0, invItems=set()))
        inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
        for item in inv.List(flag=const.flagSpecializedMaterialBay):
            qtyByTypeID[item.typeID].qty += item.stacksize
            qtyByTypeID[item.typeID].invItems.add(item)

        self.upgradeIconsByTypeID = {}
        for info in self.GetUpgradeMaterials():
            upgradeIcon = self.upgradeIconsByTypeID[info.materialTypeID] = UpgradeTypeIcon(name='%s' % info.materialTypeID, parent=self.sr.iconContainer, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, typeID=info.materialTypeID, qtyNeeded=info.quantity, qty=qtyByTypeID[info.materialTypeID].qty, invItems=qtyByTypeID[info.materialTypeID].invItems, containerID=self.itemID)
            upgradeIcon.width = ICONWIDTH
            upgradeIcon.height = ICONHEIGHT
            upgradeIcon.HookInEvents(utillib.KeyVal(OnDropData=self.OnDropData, OnDragEnter=self.OnDragEnter, OnDragExit=self.OnDragExit))

    def ArrangeIcons(self):
        containerWidth, containerHeight = self.sr.iconContainer.GetAbsoluteSize()
        iconWidth = ICONWIDTH + ICONPADDING
        iconHeight = ICONHEIGHT + ICONPADDING
        maxRows = containerHeight / iconHeight
        numberOfColumns = (containerWidth - ICONPADDING) / iconWidth
        for i, icon in enumerate(self.upgradeIconsByTypeID.itervalues()):
            column = i % numberOfColumns
            row = i / numberOfColumns
            icon.left = iconWidth * column
            icon.top = iconHeight * row
            icon.width = ICONWIDTH
            icon.height = ICONHEIGHT
            if row < maxRows:
                icon.state = uiconst.UI_NORMAL
            else:
                icon.state = uiconst.UI_HIDDEN
            icon.state = uiconst.UI_NORMAL

    def OnItemChange(self, item, change, location):
        if const.ixLocationID in change or item.locationID == self.itemID and const.ixStackSize in change:
            if self.itemID in (item.locationID, change.get(const.ixLocationID, None)):
                self.UpdateTypeQuantity(item.typeID)

    def UpdateTypeQuantity(self, typeID):
        inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
        qty = 0
        for item in inv.List():
            if item.typeID == typeID:
                qty += item.stacksize

        self.upgradeIconsByTypeID[typeID].SetQuantity(qty)
        self.CheckCanUpgrade()

    def CheckCanUpgrade(self):
        self.transferBtn.enabled = self._can_upgrade()

    def _can_upgrade(self):
        return all((icon.qty >= icon.qtyNeeded for icon in self.upgradeIconsByTypeID.values()))

    def DoGetShell(self):
        return sm.GetService('invCache').GetInventoryFromId(self.itemID)

    def IsItemHere(self, rec):
        return rec.locationID == self.itemID and rec.flagID == self.locationFlag

    def GetCapacity(self):
        return self.GetShell().GetCapacity(self.locationFlag)

    def InitiateUpgrade(self):
        posMgr = Moniker('posMgr', session.solarsystemid)
        posMgr.OnlineOrbital(self.itemID)
        self.Close()

    def GetUpgradeMaterials(self):
        upgradeTypeID = self.GetUpgradeTypeID()
        return get_type_materials_by_id(upgradeTypeID)

    def GetUpgradeTypeID(self):
        dogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        return int(dogmaStaticSvc.GetTypeAttribute2(self.typeID, const.attributeConstructionType))

    def OnDropData(self, dragObj, nodes):
        itemIDsByLocation = defaultdict(set)
        try:
            for node in nodes:
                if node.__guid__ not in ('xtriui.InvItem', 'listentry.InvItem'):
                    continue
                itemIDsByLocation[node.rec.locationID].add(node.rec.itemID)

            inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
            for locationID, itemIDs in itemIDsByLocation.iteritems():
                inv.MultiAdd(itemIDs, locationID, flag=const.flagSpecializedMaterialBay)

        finally:
            for icon in self.upgradeIconsByTypeID.itervalues():
                self.UpdateTypeQuantity(icon.typeID)

    def OnDragEnter(self, dragObj, nodes, *args):
        qtyByTypeID = defaultdict(lambda : 0)
        for node in nodes:
            if node.__guid__ not in ('xtriui.InvItem', 'listentry.InvItem'):
                continue
            if node.rec.locationID == self.itemID and node.rec.flagID == const.flagSpecializedMaterialBay:
                continue
            typeID = node.rec.typeID
            qtyByTypeID[typeID] += node.rec.quantity

        for typeID, quantity in qtyByTypeID.iteritems():
            icon = self.upgradeIconsByTypeID.get(typeID, None)
            if icon is None:
                continue
            icon.Hilite(quantity)

    def OnDragExit(self, *args):
        for icon in self.upgradeIconsByTypeID.itervalues():
            icon.Delite()


class UpgradeTypeIcon(Container):
    isDragObject = True
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.animateThread = None
        self.typeID = attributes.typeID
        self.invItems = attributes.invItems
        self.qtyNeeded = attributes.qtyNeeded
        self.containerID = attributes.containerID
        self.AddLayout()
        self.SetQuantity(attributes.qty)

    def AddLayout(self):
        self.sr.main = Container(name='main', parent=self, align=uiconst.TOPLEFT, height=ICONHEIGHT, width=ICONWIDTH)
        self.sr.background = Container(name='background', parent=self.sr.main, align=uiconst.TOTOP, height=88)
        self.sr.backgroundFrame = PanelUnderlay(name='backgroundUnderlay', parent=self.sr.background)
        self.sr.iconContainer = Container(name='iconContainer', parent=self.sr.main, align=uiconst.CENTERTOP, pos=(0, 10, 54, 54), idx=0)
        invTypeIcon = inventorycommon.typeHelpers.GetIcon(self.typeID)
        self.sr.icon = icon = eveIcon.Icon(parent=self.sr.iconContainer, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        if invTypeIcon is None:
            icon.ChangeIcon(typeID=self.typeID)
        else:
            icon.LoadIcon(invTypeIcon.iconFile)
        self.sr.quantityContainer = Container(name='quantityContainer', parent=self.sr.background, align=uiconst.CENTERBOTTOM, height=20, width=ICONWIDTH - 1, idx=0, bgColor=(0.0, 0.0, 0.0, 0.5))
        self.sr.quantityLabel = eveLabel.EveLabelMedium(text='', parent=self.sr.quantityContainer, align=uiconst.CENTERBOTTOM, left=3, bold=True)
        self.barContainer = Fill(name='barContainer', parent=self.sr.quantityContainer, align=uiconst.TOPLEFT, color=(1, 1, 1, 0.25), height=20, width=0)
        self.sr.typeNameContainer = Container(name='typeNameContainer', parent=self.sr.main, align=uiconst.TOALL)
        self.sr.typeName = eveLabel.EveLabelMedium(parent=self.sr.typeNameContainer, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, width=ICONWIDTH, text=eveformat.center(evelink.client.type_link(self.typeID)), maxLines=3, top=4)
        self.sr.typeName.maxLines = None
        self.sr.frame = Frame(parent=self, state=uiconst.UI_HIDDEN, color=(1.0, 1.0, 1.0, 0.5))

    def HookInEvents(self, events):
        for container in (self, self.sr.typeName):
            container.OnDropData = events.OnDropData
            container.OnDragEnter = events.OnDragEnter
            container.OnDragExit = events.OnDragExit

    def SetQuantity(self, qty):
        self.qty = qty
        self.DisplayQuantity(qty)
        self.hint = localization.GetByLabel('UI/UpgradeWindow/TypeIconToolTip', amount=self.qtyNeeded - self.qty, typeID=self.typeID)

    def DisplayQuantity(self, qty, highlight = False):
        self.AnimateBar(min(int(ICONWIDTH * (float(qty) / self.qtyNeeded)), ICONWIDTH) - 1)
        if qty <= 0:
            self.sr.icon.opacity = 0.2
        else:
            self.sr.icon.opacity = 1.0
        if False and self.qtyNeeded <= self.qty:
            self.sr.quantityLabel.text = localization.GetByLabel('UI/UpgradeWindow/TypeFull')
        else:
            if highlight:
                qty = '<color=yellow>%s</color>' % qty
            self.sr.quantityLabel.text = '%s / %s' % (qty, self.qtyNeeded)

    def AnimateBar(self, width):
        width = int(max(0, width))
        animations.MorphScalar(self.barContainer, 'width', endVal=width, duration=0.25)

    def Hilite(self, quantity):
        totalQuantity = min(self.qty + quantity, self.qtyNeeded)
        self.DisplayQuantity(totalQuantity, highlight=True)

    def Delite(self):
        self.DisplayQuantity(self.qty)

    def GetDragData(self, *args):
        inv = sm.GetService('invCache').GetInventoryFromId(self.containerID)
        return [ uix.GetItemData(item, 'icons') for item in inv.List(const.flagSpecializedMaterialBay) if item.typeID == self.typeID ]
