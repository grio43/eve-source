#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\structure_design\with_licenses_panel.py
from carbonui import uiconst, ButtonVariant
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveCaptionLarge, EveLabelMedium
from eve.client.script.ui.shared.neocom.corporation.structure_design.license_list_filters import LicenseListFilters
from eve.client.script.ui.shared.neocom.corporation.structure_design.license_scroll_entry import LicenseScrollEntry
from eve.client.script.ui.cosmetics.structure import licenseSignals
from localization import GetByLabel

class CorpStructureDesignHaveLicensesPanel(Container):
    __notifyevents__ = ['OnUIRefresh', 'OnUIScalingChange']
    default_clipChildren = True
    BANNER_WIDTH = 1600
    BANNER_HEIGHT = 300

    def __init__(self, structures_data, licenses_data, type_filter, text_filter, *args, **kwargs):
        super(CorpStructureDesignHaveLicensesPanel, self).__init__(*args, **kwargs)
        self._structures_data = structures_data
        self._licenses_data = licenses_data
        self._entries = {}
        self._header_container = None
        self._banner = None
        self._license_scroll = None
        self._filters = None
        self._construct_layout(type_filter, text_filter)
        licenseSignals.on_structure_filter_changed.connect(self._on_structure_filter_changed)
        licenseSignals.on_text_filter_changed.connect(self._on_text_filter_changed)
        sm.RegisterNotify(self)

    def Close(self):
        licenseSignals.on_structure_filter_changed.disconnect(self._on_structure_filter_changed)
        licenseSignals.on_text_filter_changed.disconnect(self._on_text_filter_changed)
        super(CorpStructureDesignHaveLicensesPanel, self).Close()

    def _construct_layout(self, type_filter, text_filter):
        self._construct_header()
        self._construct_list(type_filter, text_filter)
        self._OnResize()

    def _construct_header(self):
        self._header_container = Container(name='header_container', parent=self, align=uiconst.TOTOP, height=200, clipChildren=True)
        Button(name='skinr_button', parent=self._header_container, align=uiconst.BOTTOMRIGHT, label=GetByLabel('UI/Personalization/PaintTool/OpenSKINR'), texturePath='res:/UI/Texture/WindowIcons/paint_tool.png', variant=ButtonVariant.PRIMARY, func=self._on_skinr_button_click, padRight=20, padBottom=20)
        text_container = ContainerAutoSize(name='text_container', parent=self._header_container, align=uiconst.TOTOP, padLeft=20, padTop=20)
        description_container = ContainerAutoSize(name='description_container', parent=text_container, align=uiconst.TOBOTTOM)
        EveLabelMedium(name='cta_description', parent=description_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/TrySKINRDescription'))
        caption_container = ContainerAutoSize(name='caption_container', parent=text_container, align=uiconst.TOBOTTOM, padBottom=10)
        EveCaptionLarge(name='cta_caption', parent=caption_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/TrySKINRTitle'))
        self._banner = Sprite(name='banner', parent=self._header_container, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/StructureDesign/background/skinr_banner.png', state=uiconst.UI_DISABLED)

    def _construct_list(self, type_filter, text_filter):
        list_container = Container(name='list_container', parent=self, align=uiconst.TOALL, padLeft=16, padRight=16, padTop=20)
        EveCaptionMedium(name='list_title', parent=list_container, align=uiconst.TOTOP, text=GetByLabel('UI/Personalization/PaintTool/YourLicenses'))
        self._filters = LicenseListFilters(name='list_filters', parent=list_container, align=uiconst.TOTOP, height=32, padTop=20, type_filter=type_filter, text_filter=text_filter)
        self._license_scroll = ScrollContainer(name='license_scroll', parent=list_container, align=uiconst.TOALL, padTop=20)
        self._refresh_list()

    def _refresh_list(self):
        if self.destroyed:
            return
        self._populate_list()

    def _populate_list(self):
        self._license_scroll.Flush()
        self._entries = {}
        for structure_id, structure_data in self._structures_data.iteritems():
            if self._filters.is_type_filter_enabled:
                if structure_data.type_id != self._filters.structure_type_id:
                    continue
            if self._filters.is_text_filter_enabled:
                if self._filters.search_text.lower() not in structure_data.structure_name.lower():
                    continue
            license_data = self._licenses_data.get(structure_id, None)
            self._entries[structure_data.instance_id] = LicenseScrollEntry(parent=self._license_scroll, structure_data=structure_data, license_data=license_data, padBottom=8)

        if len(self._entries) == 0:
            self._license_scroll.ShowNoContentHint(GetByLabel('UI/Structures/Browser/NoStructuresFound'))

    def remove_structure_entry(self, structure_data):
        if structure_data.instance_id in self._entries:
            self._entries[structure_data.instance_id].Close()
            self._entries.pop(structure_data.instance_id)
        if structure_data.instance_id in self._structures_data:
            self._structures_data.pop(structure_data.instance_id)

    def _on_skinr_button_click(self, _buttton):
        uicore.cmd.OpenPaintToolWindow()

    def _on_structure_filter_changed(self, _structure_type_id):
        self._refresh_list()

    def _on_text_filter_changed(self, _text):
        self._refresh_list()

    def _OnResize(self, *args):
        super(CorpStructureDesignHaveLicensesPanel, self)._OnResize(*args)
        if self.destroyed:
            return
        if self._header_container and self._banner:
            scale_ratio = max(1.0, float(self._header_container.displayWidth) / float(self.BANNER_WIDTH))
            self._banner.width = float(self.BANNER_WIDTH) * scale_ratio
            self._banner.height = float(self.BANNER_HEIGHT) * scale_ratio
            header_padding = 8 if uicore.dpiScaling > 1.25 else 0
            self._header_container.padLeft = header_padding
            self._header_container.padRight = header_padding

    def OnGlobalFontSizeChanged(self):
        self._refresh_list()

    def OnUIRefresh(self):
        self._refresh_list()

    def OnUIScalingChange(self, *args):
        self._refresh_list()
