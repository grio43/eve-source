#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\containerContentWindow.py
import evetypes
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.common.lib import appConst as const
from eve.common.script.sys.eveCfg import GetShipFlagLocationName
from localization import GetByLabel

class ContainerContentWindow(Window):
    __guid__ = 'ContainerContentWindow'
    default_width = 500
    default_height = 400
    default_minSize = (500, 256)
    default_windowID = 'containerContentWindow'
    default_captionLabelPath = 'UI/Menusvc/ItemsInContainerHint'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.itemID = None
        self.typeID = None
        self.stationID = None
        self.contentsList = None
        self.topHint = EveLabelMedium(text='', parent=self.sr.main, top=4, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padding=4)
        self.topRightCont = Container(name='topRightCont2', parent=self.sr.main, align=uiconst.TOTOP, height=24, padBottom=1, clipChildren=True)
        self.filterEdit = QuickFilterEdit(name='topRightCont2', parent=self.topRightCont, hintText=GetByLabel('UI/Inventory/Filter'), maxLength=64, left=4, align=uiconst.CENTERRIGHT, OnClearFilter=self.OnFilterEditCleared, width=120, isTypeField=True)
        self.filterEdit.ReloadFunction = self.OnFilterEdit
        self.scroll = Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), id='containerContentWindow')

    def LoadContent(self, itemID, stationID, containerTypeID, invCacheSvc, contentsList = None):
        self.itemID = itemID
        self.typeID = containerTypeID
        self.stationID = stationID
        typeName = evetypes.GetName(containerTypeID)
        hasFlag = evetypes.GetCategoryID(containerTypeID) == const.categoryShip
        if evetypes.GetCategoryID(containerTypeID) == const.categoryShip:
            hint = '<center>' + GetByLabel('UI/Menusvc/ItemsInShipHint2', containerName=typeName)
            self.SetCaption('UI/Menusvc/ItemsInShipHint')
        else:
            hint = '<center>' + GetByLabel('UI/Menusvc/ItemsInContainerHint2', containerName=typeName)
            self.SetCaption('UI/Menusvc/ItemsInContainerHint')
        self.topHint.SetText(hint)
        hdr = [GetByLabel('UI/Inventory/InvItemNameShort'), GetByLabel('UI/Inventory/ItemGroup')]
        if hasFlag:
            hdr += [GetByLabel('UI/Common/Location'), GetByLabel('UI/Common/Quantity')]
        else:
            hdr += [GetByLabel('UI/Common/Quantity')]
        contentList = self.GetContentsList(itemID, hasFlag, stationID, invCacheSvc, contentsList)
        self.scroll.Load(contentList=contentList, headers=hdr, noContentHint=GetByLabel('UI/Common/NothingFound'))

    def GetContentsList(self, itemID, hasFlag, stationID, invCacheSvc, contentsList = None):
        if contentsList is None:
            contents = invCacheSvc.GetInventoryMgr().GetContainerContents(itemID, stationID)
            self.contentsList = contents
        else:
            contents = self.contentsList
        lst = []
        filterText = self.filterEdit.GetValue().strip().lower()
        for c in contents:
            flag = c.flagID
            if flag == const.flagPilot:
                continue
            locationName = GetShipFlagLocationName(flag)
            typeName = evetypes.GetName(c.typeID)
            groupID = evetypes.GetGroupID(c.typeID)
            txt = '%s<t>%s<t>' % (typeName, evetypes.GetGroupNameByGroup(groupID))
            if hasFlag:
                txt += '%s<t><right>%s' % (locationName, c.stacksize)
            else:
                txt += '<right>%s' % c.stacksize
            if filterText and typeName.lower().find(filterText) < 0:
                continue
            data = {'label': txt,
             'typeID': c.typeID,
             'itemID': c.itemID,
             'getIcon': True}
            if c.categoryID == const.categoryBlueprint and c.singleton == const.singletonBlueprintCopy:
                data['isCopy'] = True
            entry = GetFromClass(Item, data)
            lst.append(entry)

        return lst

    def ReloadContent(self):
        if self.itemID and self.typeID and self.stationID:
            self.LoadContent(self.itemID, self.stationID, self.typeID, sm.GetService('invCache'), self.contentsList)

    def OnFilterEditCleared(self):
        self.ReloadContent()

    def OnFilterEdit(self):
        self.ReloadContent()
