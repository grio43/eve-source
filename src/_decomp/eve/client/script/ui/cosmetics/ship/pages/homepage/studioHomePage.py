#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\homepage\studioHomePage.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Align, AxisAlignment, Density, uiconst, ButtonVariant
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from cosmetics.client.ships.skins.live_data.section_controller import SequencingInProgressSection, SavedDesignsSection
from cosmetics.common.ships.skins.util import SkinListingOrder
from eve.client.script.ui.cosmetics.ship.const import ANIM_DURATION_LONG
from eve.client.script.ui.cosmetics.ship.pages.homepage.savedDesignInfo import SavedDesignInfo
from eve.client.script.ui.cosmetics.ship.pages.homepage.savedDesignsSection import SavedDesignsSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.homepage.sequencingInProgress import SequencingInProgressSectionContainer
from eve.client.script.ui.cosmetics.ship.pages.homepage.sequencingJobInfo import SequencingJobInfo
from eve.client.script.ui.cosmetics.ship.pages.cards.skinDesignCard import SkinDesignCard
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSignals
from eve.client.script.ui.cosmetics.ship.const import SkinrPage
from eve.client.script.ui.cosmetics.ship.pages.homepage.savedDesignsSettings import designs_sort_by_setting
from localization import GetByLabel
from signals import Signal
import eveicon
MAX_NUM_PER_PAGE = 10

class StudioHomePage(Container):
    default_padding = (32, 128, 32, 32)

    def __init__(self, **kw):
        super(StudioHomePage, self).__init__(**kw)
        self.is_loaded = False
        self.on_create_new_design_btn = Signal('on_create_new_design_btn')
        self.connect_signals()

    def Close(self):
        try:
            self.disconnect_signals()
        finally:
            super(StudioHomePage, self).Close()

    def connect_signals(self):
        studioSignals.on_saved_design_selected.connect(self.on_saved_design_selected)
        studioSignals.on_sequencing_job_selected.connect(self.on_sequencing_job_selected)

    def disconnect_signals(self):
        studioSignals.on_saved_design_selected.disconnect(self.on_saved_design_selected)
        studioSignals.on_sequencing_job_selected.disconnect(self.on_sequencing_job_selected)

    def LoadPanel(self, section_id = None):
        self.opacity = 0.0
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
        else:
            self.section_cont.Flush()
        if section_id is SkinrPage.STUDIO_SAVED_DESIGNS:
            self.construct_view_all_saved_designs_section()
            self.saved_designs_section.deselect_all_cards()
        else:
            self.construct_right_cont()
            self.left_cont.FlagForceUpdateAlignment()
            self.saved_designs_section.verify_cards()
            self.saved_designs_section.deselect_all_cards()
            self.sequencing_in_progress_section.verify_cards()
            self.sequencing_in_progress_section.deselect_all_cards()
            self.show_buttons()
        self.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self, 0.0, 1.0, duration=0.3)

    def UnloadPanel(self):
        self.Disable()
        animations.FadeTo(self, self.opacity, 0.0, duration=uiconst.TIME_EXIT, callback=self.Hide)

    def construct_layout(self):
        self.right_cont = Container(name='right_cont', parent=self, align=Align.TORIGHT_PROP, width=0.55, maxWidth=920)
        self.left_cont = Container(name='left_cont', parent=self, padding=(0, 44, 64, 16))
        self.section_cont = ScrollContainer(parent=self.right_cont, align=Align.TOALL)
        self.construct_left_cont()

    def construct_right_cont(self):
        self.sequencing_in_progress_section = SequencingInProgressSectionContainer(parent=self.section_cont, align=Align.TOTOP, section_controller=SequencingInProgressSection(), single_row=True)
        self.saved_designs_section = SavedDesignsSectionContainer(name='saved_designs_section', parent=self.section_cont, align=Align.TOTOP, section_controller=SavedDesignsSection(), single_row=True, padTop=32)

    def construct_left_cont(self):
        self.button_group = ButtonGroup(parent=self.left_cont, align=Align.BOTTOMRIGHT, button_alignment=AxisAlignment.END, density=Density.EXPANDED, button_size_mode=ButtonSizeMode.DYNAMIC)
        self.button_group.add_button(Button(label=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CreateNewDesign'), func=self._on_create_new_design_btn, variant=ButtonVariant.PRIMARY))
        self.saved_design_info = SavedDesignInfo(name='saved_design_info', parent=self.left_cont)
        self.sequencing_job_info = SequencingJobInfo(name='sequencing_job_info', parent=self.left_cont)

    def construct_view_all_saved_designs_section(self):
        ViewAllSavedDesignsSectionContainer(parent=self.section_cont, align=Align.TOTOP, padTop=32, section_controller=SavedDesignsSection(num_per_page=MAX_NUM_PER_PAGE))

    def _on_create_new_design_btn(self, *args):
        PlaySound('nanocoating_button_start_designing_play')
        return self.on_create_new_design_btn()

    def on_saved_design_selected(self, saved_skin_design_id, skin_design):
        self.sequencing_in_progress_section.deselect_all_cards()
        if saved_skin_design_id or skin_design:
            self.hide_buttons()
        else:
            self.show_buttons()

    def on_sequencing_job_selected(self, sequencing_job):
        self.saved_designs_section.deselect_all_cards()
        if sequencing_job:
            self.hide_buttons()
        else:
            self.show_buttons()

    def hide_buttons(self):
        self.button_group.state = uiconst.UI_DISABLED
        animations.FadeTo(self.button_group, self.button_group.opacity, 0.0, ANIM_DURATION_LONG)

    def show_buttons(self):
        self.button_group.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self.button_group, self.button_group.opacity, 1.0, 0.5, timeOffset=ANIM_DURATION_LONG)


class BaseViewAllSkinsSectionContainer(SavedDesignsSectionContainer):

    def __init__(self, section_controller, max_entries = None, **kw):
        super(BaseViewAllSkinsSectionContainer, self).__init__(section_controller, max_entries, **kw)

    def connect_signals(self):
        super(BaseViewAllSkinsSectionContainer, self).connect_signals()
        designs_sort_by_setting.on_change.connect(self.on_sort_by_setting)

    def disconnect_signals(self):
        super(BaseViewAllSkinsSectionContainer, self).disconnect_signals()
        designs_sort_by_setting.on_change.disconnect(self.on_sort_by_setting)

    def on_sort_by_setting(self, *args):
        self.update()

    def construct_pagination_container(self):
        self.pagination_container = Container(name='pagination_container', parent=self, align=Align.TOTOP, height=32)

    def construct_filter_and_sorting(self):
        SortByMenuButtonIcon(parent=self.filter_and_sorting_cont, align=Align.CENTERLEFT)


class ViewAllSavedDesignsSectionContainer(BaseViewAllSkinsSectionContainer):

    def construct_card(self, card_controller):
        saved_skin_design_id, skin_design = card_controller
        card = SkinDesignCard(name='card_{design_id}'.format(design_id=saved_skin_design_id), parent=self.content, saved_skin_design_id=saved_skin_design_id, skin_design=skin_design)
        card.on_click.connect(self.on_card_clicked)
        return card


class SortByMenuButtonIcon(MenuButtonIcon):
    hint = GetByLabel('UI/Common/SortBy')
    default_texturePath = eveicon.bars_sort_ascending

    def GetMenu(self):
        m = MenuData()
        m.AddCaption(self.hint)
        m.AddRadioButton(GetByLabel('UI/Common/Name'), (SkinListingOrder.NAME, False), designs_sort_by_setting)
        m.AddRadioButton(GetByLabel('UI/Inventory/NameReversed'), (SkinListingOrder.NAME, True), designs_sort_by_setting)
        return m
