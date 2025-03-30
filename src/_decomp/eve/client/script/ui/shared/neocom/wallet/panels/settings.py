#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\settings.py
import localization
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control import eveLabel
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.shared.neocom.wallet.panels.baseWalletPanel import BaseWalletPanel
from eve.client.script.ui.shared.neocom.wallet.walletConst import SETTING_LABELS, SETTINGS_CORP, SETTINGS_PERSONAL
from eve.client.script.ui.shared.neocom.wallet.walletUtil import GetSettingValue, ToggleSetting

class SettingsWalletPanel(BaseWalletPanel):
    default_name = 'SettingsWalletPanel'

    def ConstructPanels(self):
        scroll = ScrollContainer(parent=self.panelContainer, align=uiconst.TOALL)
        grid = LayoutGrid(parent=scroll, align=uiconst.TOPLEFT, columns=1, cellSpacing=(8, 8))
        for settingName in SETTINGS_PERSONAL:
            label = localization.GetByLabel(SETTING_LABELS[settingName])
            Checkbox(parent=grid, align=uiconst.TOPLEFT, text=label, wrapLabel=False, checked=GetSettingValue(settingName), callback=lambda _, s = settingName: ToggleSetting(s))

        isk_threshold_grid = LayoutGrid(parent=grid, align=uiconst.TOPLEFT, columns=2, cellSpacing=(8, 0))
        eveLabel.EveLabelMedium(parent=isk_threshold_grid, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/Wallet/WalletWindow/Configuration/WalletBalanceChangeThreshold'))
        SingleLineEditInteger(parent=isk_threshold_grid, align=uiconst.TOPLEFT, setvalue=str(GetSettingValue('iskNotifyThreshold')), OnChange=self.OnIskThresholdChanged)
        eveLabel.EveLabelLarge(parent=grid, align=uiconst.TOPLEFT, top=16, text=localization.GetByLabel('UI/Wallet/WalletWindow/CorporationWallet'))
        for settingName in SETTINGS_CORP:
            label = localization.GetByLabel(SETTING_LABELS[settingName])
            Checkbox(parent=grid, align=uiconst.TOPLEFT, text=label, wrapLabel=False, checked=GetSettingValue(settingName), callback=lambda _, s = settingName: ToggleSetting(s))

    def OnIskThresholdChanged(self, value, *args):
        try:
            if value is '':
                value = 0
            newValue = abs(int(value))
            settings.char.ui.Set('iskNotifyThreshold', newValue)
        except Exception:
            pass
