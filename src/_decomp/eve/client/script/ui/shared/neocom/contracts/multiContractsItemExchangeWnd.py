#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\multiContractsItemExchangeWnd.py
from collections import defaultdict
import evetypes
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium, WndCaptionLabel
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.neocom.contracts.contractsDetailsWnd import GetContractItemMenu, GetBasicInfoText, AddBasicInfoRow, GetItemDamageText
from eve.client.script.util.contractutils import COL_PAY, FmtISKWithDescription, COL_GET
from eve.common.lib import appConst as const
from eve.common.script.sys.eveCfg import GetShipFlagLocationName
from eve.common.script.util.contractscommon import GetContractTitle, GetContractTypeText
from localization import GetByLabel
from carbonui import const as uiconst
from localization.formatters import FormatNumeric

class MultiContractsItemExchangeWnd(Window):
    default_windowID = 'multiContractsWnd'
    default_captionLabelPath = 'UI/Contracts/ContractsWindow/CreatedContracts'
    default_iconNum = 'res:/ui/Texture/WindowIcons/contractItemExchange.png'
    default_minSize = [520, 440]
    default_height = 480
    default_isStackable = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        contractIDs = attributes.contractIDs
        self.contractsByContractID = {}
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(0, -5, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        captionLabelPath = attributes.get('captionLabelPath', self.default_captionLabelPath)
        WndCaptionLabel(text=GetByLabel(captionLabelPath), parent=self.topParent)
        self.tabGroup = TabGroup(name='multiContractsWndTabs', parent=self.sr.main)
        self.contentCont = Container(name='contentCont', parent=self.sr.main, padding=const.defaultPadding)
        self.contentContTitleCont = Container(name='contentContTitleCont', parent=self.contentCont, align=uiconst.TOTOP, height=30)
        self.contractDetails = Container(name='contractDetails', parent=self.contentCont)
        self.titleLabel = EveLabelLarge(text='', parent=self.contentContTitleCont, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT, left=4)
        for i, contractID in enumerate(contractIDs):
            name = GetByLabel('UI/Contracts/ContractsWindow/ContractWithNum', contractNum=i + 1)
            self.tabGroup.AddTab(label=name, panel=self.contentCont, code=self, tabID=contractID, hint=name)

        self.tabGroup.AutoSelect()

    def Load(self, key, *args):
        contract = self.contractsByContractID.get(key, -1)
        if contract == -1:
            contract = sm.GetService('contracts').GetContract(key, force=True)
            self.contractsByContractID[key] = contract
        if not contract or contract == -1:
            pass
        self.contractDetails.Flush()
        c = contract.contract
        title = GetByLabel('UI/Contracts/ContractsService/ContractTitleAndType', contractTitle=GetContractTitle(c, contract.items), contractType=GetContractTypeText(c.type))
        self.titleLabel.text = title
        tabs = [115, 480]
        text = GetBasicInfoText(c)
        basicInfoParent = Container(name='infocontainer', parent=self.contractDetails, align=uiconst.TOTOP, padRight=const.defaultPadding)
        basicInfo = EveLabelMedium(text=text, parent=basicInfoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL, left=6)
        basicInfoParent.height = basicInfo.textheight + 5
        Line(parent=basicInfoParent, align=uiconst.TOTOP)
        self.AddList(tabs, contract)

    def AddList(self, tabs, contract):
        c = contract.contract
        text = ''
        if c.price > 0:
            if session.charid == c.issuerID:
                rowLabel = GetByLabel('UI/Contracts/ContractsWindow/BuyerWillPay')
            else:
                rowLabel = GetByLabel('UI/Contracts/ContractsWindow/YouWillPay')
            boldIsk = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=FmtISKWithDescription(c.price))
            rowInfo = '<color=%s>%s</color>' % (COL_PAY, boldIsk)
            text += AddBasicInfoRow(rowLabel, rowInfo)
        elif c.price == 0:
            if session.charid == c.issuerID:
                rowLabel = GetByLabel('UI/Contracts/ContractsWindow/BuyerWillGet')
            else:
                rowLabel = GetByLabel('UI/Contracts/ContractsWindow/YouWillGet')
            boldIsk = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=FmtISKWithDescription(0))
            rowInfo = '<color=%s>%s</color>' % (COL_GET, boldIsk)
            text += AddBasicInfoRow(rowLabel, rowInfo)
        infoParent = Container(name='infocontainer', parent=self.contractDetails, align=uiconst.TOTOP, width=const.defaultPadding)
        info = EveLabelLarge(text=text, parent=infoParent, top=const.defaultPadding, idx=0, tabs=tabs, state=uiconst.UI_NORMAL, left=6)
        infoParent.height = info.textheight + 2 * const.defaultPadding
        Line(parent=infoParent, align=uiconst.TOTOP)
        Line(parent=infoParent, align=uiconst.TOBOTTOM)
        if session.charid == c.issuerID:
            title = GetByLabel('UI/Contracts/ContractsWindow/BuyerWillGet')
        else:
            title = (GetByLabel('UI/Contracts/ContractsWindow/YouWillGet'),)
        self.ListItems(contract, '<color=%s>%s</color>' % (COL_GET, title))

    def ListItems(self, contract, title):
        inCrate = True
        shouldHideBlueprintInfo = contract.contract.status in [const.conStatusFinished, const.conStatusFinishedContractor]
        items = [ e for e in contract.items if e.inCrate == inCrate ]
        titleParent = Container(name='title', parent=self.contractDetails, align=uiconst.TOTOP, width=const.defaultPadding)
        boldTitle = GetByLabel('UI/Contracts/ContractsService/BoldGenericLabel', labelText=title)
        title = EveLabelLarge(text=boldTitle, parent=titleParent, top=6, idx=0, state=uiconst.UI_NORMAL, left=6)
        titleParent.height = title.textheight + 6
        self.sr.scroll = Scroll(parent=self.contractDetails, padding=const.defaultPadding)
        self.sr.scroll.sr.id = 'multiContractDetailScroll'
        scrolllist = []
        hdr = [GetByLabel('UI/Contracts/ContractsWindow/Name'),
         GetByLabel('UI/Inventory/ItemQuantityShort'),
         GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Common/Category'),
         GetByLabel('UI/Common/Details')]
        itemsByParentID = defaultdict(set)
        for eachItem in items:
            itemsByParentID[eachItem.parentID].add(eachItem)

        for item in items:
            if item.inCrate != inCrate:
                continue
            categoryID = evetypes.GetCategoryID(item.itemTypeID)
            details = ''
            isBlueprint = False
            isCopy = False
            if categoryID == const.categoryBlueprint:
                isBlueprint = True
                if item.copy == 1:
                    isCopy = True
                details = self.GetBlueprintsDetails(item, shouldHideBlueprintInfo)
            elif item.flagID:
                details = GetShipFlagLocationName(item.flagID)
            chld = ''
            sublevel = 0
            if item.parentID > 0:
                chld = ' '
                sublevel = 1
            mrdmg = GetItemDamageText(item)
            quantity = max(1, item.quantity) if item.quantity is not None else None
            scrolllist.append(GetFromClass(Item, {'itemID': item.itemID,
             'typeID': item.itemTypeID,
             'label': '%s%s<t>%s<t>%s<t>%s<t>%s%s' % (chld,
                       evetypes.GetName(item.itemTypeID),
                       FormatNumeric(quantity, useGrouping=True),
                       evetypes.GetGroupName(item.itemTypeID),
                       evetypes.GetCategoryName(item.itemTypeID),
                       details,
                       mrdmg),
             'getIcon': 1,
             'isBlueprint': isBlueprint,
             'isCopy': isCopy,
             'GetMenu': GetContractItemMenu,
             'sublevel': sublevel,
             'childrenItems': itemsByParentID.get(item.itemID, set())}))

        self.sr.scroll.Load(None, scrolllist, headers=hdr, noContentHint='UI/Contracts/ContractsWindow/NoItemsFound')

    def GetBlueprintsDetails(self, item, shouldHideBlueprintInfo):
        if item.copy == 1:
            if shouldHideBlueprintInfo:
                details = GetByLabel('UI/Contracts/ContractsService/BlueprintCopy')
            else:
                details = GetByLabel('UI/VirtualGoodsStore/BlueprintCopy', runs=item.licensedProductionRunsRemaining or 0, materialLevel=item.materialLevel or 0, productivityLevel=item.productivityLevel or 0)
        elif shouldHideBlueprintInfo:
            details = GetByLabel('UI/Contracts/ContractsService/BlueprintOriginal')
        else:
            details = GetByLabel('UI/VirtualGoodsStore/OriginalBlueprint', materialLevel=item.materialLevel or 0, productivityLevel=item.productivityLevel or 0)
        return details
