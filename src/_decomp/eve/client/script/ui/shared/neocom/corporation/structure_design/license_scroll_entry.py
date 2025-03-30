#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\structure_design\license_scroll_entry.py
import eveicon
from carbonui import fontconst, uiconst, TextColor
from carbonui.control.baseScrollContEntry import BaseScrollContEntry
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.shared.neocom.corporation.structure_design.confirm_revoke_wnd import ConfirmRevokeWnd
from eve.client.script.ui.cosmetics.structure import licenseSignals
from eve.client.script.ui.util.uix import GetTextWidth
from localization import GetByLabel

class LicenseScrollEntry(BaseScrollContEntry):
    default_height = 30
    default_fixedColor = eveColor.GUNMETAL_GREY
    WARNING_DAYS_THRESHOLD = 7
    WARNING_ICON_SIZE = 30

    def __init__(self, structure_data, license_data, *args, **kwargs):
        super(LicenseScrollEntry, self).__init__(*args, **kwargs)
        self._structure_data = structure_data
        self._license_data = license_data
        self._duration_container = None
        self._construct_layout()

    def _construct_layout(self):
        ButtonIcon(parent=self, align=uiconst.TORIGHT, width=30, height=30, texturePath=eveicon.trashcan, iconSize=16, func=self._on_revoke_button_clicked, hint=GetByLabel('UI/Personalization/PaintTool/RevokeLicenseHint'), iconColor=eveColor.GUNMETAL_GREY)
        if self._structure_data.is_low_power():
            text_str = GetByLabel('UI/Personalization/PaintTool/StructureStates/LowPowerHaveLicense', numDays=999)
        elif self._structure_data.is_abandoned():
            text_str = GetByLabel('UI/Personalization/PaintTool/StructureStates/AbandonedHaveLicense', numDays=999)
        else:
            text_str = GetByLabel('UI/Personalization/PaintTool/StructureStates/LicenseDurationHint', numDays=999)
        error_text_str = GetByLabel('UI/Personalization/PaintTool/LicenseDurationUnknown')
        text_width = max(GetTextWidth(error_text_str, fontsize=fontconst.EVE_LARGE_FONTSIZE), GetTextWidth(text_str, fontsize=fontconst.EVE_LARGE_FONTSIZE))
        show_duration_hint = self._structure_data.is_low_power() or self._structure_data.is_abandoned()
        self._duration_container = Container(name='duration_container', parent=self, align=uiconst.TORIGHT, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Personalization/PaintTool/StructureStates/LowPowerLicenseRowHint') if show_duration_hint else None, width=text_width + self.WARNING_ICON_SIZE, padLeft=10, padRight=10)
        self._duration_label = EveLabelLarge(name='duration_label', parent=self._duration_container, align=uiconst.TORIGHT, padTop=4, maxLines=1)
        self._duration_icon = Sprite(name='duration_icon', parent=self._duration_container, align=uiconst.TORIGHT, width=self.WARNING_ICON_SIZE, height=self.WARNING_ICON_SIZE, texturePath='res:/UI/Texture/classes/paintTool/low_power.png', display=False)
        name_container = Container(name='name_container', parent=self, align=uiconst.TOALL, padLeft=10, padRight=10)
        EveLabelLarge(name='name_label', parent=name_container, align=uiconst.TOLEFT, text=self._structure_data.structure_name, padTop=4, autoFadeSides=10, maxLines=1)
        self._load_duration_container()

    def _on_revoke_button_clicked(self, *args):
        if self._license_data is None:
            return
        popup = ConfirmRevokeWnd(structure_data=self._structure_data, license_data=self._license_data)
        result = popup.ShowModal()
        if result == uiconst.ID_OK:
            licenseSignals.on_license_revoked(self._structure_data)

    def _load_duration_container(self):
        remaining_seconds = max(0, self._license_data.get_remaining_time())
        remaining_days = int(remaining_seconds / 86400)
        if self._structure_data.is_low_power():
            label_text = GetByLabel('UI/Personalization/PaintTool/StructureStates/LowPowerHaveLicense', numDays=remaining_days)
        elif self._structure_data.is_abandoned():
            label_text = GetByLabel('UI/Personalization/PaintTool/StructureStates/AbandonedHaveLicense', numDays=remaining_days)
        else:
            label_text = GetByLabel('UI/Personalization/PaintTool/StructureStates/LicenseDurationHint', numDays=remaining_days)
        self._duration_label.text = label_text
        show_as_warning = remaining_days < self.WARNING_DAYS_THRESHOLD or self._structure_data.is_low_power() or self._structure_data.is_abandoned()
        self._duration_label.color = TextColor.WARNING if show_as_warning else TextColor.NORMAL
        self._duration_icon.display = show_as_warning
