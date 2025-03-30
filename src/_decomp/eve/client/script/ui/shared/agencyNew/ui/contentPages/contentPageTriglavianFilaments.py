#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageTriglavianFilaments.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge, EveLabelSmall
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.moreIcon import DescriptionIcon
from eve.client.script.ui.shared.agencyNew.ui.contentPages.baseContentPage import BaseContentPage
from carbonui.control.section import Section
from localization import GetByLabel
import evetypes
from dogma.const import attributeMicroJumpPortalMaxShipCandidates
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.control.tooltips import TooltipPanel
OUTBOUND_MARKET_GROUP_ID = 2756
INBOUND_MARKET_GROUP_ID = 2757
MINOR_VICTORY_FILAMENTS = {'title': 'UI/Agency/TriglavianSpace/MinorVictoryFilamentsTitle',
 'description': 'UI/Agency/TriglavianSpace/MinorVictoryFilamentsDescription',
 'icon': 'res:/UI/Texture/Icons/Inventory/FilamentTSpace1.png',
 'types': [56065, 56066, 56067]}
LOCAL_K_FILAMENTS = {'title': 'UI/Agency/TriglavianSpace/LocalFilamentsTitle',
 'description': 'UI/Agency/TriglavianSpace/LocalFilamentsDescription',
 'icon': 'res:/UI/Texture/Icons/Inventory/FilamentTSpace2.png',
 'types': [56068, 56069]}
CLADE_FILAMENTS = {'title': 'UI/Agency/TriglavianSpace/CladeFilamentsTitle',
 'description': 'UI/Agency/TriglavianSpace/CladeFilamentsDescription',
 'icon': 'res:/UI/Texture/Icons/Inventory/FilamentTSpace2.png',
 'types': [56070,
           56071,
           56072,
           56073,
           56074,
           56075]}
SYSTEM_TYPE_FILAMENTS = {'title': 'UI/Agency/TriglavianSpace/SystemTypeFilamentsTitle',
 'description': 'UI/Agency/TriglavianSpace/SystemTypeFilamentsDescription',
 'icon': 'res:/UI/Texture/Icons/Inventory/FilamentTSpace3.png',
 'types': [56076,
           56077,
           56078,
           56079,
           56080,
           56081]}

class ContentPageTriglavianFilaments(BaseContentPage):
    default_name = 'ContentPageTriglavianFilaments'

    def ConstructLayout(self):
        super(ContentPageTriglavianFilaments, self).ConstructLayout()
        self.ConstructLeft()
        self.ConstructRight()

    def ConstructLeft(self):
        container = Container(name='leftContainer', parent=self, align=uiconst.TOLEFT, width=500, padRight=5)
        self.ConstructInboundFilaments(container)

    def ConstructRight(self):
        container = Container(name='rightContainer', parent=self, align=uiconst.TOLEFT, width=500, padLeft=5)
        self.ConstructOutboundFilaments(container)

    def ConstructOutboundFilaments(self, container):
        section = Section(name='outboundFilamentsContainer', parent=container, align=uiconst.TOALL, headerText=GetByLabel('UI/Agency/TriglavianSpace/OutboundFilamentsSection'))
        marketButtonContainer = Container(parent=section, align=uiconst.TOBOTTOM, height=28)
        Button(parent=marketButtonContainer, align=uiconst.TORIGHT, label=GetByLabel('UI/Commands/OpenMarket'), texturePath='res:/UI/Texture/WindowIcons/market.png', func=lambda arg: self._OpenMarketGroup(OUTBOUND_MARKET_GROUP_ID))
        FilamentGroup(parent=section, group=LOCAL_K_FILAMENTS)
        FilamentGroup(parent=section, group=MINOR_VICTORY_FILAMENTS, padBottom=12)
        scroll = ScrollContainer(parent=section, align=uiconst.TOALL)
        EveLabelMedium(parent=scroll, align=uiconst.TOTOP, padBottom=20, text=GetByLabel('UI/Agency/TriglavianSpace/OutboundFilamentsDescription'))

    def ConstructInboundFilaments(self, container):
        section = Section(name='inboundFilamentsContainer', parent=container, align=uiconst.TOALL, headerText=GetByLabel('UI/Agency/TriglavianSpace/InboundFilamentsSection'))
        marketButtonContainer = Container(parent=section, align=uiconst.TOBOTTOM, height=28)
        Button(parent=marketButtonContainer, align=uiconst.TORIGHT, label=GetByLabel('UI/Commands/OpenMarket'), texturePath='res:/UI/Texture/WindowIcons/market.png', func=lambda arg: self._OpenMarketGroup(INBOUND_MARKET_GROUP_ID))
        FilamentGroup(parent=section, group=SYSTEM_TYPE_FILAMENTS)
        FilamentGroup(parent=section, group=CLADE_FILAMENTS, padBottom=12)
        scroll = ScrollContainer(parent=section, align=uiconst.TOALL)
        EveLabelMedium(parent=scroll, align=uiconst.TOTOP, padBottom=20, text=GetByLabel('UI/Agency/TriglavianSpace/InboundFilamentsDescription'))

    def _OpenMarketGroup(self, marketGroupID):
        sm.GetService('marketutils').ShowMarketGroupWithTypes(marketGroupID)


class FilamentGroup(Container):
    default_align = uiconst.TOBOTTOM
    default_height = 140

    def ApplyAttributes(self, attributes):
        super(FilamentGroup, self).ApplyAttributes(attributes)
        group = attributes.group
        iconContainer = Container(parent=self, align=uiconst.TOLEFT, width=40, padRight=8)
        Sprite(parent=iconContainer, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, height=40, texturePath=group['icon'])
        EveLabelLarge(parent=self, align=uiconst.TOTOP, top=4, text=GetByLabel(group['title']))
        scroll = ScrollContainer(parent=self, align=uiconst.TOALL, top=8, padBottom=8)
        EveLabelMedium(parent=scroll, align=uiconst.TOTOP, text=GetByLabel(group['description']))
        DescriptionIcon(parent=self, align=uiconst.TOPRIGHT, tooltipPanelClassInfo=FilamentGroupTooltip(group))


class FilamentGroupTooltip(TooltipBaseWrapper):

    def __init__(self, filamentGroup, **kwargs):
        super(FilamentGroupTooltip, self).__init__(**kwargs)
        self.filamentGroup = filamentGroup

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.cellSpacing = 6
        self.tooltipPanel.margin = 12
        self.tooltipPanel.AddLabelLarge(text=GetByLabel(self.filamentGroup['title']), padBottom=6, wrapWidth=400)
        listItemList = []
        for typeID in self.filamentGroup['types']:
            listItem = FilamentListItem(typeID)
            listItemList.append(listItem)

        cellWidth = max((listItem.width for listItem in listItemList))
        for listItem in listItemList:
            listItem.width = cellWidth
            self.tooltipPanel.AddCell(listItem)

        return self.tooltipPanel


class FilamentListItem(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_height = 40
    default_width = 600
    default_clipChildren = True
    isDragObject = True

    def __init__(self, typeID, **kwargs):
        super(FilamentListItem, self).__init__(**kwargs)
        dogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        maxShips = int(dogmaStaticSvc.GetTypeAttribute2(typeID, attributeMicroJumpPortalMaxShipCandidates))
        self.bgFill = Frame(parent=self, opacity=0, cornerSize=9, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png')
        self.itemIcon = ItemIcon(parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOLEFT, width=40, padRight=4, typeID=typeID)
        self.OnClick = self.itemIcon.OnClick
        self.GetMenu = self.itemIcon.GetMenu
        self.GetDragData = self.itemIcon.GetDragData
        label = EveLabelMedium(parent=self, align=uiconst.TOTOP, text=evetypes.GetName(typeID), maxLines=1)
        EveLabelSmall(parent=self, align=uiconst.TOTOP, color=(0.7, 0.7, 0.7, 0.7), text=GetByLabel('UI/Agency/TriglavianSpace/MaxShips', amount=maxShips))
        _, labelWidth = label.GetWidthToIndex(-1)
        self.width = self.itemIcon.displayWidth + self.itemIcon.padRight + labelWidth

    def OnMouseEnter(self, *args):
        uicore.animations.FadeTo(self.bgFill, endVal=0.1, duration=0.1)

    def OnMouseExit(self, *args):
        uicore.animations.FadeOut(self.bgFill, duration=0.3)
