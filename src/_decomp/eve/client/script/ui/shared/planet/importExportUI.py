#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\importExportUI.py
import carbonui.const as uiconst
import blue
import utillib
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.eveLabel import EveHeaderMedium
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.util import uix
import localization
import log
import eve.common.script.util.planetCommon as planetCommon
from eve.client.script.ui.inflight.orbitalConfiguration import OrbitalConfigurationWindow
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.gauge import Gauge
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import UserError
from inventorycommon.util import GetTypeVolume
GAUGE_WIDTH = 180

class CustomsItem(Item):
    __guid__ = 'listentry.CustomsItem'
    isDragObject = True

    def Startup(self, *args):
        Item.Startup(self, *args)
        self.sr.selectedEntry = Fill(parent=self, padTop=1, padBottom=1, color=(0.0, 1.0, 0.0, 0.25))
        self.sr.selectedEntry.state = uiconst.UI_HIDDEN
        if self.sr.node.isItemTransfer:
            self.sr.selectedEntry.state = uiconst.UI_PICKCHILDREN

    def GetDragData(self, *args):
        ret = []
        for node in self.sr.node.scroll.GetSelectedNodes(self.sr.node):
            if node.item is not None:
                item = uix.GetItemData(node.item, 'icon')
                item.scroll = node.scroll
                item.itemID = node.itemID
                item.typeID = node.typeID
                item.quantity = node.quantity
                ret.append(item)
            else:
                ret.append(node)

        return ret

    def LoadTooltipPanel(self, tooltipPanel, *args):
        planetCommonUI.LoadProductTooltipPanel(tooltipPanel, self.sr.node.typeID)


class PlanetaryImportExportUI(Window):
    default_windowID = 'PlanetaryImportExportUI'
    default_iconNum = 'res:/ui/Texture/WindowIcons/items.png'
    default_minSize = (560, 400)
    default_isStackable = False
    default_scope = uiconst.SCOPE_INFLIGHT
    __notifyevents__ = ['OnItemChange',
     'OnPlanetPinsChanged',
     'OnBallparkCall',
     'OnRefreshPins',
     'OnPlanetChangesSubmitted',
     'OnSkyhookFirstActivation']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.spaceportPinID = attributes.spaceportPinID
        self.customsOfficeID = attributes.customsOfficeID
        self.id = self.customsOfficeID
        self.customsOffice = sm.GetService('invCache').GetInventoryFromId(self.customsOfficeID)
        if not self.customsOffice:
            raise RuntimeError('PlanetaryImportExportUI::Cannot find cargo link with ID %s' % str(self.customsOfficeID))
        bp = sm.GetService('michelle').GetBallpark()
        if self.customsOfficeID not in bp.slimItems:
            raise RuntimeError('OpenPlanetCustomsOfficeImportWindow::Failed to get cargo link data for link ID %s' % str(self.customsOfficeID))
        self.customsOfficeItem = bp.slimItems[self.customsOfficeID]
        self.customsOfficeLevel = self.customsOfficeItem.level
        if self.customsOfficeItem.planetID is None:
            raise RuntimeError('OpenPlanetCustomsOfficeImportWindow::Customs office slim item has no planetID set, most likely failed to startup correctly %s' % str(self.customsOfficeItem))
        self.planet = sm.GetService('planetSvc').GetPlanet(self.customsOfficeItem.planetID)
        sm.GetService('inv').Register(self)
        blue.pyos.synchro.Yield()
        self.Layout()
        self._OnResize()
        self.ResetContents()

    def Layout(self):
        self.ConstructTopParent()
        self.SetCaption(localization.GetByLabel('UI/PI/Common/PlanetaryCustomsOfficeName', planetName=cfg.evelocations.Get(self.planet.planetID).name))
        self.footer = ContainerAutoSize(name='footer', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 25), padding=(0, 8, 0, 0), alignMode=uiconst.TOPRIGHT)
        self.cols = Container(name='colums', parent=self.sr.main, align=uiconst.TOALL)
        self.leftColumn = Container(name='leftColumn', parent=self.cols, align=uiconst.TOLEFT_PROP, width=0.5, clipChildren=True)
        self.rightColumn = Container(name='rightColumn', parent=self.cols, align=uiconst.TOALL, padding=(16, 0, 0, 0), clipChildren=True)
        colTopHeight = 70
        self.customsHeader = Container(name='customsHeader', parent=self.leftColumn, align=uiconst.TOTOP, height=colTopHeight)
        self.customsList = Container(name='customsList', parent=self.leftColumn, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.customsHeaderTitle = eveLabel.Label(text=localization.GetByLabel('UI/PI/Common/PlanetaryCustomsOffice'), parent=self.customsHeader, align=uiconst.TOPLEFT, fontsize=16, state=uiconst.UI_NORMAL)
        self.customsGauge = Gauge(parent=self.customsHeader, value=0.0, color=planetCommonUI.PLANET_COLOR_STORAGE, pos=(0,
         25,
         GAUGE_WIDTH,
         0), state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT)
        self.spaceportHeader = Container(name='spaceportHeader', parent=self.rightColumn, align=uiconst.TOTOP, height=colTopHeight)
        self.spaceportList = Container(name='spaceportList', parent=self.rightColumn, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.spaceportCombo = Combo(label=None, parent=self.spaceportHeader, options=[], name='imex_import_select', callback=self.OnSpaceportComboChanged, width=GAUGE_WIDTH, align=uiconst.TOPRIGHT)
        self.spaceportGauge = Gauge(parent=self.spaceportHeader, value=0.0, color=planetCommonUI.PLANET_COLOR_STORAGE, pos=(0,
         self.spaceportCombo.height + 4,
         GAUGE_WIDTH,
         0), state=uiconst.UI_HIDDEN, align=uiconst.TOPRIGHT)
        self.transferCostLabel = eveLabel.EveLabelSmall(parent=self.footer, state=uiconst.UI_NORMAL, top=7, align=uiconst.CENTERLEFT)
        btns = [(localization.GetByLabel('UI/PI/Common/CustomsOfficeTransfer'),
          self.ConfirmCommodityTransfer,
          (),
          None)]
        btns = ButtonGroup(btns=btns, parent=self.footer, align=uiconst.TOPRIGHT)
        self.transferBtn = btns.buttons[0]
        self.customsListScroll = eveScroll.Scroll(parent=self.customsList, name='customsList')
        self.customsListScroll.sr.id = 'piCustomsListScroll'
        self.spaceportListScroll = eveScroll.Scroll(parent=self.spaceportList, name='spaceportList')
        self.spaceportListScroll.sr.id = 'piSpaceportListScroll'

    def ConstructTopParent(self):
        self.windowCaption = EveHeaderMedium(parent=self.sr.main, align=uiconst.TOTOP, padBottom=8)

    def ConstructTopParentOld(self):
        topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=56, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=topParent, state=uiconst.UI_DISABLED, pos=(0, -3, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.windowCaption = eveLabel.WndCaptionLabel(text=localization.GetByLabel('UI/PI/Common/PlanetaryCustomsOfficeName', planetName=cfg.evelocations.Get(self.planet.planetID).name), subcaption=localization.GetByLabel('UI/PI/Common/ImportExportSubHeading'), parent=topParent)

    def IsAllowedToConfigureForCorp(self):
        checkIsMyCorps = self.customsOfficeItem.ownerID == session.corpid
        checkIsStationManager = session.corprole & const.corpRoleStationManager == const.corpRoleStationManager
        hasAccess = checkIsMyCorps and checkIsStationManager
        return hasAccess

    def ResetContents(self):
        self.LoadDestComboOptions()
        self.SetCustomsOfficeContent()
        self.SetSpaceportContent()
        self.importContents = {}
        self.exportContents = {}
        self.UpdateTaxRate()
        self.RefreshLists()

    def RefreshLists(self, *args):
        self.LoadContentToScroll(self.customsOfficeContents, self.exportContents, self.customsListScroll, self.OnCustomsScrollDropData)
        self.LoadContentToScroll(self.spaceportContents, self.importContents, self.spaceportListScroll, self.OnSpaceportScrollDropData)
        self.RefreshHeaderInfo()

    def GetSettingsMenu(self, *args):
        return [(localization.GetByLabel('UI/DustLink/ConfigureOrbital'), self.OpenConfiguration, ())]

    def GetMenuMoreOptions(self):
        menuData = super(PlanetaryImportExportUI, self).GetMenuMoreOptions()
        if self.IsAllowedToConfigureForCorp():
            menuData += self.GetSettingsMenu()
        return menuData

    def OpenConfiguration(self):
        OrbitalConfigurationWindow.Open(orbitalItem=self.customsOffice.GetItem())

    def LoadDestComboOptions(self):
        colony = self.planet.GetColony(session.charid)
        if colony is None:
            self.spaceportCombo.LoadOptions([(localization.GetByLabel('UI/PI/Common/NoDestinationsFound'), None)])
            return
        self.endpoints = colony.GetImportEndpoints()
        if len(self.endpoints) < 1:
            self.spaceportCombo.LoadOptions([(localization.GetByLabel('UI/PI/Common/NoDestinationsFound'), None)])
            return
        options = []
        for endpoint in self.endpoints:
            pin = self.planet.GetPin(endpoint.id)
            options.append((planetCommon.GetGenericPinName(pin.typeID, pin.id), endpoint.id))

        if self.spaceportPinID is None:
            self.spaceportPinID = options[0][1]
        self.spaceportCombo.LoadOptions(options, select=self.spaceportPinID)

    def SetCustomsOfficeContent(self):
        self.customsOfficeContents = {}
        for item in self.customsOffice.List(const.flagHangar):
            if item.flagID != const.flagHangar:
                continue
            if item.ownerID != session.charid:
                continue
            self.customsOfficeContents[item.itemID, item.typeID] = utillib.KeyVal(itemID=item.itemID, typeID=item.typeID, quantity=item.stacksize, name=planetCommonUI.GetProductNameAndTier(item.typeID), item=getattr(item, 'item', item))

    def SetSpaceportContent(self):
        self.spaceportContents = {}
        if self.spaceportPinID is None:
            return
        if self.planet.GetColony(session.charid) is None:
            log.LogWarn('Unable to update spaceport contents, colony not yet loaded')
            return
        pin = self.planet.GetPin(self.spaceportPinID)
        if pin is None:
            raise UserError('CannotImportEndpointNotFound')
        for typeID, qty in pin.GetContents().iteritems():
            name = planetCommonUI.GetProductNameAndTier(typeID)
            self.spaceportContents[None, typeID] = utillib.KeyVal(itemID=None, typeID=typeID, quantity=qty, name=name)

    def LoadContentToScroll(self, contentList, transferList, scroll, onDropDataCallback):
        scroll.sr.content.OnDropData = onDropDataCallback
        scrollHeaders = ['', localization.GetByLabel('UI/Common/Quantity'), localization.GetByLabel('UI/Common/Commodity')]
        scrollContents = []
        scrollNoContentText = localization.GetByLabel('UI/PI/Common/NoItemsFound')
        for item in contentList.values():
            data = utillib.KeyVal()
            data.label = '<t>%d<t>%s' % (item.quantity, item.name)
            data.quantity = item.quantity
            data.typeID = item.typeID
            data.itemID = item.itemID
            data.getIcon = 1
            data.hint = item.name
            data.item = getattr(item, 'item', None)
            data.isItemTransfer = (item.itemID, item.typeID) in transferList
            data.OnDropData = onDropDataCallback
            scrollContents.append(GetFromClass(CustomsItem, data))

        sortBy = scroll.GetSortBy()
        if sortBy is None:
            sortBy = localization.GetByLabel('UI/Common/Commodity')
        scroll.LoadContent(contentList=scrollContents, headers=scrollHeaders, noContentHint=scrollNoContentText, sortby=sortBy)
        scroll.RefreshSort()

    def GetCommodityVolume(self, commodities = None, excluded = None):
        volume = 0
        for key, item in commodities.iteritems():
            if excluded is None or key not in excluded:
                volume += GetTypeVolume(key[1], item.quantity)

        return volume

    def GetCustomsCapacityUsed(self):
        capacity = self.customsOffice.GetCapacity().used
        for item in self.exportContents.values():
            capacity += GetTypeVolume(item.typeID, item.quantity)

        return capacity

    def GetCustomsCapacityTotal(self):
        return self.customsOffice.GetCapacity().capacity

    def GetCustomsCapacityAvailable(self):
        used = self.GetCustomsCapacityUsed()
        capacity = self.GetCustomsCapacityTotal()
        return capacity - used

    def CheckAvailableSpaceInCustoms(self, commodities = None):
        available = self.GetCustomsCapacityAvailable()
        required = self.GetCommodityVolume(commodities, self.importContents)
        if required - available > 1e-05:
            raise UserError('NotEnoughSpace', {'volume': required,
             'available': available})

    def GetSpaceportCapacityUsed(self):
        pin = self.planet.GetPin(self.spaceportPinID)
        if not pin:
            return 0
        capacity = pin.capacityUsed
        for item in self.importContents.values():
            capacity += GetTypeVolume(item.typeID, item.quantity)

        return capacity

    def GetSpaceportCapacityTotal(self):
        pin = self.planet.GetPin(self.spaceportPinID)
        if not pin:
            return 0
        return pin.GetCapacity()

    def IsItemHere(self, item):
        return item.itemID == self.customsOfficeID

    def GetSpaceportCapacityAvailable(self):
        used = self.GetSpaceportCapacityUsed()
        capacity = self.GetSpaceportCapacityTotal()
        return capacity - used

    def CheckAvailableSpaceInSpaceport(self, commodities = None):
        available = self.GetSpaceportCapacityAvailable()
        required = self.GetCommodityVolume(commodities, self.exportContents)
        if required - available > 1e-05:
            raise UserError('NotEnoughSpace', {'volume': required,
             'available': available})

    def RefreshHeaderInfo(self):
        self.spaceportGauge.state = uiconst.UI_HIDDEN
        if self.spaceportPinID is not None:
            pin = self.planet.GetPin(self.spaceportPinID)
            if not pin:
                return
            capacityUsed = self.GetSpaceportCapacityUsed()
            capacityMax = self.GetSpaceportCapacityTotal()
            self.spaceportGauge.state = uiconst.UI_DISABLED
            self.spaceportGauge.SetSubText(localization.GetByLabel('UI/PI/Common/StorageUsed', capacityUsed=capacityUsed, capacityMax=capacityMax))
            self.spaceportGauge.SetValue(capacityUsed / capacityMax)
        self.customsGauge.state = uiconst.UI_HIDDEN
        if self.customsOffice is not None:
            capacityUsed = self.GetCustomsCapacityUsed()
            capacityMax = self.GetCustomsCapacityTotal()
            self.customsGauge.state = uiconst.UI_DISABLED
            self.customsGauge.SetSubText(localization.GetByLabel('UI/PI/Common/StorageUsed', capacityUsed=capacityUsed, capacityMax=capacityMax))
            self.customsGauge.SetValue(capacityUsed / capacityMax)
        self.RefreshCostText()

    def GetCommodities(self, source):
        commods = {}
        for itemVoucher in source.itervalues():
            if itemVoucher.typeID not in commods:
                commods[itemVoucher.typeID] = itemVoucher.quantity
            else:
                commods[itemVoucher.typeID] += itemVoucher.quantity

        return commods

    def GetCost(self):
        cost = None
        pin = self.planet.GetPin(self.spaceportPinID)
        if pin is not None and self.taxRate is not None:
            cost = pin.GetExportTax(self.GetCommodities(self.exportContents), self.taxRate)
            cost += pin.GetImportTax(self.GetCommodities(self.importContents), self.taxRate)
        return cost

    def RefreshCostText(self):
        cost = self.GetCost()
        if cost is not None:
            costStr = FmtISK(cost)
            if cost > 0:
                costStr = '<color=red>%s</color>' % costStr
            self.transferCostLabel.text = localization.GetByLabel('UI/PI/Common/TransferCost', iskAmount=costStr)
        if self.taxRate is not None:
            self.windowCaption.text = localization.GetByLabel('UI/PI/Common/CustomsOfficeTaxRate', taxRate=self.taxRate * 100)
        else:
            self.windowCaption.text = localization.GetByLabel('UI/PI/Common/CustomsOfficeAccessDenied')

    def UpdateTaxRate(self):
        self.taxRate = eveMoniker.GetPlanetOrbitalRegistry(session.solarsystemid).GetTaxRate(self.id)
        self.RefreshCostText()

    def OnSpaceportComboChanged(self, comboItem, spaceportName, spaceportPinID, *args):
        if self.spaceportPinID != spaceportPinID:
            self.spaceportPinID = spaceportPinID
            self.ResetContents()

    def OnItemChange(self, item, change, location):
        locationIdx = const.ixLocationID
        if self.id not in (item[locationIdx], change.get(locationIdx, 'No location change')):
            return
        self.ResetContents()

    def OnRefreshPins(self, pinIDs):
        if not self or self.destroyed:
            return
        if self.spaceportPinID in pinIDs:
            self.ResetContents()

    def OnPlanetPinsChanged(self, planetID):
        if self.planet.planetID == planetID:
            self.ResetContents()

    def OnPlanetChangesSubmitted(self, planetID):
        if self.planet.planetID != planetID:
            return
        colony = self.planet.GetColony(session.charid)
        if not colony.GetImportEndpoints():
            self.CloseByUser()
        else:
            self.ResetContents()

    def OnSkyhookFirstActivation(self, skyhookID, planetID):
        if self.planet.planetID == planetID:
            self.Close()
            eve.Message('SkyhookReplacingPoco')

    def OnCustomsScrollDropData(self, dragObj, nodes, *args):
        scroll = getattr(nodes[0], 'scroll', None)
        if not scroll:
            return
        if scroll.name == 'spaceportList':
            self.ExportCommodity(nodes)
        elif scroll.name != 'customsList':
            self.MoveFromInventory(nodes)

    def OnSpaceportScrollDropData(self, dragObj, nodes, *args):
        scroll = getattr(nodes[0], 'scroll', None)
        if not scroll:
            return
        if scroll.name == 'customsList':
            self.ImportCommodity(nodes)
        else:
            raise UserError('CannotDropItemsOntoSpaceport')

    def ImportCommodity(self, nodes):
        if not self.spaceportPinID:
            raise UserError('NoSpaceportsAvailable')
        if self.taxRate is None:
            raise UserError('PortStandingCheckFail', {'corpName': (const.UE_OWNERID, self.customsOfficeItem.ownerID)})
        items = self.CommoditiesToTransfer(nodes, toSpaceport=True)
        for key, item in items.iteritems():
            self.RemoveStuff(key, item, self.customsOfficeContents)
            self.AddStuff(key, item, self.spaceportContents)
            if key in self.exportContents:
                self.RemoveStuff(key, item, self.exportContents)
            else:
                self.AddStuff(key, item, self.importContents)

        self.RefreshLists()

    def ExportCommodity(self, nodes):
        if self.taxRate is None:
            raise UserError('PortStandingCheckFail', {'corpName': (const.UE_OWNERID, self.customsOfficeItem.ownerID)})
        items = self.CommoditiesToTransfer(nodes)
        for key, item in items.iteritems():
            self.RemoveStuff(key, item, self.spaceportContents)
            self.AddStuff(key, item, self.customsOfficeContents)
            if key in self.importContents:
                self.RemoveStuff(key, item, self.importContents)
            else:
                self.AddStuff(key, item, self.exportContents)

        self.RefreshLists()

    def CommoditiesToTransfer(self, commodities, toSpaceport = False):
        toMove = {}
        for item in commodities:
            toMove[item.itemID, item.typeID] = utillib.KeyVal(name=planetCommonUI.GetProductNameAndTier(item.typeID), itemID=item.itemID, typeID=item.typeID, quantity=item.quantity, item=getattr(item, 'item', item))

        if len(commodities) == 1:
            if toSpaceport:
                available = self.GetSpaceportCapacityAvailable()
                required = self.GetCommodityVolume(toMove, self.exportContents)
            else:
                available = self.GetCustomsCapacityAvailable()
                required = self.GetCommodityVolume(toMove, self.importContents)
            if required > 0 and uicore.uilib.Key(uiconst.VK_SHIFT) or required - available > 1e-05:
                selectedItem = commodities[0]
                itemID = selectedItem.itemID
                typeID = selectedItem.typeID
                typeName = planetCommonUI.GetProductNameAndTier(typeID)
                availableQuantity = min(selectedItem.quantity, int(available / required * selectedItem.quantity))
                if availableQuantity > 0:
                    ret = uix.QtyPopup(availableQuantity, 1, availableQuantity, None, localization.GetByLabel('UI/PI/Common/QuantityToTransfer', typeName=typeName))
                    if ret and 'qty' in ret:
                        toMove[itemID, typeID].quantity = min(availableQuantity, max(1, ret['qty']))
                    else:
                        toMove = {}
        if toSpaceport:
            self.CheckAvailableSpaceInSpaceport(toMove)
        else:
            self.CheckAvailableSpaceInCustoms(toMove)
        return toMove

    def AddStuff(self, key, item, toDict):
        if key not in toDict:
            toDict[key] = utillib.KeyVal(itemID=item.itemID, typeID=item.typeID, quantity=item.quantity, name=item.name, item=item.item)
        else:
            toDict[key].quantity += item.quantity

    def RemoveStuff(self, key, item, fromDict):
        if key in fromDict:
            fromDict[key].quantity -= item.quantity
            if fromDict[key].quantity <= 0:
                del fromDict[key]

    def MoveFromInventory(self, nodes):
        allowableSources = ('xtriui.InvItem', 'listentry.InvItem')
        items = [ item for item in nodes if item.Get('__guid__', None) in allowableSources ]
        if len(items) > 0:
            sourceLocation = items[0].rec.locationID
            items = self.CommoditiesToTransfer([ item.item for item in items ])
            for key, item in items.iteritems():
                self.customsOffice.Add(key[0], sourceLocation, qty=item.quantity)

    def ConfirmCommodityTransfer(self, *args):
        if self.spaceportPinID is None:
            raise UserError('CannotImportEndpointNotFound')
        planet = sm.GetService('planetUI').GetCurrentPlanet()
        if planet is not None and planet.IsInEditMode():
            raise UserError('CannotImportExportInEditMode')
        if len(self.importContents) + len(self.exportContents) < 1:
            raise UserError('PleaseSelectCommoditiesToImport')
        importData = {key[0]:value.quantity for key, value in self.importContents.iteritems()}
        exportData = {key[1]:value.quantity for key, value in self.exportContents.iteritems()}
        try:
            customsOfficeInventory = sm.GetService('invCache').GetInventoryFromId(self.customsOfficeID)
            customsOfficeInventory.ImportExportWithPlanet(self.spaceportPinID, importData, exportData, self.taxRate)
        except UserError as e:
            if e.msg != 'TaxChanged':
                raise
            self.UpdateTaxRate()
            if self.taxRate is None:
                self.ResetContents()
                raise UserError('PortStandingCheckFail', {'corpName': (const.UE_OWNERID, self.customsOfficeItem.ownerID)})
            if eve.Message('CustomsOfficeTaxRateChanged', {'cost': self.GetCost()}, uiconst.YESNO) == uiconst.ID_YES:
                customsOfficeInventory.ImportExportWithPlanet(self.spaceportPinID, importData, exportData, self.taxRate)
            else:
                self.ResetContents()
