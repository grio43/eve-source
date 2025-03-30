#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpOfferEntry.py
import evetypes
import localization
import logging
import trinity
import uthread
import utillib
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from signals import Signal
from dogma import const as dogmaconst
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.utilMenu import ExpandedUtilMenu
from shipcosmetics.common.const import CosmeticsType
from cosmetics.common.cosmeticsConst import BACKGROUND_PATH_BY_TYPE
from shipcosmetics.client.licensegateway.licenseSignals import on_ship_cosmetics_license_change
from eve.client.script.ui.station.loyaltyPointStore.lpLabels import LPStoreEntryLabel
from eve.client.script.ui.station.loyaltyPointStore.lpUtil import GetItemText
from eve.client.script.ui.station.lpstoreRequirement import getContainerName, getLabelName
from eve.common.lib import appConst
from inventorycommon import const as invconst
from localization import GetByLabel
logger = logging.getLogger(__name__)

class LPOfferEntry(SE_BaseClassCore):
    __guid__ = 'listentry.LPOffer'
    iconSize = 64
    iconMargin = 2
    lineHeight = 1
    labelMargin = 6
    entryHeight = 88

    def ApplyAttributes(self, attributes):
        self.godma = sm.GetService('godma')
        self.lpSvc = sm.GetService('lpstore')
        self.node = attributes.node
        self.typeID = self.node.typeID
        self.qty = self.node.Get('qty', 1)
        self.reqItems = self.node.Get('reqItems', [])
        self.lootItems = self.node.Get('lootItems', [])
        self.lpOfferRequirementColumns = self.lpSvc.GetRequirements(self.node.corpID)
        self.requiredStandings = self.node.Get('requiredStandings', None)
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.amountEdit = None
        self._AddRewardColumn()
        self._AddRequirementColumns()
        if self.requiredStandings:
            self._AddStandingsColumn()
        self.AddBuyButton()

    def _AddRewardColumn(self):
        self.sr.rewardParent = Container(parent=self, name='rewardParent', align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN)
        self.sr.rewardIconParent = Container(parent=self.sr.rewardParent, name='rewardIconParent', align=uiconst.TOLEFT, width=self.entryHeight, padright=self.labelMargin)
        self.sr.rewardInfoIcon = InfoIcon(parent=self.sr.rewardIconParent, align=uiconst.TOPRIGHT, left=10, top=10)
        self.CreateIcon()
        self.AddRewardLabel()

    def CreateIcon(self):
        self.sr.icon = eveIcon.Icon(name='logoIcon', parent=self.sr.rewardIconParent, size=self.iconSize, ignoreSize=True, align=uiconst.CENTER, state=uiconst.UI_DISABLED)

    def _AddRequirementColumns(self):
        for requirement in self.lpOfferRequirementColumns:
            self._AddRequirementColumn(requirement)

    def _AddRequirementColumn(self, requirement):
        parentContainerName = getContainerName(requirement)
        labelName = getLabelName(requirement)
        notFulfilledHintPath = requirement.notFulfilledHintPath
        parentContainer = Container(name=parentContainerName, parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=True)
        label = LPStoreEntryLabel(parent=parentContainer, name=labelName, left=self.labelMargin, align=uiconst.CENTERLEFT, color=self.GetRowContentTint(), opacity=0.7 if self.node.isOwned else 1.0)
        self.sr[labelName] = label
        if notFulfilledHintPath:
            self.sr[labelName].hint = localization.GetByLabel(notFulfilledHintPath)

    def GetRowContentTint(self):
        return LPStoreEntryLabel.default_color

    def _AddStandingsColumn(self):
        ownerID = self.requiredStandings['ownerID']
        standingsValue = self.requiredStandings['value']
        container = Container(name='requiredStandingsParent', parent=self, align=uiconst.TOLEFT, clipChildren=True)
        standingsLabel = LPStoreEntryLabel(parent=container, name='requiredStandingsLabel', state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, left=self.labelMargin, text=u'{:6.2f}'.format(standingsValue))
        standingsLabel.hint = localization.GetByLabel('UI/Standings/Restricted', from_id=ownerID, to_id=session.charid, required_standing=standingsValue, current_standing=sm.GetService('standing').GetStandingWithSkillBonus(ownerID, session.charid))
        if not self.lpSvc.IsStandingsFulfilled(self.node):
            standingsLabel.color = Color.RED
        OwnerIcon(parent=container, name='requiredStandingsIcon', align=uiconst.CENTERLEFT, left=standingsLabel.width + 8, size=36, width=36, height=36, ownerID=ownerID)

    def AddRewardLabel(self):
        self.sr.rewardLabel = LPStoreEntryLabel(parent=self.sr.rewardParent, align=uiconst.TOTOP, padTop=4, maxLines=3)

    def AddBuyButton(self):
        buyBtnCont = Container(parent=self.sr.rewardParent, name='buyBtnCont', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP, height=HEIGHT_NORMAL, padTop=4)
        self.sr.buyBtn = Button(name='buyBtn', parent=buyBtnCont, label=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy'), align=uiconst.TOLEFT, func=self.OnBuyBtn)

    def OnBuyBtn(self, *_args):
        self.utilMenu = ExpandedUtilMenu(parent=uicore.layer.utilmenu, controller=self.sr.buyBtn, menuAlign=uiconst.TOPLEFT, GetUtilMenu=self.GetUtilMenu)

    def GetUtilMenu(self, menuParent):
        cont = ContainerAutoSize(parent=menuParent, align=uiconst.TOTOP, padding=appConst.defaultPadding)
        cont.GetEntryWidth = lambda mc = cont: 80
        self.amountEdit = SingleLineEditInteger(name='amountEdit', parent=cont, align=uiconst.TOTOP, minValue=1, maxValue=appConst.maxLoyaltyStoreBulkOffers, setvalue=1, label=localization.GetByLabel('UI/Common/Amount'), padding=(5, 10, 5, 0), OnReturn=self.Buy)
        Button(name='buyButton', parent=cont, align=uiconst.TOTOP, label=localization.GetByLabel('UI/LPStore/Accept'), func=self.Buy, padding=(5, 5, 5, 5))
        uicore.registry.SetFocus(self.amountEdit)

    def Buy(self, *_args):
        accepted = self.lpSvc.AcceptOffer(self.node, self.amountEdit.GetValue())
        if accepted == uiconst.ID_YES and self.utilMenu:
            self.utilMenu.Close()

    def Startup(self, *etc):
        pass

    def Load(self, data):
        uthread.pool('lpStore::LPOfferEntry.Load_Thread', self.Load_Thread, data)

    def Load_Thread(self, data):
        abstractInfo = None
        isCopy = False
        if evetypes.GetCategoryID(data.typeID) == appConst.categoryBlueprint:
            bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(typeID=data.typeID, runsRemaining=data.qty, original=False)
            abstractInfo = utillib.KeyVal(bpData=bpData)
            isCopy = True
        self.sr.rewardInfoIcon.OnClick = (sm.GetService('info').ShowInfo,
         data.typeID,
         None,
         abstractInfo)
        self.LoadIcon(data.typeID, isCopy)
        self.sr.rewardLabel.SetText(GetItemText(data.typeID, data.Get('qty', 1)))
        self._LoadRequirementColumns(data)
        self.CheckCanAcceptOffer(data)
        self.CreateTooltipPanel()

    def CreateTooltipPanel(self):
        self.LoadTooltipPanel = self.LoadRewardTooltipPanel

    def LoadIcon(self, typeID, isCopy):
        self.sr.icon.LoadIconByTypeID(typeID=typeID, size=64, ignoreSize=True, isCopy=isCopy)

    def CheckCanAcceptOffer(self, data):
        if self.lpSvc.CanAcceptOffer(data):
            self.sr.buyBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.buyBtn.state = uiconst.UI_HIDDEN
            self.sr.icon.spriteEffect = trinity.TR2_SFX_SOFTLIGHT
            self.sr.icon.SetRGBA(1, 0, 0, 1)
            self.sr.icon.saturation = 0.1

    def _GetRewardCostHint(self):
        requirements = {}
        for requirementColumn in self.lpOfferRequirementColumns:
            costLabelPath = requirementColumn.costLabelPath
            if costLabelPath:
                costName = requirementColumn.name
                costNameText = localization.GetByLabel(costLabelPath)
                costLabel = getLabelName(requirementColumn)
                costLabelText = self.sr[costLabel].text
                requirements[costName] = costNameText
                requirements[costLabel] = costLabelText

        return localization.GetByLabel('UI/LPStore/HintRewardCost', rewardLabel=self.sr.rewardLabel.text, **requirements)

    def GetValidSlotForType(self, typeID):
        return self.godma.GetPowerEffectForType(typeID)

    def _GetTooltipItemTypeSortPriority(self, typeID):
        categoryID = evetypes.GetCategoryID(typeID)
        if categoryID == invconst.categoryShip:
            priority = 1
        elif categoryID == invconst.categoryShipSkin:
            priority = 2
        elif categoryID == invconst.categoryModule:
            slotType = self.GetValidSlotForType(typeID)
            if slotType == dogmaconst.effectHiPower:
                priority = 3
            elif slotType == dogmaconst.effectMedPower:
                priority = 4
            elif slotType == dogmaconst.effectLoPower:
                priority = 5
            else:
                priority = 6
        elif categoryID == invconst.categoryDrone:
            priority = 7
        elif categoryID == invconst.categoryCharge:
            priority = 8
        else:
            priority = 9
        return priority

    def _CompareTooltipEntries(self, itemAndQuantity, otherItemAndQuantity):
        itemTypeID, _ = itemAndQuantity
        priority = self._GetTooltipItemTypeSortPriority(itemTypeID)
        otherItemTypeID, _ = otherItemAndQuantity
        otherPriority = self._GetTooltipItemTypeSortPriority(otherItemTypeID)
        return priority - otherPriority

    def LoadRewardTooltipPanel(self, tooltipPanel, *_args):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.cellSpacing = 2
        icon = eveIcon.Icon(parent=tooltipPanel, size=32, ignoreSize=True, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        icon.LoadIconByTypeID(typeID=self.typeID, isCopy=True)
        tooltipPanel.AddLabelMedium(text=GetItemText(self.typeID, self.qty), align=uiconst.CENTERLEFT)
        tooltipPanel.AddInfoIcon(self.typeID, align=uiconst.CENTERRIGHT)
        items = []
        isReqItems = False
        if len(self.reqItems):
            isReqItems = True
            tooltipPanel.AddDivider()
            tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/LPStore/RequiredItems'), colSpan=3)
            items = self.reqItems
        elif len(self.lootItems):
            tooltipPanel.AddDivider()
            tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Inventory/Filters/CritContains'), colSpan=3)
            items = self.lootItems
        items = sorted(items, cmp=self._CompareTooltipEntries)
        for typeID, qty in items:
            eveIcon.Icon(parent=tooltipPanel, size=24, ignoreSize=True, align=uiconst.CENTER, state=uiconst.UI_DISABLED, typeID=typeID)
            if not isReqItems:
                qty = evetypes.GetPortionSize(typeID) * qty
            itemLabel = tooltipPanel.AddLabelMedium(text=GetItemText(typeID, qty, checkIsBlueprint=False), align=uiconst.CENTERLEFT)
            tooltipPanel.AddInfoIcon(typeID, align=uiconst.CENTERRIGHT)
            if isReqItems and not self.lpSvc.HaveItem(typeID, qty):
                itemLabel.color = Color.RED

    def _LoadRequirementColumns(self, data):
        for requirementColumn in self.lpOfferRequirementColumns:
            self._LoadRequirementColumn(data, requirementColumn)

    def _LoadRequirementColumn(self, data, requirementColumn):
        requirementName = requirementColumn.name
        cost = data.Get(requirementName, 0)
        labelName = getLabelName(requirementColumn)
        amountName = requirementColumn.amountName
        amount = requirementColumn.formatAmount(cost)
        amountHintPath = requirementColumn.amountHintPath
        amountText = amount
        if amountHintPath:
            keywords = {amountName: amount}
            amountText = localization.GetByLabel(amountHintPath, **keywords)
        self.sr[labelName].SetText(amountText)
        if not requirementColumn.checkAmount(cost):
            self.sr[labelName].color = Color.RED

    def OnColumnResize(self, newCols):
        for container, width in zip(self.children[:], newCols):
            container.width = width

        self.sr.rewardLabel.width = self.sr.rewardParent.width - self.sr.rewardIconParent.width - self.sr.rewardLabel.left - self.labelMargin

    def GetHeight(self, node, _width):
        node.height = LPOfferEntry.entryHeight
        return node.height


on_cosmetic_license_purchase_failed = Signal('on_cosmetic_license_purchase_failed')

class CosmeticLogoLPOfferEntry(LPOfferEntry):

    def ApplyAttributes(self, attributes):
        super(CosmeticLogoLPOfferEntry, self).ApplyAttributes(attributes)
        self._showHilite = not self.node.isOwned
        on_ship_cosmetics_license_change.connect(self.OnLicenseStatusChanged)

    def _UpdateStatus(self):
        self._showHilite = not self.node.isOwned
        for requirement in self.lpOfferRequirementColumns:
            labelName = getLabelName(requirement)
            self.sr[labelName].opacity = 0.7 if self.node.isOwned else 1.0
            self.sr[labelName].color = self.GetRowContentTint()

        if self.sr.rewardlabel:
            self.sr.rewardLabel.opacity = 0.7 if self.node.isOwned else 1.0
            self.sr.rewardLabel.color = self.GetRowContentTint()
        self.offerCont.Flush()
        self.AddBuyButton()
        if self.sr and self.sr.icon:
            self.sr.icon.color = self.GetRowContentTint()
            if self.node:
                self.sr.icon.opacity = 0.7 if self.node.isOwned else 1.0

    def AddRewardLabel(self):
        rewardLabelContainer = Container(name='rewardLabelContainer', parent=self.sr.rewardParent, align=uiconst.TOALL)
        self.sr.rewardLabel = LPStoreEntryLabel(parent=rewardLabelContainer, align=uiconst.CENTERLEFT, padTop=4, maxLines=3, color=self.GetRowContentTint(), opacity=0.7 if self.node.isOwned else 1.0)

    def AddBuyButton(self):
        self.offerCont = Container(name='buyButtonParent', parent=self, align=uiconst.TOLEFT, clipChildren=True)
        if self.node.isOwned:
            rewardAquiredCont = Container(name='rewardAquiredCont', parent=self.offerCont, align=uiconst.TOLEFT, padRight=20)
            labelCont = Container(name='labelCont', parent=rewardAquiredCont, align=uiconst.TOLEFT)
            rewardAquiredLabel = LPStoreEntryLabel(name='rewardAquiredLabel', parent=labelCont, align=uiconst.CENTER, text=GetByLabel('UI/ShipCosmetics/RewardAcquired'), color=self.GetRowContentTint(), opacity=0.9 if self.node.isOwned else 1.0)
            labelWidth, labelHeight = rewardAquiredLabel.GetSize()
            labelCont.SetSize(labelWidth, labelHeight)
            tickCont = Container(name='tickCont', parent=rewardAquiredCont, align=uiconst.TORIGHT)
            rewardAquiredTick = Sprite(name='rewardAquiredTick', parent=tickCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png', width=34, height=34)
            tickWidth, tickHeight = rewardAquiredTick.GetSize()
            tickCont.SetSize(tickWidth, tickHeight)
            rewardAquiredWidth = labelWidth + tickWidth
            rewardAquiredHeight = labelHeight + tickHeight
            rewardAquiredCont.SetSize(rewardAquiredWidth, rewardAquiredHeight)
        else:
            self.sr.buyBtn = Button(name='buyBtn', parent=self.offerCont, label=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy'), align=uiconst.CENTERLEFT, padLeft=8, func=self.OnBuyBtn)

    def GetRowContentTint(self):
        if self.node.isOwned:
            return Color.HextoRGBA('#8DC169')
        return (1.0, 1.0, 1.0, 1.0)

    def CreateTooltipPanel(self):
        pass

    def CreateIcon(self):
        self.sr.icon = None

    def LoadIcon(self, typeID, isCopy):
        self.sr.icon = Sprite(name='logoIcon', parent=self.sr.rewardIconParent, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.GetIconTexturePath(), color=self.GetRowContentTint(), opacity=0.7 if self.node.isOwned else 1.0)
        self.sr.icon.width = self.iconSize
        self.sr.icon.height = self.iconSize

    def CheckCanAcceptOffer(self, data):
        if self.sr.buyBtn:
            if self.node.isOwned:
                self.sr.buyBtn.state = uiconst.UI_HIDDEN
                self.sr.buyBtn.disable(animate=False)
            elif self.lpSvc.CanAcceptOffer(data):
                self.sr.buyBtn.state = uiconst.UI_NORMAL
                self.sr.buyBtn.enable(animate=False)
            else:
                self.sr.buyBtn.state = uiconst.UI_DISABLED
                self.sr.buyBtn.disable(animate=False)
        self.sr.icon.color = self.GetRowContentTint()
        self.sr.icon.opacity = 0.7 if self.node.isOwned else 1.0

    def GetIconTexturePath(self):
        return None

    def OnBuyBtn(self, *_args):
        ok = uiconst.ID_NO
        try:
            ok = self.lpSvc.AcceptOffer(self.node, 1)
        except RuntimeError as ex:
            logger.exception('Could not complete LP Store purchase: %s' % ex)
            on_cosmetic_license_purchase_failed()

        if ok == uiconst.ID_NO:
            on_cosmetic_license_purchase_failed()

    def OnLicenseStatusChanged(self, licenseID, enable):
        licenseData = sm.GetService('cosmeticsLicenseSvc').get_by_ship_license_type_id(self.node.typeID)
        if licenseData and licenseData.licenseID == licenseID:
            self.node.isOwned = enable
            self._UpdateStatus()

    def OnColumnResize(self, newCols):
        super(CosmeticLogoLPOfferEntry, self).OnColumnResize(newCols)


class AllianceLogoLPOfferEntry(CosmeticLogoLPOfferEntry):

    def ApplyAttributes(self, attributes):
        super(AllianceLogoLPOfferEntry, self).ApplyAttributes(attributes)

    def GetIconTexturePath(self):
        return BACKGROUND_PATH_BY_TYPE.get(CosmeticsType.ALLIANCE_LOGO, '')


class CorporationLogoLPOfferEntry(CosmeticLogoLPOfferEntry):

    def ApplyAttributes(self, attributes):
        super(CorporationLogoLPOfferEntry, self).ApplyAttributes(attributes)

    def GetIconTexturePath(self):
        return BACKGROUND_PATH_BY_TYPE.get(CosmeticsType.CORPORATION_LOGO, '')
