#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelIndustry.py
import eveicon
import trinity
import eveui
import evetypes
import localization
import uthread2
from carbonui import Align, TextBody, Density, TextColor, uiconst, TextDetail
from carbonui.primitives.collapsibleContainer import CollapsibleContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.shared.info.shipInfoConst import TOP_DOWN_NOSE_DOWN, TAB_INDUSTRY, CONTENT_PADDING, EXPANDED
from evetypes import TypeNotFoundException
from inventorycommon.const import typeCorporation
from npcs.npccorporations import get_npc_corporation_name, get_designer_description
from typematerials.data import get_type_materials_by_id
from eve.client.script.ui.shared.info.shipInfoPanels.panelBase import PanelBase
from eve.client.script.ui.shared.info.collapseGroup import CollapseGroup
from eve.client.script.ui.shared.info.auraHintSection import AuraHintSection
from eve.client.script.ui.shared.info.shipInfoListEntries import ListEntryEveType
DESIGNER_DESCRIPTION_MOCK = 'This Corp Excels as a ship manufacturer, integrating cutting-edge secret technology and precision engineering to craft superior spacecraft'

class BluePrintSection(eveui.ContainerAutoSize):
    default_icon_size = 64
    default_padBottom = 4
    default_align = Align.TOTOP
    default_height = 96
    icon_size = None

    def __init__(self, type_id, icon_size = None, show_background_graphic = True, *args, **kwargs):
        super(BluePrintSection, self).__init__(*args, **kwargs)
        self.type_id = type_id
        self.icon_size = icon_size if icon_size else self.default_icon_size
        self.show_background_graphic = show_background_graphic
        self._construct_content()

    def on_click_market_details(self, _object):
        sm.StartService('marketutils').ShowMarketDetails(self.type_id, None)

    def on_click_view_contract(self, _object):
        sm.GetService('contracts').FindRelated(self.type_id, None, None, None, None, None)

    def _get_product_name(self):
        product_type_id = sm.GetService('blueprintSvc').GetBlueprintType(self.type_id).productTypeID
        return evetypes.GetName(product_type_id or self.type_id)

    def _construct_item_icon(self):
        item_icon_cont = eveui.Container(parent=self.container, align=Align.TOLEFT, width=self.icon_size * 1.5 if self.show_background_graphic else self.icon_size, padRight=8, padLeft=0 if self.show_background_graphic else 8)
        ItemIcon(parent=item_icon_cont, align=Align.CENTER, typeID=self.type_id, width=self.icon_size, height=self.icon_size)
        if self.show_background_graphic:
            Sprite(parent=item_icon_cont, align=Align.CENTER, width=self.icon_size * 1.5, height=self.icon_size * 1.5, texturePath='res:/UI/Texture/classes/ShipInfo/frame_small.png')

    def _construct_top_container(self):
        top_container = eveui.Container(parent=self.container, align=Align.TOTOP, height=20)
        icon_container = eveui.Container(parent=top_container, align=Align.TORIGHT, width=16, padRight=8)
        InfoIcon(parent=icon_container, texturePath=eveicon.info, typeID=self.type_id, color=TextColor.SECONDARY)
        text_container = eveui.Container(parent=top_container, align=Align.TOALL, padRight=4)
        TextBody(parent=text_container, align=Align.TOLEFT, text=self._get_product_name(), autoFadeSides=16)

    def _construct_bottom_container(self):
        bottom_container = eveui.Container(parent=self.container, align=Align.TOALL)
        top = eveui.Container(parent=bottom_container, align=Align.TOTOP_PROP, height=0.5, padBottom=4)
        bot = eveui.Container(parent=bottom_container, align=Align.TOALL, padTop=4)
        eveui.Button(parent=bot, align=Align.TOPLEFT, label=localization.GetByLabel('UI/InfoWindow/ShowContracts'), func=self.on_click_view_contract, density=Density.COMPACT)
        eveui.Button(parent=top, align=Align.BOTTOMLEFT, label=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/ViewInMarket'), func=self.on_click_market_details, density=Density.COMPACT)

    def _construct_content(self):
        self.container = eveui.Container(parent=self, align=Align.TOTOP, height=self.height, padTop=4, padBottom=4)
        self._construct_item_icon()
        self._construct_top_container()
        self._construct_bottom_container()


class PanelIndustry(PanelBase):
    is_minimized_constructed = False

    def _construct_content(self):
        uthread2.Yield()
        bottom_cont = eveui.Container(parent=self.rightCont, align=Align.TOBOTTOM, height=32)
        blueprint = sm.GetService('blueprintSvc').GetBlueprintByProduct(self.typeID)
        if blueprint:
            AuraHintSection(parent=bottom_cont, text=localization.GetByLabel('UI/InfoWindow/ViewBlueprint'), align=Align.TOBOTTOM)
        self.infoScroll = eveui.ScrollContainer(parent=self.rightCont, name='industry_scroll', align=Align.TOALL, padBottom=20)
        self._add_blueprint_section()
        self._add_materials_section()
        self._add_required_for_section()
        self._add_designer_section()
        Sprite(parent=self.leftCont, align=Align.CENTER_PRESERVE_ASPECT, aspectRatio=1, texturePath='res:/UI/Texture/classes/ShipInfo/square_flair.png', state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_ADD, padLeft=-CONTENT_PADDING[EXPANDED])

    def _add_blueprint_section(self, parent = None, is_minimized = False):
        blueprint = sm.GetService('blueprintSvc').GetBlueprintByProduct(self.typeID)
        if blueprint:
            collapse_group = CollapseGroup(parent=parent if parent else self.infoScroll, icon=eveicon.production, text=localization.GetByLabel('UI/Industry/Blueprint'))
            BluePrintSection(parent=collapse_group.mainCont, ship_name=evetypes.GetName(self.typeID), type_id=blueprint.blueprintTypeID, show_background_graphic=False if is_minimized else True)

    def _has_any_published(self, blueprint_id_list):
        for blueprint_id in blueprint_id_list:
            if evetypes.IsPublished(blueprint_id):
                return True

        return False

    def _add_required_for_section(self, parent = None, is_minimized = False):
        blueprint_ids = cfg.blueprintsByMaterialTypeIDs.get(self.typeID, None)
        if blueprint_ids and self._has_any_published(blueprint_ids):
            collapse_group = CollapseGroup(parent=parent if parent else self.infoScroll, icon=eveicon.production, text=localization.GetByLabel('UI/InfoWindow/TabNames/RequiredFor'))
            for blueprint_id in blueprint_ids:
                try:
                    if not evetypes.IsPublished(blueprint_id):
                        continue
                except TypeNotFoundException:
                    continue

                BluePrintSection(parent=collapse_group.mainCont, type_id=blueprint_id, show_background_graphic=False if is_minimized else True)

    def _add_materials_section(self, parent = None):
        materials = get_type_materials_by_id(self.typeID)
        if materials:
            collapse_group = CollapseGroup(parent=parent if parent else self.infoScroll, icon=eveicon.resource_processing, text=localization.GetByLabel('UI/Reprocessing/ReprocessedMaterials'), padBottom=4, padTop=4)
            for material in materials:
                ListEntryEveType(parent=collapse_group.mainCont, align=Align.TOTOP, typeID=material.materialTypeID, text=localization.GetByLabel('UI/InfoWindow/TypeNameWithNumUnits', invType=material.materialTypeID, qty=material.quantity))

    def _add_designer_section(self):
        bottomCont = ContainerAutoSize(name='bottomCont', parent=self.leftCont, align=Align.TOBOTTOM, padBottom=20, padLeft=25, padRight=15)
        designerIDs = evetypes.GetDesigners(self.typeID)
        if designerIDs is None or len(designerIDs) == 0:
            bottomCont.Hide()
            return
        designerDescription = ''
        if designerDescription:
            cont = Container(name='bottomCont', parent=bottomCont, align=Align.TOBOTTOM, height=78)
            self._add_designer_icon(designerIDs[0], cont, align=Align.CENTERLEFT)
            descriptionCont = ContainerAutoSize(name='descCont', parent=cont, align=Align.TOBOTTOM, padding=(88, 0, 8, 0))
            self.descCont = CollapsibleContainer(parent=descriptionCont, align=Align.TOBOTTOM, minHeight=74, collapsedHeight=48, maxFadeHeight=0, textClass=TextDetail, backgroundColor=(0, 0, 0, 0.4), topSpacing=8)
            self.descriptionSeparator = Line(name='line_separator', parent=descriptionCont, align=Align.TOBOTTOM, weight=1)
            self.descCont.set_text(designerDescription)
        else:
            flowCont = FlowContainer(name='designerFlowCont', parent=bottomCont, align=Align.TOBOTTOM, contentSpacing=(8, 8))
            for designerID in designerIDs:
                self._add_designer_icon(designerID, flowCont, align=Align.NOALIGN)

    def _add_designer_icon(self, designerID, parent, align):
        designerLogoCont = Container(name=get_npc_corporation_name(designerID), parent=parent, align=align, width=64, height=64)
        Sprite(bgParent=designerLogoCont, state=uiconst.UI_DISABLED, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/ShipInfo/logo_frame.png', color=(1, 1, 1, 0.05))
        OwnerIcon(ownerID=designerID, parent=designerLogoCont, state=uiconst.UI_NORMAL, align=uiconst.CENTER, width=60, height=60)

    def _enable_minimized_view(self):
        if self.is_minimized_constructed:
            return
        self.minimized_footer.height = 32
        self.minimized_footer.display = True
        blueprint = sm.GetService('blueprintSvc').GetBlueprintByProduct(self.typeID)
        if blueprint:
            AuraHintSection(parent=self.minimized_footer, text=localization.GetByLabel('UI/InfoWindow/ViewBlueprint'), align=Align.TOBOTTOM)
        self._add_blueprint_section(parent=self.content_scroll_minimized, is_minimized=True)
        self._add_materials_section(parent=self.content_scroll_minimized)
        self._add_required_for_section(parent=self.content_scroll_minimized, is_minimized=True)
        self.is_minimized_constructed = True

    @classmethod
    def get_name(cls):
        return localization.GetByLabel('UI/InfoWindow/TabNames/Industry')

    @classmethod
    def get_icon(cls):
        return eveicon.production

    def get_camera_position(self):
        return TOP_DOWN_NOSE_DOWN

    def get_tab_type(self):
        return TAB_INDUSTRY

    @classmethod
    def is_visible(cls, typeID, itemID = None, rec = None):
        if sm.GetService('blueprintSvc').GetBlueprintByProduct(typeID):
            return True
        elif get_type_materials_by_id(typeID):
            return True
        elif cfg.blueprintsByMaterialTypeIDs.get(typeID, None):
            return True
        else:
            return False
