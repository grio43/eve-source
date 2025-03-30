#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelVariations.py
import eveicon
import eveui
import evetypes
import uthread2
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.info.shipInfoConst import DOWN_FRONT_RIGHT, TAB_VARIATIONS
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui import eveColor
from utillib import KeyVal
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui import TextHeader, Align, TextDetail, uiconst, TextColor, Density
from eve.client.script.ui.shared.info.shipInfoPanels.panelBase import PanelBase
from eve.client.script.ui.control.itemIcon import ItemIcon
from carbonui.control.scrollContainer import ScrollContainer
from eve.client.script.ui.shared.traits import TraitAttributeIcon, TraitsContainer
from carbonui.control.button import Button
from carbonui.button.const import ButtonVariant
from localization import GetByLabel
from carbonui.uianimations import animations
from eve.client.script.ui.shared.neocom.compare import TypeCompare
from eve.common.script.sys import idCheckers

class ShipItemIcon(ItemIcon):

    def __init__(self, *args, **kwargs):
        super(ShipItemIcon, self).__init__(*args, **kwargs)
        self.background_frame = eveui.Frame(name='background_frame', bgParent=self, color=eveColor.FOCUS_BLUE, opacity=0, padding=-1)

    def OnClick(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.SetBpDataForCopy()
        sm.GetService('info').ShowInfo(self.typeID, self.itemID, abstractinfo=KeyVal(fullBlueprintData=self.bpData), selectTabType=TAB_VARIATIONS)

    def OnMouseEnter(self, *args):
        if self.IsOmegaOverlayVisible():
            self.omegaOverlay.OnMouseEnter()
            return
        animations.MorphScalar(self.background_frame, 'opacity', duration=0.3, startVal=0, endVal=1, curveType=uiconst.ANIM_SMOOTH)

    def OnMouseExit(self, *args):
        if self.IsOmegaOverlayVisible():
            self.omegaOverlay.OnMouseExit()
            return
        animations.MorphScalar(self.background_frame, 'opacity', duration=0.3, startVal=1, endVal=0, curveType=uiconst.ANIM_SMOOTH)

    def GetHint(self):
        return ''

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddCaptionLarge(text=evetypes.GetName(self.typeID))
        wrapper = Container(align=Align.TOPRIGHT, width=300, height=450)
        traitCont = TraitsContainer(parent=wrapper, typeID=self.typeID, align=uiconst.TOTOP, traitAttributeIcons=True)
        wrapper.height = traitCont.height + 32
        tooltipPanel.AddCell(wrapper)

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2


class VariationsCard(eveui.ContainerAutoSize):
    default_align = Align.TOTOP
    default_alignMode = Align.TOTOP
    default_clipChildren = True

    def __init__(self, ship_type_id, *args, **kwargs):
        self._type_id = ship_type_id
        self._content = None
        self._item_icon = None
        super(VariationsCard, self).__init__(*args, **kwargs)
        self._construct_layout()

    def set_minimized(self):
        if self._item_icon.width == 64:
            return
        self._content.minHeight = 64
        self._item_icon.SetSize(64, 64)
        self._item_icon.SetTypeID(self._type_id)
        self.padBottom = 8

    def set_expanded(self):
        if self._item_icon.width == 92:
            return
        self._content.minHeight = 92
        self._item_icon.SetSize(92, 92)
        self._item_icon.SetTypeID(self._type_id)
        self.padBottom = 16

    def _construct_layout(self):
        eveui.Frame(name='background_frame', bgParent=self, texturePath='res:/UI/Texture/classes/Hangar/card_fill.png', cornerSize=16, opacity=0.05)
        self._content = eveui.ContainerAutoSize(parent=self, align=Align.TOTOP, alignMode=Align.TOTOP, minHeight=92, padding=8)
        icon_container = eveui.ContainerAutoSize(parent=self._content, align=Align.TOLEFT, padRight=8)
        self._item_icon = ShipItemIcon(parent=icon_container, align=Align.CENTER, typeID=self._type_id, height=92, width=92)
        top_container = eveui.Container(parent=self._content, align=Align.TOTOP, alignMode=Align.CENTERLEFT, height=20)
        ButtonIcon(parent=top_container, align=Align.TORIGHT, texturePath=eveicon.info, iconSize=16, width=20, height=20, padLeft=4, color=TextColor.SECONDARY, func=self._item_icon.OnClick)
        if sm.GetService('shipTree').IsInShipTree(self._type_id):
            ButtonIcon(parent=top_container, align=Align.TORIGHT, texturePath=eveicon.ship_tree, hint=GetByLabel('UI/InfoWindow/ShowInISIS'), iconSize=16, width=20, height=20, padLeft=4, color=TextColor.SECONDARY, func=self._open_ship_tree)
        texture = sm.GetService('bracket').GetBracketIcon(self._type_id)
        eveui.Sprite(parent=top_container, align=Align.CENTERLEFT, width=16, height=16, color=TextColor.NORMAL, texturePath=texture)
        text_container = eveui.Container(parent=top_container, align=Align.TOALL, padLeft=24)
        TextDetail(parent=text_container, align=Align.CENTERLEFT, text=evetypes.GetGroupName(self._type_id), color=TextColor.SECONDARY, maxLines=1, autoFadeSides=16)
        TextHeader(parent=self._content, align=Align.TOTOP, text=evetypes.GetName(self._type_id), padTop=4, padBottom=8, color=TextColor.HIGHLIGHT, maxLines=1, autoFadeSides=16)
        self._add_trait_icons(self._content)

    def _add_trait_icons(self, parent):
        trait_container = eveui.Container(name='ship_traits', parent=parent, align=Align.TOTOP, height=16, clipChildren=True)
        if self._type_id in cfg.infoBubbleTypeElements:
            data = cfg.infoBubbleTypeElements[self._type_id]
            attributeIDs = [ x[1] for x in sorted(data.items(), key=lambda d: int(d[0])) ]
            for index, attributeID in enumerate(attributeIDs):
                icon = TraitAttributeIcon(parent=trait_container, align=uiconst.CENTERLEFT, attributeID=attributeID, width=16, height=16, left=24 * index, iconOpacity=0.3, clipChildren=True)
                icon.OnClick = self.OnClick
                icon.isDragObject = True
                icon.GetDragData = self.GetDragData
                icon.OnDropData = self.OnDropData

    def _open_ship_tree(self, *args, **kwargs):
        sm.GetService('shipTreeUI').OpenAndShowShip(self._type_id)


class PanelVariations(PanelBase):

    def __init__(self, *args, **kwargs):
        self._variant_cards = []
        super(PanelVariations, self).__init__(*args, **kwargs)

    def _construct_content(self):
        uthread2.Yield()
        variants = evetypes.GetVariations(self._controller.type_id)
        variants.reverse()
        self._compare_button = Button(parent=self.rightCont, align=uiconst.TOBOTTOM, label=GetByLabel('UI/Compare/CompareAll'), func=self.on_compare, args=())
        self._expanded_scroll = ScrollContainer(parent=self.rightCont, name='expanded_scroll', align=Align.TOALL)
        self._content = ContainerAutoSize(parent=self._expanded_scroll, align=Align.TOTOP)
        for type_id in variants:
            card = VariationsCard(ship_type_id=type_id, parent=self._content, padBottom=16)
            self._variant_cards.append(card)

    def _enable_expanded_view(self):
        for card in self._variant_cards:
            card.set_expanded()

        self._compare_button.SetParent(self.rightCont, idx=0)
        self._content.SetParent(self._expanded_scroll)

    def _enable_minimized_view(self):
        for card in self._variant_cards:
            card.set_minimized()

        self._compare_button.SetParent(self.minimizedCont, idx=0)
        self._content.SetParent(self.content_scroll_minimized)

    def on_compare(self):
        wnd = TypeCompare.GetIfOpen()
        if wnd:
            wnd.AddVariantsOf(self.typeID)
        else:
            TypeCompare.Open(typeID=self.typeID)

    @classmethod
    def get_name(cls):
        return GetByLabel('UI/InfoWindow/TabNames/Variations')

    @classmethod
    def get_icon(cls):
        return eveicon.variation

    def get_camera_position(self):
        return DOWN_FRONT_RIGHT

    def get_tab_type(self):
        return TAB_VARIATIONS

    @classmethod
    def is_visible(cls, typeID, _itemID = None, _rec = None):
        if evetypes.GetVariations(typeID):
            return True
        return False
