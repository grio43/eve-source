#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\homepage\savedDesignsSection.py
from cosmetics.client.shipSkinDesignSvc import get_ship_skin_design_svc
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.skins.live_data import current_skin_design
from eve.client.script.ui.cosmetics.ship.controls.baseCardSectionContainer import BaseCardSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.cards.skinDesignCard import SkinDesignCard
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.pages.homepage.savedDesignsTooltipInfoIcons import MaxSavedDesignsSkillsInfoIcon
from carbonui import Align

class SavedDesignsSectionContainer(BaseCardSectionContainer):
    __notifyevents__ = ['OnSkillsChanged']

    def connect_signals(self):
        super(SavedDesignsSectionContainer, self).connect_signals()
        ship_skin_signals.on_skin_design_saved.connect(self.on_skin_design_saved)
        ship_skin_signals.on_skin_design_deleted.connect(self.on_skin_design_deleted)
        sm.RegisterNotify(self)

    def disconnect_signals(self):
        super(SavedDesignsSectionContainer, self).disconnect_signals()
        ship_skin_signals.on_skin_design_saved.disconnect(self.on_skin_design_saved)
        ship_skin_signals.on_skin_design_deleted.disconnect(self.on_skin_design_deleted)
        sm.UnregisterNotify(self)

    def OnSkillsChanged(self, *args):
        self.update_num_items_label(force_refresh=True)

    def construct_card(self, card_controller):
        saved_skin_design_id, skin_design = card_controller
        card = SkinDesignCard(name='card_{design_id}'.format(design_id=saved_skin_design_id), parent=self.content, saved_skin_design_id=saved_skin_design_id, skin_design=skin_design)
        card.on_click.connect(self.on_card_clicked)
        return card

    def deselect_all_cards(self):
        for card in self.cards:
            card.is_selected = False

    def on_card_clicked(self, clicked_card):
        for card in self.cards:
            if card != clicked_card:
                card.is_selected = False

        if clicked_card.is_selected:
            studioSignals.on_saved_design_selected(clicked_card.saved_skin_design_id, clicked_card.skin_design)
            current_skin_design.open_existing_saved_design(clicked_card.saved_skin_design_id)
        else:
            studioSignals.on_saved_design_selected(None, None)
            current_skin_design.create_blank_design()

    def on_skin_design_saved(self, design_id):
        self.update()

    def on_skin_design_deleted(self, design_id):
        studioSignals.on_saved_design_selected(None, None)
        self.update()

    def construct_header(self):
        super(SavedDesignsSectionContainer, self).construct_header()
        self.header_layout_grid.columns = 3
        MaxSavedDesignsSkillsInfoIcon(parent=self.header_layout_grid, align=Align.CENTERLEFT)

    def update_num_items_label(self, force_refresh = False):
        num_listings = self.section_controller.get_num_entries()
        num_max = get_ship_skin_design_svc().get_saved_designs_capacity(force_refresh)
        self.num_items_label.text = u'{}/{}'.format(num_listings, num_max)
