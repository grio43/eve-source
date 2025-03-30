#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\shipFilterMenuButton.py
import carbonui
import eveicon
import evetypes
from carbonui import PickState, Align, TextColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import SessionSettingEnum
from cosmetics.client.ships.skins.live_data import current_skin_design
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.cosmetics.ship.pages.studio.factionSelector import FactionSelector
from eve.client.script.ui.cosmetics.ship.pages.studio.hullTreeView import HullTreeView
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.common.lib import appConst
from localization import GetByLabel

class ShipFilterMenuButton(ButtonIcon):
    hint = GetByLabel('UI/Common/Filter')
    default_texturePath = eveicon.spaceship_command

    def __init__(self, hull_type_setting, **kw):
        self.hull_type_setting = hull_type_setting
        super(ShipFilterMenuButton, self).__init__(**kw)
        self.hull_type_setting.on_change.connect(self.on_filter_changed)

    def ConstructTooltipPanel(self):
        return FilterTooltipPanel(hull_type_setting=self.hull_type_setting, pickState=PickState.ON)

    def on_filter_changed(self, *args):
        self.UpdateIconState()

    def IsFilterActive(self):
        return bool(self.hull_type_setting.get())

    def _GetIconColor(self):
        if self.IsFilterActive():
            return eveThemeColor.THEME_FOCUS
        else:
            return super(ShipFilterMenuButton, self)._GetIconColor()


class FilterTooltipPanel(TooltipPanel):
    default_columns = 1

    def __init__(self, hull_type_setting, **kw):
        super(FilterTooltipPanel, self).__init__(**kw)
        self.hull_type_setting = hull_type_setting
        self.LoadStandardSpacing()
        content = ContainerAutoSize(name='content', parent=self, width=320)
        carbonui.TextHeader(parent=content, align=Align.TOTOP, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/HullTypeFilter'), color=TextColor.HIGHLIGHT)
        self.search_edit = QuickFilterEdit(parent=content, align=Align.TOTOP, callback=self.on_search_edit, padTop=16)
        faction_setting = SessionSettingEnum(self.get_default_faction_id())
        self.faction_selector = FactionSelector(parent=content, padTop=8, align=Align.TOTOP, faction_id_setting=faction_setting)
        self.tree_view = HullTreeView(parent=content, align=Align.TOTOP, height=400, padTop=8)
        self.tree_view.on_hull_type_selected.connect(self.on_hull_type_selected)
        faction_setting.on_change.connect(self.on_faction_setting_changed)
        self.tree_view.set_faction(faction_setting.get(), self.hull_type_setting.get())

    def get_default_faction_id(self):
        type_id = self.hull_type_setting.get()
        if not type_id:
            type_id = current_skin_design.get_default_ship_type_id()
        return evetypes.GetFactionID(type_id)

    def on_hull_type_selected(self, type_id):
        self.hull_type_setting.set(type_id)

    def on_search_edit(self, *args):
        query = self.search_edit.GetValue()
        self.faction_selector.display = not bool(query)
        self.tree_view.apply_search_query(query)

    def on_faction_setting_changed(self, faction_id):
        self.tree_view.set_faction(faction_id, selected_type_id=self.hull_type_setting.get())
