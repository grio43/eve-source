#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\personalPaySettingsPanel.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from characterSettingsStorage.characterSettingsConsts import JUMPBRIDGE_AUTOPAYMENT, JUMPBRIDGE_AUTOPAYMENT_CB, JUMPBRIDGE_AUTOPAYMENT_VALUE, PERSONAL_AUTOPAYMENT, PERSONAL_AUTOPAYMENTS_AVAILABLE
from characterSettingsStorage.characterSettingsObject import CharacterSettingsObject
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet.checkboxWithInputFieldEntry import CheckBoxWithInputField
from localization import GetByLabel
BUTTON_LABEL = GetByLabel('UI/Commands/Apply')

def GetTooltipForJB(tooltipPanel, *args):
    tooltipPanel.LoadGeneric1ColumnTemplate()
    tooltipPanel.state = uiconst.UI_NORMAL
    text = GetByLabel('UI/Wallet/WalletWindow/ActivateJumpGateTooltip')
    tooltipPanel.AddLabelMedium(text=text, align=uiconst.TOPLEFT, wrapWidth=200)


class PersonalPaySettingsPanel(Container):
    default_name = 'PersonalPaySettingsPanel'
    _apply_button = None

    def ApplyAttributes(self, attributes):
        super(PersonalPaySettingsPanel, self).ApplyAttributes(attributes)
        self.scroll = Scroll(parent=self, align=uiconst.TOALL)
        self.scroll.HideBackground()
        self.personalAutoPayButtons = ButtonGroup(name='personalAutoPayButtons', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOBOTTOM, idx=0)
        self._apply_button = Button(parent=self.personalAutoPayButtons, label=BUTTON_LABEL, func=self.SubmitPersonalAutomaticPaymentSettings, args=())

    def OnTabSelect(self):
        self._apply_button.Blink(on_off=0)
        self.SetPersonalAutopaymentSettingsIfNeeded()
        self.personalAutoPayButtons.display = True
        scrolllist = []
        configName = JUMPBRIDGE_AUTOPAYMENT
        isChecked = self.personalAutopaymentsObject.GetSingleValue(JUMPBRIDGE_AUTOPAYMENT_CB, False)
        value = self.personalAutopaymentsObject.GetSingleValue(JUMPBRIDGE_AUTOPAYMENT_VALUE, 0)
        scrolllist.append(GetFromClass(CheckBoxWithInputField, {'label': GetByLabel('UI/Wallet/WalletWindow/ActivateJumpGate'),
         'checked': isChecked,
         'cfgname': configName,
         'cfgNameCb': JUMPBRIDGE_AUTOPAYMENT_CB,
         'cfgNameValue': JUMPBRIDGE_AUTOPAYMENT_VALUE,
         'moreTooltip': GetTooltipForJB,
         'OnChange': self.OnPersonalAutoPaymentChanged,
         'currentValue': value,
         'unitString': GetByLabel('UI/Common/ISK')}))
        self.scroll.Load(contentList=scrolllist)

    def SetPersonalAutopaymentSettingsIfNeeded(self):
        if getattr(self, 'personalAutopaymentsObject', None) is None:
            yamlString = self.FetchPersonalAutopaymentSettingsToServer()
            self.personalAutopaymentsObject = CharacterSettingsObject(yamlString)

    def FetchPersonalAutopaymentSettingsToServer(self):
        yamlString = sm.GetService('characterSettings').Get(PERSONAL_AUTOPAYMENT)
        return yamlString

    def SubmitPersonalAutomaticPaymentSettings(self, *args):
        for eachNode in self.scroll.GetNodes():
            cfgname = eachNode.cfgname
            if cfgname not in PERSONAL_AUTOPAYMENTS_AVAILABLE:
                uicore.Message('CustomInfo', {'info': 'Trying to save a payment not in the list, fix your stuff!'})
                raise RuntimeError()
            isChecked = eachNode.checked
            value = eachNode.get('currentValue', 0)
            self.personalAutopaymentsObject.SetSingleValue(eachNode.cfgNameCb, isChecked)
            self.personalAutopaymentsObject.SetSingleValue(eachNode.cfgNameValue, value)

        newYamlString = self.personalAutopaymentsObject.GetYamlStringForServer()
        sm.GetService('characterSettings').Save(PERSONAL_AUTOPAYMENT, newYamlString)

    def OnPersonalAutoPaymentChanged(self, *args):
        self._apply_button.Blink()
