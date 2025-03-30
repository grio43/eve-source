#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_structure_design.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.loadingContainer import LoadingSpriteSize
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.corporation.structure_design.no_licenses_panel import CorpStructureDesignNoLicensesPanel
from eve.client.script.ui.shared.neocom.corporation.structure_design.with_licenses_panel import CorpStructureDesignHaveLicensesPanel
from eve.client.script.ui.shared.neocom.corporation.structure_design.license_loading_container import LicenseLoadingContainer
from eve.client.script.ui.cosmetics.structure import licenseSignals
from eve.client.script.ui.cosmetics.structure.corpStructureData import CorpStructureData
from eve.common.lib import appConst
from localization import GetByLabel

class CorpStructureDesignPanel(Container):
    __notifyevents__ = ['OnUIRefresh', 'OnUIScalingChange']
    LOGO_SIZE = 64

    def __init__(self, *args, **kwargs):
        super(CorpStructureDesignPanel, self).__init__(*args, **kwargs)
        self._top_container = None
        self._main_container = None
        self._no_licenses_panel = None
        self._licenses_panel = None
        self._structures_data = {}
        self._licenses_data = {}
        self._structure_type_filter = None
        self._structure_text_filter = None
        self._construct_layout()
        corpUISignals.on_corporation_changed.connect(self._on_corporation_changed)
        licenseSignals.on_license_revoked.connect(self._on_license_revoked)
        licenseSignals.on_reload_licenses_requested.connect(self._on_reload_licenses_requested)
        licenseSignals.on_structure_filter_changed.connect(self._on_structure_type_filter_changed)
        licenseSignals.on_text_filter_changed.connect(self._on_structure_text_filter_changed)

    def Close(self):
        corpUISignals.on_corporation_changed.disconnect(self._on_corporation_changed)
        licenseSignals.on_license_revoked.disconnect(self._on_license_revoked)
        licenseSignals.on_reload_licenses_requested.connect(self._on_reload_licenses_requested)
        licenseSignals.on_structure_filter_changed.disconnect(self._on_structure_type_filter_changed)
        licenseSignals.on_text_filter_changed.disconnect(self._on_structure_text_filter_changed)
        super(CorpStructureDesignPanel, self).Close()

    def _construct_layout(self):
        self._construct_top_container()
        self._construct_main_container()
        self._main_container.LoadContent(loadCallback=self._loading_callback, failedCallback=self._on_loading_failed)

    def _construct_top_container(self):
        self._top_container = Container(name='top_container', align=uiconst.TOTOP, parent=self, height=self.LOGO_SIZE)
        self._refresh_corp_info(corporationID=eve.session.corpid)

    def _construct_main_container(self):
        self._main_container = LicenseLoadingContainer(name='main_container', parent=self, align=uiconst.TOALL, loadingSpriteSize=LoadingSpriteSize.LARGE, failureStateMessage=GetByLabel('UI/Personalization/PaintTool/GetAllLicensesLoadingErrorTitle'), failureStateSubtext=GetByLabel('UI/Personalization/PaintTool/GetAllLicensesLoadingErrorDescription'), retryBtnLabel=GetByLabel('UI/Personalization/PaintTool/ErrorRetry'), padTop=40)

    def _refresh_corp_info(self, corporationID):
        if self is None or self.destroyed:
            return
        if self._top_container is None:
            return
        self._top_container.Flush()
        GetLogoIcon(name='logo_container', parent=self._top_container, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, itemID=corporationID, size=self.LOGO_SIZE)
        caption_container = ContainerAutoSize(name='caption_container', parent=self._top_container, align=uiconst.TOLEFT, height=self.LOGO_SIZE, padLeft=8)
        corp_name = cfg.eveowners.Get(corporationID).ownerName
        caption = EveCaptionMedium(name='caption', parent=caption_container, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Corporations/CorpUIHome/CorpNamePlaceholder', corpName=corp_name))
        info_container = ContainerAutoSize(name='info_container', parent=self._top_container, align=uiconst.TOLEFT, height=self.LOGO_SIZE, padLeft=4)
        InfoIcon(name='info_icon', parent=info_container, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, typeID=appConst.typeCorporation, itemID=corporationID)

    def _populate_panels(self):
        self._main_container.Flush()
        if self._no_licenses_panel:
            self._no_licenses_panel.Close()
            self._no_licenses_panel = None
        if self._licenses_panel:
            self._licenses_panel.Close()
            self._licenses_panel = None
        if len(self._structures_data) == 0:
            self._no_licenses_panel = CorpStructureDesignNoLicensesPanel(name='no_licenses_panel', parent=self._main_container, align=uiconst.TOALL)
        else:
            self._licenses_panel = CorpStructureDesignHaveLicensesPanel(name='have_licenses_panel', parent=self._main_container, align=uiconst.TOALL, structures_data=self._structures_data, licenses_data=self._licenses_data, type_filter=self._structure_type_filter, text_filter=self._structure_text_filter)

    def _fetch_data(self):
        corp_structures = sm.GetService('structureDirectory').GetCorporationStructures()
        cfg.evelocations.Prime(corp_structures.keys())
        self._structures_data = {}
        self._licenses_data = sm.GetService('cosmeticsLicenseSvc').get_structure_licenses_for_corporation()
        for structure_id, structure in corp_structures.iteritems():
            license_data = self._licenses_data.get(structure_id, None)
            if license_data is None:
                continue
            self._structures_data[structure_id] = CorpStructureData(instance_id=structure_id, type_id=structure['typeID'], upkeep_state=structure['upkeepState'], location_id=structure['solarSystemID'], license_id=license_data.id)

    def _on_corporation_changed(self, corporation_id):
        self._refresh_corp_info(corporationID=corporation_id)

    def _on_license_revoked(self, structure_data):
        if len(self._structures_data) == 0:
            return
        if structure_data.instance_id not in self._structures_data:
            return
        self._structures_data.pop(structure_data.instance_id)
        if structure_data.instance_id in self._licenses_data:
            self._licenses_data.pop(structure_data.instance_id)
        if len(self._structures_data) == 0:
            self._populate_panels()
        elif self._licenses_panel is not None:
            self._licenses_panel.remove_structure_entry(structure_data)

    def _on_reload_licenses_requested(self):
        self._main_container.LoadContent(loadCallback=self._loading_callback, failedCallback=self._on_loading_failed)

    def _loading_callback(self):
        self._fetch_data()
        self._populate_panels()

    def _on_loading_failed(self, exception):
        pass

    def _on_structure_type_filter_changed(self, structure_type_id):
        self._structure_type_filter = structure_type_id

    def _on_structure_text_filter_changed(self, text):
        self._structure_text_filter = text

    def Load(self, panel_id, *args):
        pass

    def OnGlobalFontSizeChanged(self):
        self._refresh_corp_info(corporationID=eve.session.corpid)
        self._populate_panels()

    def OnUIRefresh(self):
        self._refresh_corp_info(corporationID=eve.session.corpid)
        self._populate_panels()

    def OnUIScalingChange(self, *args):
        self._refresh_corp_info(corporationID=eve.session.corpid)
        self._populate_panels()
