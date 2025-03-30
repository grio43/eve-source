#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpOfferEntry2.py
from sys import maxint
from carbonui import uiconst, TextColor
from carbonui.control.button import Button
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.station.loyaltyPointStore.lpUtil import GetItemText
from eve.client.script.ui.station.loyaltyPointStore.selectQuantityWnd import SelectQuantityWnd
from eve.client.script.ui.station.lpstoreRequirement import LpRequirement, ISKRequirement, AnalysisKreditsRequirement
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eve.common.script.util.eveFormat import FmtISK, FmtISKAndRound
from eveui import Sprite
from inventorycommon import typeHelpers
from localization import GetByLabel

class LPOfferEntry2(SE_BaseClassCore):
    entryHeight = 88
    ColumnWidths = {GetByLabel('UI/LPStore/Reward'): 260,
     GetByLabel('UI/LPStore/cost'): 124,
     GetByLabel('UI/LPStore/RequiredItems'): 300,
     '': 100}
    Headers = (GetByLabel('UI/LPStore/Reward'),
     GetByLabel('UI/LPStore/cost'),
     GetByLabel('UI/LPStore/RequiredItems'),
     '')
    PER_REQUIRED_ITEM_HEIGHT = 20

    def ApplyAttributes(self, attributes):
        super(LPOfferEntry2, self).ApplyAttributes(attributes)
        self.lpSvc = sm.GetService('lpstore')
        self.node = attributes.node
        self.typeID = self.node.typeID
        self.iskBalance = self.node.Get('iskBalance')
        self.lpBalance = self.node.Get('lpBalance')
        self.akBalance = self.node.Get('akBalance')
        self.qty = self.node.Get('qty', 1)
        self.reqItems = self.node.Get('reqItems', [])
        self.lootItems = self.node.Get('lootItems', [])
        self.lpOfferRequirementColumns = self.lpSvc.GetRequirements(self.node.corpID)
        self.requiredStandings = self.node.Get('requiredStandings', None)
        self.allRequirementsMet = True
        self.costRequirementLabels = []
        self.itemRequirementLabels = []

    def GetMaxPurchaseable(self):
        maxQnt = maxint
        for requirement in self.reqItems:
            typeID, quantityNeeded = requirement
            maxQnt = min(int(self.lpSvc.GetInvenoryItemQuantity(typeID) / quantityNeeded), maxQnt)

        for requirement in self.lpOfferRequirementColumns:
            amount = self.node[requirement.name]
            if amount == 0:
                continue
            if requirement.name == LpRequirement.LP_REQUIREMENT_NAME:
                maxQnt = min(int(self.lpBalance / amount), maxQnt)
            elif requirement.name == ISKRequirement.ISK_REQUIREMENT_NAME:
                maxQnt = min(int(self.iskBalance / amount), maxQnt)
            elif requirement.name == AnalysisKreditsRequirement.AK_REQUIREMENT_NAME:
                maxQnt = min(int(self.akBalance / amount), maxQnt)

        return maxQnt

    def IsCostRequirementMet(self, requirement):
        amount = self.node[requirement.name]
        if amount == 0:
            return True
        requirementMet = True
        if requirement.name == LpRequirement.LP_REQUIREMENT_NAME:
            requirementMet = amount <= self.lpBalance
        elif requirement.name == ISKRequirement.ISK_REQUIREMENT_NAME:
            requirementMet = amount <= self.iskBalance
        elif requirement.name == AnalysisKreditsRequirement.AK_REQUIREMENT_NAME:
            requirementMet = amount <= self.akBalance
        return requirementMet

    def IsItemRequirementMet(self, requirement):
        typeID, quantity = requirement
        return self.lpSvc.HaveItem(typeID, quantity)

    def AreAllRequirementsMet(self):
        for requirement in self.lpOfferRequirementColumns:
            if not self.IsCostRequirementMet(requirement):
                return False

        for requirement in self.reqItems:
            if not self.IsItemRequirementMet(requirement):
                return False

        return True

    def OnMouseEnter(self, *args):
        super(LPOfferEntry2, self).OnMouseEnter(*args)
        for label, requirement in self.itemRequirementLabels:
            if not self.IsItemRequirementMet(requirement):
                label.color = TextColor.DANGER

        for label, requirement in self.costRequirementLabels:
            if not self.IsCostRequirementMet(requirement):
                label.color = TextColor.DANGER

    def OnMouseExit(self, *args):
        super(LPOfferEntry2, self).OnMouseExit(*args)
        for label, _requirement in self.itemRequirementLabels:
            label.color = TextColor.NORMAL

        for label, _requirement in self.costRequirementLabels:
            label.color = TextColor.NORMAL

    def _AddRewardColumn(self):
        rewardContWidth = LPOfferEntry2.ColumnWidths[GetByLabel('UI/LPStore/Reward')]
        rewardCont = Container(parent=self, name='rewardCont', align=uiconst.TOLEFT, width=rewardContWidth, state=uiconst.UI_PICKCHILDREN)
        spriteTransformCont = Container(parent=rewardCont, name='spriteTransformCont', align=uiconst.TOLEFT, width=LPOfferEntry2.entryHeight)
        spriteTransform = Transform(parent=spriteTransformCont, name='spriteTransform', align=uiconst.CENTER, width=64, height=64)
        techIcon = Sprite(name='techIcon', parent=spriteTransform, pos=(1, 0, 16, 16))
        techSprite = GetTechLevelIcon(techIcon, 1, self.typeID)
        rewardSprite = Sprite(parent=spriteTransform, name='rewardSprite', width=64, height=64, align=uiconst.CENTER)
        InfoIcon(parent=spriteTransform, align=uiconst.TOPRIGHT, typeID=self.typeID, idx=0)
        self.LoadIconByTypeID(self.typeID, rewardSprite)
        rewardNameCont = Container(parent=rewardCont, name='rewardNameCont', align=uiconst.TOALL)
        EveLabelMedium(parent=rewardNameCont, name='rewardLabel', text=GetItemText(self.typeID, self.qty), align=uiconst.CENTERLEFT, padLeft=8, maxWidth=rewardContWidth - 110, color=TextColor.NORMAL)

    def _AddCostColumn(self):
        costContWidth = LPOfferEntry2.ColumnWidths[GetByLabel('UI/LPStore/cost')]
        costCont = Container(parent=self, name='costCont', align=uiconst.TOLEFT, width=costContWidth, state=uiconst.UI_PICKCHILDREN)
        costRowsCont = ContainerAutoSize(parent=costCont, align=uiconst.CENTER, minWidth=costContWidth, width=costContWidth, alignMode=uiconst.TOTOP)
        for requirement in self.lpOfferRequirementColumns:
            amount = self.node[requirement.name]
            if amount == 0:
                continue
            amountName = requirement.amountName
            amountText = requirement.formatAmount(amount)
            amountHintPath = requirement.amountHintPath
            if amountHintPath:
                keywords = {amountName: amountText}
                amountText = GetByLabel(amountHintPath, **keywords)
            label = EveLabelMedium(parent=costRowsCont, align=uiconst.TOTOP, text=amountText, color=TextColor.NORMAL)
            self.costRequirementLabels.append((label, requirement))

    def _AddReqItemsColumn(self):
        reqItemsContWidth = LPOfferEntry2.ColumnWidths[GetByLabel('UI/LPStore/RequiredItems')]
        reqItemsCont = Container(parent=self, name='costCont', align=uiconst.TOLEFT, width=reqItemsContWidth, state=uiconst.UI_PICKCHILDREN)
        reqRowsCont = ContainerAutoSize(parent=reqItemsCont, align=uiconst.CENTER, minWidth=reqItemsContWidth, width=reqItemsContWidth, alignMode=uiconst.TOTOP)
        for req in self.reqItems:
            typeID, quantity = req
            requiredItemRowCont = ContainerAutoSize(name='requiredItemRowCont', parent=reqRowsCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
            label = EveLabelMedium(name='requiredItem', parent=requiredItemRowCont, text=GetItemText(typeID, quantity), align=uiconst.TOTOP, color=TextColor.NORMAL, state=uiconst.UI_NORMAL)
            textWidth, _height = EveLabelMedium.MeasureTextSize(GetItemText(typeID, quantity))
            infoIconOffset = min(reqItemsContWidth - InfoIcon.default_width, textWidth + 5)
            InfoIcon(parent=requiredItemRowCont, align=uiconst.TOPLEFT, typeID=typeID, idx=0, left=infoIconOffset)
            self.itemRequirementLabels.append((label, req))

    def _AddPurchaseButtonColumn(self):
        purchaseButtonContWidth = LPOfferEntry2.ColumnWidths['']
        purchaseButtonCont = Container(parent=self, name='costCont', align=uiconst.TOLEFT, width=purchaseButtonContWidth, state=uiconst.UI_PICKCHILDREN)
        Button(parent=purchaseButtonCont, align=uiconst.CENTER, label='Purchase', enabled=self.AreAllRequirementsMet(), func=self.AmountConfirmationDialogue)

    def AmountConfirmationDialogue(self, *args):
        SelectQuantityWnd.ConfirmPurchaseQuantity(GetItemText(self.typeID, self.qty), self.GetMaxPurchaseable(), self.Purchase)

    def Purchase(self, amount):
        self.lpSvc.AcceptOffer(self.node, amount)

    def Load(self, data):
        self.Flush()
        self._AddRewardColumn()
        self._AddCostColumn()
        self._AddReqItemsColumn()
        self._AddPurchaseButtonColumn()

    def GetHeight(self, node, _width):
        return max(LPOfferEntry2.entryHeight, len(node.Get('reqItems', [])) * LPOfferEntry2.PER_REQUIRED_ITEM_HEIGHT)

    def LoadIconByTypeID(object, typeID, sprite):
        sm.GetService('photo').GetIconByType(sprite, typeID, itemID=None, size=None, ignoreSize=False, isCopy=False)

    def LoadTooltipPanel(self, tooltipPanel, *_args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        avgPrice = typeHelpers.GetAveragePrice(self.typeID)
        if avgPrice is None:
            avgPrice = 0
        estimatedMaketPrice = self.qty * avgPrice
        estimatedPriceString = GetByLabel('UI/Inventory/EstIskPrice', iskString=FmtISKAndRound(estimatedMaketPrice, False))
        tooltipPanel.AddLabelSmall(text=estimatedPriceString)
