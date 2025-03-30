#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\redeem\redeemItem.py
from carbon.common.lib.const import MIN, HOUR, DAY
from carbon.common.script.util.commonutils import GetAttrs
from carbonui import uiconst, fontconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelSmall, EveLabelSmallBold, Label
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.shared.container import ItemSortData
from eve.client.script.ui.shared.redeem.redeemUiConst import CREATION_DATE_SORT_KEY, EXPIRY_DATE_SORT_KEY
from eve.client.script.ui.shared.tooltip.blueprints import AddBlueprintInfo
from evetypes import GetName, GetCategoryID, GetGroupID
from gametime import GetWallclockTime
from inventorycommon.const import flagHangar
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten, TIME_CATEGORY_DAY, TIME_CATEGORY_HOUR, TIME_CATEGORY_MINUTE, TIME_CATEGORY_SECOND
from utillib import KeyVal
PICTURE_CONTAINER_HEIGHT = 75
ITEM_NAME_HEIGHT = 32
ITEM_DESCRIPTION_HEIGHT = 15
ITEM_EXPIRY_HEIGHT = 15
BOTTOM_PADDING = 3
ITEM_NAME_PADDING = 4
REDEEM_ITEM_WIDTH = 140
PICTURE_SIZE = 64

def GetRedeemItemHeight():
    return PICTURE_CONTAINER_HEIGHT + ITEM_NAME_HEIGHT + ITEM_DESCRIPTION_HEIGHT + ITEM_EXPIRY_HEIGHT + BOTTOM_PADDING


def GetRedeemItemHeightWithoutDescription():
    return GetRedeemItemHeight() - ITEM_DESCRIPTION_HEIGHT


class RedeemItemEntryUnderlay(ListEntryUnderlay):
    OPACITY_IDLE = 0.03
    OPACITY_HOVER = 0.3
    OPACITY_MOUSEDOWN = 0.35
    OPACITY_SELECTED = 0.2
    IDLE_COLOR = (1.0,
     1.0,
     1.0,
     OPACITY_IDLE)
    MOUSEDOWN_COLOR = (1.0,
     1.0,
     1.0,
     OPACITY_MOUSEDOWN)
    SELECTION_COLOR = (1.0,
     1.0,
     1.0,
     OPACITY_SELECTED)
    default_color = IDLE_COLOR
    default_opacity = OPACITY_IDLE

    def OnMouseDown(self, *args):
        super(RedeemItemEntryUnderlay, self).OnMouseDown(*args)
        self.color = self.MOUSEDOWN_COLOR

    def OnMouseUp(self, *args):
        super(RedeemItemEntryUnderlay, self).OnMouseUp(*args)
        self.color = self.SELECTION_COLOR


class RedeemItem(SE_BaseClassCore):
    __guid__ = 'xtriui.InvItem'
    default_name = 'RedeemItem'
    default_showInfo = True
    default_showDescription = True

    def ApplyAttributes(self, attributes):
        super(RedeemItem, self).ApplyAttributes(attributes)
        self.showInfo = attributes.get('showInfo', self.default_showInfo)
        self.showDescription = attributes.get('showDescription', self.default_showDescription)
        self.redeemSvc = sm.GetService('redeem')

    @classmethod
    def GetEntryHeight(cls):
        return GetRedeemItemHeight()

    @classmethod
    def GetEntryWidth(cls):
        return REDEEM_ITEM_WIDTH

    @classmethod
    def GetEntryColMargin(cls):
        return 16

    @classmethod
    def IsFixedWidth(cls):
        return True

    def ConstructLayout(self):
        self.ConstructHiliteFill()
        self.itemContainer = Container(parent=self, name='itemContainer', align=uiconst.NOALIGN, width=REDEEM_ITEM_WIDTH, height=GetRedeemItemHeight() if self.showDescription else GetRedeemItemHeightWithoutDescription(), state=uiconst.UI_PICKCHILDREN)
        self.ConstructShowInfo()
        self.ConstructAutoInjectIcon()
        self.ConstructPicture()
        self.ConstructName()
        self.ConstructDescription()
        self.ConstructExpiry()

    def ConstructShowInfo(self):
        if not self.showInfo:
            return
        bpData = self.GetBpData()
        if bpData:
            abstractInfo = KeyVal(fullBlueprintData=bpData)
        else:
            abstractInfo = None
        InfoIcon(parent=self.itemContainer, align=uiconst.TOPRIGHT, idx=0, top=8, left=8, itemID=self.itemID, typeID=self.typeID, abstractinfo=abstractInfo)

    def GetBpData(self):
        bpInfo = self.token.blueprintInfo
        if not bpInfo:
            return None
        bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(typeID=self.typeID, original=not bpInfo.isCopy, runsRemaining=bpInfo.runs, materialEfficiency=bpInfo.materialEfficiency, timeEfficiency=bpInfo.timeEfficiency)
        return bpData

    def ConstructAutoInjectIcon(self):
        if not self.isAutoInject:
            return
        Sprite(parent=self.itemContainer, align=uiconst.TOPLEFT, idx=0, pos=(8, 8, 24, 24), texturePath='res://UI/Texture/Classes/RedeemPanel/autoInject.png', hint=GetByLabel('UI/RedeemWindow/AutoInjectHint'))

    def ConstructPicture(self):
        pictureParent = Container(parent=self.itemContainer, name='pictureParent', align=uiconst.TOTOP, height=PICTURE_CONTAINER_HEIGHT, state=uiconst.UI_DISABLED)
        pictureCenter = Container(parent=pictureParent, name='pictureCenter', align=uiconst.CENTER, width=PICTURE_SIZE, height=PICTURE_SIZE)
        itemPicture = Icon(parent=pictureCenter, align=uiconst.CENTER, width=pictureCenter.height, height=pictureCenter.width)
        isCopy = self.token.blueprintInfo and self.token.blueprintInfo.isCopy
        itemPicture.LoadIconByTypeID(typeID=self.typeID, ignoreSize=True, isCopy=isCopy)
        quantityContainer = ContainerAutoSize(parent=pictureCenter, idx=0, name='qtypar', pos=(2, 48, 0, 0), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, bgColor=(0, 0, 0, 0.9))
        Label(parent=quantityContainer, maxLines=1, bold=True, fontsize=fontconst.EVE_SMALL_FONTSIZE, opacity=1.0, padding=(4, 1, 4, 0), text=self.quantity)

    def ConstructName(self):
        nameContainer = Container(parent=self.itemContainer, name='nameContainer', align=uiconst.TOTOP, height=ITEM_NAME_HEIGHT)
        self.itemName = EveLabelMediumBold(parent=nameContainer, name='redeemItemName', align=uiconst.CENTER, maxLines=2, width=self.itemContainer.width - ITEM_NAME_PADDING * 2, text='<center>' + GetName(self.typeID) + '</center>')

    def ConstructDescription(self):
        if self.showDescription:
            maxWidth = self.itemContainer.width
            descriptionContainer = Container(parent=self.itemContainer, name='descriptionContainer', align=uiconst.TOTOP, height=ITEM_DESCRIPTION_HEIGHT, description=self.description)
            itemDescription = EveLabelSmall(parent=descriptionContainer, name='redeemItemDescription', align=uiconst.TOTOP, padLeft=4, maxWidth=maxWidth, maxLines=1, showEllipsis=True)
            if self.description:
                itemDescription.text = '<center>' + self.description + '</center>'

    def ConstructExpiry(self):
        expiryContainer = Container(parent=self.itemContainer, name='expiryContainer', align=uiconst.TOTOP, height=ITEM_EXPIRY_HEIGHT)
        self.itemExpiryDate = EveLabelSmallBold(parent=expiryContainer, name='redeemItemExpiryDate', align=uiconst.TOALL, color=(1.0, 0.539, 0.0, 1.0), padLeft=4)
        self.SetExpiryDate()

    def SetExpiryDate(self):
        if self.expireDateTime and self.expireDateTime > 0:
            now = GetWallclockTime()
            timeLeft = self.expireDateTime - now
            if timeLeft > 0:
                if timeLeft > DAY:
                    time = FormatTimeIntervalShortWritten(timeLeft, showFrom=TIME_CATEGORY_DAY, showTo=TIME_CATEGORY_HOUR)
                elif timeLeft > HOUR:
                    time = FormatTimeIntervalShortWritten(timeLeft, showFrom=TIME_CATEGORY_HOUR, showTo=TIME_CATEGORY_MINUTE)
                elif timeLeft > MIN:
                    time = FormatTimeIntervalShortWritten(timeLeft, showFrom=TIME_CATEGORY_MINUTE, showTo=TIME_CATEGORY_SECOND)
                else:
                    time = FormatTimeIntervalShortWritten(timeLeft, showFrom=TIME_CATEGORY_SECOND, showTo=TIME_CATEGORY_SECOND)
                text = GetByLabel('UI/RedeemWindow/RedeemExpires', timeLeftToExpiry=time)
                self.itemExpiryDate.fontsize = 9
                self.itemExpiryDate.text = '<center>' + text + '</center>'
            else:
                self.itemExpiryDate.fontsize = 9
                (self.itemExpiryDate.SetTextColor(eveColor.DANGER_RED),)
                self.itemExpiryDate.text = '<center>%s</center>' % GetByLabel('UI/Generic/Expired')

    def Load(self, node):
        self.sr.node = node
        self.token = node.item
        self.itemID = None
        self.typeID = int(self.token.typeID)
        self.ownerID = session.charid
        self.locationID = session.stationid
        self.flagID = flagHangar
        self.quantity = int(self.token.quantity)
        self.categoryID = GetCategoryID(self.token.typeID)
        self.groupID = GetGroupID(self.token.typeID)
        self.customInfo = None
        self.stacksize = None
        self.singleton = None
        self.tokenID = self.token.tokenID
        self.massTokenID = self.token.massTokenID
        self.stationID = self.token.stationID
        self.expireDateTime = self.token.expireDateTime
        self.createDateTime = self.token.dateTime
        self.description = self.token.description
        self.isAutoInject = self.token.isAutoInject
        self.Flush()
        self.ConstructLayout()
        if self.sr.node.Get('selected', 0):
            self.Select(animate=False)
        else:
            self.Deselect(animate=False)

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)
            else:
                self.sr.node.scroll.SelectNode(self.sr.node)
                eve.Message('ListEntryClick')

    def OnMouseDown(self, *args):
        super(RedeemItem, self).OnMouseDown(*args)
        self._hiliteFill.OnMouseDown(*args)

    def OnMouseUp(self, *args):
        super(RedeemItem, self).OnMouseUp(*args)
        self._hiliteFill.OnMouseUp(*args)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.description, wrapWidth=400)
        bpInfo = self.token.blueprintInfo
        if bpInfo:
            if bpInfo.materialEfficiency or bpInfo.timeEfficiency:
                bpData = self.GetBpData()
                AddBlueprintInfo(tooltipPanel, bpData=bpData)
            else:
                text = GetByLabel('UI/Industry/CopyRunsRemaining', runsRemaining=bpInfo.runs)
                tooltipPanel.AddLabelMedium(text=text, wrapWidth=400)


class RedeemItemSortData(ItemSortData):

    def __init__(self, rec):
        super(RedeemItemSortData, self).__init__(rec)
        self.createDataTime = rec.dateTime
        self.expireDateTime = rec.expireDateTime

    def GetSortKey(self, sortby, direction):
        baseSortKey = (self.createDataTime,
         self.name,
         self.typeName,
         self.quantity,
         self.itemID,
         self.rec)
        if sortby == CREATION_DATE_SORT_KEY:
            return (self.createDataTime,) + baseSortKey
        if sortby == EXPIRY_DATE_SORT_KEY:
            expirySortVal = self.expireDateTime or const.maxLong
            return (expirySortVal,) + baseSortKey
        return super(RedeemItemSortData, self).GetSortKey(sortby, direction)


class DraggableRedeemItem(RedeemItem):
    default_showInfo = False
    default_showDescription = False
    isDragObject = True
    isDropLocation = False
    TOOLTIP_LABEL_PATH = 'UI/RedeemWindow/DragAndDropToGive'

    @classmethod
    def GetEntryHeight(cls):
        return GetRedeemItemHeightWithoutDescription()

    def GetDragData(self, *args):
        if not self.sr.node:
            return
        nodesToDrag = []
        for node in self.sr.node.scroll.GetSelectedNodes(self.sr.node):
            nodeToDrag = node.Copy()
            nodeToDrag.Set('tokenID', node.tokenID)
            nodeToDrag.Set('massTokenID', node.massTokenID)
            nodesToDrag.append(nodeToDrag)

        return nodesToDrag

    def OnDragEnter(self, dragObj, nodes):
        if self.sr.node.container:
            self.sr.node.container.OnDragEnter(dragObj, nodes)

    def OnDragExit(self, dragObj, nodes):
        if self.sr.node.container:
            self.sr.node.container.OnDragExit(dragObj, nodes)

    def OnDropData(self, dragObj, nodes):
        if len(nodes) and getattr(nodes[0], 'scroll', None):
            nodes[0].scroll.ClearSelection()
        nodesToDrop = [ node for node in nodes if isinstance(node, RedeemItem) ]
        if nodesToDrop and GetAttrs(self, 'sr', 'node', 'container', 'OnDropData'):
            self.sr.node.container.OnDropData(dragObj, nodesToDrop)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=GetByLabel(self.TOOLTIP_LABEL_PATH))
