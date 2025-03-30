#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\cards\skinDesignCard.py
import evetypes
from carbonui.control.contextMenu.menuData import MenuData
from cosmetics.client.ships.qa.menus import is_qa, get_qa_menu_for_design_card
from eve.client.script.ui.cosmetics.ship.pages.cards.baseSkinCard import SkinCard
from eve.client.script.ui.cosmetics.ship.pages.studio.skinDesignDragData import SkinDesignDragData
from eveservices.menu import GetMenuService

class SkinDesignCard(SkinCard):
    isDragObject = True

    def __init__(self, saved_skin_design_id, skin_design, *args, **kwargs):
        self.saved_skin_design_id = saved_skin_design_id
        self.skin_design = skin_design
        super(SkinDesignCard, self).__init__(*args, **kwargs)

    def get_live_rendered_icon_skin_design(self):
        return self.skin_design

    def get_skin_tier_level(self):
        return self.skin_design.tier_level

    def get_skin_name(self):
        return self.skin_design.name

    def GetMenu(self):
        menu_data = MenuData()
        type_id = self.skin_design.ship_type_id
        menu_data.AddEntry(text=evetypes.GetName(type_id), subMenuData=lambda : GetMenuService().GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True))
        if is_qa():
            menu_data.AddEntry('QA:', subMenuData=lambda : get_qa_menu_for_design_card(self.saved_skin_design_id))
        return menu_data

    def GetDragData(self):
        return SkinDesignDragData(self.skin_design, self.saved_skin_design_id)
