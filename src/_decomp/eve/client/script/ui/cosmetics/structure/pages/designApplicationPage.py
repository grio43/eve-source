#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\pages\designApplicationPage.py
from carbonui import const as uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.util.dpi import ReverseScaleDpi
from eve.client.script.ui.control.loadingContainer import LoadingSpriteSize, LoadingContainer
from eve.client.script.ui.cosmetics.structure import const as paintToolConst, paintToolUtils
from eve.client.script.ui.cosmetics.structure import paintToolSelections
from eve.client.script.ui.cosmetics.structure import paintToolSignals
from eve.client.script.ui.cosmetics.structure.components.corpStructureSelector import CorpStructureSelector
from eve.client.script.ui.cosmetics.structure.components.durationSelector import DurationSelector
from eve.client.script.ui.cosmetics.structure.components.navigationButtons import BackButton
from eve.client.script.ui.cosmetics.structure.confirmApplyWnd import ConfirmApplyWnd
from eve.client.script.ui.cosmetics.structure.pages.basePage import BasePage
from localization import GetByLabel

class DesignApplicationPage(BasePage):

    def __init__(self, **kw):
        paintToolSelections.clear_all_selected_structures()
        paintToolSignals.on_structure_selection_changed.connect(self._on_structure_selection_changed)
        paintToolSignals.on_duration_selection_changed.connect(self._on_duration_selection_changed)
        self._panel_container = None
        super(DesignApplicationPage, self).__init__(**kw)
        self._content.LoadContent(loadCallback=self._load_catalogue_callback)

    def Close(self):
        paintToolSignals.on_structure_selection_changed.disconnect(self._on_structure_selection_changed)
        paintToolSignals.on_duration_selection_changed.disconnect(self._on_duration_selection_changed)
        super(DesignApplicationPage, self).Close()

    def _OnResize(self, *args):
        super(DesignApplicationPage, self)._OnResize(*args)
        self._set_panel_container_size()

    def _open_page(self):
        super(DesignApplicationPage, self)._open_page()
        self._corp_structure_selector.update()

    def _construct_layout(self):
        self._content = LoadingContainer(parent=self, name='contentCont', align=uiconst.TOALL, loadingSpriteSize=LoadingSpriteSize.LARGE, failureStateMessage=GetByLabel('UI/Personalization/PaintTool/CatalogueLoadingErrorTitle'), failureStateSubtext=GetByLabel('UI/Personalization/PaintTool/CatalogueLoadingErrorDescription'), retryBtnLabel=GetByLabel('UI/Personalization/PaintTool/ErrorRetry'), padTop=40, failedCallback=self._on_loading_failed)
        self._panel_container = Container(name='panel_container', parent=self._content, align=uiconst.CENTERTOP)
        self._set_panel_container_size()
        self._create_navigation_button()
        self._create_duration_selection()
        self._create_apply_button()
        self._create_structure_list()
        self.UpdateAlignment()

    def _set_panel_container_size(self):
        if self._panel_container:
            self._panel_container.width = paintToolConst.get_design_application_page_width()
            self._panel_container.height = ReverseScaleDpi(self.displayHeight)

    def _on_loading_failed(self, exception):
        raise exception

    def _create_navigation_button(self):
        BackButton(name='back_button', parent=self, align=uiconst.TOPLEFT, left=23, top=23, onClick=self._on_back_clicked)

    def _create_duration_selection(self):
        self._duration_selector = DurationSelector(parent=self._panel_container, name='durationSelector', align=uiconst.TOTOP)

    def _create_apply_button(self):
        apply_button_cont = Container(parent=self._panel_container, name='applyButtonCont', align=uiconst.TOBOTTOM, height=98)
        self._apply_button = Button(parent=apply_button_cont, align=uiconst.CENTERTOP, label=GetByLabel('UI/Personalization/PaintTool/BuyLicense'), enabled=self._is_apply_enabled(), func=self._on_apply_clicked)

    def _create_structure_list(self):
        self._corp_structure_selector = CorpStructureSelector(parent=self._panel_container, name='corpStructureSelector', align=uiconst.TOALL)

    def _load_catalogue_callback(self):
        catalogue = sm.GetService('cosmeticsLicenseSvc').get_structure_paintwork_licenses_catalogue()
        self._duration_selector.set_durations(catalogue.get_available_durations_sorted())
        self._corp_structure_selector.set_prices(catalogue)

    @staticmethod
    def _is_apply_enabled():
        return len(paintToolSelections.SELECTED_STRUCTURES) > 0 and paintToolUtils.has_sufficient_funds()

    @staticmethod
    def _on_back_clicked():
        paintToolSelections.SELECTED_PAGE.set(paintToolConst.DESIGN_CREATION_PAGE_ID)

    @staticmethod
    def _on_apply_clicked(_button):
        popup = ConfirmApplyWnd(paintwork=paintToolSelections.SELECTED_PAINTWORK, structure_ids=paintToolSelections.SELECTED_STRUCTURES.keys(), duration_days=paintToolSelections.SELECTED_DURATION / 86400, total_em_cost=paintToolUtils.get_total_price())
        result = popup.ShowModal()
        if result == uiconst.ID_OK:
            paintToolSelections.SELECTED_PAGE.set(paintToolConst.SUMMARY_PAGE_ID)

    def _on_structure_selection_changed(self, *_args):
        self._apply_button.enabled = self._is_apply_enabled()

    def _on_duration_selection_changed(self):
        self._apply_button.enabled = self._is_apply_enabled()
