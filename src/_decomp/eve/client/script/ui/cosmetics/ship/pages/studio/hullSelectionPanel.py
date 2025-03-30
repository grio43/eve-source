#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\hullSelectionPanel.py
import carbonui
import eveicon
from carbonui import Align, TextColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from cosmetics.client.ships.skins.live_data import current_skin_design
from eve.client.script.ui.cosmetics.ship.const import PANEL_BG_COLOR, PANEL_BG_OPACITY
from eve.client.script.ui.cosmetics.ship.pages.studio.factionSelector import FactionSelector
from eve.client.script.ui.cosmetics.ship.pages.studio.hullTreeView import HullTreeView
from eve.client.script.ui.cosmetics.ship.pages.studio.studioSettings import selected_faction_id_setting
from eve.client.script.ui.quickFilter import QuickFilterEdit
from localization import GetByLabel
from signals import Signal

class HullSelectionPanel(Container):

    def __init__(self, **kw):
        super(HullSelectionPanel, self).__init__(**kw)
        self.on_close_btn = Signal('on_close_btn')
        self.construct_layout()
        selected_faction_id_setting.on_change.connect(self.on_faction_setting_changed)
        self.tree_view.set_faction(selected_faction_id_setting.get(), current_skin_design.get().ship_type_id)

    def construct_layout(self):
        self.content = Container(name='content', parent=self, padding=16)
        Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', color=PANEL_BG_COLOR, opacity=PANEL_BG_OPACITY, cornerSize=12)
        ButtonIcon(parent=self, align=Align.TOPRIGHT, texturePath=eveicon.close, func=self.on_close_btn)
        carbonui.TextHeader(parent=self.content, align=Align.TOTOP, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/HullSelection'), color=TextColor.HIGHLIGHT)
        self.search_edit = QuickFilterEdit(parent=self.content, align=Align.TOTOP, callback=self.on_search_edit, padTop=16)
        self.faction_selector = FactionSelector(parent=self.content, padTop=8, align=Align.TOTOP, faction_id_setting=selected_faction_id_setting)
        self.tree_view = HullTreeView(parent=self.content, padTop=8)
        self.tree_view.on_hull_type_selected.connect(self.on_hull_type_selected)

    def on_hull_type_selected(self, type_id):
        if type_id is not None:
            current_skin_design.get().ship_type_id = type_id
            current_skin_design.add_to_undo_history()

    def on_search_edit(self, *args):
        query = self.search_edit.GetValue()
        self.faction_selector.display = not bool(query)
        self.tree_view.apply_search_query(query)

    def on_faction_setting_changed(self, faction_id):
        self.tree_view.set_faction(faction_id, current_skin_design.get().ship_type_id)
