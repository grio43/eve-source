#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\sequence\sequenceBinderEntries.py
import carbonui
import eveformat
import eveicon
import evetypes
from carbonui import Align, TextBody, TextColor, PickState, uiconst, ButtonVariant
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uiconst import OutputMode
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.warningIcon import WarningIcon
from eve.client.script.ui.cosmetics.ship.const import PANEL_BG_COLOR, PANEL_BG_OPACITY, SEQUENCE_BINDER_ICONS_BY_MATERIAL_TYPE, SEQUENCE_BINDER_NAMES_BY_MATERIAL_TYPE
from eve.client.script.ui.cosmetics.ship.pages.studio.requiredComponentTooltipPanel import RequiredComponentTooltipPanel
from eveservices.menu import GetMenuService
from localization import GetByLabel

class SequenceBinderCostEntry(Container):
    default_height = 32

    def __init__(self, type_id, **kw):
        super(SequenceBinderCostEntry, self).__init__(**kw)
        self.type_id = type_id
        self.is_lacking = False
        self.construct_layout()
        self.update()

    def construct_layout(self):
        self.icon = Sprite(parent=self, texturePath=SEQUENCE_BINDER_ICONS_BY_MATERIAL_TYPE[self.type_id], align=Align.CENTERLEFT, pos=(0, 0, 16, 16), color=TextColor.NORMAL, pickState=PickState.OFF)
        self.label = carbonui.TextBody(name='name_label', parent=self, align=Align.CENTERLEFT, left=24, text=evetypes.GetName(self.type_id))
        self.warning_icon = WarningIcon(parent=self, align=Align.CENTERLEFT, left=self.label.left + self.label.width + 4, top=2, display=False)
        self.amount_label = carbonui.TextBody(name='amount_label', parent=self, align=Align.CENTERRIGHT, color=TextColor.HIGHLIGHT, bold=True)

    def update(self):
        num_runs = get_ship_skin_sequencing_svc().get_num_runs()
        amount_required_by_type = current_skin_design.get().get_sequence_binder_amounts_required(num_runs)
        amount_available_by_type = get_ship_skin_sequencing_svc().get_available_at_active_location(amount_required_by_type)
        required_amount = amount_required_by_type[self.type_id]
        available_amount = amount_available_by_type[self.type_id]
        self.amount_label.text = eveformat.number(required_amount)
        self.is_lacking = required_amount > available_amount
        text_color = eveColor.DANGER_RED if self.is_lacking else TextColor.NORMAL
        self.amount_label.rgba = self.label.rgba = text_color
        self.warning_icon.display = self.is_lacking
        if self.is_lacking:
            self.hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/InsufficientSequenceBinderAmount', type_id=self.type_id, available_amount=available_amount)
        else:
            self.hint = None

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=self.type_id, includeMarketDetails=True)

    def OnClick(self, *args):
        sm.GetService('info').ShowInfo(self.type_id)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.hint:
            return
        tooltipPanel.columns = 1
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.pickState = PickState.ON
        tooltipPanel.AddLabelMedium(text=self.hint, wrapWidth=300, color=eveColor.DANGER_RED)
        button_group = ButtonGroup(parent=tooltipPanel, align=Align.TOTOP, button_size_mode=ButtonSizeMode.DYNAMIC, padTop=8)
        Button(parent=button_group, label=GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), func=self.on_view_on_market_button, texturePath=eveicon.market_details, variant=ButtonVariant.GHOST)

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def on_view_on_market_button(self, *args):
        sm.GetService('marketutils').ShowMarketDetails(self.type_id)


class SequenceBinderCostEntryCompact(Container):
    default_width = 60
    default_height = 68

    def __init__(self, type_id, **kw):
        super(SequenceBinderCostEntryCompact, self).__init__(**kw)
        self.type_id = type_id
        cont = ContainerAutoSize(parent=self, align=Align.VERTICALLY_CENTERED)
        self.icon = Sprite(parent=cont, texturePath=SEQUENCE_BINDER_ICONS_BY_MATERIAL_TYPE[self.type_id], align=Align.CENTERTOP, pos=(0, 0, 16, 16), color=TextColor.SECONDARY, pickState=PickState.OFF)
        self.amount_label = carbonui.TextHeader(name='amount_label', parent=cont, align=Align.CENTERTOP, top=18, color=TextColor.HIGHLIGHT)
        carbonui.TextBody(name='name_label', parent=self, align=Align.CENTERBOTTOM, top=-20, text=GetByLabel(SEQUENCE_BINDER_NAMES_BY_MATERIAL_TYPE[self.type_id]), color=TextColor.NORMAL)
        self.frame = Sprite(name='frame_bg', bgParent=self, opacity=0.2, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/sequencing/hex_frame.png', outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.0)
        Sprite(name='bg', bgParent=self, color=PANEL_BG_COLOR, opacity=PANEL_BG_OPACITY, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/sequencing/hex_bg.png')

    def update_frame(self, required_amount):
        if required_amount:
            self.frame.rgba = TextColor.NORMAL
            self.frame.glowBrightness = 0.5
        else:
            self.frame.rgba = TextColor.DISABLED
            self.frame.glowBrightness = 0.0

    def update(self, required_amount):
        self.amount_label.text = eveformat.number_readable_short(required_amount)
        self.update_frame(required_amount)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=self.type_id, includeMarketDetails=True)

    def OnClick(self, *args):
        sm.GetService('info').ShowInfo(self.type_id)


class UnlimitedComponentLicenseEntry(Container):
    default_height = 28
    ITEM_ICON_SIZE = 28
    TYPE_ICON_SIZE = 16

    def __init__(self, type_id, component, *args, **kwargs):
        super(UnlimitedComponentLicenseEntry, self).__init__(*args, **kwargs)
        self.type_id = type_id
        self.component = component
        self.construct_layout()
        self.update()

    def construct_layout(self):
        self.sequence_binder_name = SequenceBinderName(parent=self, align=Align.TOLEFT, component=self.component, license_type=ComponentLicenseType.UNLIMITED, height=self.default_height, padLeft=32)
        warning_icon_container = Container(parent=self, align=Align.TOLEFT, width=16, top=2, padLeft=4)
        self.warning_icon = WarningIcon(parent=warning_icon_container, align=Align.CENTER, display=False)
        SequenceBinderAmount(parent=self, align=Align.TORIGHT, type_id=self.type_id, component_data=self.component.get_component_data(), height=self.default_height)

    def update(self):
        license = self.component.get_component_license()
        self.show_warning = license is None
        self.sequence_binder_name.show_warning = self.show_warning
        self.warning_icon.display = self.show_warning


class LimitedComponentLicenseEntry(Container):
    default_height = 28
    ITEM_ICON_SIZE = 28

    def __init__(self, component, *args, **kwargs):
        super(LimitedComponentLicenseEntry, self).__init__(*args, **kwargs)
        self.component = component
        self.show_warning = False
        self.construct_layout()
        self.update()

    def construct_layout(self):
        self.sequence_binder_name = SequenceBinderName(parent=self, align=Align.TOLEFT, component=self.component, license_type=ComponentLicenseType.LIMITED, height=self.default_height)
        warning_icon_container = Container(parent=self, align=Align.TOLEFT, width=16, top=2, padLeft=4)
        self.warning_icon = WarningIcon(parent=warning_icon_container, align=Align.CENTER, display=False)
        label_container = ContainerAutoSize(parent=self, align=Align.TORIGHT, height=self.default_height)
        self.label = TextBody(parent=label_container, align=Align.CENTERRIGHT)

    def update(self):
        license = self.component.get_component_license()
        if license is None:
            self.show_warning = True
        elif license.license_type == ComponentLicenseType.LIMITED:
            self.show_warning = not license.has_enough_remaining_uses(self.component_amount)
        else:
            self.show_warning = False
        self.label.text = eveformat.number(self.component_amount)
        self.label.rgba = eveColor.DANGER_RED if self.show_warning else TextColor.NORMAL
        self.sequence_binder_name.show_warning = self.show_warning
        self.warning_icon.display = self.show_warning
        self.sequence_binder_name.state = uiconst.UI_PICKCHILDREN if self.show_warning else uiconst.UI_NORMAL
        self.state = uiconst.UI_NORMAL if self.show_warning else uiconst.UI_PICKCHILDREN

    @property
    def item_type_id(self):
        return self.sequence_binder_name.item_type_id

    @property
    def component_amount(self):
        slot_layout = current_skin_design.get().slot_layout
        num_runs = get_ship_skin_sequencing_svc().get_num_runs()
        return num_runs * slot_layout.get_amount_of_components_with_license_type(component_id=self.component.component_id, license_type=ComponentLicenseType.LIMITED)

    def GetMenu(self):
        if not self.item_type_id:
            return None
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=self.item_type_id, includeMarketDetails=True)

    def ConstructTooltipPanel(self):
        return RequiredComponentTooltipPanel(component_instance=self.component, title=self.component.get_component_data().name, show_warning=self.show_warning)

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def OnClick(self, *args):
        if self.item_type_id:
            sm.GetService('info').ShowInfo(self.item_type_id)


class SequenceBinderName(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL

    def __init__(self, component, license_type, *args, **kwargs):
        super(SequenceBinderName, self).__init__(*args, **kwargs)
        self.component = component
        self.license_type = license_type
        self._show_warning = False
        self.construct_layout()

    def construct_layout(self):
        icon_container = Container(parent=self, align=Align.TOLEFT, width=self.height)
        Sprite(parent=icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=self.component.get_component_data().icon_file_path, textureSecondaryPath='res:/UI/Texture/circle_full.png', spriteEffect=uiconst.SpriteEffect.MODULATE, pos=(0,
         0,
         self.height,
         self.height))
        label_container = ContainerAutoSize(parent=self, align=Align.TOLEFT, height=self.default_height, padLeft=8)
        self.label = TextBody(parent=label_container, align=Align.CENTERLEFT, text=self.component.get_component_data().name, color=TextColor.SECONDARY)

    def update(self):
        self.label.rgba = eveColor.DANGER_RED if self.show_warning else TextColor.NORMAL

    @property
    def show_warning(self):
        return self._show_warning

    @show_warning.setter
    def show_warning(self, value):
        if self._show_warning == value:
            return
        self._show_warning = value
        self.update()

    @property
    def item_type_id(self):
        return self.component.get_component_data().get_item_type(self.license_type)

    def GetMenu(self):
        if not self.item_type_id:
            return None
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=self.item_type_id, includeMarketDetails=True)

    def OnClick(self, *args):
        if self.item_type_id:
            sm.GetService('info').ShowInfo(self.item_type_id)

    def ConstructTooltipPanel(self):
        if not self.show_warning:
            return
        return RequiredComponentTooltipPanel(component_instance=self.component, title=self.component.get_component_data().name, show_warning=self.show_warning)


class SequenceBinderAmount(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL

    def __init__(self, type_id, component_data, *args, **kwargs):
        super(SequenceBinderAmount, self).__init__(*args, **kwargs)
        self.type_id = type_id
        self.component_data = component_data
        self.construct_layout()

    def construct_layout(self):
        text_container = ContainerAutoSize(parent=self, align=Align.TORIGHT, height=self.default_height)
        required_amount = self.component_data.sequence_binder_required_amount
        num_runs = get_ship_skin_sequencing_svc().get_num_runs()
        TextBody(parent=text_container, align=Align.CENTERRIGHT, text=eveformat.number(required_amount * num_runs), color=TextColor.SECONDARY)
        icon_container = Container(parent=self, align=Align.TORIGHT, opacity=0.75, width=16, padRight=8)
        Sprite(parent=icon_container, align=Align.CENTER, state=uiconst.UI_DISABLED, texturePath=SEQUENCE_BINDER_ICONS_BY_MATERIAL_TYPE[self.type_id], textureSecondaryPath='res:/UI/Texture/circle_full.png', spriteEffect=uiconst.SpriteEffect.MODULATE, pos=(0, 0, 16, 16), color=TextColor.SECONDARY)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=self.type_id, includeMarketDetails=True)

    def OnClick(self, *args):
        sm.GetService('info').ShowInfo(self.type_id)
